import wx


StationKey = '503'
BookingNumber = 'TCTY3F'


class CollectionAPI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Only tote collection API', size=(300, 300))
        panel = wx.Panel(self)
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
        CreateBookingButton = wx.Button(
            panel, label="自動創建訂單", pos=(10, 165), size=(130, 20))
        CreateBookingButton.SetFont(Buttonfont)
        self.Account_lable = wx.StaticText(
            panel, label="MMS帳號", pos=(15, 108))
        self.Account_text = wx.TextCtrl(
            panel, value=StationKey, pos=(90, 105), size=(150, -1))
        self.Account_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Account_lable = wx.StaticText(
            panel, label="MMS密碼", pos=(15, 135))
        self.Account_text = wx.TextCtrl(
            panel, value=StationKey, pos=(90, 132), size=(150, -1))
        self.Account_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Title_lable = wx.StaticText(
            panel, label="若有訂單可忽略,非必需!", pos=(145, 165))
        # CreateBookingButton.Bind(
        #     wx.EVT_BUTTON, lambda event:  self.create_booking())
        # Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
        #                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

    def OnKeyPressBooking(self, event):
        key_code = event.GetKeyCode()
        BookingNumber = self.BookingNumber_text.GetValue()
        BookingLen = len(BookingNumber)
        print(BookingNumber)
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            event.Skip()
            return
        if chr(key_code).isdigit():
            if BookingNumber.startswith('TCTY3F') and BookingLen < 14:
                event.Skip()
            else:
                wx.Bell()
                self.BookingNumber_text.SetValue("TCTY3F")
        else:
            wx.Bell()

    def Set_Text_Value(self, event):
        global StationKey, BookingNumber
        StationKey = self.Station_text.GetValue()
        if len(StationKey) > 3:
            self.Station_text.SetValue("503")
        if not BookingNumber.startswith('TCTY3F'):
            self.BookingNumber_text.SetValue("TCTY3F")

    def OnKeyPress(self, event):
        key_code = event.GetKeyCode()
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
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
