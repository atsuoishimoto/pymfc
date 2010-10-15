from pymfc import wnd, app, gdi, menu


def onlll(msg):
        popup = menu.PopupMenu(u"popup")
        popup.append(menu.MenuItem(u"item1", u"item1"))
        popup.append(menu.MenuItem(u"item2", u"item2"))
        popup.append(menu.MenuItem(u"item3", u"item3"))
        popup.create()

        pos =msg.wnd.clientToScreen((msg.x, msg.y))
        item = popup.trackPopup(pos, msg.wnd, nonotify=True, returncmd=True)
    

    
def run():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = color=0xffffff
    f.msglistener.LBUTTONDOWN = onlll
    f.create()
    app.run()

if __name__ == '__main__':
    run()

