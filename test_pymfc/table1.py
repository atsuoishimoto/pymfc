# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import app, wnd, table

class tablewnd(table.Table, wnd.Wnd):
    pass
    
def test():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    tbl = table.Table(f)
    
    f.create()
    
#    c = table.TableWnd(parent=f)
#    
#    c.WNDCLASS_BACKGROUNDCOLOR=0xffffff
#    def cccc(msg):
#        c.create()
#        c.setFocus()
#
#    f.msglistener.CREATE=cccc
#    f.msglistener.SIZE=lambda msg:c.setWindowPos(size=(msg.width, msg.height))
#
#    f.create()
#    
    def fx(msg):
        if msg.control:
            tbl.addHorzBorder((msg.x, msg.y))
        else:
            tbl.addVertBorder((msg.x, msg.y))
        msg.wnd.invalidateRect(None)

    f.msgproc.RBUTTONDOWN = fx


    def s1(msg):
        pos = f.getCursorPos()
        tbl.beginSplit(pos, horz=True)
    
    def s2(msg):
        pos = f.getCursorPos()
        tbl.beginSplit(pos, horz=False)

    f.keymap.addKey(s1, [(0,0,0,wnd.KEY.F12)])
    f.keymap.addKey(s2, [(0,1,0,wnd.KEY.F12)])
    

    tbl.addHorzBorder((100,100))
    tbl.addHorzBorder((100,200))
    tbl.addHorzBorder((100,300))
    
    tbl.addVertBorder((100,0))
    tbl.addVertBorder((200,100))
    tbl.addVertBorder((300,150))
    tbl.addVertBorder((400,100))
    
    tbl.addHorzBorder((100,150))
    tbl.addHorzBorder((100,250))
    tbl.addHorzBorder((350,150))
    
    tbl.addVertBorder((350,100))
    
    def ff2(table):
        print "-----------------------", table
    tbl.msglistener.CELLDRAGGED = ff2
    
##    for cell in c._cells:
##        print cell.getRect()
    app.run()


test()
