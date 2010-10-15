# -*- coding: ShiftJIS -*-
import random
from pymfc import wnd, gdi, app

class TestFrame(wnd.FrameWnd):
    WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    WNDCLASS_CURSOR = gdi.Cursor(arrow=True)

    def _prepare(self, kwargs):
        super(TestFrame, self)._prepare(kwargs)

        def oncreate(msg):
            self.callLater(500, self.runtest)
        self.msglistener.CREATE = oncreate

    def wndReleased(self):
        super(TestFrame, self).wndReleased()
    
    def runtest(self):
        for i in range(100):
            print i
            self.test()

    def test(self):
        ret = wnd.PrintDialog(returndc=True, returndefault=True).doModal()
        w, h = ret.dc.PHYSICALWIDTH, ret.dc.PHYSICALHEIGHT
        rc = (0, 0, int(w*25.4/ret.dc.LOGPIXELSX*100), int(h*25.4/ret.dc.LOGPIXELSY*100))
        dc = gdi.EnhMetaFileDC(ret.dc, None, rc, None)
        dc.fillSolidRect((0, 0, w/2, h/2), random.randint(0, 0xffffff))
        dc.fillSolidRect((w/2, 0, w, h/2), random.randint(0, 0xffffff))
        dc.fillSolidRect((0, h/2, w/2, h), random.randint(0, 0xffffff))
        dc.fillSolidRect((w/2, h/2, w, h), random.randint(0, 0xffffff))
        emf = dc.close()
        
        w, h = emf.rclFrame[2]-emf.rclFrame[0], emf.rclFrame[3]-emf.rclFrame[1]
        p = 0.01 * 96.0 / 25.4
        w, h = int(w*p), int(h*p)

        gdi.ClientDC(self).playEnhMetaFile(emf, (0, 0, w, h))

f = TestFrame()
f.create()
app.run()
