import requests
from GlobalVar import *

def __WMSLogin__():
    global WMStoken
    LoginURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/sso/login'
    Payload = {
                "username": "TYWMS.TestAdmin1",
                "password": "1qaz@WSX"
    }
    TokenResponse = requests.post(LoginURL,json=Payload).json()
    WMStoken = TokenResponse['data']['token']
    return WMStoken

def __CreateInternalToteInBooking__(ToteList):
    CreateBookingURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/internal/booking'
    Payload = {"toteCodes": ToteList}
    headers = {'Authorization' : f'Bearer {WMStoken}'}
    BookingResponse = requests.post(CreateBookingURL,json=Payload,headers=headers).json()
    print(BookingResponse)
    MaxPage = 1
    GetBookingNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote/booking/internal/tote_in?currentPage=1&pageSize=10&sort=bookingNo:asc&pageNo={MaxPage}'
    GetBookingNoResponse = requests.get(GetBookingNoURL,headers=headers).json()
    MaxPage = GetBookingNoResponse['data']['pagination']['totalPages']
    GetBookingNoResponse = requests.get(GetBookingNoURL,headers=headers).json()
    BookingNumber = GetBookingNoResponse['data']['bookings'][-1]
    return BookingNumber


def __InternalToteInAPI__(BookingNumber,StationKey,ToteList):
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=TOTE_RETURN&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    TaskNo = TaskNoResponse['responseData'][0]['taskNo']
    print("Get Internal Tote in Task no. " + TaskNo)
    containerCode = ','.join(map(str, ToteList))
    M5102URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_status_report'
    M5102Body = {
                "msgTime": "2022-11-01T19:02:33.597+08:00",
                "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
                "data": [
                {
                    "stationKey": StationKey,
                    "taskNo": TaskNo,
                    "containerCode": containerCode,
                    "weight": 100,
                    "success": True,
                    "errorCode": "",
                    "remarks": ""
                }
                ]
            }
    M5102SendRequsets = requests.post(M5102URL,json=M5102Body).json()
    print(M5102SendRequsets)
