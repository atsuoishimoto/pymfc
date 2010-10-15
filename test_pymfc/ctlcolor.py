# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd, gdi

brush=gdi.Brush(color=0xff0000)
def ctlcolor(msg):
    dc = gdi.DC(hdc=msg.hdc)
    dc.setBkColor(0xff0000)
    return brush.getHandle().handle

def pppp(msg):
    print "lksmflksmflkm"
    import _pymfclib
    print _pymfclib.xxxx()

def test():
    dlg = wnd.Dialog(u"abcdefg", (200, 400), pos=(100,100))
    e = wnd.Edit(u"def", size=(100, 125), pos=(10, 10), parent=dlg)
#    e2 = wnd.Edit(u"def", size=(100, 125), pos=(10, 10), parent=dlg)
#    e3 = wnd.Edit(u"def", size=(100, 125), pos=(10, 10), parent=dlg)
    e.msgproc.CTLCOLOREDIT = ctlcolor
#
    dlg.msgproc.PARENTNOTIFY = pppp
    dlg.doModal()


for i in  xrange(10):
    test()
    
gc.collect()

import _pymfclib
print _pymfclib.xxxx()
