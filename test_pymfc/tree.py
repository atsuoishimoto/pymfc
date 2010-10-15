# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd


def onCreate(msg):
    image = wnd.ImageList()
    image.create(cx=16, cy=16, initial=1, grow=1, color=8, mask=1)
    icon = wnd.Icon(filename=u"c:\\aaa.ico")
    image.addIcon(icon)
    msg.wnd.setImageList(normal=image)

    item = wnd.TreeItem()
    item.text = u"あいうえお"
    msg.wnd.insert(item)

    item = wnd.TreeItem()
    item.text = u"abcdeg1"
    msg.wnd.insert(item)


def test():
    dlg = wnd.Dialog(u"abcdefg", (200, 300), pos=(100,100))
    tree = wnd.TreeView(size=(100, 200), pos=(10, 10), parent=dlg)
    tree.msglistener.CREATE=onCreate
    dlg.doModal()


for i in  range(1):
    print i
    test()
