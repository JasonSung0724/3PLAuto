import wx
from ToteRegistration import __TPLCMSlogin__
from ToteCollection import __MMSlogin__
from internalToteIn import __WMSLogin__
from CreateProductAPI import CreateProduct
from InternalAndCollectionUI import InternalAndCollection
from OnlyInternalToteInAPI import OnlyInternalAPI
from OnlyCollectionAPI import CollectionAPI
from StockOutUI import StockOutAPI
from StockInUI import StockInUI
from GlobalVar import *
import sys
from io import StringIO


class LogWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Log Viewer", size=(400, 300))

        self.log_text = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.stdout_orig = sys.stdout
        self.stderr_orig = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        sys.stdout.write = self.write_text_ctrl
        sys.stderr.write = self.write_text_ctrl

    def write_text_ctrl(self, text):
        self.log_text.AppendText(text)

    def __del__(self):
        sys.stdout = self.stdout_orig
        sys.stderr = self.stderr_orig


class ServiceSelectionFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="3PL service", size=(240, 400))
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT,
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        panel = wx.Panel(self)
        cur.execute("SELECT TestEnv FROM `Var_3PL_Table` WHERE ID = 1")
        Result = cur.fetchone()
        TestEnv = Result[0]
        conn.commit()
        self.ENVButton = wx.ToggleButton(
            panel, label=f"{TestEnv}", pos=(10, 250), size=(205, 80))
        self.ENVButton.Bind(wx.EVT_TOGGLEBUTTON, self.ENV_Setting)

        self.Option1_radio = wx.RadioButton(
            panel, label='Only internal tote-in API')
        self.Option2_radio = wx.RadioButton(
            panel, label='Internal tote-in + Tote collection')
        self.Option3_radio = wx.RadioButton(
            panel, label='Only tote collection API')
        self.Option4_radio = wx.RadioButton(
            panel, label='Stock-in binding + API')
        self.Option5_radio = wx.RadioButton(panel, label='Stock-out API')
        self.Option6_radio = wx.RadioButton(panel, label='Create Product')

        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option1_radio)
        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option2_radio)
        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option3_radio)
        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option4_radio)
        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option5_radio)
        self.Bind(wx.EVT_RADIOBUTTON,
                  self.on_select_service, self.Option6_radio)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.Option1_radio, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.Option2_radio, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.Option3_radio, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.Option4_radio, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.Option5_radio, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.Option6_radio, 0, wx.ALL | wx.EXPAND, 10)
        panel.SetSizer(sizer)
        self.current_frame = None

    def on_select_service(self, event):
        selected_service = event.GetEventObject().GetLabel()
        if self.current_frame:
            self.current_frame.Close()
        if selected_service == 'Internal tote-in + Tote collection':
            self.current_frame = InternalAndCollection()
        elif selected_service == 'Only internal tote-in API':
            self.current_frame = OnlyInternalAPI()
        elif selected_service == 'Only tote collection API':
            self.current_frame = CollectionAPI()
        elif selected_service == 'Create Product':
            self.current_frame = CreateProduct()
        elif selected_service == 'Stock-out API':
            self.current_frame = StockOutAPI()
        elif selected_service == 'Stock-in binding + API':
            self.current_frame = StockInUI()
        if self.current_frame:
            self.current_frame.Show()

    def ENV_Setting(self, event):
        if self.ENVButton.GetValue():
            TestEnv = 'staging'
            self.ENVButton.SetLabel(f"{TestEnv}")
            print(TestEnv)
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{TestEnv}' WHERE ID = 1")
            conn.commit()
            self.SetStatusText(f"ENV set to {TestEnv}")
            __TPLCMSlogin__()
            __WMSLogin__()
        else:
            TestEnv = 'dev'
            self.ENVButton.SetLabel(f"{TestEnv}")
            print(TestEnv)
            cur.execute(
                f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{TestEnv}' WHERE ID = 1")
            conn.commit()
            self.SetStatusText(f"ENV set to {TestEnv}")
            __TPLCMSlogin__()
            __WMSLogin__()


if __name__ == "__main__":
    app = wx.App()
    frame = ServiceSelectionFrame()
    frame.Show()
    log_window = LogWindow()
    log_window.Show()
    __TPLCMSlogin__()
    __WMSLogin__()
    app.MainLoop()
