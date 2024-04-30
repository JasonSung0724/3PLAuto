import requests
from GlobalVar import *
from internalToteIn import __WMSLogin__

__WMSLogin__()
BookingNumber = 'SITY3F00004186'
cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
WMStokenResult = cur.fetchone()
WMStoken = WMStokenResult[0]
conn.commit()
WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
GetBookingInfoURL = f'https://mwms-whtsy-dev.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job/tote_record?bookingType=Stock+In&bookingNo={BookingNumber}&pageNo=1&pageSize=100'
BookingResponse = requests.get(GetBookingInfoURL,headers=WMSheaders)
BookingInfo = BookingResponse.json()
print(BookingResponse.status_code)
if BookingResponse.status_code == 200 :
    BookingInfoList = BookingInfo['data']['bookingRecords']
    if BookingInfoList[0]['status'] == "MAPPED" :
        print("Total batches count : " + str(len(BookingInfoList)))
        
        # return
    else:
        status = "Stock-in Booking status has not been change to MAPPED yet."
        print(status)
        # return status
