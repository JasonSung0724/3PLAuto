import requests
import json
from GlobalVar import *
from ToteCollection import __MMSlogin__


def __CheckTote__(Tote):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    cur.execute("SELECT MMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMStoken = Result[0]
    conn.commit()
    CheckToteURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/appscan/tote/{Tote}'
    APIheaders = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {MMStoken}"
    }
    ToteResponse = requests.get(CheckToteURL, headers=APIheaders)
    print(ToteResponse.json())
    if ToteResponse.status_code == 200:
        return ToteResponse.json()
    else:
        return ToteResponse.json()['errorMessage']

#     CheckEanURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/appscan/sku?barcode={Ean}&orderId={BookingNumber}'


def __CheckEan__(Ean):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    cur.execute("SELECT MMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMStoken = Result[0]
    conn.commit()
    CheckEanURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/appscan/sku?barcode={Ean}'
    APIheaders = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {MMStoken}"
    }
    EanResponse = requests.get(CheckEanURL, headers=APIheaders)
    if EanResponse.status_code == 200:
        return EanResponse.json()
    else:
        return EanResponse.json()['errorMessage']


def __Binding__():
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    cur.execute("SELECT MMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMStoken = Result[0]
    conn.commit()
    BindingURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/appscan/order'
    APIheaders = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {MMStoken}"
    }
    BindingBody = {
        "orderId": "SITY3F00004188",
        "tote": {
            "toteId": "1100011880",
            "partitions": [{
                "expiration": 43043587200000,
                "partitionName": "a",
                "skuUuid": "7443ef04-062e-4fb6-919b-4464c487e859",
                "inCompartmentQty": 1,
                "barcode": "02059901"
            }]
        }
    }
    return


def __CreateStockInBooking__(TY11=0, TY12=0, TY14=0, StorageType="AMBIENT"):
    cur.execute("SELECT MMSAccount FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMSAccount = Result[0]
    cur.execute("SELECT MMSPassword FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMSPassword = Result[0]
    __MMSlogin__(MMSAccount, MMSPassword)
    cur.execute("SELECT MMStoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MMStoken = Result[0]
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    headers = {
        'Authorization': f'Bearer {MMStoken}'
    }
    GetStockInQuotqaPayload = {
        "fullCompTote": TY11,
        "twoCompTote": TY12,
        "fourCompTote": TY14,
        "quotaType": "STOCK_IN",
        "warehouse": "TY3F",
        "isSpecial": False,
        "isOverSell": False
    }
    GetQuotaURL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/wms/quota'
    QuotaResponse = requests.post(
        GetQuotaURL, json=GetStockInQuotqaPayload, headers=headers).json()
    print(QuotaResponse)
    try:
        Quota = QuotaResponse['quotaTimeslotResponseDataList'][0]
    except:
        try:
            return QuotaResponse['errorMessage']
        except:
            return "Quota not match , Quota error"

    CreateStockInBody = {
        "warehouseCode": "TY3F",
        "storageType": StorageType.upper(),
        "oneCompQty": TY11,
        "twoCompQty": TY12,
        "fourCompQty": TY14,
        "stockInExceptDate": Quota['startTimestamp'],
        "stockInEndDate": Quota['endTimestamp'],
        "timeSlotData": {
            "special": False,
            "timeslot": Quota['timeslot'],
            "timeslotDate": Quota['timeslotDate'],
            "timeslotType": Quota['timeslotType']
        }
    }
    CreateStockInAPI = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/stockin'
    StockInBooking = requests.post(
        CreateStockInAPI, json=CreateStockInBody, headers=headers)
    print(StockInBooking.status_code)
    if StockInBooking.status_code == 201:
        BookingNumber = StockInBooking.text
        print(BookingNumber)
        return BookingNumber
    else:
        print('Create StockIn booking fail')
        print(StockInBooking)


def __SendBindListMerchantAPP__(BookingNumber, ToteCode, Detail):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    URL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/appscan/order'
    payload = json.dump({
        "orderId": BookingNumber,
        "tote": {
            "toteId": ToteCode,
            "partitions": Detail
        }
    })
    Response = requests.put(URL, data=payload).json()
    return Response


def __CheckBookingExist__(BookingNumber):
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    # 利用admin帳號,確認訂單是否存在
    Login_url = f'https://mms-user-{TestEnv.lower()}.hkmpcl.com.hk/user/login/webLogin'
    login_request_body = {
        "userCode": "gary+admin",
        "userPwd": "15SYQTtoHKO4EPSYNnBLnA=="
    }
    MMSTokenresponse = requests.post(Login_url, json=login_request_body)
    if MMSTokenresponse.status_code == 200:
        print(MMSTokenresponse.json())
        AccessToken = MMSTokenresponse.json()['accessToken']
    URL = f'https://tpl-mms-{TestEnv.lower()}.hkmpcl.com.hk/hktv3plmms/admin/stockin?page=1&pageSize=10&stockInOrderId={BookingNumber}&sort=stockInId&sortType=DESC'
    headers = {
        'Authorization': f'Bearer {AccessToken}'
    }
    Response = requests.get(URL, headers=headers).json()
    if Response['content'] == []:
        return False
    else:
        return True
