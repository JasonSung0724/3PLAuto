import requests
from GlobalVar import *
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def __MMSlogin__(MMSAccount,MMSPasword):
    global MMStoken
    Login_url = f'https://mms-user-{TestEnv.lower()}.hkmpcl.com.hk/user/login/merchantAppLogin2'
    login_request_body = {
        "password": MMSPasword,
        "username": MMSAccount
    }
    MMSTokenresponse = requests.post(Login_url , json=login_request_body)
    AccessToken = MMSTokenresponse.json()['accessToken']
    MMStoken = AccessToken
    return AccessToken

def __CreateCollectionBooking__(TY11=0,TY12=0,TY14=0):
    headers = {
                'Authorization' : f'Bearer {MMStoken}'
            }
    GetCollectionQuotqaPayload = {
                            "fullCompTote": TY11,
                            "twoCompTote": TY12,
                            "fourCompTote": TY14,
                            "quotaType": "TOTE_COLLECTION",
                            "warehouse": "TY3F",
                            "isSpecial": False,
                            "isOverSell": False
                        }
    GetQuotaURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/wms/quota'
    QuotaResponse = requests.post(GetQuotaURL,json=GetCollectionQuotqaPayload,headers=headers).json()
    Quota = QuotaResponse['quotaTimeslotResponseDataList'][0]
    CreateCollectionBody = {
                            "collectionStartTime": Quota['startTimestamp'],
                            "collectionEndTime": Quota['endTimestamp'],
                            "warehouseId": "TY3F",
                            "totesCollectionDetailList": [
                                {
                                "toteType": "ONE_COMP",
                                "unitAmount": TY11
                                },
                                {
                                "toteType": "TWO_COMP",
                                "unitAmount": TY12
                                },
                                {
                                "toteType": "FOUR_COMP",
                                "unitAmount": TY14
                                }
                            ],
                            "timeSlotRequestData": {
                                "special": False,
                                "timeslot": Quota['timeslot'],
                                "timeslotDate": Quota['timeslotDate'],
                                "timeslotType": Quota['timeslotType']
                            }
                            }
    CreateCollectionAPI = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/tote/collection'
    CollectionBooking = requests.post(CreateCollectionAPI,json=CreateCollectionBody,headers=headers)
    print(CollectionBooking)
    if CollectionBooking.status_code == 201 :
        print('Create collection booking success')
        GetBookingNumber = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/tote/collection?sort=collectionId&sortType=DESC&pageSize=10&page=1'
        BookingRecord = requests.get(GetBookingNumber,headers=headers).json()
        BookingNumber = BookingRecord['content'][0]['collectionId']
        __KIOSKFlow__(BookingNumber)
    else:
        print('Create collection booking fail')
        
def __OpenStaiton__():
    Station503 = WebDriverWait(driver,2).until(EC.visibility_of_element_located((By.XPATH,"(//*[text()='503'])[last()]/../..")))
    Station503.click()
    OK = WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//*[text()='OK']")))
    OK.click()


def __KIOSKFlow__(BookingNumber):
    global driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    driver = webdriver.Chrome(options=chrome_options)
    SelectStation = f'https://mwms-kiosk-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/selectStation'
    driver.get(SelectStation)
    AuthenticateForStation = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/authenticate_for_station'
    AuthBudy = {
                "userName": "selectPage",
                "userPassword": ""
                }
    AuthenticateResponse = requests.post(AuthenticateForStation,json=AuthBudy).json()
    StationToken = AuthenticateResponse['data']['token']
    StationHeaders = {
                        'Authorization' : f'Bearer {StationToken}'
                    }
    GetStationStatus = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/api/get_warehouse_station_list'
    StationStatus = requests.post(GetStationStatus,headers=StationHeaders).json()
    Station503 = WebDriverWait(driver,2).until(EC.visibility_of_element_located((By.XPATH,"(//*[text()='503'])[last()]/../..")))
    print(Station503.is_enabled())
    if Station503.is_enabled() == False :
        if StationStatus['data'][2]['stationStatus'][1]['inUse'] == True :
            RemoveStation = driver.find_element(By.XPATH,"//*[text()='強制移除']")
            RemoveStation.click()
            __OpenStaiton__()
            __OpenStaiton__()
        else:
            Station503 = WebDriverWait(driver,2).until(EC.visibility_of_element_located((By.XPATH,"(//*[text()='503'])[last()]/../..")))
            Station503.click()
            OK = WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//*[text()='OK']")))
            OK.click()
    else:
        print('Station Error')    
    time.sleep(1)
    StationEntryele = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH,"//*[text()='手動輸入']")))
    StationEntryele.click()
    InputBookingNumberEle = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH,'//input[@type="text"]')))
    InputBookingNumberEle.click()
    time.sleep(10)




