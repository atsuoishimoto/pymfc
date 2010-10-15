# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd



for i in range(10):
    dlg = wnd.Dialog(u"abcdefg", (300, 300), pos=(100,100))
    tab = wnd.TabCtrl(u"abcde", size=(300, 100), pos=(0, 100), 
        style=wnd.TabCtrlStyle(wnd.TabCtrl.STYLE, multiline=True),
        parent=dlg)
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"0abcdefg")
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"1abcdefg")
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"2abcdefg")
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"3abcdefg")
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"4abcdefg")
    tab.msglistener.CREATE=lambda ev:ev.wnd.insertItem(0, u"5abcdefg")

    dlg.doModal()

del dlg