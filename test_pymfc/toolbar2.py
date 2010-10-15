# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc.wnd import *
from pymfc.gdi import *
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
    tb.setButtons([100, 101, 102, 103])
    index = tb.getButtonIndex(100)

    cmdId, iImage, style = tb.getButtonInfo(index)
    tb.setButtonInfo(index, cmdId, 100, separator=True)
    
    r = tb.getButtonRect(index)
    
    combo = DropDownList(u"", size=(r[2]-r[0], r[3]-r[1]+200), pos=(r[0], r[1]), parent=tb, wndId=100)
    combo.create()
    font = StockFont(default_gui=True)
    combo.setFont(font)
    combo.addItem(text=u"あいうえお")
    combo.addItem(text=u"abcdefg")
    combo.addItem(text=u"abcdefg")
    combo.setCurSel(0)
    
    bmp = Bitmap(filename=ur".\test_pymfc\stdbar.bmp", loadmap3dcolors=1)
    tb.setBitmap(bmp)

    tb.enableDocking()
    f.dockControlBar(tb, top=1)

pymfc.app.run()
