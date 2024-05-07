import requests , mimetypes 
import pandas as pd
import time
import json
from GlobalVar import *

'''Tote Registration in TPL system'''


def __TPLCMSlogin__():
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    LoginAPI = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/sso/login'
    Account = {
        "username": "MIX.TestAdmin1",
        "password": "1qaz@WSX"
    }
    LoginResponse = requests.post(LoginAPI, json=Account).json()
    token = LoginResponse['data']['roles']
    for system in token:
        if system['system'] == 'MOX':
            MOXtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `MOXtoken` = '{MOXtoken}' WHERE ID = 1")
        elif system['system'] == "MIX":
            MIXtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `MIXtoken` = '{MIXtoken}' WHERE ID = 1")
        elif system['system'] == "TPLRS":
            TPLtoken = system['token']
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TPLtoken` = '{TPLtoken}' WHERE ID = 1")
    conn.commit()
    print("TPLCMS login success")


'''Please input how much tote you want to generate'''


def __NewToteRegistration__(TY11=0, TY12=0, TY14=0):
    cur.execute("SELECT MIXtoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MIXtoken = Result[0]
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    TotalTotes = TY11 + TY12 + TY14
    RegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes'
    headers = {'Authorization': f'Bearer {MIXtoken}'}
    GenerateTote = {
        "ty11": TY11,
        "ty12": TY12,
        "ty14": TY14
    }
    RegistrationResponse = requests.post(
        RegistrationURL, json=GenerateTote, headers=headers)
    if RegistrationResponse.status_code == 200:
        print("Generate tote : " + RegistrationResponse.json()['message'])
        retry = 0
        while True:
            ToteRecordURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/history?pageNo=1&pageSize=10&'
            ToteRecordResponse = requests.get(
                ToteRecordURL, headers=headers).json()
            registerTote = ToteRecordResponse['data']['list'][0]['toteCode']
            if len(registerTote) == TotalTotes or retry > 3:
                break
            else:
                retry += 1
                print("Get wrong generate tote record , retry...")
        ToteList_str = json.dumps(
            __BatchUploadTotes__(registerTote))
        cur.execute(
            f"UPDATE `Var_3PL_Table` SET `NewRegisterToteList` = ? WHERE ID = 1", (ToteList_str,))
        conn.commit()
    else:
        print(RegistrationResponse.json()['message'])
    time.sleep(2)
    return registerTote


# def __SingleRegisterTote__(ToteList, headers):
#     print("Single tote registration...")
#     cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
#     Result = cur.fetchone()
#     TestEnv = Result[0]
#     conn.commit()
#     for tote in ToteList:
#         SingleRegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/{tote}'
#         requests.put(SingleRegistrationURL, headers=headers)
#     print(ToteList)
#     return ToteList

def __BatchUploadTotes__(totecode):
    print(totecode)
    cur.execute("SELECT MIXtoken FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    MIXtoken = Result[0]
    cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
    Result = cur.fetchone()
    TestEnv = Result[0]
    conn.commit()
    data = {'Tote Code': totecode}
    df = pd.DataFrame(data)
    excel_file = 'ToteCodeList.xlsx' 
    df.to_excel(excel_file, index=False)
    upload_url = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/upload'
    headers = {
        "Authorization": f"Bearer {MIXtoken}",
    }
    mime_type, _ = mimetypes.guess_type('ToteCodeList.xlsx')
    files = {
        'file': ('ToteCodeList.xlsx',open('ToteCodeList.xlsx', 'rb'),mime_type)
    }
    response = requests.post(upload_url, headers=headers, files=files)
    if response.status_code == 200 :
        print("Batch upload totes to MIX successfully")
        print(response.json())
    return totecode

# __NewToteRegistration__(5,5,5)