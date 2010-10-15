from pymfc import wnd, app, gdi
f = wnd.FrameWnd()
f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
f.create()

e1 = wnd.Button(parent=f, pos=(0,0), size=(50, 30))
e1.create()

e2 = wnd.Button(parent=f, size=(50, 10), anchor=wnd.Anchor(left=10, top=10, height=100, width=100))
e2.create()


def ff1(msg):
    e1.setFocus()
    
f.msglistener.LBUTTONDOWN = ff1

def f1(msg):
    print "e1.click"

def f2(msg):
    print "e2.click"

    
e1.msglistener.CLICKED=f1
e2.msglistener.CLICKED=f2

f.setFocus()
from pymfc import app
app.run()
