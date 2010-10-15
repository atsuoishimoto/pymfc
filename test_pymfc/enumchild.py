# -*- coding: ShiftJIS -*-

from pymfc import app, wnd, gdi, hyperlabel

for i in range(100):
    w = wnd.FrameWnd()
    w.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    w.WNDCLASS_CURSOR = gdi.Cursor(arrow=True)
    w.create()

    wnd.Edit(parent=w, size=(100,100)).create()
    wnd.Edit(parent=w, size=(100,100)).create()
    wnd.Edit(parent=w, size=(100,100)).create()
    wnd.Edit(parent=w, size=(100,100)).create()

    for hwnd in w.enumChildWindows():
        print hwnd


app.run()



