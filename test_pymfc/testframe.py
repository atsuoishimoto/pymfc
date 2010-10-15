# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu, shellapi

def close(msg):
    print "close"
    return msg.wnd.defWndProc(msg)
    
def run():
    def c():
        f = wnd.FrameWnd(u"title1")

        def buildMenuBar():
            mmap = menu.MenuMap(100, 1000)
            menubar = menu.MenuBar(u"menubar", mmap)

            popup = menu.PopupMenu(u"popup1", u"popup1-str")
            item1 = menu.MenuItem(u"item1", u"item1_caption", desc=u"item1_desc")
            item2 = menu.MenuItem(u"item2", u"item2_caption", desc=u"item2_desc")
            popup.append(item1)
            popup.append(item2)
            
            menubar.append(popup)
            menubar.create()
            
            return menubar

        f.setMenu(buildMenuBar())
        f.create()
        
        def onKey(msg):
            print msg.wnd, msg
            print ">>>>>>>>>>>>>>>>>>>>>>", msg.wnd.getWindowPlacement().position
        def onKey2(msg):
            print "KEY2", msg, msg
        
        def onKey3(msg):
            print "KEY3", msg, msg
        
        f.keymap.addKey(onKey, [(0,0,0,'a')])
        f.keymap.addKey(onKey2, [(0,0,0,wnd.KEY.PGDN)])
        f.keymap.addKey(onKey3, [(0,1,0,wnd.KEY.PGDN)])

        f.msgproc.CLOSE = close

    for i in range(10):
        c()
    app.run()

if __name__ == '__main__':
    run()
