# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu

def run():
    def c():
        f = wnd.MDIFrame(u"title1")
        

        
        def buildMenuBar(t):
            mmap = menu.MenuMap(100, 1000)
            menubar = menu.MenuBar(t+"menubar")
            
            def frame(n):
                print t, n
            
            popup = menu.PopupMenu(t+u":popup1", t+u"/popup1-str")
            item1 = menu.MenuItem(t+u"item1", t+u"item1_caption", desc=t+u"item1_desc", command=lambda e:frame(1))
            item2 = menu.MenuItem(t+u"item2", t+u"item2_caption", desc=t+u"item2_desc", command=lambda e:frame(2))
            popup.append(item1)
            popup.append(item2)
            menubar.append(popup)

            popup = menu.PopupMenu(t+u":popup2", t+u"/popup2-str")
            item1 = menu.MenuItem(t+u"item3", t+u"item3_caption", desc=t+u"item3_desc", command=lambda e:frame(3))
            item2 = menu.MenuItem(t+u"item4", t+u"item4_caption", desc=t+u"item4_desc", command=lambda e:frame(4))
            popup.append(item1)
            popup.append(item2)
            menubar.append(popup)


            menubar.create(mmap)

            return menubar


        def buildMenuBar2(t):
            mmap = menu.MenuMap(100, 1000)
            menubar = menu.MenuBar(t+"menubar")
            
            def frame(n):
                print t, n
            
            popup = menu.PopupMenu(t+u":popup1", t+u"/popup1-str")
            item1 = menu.MenuItem(t+u"item1", t+u"item1_caption", desc=t+u"item1_desc", command=lambda e:frame(1))
            item2 = menu.MenuItem(t+u"item2", t+u"item2_caption", desc=t+u"item2_desc", command=lambda e:frame(2))
            popup.append(item1)
            popup.append(item2)
            menubar.append(popup)

            popup = menu.PopupMenu(t+u":popup2", t+u"/popup2-str")
            item1 = menu.MenuItem(t+u"item3", t+u"item3_caption", desc=t+u"item3_desc", command=lambda e:frame(3))
            item2 = menu.MenuItem(t+u"item4", t+u"item4_caption", desc=t+u"item4_desc", command=lambda e:frame(4))
            popup.append(item1)
            popup.append(item2)
            menubar.append(popup)

            popup = menu.PopupMenu(t+u":popup3", t+u"/popup3-str")
            item1 = menu.MenuItem(t+u"item5", t+u"item3_caption", desc=t+u"item3_desc", command=lambda e:frame(3))
            popup.append(item1)
            menubar.append(popup)


            menubar.create(mmap)

            return menubar


        def buildChild(p, n):
            c = wnd.MDIChild(u"child"+n, parent=p, menu=buildMenuBar2(u"child"+n+u"///"))
            c.xxxx = u"child"+n
            c.create()
            
            return c
        
        
        f.setMenu(buildMenuBar(u"frame"))
        f.create()
        buildChild(f, u"1")
        buildChild(f, u"2")

    c()
    app.run()

if __name__ == '__main__':
    run()
