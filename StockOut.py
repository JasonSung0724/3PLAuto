import requests , json
from GlobalVar import *
import math
TestEnv = 'staging'
def __StockOutAPI__(BookingNumber):
    GetStockOutInfoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/tote/booking_job/tote_record?bookingType=Stock+Out&bookingNo={BookingNumber}&pageNo=1&pageSize=100'
    # conn.execute("SELECT WMStoken FROM `3PL_Var_Table` WHERE ID = 1")
    # WMStokenResult = cur.fetchone()
    # WMStoken = WMStokenResult[0]
    # conn.commit()
    WMStoken = 'eyJhbGciOiJSUzI1NiJ9.eyJST0xFX1dNU19MRUFERVIiOnRydWUsIlJPTEVfV0hfRVJST1JfQ0hFQ0siOnRydWUsIlJPTEVfV01TX01HVCI6dHJ1ZSwidXNlclV1aWQiOiI5YzNkOTUxYy0zOTRjLTQxNGEtODMxNi00OTZhZDM0ODAyZWEiLCJST0xFX1dNU19BRE1JTiI6dHJ1ZSwiUk9MRV9BRE1JTiI6dHJ1ZSwiUk9MRV9XSF9QQUNLIjp0cnVlLCJST0xFX05PQyI6dHJ1ZSwidXNlcm5hbWUiOiJUWVdNUy5UZXN0QWRtaW4xIiwic3ViIjoiVFlfTVdNU19TU08iLCJpYXQiOjE3MTQwNDMxMjEsImV4cCI6MTcxNDA2MTEyMX0.cAkO4h59WYb1MgzAiEvCE19FVyZ6-6tsUaIOTQhKo-N7qEFYemHQDeOYzFORw1Y4yV_41JCXo6tvlP6683tutQHXWL9zwcVynzcQbkMc1564uwAVyHjlGS5noKpfzWVcQZXs5Di7s1lGQcNy1fY4SbQCqLpS_Iv_l7MFmslbFQ9crT5YB9WfREY0CEw-LKY8pdcn1goEgrZ7Xdg9KCLoLj60IdIalabbEm2EmEeJQcg6s7QoCBDtFzrt73GV_mPy2-dhV9xQVkP09KsxD_9K_-U5cAIaAC5iXoEGRcEZht5mniuknrMo5P1-ADf18QO6M2JJ6ikFDzYx4xf9Gmzq3g'
    WMSheaders = {'Authorization' : f'Bearer {WMStoken}'}
    BookingInfoResponse = requests.get(GetStockOutInfoURL,headers=WMSheaders).json()
    BatchQTY = BookingInfoResponse['data']['pagination']['totalElements']
    print(f"Stock-out {BatchQTY} batch")
    BatchDict = {}
    TaskList = []
    if BatchQTY <= 100 :
        BookingInfoList = BookingInfoResponse['data']['bookingRecords']
        for batch in BookingInfoList :
            BatchDict[batch['batchId']] = batch
    print(BatchDict)
    GetTaskNoURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/task_number/get_task_number?serviceType=STOCK_OUT_CONSOLIDATION&bookingNo={BookingNumber}'
    TaskNoResponse = requests.get(GetTaskNoURL).json()
    print(TaskNoResponse['resultStatus'])
    if TaskNoResponse['resultStatus'] == "SUCCESS" :
        TaskList = TaskNoResponse['responseData']
    for task in TaskList :
        __ConsolidationTaskHandle__(task , BatchDict)
            


