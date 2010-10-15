# -*- coding: ShiftJIS
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd

def onCreate(msg):
    item = wnd.TreeItem()
    item.text = u"abcdeg"
    msg.wnd.insert(item)
    item.text = u"あいうえお"
    msg.wnd.insert(item)
    item.text = u"3222222"
    msg.wnd.insert(item)
    item.text = u"422222"
    msg.wnd.insert(item)

def onDelete(msg):
    item = tree.getCaretItem()
    tree.deleteItem(item)

def onDeleteItem(msg):
    print msg

def test():
    dlg = wnd.Dialog(u"abcdefg", size=(500, 300), pos=(100,100))
    global tree
    tree = wnd.TreeView(size=(100, 200), pos=(10, 10), parent=dlg)
    tree.msglistener.CREATE=onCreate
    tree.msgproc.DELETEITEM = onDeleteItem
    
    print "@@@@@@@@@@@@@@@@@@@@@@@@@"
    print tree.MSGDEF["DELETEITEM"]
    print "::::::::::::::::::::::::"
    btn1 = wnd.Button(u"delete", size=(40, 20), pos=(120, 10), parent=dlg)
    btn1.msglistener.CLICKED=onDelete


    dlg.doModal()


for i in  range(1):
    test()
    