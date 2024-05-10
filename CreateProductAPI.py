import wx , os , json ,sys
import requests
from datetime import datetime
from GlobalVar import *

env = 'staging'
Account = "cindy.yeh@shoalter.com"
Password = "Aa123456"
Creator = "Jason"
ProductTypeCode = "AA11031500001"
ImageURL = "https://mms-dyn-image-server-dev.hkmpcl.com.hk/hktv/mms/uploadProductImage/0405/d595/e538/PPAwMlztdP20231031163931.jpg"
OnlineStatus = "ONLINE"
visibility = "Y"
IsPrimary = "Y"
currency = "HKD"
OriginalPrice = 100
SellingPrice = 90
PackingHeight = 10
PackingLength = 10
PackingWidth = 10
weight = 10
ReturnDays = "0"
headers = ""
AccessToken = ""
MerchantId = ""
MerchantName = ""
StoreFrontStoreCodeList = []
store_info_dict = {}
StoreFrontStoreCode = ""
StoreCode = ""
ProductReadyMethodList = []
ProductReadyMethodDict = {}
ProductReadyMethodCode = ""
DeliveryMethod = ""
WareHouseIdList = []
WareHouseDict = {}
WareHouseId = ""
PackingBoxTypeDict = {}
PackingBoxTypeList = []
MainEan = ""
Ean2 = ""
Ean3 = ""
Ean4 = ""
Ean5 = ""
PackingBoxType = ""
ProductReadyDays = ""
ProductReadyDaysCodeList = []
PickupDays = ""
PickupDaysDict = {}
PickupDaysList = []
ReturnDaysList = []
PickupTimeSlotList = []
PickupTimeSlot = ""

def TimeCreate(len=None):
    if len == None :
        current_datetime  = datetime.now()
        formatted_datetime = current_datetime.strftime("%m%d%H%M%S")
        return formatted_datetime
    else :
        current_datetime  = datetime.now()
        formatted_datetime = current_datetime.strftime("%m%d%H%M%S%f")
        return formatted_datetime
