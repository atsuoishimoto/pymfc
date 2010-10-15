# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.
import time
from pymfc import wnd

for i in range(1):
    class D(wnd.Dialog):
        CONTEXT = True
        ROLE = "KEYBORADSHORTCUT"
        
        def runKeyboardShortcut(self, alt, ctrl, shift, key):
            print "on key:", alt, ctrl, shift, key
            return False
        
    dlg = D(u"abcdefg", (200, 400), pos=(200,400))
    #edit1 = wnd.Edit("def", size=(100, 20), pos=(10, 10), parent=dlg)
    #sc1 = wnd.VertScrollBar(size=(100, 100), pos=(10, 10), parent=dlg)
#    sc1 = wnd.HorzScrollBar(size=(100, 100), pos=(10, 10), parent=dlg)

    listbox = wnd.ListBox(size=(100, 100), pos=(10, 10), parent=dlg, 
        inititems=(u'111111', u'222222222222', u'333333333333'),
        initidx=1, autocreate=True)
        
#    edit2 = wnd.Edit(u"def", size=(100, 20), pos=(10, 10), parent=dlg)
    

    radiobutton = wnd.AutoRadioButton(title=u'autoradiobutton', size=(100, 100), pos=(10, 110), parent=dlg, 
         checked=True, autocreate=True)
         
    btn1 = wnd.OkButton(size=(60, 20), pos=(10, 360), parent=dlg, title=u"1")
    btn2 = wnd.Button(size=(60, 20), pos=(70, 360), parent=dlg, title=u"2")

    def clicked(msg):
        print "clicked"

        font = dlg.getFont()
        for c in dlg._childWnds:
            c.setFont(font)
#            print font.hFont
#        edit2.setText("abcdefg")
#        dlg.endDialog(0)
#        print `edit2.getText()`
        
        print "getItemFromPos():", listbox.getItemFromPos((0,0))
        print "getItemRect():", listbox.getItemRect(0)
        
    def clicked2(msg):
        btn1.enableWindow(False)
        
    btn1.msgproc.CLICKED=clicked
    btn2.msgproc.CLICKED=clicked2
    
    v = [0]
    def f():
        print "idle", time.clock(), v[0]
        v[0] += 1
        if v[0] % 100 == 0:
            return 1
        return 1
#    idle = wnd.IdleProc(f) 
    dlg.doModal()

del dlg