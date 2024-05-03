import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(300, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        button = wx.Button(panel, label='彈出輸入框')
        button.Bind(wx.EVT_BUTTON, self.on_button_click)
        vbox.Add(button, flag=wx.EXPAND|wx.ALL, border=10)

        panel.SetSizer(vbox)

    def on_button_click(self, event):
        dialog = wx.TextEntryDialog(self, '請輸入:', '輸入框')
        if dialog.ShowModal() == wx.ID_OK:
            input_value = dialog.GetValue()
            self.execute_function(input_value)
        dialog.Destroy()

    def execute_function(self, value):
        print("執行函數，輸入值為:", value)

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None, title='彈出輸入框示例')
    frame.Show()
    app.MainLoop()
