import pymfc
from pymfc import app, wnd
import time


nnn = 0

def run():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xc0c0c0
    f.create()
    
    
    def ontimer():
        global nnn 
        nnn += 1
        print "++++++++++++++++++++++++++++++", time.clock(), nnn
        if nnn == 20:
            timer2.unRegister()

    def ontimer2():
        print "222222222222222222222222222", time.clock()

    timer = wnd.TimerProc(100, ontimer, f)
    timer2 = wnd.TimerProc(200, ontimer2, f)


    f.invalidateRect(None, True)
    app.run()

if __name__ == '__main__':
    run()

