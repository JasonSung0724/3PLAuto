import requests
import json
import re
import time
from GlobalVar import *
import math


def __StockOutAPI__(BookingNumber):
    Consolidation = __ConsolidationTaskHandle__(BookingNumber)
    time.sleep(2)
    CycleCount = __CycleCount__(BookingNumber)
    WeigthCheck = __WeigthCheck__(BookingNumber)
    if CycleCount == False and WeigthCheck == False:
        print("Stock-out flow error")
    elif CycleCount == True or WeigthCheck == True:
        print("Please check stock-out status , should change to 'ready'")


def __GetBookingInfo__(BookingNumber):
    GetStockOutInfoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job/tote_record?bookingType=Stock+Out&bookingNo={BookingNumber}&pageNo=1&pageSize=100'
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    WMStoken = WMStokenResult[0]
    conn.commit()
    WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
    BookingInfoResponse = requests.get(
        GetStockOutInfoURL, headers=WMSheaders).json()
    BatchQTY = BookingInfoResponse['data']['pagination']['totalElements']
    print(f"Stock-out {BatchQTY} batch")
    BatchDict = {}
    if BatchQTY <= 100:
        BookingInfoList = BookingInfoResponse['data']['bookingRecords']
        for batch in BookingInfoList:
            BatchDict[batch['batchId']] = batch
    print(BatchDict)
    return BatchDict


def __ConsolidationTaskHandle__(BookingNumber):
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_OUT_CONSOLIDATION&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    print("Consolidation Get Task Number : " + TaskNoResponse['resultStatus'])
    SKUdict = __GetBookingInfo__(BookingNumber)
    if TaskNoResponse['resultStatus'] == "SUCCESS":
        TaskList = TaskNoResponse['responseData']
        for Task in TaskList:
            TaskNo = Task['taskNo']
            Compartment = Task['batches'][0]['fromTote']
            if Compartment.startswith("14"):
                CompartmentType = "TY14"
                CompartmentQty = 4
            elif Compartment.startswith("12"):
                CompartmentType = "TY12"
                CompartmentQty = 2
            else:
                print("Please check consolidation task , occrus error")

            TotesQty = math.ceil(len(Task['batches'])/CompartmentQty)
            TotesList = __GetTotes__(CompartmentType, TotesQty)
            M5121Totaldata = []
            j = 0  # 計算空箱
            BatchesList = Task['batches']
            for i in range(len(Task['batches'])):  # 迴圈處理任務中的每個箱子
                BatchId = BatchesList[i]['batchId']
                FromTote = BatchesList[i]['fromTote']
                FromCells = BatchesList[i]['fromComp']
                Ean = SKUdict[BatchId]['ean']
                UUID = SKUdict[BatchId]['uuid']
                QTY = SKUdict[BatchId]['qty']
                M5121data = {
                    "taskNo": TaskNo,
                    "isNormalComplete": True,
                    "isLast": i == len(BatchesList) - 1,
                    "stationKey": "test_7f036537fed7",
                    "operatorId": "test_776ab1b1b4d2",
                    "detail": [
                        {
                            "uId": UUID,
                            "eanCode": Ean,
                            "actualEanCode": Ean,
                            "isLock": False,
                            "fromCellsCode": FromCells,
                            "toCellsCode": TotesList[j]['count'],
                            "qty": QTY,
                            "fromErrorCode": "",
                            "fromRemarks": "",
                            "toErrorCode": "",
                            "toRemarks": ""
                        }
                    ],
                    "fromContainerCode": FromTote,
                    "toContainerCode": TotesList[j]['ToteCode'],
                    "errorCode": "",
                    "remarks": ""
                }
                M5121Totaldata.append(M5121data)
                TotesList[j]['count'] += 1
                if TotesList[j]['count'] > CompartmentQty and j <= TotesQty - 1:
                    j += 1
            M5121Body = json.dumps({
                "msgTime": "test_23b549b76fda",
                "msgId": "test_7817ccb87aba",
                "data": M5121Totaldata
            })
            APIheaders = {"Content-Type": "application/json"}
            M5121URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/consolidation_complete_report'
            M5121Response = requests.post(
                M5121URL, data=M5121Body, headers=APIheaders).json()
            print(M5121Body)
            print(M5121Response)
        print("Stock-out consolidation completed")
        time.sleep(2)
        return True
    else:
        print("Maybe shouldn't consolidate or occur dirty data error.")
        return False


def __GetTotes__(CompartmentType, TotesQty):
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
        ToteList.append(
            {"ToteCode": TotesRecord[len(TotesRecord)-i-1]['toteCode'], "count": 1})
    # 找第一頁 size 200 開始倒數抓需要的tote數量
    print(ToteList)
    return ToteList