def __ConsolidationTaskHandle__(Task , SKUinfo):
    TaskNo = Task['taskNo']
    Compartment = Task['batches'][0]['fromTote']
    if Compartment.startswith("14"):
        CompartmentType = "TY14"
        CompartmentQty = 4
    elif Compartment.startswith("12"):
        CompartmentType = "TY12"
        CompartmentQty = 2
    else :
        print("Please check consolidation task , occrus error")

    TotesQty = math.ceil(len(Task['batches'])/CompartmentQty)
    TotesList = __GetTotes__(CompartmentType,TotesQty)

    M5121Totaldata = []
    j = 0 #計算空箱
    BatchesList = Task['batches']
    for i in range(len(Task['batches'])) : # 迴圈處理任務中的每個箱子
        if TotesList[j][1] == CompartmentQty :
            j += 1
        BatchId = BatchesList[i]['batchId']
        FromTote = BatchesList[i]['fromTote']
        FromCells = BatchesList[i]['fromComp']
        Ean = SKUinfo[BatchId]['ean']
        UUID = SKUinfo[BatchId]['uuid']
        QTY = SKUinfo[BatchId]['qty']
        M5121data = {
                    "taskNo": TaskNo,
                    "isNormalComplete": True,
                    "isLast": i == len(BatchesList) - 1 ,
                    "stationKey": "test_7f036537fed7",
                    "operatorId": "test_776ab1b1b4d2",
                    "detail": [
                        {
                        "uId": UUID,
                        "eanCode": Ean,
                        "actualEanCode": Ean,
                        "isLock": False,
                        "fromCellsCode": FromCells,
                        "toCellsCode": TotesList[j][1],
                        "qty": QTY,
                        "fromErrorCode": "",
                        "fromRemarks": "",
                        "toErrorCode": "",
                        "toRemarks": ""
                        }
                    ],
                    "fromContainerCode": FromTote,
                    "toContainerCode": TotesList[j][0],
                    "errorCode": "",
                    "remarks": ""
                    }
        M5121Totaldata.append(M5121data)
    M5121Body = json.dumps({
        "msgTime": "test_23b549b76fda",
        "msgId": "test_7817ccb87aba",
        "data": M5121Totaldata
        })
    APIheaders = {"Content-Type" : "application/json"}
    M5121URL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/wcs/consolidation_complete_report'
    M5121Response = requests.post(M5121URL,data=M5121Body,headers=APIheaders).json()
    print(M5121Body)
    print(M5121Response)
    
        
def __GetTotes__(CompartmentType,TotesQty):
    # 獲取Tote , 條件(Available for rent , In System , TY3F)
    # conn.execute("SELECT WMStoken FROM `3PL_Var_Table` WHERE ID = 1")
    # WMStokenResult = cur.fetchone()
    # WMStoken = WMStokenResult[0]
    # conn.commit()
    WMStoken = 'eyJhbGciOiJSUzI1NiJ9.eyJST0xFX1dNU19MRUFERVIiOnRydWUsIlJPTEVfV0hfRVJST1JfQ0hFQ0siOnRydWUsIlJPTEVfV01TX01HVCI6dHJ1ZSwidXNlclV1aWQiOiI5YzNkOTUxYy0zOTRjLTQxNGEtODMxNi00OTZhZDM0ODAyZWEiLCJST0xFX1dNU19BRE1JTiI6dHJ1ZSwiUk9MRV9BRE1JTiI6dHJ1ZSwiUk9MRV9XSF9QQUNLIjp0cnVlLCJST0xFX05PQyI6dHJ1ZSwidXNlcm5hbWUiOiJUWVdNUy5UZXN0QWRtaW4xIiwic3ViIjoiVFlfTVdNU19TU08iLCJpYXQiOjE3MTQwNDMxMjEsImV4cCI6MTcxNDA2MTEyMX0.cAkO4h59WYb1MgzAiEvCE19FVyZ6-6tsUaIOTQhKo-N7qEFYemHQDeOYzFORw1Y4yV_41JCXo6tvlP6683tutQHXWL9zwcVynzcQbkMc1564uwAVyHjlGS5noKpfzWVcQZXs5Di7s1lGQcNy1fY4SbQCqLpS_Iv_l7MFmslbFQ9crT5YB9WfREY0CEw-LKY8pdcn1goEgrZ7Xdg9KCLoLj60IdIalabbEm2EmEeJQcg6s7QoCBDtFzrt73GV_mPy2-dhV9xQVkP09KsxD_9K_-U5cAIaAC5iXoEGRcEZht5mniuknrMo5P1-ADf18QO6M2JJ6ikFDzYx4xf9Gmzq3g'
    WMSheaders = {'Authorization' : f'Bearer {WMStoken}'}
    GetTotesURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote?pageNo=5&pageSize=10&sort=toteCode:asc&status=Available+for+rent&warehouseCode=TY3F&toteType={CompartmentType}&locationType=In+System'
    GetToteResponse = requests.get(GetTotesURL,headers=WMSheaders).json()
    TotesRecord = GetToteResponse['data']['totes']
    ToteList = []
    for i in range(TotesQty) :
        ToteList.append((TotesRecord[i]['toteCode'],0))
    print(ToteList)
    return ToteList


__StockOutAPI__("SOTY3F00000651")
