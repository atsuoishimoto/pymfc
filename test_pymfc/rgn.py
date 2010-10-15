# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi

def run():
    f = wnd.FrameWnd()
    f.create()
    
    brush = gdi.Brush(color=0xff0000)
    brush2 = gdi.Brush(color=0x0000ff)
    rgn1 = gdi.EllipticRgn((0, -300, 300, 0))
    rgn2 = gdi.RectRgn((0,-300, 300, 0))
    
    rgn3 = rgn1.combine(rgn2, xor=True)
    rgn3.offset((500, -100))
 
    rgn4 = gdi.RectRgn((900,-300, 902, 0))
    def ontimer(msg):
        f.invalidateRect(None)
        
    def paint(msg):
        dc = gdi.PaintDC(msg.wnd)
        
        for i in range(5):
            paintdc = dc.createCompatibleDC()
            paintdc.setMapMode(lometric=True)

            
            wndrc = msg.wnd.getClientRect()

            bmp = dc.createCompatibleBitmap(wndrc[2] - wndrc[0], wndrc[3] - wndrc[1])
            orgbmp = paintdc.selectObject(bmp)

            paintdc.fillSolidRect(paintdc.dpToLp(wndrc), 0x00ff00)
            paintdc.selectObject(brush)
            
            rgn1.paint(paintdc)
            rgn1.offset((1,-1))

            rgn2.fill(paintdc, brush2)
            rgn3.fill(paintdc, brush2)

            rgn4.fill(paintdc, brush)

            paintdc.setMapMode(text=True)
            dc.bitBlt(wndrc, paintdc, (0,0), srccopy=True)
        
        dc.endPaint()


    f.msgproc.PAINT = paint
    f.setTimer(999, 1)
    f.msgproc.TIMER = ontimer
    app.run()

if __name__ == '__main__':
    run()

