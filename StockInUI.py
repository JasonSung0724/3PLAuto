import wx
import time
import requests
from ToteCollection import __CreateCollectionBooking__, __MMSlogin__, __CollectionAPI__
from internalToteIn import __WMSLogin__
from Binding import __CreateStockInBooking__, __CheckTote__, __CheckBookingExist__, __SendBindListToMIX__
from ToteBindUI import OneCompartment, FourCompartment, TwoCompartment, RunStockInAPI
from GlobalVar import *


StationKey = '503'
BookingNumber = 'SITY3F'
TY11 = "0"
TY12 = "0"
TY14 = "0"
StorageType = 'AMBIENT'
inUseTY11 = 0
inUseTY12 = 0
inUseTY14 = 0
BindingTote = ''


class StockInUI(wx.Frame):
    def __init__(self):
        global MMSAccount, MMSPassword
        super().__init__(parent=None, title='Stock-in UI', size=(330, 450))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        TestEnv = Result[0]
        cur.execute("SELECT MMSAccount FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        MMSAccount = Result[0]
        cur.execute("SELECT MMSPassword FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        MMSPassword = Result[0]
        conn.commit()
        self.Binding_label = wx.StaticText(
            panel, label="---------------------Binding Tote---------------------", pos=(15, 200))
        self.BookingNumber_lable = wx.StaticText(
            panel, label="訂單號碼 :", pos=(15, 20))
        self.BookingNumber_text = wx.TextCtrl(
            panel, value=BookingNumber, pos=(90, 17), size=(150, -1))
        self.BookingNumber_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.BookingNumber_text.Bind(wx.EVT_CHAR, self.OnKeyPressBooking)
        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.MMSLogin = wx.Button(
            panel, label="MMS登入更新token", pos=(15, 135), size=(290, 30))
        self.MMSLogin.SetFont(Buttonfont)
        self.MMSLogin.Bind(
            wx.EVT_BUTTON, lambda event: self.MMSlogin())
        self.CreateBookingButton = wx.Button(
            panel, label="自動創建訂單", pos=(15, 165), size=(290, 30))
        self.CreateBookingButton.SetFont(Buttonfont)
        self.CreateBookingButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.CreateBooking())
        self.TY11_lable = wx.StaticText(panel, label="TY11", pos=(15, 110))
        self.TY11_text = wx.TextCtrl(panel, value=str(
            TY11), pos=(45, 107), size=(20, -1))
        self.TY11_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY11_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY12_lable = wx.StaticText(panel, label="12", pos=(65, 110))
        self.TY12_text = wx.TextCtrl(panel, value=str(
            TY12), pos=(82, 107), size=(20, -1))
        self.TY12_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY12_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY14_lable = wx.StaticText(panel, label="14", pos=(103, 110))
        self.TY14_text = wx.TextCtrl(panel, value=str(
            TY14), pos=(120, 107), size=(20, -1))
        self.TY14_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY14_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Account_lable = wx.StaticText(
            panel, label="MMS帳號", pos=(15, 48))
        self.Account_text = wx.TextCtrl(
            panel, value=MMSAccount, pos=(90, 45), size=(150, -1))
        self.Account_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.password_lable = wx.StaticText(
            panel, label="MMS密碼", pos=(15, 75))
        self.password_text = wx.TextCtrl(
            panel, value=MMSPassword, pos=(90, 75), size=(150, -1))
        self.password_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.ExcecueButton = wx.Button(
            panel, label="Run Stock-in API flow", pos=(15, 360), size=(290, 30))
        self.ExcecueButton.SetFont(Buttonfont)
        self.ExcecueButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.RunStockIn())
        self.ExcecueButton.SetBackgroundColour(wx.BLUE)

        self.StorageTypeButton = wx.ToggleButton(
            panel, label="Ambient",  pos=(150, 102), size=(155, 30))
        self.StorageTypeButton.Bind(
            wx.EVT_TOGGLEBUTTON, self.StorageTypeSetting)
        self.ENVButton = wx.ToggleButton(
            panel, label=f"{TestEnv}", pos=(250, 15), size=(60, 80))
        self.ENVButton.Bind(wx.EVT_TOGGLEBUTTON, self.ENV_Setting)

        self.GetTY11Btn = wx.Button(
            panel, label="GET TY11", pos=(15, 200), size=(95, 70))
        self.GetTY11Btn.Bind(
            wx.EVT_BUTTON, lambda event:  self.GetTotes("TY11", inUseTY11))
        self.GetTY12Btn = wx.Button(
            panel, label="GET TY12", pos=(112, 200), size=(95, 70))
        self.GetTY12Btn.Bind(
            wx.EVT_BUTTON, lambda event:  self.GetTotes("TY12", inUseTY12))
        self.GetTY14Btn = wx.Button(
            panel, label="GET TY14", pos=(210, 200), size=(95, 70))
        self.GetTY14Btn.Bind(
            wx.EVT_BUTTON, lambda event:  self.GetTotes("TY14", inUseTY14))

        self.BindingTote_label = wx.StaticText(
            panel, label="Binding Tote Check", pos=(20, 290))
        self.BindingTote_Text = wx.TextCtrl(
            panel, value=BindingTote, pos=(15, 310), size=(120, 20))
        self.BindingTote_Text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.CheckToteBtn = wx.Button(
            panel, label="Check Tote", pos=(140, 282), size=(165, 50))
        self.CheckToteBtn.Bind(
            wx.EVT_BUTTON, lambda event:  self.CheckTote(BindingTote))
        self.SendBindListButton = wx.Button(
            panel, label="SITY3F Send bind list", pos=(15, 330), size=(290, 30))
        self.SendBindListButton.SetFont(Buttonfont)
        self.SendBindListButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.SendBindList())

    def SendBindList(self):
        Response = __SendBindListToMIX__(BookingNumber=BookingNumber)
        wx.MessageBox(f'{Response}', 'Send bind list response',
                      wx.OK | wx.ICON_WARNING)

    def MMSlogin(self):
        Response = __MMSlogin__(MMSAccount=MMSAccount, MMSPassword=MMSPassword)
        if type(Response) == str:
            wx.MessageBox(f'帳號：{MMSAccount} \n密碼：{MMSPassword}',
                          '登入成功', wx.OK | wx.ICON_WARNING)
        else:
            wx.MessageBox(f'帳號：{MMSAccount} \n密碼：{MMSPassword}',
                          '登入失敗', wx.OK | wx.ICON_WARNING)

    def CheckTote(self, Tote):
        if Tote == "":
            self.SetStatusText("Please input tote code first.")
            wx.MessageBox(
                '請先自行輸入箱號,或是按Get Tote可自動從WMS抓取符合條件的tote\n(On Rent & Hold by merchant & TY3F & Tote Type)', 'Warning', wx.OK | wx.ICON_WARNING)
            return
        if len(Tote) == 10 or Tote.startswith("11") or Tote.startswith("12") or Tote.startswith("14"):
            pass
        else:
            self.SetStatusText("Tote format wrong")
            wx.MessageBox(
                '請先輸入正確的MS訂單號', 'Warning', wx.OK | wx.ICON_WARNING)
            return
        Response = __CheckTote__(BindingTote)
        if type(Response) == str:
            self.SetStatusText(Response)
            wx.MessageBox(f'{Response}', 'Check Tote', wx.OK | wx.ICON_WARNING)
        elif type(Response) == dict:
            if BookingNumber.startswith("SITY3F") and len(BookingNumber) == 14:
                print("利用gary+admin確認訂單是否存在")
                if __CheckBookingExist__(BookingNumber, status="PENDING"):
                    if Tote.startswith("11"):
                        dialog = OneCompartment(self, Tote, BookingNumber)
                        dialog.ShowModal()
                        dialog.Destroy()
                    elif Tote.startswith("12"):
                        dialog = TwoCompartment(self, Tote, BookingNumber)
                        dialog.ShowModal()
                        dialog.Destroy()
                    else:
                        dialog = FourCompartment(self, Tote, BookingNumber)
                        dialog.ShowModal()
                        dialog.Destroy()
                else:
                    self.SetStatusText(
                        f"Booking number : {BookingNumber} not exist")
                    wx.MessageBox(
                        f"Booking number : {BookingNumber} not exist or Booking status is not pending", 'Booking number check', wx.OK | wx.ICON_WARNING)
            else:
                self.SetStatusText(
                    f"Booking number : {BookingNumber} format wrong")
                wx.MessageBox(f"Booking number : {BookingNumber} format wrong",
                              'Booking number check', wx.OK | wx.ICON_WARNING)

    def GetTotes(self, ToteType, inUse):
        global inUseTY11, inUseTY12, inUseTY14, BindingTote
        cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        TestEnv = Result[0]
        conn.commit()
        cur.execute("SELECT WMStoken FROM `Var_3PL_Table` WHERE ID = 1")
        WMStokenResult = cur.fetchone()
        WMStoken = WMStokenResult[0]
        conn.commit()
        if ToteType == "TY11":
            inUseTY11 += 1
        elif ToteType == "TY12":
            inUseTY12 += 1
        elif ToteType == "TY14":
            inUseTY14 += 1
        WMSheaders = {'Authorization': f'Bearer {WMStoken}'}
        GetTotesURL = f'https://mwms-whtsy-{TestEnv.lower()}.hkmpcl.com.hk/hktv_ty_mwms/cms/inventory_tote?pageNo=1&pageSize=200&sort=toteCode:asc&locationType=Hold+by+Merchant&status=On+rent&warehouseCode=TY3F&toteType={ToteType}'
        GetToteResponse = requests.get(GetTotesURL, headers=WMSheaders).json()
        TotesRecord = GetToteResponse['data']['totes']
        least = len(GetToteResponse) - 1
        BindingTote = TotesRecord[least-inUse]['toteCode']
        self.BindingTote_Text.SetValue(BindingTote)
        return BindingTote

    def ENV_Setting(self, event):
        if self.ENVButton.GetValue():
            env = 'staging'
            self.ENVButton.SetLabel(f"{env}")
            print(env)
            self.SetStatusText(f"ENV set to {env}")
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{env}' WHERE ID = 1")
            conn.commit()
        else:
            env = 'dev'
            self.ENVButton.SetLabel(f"{env}")
            print(env)
            self.SetStatusText(f"ENV set to {env}")
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{env}' WHERE ID = 1")
            conn.commit()

    def StorageTypeSetting(self, event):
        global StorageType
        if self.StorageTypeButton.GetValue():
            self.StorageTypeButton.SetLabel("Air-con")
            StorageType = 'Aircon'
            print(StorageType)
            self.SetStatusText(
                f"Select storage type {StorageType} you wanna booking")
        else:
            self.StorageTypeButton.SetLabel("Ambient")
            StorageType = 'Ambient'
            print(StorageType)
            self.SetStatusText(
                f"Select storage type {StorageType} you wanna booking")

    def RunStockIn(self):
        if len(BookingNumber) == 14:
            if __CheckBookingExist__(BookingNumber=BookingNumber, status="MAPPED"):
                dialog = RunStockInAPI(self, BookingNumber)
                dialog.ShowModal()
                dialog.Destroy()
                return
        wx.MessageBox(
            f'Booking number {BookingNumber} is not exist , or Boooking status is not MAPPED')
        return

    def CreateBooking(self):
        global TY11, TY12, TY14, BookingNumber, StorageType
        if TY11 == "":
            self.TY11_text.SetValue("0")
        if TY12 == "":
            self.TY12_text.SetValue("0")
        if TY14 == "":
            self.TY14_text.SetValue("0")
        self.SetStatusText("")
        token = __MMSlogin__(MMSAccount=MMSAccount, MMSPassword=MMSPassword)
        cur.execute(
            f"UPDATE `Var_3PL_Table` SET `MMSAccount` = '{MMSAccount}' WHERE ID = 1")
        cur.execute(
            f"UPDATE `Var_3PL_Table` SET `MMSPassword` = '{MMSPassword}' WHERE ID = 1")
        conn.commit()
        if token == 401:
            self.SetStatusText("MMS account or password wrong")
            return
        else:
            self.SetStatusText(f"{MMSAccount} / {MMSPassword}")
            time.sleep(3)
            try:
                TY11_int = int(TY11)
                TY12_int = int(TY12)
                TY14_int = int(TY14)
            except ValueError:
                self.SetStatusText(
                    "Invalid input. Please enter integers for TY11, TY12, and TY14.")
            if TY11_int + TY12_int + TY14_int > 0:
                self.SetStatusText(
                    f"TY11 : {TY11} , TY12 : {TY12} , TY14 : {TY14}")
                BookingNumber = __CreateStockInBooking__(
                    TY11, TY12, TY14, StorageType=StorageType)
                if BookingNumber.startswith("SITY3F"):
                    self.SetStatusText(f"Booking Number : {BookingNumber}")
                    self.BookingNumber_text.SetValue(BookingNumber)
                    BookingNumber = BookingNumber
                    self.SendBindListButton.SetLabel(
                        f"{BookingNumber} Send bind list")
                    wx.MessageBox(
                        f'{BookingNumber} 訂單創建成功', 'Create Booking Response', wx.OK | wx.ICON_WARNING)
                else:
                    self.SetStatusText(BookingNumber)
                    wx.MessageBox(f'{BookingNumber}',
                                  'Stock-in 訂單狀態', wx.OK | wx.ICON_WARNING)
            else:
                print(TY11_int + TY12_int + TY14_int)
                self.SetStatusText(f"請輸入箱數")
                wx.MessageBox('請輸入確認MMS帳號 & token 是你要創建訂單的帳號\n並輸入箱子數量',
                              'Warning', wx.OK | wx.ICON_WARNING)

    def OnKeyPressBooking(self, event):
        global BookingNumber
        key_code = event.GetKeyCode()
        BookingNumber = self.BookingNumber_text.GetValue()
        BookingLen = len(BookingNumber)
        print(BookingNumber)
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK or key_code == wx.WXK_LEFT or key_code == wx.WXK_RIGHT:
            event.Skip()
            return
        if chr(key_code).isdigit():
            if BookingNumber.startswith('SITY3F') and BookingLen < 14:
                event.Skip()
            else:
                wx.Bell()
                self.BookingNumber_text.SetValue("SITY3F")
                BookingNumber = "SITY3F"
        else:
            wx.Bell()

    def Set_Text_Value(self, event):
        global BookingNumber, MMSAccount, MMSPassword, TY11, TY12, TY14, BindingTote
        MMSAccount = self.Account_text.GetValue()
        MMSPassword = self.password_text.GetValue()
        TY11 = self.TY11_text.GetValue()
        TY12 = self.TY12_text.GetValue()
        TY14 = self.TY14_text.GetValue()
        BookingNumber = self.BookingNumber_text.GetValue()
        BindingTote = self.BindingTote_Text.GetValue()
        self.SendBindListButton.SetLabel(f"{BookingNumber} Send bind list")
        if not BookingNumber.startswith('SITY3F'):
            self.BookingNumber_text.SetValue("SITY3F")
            BookingNumber = "SITY3F"
        if len(BookingNumber) > 14:
            self.BookingNumber_text.SetValue("SITY3F")
            BookingNumber = "SITY3F"

    def OnKeyPress(self, event):
        key_code = event.GetKeyCode()
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK or key_code == wx.WXK_LEFT or key_code == wx.WXK_RIGHT:
            event.Skip()
            return
        if chr(key_code).isdigit():
            event.Skip()
        else:
            wx.Bell()
            return


if __name__ == "__main__":
    app = wx.App()
    frame = StockInUI()
    frame.Show()
    app.MainLoop()
