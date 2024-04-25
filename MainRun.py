from ToteRegistration import __TPLCMSlogin__ ,__NewToteRegistration__
from GlobalVar import *
from StationFlow import __KIOSKFlow__
from ToteCollection import __MMSlogin__ , __CollectionAPI__ , __CreateCollectionBooking__
from internalToteIn import __WMSLogin__ , __InternalToteInAPI__ , __CreateInternalToteInBooking__
import sqlite3
import time


__TPLCMSlogin__()
__WMSLogin__()
totelist = __NewToteRegistration__(5,5,5)
bookingNumber = __CreateInternalToteInBooking__(totelist)
stationKey = '105'
__KIOSKFlow__(bookingNumber,stationKey,totelist)
__MMSlogin__(MMSAccount,MMSPasword)
BookingNumber = __CreateCollectionBooking__(5,5,5)
__KIOSKFlow__(BookingNumber,'503',totelist)
time.sleep(10)
