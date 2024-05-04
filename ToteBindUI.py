import wx

Batch1 = ''
Batch2 = ''
Batch3 = ''
Batch4 = ''


class FourCompartment(wx.Dialog):
    def __init__(self, parent, ToteCode, BookingNumber):
        super(FourCompartment, self).__init__(
            parent, title="Tote Binding", size=(300, 400))
        self.SetTitle("Tote Binding")
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f"輸入EAN到箱子,全部完成後按下SAVE \n訂單:{BookingNumber} -綁定{ToteCode}", pos=(30, 10))
        size = (120, 120)
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(20, 60))
        self.Batch2_text = wx.TextCtrl(
            panel, value=Batch2, size=size, pos=(160, 60))
        self.Batch3_text = wx.TextCtrl(
            panel, value=Batch3, size=size, pos=(160, 190))
        self.Batch4_text = wx.TextCtrl(
            panel, value=Batch4, size=size, pos=(20, 190))

        self.save_button = wx.Button(
            panel, label='Save', pos=(20, 320), size=(260, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        values = [self.Batch1_text.GetValue(), self.Batch2_text.GetValue(),
                  self.Batch3_text.GetValue(), self.Batch4_text.GetValue()]
        print("保存的值:", values)
        self.Close()


class TwoCompartment(wx.Dialog):
    def __init__(self, parent, ToteCode, BookingNumber):
        super(TwoCompartment, self).__init__(
            parent, title="Tote Binding", size=(300, 300))
        self.SetTitle("Tote Binding")
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f"輸入EAN到箱子,全部完成後按下SAVE \n訂單:{BookingNumber} -綁定{ToteCode}", pos=(20, 10))
        size = (120, 120)
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(20, 60))
        self.Batch2_text = wx.TextCtrl(
            panel, value=Batch2, size=size, pos=(160, 60))

        self.save_button = wx.Button(
            panel, label='Save', pos=(20, 200), size=(260, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        # 获取文本输入框的值并关闭对话框
        values = [self.Batch1_text.GetValue(), self.Batch2_text.GetValue(),
                  self.Batch3_text.GetValue(), self.Batch4_text.GetValue()]
        print("保存的值:", values)
        self.Close()


class OneCompartment(wx.Dialog):
    def __init__(self, parent, ToteCode, BookingNumber):
        super(OneCompartment, self).__init__(
            parent, title="Tote Binding", size=(260, 300))
        self.SetTitle("Tote Binding")
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f"輸入EAN到箱子,全部完成後按下SAVE \n訂單:{BookingNumber} -綁定{ToteCode}", pos=(10, 10))
        size = (170, 170)
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(45, 45))

        self.save_button = wx.Button(
            panel, label='Save', pos=(30, 230), size=(200, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event, ToteCode, BookingNumber):

        values = [self.Batch1_text.GetValue(), self.Batch2_text.GetValue(),
                  self.Batch3_text.GetValue(), self.Batch4_text.GetValue()]
        print("保存的值:", values)
        self.Close()
