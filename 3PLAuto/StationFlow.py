import requests
import json
from GlobalVar import *
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from internalToteIn import __InternalToteInAPI__
from ToteCollection import __CollectionAPI__
driver = ''


def __CheckServiceType__(BookingNumber, StationKey):
    ServiceType = ""
    # Check 3PL service type and station key
    if BookingNumber[:-8] == "SITY3F" or BookingNumber[:-8] == "ITRTY3F" or BookingNumber[:-8] == "CITY3F":
        if str(StationKey).startswith("1") == False:
            print("Input wrong station key")
        else:
            if BookingNumber[:-8] == "SITY3F":
                ServiceType = "Stock-in"
            elif BookingNumber[:-8] == "ITRTY3F":
                ServiceType = "Internal Tote-in"
            elif BookingNumber[:-8] == "CITY3F":
                ServiceType = "Carton Stock-in"
    elif BookingNumber[:-8] == "SOTY3F":
        if StationKey == "505" or StationKey == "752":
            ServiceType = "Stock-out"
        else:
            print("Input wrong staion key")
    elif BookingNumber[:-8] == "TCTY3F":
        if StationKey == "503" or StationKey == "751":
            ServiceType = "Tote Collection"
    print("Sevice type : " + ServiceType + ", Station : " + StationKey)
    return ServiceType

# 完成API後退出Station Flow


def __StationDone__(StationKey):
    if str(StationKey).startswith("1"):
        DoneButton = driver.find_element(By.XPATH, '//*[text()="投箱完成"]')
        DoneButton.click()
        time.sleep(1)
    ConfirmButton = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.XPATH, '//*[text()="確認"]')))
    ConfirmButton.click()
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, '//*[text()="請點擊確認返回首頁或等待自動跳轉。"]')))
    ConfirmButton = driver.find_element(By.XPATH, '//*[text()="確 認"]')
    ConfirmButton.click()
    time.sleep(2)


def __OpenStaiton__(StationKey):
    Station = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, f"(//*[text()='{StationKey}'])[last()]/../..")))
    Station.click()
    OK = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='OK']")))
    OK.click()


def __KIOSKFlow__(BookingNumber, StationKey, ToteList=None):
    global driver
    ServiceType = __CheckServiceType__(BookingNumber, StationKey)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')  # 瀏覽器最大Size
    chrome_options.add_argument("--disable-notifications")  # 禁止通知
    chrome_options.add_argument("--use-fake-ui-for-media-stream")  # 禁止錄影提示視窗
    chrome_options.add_argument('--disable-print-preview')  # 禁止列印彈出視窗
    driver = webdriver.Chrome(options=chrome_options)
    SelectStation = f'https://mwms-kiosk-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/selectStation'
    driver.get(SelectStation)
    Station = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
        (By.XPATH, f"(//*[text()='{StationKey}'])[last()]/../..")))
    NotificationBarDisable = driver.find_element(
        By.XPATH, '//*[@class="ant-notification ant-notification-topRight"]')
    driver.execute_script(
        "arguments[0].style.display='none';", NotificationBarDisable)
    if Station.is_enabled() == False:
        RemoveStation = driver.find_element(By.XPATH, "//*[text()='強制移除']")
        RemoveStation.click()
        __OpenStaiton__(StationKey)
        __OpenStaiton__(StationKey)
    else:
        __OpenStaiton__(StationKey)
    time.sleep(1)
    # Determine which station
    # 101~110
    if str(StationKey).startswith("1"):
        print(f"Open {StationKey}")
        try:
            Button = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, '//*[text()="開始投箱"]')))
            Button.click()
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                (By.XPATH, '//*[text()="請將箱子放置於輸送帶。"]')))
            if ServiceType == "Internal Tote-in":
                __InternalToteInAPI__(BookingNumber, StationKey, ToteList)
                driver.refresh()
                time.sleep(2)
                __StationDone__(StationKey)
                driver.quit()
                return
        except TimeoutException:
            try:
                StationStatus = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.XPATH, '//*[text()="請將箱子放置於輸送帶。"]')))
                if ServiceType == "Internal Tote-in":
                    __InternalToteInAPI__(BookingNumber, StationKey, ToteList)
                    time.sleep(2)
                    __StationDone__(StationKey)
                    driver.quit()
                    return
            except TimeoutException:
                print(StationKey + "Station flow error")
    # 503 or 751 station
    elif StationKey == "503" or StationKey == "751":
        print(f"Open {StationKey}")
        try:
            __InputBookingNoEnterStation__(BookingNumber)
        except:
            __503StuckOrderHandle__()
            __InputBookingNoEnterStation__(BookingNumber)
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                (By.XPATH, "//*[text()='空箱送出中，請稍候。']")))
            time.sleep(2)
            __CollectionAPI__(BookingNumber, StationKey)
            time.sleep(2)
            __StationDone__(StationKey)
            driver.quit()
        except TimeoutException:
            print("Station occurs error, Please check")
     # 505 or 752 station
    elif StationKey == "505" or StationKey == "752":
        print(f"Open {StationKey}")
        __InputBookingNoEnterStation__(BookingNumber)
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(
                (By.XPATH, "//*[text()='貨箱送出中，請稍候。']")))

        except TimeoutException:
            print("Station occurs error, Please check")


