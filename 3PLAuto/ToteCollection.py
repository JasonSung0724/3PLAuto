import requests
import json
from GlobalVar import *
import time
from datetime import datetime, timedelta


def __MMSlogin__(MMSAccount, MMSPasword):
    Login_url = f'https://mms-user-{TestEnv.lower()}.hkmpcl.com.hk/user/login/merchantAppLogin2'
    login_request_body = {
        "password": MMSPasword,
        "username": MMSAccount
    }
    MMSTokenresponse = requests.post(Login_url, json=login_request_body)
    AccessToken = MMSTokenresponse.json()['accessToken']
    cur.execute(
        f"UPDATE `Var_3PL_Table` SET `MMStoken` = '{AccessToken}' WHERE ID = 1")
    return AccessToken


def __CreateCollectionBooking__(TY11=0, TY12=0, TY14=0):
    cur.execute("SELECT MMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMStoken = Result[0]
    conn.commit()
    headers = {
        'Authorization': f'Bearer {MMStoken}'
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
    QuotaResponse = requests.post(
        GetQuotaURL, json=GetCollectionQuotqaPayload, headers=headers).json()
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
    CollectionBooking = requests.post(
        CreateCollectionAPI, json=CreateCollectionBody, headers=headers)
    if CollectionBooking.status_code == 201:
        print('Create collection booking success')
        GetBookingNumber = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/tote/collection?sort=collectionId&sortType=DESC&pageSize=10&page=1'
        BookingRecord = requests.get(GetBookingNumber, headers=headers).json()
        BookingNumber = BookingRecord['content'][0]['collectionId']
        return BookingNumber
    else:
        print('Create collection booking fail')

# 待修改，註冊且InternalToteIn後容易發生預定數量和實際入倉數量不符的問題
# 利用InternalToteIn的Tote容易導致Collection到沒有成功入倉的箱子


def __CollectionAPI__(BookingNumber, stationKey):
    CheckDict = __GetCollectionBookingInfo__(BookingNumber)
    TY11 = CheckDict[BookingNumber]['TY11']
    TY12 = CheckDict[BookingNumber]['TY12']
    TY14 = CheckDict[BookingNumber]['TY14']
    ToteList = []
    if TY11 != 0:
        TY11ToteList = __CollectionGetTotes__("TY11", TY11)
        for TY11tote in TY11ToteList:
            ToteList.append(TY11tote)
    if TY12 != 0:
        TY12ToteList = __CollectionGetTotes__("TY12", TY12)
        for TY12tote in TY12ToteList:
            ToteList.append(TY12tote)
    if TY14 != 0:
        TY14ToteList = __CollectionGetTotes__("TY14", TY14)
        for TY14tote in TY14ToteList:
            ToteList.append(TY14tote)
    print(ToteList)
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_COLLECTION&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Collection Task no. " + TaskNo)
    M5111URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_location_report'
    for perTote in ToteList:
        M5111Body = {
            "msgTime": "2021-09-01T19:02:33.597+08:00",
            "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
            "data": [
                {
                    "taskNo": TaskNo,
                    "containerCode": str(perTote),
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
        M5111SendRequest = requests.post(M5111URL, json=M5111Body)
        print(M5111SendRequest)
    time.sleep(2)
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
                        "containerCodes": TY14container,
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


def __GetCollectionBookingInfo__(BookingNumber):
    Current = datetime.now()
    StartTime = Current - timedelta(days=1)
    StartDateTime = StartTime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    EndTime = Current + timedelta(days=7)
    EndDateTime = EndTime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    print(WMStokenResult)
    WMStoken = WMStokenResult[0]
    conn.commit()
    GetURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job?startTimestamp={StartDateTime}&endTimestamp={EndDateTime}&bookingType=Tote+Collect&pageNo=1&pageSize=30'
    WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
    Response = requests.get(GetURL, headers=WMSheaders).json()
    print(Response)
    BookingList = Response['data']['bookingDetails']
    BookingDict = {}
    for booking in BookingList:
        if BookingNumber == booking['bookingNo']:
            BookingDict[booking['bookingNo']] = {
                "TotalBatch": booking["estimatedToteQuantityTotal"],
                "TY11": booking["estimatedToteQuantity1C"],
                "TY12": booking["estimatedToteQuantity2C"],
                "TY14": booking["estimatedToteQuantity4C"]
            }
            print(BookingDict)
            return BookingDict
        else:
            pass
    print(f"Can not found booking info : {BookingNumber}")


def __CollectionGetTotes__(CompartmentType, TotesQty):
    # 獲取Tote , 條件(Available for rent , In System , TY3F)
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    WMStoken = WMStokenResult[0]
    conn.commit()
    WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
    GetTotesURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote?pageNo=1&pageSize=200&sort=toteCode:asc&status=Available+for+rent&warehouseCode=TY3F&toteType={CompartmentType}&locationType=In+System'
    GetToteResponse = requests.get(GetTotesURL, headers=WMSheaders).json()
    TotesRecord = GetToteResponse['data']['totes']
    ToteList = []
    for i in range(TotesQty):
        ToteList.append(TotesRecord[len(TotesRecord)-i-1]['toteCode'])
    # 找第一頁 size 200 開始倒數抓需要的tote數量
    print(ToteList)
    return ToteList
