import wx
from InternalToteInFunction import *

class InternalAndCollection(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Internal tote-in + Station', size=(400, 200))
        panel = wx.Panel(self)
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        self.InternalStation_label = wx.StaticText(panel, label="Internal Tote-in Station", pos=(15, 23))
        self.InternalStation_text = wx.TextCtrl(panel, value = InternalStation , pos=(170, 20), size=(50, -1))
        self.InternalStation_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.InternalStation_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.CollectionStation_lable = wx.StaticText(panel, label="Tote collection Station", pos=(15, 48))
        self.CollectionStation_text = wx.TextCtrl(panel, value = CollectionStation ,pos=(170, 45), size=(50, -1))
        self.CollectionStation_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.CollectionStation_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY11_lable = wx.StaticText(panel, label="TY11", pos=(120, 73))
        self.TY11_text = wx.TextCtrl(panel, value = str(TY11) ,pos=(170, 70), size=(50, -1))
        self.TY11_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY11_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY12_lable = wx.StaticText(panel, label="TY12", pos=(120, 98))
        self.TY12_text = wx.TextCtrl(panel, value = str(TY12) ,pos=(170, 95), size=(50, -1))
        self.TY12_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY12_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.TY14_lable = wx.StaticText(panel, label="TY14", pos=(120, 123))
        self.TY14_text = wx.TextCtrl(panel, value = str(TY14) ,pos=(170, 120), size=(50, -1))
        self.TY14_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.TY14_text.Bind(wx.EVT_CHAR, self.OnKeyPress)

        Buttonfont = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        button = wx.Button(panel, label="RUN", pos = (300,58), size=(100, 150))  # 增加按钮的宽度和高度
        button.SetFont(Buttonfont)

     
    def Set_Text_Value(self, event):
        global InternalStation , CollectionStation
        InternalStation = self.InternalStation_text.GetValue()
        CollectionStation = self.CollectionStation_text.GetValue()
        TY11 = self.TY11_text.GetValue()
        if InternalStation == "":
            self.SetStatusText("StationKey is mandatory field")
            self.InternalStation_text.SetValue("101")
        if not InternalStation.startswith("1"):
            self.SetStatusText("Wrong station key")
            self.InternalStation_text.SetValue("101")
        if int(InternalStation) > 150 :
            self.InternalStation_text.SetValue("101")
        if CollectionStation == "":
            self.SetStatusText("StationKey is mandatory field")
            self.CollectionStation_text.SetValue("503")
        if CollectionStation != "503" and CollectionStation != "751" :
            self.SetStatusText("Wrong station key")
        if int(InternalStation) > 751 :
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
        
if __name__ == "__main__":
    app = wx.App()
    frame = InternalAndCollection()
    frame.Show()
    app.MainLoop()