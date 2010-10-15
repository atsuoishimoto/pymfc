# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi, wndpanel
f = wnd.FrameWnd()
f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0

def onok():
    print "ok"
wnd.DialogKeyHandler(f, onok=onok)

f.create()

l = wnd.Static(parent=f, title=u"abc&defg", pos=(0,0), size=(100, 25))
l.create()

e = wnd.Edit(parent=f, pos=(0,30), size=(10, 20), anchor=wnd.Anchor(right=-10), style=wnd.Edit.STYLE(wantreturn=True))
e.create()

def a_r(w):
    l, t, r, b = w._parent.getClientRect()
    return r - 10
e = wnd.Edit(parent=f, pos=(0,70), size=(10, 20), anchor=wnd.Anchor(right=a_r))
e.create()

e = wnd.Edit(parent=f, pos=(0,120), size=(100, 20), anchor=wnd.Anchor(left=10))
e.create()

def a_l(w):
    l, t, r, b = w._parent.getClientRect()
    return l + 10
e = wnd.Edit(parent=f, pos=(0,170), size=(100, 20), anchor=wnd.Anchor(left=a_l))
e.create()

e = wnd.Edit(parent=f, anchor=wnd.Anchor(top=220, left=20, width=100, height=100), title=u"bbb")
e.create()

e = wnd.OkButton(parent=f, pos=(0,370), size=(100, 20), anchor=wnd.Anchor(top=370, bottom=-100), title=u"aaa")
e.create()





from pymfc import app
app.run()
