# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu, gdi

    
def run():
    def ff(msg):
        print "KNLKMJNKJNKJNKJNKJNKJ"

    def c():
        f = wnd.FrameWnd(u"title1")
        f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
        f.create()
        
        tooltip = wnd.ToolTip(parent=f)
        tooltip.create()
        tooltip.addTool(9999, f, (0,0,100,100), u"abcdefg", subclass=True)
        tooltip.activate(True)

        f.msglistener.LBUTTONDOWN = ff

    for i in range(1):
        c()
    app.run()

if __name__ == '__main__':
    run()

