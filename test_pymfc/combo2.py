# -*- coding: ShiftJIS -*-


# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd

def onCreate(msg):
    msg.wnd.insertItem(-1, u"abcdefg")
    msg.wnd.insertItem(-1, u"11111")
    msg.wnd.insertItem(-1, unicode("あいうえお", "mbcs"))
    msg.wnd.insertItem(-1, u"11111")
    msg.wnd.insertItem(-1, u"abcdefg")
    msg.wnd.insertItem(-1, u"11111")
    msg.wnd.setCurSel(0)
    
def check(msg):
    print msg.wnd._parent.combo1.getText()

def test():
    dlg = wnd.Dialog(u"abcdefg", (200, 300), pos=(100,100))
    dlg.combo1 = wnd.DropDownList(u"", size=(100, 200), pos=(10, 10), parent=dlg)
    dlg.combo1.msglistener.CREATE=onCreate
    
    dlg.combo2 = wnd.DropDownList(u"", size=(100, 200), pos=(10, 40), parent=dlg)

    dlg.combo3 = wnd.DropDownCombo(u"", size=(100, 200), pos=(10, 80), parent=dlg)

    b = wnd.Button(u"get", pos=(10, 220), size=(40, 20), parent=dlg)

    b.msglistener.CLICKED = check
    dlg.doModal()


for i in  range(10):
    print i
    test()