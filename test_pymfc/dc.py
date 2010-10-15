# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd, pymfc.gdi
def onPaint(msg):
    dc = pymfc.gdi.PaintDC(msg.wnd)
    try:
        rc = msg.wnd.getClientRect()
        dc.fillSolidRect(rc, 0x00ff00)
        
        comp = dc.createCompatibleDC()
    finally:
        dc.endPaint()
        
w = pymfc.wnd.FrameWnd()
w.msgproc.PAINT=onPaint

w.create()

pymfc.app.run()
