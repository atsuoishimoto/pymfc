# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi, util

class Button:
    def __init__(self, pos, size):
        self._pos = pos
        self._size = size
        self._selected = False
        
    def getTextFont(self):
        font = gdi.Font(face=u"Courier New", point=9, weight=800)
        return font
        
    def draw(self, dc):
        l, t, r, b = self.getRect()
        dc.fillSolidRect((l, t, r, b), 0xbaaaa1)

        if not self._selected:
            dc.drawEdge(rc=(l+1, t, r, b), raisedouter=True, left=True, top=True, right=True, bottom=True)
        else:
            dc.drawEdge(rc=(l, t, r, b), bump=True, left=True, top=True, right=True, bottom=True)
        
        font = gdi.Font(face=u"Verdana", point=8)
        org = dc.selectObject(font)
        dc.textOut(u"Button1", (self._pos[0]+18, self._pos[1]+4))
        dc.selectObject(org)

    def getRect(self):
        return (self._pos[0], self._pos[1], self._pos[0]+self._size[0], self._pos[1]+self._size[1])

class w(wnd.Wnd):
    def _prepare(self, kwargs):
        super(w, self)._prepare(kwargs)
        self.msgproc.PAINT = self._onPaint
        self.msglistener.LBUTTONDOWN = self._onLBtnDown

        self.button1 = Button((10,10), (90, 20))
        self.button2 = Button((10, 30), (90, 20))
        
    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            wndrc = msg.wnd.getClientRect()
            dc.fillSolidRect(wndrc, 0xc0c0c0)
            dc.fillSolidRect(wndrc, 0xb4aaa1)
            dc.fillSolidRect(wndrc, 0xbbc2bb)
            
            self.button1.draw(dc)
            self.button2.draw(dc)
        finally:
            dc.endPaint()
    
    def _onLBtnDown(self, msg):
        if util.ptInRect((msg.x, msg.y), self.button1.getRect()):
            self.button1._selected = not self.button1._selected
            if self.button1._selected:
                self.button2._selected = False
        elif util.ptInRect((msg.x, msg.y), self.button2.getRect()):
            self.button2._selected = not self.button2._selected
            if self.button2._selected:
                self.button1._selected = False
        self.invalidateRect(None)

def run():
    for i in range(10):
        f = wnd.FrameWnd()
        c = w(parent=f, anchor=wnd.Anchor(occupy=True))
        f.create()
        c.create()
    
    app.run()

if __name__ == '__main__':
    run()

