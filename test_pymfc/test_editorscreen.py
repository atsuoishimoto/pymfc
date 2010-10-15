# -*- coding: ShiftJIS -*-

import unittest
from pymfc import gdi
from pymfc.editor import screen, buffer


class test_screen(unittest.TestCase):

    FONT1 = gdi.Font(face=u"MS Gothic", point=10)

    BG = 0xffffff
    BG_SEL = 0xff0000
    FG = 0x000000
    TAB = 0x00ff00
    LF = 0x0000ff
    SPC = 0xc0c0c0

    COLOR1 = screen.StyleColor(
            text = (FG, BG),
            text_sel = (FG, BG_SEL),
            lf = (LF, BG),
            lf_sel = (LF, BG_SEL),
            tab = (TAB, BG),
            tab_sel = (TAB, BG_SEL),
            fullspc = (SPC, BG),
            fullspc_sel = (SPC, BG_SEL))

    STYLE1 = screen.TextStyle(FONT1, FONT1, COLOR1)
    DC = gdi.IC(u"Display", u"")

    def testSingle(self):
        
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=20,
            wordwrap=0, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")

        buf = buffer.Buffer()
        buf.ins(0, u"abcdefg")

        scrn = screen.Screen(self.DC, buf, conf, 100, 100)
        scrn.locate(0)
        
        self.failUnlessEqual(len(scrn), 1)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 7)
        self.failUnlessEqual(row.lineNo, 0)

    def testLf1(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=20,
            wordwrap=0, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")

        buf = buffer.Buffer()
        buf.ins(0, u"abc\ndef")

        scrn = screen.Screen(self.DC, buf, conf, 100, 100)
        scrn.locate(0)
        
        self.failUnlessEqual(len(scrn), 2)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 4)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[1]
        self.failUnlessEqual(row.top, 4)
        self.failUnlessEqual(row.end, 7)
        self.failUnlessEqual(row.lineNo, 1)

    def testLf2(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=20,
            wordwrap=0, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")

        buf = buffer.Buffer()
        buf.ins(0, u"abc\ndef\n")

        scrn = screen.Screen(self.DC, buf, conf, 100, 100)
        scrn.locate(0)
        
        self.failUnlessEqual(len(scrn), 3)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 4)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[1]
        self.failUnlessEqual(row.top, 4)
        self.failUnlessEqual(row.end, 8)
        self.failUnlessEqual(row.lineNo, 1)

        row = scrn[2]
        self.failUnlessEqual(row.top, 8)
        self.failUnlessEqual(row.end, 8)
        self.failUnlessEqual(row.lineNo, 2)

    def testWrap1(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=5,
            wordwrap=0, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")


        buf = buffer.Buffer()
        buf.ins(0, u"012345")

        scrn = screen.Screen(self.DC, buf, conf, 100, 100)
        scrn.locate(0)
        
        self.failUnlessEqual(len(scrn), 2)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 5)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[1]
        self.failUnlessEqual(row.top, 5)
        self.failUnlessEqual(row.end, 6)
        self.failUnlessEqual(row.lineNo, 0)


    def testWrap2(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=0,
            wordwrap=0, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")

        buf = buffer.Buffer()
        buf.ins(0, u"012345")

        scrn = screen.Screen(self.DC, buf, conf, 3, 100)
        scrn.locate(0)
        
        self.failUnlessEqual(len(scrn), 6)
        
        for i in range(5):
            row = scrn[i]
            self.failUnlessEqual(row.top, i)
            self.failUnlessEqual(row.end, i+1)
            self.failUnlessEqual(row.lineNo, 0)

    def testWordWrap1(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=0,
            wordwrap=1, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")


        buf = buffer.Buffer()
        buf.ins(0, u"a..012345 abcdefg")
        
#        self.DC.selectObject(self.FONT1)
#        for c in "a..012345 abcdefg":
#            print self.DC.getTextExtent(c)
        
        scrn = screen.Screen(self.DC, buf, conf, 60, 100)
        scrn.locate(0)

        self.failUnlessEqual(len(scrn), 3)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 3)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[1]
        self.failUnlessEqual(row.top, 3)
        self.failUnlessEqual(row.end, 10)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[2]
        self.failUnlessEqual(row.top, 10)
        self.failUnlessEqual(row.end, 17)
        self.failUnlessEqual(row.lineNo, 0)

    def testWordWrap2(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=0,
            wordwrap=1, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")


        buf = buffer.Buffer()
        buf.ins(0, u"あいうえおかきくけこ")
        
        scrn = screen.Screen(self.DC, buf, conf, 60, 100)
        scrn.locate(0)

        self.failUnlessEqual(len(scrn), 3)
        
        row = scrn[0]
        self.failUnlessEqual(row.top, 0)
        self.failUnlessEqual(row.end, 3)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[1]
        self.failUnlessEqual(row.top, 3)
        self.failUnlessEqual(row.end, 10)
        self.failUnlessEqual(row.lineNo, 0)

        row = scrn[2]
        self.failUnlessEqual(row.top, 10)
        self.failUnlessEqual(row.end, 17)
        self.failUnlessEqual(row.lineNo, 0)


    def testLarge(self):
        conf = screen.ScreenConf(
            [self.STYLE1],
            linegap=3, tab=4, wrap=1, maxcol=80,
            wordwrap=1, indentwrap=1, forcewrap=1, nowrapchars=(u'', u''),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=self.STYLE1,
            nowrapheaders=u"", itemize=u"")

        buf = buffer.Buffer()
        buf.ins(0, u"0123456789abcdefg"*60000)

        scrn = screen.Screen(self.DC, buf, conf, 1000, 1000)

        import time
        f = time.clock()
        scrn.locate(60000, mid=True)
        print time.clock() - f


if __name__ == '__main__':
    unittest.main()

