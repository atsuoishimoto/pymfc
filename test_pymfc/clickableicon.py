# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi, clickableicon 
import traceback

class Frame(wnd.FrameWnd):
    def _prepare(self, kwargs):
        super(Frame, self)._prepare(kwargs)

        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msglistener.LBUTTONDOWN = self._onLBtnDown

        def f():
            print "clicked"
        icon = gdi.Icon(filename=u".\\test_pymfc\\pc.ico")
        self._btn = clickableicon.ClickableIcon(parent=self, icon=icon, iconsize=16, 
            title=u"abcdefg", bgcolor=0xff0080, onclick=f)
        size = self._btn.calcSize(gdi.DesktopDC())
        self._btn.setRect((10, 10, 10+size[0], 10+size[1]))
        
        def f2():
            print "clicked2"
        self._btn2 = clickableicon.ClickableIconButton(parent=self, icon=icon, iconsize=16, 
            title=u"abcdefg", bgcolor=0xff0080, onclick=f2)
        size = self._btn2.calcSize()
        
        def f3():
            print "clicked3"
            
        def f4():
            self._btn3.dropDown(not self._btn3.isDropDown())
        self._btn3 = clickableicon.ClickableIconButton(parent=self, icon=icon, iconsize=16, 
            title=u"abcdefg", bgcolor=0xc0c0c0, dropdown=True, onclick=f2, ondropdown=f4)
        size = self._btn3.calcSize()
        print size

    def wndReleased(self):
        super(Frame, self).wndReleased()
        self._btn = None
        self._btn2 = None
        self._btn3 = None

    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            rc = self.getClientRect()
            dc.fillSolidRect(rc, 0xffffff)
            self._btn.draw(dc)
        finally:
            dc.endPaint()

    def _onSetCursor(self, msg):
        if self._btn.onSetCursor(msg):
            return
        cursor = gdi.Cursor(arrow=True)
        cursor.setCursor()

    def _onLBtnDown(self, msg):
        if self._btn.onLBtnDown(msg):
            return

def run():
    f = Frame()
    f.create()

    f._btn2.create()
    size = f._btn2.calcSize()
    f._btn2.setWindowPos(pos=(100,100), size=size)

    f._btn3.create()
    size = f._btn3.calcSize()
    f._btn3.setWindowPos(pos=(200,200), size=size)
    app.run()


if __name__ == '__main__':
    run()



