# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.
import time, sys, os
from pymfc import wnd, htmlhelp


path = os.path.split(os.path.abspath(sys.argv[0]))[0]
chm1 = os.path.join(path, u"test1.chm::/index.html")
chm2 = os.path.join(path, u"test1.chm::/index2.html#anchor1")

cookie = htmlhelp.init()

for i in range(1):
    dlg = wnd.Dialog(u"abcdefg", (200, 400), pos=(200,400))

    btn1 = wnd.Button(size=(60, 20), pos=(10, 360), parent=dlg, title=u"1")
    btn2 = wnd.Button(size=(60, 20), pos=(70, 360), parent=dlg, title=u"2")

    def clicked(msg):
        htmlhelp.display_topic(dlg, chm1)

        
    def clicked2(msg):
        htmlhelp.display_topic(dlg, chm2)
        
    btn1.msgproc.CLICKED=clicked
    btn2.msgproc.CLICKED=clicked2
    
    def onhelp(msg):
        print "help", msg.ctrl
    dlg.msgproc.HELP = onhelp
    dlg.doModal()

del dlg

htmlhelp.uninit(cookie)
