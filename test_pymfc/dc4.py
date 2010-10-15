# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd, pymfc.gdi
def onPaint(msg):
    dc = pymfc.gdi.PaintDC(msg.wnd)
    try:
        rc = msg.wnd.getClientRect()
        dc.fillSolidRect(rc, 0xffffff)
        dc.selectObject(pymfc.gdi.StockFont(default_gui=True))
        dc.polyBezier([
            (0,0), 
            (5, 2), (15, 8), (20, 20), 
            (50, 20), (50, 20), (100, 20), 
            (100, 0), (100, 0), (100, 0), 
            ] )
    finally:
        dc.endPaint()
        
for i in range(100):
    w = pymfc.wnd.FrameWnd()
    w.msgproc.PAINT=onPaint

    w.create()

pymfc.app.run()

