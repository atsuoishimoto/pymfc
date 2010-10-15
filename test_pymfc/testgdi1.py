# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi
import time

def p(msg):
    t = int(time.time()) % 50
    c = int(time.time()*1000) % 256
    color = (c << 16) & 0xff0000 | (c << 8) & 0xff00 | c & 0xff
    color=0x000000
    dc = gdi.PaintDC(msg.wnd)
    try:
        dc.fillSolidRect(msg.wnd.getClientRect(), 0xffffff)
        pen = gdi.Pen(color=color, width=2, solid=1)
#        pen = gdi.Pen(geometric=1, color=color, width=1, dot=1)
        print pen.getLogPen()
        orgpen = dc.selectObject(pen)
        dc.rectangle((100,100,200,200))
    finally:
        dc.endPaint()

def run():
    def c():
        f = wnd.FrameWnd(u"title1")
        f.create()
        f.msgproc.PAINT = p

        def t(msg):
            msg.wnd.invalidateRect(None, erase=False)
        f.msgproc.TIMER = t
        

    for i in range(1):
        c()
    app.run()

if __name__ == '__main__':
    run()
