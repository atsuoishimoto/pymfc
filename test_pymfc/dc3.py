# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd, pymfc.gdi
def onPaint(msg):
    dc = pymfc.gdi.PaintDC(msg.wnd)
    try:
        rc = msg.wnd.getClientRect()
        dc.fillSolidRect(rc, 0xffffff)
        dc.selectObject(pymfc.gdi.StockFont(default_gui=True))
        dc.drawText(u"abc\ndef\n", (0,0,100,100),
            singleline=False, noprefix=True, wordbreak=True, editcontrol=True)
        
        print dc.getTextExtentEx(u"abcdefg", 1)

    finally:
        dc.endPaint()
        
for i in range(10):
    w = pymfc.wnd.FrameWnd()
    w.msgproc.PAINT=onPaint

    w.create()

pymfc.app.run()
