# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import traceback
import pymfc
import _pymfclib

desktop = _pymfclib.SHItemIdList(desktop=True)
print desktop.getFilename()
print desktop.getDisplayName()

def ddd(f, lv=0):
    lv += 1
    if lv >= 4:
        return
    print "@", f.getDisplayName()
    try:
        for s in f.getSubItems(nonfolder=False):
            print ">"*lv, s.getDisplayName()
            ddd(s, lv)
    except:
        traceback.print_exc()
#        raise

    lv -= 1
        
ddd(desktop)

f = _pymfclib.SHItemIdList(filename="c:\\")
print f.getDisplayName()
