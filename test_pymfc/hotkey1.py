# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd


def test():
    class D(wnd.Dialog):
        def onOk(self, msg):
            return 0
            
    dlg = D(u"abcdefg", (200, 400), pos=(100,100))
    
    ctrl = wnd.HotKeyCtrl(size=(100, 20), pos=(10, 10), parent=dlg)
    
    def onchange(msg):
        print ctrl.getHotKey()
        
    ctrl.msglistener.CHANGE = onchange
    
    btn = wnd.Button(u"get", size=(100, 20), pos=(10, 40), parent=dlg)
    btn2 = wnd.Button(u"set", size=(100, 20), pos=(10, 80), parent=dlg)
    btn3 = wnd.Button(u"register", size=(100, 20), pos=(10, 120), parent=dlg)


    def btn1clk(msg):
        print ctrl.getHotKey()

    btn.msglistener.CLICKED = btn1clk


    def btn2clk(msg):
        ctrl.setHotKey(True, False, True, False, ord('X'))
    btn2.msglistener.CLICKED = btn2clk
    
    
    def btn3clk(msg):
        alt, ctl, shift, ext, key = ctrl.getHotKey()
        dlg.registerHotKey(0x8000, alt, ctl, shift, False, key)

    btn3.msglistener.CLICKED = btn3clk
    
    
    dlg.doModal()


for i in  range(1):
    test()