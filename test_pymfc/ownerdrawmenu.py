# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu, gdi, ownerdrawbutton

def measureitem(item, msg):
    msg.itemsize = (200, 300)
    return True
    
def drawitem(item, msg):
    dc = gdi.DC(msg.hdc)
    dc.fillSolidRect(msg.rcitem, 0x409090)
    dc.drawText(u"abcdefg", msg.rcitem)
    

def lbtn(msg):
    popup = menu.PopupMenu(u"popup")
    popup.append(menu.MenuItem(u"item1", u"item1", sizeMenu=measureitem, drawMenu=drawitem))
    popup.append(menu.MenuItem(u"item2", u"item2"))
    popup.append(menu.MenuItem(u"item3", u"item3"))
    popup.create()

    pos = msg.wnd.clientToScreen((msg.x, msg.y))
    item = popup.trackPopup(pos, msg.wnd, nonotify=True, returncmd=True)

    
def run():
    def c():
        f = wnd.FrameWnd(u"title1")
        f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
        f.create()
        f.msglistener.LBUTTONDOWN = lbtn
        btn = ownerdrawbutton.OwnerDrawButton(parent=f, pos=(0,0), size=(100,100), title=u";sld,fa;s,f;s,d")
        btn.create()
        
        lst = ownerdrawbutton.OwnerDrawDropDownList(parent=f, pos=(0,110), size=(100,100), inititems=[u'0', u'1', u'2', u'3', u'4', ])
        lst.create()
        
    for i in range(1):
        c()
    app.run()

if __name__ == '__main__':
    run()
