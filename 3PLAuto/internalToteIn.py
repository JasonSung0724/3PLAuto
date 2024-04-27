import requests
import json
import time
from GlobalVar import *


def __WMSLogin__():
    global WMStoken
    LoginURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/sso/login'
    Payload = {
        "username": "TYWMS.TestAdmin1",
        "password": "1qaz@WSX"
    }
    TokenResponse = requests.post(LoginURL, json=Payload).json()
    WMStoken = TokenResponse['data']['token']
    cur.execute(
        f"UPDATE `Var_3PL_Table` SET `WMStoken` = '{WMStoken}' WHERE ID = 1")
    conn.commit()
    print("WMSCMS login success")
    return WMStoken


def __GetBookingNumber__(headers, page=1):
    if page == 1:
        GetBookingNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/booking/internal/tote_in?currentPage=1&pageSize=10&sort=bookingNo:asc&pageNo={page}'
        GetBookingNoResponse = requests.get(
            GetBookingNoURL, headers=headers).json()
        MaxPage = GetBookingNoResponse['data']['pagination']['totalPages']
        return __GetBookingNumber__(headers, MaxPage)
    else:
        print("Search booking : " + str(page))
        GetBookingNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/booking/internal/tote_in?currentPage=1&pageSize=10&sort=bookingNo:asc&pageNo={page}'
        GetBookingNoResponse = requests.get(
            GetBookingNoURL, headers=headers).json()
        BookingNumber = GetBookingNoResponse['data']['bookings'][-1]['bookingNo']
        return BookingNumber


def __CreateInternalToteInBooking__(ToteList):
    CreateBookingURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/internal/booking'
    Payload = {"toteCodes": ToteList}
    headers = {'Authorization': f'Bearer {WMStoken}'}
    retry = 0
    while retry < 4:
        BookingResponse = requests.post(
            CreateBookingURL, json=Payload, headers=headers)
        if BookingResponse.status_code == 200:
            BookingNumber = __GetBookingNumber__(headers)
            print(BookingNumber)
            return BookingNumber

        elif BookingResponse.status_code == 5043:
            print(
                "Create internal tote-in booking failed, trying again after 2 seconds...")
            retry += 1
            time.sleep(2)
        else:
            print("Create internal tote-in booking failed")
            break


def __InternalToteInAPI__(BookingNumber, StationKey, ToteList):
    time.sleep(2)
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_RETURN&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Internal Tote in Task no. " + TaskNo)
    time.sleep(2)
    for tote in ToteList:
        print(tote)
        time.sleep(1)
        M5102URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_status_report'
        M5102Body = {
            "msgTime": "2022-11-01T19:02:33.597+08:00",
            "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
            "data": [
                {
                    "stationKey": StationKey,
                    "taskNo": TaskNo,
                    "containerCode": tote,
                    "weight": 100,
                    "success": True,
                    "errorCode": "",
                    "remarks": ""
                }
            ]
        }
        print(M5102Body)
        M5102SendRequsets = requests.post(M5102URL, json=M5102Body).json()
        print(M5102SendRequsets)