def __GetSKUinfo__(uuid):
    URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/sku_inventory?pageNo=1&pageSize=10&skuUuid={uuid}&sort=skuUuid:desc'
    cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    WMStokenResult = cur.fetchone()
    WMStoken = WMStokenResult[0]
    conn.commit()
    WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
    Response = requests.get(url=URL, headers=WMSheaders).json()
    SKUinfo = Response['data']['skuInventories'][0]
    return SKUinfo


def __CycleCount__(BookingNumber):
    SKUdict = __GetBookingInfo__(BookingNumber)
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_OUT_CYCLE&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    print("Cycle Count Get Task Number : " + TaskNoResponse['resultStatus'])
    if TaskNoResponse['resultStatus'] == "SUCCESS":
        TaskList = TaskNoResponse['responseData']
        TaskDict = {}
        for batches in TaskList:
            if batches['taskNo'] not in TaskDict:
                TaskDict[batches['taskNo']] = [batches['batchId']]
            else:
                TaskDict[batches['taskNo']].append(batches['batchId'])
        for task, batchid in TaskDict.items():
            M5108TotalDetail = []
            # 處理同一個隔層內有兩個Batch ID 的髒資料
            try:
                TOTE = SKUdict[batchid[0]]['toteNo']
            except IndexError:
                print("Dirty data")
                return
            except KeyError:
                print(
                    f"Dirty data , have multiple batchid with same compartment {batchid[0]}")

                return
            for batch in batchid:
                Compartment = SKUdict[batch]['compartment']
                if Compartment == "A":
                    CellsCode = 1
                elif Compartment == "B":
                    CellsCode = 2
                elif Compartment == "C":
                    CellsCode = 3
                elif Compartment == "D":
                    CellsCode = 4
                UUID = SKUdict[batch]['uuid']
                QTY = SKUdict[batch]['qty']
                EAN = SKUdict[batch]['ean']
                SKUinfo = __GetSKUinfo__(UUID)
                length = SKUinfo['length']
                width = SKUinfo['width']
                height = SKUinfo['height']
                SKU_weight = re.match(r"(\d+)", SKUinfo['skuWeight'])
                weight = float(SKU_weight.group(1))
                M5108Detail = {
                    "cellsCode": CellsCode,
                    "eanCode": EAN,
                    "actualEanCode": EAN,
                    "lotId": batch,
                    "qty": QTY,
                    "actualQty": QTY,
                    "length": length,
                    "width": width,
                    "weight": weight,
                    "height": height,
                    "success": False,
                    "errorCode": "",
                    "remarks": ""
                }
                M5108TotalDetail.append(M5108Detail)
            M5108Body = json.dumps({
                "data": [
                    {
                        "taskNo": task,
                        "containerCode": TOTE,
                        "stationKey": "test_61763bae8367",
                        "operatorId": "test_9c5e08a0562b",
                        "detail": M5108TotalDetail
                    }
                ],
                "msgTime": "test_58e0dd20cdeb",
                "msgId": "test_48044c1054aa"
            })
            M5108URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/take_inventory_report'
            APIheaders = {"Content-Type": "application/json"}
            M5108Response = requests.post(
                M5108URL, data=M5108Body, headers=APIheaders).json()
            print(M5108Body)
            print(M5108Response)
        return True
    else:
        return False


def __WeigthCheck__(BookingNumber):
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_OUT_WEIGHT&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    print("Weigth Check Task Number : " + TaskNoResponse['resultStatus'])
    if TaskNoResponse['resultStatus'] == "SUCCESS":
        TaskList = TaskNoResponse['responseData']
        for task in TaskList:
            TaskNo = task['taskNo']
            ToteCode = task['toteCode']
            CorrectWeigth = float(
                (task['weightUpperLimit'] + task['weightLowerLimit'])/2)
            M5112Body = json.dumps({
                "msgTime": "2021-09-01T19:02:33.597+08:00",
                "msgId": "e4ef9fee-d6de-4bcc-9a90-cb1e091a6092",
                "data": [
                    {
                        "taskNo": TaskNo,
                        "containerCode": ToteCode,
                        "balanceCode": "1332",
                        "weight": CorrectWeigth
                    }
                ]
            })
            M5112URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/tote_weight_report'
            APIheaders = {"Content-Type": "application/json"}
            M5112Response = requests.post(
                M5112URL, data=M5112Body, headers=APIheaders).json()
            print(M5112Body)
            print(M5112Response)
            print("Weigth check completed")
    else:
        return False


__StockOutAPI__("SOTY3F00001034")
