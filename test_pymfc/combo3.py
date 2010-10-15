# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd
from pymfc import completecombo


def onCreate(msg):
    msg.wnd.addItem(u"113")
    msg.wnd.addItem(u"111")
    msg.wnd.addItem(u"1122333")
    msg.wnd.addItem(u"1131")
    msg.wnd.addItem(u"112211")
    msg.wnd.addItem(u"112211")
    msg.wnd.addItem(unicode("ああ", "mbcs"))
    msg.wnd.addItem(unicode("あい", "mbcs"))
    msg.wnd.addItem(unicode("あいう", "mbcs"))
    msg.wnd.setCurSel(0)

def check(msg):
    print msg.wnd._parent.combo1.getText(), msg.wnd._parent.combo2.getText()
    
def test():
    dlg = wnd.Dialog(u"abcdefg", (300, 300), pos=(100,100))
    dlg.combo1 = completecombo.CompleteCombo(u"", 
            size=(100, 100), pos=(10, 10), parent=dlg)
    dlg.combo1.msglistener.CREATE=onCreate

    dlg.combo2 = completecombo.CompleteDropDownCombo(u"", 
            size=(100, 100), pos=(110, 10), parent=dlg)
    dlg.combo2.msglistener.CREATE=onCreate

    print isinstance(dlg.combo2, completecombo.CompleteCombo)
    b = wnd.Button(u"get", pos=(10, 220), size=(40, 20), parent=dlg)

    b.msglistener.CLICKED = check
    dlg.doModal()


for i in  range(1):
    print i
    test()
