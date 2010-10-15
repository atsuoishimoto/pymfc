# -*- coding: ShiftJIS -*-

from pymfc import app, wnd, gdi, hyperlabel

w = wnd.FrameWnd()
w.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
w.WNDCLASS_CURSOR = gdi.Cursor(arrow=True)
w.create()

style = hyperlabel.HyperLabel.STYLE(border=True)
style = hyperlabel.HyperLabel.STYLE()
label = hyperlabel.HyperLabel(parent=w, pos=(0,0), size=(120,100),  style=style)

label.WNDCLASS_CURSOR = gdi.Cursor(arrow=True)
label.create()
icon1 = gdi.Icon(filename=u".\\test_pymfc\\pc.ico", cx=16, cy=16)
icon2 = gdi.Icon(filename=u".\\test_pymfc\\link.ico", cx=16, cy=16)


def f(item):
    print item._text
    
label.setItems([
    hyperlabel.LinkItem(u"あいうえお", icon1, clicked=f),
    hyperlabel.LinkItem(u"1abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"2abcdefgabc2abcdefgabc2abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"3abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"4abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"5abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"6abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"7abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"8abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"9abcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Aabcdefgabcあ", icon1, clicked=f),
    hyperlabel.LinkItem(u"Babcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Cabcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Dabcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Eabcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Fabcdefgabc", icon1, clicked=f),
    hyperlabel.LinkItem(u"Gabcdefgabc", icon1, clicked=f),
])
label.layout()

app.run()



