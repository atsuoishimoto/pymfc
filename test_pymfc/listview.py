# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys, time
from pymfc import wnd



def onCreate(msg):
    
    image = wnd.ImageList()
    image.create(cx=32, cy=32, initial=1, grow=1, color=8, mask=1)
    icon = wnd.Icon(filename=u"c:\\aaa.ico")
    image.addIcon(icon)

    msg.wnd.setImageList(normal=image, small=image)
    
    col = wnd.ListColumn()
    col.text = u"ABCDEFG"
    col.cx = 150
    msg.wnd.insertColumn(0, col)
    
    col.text = u"11111"
    col.cx = 50
    col.right = 1
    msg.wnd.insertColumn(1, col)
    
    f = time.clock()

    item = wnd.ListItem()

    for i in range(1):
        item.item = i*2
        item.text = u"abcdxxeg"+`i`
        item.selected = True
        item.focused = True
        msg.wnd.insert(item)
        msg.wnd.setItemText(i*2, 1, u"222222"+`i`)

        item.item = i*2+1
        item.text = u"33333"+`i`
        msg.wnd.insert(item)

        msg.wnd.setItemText(i*2+1, 1, u"444444"+`i`)

    item = wnd.ListItem(item=1, subitem=1)
    print msg.wnd.getItemText(1)
    print msg.wnd.getItemCount()
#    print item.text
#    assert msg.wnd.getItemCount() == 2000
    print "===", time.clock() - f


    

def test():
    dlg = wnd.Dialog(u"abcdefg", (600, 300), pos=(100,100))
    listview = wnd.ListView(size=(400, 200), pos=(10, 10), parent=dlg,
        style=wnd.ListView.STYLE(report=True, editlabels=True))
    listview.msglistener.CREATE=onCreate

    def fff(key):
        listview.editLabel(0)
    listview.keymap.addKey(fff, [(0,0,0,wnd.KEY.F12)])
    dlg.doModal()


for i in  range(1):
    test()
