import pymfc
import _pymfclib
import _pymfclib_system
tz= _pymfclib_system.Win32TZInfo()
print tz._tzname
print tz._offset

import datetime
print datetime.datetime.now(tz=tz)
print datetime.datetime.utcnow()
