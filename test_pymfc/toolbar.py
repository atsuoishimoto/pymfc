# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc.wnd import *
from pymfc.menu import *


for i in range(1):
    mmap = MenuMap(0x8000, 0x9000)
    bar = MenuBar("MENUBAR", mmap)
    popup = PopupMenu(u'MENU1', u"menu1")
    bar.children.append(popup)
    bar.create()

    f = FrameWnd(size=(300, 300), menu=bar)
    f.create()
    f.enableDocking()


    tb = ToolBar(u"abcdefg", parent=f, top=1, right=1)
    tb.create()
    bmp = Bitmap(filename=ur".\test_pymfc\stdbar.bmp", loadmap3dcolors=1)
    tb.setBitmap(bmp)
#
#
    tb.setButtons([100, 101, 102])

    def f100(msg):
        print "f100"
    f.msglistener.setCommand(100, f100)
    
    tb.enableDocking()
    f.dockControlBar(tb, top=1)



pymfc.app.run()
