# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu
import thread, threading, time, traceback

def xxx():
    for i in xrange(10000000):
        time.sleep(0.01)
    print "fin"
    
def run():
    def c():
        f = wnd.FrameWnd(u"title1")
        def ff(msg):
            try:
                f.openClipboard()
                f.setClipboardText(u"abcdefg")
                f.closeClipboard()
            except:
                traceback.print_exc()
        f.msglistener.KEYDOWN = ff
        f.create()

#    thread.start_new_thread(xxx, ())
    c()
    app.run()

if __name__ == '__main__':
    run()
