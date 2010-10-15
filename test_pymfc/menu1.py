# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import unittest

from pymfc.menu import *


class test_popups(unittest.TestCase):
    def testMenuBar(self):
        mmap = MenuMap(100, 1000)
        menubar = MenuBar(u"menubar", mmap)
        
        def item1_func():
            print "item1_func"

        def item1_update(item, parent):
            print "item1_update"

        def item2_func():
            print "item2_func"

        def item2_update(item, parent):
            print "item2_update"

        item1 = MenuItem(u"item1", u"item1_caption", u"item1_desc", item1_func, item1_update)
        item2 = MenuItem(u"item2", u"item2_caption", u"item2_desc", item2_func, item2_update)
        menubar.append(item1)
        menubar.append(item2)
        
        menubar.create()
        
        hmenu = menubar.getHandle()
        
        self.failUnlessEqual(menubar._getString(0), item1.getCaption())
        self.failUnlessEqual(menubar._getString(1), item2.getCaption())
        self.failUnlessEqual(menubar.size(), 2)
        self.failUnlessEqual(menubar.getIndex(u"item1"), 0)
        self.failUnlessEqual(menubar.getIndex(u"item2"), 1)
        self.failUnless(menubar.getItem(item1.getHandle()) is item1)
        self.failUnless(menubar.getItem(item2.getHandle()) is item2)
        
        self.failUnlessEqual(isMenu(hmenu), True)
        del menubar
        self.failUnlessEqual(isMenu(hmenu), False)
        
    def testPopup(self):
        mmap = MenuMap(100, 1000)
        popup = PopupMenu(u"popup1", u"popup1.caption", mmap)
        
        def item1_func():
            print u"item1_func"

        def item1_update(item, parent):
            print u"item1_update"

        def item2_func():
            print u"item2_func"

        def item2_update(item, parent):
            print u"item2_update"

        item1 = MenuItem(u"item1", u"item1_caption", u"item1_desc", item1_func, item1_update)
        item2 = MenuItem(u"item2", u"item2_caption", u"item2_desc", item2_func, item2_update)
        popup.append(item1)
        popup.append(item2)
        
        popup.create(None)
        
        hmenu = popup.getHandle()
        
        self.failUnlessEqual(popup._getString(0), item1.getCaption())
        self.failUnlessEqual(popup._getString(1), item2.getCaption())
        self.failUnlessEqual(popup.size(), 2)
        self.failUnlessEqual(popup.getIndex(u"item1"), 0)
        self.failUnlessEqual(popup.getIndex(u"item2"), 1)
        self.failUnless(popup.getItem(item1.getHandle()) is item1)
        self.failUnless(popup.getItem(item2.getHandle()) is item2)
        
        self.failUnlessEqual(isMenu(hmenu), True)
        del popup
        self.failUnlessEqual(isMenu(hmenu), False)

    def testSubmenu(self):
        mmap = MenuMap(100, 1000)
        popup = PopupMenu(u"popup1", u"popup1.caption", mmap)
        popup2 = PopupMenu(u"popup2", u"popup2.caption")
        popup.append(popup2)

        popup.create(None)
        popup.onInitMenu(None, None)
        popup.onPopup(None, None)

        hmenu1 = popup.getHandle()
        hmenu2 = popup2.getHandle()

        self.failUnlessEqual(popup.size(), 1)
        self.failUnlessEqual(popup._getString(0), u"popup2.caption")

        self.failUnlessEqual(isMenu(hmenu1), True)
        self.failUnlessEqual(isMenu(hmenu2), True)
        del popup
        self.failUnlessEqual(isMenu(hmenu1), False)
        self.failUnlessEqual(isMenu(hmenu2), False)
        
    def test_dynmenu(self):
        for i in range(100):
            mmap = MenuMap(100, 1000)
            popup = PopupMenu(u"popup1", u"popup1.caption", mmap)
            
            popup.append(MenuItem(u"item1", u"item1_caption", desc=u"item1_desc"))
            popup.append(MenuItem(u"item2", u"item2_caption", desc=u"item2_desc"))
            
            def dyn_func(dynmenu, parent, wnd):
                yield MenuItem(u"dyn1", u"dyn1_caption", desc=u"dyn1_desc")
                yield MenuItem(u"dyn2", u"dyn2_caption", desc=u"dyn2_desc")
                yield MenuItem(u"dyn3", u"dyn3_caption", desc=u"dyn3_desc")
                yield MenuItem(u"dyn4", u"dyn4_caption", desc=u"dyn4_desc")

            dyn = DynMenuItems(u"dyn1", dyn_func)
            popup.append(dyn)

            popup.append(MenuItem(u"item3", u"item3_caption", desc=u"item3_desc"))

            popup.create(None)
            # initialize dynamic menus
            popup.onInitMenu(None, None)
            self.failUnlessEqual(popup.size(), 4)

            # populate dynamic menus
            popup.onPopup(None, None)
            hmenu = popup.getHandle()
            
            self.failUnlessEqual(popup.size(), 7)
            
            self.failUnlessEqual(popup._getString(0), u"item1_caption")
            self.failUnlessEqual(popup._getString(1), u"item2_caption")
            self.failUnlessEqual(popup._getString(2), u"dyn1_caption")
            self.failUnlessEqual(popup._getString(3), u"dyn2_caption")
            self.failUnlessEqual(popup._getString(4), u"dyn3_caption")
            self.failUnlessEqual(popup._getString(5), u"dyn4_caption")
            self.failUnlessEqual(popup._getString(6), u"item3_caption")

            # initialize dynamic menus again
            popup.onInitMenu(None, None)
            self.failUnlessEqual(popup.size(), 4)

            self.failUnlessEqual(popup._getString(0), u"item1_caption")
            self.failUnlessEqual(popup._getString(1), u"item2_caption")
            self.failUnlessEqual(popup._getString(3), u"item3_caption")


            self.failUnlessEqual(isMenu(hmenu), True)
            del popup
            self.failUnlessEqual(isMenu(hmenu), False)


if __name__ == '__main__':
    unittest.main()

