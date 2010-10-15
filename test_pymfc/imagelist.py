# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import sys
#sys.path.append("c:\\src\\infopile-cabinet\\src\\pymfc-vc9")

import gc, sys, time
from pymfc import wnd, gdi

import pymfc.wnd, pymfc.gdi
def onPaint(msg):
    image = wnd.ImageList()
    image.create(cx=16, cy=16, initial=1, grow=1, color=8, mask=1)

    link = gdi.Icon(filename=u".\\test_pymfc\\link.ico", cx=16, cy=16)
    idx_link = image.addIcon(link)
    image.setOverlayImage(idx_link, 1)
    
    icon = gdi.Icon(filename=u".\\test_pymfc\\pc.ico", cx=16, cy=16)
    idx = image.addIcon(icon)
    
    icon2 = image.getIcon(idx, overlay=1)
    
    dc = pymfc.gdi.PaintDC(msg.wnd)
    try:
        rc = msg.wnd.getClientRect()
        dc.fillSolidRect(rc, 0x00ff00)
#        image.draw(idx, dc, (0,0), overlay=1)
        dc.drawIcon((0,0), icon2, size=(16, 16), normal=True)
        dc.drawState((0,20), size=(16, 16), image=icon2, disabled=True)
    finally:
        dc.endPaint()
        
for i in range(10):
    w = pymfc.wnd.FrameWnd()
    w.msgproc.PAINT=onPaint

    w.create()

pymfc.app.run()
