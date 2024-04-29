import wx
from StockOut import __StockOutAPI__

BookingNumber = 'SOTY3F'

class StockOutAPI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Internal tote-in + Tote collection', size=(300, 200))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        self.BookingNumber_lable = wx.StaticText(
            panel, label="* Booking Number", pos=(15, 23))
        self.BookingNumber_text = wx.TextCtrl(
            panel, value=BookingNumber, pos=(15, 50), size=(120, -1))
        self.BookingNumber_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.BookingNumber_text.Bind(wx.EVT_CHAR, self.OnKeyPressBooking)
        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        Button = wx.Button(panel, label="RUN", pos=(150, 20), size=(130, 110))
        Button.SetFont(Buttonfont)
        Button.Bind(wx.EVT_BUTTON, lambda event: self.CheckStockOut())

    def CheckStockOut(self):
        if len(BookingNumber) != 14 :
            print("Booking Number Error")
            self.SetStatusText("Booking Number Error")
            return
        __StockOutAPI__(BookingNumber)


    def Set_Text_Value(self, event):
        global  BookingNumber
        BookingNumber = self.BookingNumber_text.GetValue()
        if not BookingNumber.startswith('SOTY3F') or len(BookingNumber) > 14:
            self.BookingNumber_text.SetValue('SOTY3F')

    def OnKeyPressBooking(self, event):
        key_code = event.GetKeyCode()
        BookingNumber = self.BookingNumber_text.GetValue()
        BookingLen = len(BookingNumber)
        print(BookingNumber)
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            event.Skip()
            return
        if chr(key_code).isdigit():
            if BookingNumber.startswith('SOTY3F') and BookingLen < 15:
                event.Skip()
            else:
                wx.Bell()
                self.BookingNumber_text.SetValue("SOTY3F")
        else:
            wx.Bell()

    def OnPaste(self, event):
        print("Paste")
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
            if success:
                pasted_text = text_data.GetText().strip()
                if pasted_text.isdigit():
                    self.GetTotes_text.AppendText(pasted_text)
                    return
                else:
                    wx.Bell()
                    print("Invalid paste")
                    self.SetStatusText(f"Invalid paste ( {pasted_text} )")
                    return
        wx.Bell()



if __name__ == "__main__":
    app = wx.App()
    frame = StockOutAPI()
    frame.Show()
    # __TPLCMSlogin__()
    # __WMSLogin__()
    app.MainLoop()