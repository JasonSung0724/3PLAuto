import requests , re
from GlobalVar import *
from internalToteIn import __WMSLogin__

def __GetBookingInfo__(BookingNumber):
    __WMSLogin__()
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    WMStoken = WMStokenResult[0]
    conn.commit()
    WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
    GetBookingInfoURL = f'https://mwms-whtsy-dev.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job/tote_record?bookingType=Stock+In&bookingNo={BookingNumber}&pageNo=1&pageSize=100'
    BookingResponse = requests.get(GetBookingInfoURL,headers=WMSheaders)
    BookingInfo = BookingResponse.json()
    print(BookingResponse.status_code)
    BookingDict = {}
    if BookingResponse.status_code == 200 :
        BookingInfoList = BookingInfo['data']['bookingRecords']
        if BookingInfoList[0]['status'] == "MAPPED" :
            print("Total batches count : " + str(len(BookingInfoList)))
            for batchinfo in BookingInfoList:
                Ean = batchinfo['ean']
                Compartment = batchinfo['compartment']
                SKUuuid = batchinfo['uuid']
                QTY = batchinfo['qty']
                ToteCode = batchinfo['toteNo']                
                if ToteCode in BookingDict :
                    BookingDict[ToteCode][Compartment] = {
                        'ean': Ean,
                        'SKUuuid': SKUuuid,
                        'qty': QTY,
                    }
                else:
                    BookingDict[ToteCode] = {
                        Compartment: {
                            'ean': Ean,
                            'SKUuuid': SKUuuid,
                            'qty': QTY,
                        }
                    }
            return BookingDict
        else:
            status = "Stock-in Booking status has not been change to MAPPED yet."
            print(status)
            # return status

def __GetTaskNo__(BookingNumber):
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_IN&bookingNo={BookingNumber}'
    APIheaders = {"Content-Type": "application/json"}
    TaskResponse = requests.get(GetTaskNoURL,headers=APIheaders).json()
    print(TaskResponse)
    BookingDict = __GetBookingInfo__(BookingNumber)
    if TaskResponse['resultStatus'] == "SUCCESS" :
        batchesList = TaskResponse['responseData']
        for batch in batchesList:
            ToteCode = batch['toteCode']
            TaskNo = batch['taskNo']
            Batchid = batch['batchId']
            Compartment = __CheckCompartment__(batch['batchId'])[0]
            BookingDict[ToteCode][Compartment]['TaskNo'] = TaskNo
            BookingDict[ToteCode][Compartment]['BatchId'] = Batchid 
        print(BookingDict)
    else :
        print(TaskResponse['resultStatus'])
        return TaskResponse['resultStatus']

def __CheckCompartment__(BatchId):
    EnCheck = re.compile('[A-Za-z]')
    Result = EnCheck.findall(BatchId)
    return Result

def __M5102__(BookingDict):
    M5102URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_status_report'
    APIheaders = {"Content-Type": "application/json"}
    M5102Body = {
                    "msgTime": "2022-11-01T19:02:33.597+08:00",
                    "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
                    "data": [
                    {
                        "stationKey": "109",
                        "taskNo": "20240326-M01-00000000000000318",
                        "containerCode": "1100052155",
                        "weight": 100,
                        "success": True,
                        "errorCode": "",
                        "remarks": ""
                    }
    ]
}

# __GetTaskNo__("SITY3F00004197")