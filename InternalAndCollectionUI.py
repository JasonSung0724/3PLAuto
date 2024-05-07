import wx
from ToteRegistration import __TPLCMSlogin__, __NewToteRegistration__
from GlobalVar import *
from StationFlow import __KIOSKFlow__
from ToteCollection import __MMSlogin__, __CollectionAPI__, __CreateCollectionBooking__
from internalToteIn import __WMSLogin__, __InternalToteInAPI__, __CreateInternalToteInBooking__
import time

InternalStation = '101'
CollectionStation = '503'
TY11 = 0
TY12 = 0
TY14 = 0


class InternalAndCollection(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Internal tote-in + Tote collection', size=(500, 220))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        cur.execute("SELECT MMSAccount FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        MMSAccount = Result[0]
        cur.execute("SELECT MMSPassword FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        MMSPassword = Result[0]
        conn.commit()
        wx.MessageBox('此介面比較不穩定，他會自己打開Staion站台\n當Station開太慢時會導致出錯\n若要使用該功能請填好介面上所有欄位\n然後耐心等待...\n他會去MIX註冊新Tote > WMS創建Internal Tote-in訂單\n自己打開Station介面Call internal tote-in訂單\n並在你輸入的MMS帳號創一張Collection訂單 > 自動打開Station介面\nCall collection API完成所有操作','說明',wx.OK|wx.ICON_WARNING)
        self.InternalStation_label = wx.StaticText(
            panel, label="Internal Tote-in Station", pos=(15, 23))
        self.InternalStation_text = wx.TextCtrl(
            panel, value=InternalStation, pos=(170, 20), size=(50, -1))
        self.InternalStation_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.InternalStation_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.CollectionStation_lable = wx.StaticText(
            panel, label="Tote collection Station", pos=(15, 48))
        self.CollectionStation_text = wx.TextCtrl(
            panel, value=CollectionStation, pos=(170, 45), size=(50, -1))
        self.CollectionStation_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.CollectionStation_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY11_lable = wx.StaticText(panel, label="TY11", pos=(120, 73))
        self.TY11_text = wx.TextCtrl(panel, value=str(
            TY11), pos=(170, 70), size=(50, -1))
        self.TY11_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY11_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY12_lable = wx.StaticText(panel, label="TY12", pos=(120, 98))
        self.TY12_text = wx.TextCtrl(panel, value=str(
            TY12), pos=(170, 95), size=(50, -1))
        self.TY12_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY12_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY14_lable = wx.StaticText(panel, label="TY14", pos=(120, 123))
        self.TY14_text = wx.TextCtrl(panel, value=str(
            TY14), pos=(170, 120), size=(50, -1))
        self.TY14_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY14_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Account_lable = wx.StaticText(
            panel, label="MMS帳號", pos=(240, 23))
        self.Account_text = wx.TextCtrl(
            panel, value=MMSAccount, pos=(300, 20), size=(150, -1))
        self.password_lable = wx.StaticText(
            panel, label="MMS密碼", pos=(240, 48))
        self.password_text = wx.TextCtrl(
            panel, value=MMSPassword, pos=(300, 45), size=(150, -1))


        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        Button = wx.Button(panel, label="RUN", pos=(320, 80), size=(130, 70))
        Button.SetFont(Buttonfont)
        Button.Bind(wx.EVT_BUTTON, lambda event: self.__InternalToteInAndToteCollection__(
            TY11, TY12, TY14))

    def Set_Text_Value(self, event):
        global InternalStation, CollectionStation, TY11, TY12, TY14
        InternalStation = self.InternalStation_text.GetValue()
        CollectionStation = self.CollectionStation_text.GetValue()
        TY11 = self.TY11_text.GetValue()
        TY12 = self.TY12_text.GetValue()
        TY14 = self.TY14_text.GetValue()
        if InternalStation == "":
            self.SetStatusText("StationKey is mandatory field")
            self.InternalStation_text.SetValue("101")
        if not InternalStation.startswith("1"):
            self.SetStatusText("Wrong station key")
            self.InternalStation_text.SetValue("101")
        if int(InternalStation) > 150:
            self.InternalStation_text.SetValue("101")
        if CollectionStation == "":
            self.SetStatusText("StationKey is mandatory field")
            self.CollectionStation_text.SetValue("503")
        if CollectionStation != "503" and CollectionStation != "751":
            self.SetStatusText("Wrong station key")
        if int(InternalStation) > 751:
            self.CollectionStation_text.SetValue("503")

    def OnKeyPress(self, event):
        key_code = event.GetKeyCode()
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            if event.ControlDown() and key_code == 22:
                if self.OnPaste(event) == False:
                    return
            event.Skip()
            return
        if chr(key_code).isdigit():
            event.Skip()
        else:
            wx.Bell()
            return

    def OnPaste(self, event):
        print("Paste")
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
            if success:
                pasted_text = text_data.GetText().strip()
                if pasted_text.isdigit():
                    return
                else:
                    wx.Bell()
                    self.SetStatusText(f"Invalid paste ( {pasted_text} )")
                    return False
        wx.Bell()

    def __InternalToteInAndToteCollection__(self, TY11=0, TY12=0, TY14=0):
        MMSAccount = self.Account_text.GetValue()
        MMSPassword = self.password_text.GetValue()
        cur.execute(f"UPDATE `Var_3PL_Table` SET `MMSAccount` = '{MMSAccount}' WHERE ID = 1")
        cur.execute(f"UPDATE `Var_3PL_Table` SET `MMSPassword` = '{MMSPassword}' WHERE ID = 1")
        conn.commit()
        if InternalStation.startswith("1"):
            self.InternalStation_text.SetValue("101")
        if CollectionStation != "503" and CollectionStation != "751":
            self.CollectionStation_text.SetValue("503")
        try:
            TY11 = int(TY11)
            TY12 = int(TY12)
            TY14 = int(TY14)
        except ValueError:
            self.SetStatusText(
                "Invalid input. Please enter integers for TY11, TY12, and TY14.")
            self.TY11_text.SetValue("0")
            self.TY12_text.SetValue("0")
            self.TY14_text.SetValue("0")
            return
        print(f"TY11 : {TY11}, TY12 : {TY12}, TY14 : {TY14}")
        self.SetStatusText(f"TY11 : {TY11}, TY12 : {TY12}, TY14 : {TY14}")
        if TY11 < 0 or TY12 < 0 or TY14 < 0:
            self.SetStatusText(
                "Invalid input. Please enter integers for TY11, TY12, and TY14.")
            return
        if TY11 + TY12 + TY14 == 0:
            self.SetStatusText("Select at least one tote")
            wx.MessageBox('箱子數量未輸入','Warning',wx.OK|wx.ICON_ERROR)
            return
        if type(__MMSlogin__(MMSAccount, MMSPassword)) == int:
            wx.MessageBox("MMS登入失敗，請檢查帳號密碼是否正確","Warning",wx.OK|wx.ICON_ERROR)
        totelist = __NewToteRegistration__(TY11, TY12, TY14)
        bookingNumber = __CreateInternalToteInBooking__(totelist)
        __KIOSKFlow__(bookingNumber, InternalStation, totelist)
        BookingNumber = __CreateCollectionBooking__(
            TY11, TY12, TY14)
        __KIOSKFlow__(BookingNumber, CollectionStation, totelist)
        time.sleep(3)


if __name__ == "__main__":
    app = wx.App()
    frame = InternalAndCollection()
    frame.Show()
    app.MainLoop()
