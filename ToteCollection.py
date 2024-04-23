import requests
from GlobalVar import *
import time
from StationFlow import __KIOSKFlow__

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
        

def __CollectionAPI__(BookingNumber,stationKey,ToteList):
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_COLLECTION&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Collection Task no. " + TaskNo)
    containerCode = ','.join(map(str, ToteList))
    M5111URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_location_report'
    M5111Body = {
                "msgTime": "2021-09-01T19:02:33.597+08:00",
                "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
                "data": [
                    {
                        "taskNo": TaskNo,
                        "containerCode": containerCode,
                        "stationKey": stationKey,
                        "detail": [
                            {
                                "arriveCode": "normal",
                                "remarks": ""
                            }
                        ]
                    }
                ]
            }
    print(M5111Body)
    M5111SendRequest = requests.post(M5111URL,json=M5111Body)
    print(M5111SendRequest)
    time.sleep(3)
    TY11container = ""
    TY12container = ""
    TY14container = ""
    for code in ToteList:
        if str(code).startswith('11'):
            TY11container += str(code) + ','
        elif str(code).startswith('12'):
            TY12container += str(code) + ','
        elif str(code).startswith('14'):
            TY14container += str(code) + ','
    TY11container = TY11container.rstrip(',')
    TY12container = TY12container.rstrip(',')
    TY14container = TY14container.rstrip(',')

    M5119URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/empty_tote_out_report'
    M5119Body = {
                "msgTime": "2021-09-01T19:02:33.597+08:00",
                "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
                "data": [
                    {
                        "taskNo": "20230419-M14-8596d6ca99e24fafb",
                        "isSuccess": True,
                        "detail": [
                            {
                                "cellsNumber": 11,
                                "containerCodes": TY11container,
                                "errorCode": None,
                                "remarks": None
                            },
                            {
                                "cellsNumber": 12,
                                "containerCodes": TY12container,
                                "errorCode": None,
                                "remarks": None
                            },
                            {
                                "cellsNumber": 14,
                                "containerCodes": TY12container,
                                "errorCode": None,
                                "remarks": None
                            }
                        ]
                    }
                ]
            }
    print(M5119Body)
    M5119SendRequsets = requests.post(M5119URL,json=M5111Body).json()
    print(M5119SendRequsets)
