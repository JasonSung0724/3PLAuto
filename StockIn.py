import requests
import time
import json
import re
from GlobalVar import *
from internalToteIn import __WMSLogin__

BookingDict = {}


def __GetBookingInfo__(BookingNumber):
    global BookingDict
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    WMStoken = WMStokenResult[0]
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    if TestEnv == 'dev':
        WMSheaders = {'Authorization': f'Bearer {WMStoken}'
                      }
    else:
        WMSheaders = {'authorization': f'Bearer {WMStoken}'
                      }
    GetBookingInfoURL = f'https://mwms-whtsy-dev.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job/tote_record?bookingType=Stock+In&bookingNo={BookingNumber}&pageNo=1&pageSize=100'
    BookingResponse = requests.get(GetBookingInfoURL, headers=WMSheaders)
    BookingInfo = BookingResponse.json()
    print(BookingResponse.status_code)
    BookingDict = {}
    if BookingResponse.status_code == 200:
        BookingInfoList = BookingInfo['data']['bookingRecords']
        if BookingInfoList[0]['status'] == "MAPPED":
            print("Total batches count : " + str(len(BookingInfoList)))
            for batchinfo in BookingInfoList:
                Ean = batchinfo['ean']
                Compartment = batchinfo['compartment']
                SKUuuid = batchinfo['uuid']
                QTY = batchinfo['qty']
                ToteCode = batchinfo['toteNo']
                SKUdetailURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/sku_inventory?pageNo=1&pageSize=10&skuUuid={SKUuuid}'
                SKUdetailResponse = requests.get(
                    SKUdetailURL, headers=WMSheaders).json()
                SKUdetail = SKUdetailResponse['data']['skuInventories'][0]
                skuWeight_unit = re.match(r"(\d+)", SKUdetail['skuWeight'])
                skuWeight = float(skuWeight_unit.group(1))
                if ToteCode in BookingDict:
                    BookingDict[ToteCode][Compartment] = {
                        'ean': Ean,
                        'SKUuuid': SKUuuid,
                        'qty': QTY,
                        'length': SKUdetail['length'],
                        'width': SKUdetail['width'],
                        'height': SKUdetail['height'],
                        'skuWeight': skuWeight,
                        'merchantCode': SKUdetail['merchantCode'],
                        'warehouseCode': SKUdetail['mmsSkuCode'].split('_')[0] + "98"
                    }
                else:
                    BookingDict[ToteCode] = {
                        Compartment: {
                            'ean': Ean,
                            'SKUuuid': SKUuuid,
                            'qty': QTY,
                            'length': SKUdetail['length'],
                            'width': SKUdetail['width'],
                            'height': SKUdetail['height'],
                            'skuWeight': skuWeight,
                            'merchantCode': SKUdetail['merchantCode'],
                            'warehouseCode': SKUdetail['mmsSkuCode'].split('_')[0] + "98"
                        }
                    }
            return BookingDict
        else:
            status = "Stock-in Booking status has not been change to MAPPED yet."
            print(status)
            # return status


def __StockInAPIFlow__(BookingNumber, StationKey):
    global BookingDict
    # Get Task Number
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_IN&bookingNo={BookingNumber}'
    APIheaders = {"Content-Type": "application/json"}
    TaskResponse = requests.get(GetTaskNoURL, headers=APIheaders).json()
    print(TaskResponse)
    BookingDict = __GetBookingInfo__(BookingNumber)
    if TaskResponse['resultStatus'] == "SUCCESS":
        batchesList = TaskResponse['responseData']
        # 整理字典
        for batch in batchesList:
            ToteCode = batch['toteCode']
            TaskNo = batch['taskNo']
            Batchid = batch['batchId']
            Compartment = __CheckCompartment__(batch['batchId'])[0]
            BookingDict[ToteCode][Compartment]['taskNo'] = TaskNo
            BookingDict[ToteCode][Compartment]['BatchId'] = Batchid
        # M5102 + M5123
        toteCompleted = []
        for batch in batchesList:
            if batch['toteCode'] in toteCompleted:
                pass
            else:
                toteCompleted.append(batch['toteCode'])
                __M5102__(batch, StationKey)
        # M5104
        time.sleep(2)
        for toteCode in BookingDict.keys():
            __M5104__(toteCode, StationKey)
            time.sleep(2)

        # M5112
        time.sleep(2)
        for toteCode in BookingDict.keys():
            __M5112__(toteCode)
            time.sleep(2)
        # M5103
        time.sleep(2)
        __M5103__()
        print("Stock-in flow finished , please check booking status")
        BookingDict = {}
        return "Stock-in flow finished , please check booking status"
    else:
        print(TaskResponse['resultStatus'])
        return TaskResponse['resultStatus']


def __CheckCompartment__(BatchId):
    EnCheck = re.compile('[A-Za-z]')
    Result = EnCheck.findall(BatchId)
    return Result


def __ToteWeight__(toteCode):
    global BookingDict
    if toteCode.startswith('11'):
        TotalWeight = 3270
    elif toteCode.startswith('12'):
        TotalWeight = 3600
    elif toteCode.startswith('14'):
        TotalWeight = 4070
    for batches, batches_data in BookingDict[toteCode].items():
        skuweight = batches_data['skuWeight']
        qty = batches_data['qty']
        TotalWeight += float(skuweight) * float(qty)
        print(TotalWeight)
        return TotalWeight


