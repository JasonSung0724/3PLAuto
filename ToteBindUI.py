import wx
import json
import datetime
import time
from Binding import __CheckEan__, __SendBindListMerchantAPP__
from StockIn import __StockInAPIFlow__

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
        boxsize = (50, 30)
        self.BookingNumber = BookingNumber
        self.ToteCode = ToteCode
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(20, 60))
        self.Batch2_text = wx.TextCtrl(
            panel, value=Batch2, size=size, pos=(160, 60))
        self.Batch3_text = wx.TextCtrl(
            panel, value=Batch3, size=size, pos=(20, 190))
        self.Batch4_text = wx.TextCtrl(
            panel, value=Batch4, size=size, pos=(160, 190))

        self.QTY1_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(90, 150))
        self.QTY1_text.SetBackgroundColour(wx.YELLOW)
        self.QTY1_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.QTY2_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(230, 150))
        self.QTY2_text.SetBackgroundColour(wx.YELLOW)
        self.QTY2_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.QTY3_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(90, 280))
        self.QTY3_text.SetBackgroundColour(wx.YELLOW)
        self.QTY3_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.QTY4_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(230, 280))
        self.QTY4_text.SetBackgroundColour(wx.YELLOW)
        self.QTY4_text.Bind(wx.EVT_CHAR, self.OnKeyPress)

        self.save_button = wx.Button(
            panel, label='Save', pos=(20, 320), size=(260, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

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

    def on_save(self, event):
        Barcodes = [self.Batch1_text.GetValue(), self.Batch2_text.GetValue(),
                    self.Batch3_text.GetValue(), self.Batch4_text.GetValue()]
        Processed = {}
        BindingDetail = []
        i = 1
        for ean in Barcodes:
            if ean in Processed or ean == "":
                if ean == "":
                    i += 1
                    pass
                elif ean in Processed:
                    try:
                        if i == 1:
                            cellsCode = "a"
                            QTY = int(self.QTY1_text.GetValue())
                        elif i == 2:
                            cellsCode = "b"
                            QTY = int(self.QTY2_text.GetValue())
                        elif i == 3:
                            cellsCode = "c"
                            QTY = int(self.QTY3_text.GetValue())
                        elif i == 4:
                            cellsCode = "d"
                            QTY = int(self.QTY4_text.GetValue())
                    except ValueError:
                        wx.MessageBox('若有輸入ean,數量為必填', 'Input qty error',
                                      wx.OK | wx.ICON_WARNING)
                        return
                    detail = {
                        "expiration": Processed[ean]['expiration'],
                        "partitionName": cellsCode,
                        "skuUuid": Processed[ean]['skuUuid'],
                        "inCompartmentQty": QTY,
                        "barcode": ean
                    }
                    BindingDetail.append(detail)
                    i += 1
            else:
                EanCheck = __CheckEan__(ean)
                if type(EanCheck) == str:
                    print("Ean wrong")
                    wx.MessageBox(f'{EanCheck}', f'Wrong Ean : {ean}',
                                  wx.OK | wx.ICON_WARNING)
                    return
                elif type(EanCheck) == dict:
                    try:
                        if i == 1:
                            cellsCode = "a"
                            QTY = int(self.QTY1_text.GetValue())
                        elif i == 2:
                            cellsCode = "b"
                            QTY = int(self.QTY2_text.GetValue())
                        elif i == 3:
                            cellsCode = "c"
                            QTY = int(self.QTY3_text.GetValue())
                        elif i == 4:
                            cellsCode = "d"
                            QTY = int(self.QTY4_text.GetValue())
                    except ValueError:
                        wx.MessageBox('若有輸入ean,數量為必填', 'Input qty error',
                                      wx.OK | wx.ICON_WARNING)
                        return
                    uuid = EanCheck['skuUuid']
                    if EanCheck['disableNoExpiryDateBtn'] == False:
                        expiration = 43043587200000
                    else:
                        TimeStamp = EanCheck['enableExpiryStartDate'] / 1000
                        dt = datetime.datetime.fromtimestamp(TimeStamp)
                        dtAfterOneYear = dt + datetime.timedelta(days=365)
                        dtAfterOneYear = dtAfterOneYear.replace(
                            hour=0, minute=0, second=0, microsecond=0)
                        expiration = int(dtAfterOneYear.timestamp() * 1000)
                    detail = {
                        "expiration": expiration,
                        "partitionName": cellsCode,
                        "skuUuid": uuid,
                        "inCompartmentQty": QTY,
                        "barcode": ean
                    }
                    BindingDetail.append(detail)
                    Processed[ean] = detail
                    i += 1
        if BindingDetail == []:
            wx.MessageBox('請輸入Ean', '請輸入Ean', wx.OK | wx.ICON_WARNING)
            return
        Response = __SendBindListMerchantAPP__(
            BookingNumber=self.BookingNumber, ToteCode=self.ToteCode, Detail=BindingDetail)
        print(BindingDetail)
        wx.MessageBox(f'{Response}', '綁定回應', wx.OK | wx.ICON_WARNING)
        self.Close()


class TwoCompartment(wx.Dialog):
    def __init__(self, parent, ToteCode, BookingNumber):
        super(TwoCompartment, self).__init__(
            parent, title="Tote Binding", size=(300, 300))
        self.SetTitle("Tote Binding")
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f"輸入EAN到箱子,全部完成後按下SAVE \n訂單:{BookingNumber} -綁定{ToteCode}", pos=(20, 10))
        self.BookingNumber = BookingNumber
        self.ToteCode = ToteCode
        size = (120, 120)
        boxsize = (50, 30)
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(20, 60))
        self.Batch2_text = wx.TextCtrl(
            panel, value=Batch2, size=size, pos=(160, 60))

        self.QTY1_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(90, 150))
        self.QTY1_text.SetBackgroundColour(wx.YELLOW)
        self.QTY1_text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.QTY2_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(230, 150))
        self.QTY2_text.SetBackgroundColour(wx.YELLOW)
        self.QTY2_text.Bind(wx.EVT_CHAR, self.OnKeyPress)

        self.save_button = wx.Button(
            panel, label='Save', pos=(20, 200), size=(260, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        Barcodes = [self.Batch1_text.GetValue(), self.Batch2_text.GetValue()]
        Processed = {}
        BindingDetail = []
        i = 1
        for ean in Barcodes:
            if ean in Processed or ean == "":
                if ean == "":
                    i += 1
                    pass
                elif ean in Processed:
                    try:
                        if i == 1:
                            cellsCode = "a"
                            QTY = int(self.QTY1_text.GetValue())
                        elif i == 2:
                            cellsCode = "b"
                            QTY = int(self.QTY2_text.GetValue())
                    except ValueError:
                        wx.MessageBox('若有輸入ean,數量為必填', 'Input qty error',
                                      wx.OK | wx.ICON_WARNING)
                        return
                    detail = {
                        "expiration": Processed[ean]['expiration'],
                        "partitionName": cellsCode,
                        "skuUuid": Processed[ean]['skuUuid'],
                        "inCompartmentQty": QTY,
                        "barcode": ean
                    }
                    BindingDetail.append(detail)
                    i += 1
            else:
                EanCheck = __CheckEan__(ean)
                if type(EanCheck) == str:
                    print("Ean wrong")
                    wx.MessageBox(f'{EanCheck}', f'Wrong Ean : {ean}',
                                  wx.OK | wx.ICON_WARNING)
                    return
                elif type(EanCheck) == dict:
                    try:
                        if i == 1:
                            cellsCode = "a"
                            QTY = int(self.QTY1_text.GetValue())
                        elif i == 2:
                            cellsCode = "b"
                            QTY = int(self.QTY2_text.GetValue())
                    except ValueError:
                        wx.MessageBox('若有輸入ean,數量為必填', 'Input qty error',
                                      wx.OK | wx.ICON_WARNING)
                        return
                    uuid = EanCheck['skuUuid']
                    if EanCheck['disableNoExpiryDateBtn'] == False:
                        expiration = 43043587200000
                    else:
                        TimeStamp = EanCheck['enableExpiryStartDate'] / 1000
                        dt = datetime.datetime.fromtimestamp(TimeStamp)
                        dtAfterOneYear = dt + datetime.timedelta(days=365)
                        dtAfterOneYear = dtAfterOneYear.replace(
                            hour=0, minute=0, second=0, microsecond=0)
                        expiration = int(dtAfterOneYear.timestamp() * 1000)
                    detail = {
                        "expiration": expiration,
                        "partitionName": cellsCode,
                        "skuUuid": uuid,
                        "inCompartmentQty": QTY,
                        "barcode": ean
                    }
                    BindingDetail.append(detail)
                    Processed[ean] = detail
                    i += 1
        if BindingDetail == []:
            wx.MessageBox('請輸入Ean', '請輸入Ean', wx.OK | wx.ICON_WARNING)
            return
        Response = __SendBindListMerchantAPP__(
            BookingNumber=self.BookingNumber, ToteCode=self.ToteCode, Detail=BindingDetail)
        print(BindingDetail)
        wx.MessageBox(f'{Response}', '綁定回應', wx.OK | wx.ICON_WARNING)
        self.Close()

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


class OneCompartment(wx.Dialog):
    def __init__(self, parent, ToteCode, BookingNumber):
        super(OneCompartment, self).__init__(
            parent, title="Tote Binding", size=(260, 300))
        self.SetTitle("Tote Binding")
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f"輸入EAN到箱子,全部完成後按下SAVE \n訂單:{BookingNumber} -綁定{ToteCode}", pos=(10, 10))
        self.BookingNumber = BookingNumber
        self.ToteCode = ToteCode
        size = (170, 170)
        boxsize = (50, 30)
        self.Batch1_text = wx.TextCtrl(
            panel, value=Batch1, size=size, pos=(45, 45))
        self.QTY1_text = wx.TextCtrl(
            panel, value="", size=boxsize, pos=(165, 185))
        self.QTY1_text.SetBackgroundColour(wx.YELLOW)
        self.QTY1_text.Bind(wx.EVT_CHAR, self.OnKeyPress)

        self.save_button = wx.Button(
            panel, label='Save', pos=(30, 230), size=(200, 40))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

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

    def on_save(self, event):
        ean = self.Batch1_text.GetValue()
        BindingDetail = []
        if ean == "":
            wx.MessageBox('Ean 不可為空值', 'warning',
                          wx.OK | wx.ICON_WARNING)
            return
        else:
            EanCheck = __CheckEan__(ean)
            if type(EanCheck) == str:
                print("Ean wrong")
                wx.MessageBox(f'{EanCheck}', f'Wrong Ean : {ean}',
                              wx.OK | wx.ICON_WARNING)
                return
            elif type(EanCheck) == dict:
                try:
                    cellsCode = "a"
                    QTY = int(self.QTY1_text.GetValue())
                except ValueError:
                    wx.MessageBox('若有輸入ean,數量為必填', 'Input qty error',
                                  wx.OK | wx.ICON_WARNING)
                    return
                uuid = EanCheck['skuUuid']
                if EanCheck['disableNoExpiryDateBtn'] == False:
                    expiration = 43043587200000
                else:
                    TimeStamp = EanCheck['enableExpiryStartDate'] / 1000
                    dt = datetime.datetime.fromtimestamp(TimeStamp)
                    dtAfterOneYear = dt + datetime.timedelta(days=365)
                    dtAfterOneYear = dtAfterOneYear.replace(
                        hour=0, minute=0, second=0, microsecond=0)
                    expiration = int(dtAfterOneYear.timestamp() * 1000)
                detail = {
                    "expiration": expiration,
                    "partitionName": cellsCode,
                    "skuUuid": uuid,
                    "inCompartmentQty": QTY,
                    "barcode": ean
                }
                BindingDetail.append(detail)
        if BindingDetail == []:
            wx.MessageBox('請輸入Ean', '請輸入Ean', wx.OK | wx.ICON_WARNING)
            return
        Response = __SendBindListMerchantAPP__(
            BookingNumber=self.BookingNumber, ToteCode=self.ToteCode, Detail=BindingDetail)
        print(BindingDetail)
        wx.MessageBox(f'{Response}', '綁定回應', wx.OK | wx.ICON_WARNING)
        self.Close()


class RunStockInAPI(wx.Dialog):
    def __init__(self, parent, BookingNumber):
        super(RunStockInAPI, self).__init__(
            parent, title="Run Stock-In API", size=(260, 160))
        self.SetTitle("Run Stock-In API")
        self.BookingNumber = BookingNumber
        panel = wx.Panel(self)
        self.TextLable = wx.StaticText(
            panel, label=f'訂單號碼{BookingNumber}\n請先進入工作站\n並在下方輸入工作站號碼\n按下執行後就會call api', pos=(10, 10))
        self.StationKey_text = wx.TextCtrl(
            panel, value="", size=(60, 30), pos=(10, 80))
        self.StationKey_text.Bind(wx.EVT_CHAR, self.OnKeyPress)

        self.save_button = wx.Button(
            panel, label='執行', pos=(80, 70), size=(150, 60))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)

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

    def on_save(self, event):
        stationKey = self.StationKey_text.GetValue()
        if not stationKey.startswith('1') or stationKey == "" or len(str(stationKey)) > 3:
            wx.MessageBox(f'Station Key {stationKey} wrong')
            self.StationKey_text.SetValue("")
            self.StationKey_text.Clear()
            return
        Response = __StockInAPIFlow__(BookingNumber=self.BookingNumber,
                                      StationKey=stationKey)
        print(Response)
        wx.MessageBox(f'{Response}', 'Stock-in API flow result',
                      wx.OK | wx.ICON_WARNING)
        self.Close()
