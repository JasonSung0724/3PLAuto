import requests
import asyncio
from GlobalVar import *

'''Tote Registration in TPL system'''

def __TPLCMSlogin__():
    global MOXtoken , MIXtoken , TPLtoken
    LoginAPI = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/sso/login'
    Account = {
    "username": "MIX.TestAdmin1",
    "password": "1qaz@WSX"
    }
    LoginResponse = requests.post(LoginAPI,json=Account).json()
    token = LoginResponse['data']['roles']
    for system in token :
        if system['system'] == 'MOX':
            MOXtoken == system['token']
        elif system['system'] == "MIX":
            MIXtoken = system['token']
        elif system['system'] == "TPLRS":
            TPLtoken = system['token']

'''Please input how much tote you want to generate'''

def __NewToteRegistration__(TY11 = 0,TY12 = 0,TY14 = 0):
    RegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes'
    headers = {'Authorization' : f'Bearer {MIXtoken}'}
    GenerateTote = {
    "ty11": TY11,
    "ty12": TY12,
    "ty14": TY14
    }
    RegistrationResponse = requests.post(RegistrationURL,json=GenerateTote,headers=headers)
    if RegistrationResponse.status_code == 200 :
        print(RegistrationResponse.json()['message'])
        ToteRecordURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/history?pageNo=1&pageSize=10&'
        ToteRecordResponse = requests.get(ToteRecordURL,headers=headers).json()
        # BatchUploadURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/upload'
        registerTote = ToteRecordResponse['data']['list'][0]['toteCode']
        toteList = __SingleRegisterTote__(registerTote, headers)
    else :
        print(RegistrationResponse.json()['message'])
    return toteList


def __SingleRegisterTote__(ToteList,headers):
    for tote in ToteList :
        SingleRegistrationURL = f'https://mix-{TestEnv.lower()}.hkmpcl.com.hk/hktv_mix/cms/inventory_tote/totes/{tote}'
        requests.put(SingleRegistrationURL,headers=headers)
    print(ToteList)
    return(ToteList)

