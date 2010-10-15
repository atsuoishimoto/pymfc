# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd, gdi

def overwrite(w, dc, rc):
    dc.textOut(u"overwrite", (rc[0], rc[3]-20))
    
def ff(msg):
    print msg.getDict()
    
def test():
    dlg = wnd.Dialog(u"abcdefg", (200, 400), pos=(100,100))
    e = wnd.Edit(u"def", size=(100, 125), pos=(10, 10), parent=dlg)
    e.addOverWrite(overwrite)
    e.msglistener.CHAR = ff
    dlg.doModal()


test()
    
gc.collect()

import _pymfclib

