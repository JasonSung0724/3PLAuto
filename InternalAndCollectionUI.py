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
        super().__init__(parent=None, title='Internal tote-in + Station', size=(400, 200))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
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

        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT,
                             wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        Button = wx.Button(panel, label="RUN", pos=(300, 120), size=(100, 20))
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
            event.Skip()
            return
        if chr(key_code).isdigit():
            event.Skip()
        else:
            wx.Bell()
            return

    def __InternalToteInAndToteCollection__(self, TY11=0, TY12=0, TY14=0):
        try:
            TY11 = int(TY11)
            TY12 = int(TY12)
            TY14 = int(TY14)
        except ValueError:
            self.SetStatusText(
                "Invalid input. Please enter integers for TY11, TY12, and TY14.")
            return
        print(f"TY11 : {TY11}, TY12 : {TY12}, TY14 : {TY14}")
        self.SetStatusText(f"TY11 : {TY11}, TY12 : {TY12}, TY14 : {TY14}")
        if TY11 < 0 or TY12 < 0 or TY14 < 0:
            self.SetStatusText(
                "Invalid input. Please enter integers for TY11, TY12, and TY14.")
            return
        if TY11 + TY12 + TY14 == 0:
            self.SetStatusText("Select at least one tote")
            return
        __TPLCMSlogin__()
        __WMSLogin__()
        totelist = __NewToteRegistration__(TY11, TY12, TY14)
        bookingNumber = __CreateInternalToteInBooking__(totelist)
        __KIOSKFlow__(bookingNumber, InternalStation, totelist)
        __MMSlogin__(MMSAccount, MMSPasword)
        BookingNumber = __CreateCollectionBooking__(
            TY11, TY12, TY14)
        __KIOSKFlow__(BookingNumber, CollectionStation, totelist)
        time.sleep(3)


if __name__ == "__main__":
    app = wx.App()
    frame = InternalAndCollection()
    frame.Show()
    app.MainLoop()
