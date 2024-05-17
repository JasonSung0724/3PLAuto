import requests
import json
import time
from GlobalVar import *


def __WMSLogin__():
    global WMStoken
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    LoginURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/sso/login'
    Payload = {
        "username": "TYWMS.TestAdmin1",
        "password": "1qaz@WSX"
    }
    TokenResponse = requests.post(LoginURL, json=Payload).json()
    try:
        WMStoken = TokenResponse['data']['token']
        cur.execute(
            f"UPDATE `Var_3PL_Table` SET `WMStoken` = '{WMStoken}' WHERE ID = 1")
        conn.commit()
        print("WMSCMS login success")
        print(f"Current environment : {TestEnv}")
        return WMStoken
    except:
        print(f"Current environment : {TestEnv}")
        print(f'!!!!!!!!!!Get token fail "{TestEnv}"!!!!!!!!!!')


def __GetBookingNumber__(headers, page=1):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
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
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    WMStoken = Result[0]
    conn.commit()
    CreateBookingURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/internal/booking'
    Payload = {"toteCodes": ToteList}
    if TestEnv == 'dev':
        headers = {'Authorization': f'Bearer {WMStoken}'}
    else:
        headers = {'authorization': f'Bearer {WMStoken}'}
    retry = 0
    while retry < 4:
        BookingResponse = requests.post(
            CreateBookingURL, json=Payload, headers=headers).json()
        if BookingResponse['status'] == 200:
            BookingNumber = __GetBookingNumber__(headers)
            print(BookingNumber)
            return BookingNumber

        elif BookingResponse['status'] == 5043 and retry > 3:
            print(
                "Create internal tote-in booking failed, trying again after 2 seconds...")
            retry += 1
            time.sleep(2)
        else:
            print("Create internal tote-in booking failed")
            return BookingResponse['message']


def __InternalToteInAPI__(BookingNumber, StationKey, ToteList):
    print(f'Booking Number : {BookingNumber} , StationKey : {StationKey}')
    print("Tote List")
    print(ToteList)
    time.sleep(2)
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_RETURN&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Internal Tote in Task no. " + TaskNo)
    APIheaders = {"Content-Type": "application/json"}
    time.sleep(2)
    for tote in ToteList:
        print(tote)
        time.sleep(3)
        M5102URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_status_report'
        M5102Body = {
            "msgTime": "2022-11-01T19:02:33.597+08:00",
            "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
            "data": [
                {
                    "stationKey": StationKey,
                    "taskNo": TaskNo,
                    "containerCode": tote,
                    "weight": 3000,
                    "success": True,
                    "errorCode": "",
                    "remarks": ""
                }
            ]
        }
        print(M5102Body)
        M5102SendRequsets = requests.post(
            M5102URL, json=M5102Body, headers=APIheaders).json()
        print(M5102SendRequsets)
    print("Internal API flow compledted")
