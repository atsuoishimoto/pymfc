# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi


def run():
    f = wnd.FrameWnd()
    f.DEFAULT_WNDCLASS = wnd.WndClassStyle(hredraw=True, vredraw=True).register()

    f.create()
    
    brush = gdi.Brush(color=0xff0000)
    brush2 = gdi.HatchBrush(color=0x00ff00, bdiagonal=True)
    rgn1 = gdi.EllipticRgn((350, -350, 600, -600))

    rgn2 = gdi.RectRgn((50, -50, 300, -300))
    n = 10
    rgn3 = gdi.RectRgn((50+n, -50-n, 300-n, -300+n))
    
    rgn4 = rgn3.combine(rgn2, xor=True)
    
    
    bk = gdi.Brush(color=0xcc6633)
    
    def ontimer(msg):
        f.invalidateRect(None, False)
        
    def drawBorder(dc):
#        rgn4.fill(dc, brush)
        rgn4.invert(dc)
        
        
    def erase(msg):
        dc = gdi.DC(hdc=msg.hdc)
        rc = dc.getClipBox()
        dc.fillSolidRect(rc, 0xcc6633)
        dc.setMapMode(lometric=True)
        brush = gdi.Brush(color=0xff0000)
#        dc.selectObject(brush)
        rgn1.paint(dc)
        
        drawBorder(dc)
        return 1

    def paint(msg):
        dc = gdi.PaintDC(msg.wnd)
        dc.setMapMode(lometric=True)
        import time
        f = time.clock()
        for i in range(1):
            drawBorder(dc)
            rgn4.offset((1, -1))
            drawBorder(dc)
        dc.endPaint()
        
#        dc.patBlt(dc.dpToLp(wndrc), copy=True)
        
#        dc.patBlt([0,0,200,200], invert=True)


#        dc.setMapMode(lometric=True)
##        rgn1.fill(dc, brush)
#        dc.selectObject(brush)
#        rgn2.frame(dc, brush2, 10, 10)
#        rgn2.invert(dc)
        
#        for i in range(5):
#            dc.setMapMode(lometric=True)
#            
#            paintdc = dc.createCompatibleDC()
#            paintdc.setMapMode(lometric=True)
#
#            wndrc = msg.wnd.getClientRect()
#
#            bmp = dc.createCompatibleBitmap(wndrc[2] - wndrc[0], wndrc[3] - wndrc[1])
#            orgbmp = paintdc.selectObject(bmp)
#
#            paintdc.fillSolidRect(paintdc.dpToLp(wndrc), 0x00ff00)
#            paintdc.selectObject(brush)
#            
#            rgn1.paint(paintdc)
#            rgn1.offset((1,-1))
#
#            rgn2.fill(paintdc, brush2)
#            rgn3.fill(paintdc, brush2)
#
#            paintdc.setMapMode(text=True)
#            dc.bitBlt(wndrc, paintdc, (0,0), srccopy=True)
        

    f.nnn = 0
    f.msgproc.ERASEBKGND = erase
    f.msgproc.PAINT = paint
    f.setTimer(999, 20)
    f.msgproc.TIMER = ontimer
    f.invalidateRect(None, True)
    app.run()

if __name__ == '__main__':
    run()

