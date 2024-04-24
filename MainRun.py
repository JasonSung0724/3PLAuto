from ToteRegistration import __TPLCMSlogin__ ,__NewToteRegistration__
from GlobalVar import *
from StationFlow import __KIOSKFlow__
from internalToteIn import __WMSLogin__ , __InternalToteInAPI__ , __CreateInternalToteInBooking__
import sqlite3
import time


__TPLCMSlogin__()
__WMSLogin__()
totelist = __NewToteRegistration__(10,10,10)
bookingNumber = __CreateInternalToteInBooking__(totelist)
stationKey = '102'
__KIOSKFlow__(bookingNumber,stationKey,totelist)
time.sleep(10)
