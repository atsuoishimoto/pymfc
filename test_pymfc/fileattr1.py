import pymfc
import _pymfclib
import _pymfclib_system
tz= _pymfclib_system.Win32TZInfo()

f = open("test", "w")
f.close()

for i in range(100):
    attr = _pymfclib_system.getFileAttribute(u"test")
    print hex(attr)

    _pymfclib_system.setFileAttribute(u"test", attr, archive=0)
    attr = _pymfclib_system.getFileAttribute(u"test")
    print hex(attr)

    _pymfclib_system.setFileAttribute(u"test", attr, archive=1)
    attr = _pymfclib_system.getFileAttribute(u"test")
    print hex(attr)
