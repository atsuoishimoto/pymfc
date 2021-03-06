# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import app, wnd, traynotify, gdi, menu



class Notify(traynotify.TrayNotify):
    def onRBtnUp(self, msg):
        popup = menu.PopupMenu(u"popup")
        popup.append(menu.MenuItem(u"item1", u"item1"))
        popup.append(menu.MenuItem(u"item2", u"item2"))
        popup.append(menu.MenuItem(u"item3", u"item3"))
        popup.create()
        msg.wnd.setForegroundWindow()
        pos = msg.wnd.getCursorPos()
        pos =msg.wnd.clientToScreen(pos)
        item = popup.trackPopup(pos, msg.wnd, nonotify=True, returncmd=True)
        print item


class Frame(wnd.FrameWnd):
    STYLE=wnd.FrameWnd.STYLE(visible=False)
    
    def _prepare(self, kwargs):
        super(Frame, self)._prepare(kwargs)
        self.icon1 = gdi.Icon(filename=u".\\test_pymfc\\pc.ico", cx=16, cy=16)
        self.notify = Notify(self, self.icon1, u"abcdefg")


    
import time

def run():
    def ontimer():
        f.notify.setIcon(tip=unicode(time.clock()))
        
    f = Frame()
    f.create()
    timer = wnd.TimerProc(1000, ontimer, f)

    app.run()

if __name__ == '__main__':
    run()

