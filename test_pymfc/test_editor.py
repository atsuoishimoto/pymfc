# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, gdi, app, menu, grid
from pymfc.editor import editor, buffer, screen, mode

def save(msg):
    s = msg.wnd.getBuffer()[:]
    open("saved.txt", "wb").write(s.encode("utf-8"))
    
def run():
    class TestMode(mode.Mode):
        pass
        def _getTokenizer(self):
            return mode.URLTokenizer()

    def c():
        f = wnd.FrameWnd(u"title1")
        f.create()

        BG = 0xffffff
        BG_SEL = 0xff0000
        FG = 0x000000
        TAB = 0x00ff00
        LF = 0x0000ff
        SPC = 0xc0c0c0
        
        nonlatin = gdi.Font(face=u"ＭＳ Ｐゴシック", point=9)
        latin = gdi.Font(face=u"Courier New", point=12)
        color = screen.StyleColor(
            text = (FG, BG),
            text_sel = (FG, BG_SEL),
            lf = (LF, BG),
            lf_sel = (LF, BG_SEL),
            tab = (TAB, BG),
            tab_sel = (TAB, BG_SEL),
            fullspc = (SPC, BG),
            fullspc_sel = (SPC, BG_SEL))

        style = screen.TextStyle(latin, nonlatin, color)
        

        color_url = screen.StyleColor(
            text = (0x00ff00, 0x202020),
            text_sel = (FG, BG_SEL),
            lf = (LF, BG),
            lf_sel = (LF, BG_SEL),
            tab = (TAB, BG),
            tab_sel = (TAB, BG_SEL),
            fullspc = (SPC, BG),
            fullspc_sel = (SPC, BG_SEL))

        font_url_nonlatin = gdi.Font(face=u"ＭＳ Ｐ明朝", point=20, weight=700)
        font_url_latin = gdi.Font(face=u"Arial", point=20, weight=700)
        style_url = screen.TextStyle(font_url_latin, font_url_nonlatin, color_url)

        color_mail = screen.StyleColor(
            text = (0xf0f0f0, 0xff3f3f),
            text_sel = (FG, BG_SEL),
            lf = (LF, BG),
            lf_sel = (LF, BG_SEL),
            tab = (TAB, BG),
            tab_sel = (TAB, BG_SEL),
            fullspc = (SPC, BG),
            fullspc_sel = (SPC, BG_SEL))

        font_mail_nonlatin = gdi.Font(face=u"ＭＳ Ｐ明朝", point=20, underline=True)
        font_mail_latin = gdi.Font(face=u"Times New Roman", point=20)
        style_mail = screen.TextStyle(font_mail_latin, font_mail_nonlatin, color_mail)

        conf = screen.ScreenConf(
            styles=[style, style_url, style_mail],
            linegap=10, tab=8, wrap=1, forcewrap=0, maxcol=78,
            wordwrap=1, indentwrap=1, 
            nowrapchars=(u'、。，．・？！゛゜ヽヾゝゞ々ー）］｝」』!),.:;?]}｡｣､･ｰﾞﾟ>', 
                u'（［｛「『([{｢<'),
            showtab=1, showlf=1, showfullspc=1,
            bgcolor=0xffffff, linenostyle=style,
            nowrapheaders=u">", itemize=u"*-・")

        e = editor.Editor(parent=f, pos=(0,0), size=(10, 20), anchor=wnd.Anchor(occupy=True))
        e.initEditor(editmode=TestMode(buffer.Buffer()), conf=conf)
        e.create()
#        e.getMode().insertString(e._editorwnd, 0, u"abc\ndefg")
        e._editorwnd.keymap.addKey(save, [(0,0,0,wnd.KEY.F12)])

    c()
    app.run()

if __name__ == '__main__':
    run()

