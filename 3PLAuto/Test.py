import requests
from GlobalVar import *
from ToteCollection import __CollectionAPI__, __GetCollectionBookingInfo__, __MMSlogin__, __CreateCollectionBooking__
from internalToteIn import __WMSLogin__
from StationFlow import __KIOSKFlow__
TY11 = 2
TY12 = 2
TY14 = 2
__MMSlogin__(MMSAccount, MMSPasword)
BookingNumber = __CreateCollectionBooking__(TY11, TY12, TY14)
__KIOSKFlow__(BookingNumber, '503')
