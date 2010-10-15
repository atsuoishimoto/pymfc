# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu, gdi

def f1(msg):
    print msg

def run():
    f = wnd.FrameWnd(u"title1")
    f.DEFAULT_WNDCLASS = wnd.WndClassStyle().register(brush=gdi.Brush(color=0xff0000))
    f.create()

    fonts = []
    def e(tm, lf, isTrueType):
        font = gdi.Font(face=lf.facename, point=10, ansi_charset=True)
        button = wnd.Button(pos=(300*(len(fonts)%2), (len(fonts)/2)*20), size=(300, 20), title=lf.facename+u'【ああああ】', parent=f)
        button.create()
        button.setFont(font)
        fonts.append(font)
        return 1

    gdi.DisplayDC().EnumFontFamilies(e, ansi_charset=True)
    
    print "a======================="

    app.run()

if __name__ == '__main__':
    run()
