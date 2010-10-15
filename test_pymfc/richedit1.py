# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import time, cStringIO, re
from pymfc import wnd, app, menu, gdi

def run():

    def openrtf(msg):
        f = open(r".\test_pymfc\rich1.rtf", "rb")
        rich.streamIn(f)

        cf = wnd.CharFormat(italic=True)
        rich.setCharFormat(cf, all=True)

        pf = wnd.ParaFormat(bullet=True)
        rich.setParaFormat(pf)
        rich.setEventMask(link=True)

    def savertf(msg):
        f = open(r".\test_pymfc\rich11.rtf", "wb")
        rich.streamOut(f)

    mmap = menu.MenuMap(0x8000, 0x9000)
    bar = menu.MenuBar(u"MENUBAR", mmap)

    popup = menu.PopupMenu(u'File', u"File")
    openmenu = menu.MenuItem(u"open", u"open", u"open", openrtf)
    popup.append(openmenu)
    
    save = menu.MenuItem(u"save", u"save", u"save", savertf)
    popup.append(save)
    bar.append(popup)


    bar.create()

    f = wnd.FrameWnd(menu=bar)
    f.create()
    f.enableDocking()


    rich = wnd.RichEdit(parent=f, 
        style=wnd.RichEdit.STYLE(multiline=True, autovscroll=True, autohscroll=False, vscroll=True), anchor=wnd.Anchor(left=0, right=0, top=0, bottom=0))

    def calcrect(msg):
        print "???????????????????????????"
        print msg.getDict()
        ret = rich.defWndProc(msg)
        print ret, msg.getDict()
        return ret
    rich.msgproc.NCCALCSIZE = calcrect
    
    def ncpaint(msg):
        ret = rich.defWndProc(msg)
        return ret
        
    rich.msgproc.NCPAINT = ncpaint
    rich.create()
    rich.setEventMask(link=True, change=True)

    def f(msg):
        if msg.cause == rich.MSGDEF['LBUTTONDBLCLK']:
            print msg.getDict()
            
    def change(msg):
        w = msg.wnd
        stream = cStringIO.StringIO()
        msg.wnd.streamOut(stream, utf8=True, text=True)
        text = unicode(stream.getvalue(), "utf-8")
        text = text.replace("\r\n", "\n")
        
        r = re.compile(u"abc")

        cur = w.getSel()
        w.setRedraw(0)
        
        f = pos = 0
        for m in r.finditer(text):
            f, t = m.span()
            if pos != f:
                w.setSel((pos, f))
                fmt = msg.wnd.getCharFormat(selection=True)
                fmt.link = False
                w.setCharFormat(fmt, selection=True)

            w.setSel((f, t))
            fmt = msg.wnd.getCharFormat(selection=True)
            fmt.link = True
            w.setCharFormat(fmt, selection=True)
            pos = t
        
        end = len(text)
        if pos != end:
            w.setSel((pos, end))
            fmt = msg.wnd.getCharFormat(selection=True)
            fmt.link = False
            w.setCharFormat(fmt, selection=True)

        w.setSel(cur)
        w.setRedraw(1)
        w.invalidateRect(None, erase=False)

#        print msg.wnd.findWordBreak(msg.wnd.getSel()[1], movewordleft=True), msg.wnd.findWordBreak(msg.wnd.getSel()[1], movewordright=True)
#    rich.msglistener.LINK = f
    rich.msglistener.CHANGE = change

    app.run()

if __name__ == '__main__':
    run()