def __InputBookingNoEnterStation__(BookingNumber):
    StationEntryele = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//*[text()='手動輸入']")))
    StationEntryele.click()
    InputBookingNumberEle = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, '//input[@type="text"]')))
    InputBookingNumberEle.click()
    InputBookingNumberEle.send_keys(f'{BookingNumber[-8:]}')
    driver.find_element(By.XPATH, "//*[text()='確認']").click()
    StationStatusText = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, '//*[@class="story-patientblock-content-title whitespace-pre-wrap"]')))
    print(StationStatusText.text)

    if StationStatusText.text == "非預約時間，請點擊尋找協助。":
        if TestEnv.lower() == "dev":
            OperatorPassword = "9d0bb6471"
        else:
            OperatorPassword = "958c0b310"
        driver.find_element(By.XPATH, '(//*[text()="尋求協助"])[last()]').click()
        OperatorLogin = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[text()="工作人員登入"]')))
        OperatorLogin.click()
        OperatorInput = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='手動輸入']")))
        OperatorInput.click()
        Input = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//input[@type="text"]')))
        Input.click()
        Input.send_keys(f"{OperatorPassword}")
        driver.find_element(By.XPATH, "//*[text()='確認']").click()
        Confirm = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[text()='批准']")))
        Confirm.click()
    else:
        pass

# 卡單處理，無條件清空頁面並重啟


def __503StuckOrderHandle__():
    StationKey = "503"
    StuckOrder = driver.find_element(
        By.XPATH, '//*[@class="storybook-navtab-bookingNo storybook-navtab-clicked pt-2"]')
    StuckOrderBookingNumber = StuckOrder.text
    print("Stuck order : " + StuckOrderBookingNumber)
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_COLLECTION&bookingNo={StuckOrderBookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Collection Task no. " + TaskNo)
    M5119URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/empty_tote_out_report'
    M5119Body = json.dumps({
        "msgTime": "2021-09-01T19:02:33.597+08:00",
        "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
        "data": [
            {
                "taskNo": TaskNo,
                "isSuccess": True,
                "detail": [
                    {
                        "cellsNumber": 11,
                        "containerCodes": "",
                        "errorCode": None,
                        "remarks": None
                    },
                    {
                        "cellsNumber": 12,
                        "containerCodes": "",
                        "errorCode": None,
                        "remarks": None
                    },
                    {
                        "cellsNumber": 14,
                        "containerCodes": "",
                        "errorCode": None,
                        "remarks": None
                    }
                ]
            }
        ]
    })
    APIheaders = {"Content-Type": "application/json"}
    print(M5119Body)
    M5119SendRequsets = requests.post(
        M5119URL, data=M5119Body, headers=APIheaders).json()
    print(M5119SendRequsets)
    driver.refresh()
    __StationDone__(StationKey)
