# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi, drawpanel
from pymfc.drawpanel.tools import SelectTool, NewShapeTool

def run():
    f = wnd.FrameWnd()
    f.create()
    
    child = drawpanel.DrawPanel(parent=f)


    def onKey(msg):
        if isinstance(child._tool, SelectTool):
            child._tool = NewShapeTool(child)
        else:
            child._tool = SelectTool(child)
    
    child.keymap.addKey(onKey, [(0,0,0,wnd.KEY.F12)])

    child.create()

    f.msglistener.SIZE = lambda msg:child.setWindowPos(size=(msg.width, msg.height))
    s = f.getClientRect()
    child.setWindowPos(size=(s[2]-s[0], s[3]-s[1]))
    child.setFocus()
    f.msgproc.ACTIVATE = lambda msg:child.setFocus()

    app.run()



if __name__ == '__main__':
    run()

