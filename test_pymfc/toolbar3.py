# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc.wnd import *
from pymfc.gdi import *
from pymfc.menu import *


for i in range(10):
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
    tb.setButtons([100, 101, 102, 103])
    index = tb.getButtonIndex(100)

    imglist = ImageList()
    imglist.create(cx=16, cy=15, initial=1, grow=1, color=8, mask=1)
    bmp1 = Bitmap(filename=ur".\test_pymfc\tb_paste.bmp", loadmap3dcolors=1)
    imglist.addBitmap(bmp1, maskrgb=0xc0c0c0)

    tb.setImageList(imglist)
    tb.setButtonStyle(0, disabled=True)
    tb.setButtonStyle(1, disabled=True)
    print hex(tb.getButtonStyle(0))
    
    tb.enableDocking()
    f.dockControlBar(tb, top=1)

pymfc.app.run()
