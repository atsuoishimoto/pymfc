# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu

def createBar(msg):
    sb = wnd.StatusBar(parent=msg.wnd, indicators=(5,5,10,15))
    sb.create()
    sb.setPaneText(0, u'abc')
    sb.setPaneText(1, u'def')
    sb.setPaneText(2, u'ghi')
    sb.setPaneText(3, u'jkl')

def run():
    def c():
        f = wnd.FrameWnd(u"title1")
        f.msglistener.CREATE = createBar

        def buildMenuBar():
            mmap = menu.MenuMap(100, 1000)
            menubar = menu.MenuBar(u"menubar", mmap)
            popup = menu.PopupMenu(u"popup1", u"popup1-str")
            menubar.append(popup)
            menubar.create()
            return menubar

        f.setMenu(buildMenuBar())
        f.create()
        

    for i in range(100):
        c()
    app.run()

if __name__ == '__main__':
    run()
