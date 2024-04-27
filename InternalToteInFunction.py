from ToteRegistration import __TPLCMSlogin__, __NewToteRegistration__
from GlobalVar import *
from StationFlow import __KIOSKFlow__
from ToteCollection import __MMSlogin__, __CollectionAPI__, __CreateCollectionBooking__
from internalToteIn import __WMSLogin__, __InternalToteInAPI__, __CreateInternalToteInBooking__
import sqlite3
import time

InternalStation = '101'
CollectionStation = '503'
TY11 = 0
TY12 = 0
TY14 = 0

def __InternalToteInAndToteCollection__(TY11=0, TY12=0, TY14=0):
    __TPLCMSlogin__()
    __WMSLogin__()
    totelist = __NewToteRegistration__(TY11, TY12, TY14)
    bookingNumber = __CreateInternalToteInBooking__(totelist)
    __KIOSKFlow__(bookingNumber, InternalStation, totelist)
    __MMSlogin__(MMSAccount, MMSPasword)
    BookingNumber = __CreateCollectionBooking__(TY11, TY12, TY14)
    __KIOSKFlow__(BookingNumber, CollectionStation, totelist)
    time.sleep(3)


# __InternalToteInAndToteCollection__(2, 2, 2)
