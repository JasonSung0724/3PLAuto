import wx , time
from ToteCollection import __CreateCollectionBooking__ , __MMSlogin__ , __CollectionAPI__
from internalToteIn import __WMSLogin__



StationKey = '503'
BookingNumber = 'TCTY3F'
MMSAccount = ''
MMSPassword = ''
TY11 = "0"
TY12 = "0"
TY14 = "0"


class CollectionAPI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Only tote collection API', size=(330, 360))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        self.Title_lable = wx.StaticText(
            panel, label="請先進入工作站", pos=(15, 23))
        self.Station_lable = wx.StaticText(
            panel, label="你進入的工作站台是？", pos=(15, 50))
        self.Station_text = wx.TextCtrl(
            panel, value=StationKey, pos=(150, 47), size=(50, -1))
        self.Station_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Station_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.BookingNumber_lable = wx.StaticText(
            panel, label="訂單號碼 :", pos=(15, 80))
        self.BookingNumber_text = wx.TextCtrl(
            panel, value=BookingNumber, pos=(90, 77), size=(150, -1))
        self.BookingNumber_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.BookingNumber_text.Bind(wx.EVT_CHAR, self.OnKeyPressBooking)
        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.CreateBookingButton = wx.Button(
            panel, label="自動創建訂單", pos=(10, 195), size=(130, 30))
        self.CreateBookingButton.SetFont(Buttonfont)
        self.CreateBookingButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.CreateBooking())
        self.TY11_lable = wx.StaticText(panel, label="TY11", pos=(15, 165))
        self.TY11_text = wx.TextCtrl(panel, value=str(
            TY11), pos=(45, 162), size=(20, -1))
        self.TY11_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY11_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY12_lable = wx.StaticText(panel, label="12", pos=(65, 165))
        self.TY12_text = wx.TextCtrl(panel, value=str(
            TY12), pos=(82, 162), size=(20, -1))
        self.TY12_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY12_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY14_lable = wx.StaticText(panel, label="14", pos=(103, 165))
        self.TY14_text = wx.TextCtrl(panel, value=str(
            TY14), pos=(120, 162), size=(20, -1))
        self.TY14_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY14_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Account_lable = wx.StaticText(
            panel, label="MMS帳號", pos=(15, 108))
        self.Account_text = wx.TextCtrl(
            panel, value=MMSAccount, pos=(90, 105), size=(150, -1))
        self.Account_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.password_lable = wx.StaticText(
            panel, label="MMS密碼", pos=(15, 135))
        self.password_text = wx.TextCtrl(
            panel, value=MMSPassword, pos=(90, 132), size=(150, -1))
        self.password_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Title_lable = wx.StaticText(
            panel, label=f"若有訂單可忽略,非必需! \n創建訂單後\n請自行進入站台再按執行", pos=(165, 170))
        self.ExcecueButton = wx.Button(
            panel, label="執行", pos=(170, 230), size=(130, 50))
        self.ExcecueButton.SetFont(Buttonfont)
        self.ExcecueButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.Excecute())
        

    def Excecute(self):
        if len(BookingNumber) != 13 :
            self.SetStatusText("invalid booking number")
            return 
        if StationKey != "503" and StationKey != "751" :
            self.SetStatusText("Station should input 503 or 751")
            return
        else :
            Status = __CollectionAPI__(BookingNumber=BookingNumber,stationKey=StationKey)
            self.SetStatusText(Status)
    
    def CreateBooking(self):
        global TY11,TY12,TY14 , BookingNumber
        if TY11 == "" : self.TY11_text.SetValue("0")
        if TY12 == "" : self.TY12_text.SetValue("0")
        if TY14 == "" : self.TY14_text.SetValue("0")
        self.SetStatusText("")
        token = __MMSlogin__(MMSAccount=MMSAccount,MMSPassword=MMSPassword)
        if token == 401 :
            self.SetStatusText("MMS account or password wrong")
            return
        else :
            self.SetStatusText(f"{MMSAccount} / {MMSPassword}")
            time.sleep(3)
            try:
                TY11_int = int(TY11)
                TY12_int = int(TY12)
                TY14_int = int(TY14)
            except ValueError:
                self.SetStatusText("Invalid input. Please enter integers for TY11, TY12, and TY14.")
            if TY11_int + TY12_int + TY14_int > 0 :
                self.SetStatusText(f"TY11 : {TY11} , TY12 : {TY12} , TY14 : {TY14}")
                BookingNumber = __CreateCollectionBooking__(TY11,TY12,TY14)
                if BookingNumber.startswith("TCTY3F") :
                    self.SetStatusText(f"Booking Number : {BookingNumber}")
                    self.BookingNumber_text.SetValue(BookingNumber)
                    BookingNumber = BookingNumber
                else:
                    self.SetStatusText(BookingNumber)
            else:
                print(TY11_int + TY12_int + TY14_int)
                self.SetStatusText(f"請輸入箱數")


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
            if BookingNumber.startswith('TCTY3F') and BookingLen < 14:
                event.Skip()
            else:
                wx.Bell()
                self.BookingNumber_text.SetValue("TCTY3F")
                BookingNumber = "TCTY3F"
        else:
            wx.Bell()

    def Set_Text_Value(self, event):
        global StationKey, BookingNumber , MMSAccount , MMSPassword , TY11 , TY12 , TY14
        StationKey = self.Station_text.GetValue()
        MMSAccount = self.Account_text.GetValue()
        MMSPassword = self.password_text.GetValue()
        TY11 = self.TY11_text.GetValue()
        TY12 = self.TY12_text.GetValue()
        TY14 = self.TY14_text.GetValue()
        BookingNumber = self.BookingNumber_text.GetValue()
        
        if len(StationKey) > 3:
            self.Station_text.SetValue("503")
            StationKey = "503"
        if not BookingNumber.startswith('TCTY3F'):
            self.BookingNumber_text.SetValue("TCTY3F")
            BookingNumber = "TCTY3F"

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
    frame = CollectionAPI()
    frame.Show()
    app.MainLoop()