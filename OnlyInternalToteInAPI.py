import wx
from ToteRegistration import __TPLCMSlogin__, __NewToteRegistration__
from GlobalVar import *
from StationFlow import __KIOSKFlow__
from ToteCollection import __MMSlogin__, __CollectionAPI__, __CreateCollectionBooking__
from internalToteIn import __WMSLogin__, __InternalToteInAPI__, __CreateInternalToteInBooking__
import time
import openpyxl

InternalStation = '101'
BookingNumber = 'ITRTY3F'
GetTotes = ''


class OnlyInternalAPI(wx.Frame):

    def __init__(self):
        super().__init__(parent=None, title='Only internal Tote-in API', size=(400, 220))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        self.BookingNumber_lable = wx.StaticText(
            panel, label="* Booking Number", pos=(15, 23))
        self.BookingNumber_text = wx.TextCtrl(
            panel, value=BookingNumber, pos=(170, 20), size=(150, -1))
        self.BookingNumber_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.BookingNumber_text.Bind(wx.EVT_CHAR, self.OnKeyPressBooking)

        self.InternalStation_label = wx.StaticText(
            panel, label="Internal Tote-in Station", pos=(15, 48))
        self.InternalStation_text = wx.TextCtrl(
            panel, value=InternalStation, pos=(170, 45), size=(50, -1))
        self.InternalStation_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.InternalStation_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.GetTotes_label = wx.StaticText(
            panel, label="* Tote code : ", pos=(15, 73))
        self.GetTotes_text = wx.TextCtrl(panel, value=str(GetTotes),pos=(90,75) , size=(250, -1))
        self.GetTotes_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.GetTotes_text.Bind(wx.EVT_CHAR, self.OnKeyPressToteCode)
        # self.GetTotes_text.Bind(wx.EVT_TEXT_PASTE, self.OnPaste)

        Buttonfont = wx.Font(13, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        Button = wx.Button(panel, label="RUN", pos=(300, 120), size=(80, 30))
        Button.SetFont(Buttonfont)
        Button.Bind(wx.EVT_BUTTON, lambda event: __InternalToteInAPI__(
            BookingNumber=BookingNumber, StationKey=InternalStation, ToteList=GetTotes))
        CreateBookingButton = wx.Button(
            panel, label="Create Booking", pos=(170, 120), size=(130, 30))
        CreateBookingButton.SetFont(Buttonfont)
        CreateBookingButton.Bind(
            wx.EVT_BUTTON, lambda event:  self.create_booking())
        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        Button = wx.Button(panel, label="Upload excel",
                           pos=(10, 120), size=(160, 30))
        Button.SetFont(Buttonfont)
        Button.Bind(wx.EVT_BUTTON, lambda event: self.__UploadExcel__())

    def create_booking(self):
        global BookingNumber
        self.SetStatusText("")
        if GetTotes != "":
            BookingNumber = __CreateInternalToteInBooking__(ToteList=GetTotes)
            if BookingNumber.startswith("ITRTY3F"):
                self.BookingNumber_text.SetValue(BookingNumber)
            else:
                self.SetStatusText(BookingNumber)
        else:
            self.SetStatusText("Please input tote code")
            return

    def Set_Text_Value(self, event):
        global InternalStation, GetTotes, BookingNumber
        InternalStation = self.InternalStation_text.GetValue()
        BookingNumber = self.BookingNumber_text.GetValue()
        TotesText = self.GetTotes_text.GetValue()
        GetTotes = TotesText.split(",")
        if InternalStation == "":
            self.SetStatusText("StationKey is mandatory field")
            self.InternalStation_text.SetValue("101")
        if not InternalStation.startswith("1"):
            self.SetStatusText("Wrong station key")
            self.InternalStation_text.SetValue("101")
        if int(InternalStation) > 150:
            self.InternalStation_text.SetValue("101")
        if not BookingNumber.startswith('ITRTY3F') or len(BookingNumber) > 15:
            self.BookingNumber_text.SetValue('ITRTY3F')

    def OnPaste(self, event):
        print("Paste")
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
            if success:
                pasted_text = text_data.GetText().strip()
                if pasted_text.isdigit() or pasted_text == ",":
                    self.GetTotes_text.AppendText(pasted_text)
                    return
                else:
                    wx.Bell()
                    print("Invalid paste")
                    self.SetStatusText(f"Invalid paste ( {pasted_text} )")
                    return
        wx.Bell()

    def OnKeyPressToteCode(self, event):
        key_code = event.GetKeyCode()
        if key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            event.Skip()
            return
        if event.ControlDown() and key_code == 22:
            self.OnPaste(event)
        if key_code == wx.WXK_SPACE:
            wx.Bell()
            return
        if chr(key_code).isdigit() or chr(key_code) == ",":
            event.Skip()
            return
        if event.ControlDown() and key_code == 3 : 
            event.Skip()
            return
        else:
            wx.Bell()
            return

    def OnKeyPress(self, event):
        key_code = event.GetKeyCode()
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            event.Skip()
            return
        elif chr(key_code).isdigit():
            event.Skip()
        else:
            wx.Bell()
            return


    def OnKeyPressBooking(self, event):
        key_code = event.GetKeyCode()
        BookingNumber = self.BookingNumber_text.GetValue()
        BookingLen = len(BookingNumber)
        print(BookingNumber)
        if key_code < wx.WXK_SPACE or key_code == wx.WXK_DELETE or key_code == wx.WXK_BACK:
            event.Skip()
            return
        if chr(key_code).isdigit():
            if BookingNumber.startswith('ITRTY3F') and BookingLen < 15:
                event.Skip()
            else:
                wx.Bell()
                self.BookingNumber_text.SetValue("ITRTY3F")
        else:
            wx.Bell()

    def __UploadExcel__(self):
        wildcard = "Excel files (*.xls;*.xlsx)|*.xls;*.xlsx"
        dialog = wx.FileDialog(self, message="Choose a file",
                               defaultDir="",
                               defaultFile="",
                               wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        path = dialog.GetPath()
        dialog.Destroy()
        self.UploadFile(path)

    def UploadFile(self, path):
        global GetTotes
        data = ''
        workbook = openpyxl.load_workbook(path)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            for cell in row:
                if cell is not None:
                    data += str(cell) + ','
        if data:
            data = data[:-1]
        print(data)
        self.GetTotes_text.SetValue(data)


if __name__ == "__main__":
    app = wx.App()
    frame = OnlyInternalAPI()
    frame.Show()
    app.MainLoop()
