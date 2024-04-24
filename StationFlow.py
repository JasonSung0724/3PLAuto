import requests
from GlobalVar import *
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from internalToteIn import __InternalToteInAPI__

driver = ''

def __CheckServiceType__(BookingNumber,StationKey):
    ServiceType = ""
    # Check 3PL service type and station key
    if BookingNumber[:-8] == "SITY3F" or BookingNumber[:-8] == "ITRTY3F" or BookingNumber[:-8] == "CITY3F" :
        if str(StationKey).startswith("1") == False :
            print("Input wrong station key")
        else:
            if BookingNumber[:-8] == "SITY3F" :
                ServiceType = "Stock-in"
            elif BookingNumber[:-8] == "ITRTY3F" :
                ServiceType = "Internal Tote-in"
            elif BookingNumber[:-8] == "CITY3F" :
                ServiceType = "Carton Stock-in"
    elif BookingNumber[:-8] == "SOTY3F" :
        if StationKey == "505" or StationKey == "752":
            ServiceType = "Stock-out"
        else:
            print("Input wrong staion key")
    elif BookingNumber[:-8] == "TCTY3F" :
        if StationKey == "503" or StationKey == "751":
            ServiceType = "Tote Collection"
    print("Sevice type : " + ServiceType + ", Station : " + StationKey)
    return ServiceType

def __StationDone__():
    DoneButton = driver.find_element(By.XPATH,'//*[text()="投箱完成"]')
    DoneButton.click()
    ConfirmButton = WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="確認"]')))
    ConfirmButton.click()
    ConfirmButton = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="確認"]')))
    ConfirmButton.click()
    WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="請點擊確認返回首頁或等待自動跳轉。"]')))
    ConfirmButton = driver.find_element(By.XPATH,'//*[text()="確 認"]')
    ConfirmButton.click()
    time.sleep(2)


def __OpenStaiton__(StationKey):
    Station = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,f"(//*[text()='{StationKey}'])[last()]/../..")))
    Station.click()
    OK = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//*[text()='OK']")))
    OK.click()

def __KIOSKFlow__(BookingNumber,StationKey,ToteList=None):
    global driver , NewRegisterToteList
    ServiceType = __CheckServiceType__(BookingNumber,StationKey)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    driver = webdriver.Chrome(options=chrome_options)
    SelectStation = f'https://mwms-kiosk-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/selectStation'
    driver.get(SelectStation)
    Station = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,f"(//*[text()='{StationKey}'])[last()]/../..")))
    if Station.is_enabled() == False :
        RemoveStation = driver.find_element(By.XPATH,"//*[text()='強制移除']")
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
        try :
            Button = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="開始投箱"]'))) 
            Button.click()
            WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="請將箱子放置於輸送帶。"]')))
            if ServiceType == "Internal Tote-in" :
                __InternalToteInAPI__(BookingNumber,StationKey,ToteList)
                time.sleep(2)
                __StationDone__()
                return
        except TimeoutException:
            try :
                StationStatus = WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="請將箱子放置於輸送帶。"]')))
                if ServiceType == "Internal Tote-in" :
                    print(NewRegisterToteList)
                    __InternalToteInAPI__(BookingNumber,StationKey,NewRegisterToteList)
                    time.sleep(2)
                    __StationDone__()
                    return
            except TimeoutException:
                print(StationKey + " Error")
    # 503 or 751 station
    elif StationKey == "503" or StationKey == "751" :
        print(f"Try to open {StationKey}")
        __InputBookingNoEnterStation__(BookingNumber)
        try :
            WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,"//*[text()='空箱送出中，請稍候。']")))
        except TimeoutException :
            print("Station occurs error, Please check")
     # 505 or 752 station
    elif StationKey == "505" or StationKey == "752" :
        print(f"Try to open {StationKey}")
        __InputBookingNoEnterStation__(BookingNumber)
        try :
            WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,"//*[text()='貨箱送出中，請稍候。']")))
        except TimeoutException :
            print("Station occurs error, Please check")

def __InputBookingNoEnterStation__(BookingNumber):
    StationEntryele = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,"//*[text()='手動輸入']")))
    StationEntryele.click()
    InputBookingNumberEle = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,'//input[@type="text"]')))
    InputBookingNumberEle.click()
    InputBookingNumberEle.send_keys(f'{BookingNumber[-8:]}')
    driver.find_element(By.XPATH,"//*[text()='確認']").click()
    StationStatusText = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[@class="story-patientblock-content-title whitespace-pre-wrap"]')))
    print(StationStatusText.text)

    if StationStatusText.text == "非預約時間，請點擊尋找協助。" :
        if TestEnv.lower() == "dev" :
            OperatorPassword = "9d0bb6471"
        else:
            OperatorPassword = "958c0b310"
        driver.find_element(By.XPATH,'(//*[text()="尋求協助"])[last()]').click()
        OperatorLogin = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[text()="工作人員登入"]')))
        OperatorLogin.click()
        OperatorInput = WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,"//*[text()='手動輸入']")))
        OperatorInput.click()
        Input = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,'//input[@type="text"]')))
        Input.click()
        Input.send_keys(f"{OperatorPassword}")
        driver.find_element(By.XPATH,"//*[text()='確認']").click()
        Confirm = WebDriverWait(driver,5).until(EC.visibility_of_element_located((By.XPATH,"//*[text()='批准']")))
        Confirm.click()
    else :
        pass