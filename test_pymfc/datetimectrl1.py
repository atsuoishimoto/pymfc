# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys, datetime
from pymfc import wnd

def check(msg):
    print msg.wnd._parent.datetime1.getTime()
#    msg.wnd._parent.datetime1.setFormat(u"yyyy/MM/dd HH:mm" )
    msg.wnd._parent.datetime1.setFormat(u"yyyy/MM" )

def set(msg):
    msg.wnd._parent.datetime1.setTime(datetime.date.today())

def test():
    dlg = wnd.Dialog(u"abcdefg", (300, 300), pos=(100,100))
    dlg.datetime1 = wnd.DateTimeCtrl(parent=dlg, size=(200, 20), pos=(10, 10))
    b = wnd.Button(u"get", pos=(10, 220), size=(40, 20), parent=dlg)
    b.msglistener.CLICKED = check

    b = wnd.Button(u"set", pos=(60, 220), size=(40, 20), parent=dlg)
    b.msglistener.CLICKED = set
    dlg.doModal()


for i in  range(1):
    print i
    test()