def __M5102__(Task, StationKey):
    global BookingDict
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    M5102URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_status_report'
    APIheaders = {"Content-Type": "application/json"}
    TaskNo = Task['taskNo']
    toteCode = Task['toteCode']
    TotalWeight = __ToteWeight__(toteCode)
    M5102Body = json.dumps({
        "msgTime": "2022-11-01T19:02:33.597+08:00",
        "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
        "data": [
            {
                "stationKey": StationKey,
                "taskNo": TaskNo,
                "containerCode": toteCode,
                "weight": TotalWeight,
                "success": True,
                "errorCode": "",
                "remarks": ""
            }
        ]
    })
    Response = requests.post(M5102URL, data=M5102Body,
                             headers=APIheaders).json()
    print(Response)
    print("Call M5102 Completed " + TaskNo)
    print(M5102Body)
    time.sleep(3)
    __M5123__(TaskNo)


def __M5123__(TaskNo):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    M5123URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/task_status_report'
    APIheaders = {"Content-Type": "application/json"}
    M5123Body = json.dumps({
        "msgTime": "2021-09-01T19:02:33.597+08:00",
        "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
        "data": [
            {
                "taskNo": TaskNo,
                "taskStatus": "PENDING"
            }
        ]
    })
    Response = requests.post(M5123URL, data=M5123Body,
                             headers=APIheaders).json()
    print(Response)
    print(f"Call M5123 Completed {TaskNo}")
    print(M5123Body)
    return


def __M5104__(toteCode, stationKey):
    global BookingDict
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    M5104URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_in_checking_report'
    APIheaders = {"Content-Type": "application/json"}
    first_Key = list(BookingDict[toteCode].keys())[0]
    print(first_Key)
    M5104TotalDetail = []
    for batches, batches_data in BookingDict[toteCode].items():
        if batches == "A":
            cellsCode = 1
        elif batches == "B":
            cellsCode = 2
        elif batches == "C":
            cellsCode = 3
        elif batches == "D":
            cellsCode = 4
        DetailBody = {
            "cellsCode": cellsCode,
            "originCellsCode": cellsCode,
            "warehouseId": batches_data['warehouseCode'],
            "ownerId": batches_data['merchantCode'],
            "uId": batches_data['SKUuuid'],
            "eanCode": batches_data['ean'],
            "actualEanCode": batches_data['ean'],
            "supervisorId": "id001",
            "length": batches_data['length'],
            "width": batches_data['width'],
            "height": batches_data['height'],
            "weight": batches_data['skuWeight'],
            "qty": batches_data['qty'],
            "actualQty": batches_data['qty'],
            "success": True,
            "errorCode": "",
            "remarks": "",
            "lotId": batches_data['BatchId']
        }
        M5104TotalDetail.append(DetailBody)
    M5104Body = json.dumps({
        "msgTime": "2022-11-01T19:02:33.597+08:00",
        "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
        "data": [
            {
                "taskNo": BookingDict[toteCode][first_Key]['taskNo'],
                "containerType": 1,
                "containerCode": toteCode,
                "isTaskComplete": True,
                "isRemoved": False,
                "stationKey": stationKey,
                "operatorId": "1",
                "taskType": 1,
                "detail": M5104TotalDetail
            }
        ]
    })
    Response = requests.post(M5104URL, data=M5104Body,
                             headers=APIheaders).json()
    print(Response)
    print(toteCode + " M5104 task completed.")
    print(M5104Body)


def __M5112__(toteCode):
    global BookingDict
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    TotalWeight = __ToteWeight__(toteCode)
    first_key = list(BookingDict[toteCode].keys())[0]
    TaskNo = BookingDict[toteCode][first_key]['taskNo']
    APIheaders = {"Content-Type": "application/json"}
    M5112URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_weight_report'
    M5112Body = json.dumps({
        "msgTime": "2021-09-01T19:02:33.597+08:00",
        "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
        "data": [
            {
                "taskNo": TaskNo,
                "containerCode": toteCode,
                "balanceCode": "1332",
                "weight": TotalWeight
            }
        ]
    })
    Response = requests.post(M5112URL, data=M5112Body,
                             headers=APIheaders).json()
    print(Response)
    print(toteCode + " M5112 task completed.")
    print(M5112Body)


def __M5103__():
    global BookingDict
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    for toteCode in BookingDict.keys():
        TotalData = []
        first_key = list(BookingDict[toteCode].keys())[0]
        dataDetail = {
            "containerCode": toteCode,
            "layer": 1,
            "location": "110111",
                        "taskNo": BookingDict[toteCode][first_key]['taskNo']
        }
        TotalData.append(dataDetail)
        APIheaders = {"Content-Type": "application/json"}
        M5103URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/launch_container_report'
        M5103Body = json.dumps({
            "data": TotalData,
            "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
            "msgTime": "2021-09-01T19:02:33.597+08:00"
        })
        Response = requests.post(M5103URL, data=M5103Body,
                                 headers=APIheaders).json()
        print(Response)
        print("M5103 task completed")
        print(M5103Body)
        time.sleep(2)


# __StockInAPIFlow__("SITY3F00004245", "102")