class CreateProduct(wx.Frame):
    def __init__(self):
        global Account , Password , ProductTypeCode , MainEan
        super().__init__(None, title="Create Product", size=(1000, 400))
        self.CreateStatusBar()
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.GetStatusBar().SetFont(font)
        panel = wx.Panel(self)
        self.account_label = wx.StaticText(panel, label="*Account:", pos=(15, 23))
        self.account_text = wx.TextCtrl(panel, value = Account , pos=(90, 20), size=(150, -1))
        self.account_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.password_label = wx.StaticText(panel, label="*Password:", pos=(15, 48))
        self.password_text = wx.TextCtrl(panel, value = Password ,pos=(90, 45), size=(150, -1))
        self.password_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.SKUID_label = wx.StaticText(panel, label = "Default + Timestamp" , pos=(135,83))
        self.Creator_label = wx.StaticText(panel, label="SKU ID :", pos=(15, 83))
        self.Creator_text = wx.TextCtrl(panel, value = Creator ,pos=(70, 80), size=(60, -1))
        self.Creator_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.ProductTypeCode_label = wx.StaticText(panel, label="Product Type Code:", pos=(400, 21))
        self.ProductTypeCode_text = wx.TextCtrl(panel, value = ProductTypeCode ,pos=(520, 18), size=(150, -1))
        self.ProductTypeCode_text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.Image_label = wx.StaticText(panel, label="Image server URL:", pos=(200, 287))
        self.Image_text = wx.TextCtrl(panel, value = ImageURL ,pos=(200, 304), size=(650, -1))
        self.Image_text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.OriginalPrice_label = wx.StaticText(panel, label="Original Price:", pos=(400, 48))
        self.OriginalPrice_Text = wx.TextCtrl(panel, value = str(OriginalPrice) ,pos=(520, 45), size=(150, -1))
        self.OriginalPrice_Text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.OriginalPrice_Text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.SellingPrice_label = wx.StaticText(panel, label="Selling Price:", pos=(400, 75))
        self.SellingPrice_Text = wx.TextCtrl(panel, value = str(SellingPrice) ,pos=(520, 72), size=(150, -1))
        self.SellingPrice_Text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.SellingPrice_Text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.PackingHeight_label = wx.StaticText(panel, label="Packing Height (mm):", pos=(400, 102))
        self.PackingHeight_Text = wx.TextCtrl(panel, value = str(PackingHeight) ,pos=(520, 99), size=(150, -1))
        self.PackingHeight_Text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.PackingHeight_Text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.PackingLength_label = wx.StaticText(panel, label="Packing Length (mm):", pos=(400, 129))
        self.PackingLength_Text = wx.TextCtrl(panel, value = str(PackingLength) ,pos=(520, 126), size=(150, -1))
        self.PackingLength_Text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.PackingLength_Text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.PackingWidth_label = wx.StaticText(panel, label="Packing Width (mm):", pos=(400, 156))
        self.PackingWidth_Text = wx.TextCtrl(panel, value = str(PackingWidth) ,pos=(520, 153), size=(150, -1))
        self.PackingWidth_Text.Bind(wx.EVT_TEXT,self.Set_Text_Value)
        self.PackingWidth_Text.Bind(wx.EVT_CHAR, self.OnKeyPress)
        self.Result_ctrl_label = wx.StaticText(panel, label="Previous SKU ID" ,pos=(700,245))
        self.Result_ctrl = wx.TextCtrl(panel, value="", style=wx.TE_READONLY | wx.TE_MULTILINE , pos=(700,260),size=(230,30))
        self.Response_label = wx.StaticText(panel, label="Response:" ,pos=(700,190))
        self.Response_ctrl = wx.TextCtrl(panel, value="", style=wx.TE_READONLY | wx.TE_MULTILINE , pos=(700,210),size=(230,30))

        self.ProductTypeCode_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.MainEan_label = wx.StaticText(panel, label="MainEan:", pos=(700, 48))
        self.MainEan_text = wx.TextCtrl(panel, value = MainEan ,pos=(760, 45), size=(200, -1))
        self.MainEan_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Ean2_label = wx.StaticText(panel, label="Ean2:", pos=(700, 75))
        self.Ean2_text = wx.TextCtrl(panel, value = MainEan ,pos=(760, 72), size=(200, -1))
        self.Ean2_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Ean3_label = wx.StaticText(panel, label="Ean3:", pos=(700, 102))
        self.Ean3_text = wx.TextCtrl(panel, value = MainEan ,pos=(760, 99), size=(200, -1))
        self.Ean3_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Ean4_label = wx.StaticText(panel, label="Ean4:", pos=(700, 129))
        self.Ean4_text = wx.TextCtrl(panel, value = MainEan ,pos=(760, 126), size=(200, -1))
        self.Ean4_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Ean5_label = wx.StaticText(panel, label="Ean5:", pos=(700, 156))
        self.Ean5_text = wx.TextCtrl(panel, value = MainEan ,pos=(760, 153), size=(200, -1))
        self.Ean5_text.Bind(wx.EVT_TEXT, self.Set_Text_Value)
        self.Ean2_label.Hide(),self.Ean2_text.Hide(),self.Ean3_label.Hide(),self.Ean3_text.Hide(),self.Ean4_label.Hide(),self.Ean4_text.Hide(),self.Ean5_label.Hide(),self.Ean5_text.Hide()



        self.StoreFrontStoreCode_label = wx.StaticText(panel, label="*StoreFront:", pos=(15, 123))
        self.StoreFrontOption = wx.Choice(panel, choices=StoreFrontStoreCodeList, pos=(15, 140) ,size =(170,-1))
        self.StoreFrontOption.Bind(wx.EVT_CHOICE, self.Select_Store)
        self.ProductReadyMethod_lable = wx.StaticText(panel, label="*ProductReadyMethod:", pos=(15, 173))
        self.ProductReadyMethodOption = wx.Choice(panel, choices=ProductReadyMethodList, pos=(15, 190) ,size =(150,-1))
        self.ProductReadyMethodOption.Bind(wx.EVT_CHOICE, self.Select_Product_Ready_Method)
        self.WareHouse_lable = wx.StaticText(panel, label="WareHouse:", pos=(15, 223))
        self.WareHouseOption = wx.Choice(panel, choices=WareHouseIdList, pos=(15, 240) ,size =(150,-1))
        self.WareHouseOption.Bind(wx.EVT_CHOICE, self.Select_WareHouse)
        self.PackingBoxType_lable = wx.StaticText(panel, label="Packing Box Type:", pos=(200, 193))
        self.PackingBoxTypeOption = wx.Choice(panel, choices=PackingBoxTypeList, pos=(200, 210) ,size =(200,-1))
        self.PackingBoxTypeOption.Bind(wx.EVT_CHOICE, self.Select_Packing_Box_Type)
        self.PickupTimeSlot_lable = wx.StaticText(panel, label="Pickup TimeSlot:", pos=(440, 193))
        self.PickupTimeSlotOption = wx.Choice(panel, choices=PickupTimeSlotList, pos=(440, 210) ,size =(200,-1))
        self.PickupTimeSlotOption.Bind(wx.EVT_CHOICE, self.Select_Pickup_TimeSlot)
        self.ProductReadyDays_lable = wx.StaticText(panel, label="Product Ready Days:", pos=(440, 240))
        self.ProductReadyDaysOption = wx.Choice(panel, choices=ProductReadyDaysCodeList, pos=(440, 257) ,size =(200,-1))
        self.ProductReadyDaysOption.Bind(wx.EVT_CHOICE, self.Select_Product_Ready_Days)
        self.ReturnDays_lable = wx.StaticText(panel, label="Return Days:", pos=(15, 268))
        self.ReturnDaysOption = wx.Choice(panel, choices=ReturnDaysList, pos=(15, 285) ,size =(150,-1))
        self.ReturnDaysOption.Bind(wx.EVT_CHOICE, self.Select_Return_Days)
        self.PickUpDays_lable = wx.StaticText(panel, label="PickUp Days:", pos=(200, 240))
        self.PickUpDaysOption = wx.Choice(panel, choices=PickupDaysList, pos=(200, 257) ,size =(200,-1))
        self.PickUpDaysOption.Bind(wx.EVT_CHOICE, self.Select_PickUp_Days)


        Logintbtn = wx.Button(panel, label="Login", pos=(250, 40) , size=(120,30))
        Logintbtn.Bind(wx.EVT_BUTTON, self.Get_Merchant_Info)
        self.IsPrimarySku_Lable = wx.StaticText(panel, label="IsPrimarySku:", pos=(200, 134))
        self.IsPrimarySkuButton = wx.ToggleButton(panel, label="Yes" , pos = (300,131))
        self.IsPrimarySkuButton.Bind(wx.EVT_TOGGLEBUTTON, self.Is_Primary_Sku)
        self.Visibility_Lable = wx.StaticText(panel, label="Visibility:", pos=(200, 161))
        self.VisibilityButton = wx.ToggleButton(panel, label="Yes" , pos = (300,158))
        self.VisibilityButton.Bind(wx.EVT_TOGGLEBUTTON, self.Is_Visibility)
        self.OnlineStatus_Lable = wx.StaticText(panel, label="Online Status:", pos=(200, 107))
        self.OnlineStatusButton = wx.ToggleButton(panel, label="OnLine" , pos = (300,104))
        self.OnlineStatusButton.Bind(wx.EVT_TOGGLEBUTTON, self.Online_Status)
        GenerateEan = wx.Button(panel, label="GenerateEan", pos=(810, 18) , size=(100,-1))
        GenerateEan.Bind(wx.EVT_BUTTON, self.Generate_Ean)
        BatchEan = wx.Button(panel, label="BatchEan", pos=(700, 18) , size=(100,-1))
        BatchEan.Bind(wx.EVT_BUTTON, self.Batch_Ean)
        CreateProductbtn = wx.Button(panel, label="Create!", pos=(900, 300))
        CreateProductbtn.Bind(wx.EVT_BUTTON, self.Save_Product_Button)
        self.ENVButton = wx.ToggleButton(panel, label="DEV" , pos = (250,10) ,size=(120,30) )
        self.ENVButton.Bind(wx.EVT_TOGGLEBUTTON, self.ENV_Setting)
        
    def ENV_Setting(self ,event):
        global env
        if self.ENVButton.GetValue():
            env = 'staging'
            self.ENVButton.SetLabel(f"{env}")
            print(env)
            self.SetStatusText(f"ENV set to {env}")
            cur.execute(f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{env}' WHERE ID = 1")
            conn.commit()
        else:
            env = 'dev'
            self.ENVButton.SetLabel(f"{env}")
            print(env)
            self.SetStatusText(f"ENV set to {env}")
            cur.execute(f"UPDATE `Var_3PL_Table` SET `TestEnv` = '{env}' WHERE ID = 1")
            conn.commit()  
            
    def Select_Return_Days(self , event):
        global ReturnDays
        if self.ReturnDaysOption.GetStringSelection() :
            ReturnDays = self.ReturnDaysOption.GetStringSelection()
            return
        ReturnDaysList = []
        ReturnDaysList = ["0","7"]
        self.ReturnDaysOption.Clear()
        self.ReturnDaysOption.AppendItems(ReturnDaysList)
        self.ReturnDaysOption.SetSelection(0)

    def Select_PickUp_Days(self , event):
        global PickupDays , ProductReadyMethodCode , PickupDaysList
        if self.PickUpDaysOption.GetStringSelection() :
            PickupDays = PickupDaysDict[self.PickUpDaysOption.GetStringSelection()]['PickupDaysCode']
            return
        GetPickupDaysURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/pickupDays?buCode=HKTV&storeId={StoreId}&productReadyMethodCode={ProductReadyMethodCode}'
        GetPickupDaysResponse = requests.get(GetPickupDaysURL,headers=headers)
        PickupDaysResponse = GetPickupDaysResponse.json()
        PickupDaysList = []
        for option in PickupDaysResponse['data']:
            PickupDaysText = option['longDesc']
            PickupDaysCode = option['code']
            PickupDaysDict[str(PickupDaysText)] = {
                "PickupDaysCode" : PickupDaysCode
            }
            PickupDaysList.append(PickupDaysText)
        self.PickUpDaysOption.AppendItems(PickupDaysList)
        PickupDays = PickupDaysDict[PickupDaysList[0]]['PickupDaysCode']
        self.PickUpDaysOption.SetSelection(0)


    def Select_Product_Ready_Days(self , event):
        global ProductReadyDays , ProductReadyMethodCode
        if self.ProductReadyDaysOption.GetStringSelection() :
            ProductReadyDays = self.ProductReadyDaysOption.GetStringSelection()
            return
        GetProductReadyDaysURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/readyDays?buCode=HKTV&productReadyMethodCode={ProductReadyMethodCode}'
        GetProductReadyDaysResponse = requests.get(GetProductReadyDaysURL , headers= headers)
        ProductReadyDaysResponse = GetProductReadyDaysResponse.json()
        ProductReadyDaysCodeList = []
        for option in ProductReadyDaysResponse['data']:
            ProductReadyDaysCode = option['parmValue']
            ProductReadyDaysCodeList.append(ProductReadyDaysCode)
        self.ProductReadyDaysOption.AppendItems(ProductReadyDaysCodeList)
        ProductReadyDays = ProductReadyDaysCodeList[0]
        self.ProductReadyDaysOption.SetSelection(0)
    
    def Select_Pickup_TimeSlot(self , event):
        global PickupTimeSlot , ProductReadyMethodCode
        if self.PickupTimeSlotOption.GetStringSelection() :
            PickupTimeSlot = self.PickupTimeSlotOption.GetStringSelection()
            return
        GetPickUpTimeSlotURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/timeSlot?buCode=HKTV&productReadyMethodCode={ProductReadyMethodCode}'
        GetPickUpTimeSlotResponse = requests.get(GetPickUpTimeSlotURL , headers= headers)
        PickupTimeSlotList = []
        PickUpTimeSlotResponse = GetPickUpTimeSlotResponse.json()
        for option in PickUpTimeSlotResponse['data']:
            PickUpTimeSlotCode = option['code']
            PickupTimeSlotList.append(PickUpTimeSlotCode)
        self.PickupTimeSlotOption.AppendItems(PickupTimeSlotList)
        PickupTimeSlot = PickupTimeSlotList[0]
        self.PickupTimeSlotOption.SetSelection(0)

    def Batch_Ean(self , event):
        global ProductReadyMethodCode , MainEan , Ean2 , Ean3 , Ean4 , Ean5
        if ProductReadyMethodCode == "3PL" :
            self.Ean2_label.Show()
            self.Ean2_text.Show()
            self.Ean3_label.Show()
            self.Ean3_text.Show()
            self.Ean4_label.Show()
            self.Ean4_text.Show()
            self.Ean5_label.Show()
            self.Ean5_text.Show()
        else :
            self.Ean2_label.Hide()
            self.Ean2_text.Hide()
            self.Ean2_text.SetValue("")
            Ean2 = ""
            self.Ean3_label.Hide()
            self.Ean3_text.Hide()
            self.Ean3_text.SetValue("")
            Ean3 = ""
            self.Ean4_label.Hide()
            self.Ean4_text.Hide()
            self.Ean4_text.SetValue("")
            Ean4 = ""
            self.Ean5_label.Hide()
            self.Ean5_text.Hide()
            self.Ean5_text.SetValue("")
            Ean5 = ""

    def Generate_Ean (self , event):
        global MainEan , Ean2 , Ean3 , Ean4 , Ean5
        if MainEan == "" :
            MainEan = "Barcode" + TimeCreate(1)
            self.MainEan_text.SetValue(MainEan)
            self.SetStatusText("MainEan generate success : " + MainEan)
            return
        elif self.Ean2_label.IsShown() :
            if Ean2 == "" :
                Ean2 = "Barcode" + TimeCreate(1)
                self.Ean2_text.SetValue(Ean2)
                self.SetStatusText("Ean2 generate success : " + Ean2)
                return
            elif Ean3 == "" :
                Ean3 = "Barcode" + TimeCreate(1)
                self.Ean3_text.SetValue(Ean3)
                self.SetStatusText("Ean3 generate success : " + Ean3)
                return
            elif Ean4 == "" :
                Ean4 = "Barcode" + TimeCreate(1)
                self.Ean4_text.SetValue(Ean4)
                self.SetStatusText("Ean4 generate success : " + Ean4)
                return
            elif Ean5 == "" :
                Ean5 = "Barcode" + TimeCreate(1)
                self.Ean5_text.SetValue(Ean5)
                self.SetStatusText("Ean5 generate success : " + Ean5)
                return

    def Online_Status(self , event):
        global OnlineStatus
        if self.OnlineStatusButton.GetValue():
            self.OnlineStatusButton.SetLabel("OffLine")
            OnlineStatus = "OFFLINE"
        else :
            self.OnlineStatusButton.SetLabel("OnLine")
            OnlineStatus = "ONLINE"
    def Is_Visibility (self , event):
        global visibility
        if self.VisibilityButton.GetValue():
            self.VisibilityButton.SetLabel("No")
            visibility = "N"
        else :
            self.VisibilityButton.SetLabel("Yes")
            visibility = "Y"
        self.SetStatusText("SKU Visiable ?  = " + visibility)
    def Is_Primary_Sku (self , event):
        global IsPrimary 
        if self.IsPrimarySkuButton.GetValue():
            self.IsPrimarySkuButton.SetLabel("No")
            IsPrimary = "N"
        else:
            self.IsPrimarySkuButton.SetLabel("Yes")
            IsPrimary = "Y"
        self.SetStatusText("Is Primary SKU = " + IsPrimary)
    def Select_Store(self, event):
        global StoreFrontStoreCode , StoreId , contract_no , StoreCode
        if self.StoreFrontOption.GetStringSelection() :
            self.ProductReadyDaysOption.Clear()
            self.ProductReadyDaysOption.Clear()
            self.WareHouseOption.Clear()
            self.PackingBoxTypeOption.Clear()
            self.PickUpDaysOption.Clear()
            self.PickupTimeSlotOption.Clear()
            self.ProductReadyMethodOption.Clear()
        storeName = self.StoreFrontOption.GetStringSelection()
        StoreFrontStoreCode = store_info_dict[storeName]['storefrontStoreCode']+"-"+storeName
        self.SetStatusText("Selected Option:" + StoreFrontStoreCode)
        StoreId = store_info_dict[storeName]["storeId"]
        StoreCode = store_info_dict[storeName]["storeCode"]
        contract_no = store_info_dict[storeName]["contractId"]
        GetProductReadyMethodURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/productReadyMethod?buCode=HKTV&contractId={contract_no}'
        ReadyMethodResponse = requests.get(GetProductReadyMethodURL , headers = headers).json()
        ProductReadyMethodList = []
        for option in ReadyMethodResponse['data'] :
            ProductReadyMethodText = option['longDesc']
            ProductReadyMethodcode = option['code']
            if ProductReadyMethodText and ProductReadyMethodcode :
                ProductReadyMethodDict[str(ProductReadyMethodText)] = {
                    "ProductReadyMethodcode" : ProductReadyMethodcode
                }
            ProductReadyMethodList.append(ProductReadyMethodText)
        self.ProductReadyMethodOption.Clear()
        self.ProductReadyMethodOption.AppendItems(ProductReadyMethodList)

    def Select_Packing_Box_Type(self ,event) :
        global PackingBoxType , PackingBoxTypeDict
        if self.PackingBoxTypeOption.GetStringSelection() :
            PackingBoxTypeText = self.PackingBoxTypeOption.GetStringSelection()
            PackingBoxType = PackingBoxTypeDict[PackingBoxTypeText]['PackingBoxTypeCode']
            return
        PackingBoxTypeURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/packingBoxType?buCode=HKTV&categoryCode={ProductTypeCode}&productReadyMethodCode={ProductReadyMethodCode}'
        PackingBoxTypeResponse = requests.get(PackingBoxTypeURL , headers= headers).json()
        PackingBoxTypeList = []
        for option in PackingBoxTypeResponse['data'] :
            PackingBoxTypeText = option['longDesc']
            PackingBoxTypeDict[str(PackingBoxTypeText)] = {
                "PackingBoxTypeCode" : option['code']
            }
            PackingBoxTypeList.append(PackingBoxTypeText)
        self.PackingBoxTypeOption.AppendItems(PackingBoxTypeList)
        PackingBoxType = PackingBoxTypeDict[PackingBoxTypeList[0]]["PackingBoxTypeCode"]
        self.PackingBoxTypeOption.SetSelection(0)
    
    def Select_Product_Ready_Method(self , event):
        global ProductReadyMethodCode , WareHouseId , MainEan , DeliveryMethod
        self.SetStatusText("Select Product Ready Method : " + self.ProductReadyMethodOption.GetStringSelection())
        ProductReadyMethodText = self.ProductReadyMethodOption.GetStringSelection()
        ProductReadyMethodCode = ProductReadyMethodDict[ProductReadyMethodText]['ProductReadyMethodcode']
        self.MainEan_text.SetValue("")
        MainEan = ""
        self.ProductReadyDaysOption.Clear()
        self.Select_Product_Ready_Days(event)
        self.PackingBoxTypeOption.Clear()
        self.Select_Packing_Box_Type(event)
        self.PickupTimeSlotOption.Clear()
        self.Select_Pickup_TimeSlot(event)
        self.PickUpDaysOption.Clear()
        self.Select_PickUp_Days(event)
        self.ReturnDaysOption.Clear()
        self.Select_Return_Days(event)
        self.Batch_Ean(event)
        self.WareHouseOption.Clear()
        self.Select_WareHouse(event)
        if ProductReadyMethodCode == "3PL" and MainEan == "":
            self.Generate_Ean(event)
        GetDeliveryMethodURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/deliveryMethod?buCode=HKTV&productReadyMethodCode={ProductReadyMethodCode}'
        GetDeliveryMethodResponse = requests.get(GetDeliveryMethodURL, headers=headers).json()
        DeliveryMethod = GetDeliveryMethodResponse['data']['code']

    
    def Select_WareHouse(self , event):
        global WareHouseId
        if self.WareHouseOption.GetStringSelection():
            WareHouseIdSelect = self.WareHouseOption.GetStringSelection()
            WareHouseId = WareHouseIdSelect
            return
        GetWareHouseURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/warehouse?storeId={StoreId}&productReadyMethodCode={ProductReadyMethodCode}'
        GetWareHouseResponse = requests.get(GetWareHouseURL , headers=headers)
        WareHouseResponse = GetWareHouseResponse.json()
        WareHouseIdList = []
        for option in WareHouseResponse['data'] :
            warehouseId = option['warehouseId']
            WareHouseDict[str(warehouseId)] = {
                "storeWarehouseId" : option['storeWarehouseId']
            }
            WareHouseIdList.append(warehouseId)
        if not WareHouseIdList :
            self.SetStatusText("No warehouse can select , please sync warehouse before create product")
        else :
            WareHouseId = WareHouseDict[WareHouseIdList[0]]['storeWarehouseId']
            self.WareHouseOption.AppendItems(WareHouseIdList)
            self.WareHouseOption.SetSelection(0)


    def Set_Text_Value(self, event):
        global Account , Password , ProductTypeCode , OriginalPrice , SellingPrice , MainEan , Ean2 , Ean3 , Ean4 , Ean5 ,\
            PackingHeight , PackingLength , PackingWidth , ImageURL , Creator
        Account = self.account_text.GetValue()
        Password = self.password_text.GetValue()
        ProductTypeCode = self.ProductTypeCode_text.GetValue()
        MainEan = self.MainEan_text.GetValue()
        Ean2 = self.Ean2_text.GetValue()
        Ean3 = self.Ean3_text.GetValue()
        Ean4 = self.Ean4_text.GetValue()
        Ean5 = self.Ean5_text.GetValue()
        Creator = self.Creator_text.GetValue()
        ImageURL = self.Image_text.GetValue()
        if self.OriginalPrice_Text.GetValue() != "":
            OriginalPrice = float(self.OriginalPrice_Text.GetValue())
        else :
            OriginalPrice = ""
            self.SetStatusText("Original Price is mandatory field")
        if self.SellingPrice_Text.GetValue() != "":
            SellingPrice =float(self.SellingPrice_Text.GetValue())
        else :
            SellingPrice = ""
        if self.PackingHeight_Text.GetValue() != "":
            PackingHeight = float(self.PackingHeight_Text.GetValue())
        else :
            PackingHeight = ""
        if self.PackingLength_Text.GetValue() != "":
            PackingLength = float(self.PackingLength_Text.GetValue())
        else :
            PackingLength = ""
        if self.PackingWidth_Text.GetValue() != "":
            PackingWidth = float(self.PackingWidth_Text.GetValue())
        else :
            PackingWidth = ""

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

    def Get_Merchant_Info(self,event):
        global Account , Password , headers ,\
            AccessToken, MerchantId , store_info_dict , MerchantName
        try :
            Login_url = f'https://mms-user-{env}.hkmpcl.com.hk/user/login/merchantAppLogin2'
            print(Login_url)
            login_request_body = {
                "password": Password,
                "username": Account
            }
            Tokenresponse = requests.post(Login_url , json=login_request_body)
            print(Tokenresponse.json())
            AccessToken = Tokenresponse.json()['accessToken']
        except :
            Login_url = f'https://mms-user-{env}.hkmpcl.com.hk/user/login/webLogi'
            login_request_body = {
            "userCode": "jason.sung@shoalter.com",
            "userPwd": "BeF0YoWHPn5DOG7JMHwCVQ=="
            }
            Tokenresponse = requests.post(Login_url , json=login_request_body)
            print(Tokenresponse.json())
            AccessToken = Tokenresponse.json()['accessToken']
        if Tokenresponse.status_code == 200 :
            self.SetStatusText("Login success :  Account : " + Account + " Paswword : " + Password)
            self.ProductReadyDaysOption.Clear()
            self.ProductReadyDaysOption.Clear()
            self.StoreFrontOption.Clear()
            self.WareHouseOption.Clear()
            self.PackingBoxTypeOption.Clear()
            self.PickUpDaysOption.Clear()
            self.PickupTimeSlotOption.Clear()
            self.ProductReadyMethodOption.Clear()
            86
            Profile_url = f'https://mms-user-{env}.hkmpcl.com.hk/user/login/profile'
            headers = {
                'Authorization': f'Bearer {AccessToken}'
            }
            Profile_Response = requests.post(Profile_url , headers = headers)
            print(Profile_Response.status_code)
            print(Profile_Response.json())
            MerchantName = Profile_Response.json()['merchantName']
            MerchantId = Profile_Response.json()['merchantId']
            StoreFrontStoreCodeList = []
            storeurl = f'https://mms-product-{env}.hkmpcl.com.hk/product/store?merchantId={MerchantId}'
            sotore_Response = requests.get(storeurl , headers = headers)
            StoreData = sotore_Response.json()
            for store in StoreData["data"]:
                if "storeId" in store and "storeName" in store:
                    storeName = store["storeName"]
                    store_info_dict[str(storeName)] = {
                        "storeId": store["storeId"], 
                        "storefrontStoreCode": store["storefrontStoreCode"], 
                        "contractId": store["contractId"],
                        "storeCode": store["storeCode"]
                    }
                    StoreFrontStoreCodeList.append(storeName)
            self.StoreFrontOption.Clear()
            self.StoreFrontOption.AppendItems(StoreFrontStoreCodeList)

        else :
            self.SetStatusText("Account : " + Account + " Paswword : " + Password + " !!Login Fail!! ")


    def Save_Product_Button(self, event):
        global OriginalPrice , SellingPrice , MerchantId , Creator , MainEan , Ean2 , Ean3 , Ean4 , Ean5 
        if OriginalPrice == '' :
            self.SetStatusText("Original Price is mandatory field")
            return
        if float(OriginalPrice) <= float(SellingPrice):
            self.SetStatusText("Original Price can not less then Selling Price")
            return
        Barcodes = [
            {
                "ean": MainEan,
                "sequence_no":1
            }
        ]
        i = 0
        BatchEanList = []
        BatchEanList.extend(filter(None, [Ean2, Ean3, Ean4, Ean5]))
        BatchEanListLegnth = len(BatchEanList)
        while i < BatchEanListLegnth :
            Barcodes.append({"ean": BatchEanList[i], "sequence_no": i+2})
            i += 1
        SKUID = Creator + "_" + ProductReadyMethodCode + "_" + str(TimeCreate())
        ProductId = SKUID
        skuNameEn = SKUID
        skuNameCh = SKUID
        SkuShortDescriptionEn = SKUID
        SkuShortDescriptionCh = SKUID
        if StoreCode and contract_no and ProductReadyMethodCode and DeliveryMethod and MerchantId and SKUID and ImageURL and StoreId is not None :
            Create_Product_body = {
                "product": {
                    "barcodes":Barcodes,
                    "weight_unit": "g",
                    "weight": weight,
                    "brand_id": 7,
                    "merchant_id": MerchantId,
                    "sku_id": SKUID,
                    "manufactured_country": "AT",
                    "packing_dimension_unit": "mm",
                    "packing_height": PackingHeight,
                    "packing_length": PackingLength,
                    "packing_depth": PackingWidth,
                    "packing_box_type": PackingBoxType,
                    "original_price": OriginalPrice,
                    "product_id": ProductId,
                    "merchant_name": MerchantName,
                    "sku_name_en": skuNameEn,
                    "sku_name_ch": skuNameCh,
                    "additional": {
                        "hktv": {
                            "stores": StoreCode,
                            "product_ready_method": ProductReadyMethodCode,
                            "delivery_method": DeliveryMethod,
                            "product_type_code": [
                                ProductTypeCode
                            ],
                            "primary_category_code": ProductTypeCode,
                            "visibility": visibility,
                            "currency": currency,
                            "contract_no": contract_no,
                            "is_primary_sku": IsPrimary,
                            "sku_short_description_en": f"<p>{SkuShortDescriptionEn}</p>",
                            "sku_short_description_ch": f"<p>{SkuShortDescriptionCh}</p>",
                            "selling_price": SellingPrice,
                            "mall_dollar": 0,
                            "vip_mall_dollar": 0,
                            "main_photo": ImageURL,
                            "warehouse_id": WareHouseId,
                            "return_days": ReturnDays,
                            "product_ready_days": ProductReadyDays,
                            "pickup_days": PickupDays,
                            "pickup_timeslot": PickupTimeSlot,
                            "online_status": OnlineStatus,
                            "store_id": StoreId
                        },
                        "3pl": {
                            "carton_size": [
                                {}
                            ]
                        }
                    }
                }
            }
            CreateProductURL = f'https://mms-product-{env}.hkmpcl.com.hk/product/single/save'
            CreateProductResponse = requests.post(CreateProductURL , json=Create_Product_body , headers = headers)
            self.Response_ctrl.SetValue(str(CreateProductResponse.json()))
            if CreateProductResponse.status_code == 200 :
                wx.MessageBox(f"SKU ID : {SKUID}","Create product successfully.", wx.OK | wx.ICON_INFORMATION)
                self.Result_ctrl.SetValue(f"{SKUID}")
                print(Create_Product_body)
            self.MainEan_text.SetValue("")
            MainEan = ""
            self.Ean2_text.SetValue("")
            Ean2 = ""
            self.Ean3_text.SetValue("")
            Ean3 = ""
            self.Ean4_text.SetValue("")
            Ean4 = ""
            self.Ean5_text.SetValue("")
            Ean5 = ""
            self.Generate_Ean(event)
        else:
            self.SetStatusText("Required fields are not filled in")

if __name__ == "__main__":
    app = wx.App()
    frame = CreateProduct()
    frame.Show()
    app.MainLoop()