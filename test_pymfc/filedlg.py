# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd

for i in range(10):
    dlg = wnd.FileDialog(title=u'abcdefg', multiselect=True, height=300)

    e = wnd.Edit(title=unicode("あいうえお", "mbcs"), size=(200, 20), pos=(200, 10), parent=dlg)
    wnd.Static(title=u"abcdefg", size=(200, 20), pos=(200, 40), parent=dlg)

    def f(ev):
        print ev, ev.wnd, "change"
        pass
        

    e.msglistener.CHANGE = f
    
    f = dlg.openDlg()
    print f

