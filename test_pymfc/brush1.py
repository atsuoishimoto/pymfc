# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import sys
#sys.path.append("c:\\src\\infopile-cabinet\\src\\pymfc-vc9")
from pymfc import wnd, app, gdi


def run():
    for i in range(1):
        wnd.getStartupInfo()
        f = wnd.FrameWnd()

        def oncreate(msg):
            f.icon1 = gdi.Icon(filename=u".\\pymfc\\test_pymfc\\pc.ico", cx=32, cy=32)
            f.icon2 = gdi.Icon(filename=u".\\pymfc\\test_pymfc\\pc.ico", cx=16, cy=16)
            
            f.setIcon(f.icon1, f.icon2)
            
        def ontimer(msg):
            f.invalidateRect(None, False)
            
        def erase(msg):
            dc = gdi.DC(hdc=msg.hdc)
            rc = msg.wnd.getClientRect()
            dc.fillSolidRect(rc, 0xcc6633)
            return 1

        def paint(msg):
            dc = gdi.PaintDC(msg.wnd)
            dc.setMapMode(lometric=True)

            pattern = '\xcc\x00'*8
            bmp = gdi.Bitmap(cx=8, cy=8, panes=1, bitsperpel=1, bits=pattern)
            brush = gdi.PatternBrush(bmp)
            dc.selectObject(brush)

            wndrc = msg.wnd.getClientRect()
            dc.patBlt(dc.dpToLp(wndrc), invert=True)

            dc.endPaint()
            
            
        f.msglistener.CREATE = oncreate
        f.msgproc.ERASEBKGND = erase
        f.msgproc.PAINT = paint

        f.create()
        f.setTimer(999, 500)
        f.msgproc.TIMER = ontimer
        f.invalidateRect(None, True)


    app.run()



if __name__ == '__main__':
    run()
