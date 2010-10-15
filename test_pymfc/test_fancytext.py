# -*- coding: ShiftJIS -*-

import pymfc
from pymfc import app, wnd, gdi, fancytext

s1 = u"""2008/02/13 13:31
エリクソンCEO：「モバイルブロードバンドは世界を救う」
from CNET Japan
エリクソンのスヴァンベリCEOはバルセロナで開催されている「Mobile World Congress」で「モバイルブロードバンドは世界を救うことができる」との持論を披露した。"""

s2 = u"""2008/02/13 13:31
ツタヤオンライン、モバイル向けSNS「TSUTAYAコミュ！」を開始
from CNET Japan
ツタヤオンラインがモバイル向けSNS「TSUTAYAコミュ！」を開始した。Flashゲームなど約2万4000点のコンテンツをダウンロードできるほか、映画予告やTSUTAYAの店舗情報を配信する。"""


font1 = gdi.Font(face=u"Arial", point=12, weight=700, shiftjis_charset=True)
font2 = gdi.Font(face=u"ＭＳ Ｐゴシック", point=10, weight=300, shiftjis_charset=True)
font3 = gdi.Font(face=u"ＭＳ Ｐゴシック", point=12, weight=300, shiftjis_charset=True)
font4 = gdi.Font(face=u"Century", point=10, weight=300, shiftjis_charset=True)




docstyle = fancytext.Style(font=font1, textcolor=0x0, bgcolor=0x80ffff, 
    margin_left=5, margin_right=5, margin_top=20, margin_bottom=20)
style1 = fancytext.Style(font=font1, textcolor=0x0, bgcolor=0x80ffff)
style2 = fancytext.Style(font=font3, textcolor=0x0, margin_left=10, margin_top=5, margin_bottom=50)
style3 = fancytext.Style(font=font4, textcolor=0x0)

icon = gdi.Icon(filename=u".\\pymfc\\test_pymfc\\pc.ico", cx=16, cy=16)

doc = fancytext.Doc(docstyle)
doc.add(s1, style1, None)

doc.add(icon, style1, None)
doc.add(s2, style1, None)



doc.add(s1, style2, None)
doc.add(s2, style3, None)

doc.add(u"\nxyzxyz", style1, None)
doc.add(u"abcdefg", style1, None)



style4 = fancytext.Style(font=font2, textcolor=0x204055, bgcolor=0x0000ff)
node0 = fancytext.Node()

action = fancytext.Action()

node0.add(u"リンクテキスト", style4, action)
doc.add(icon, style4, None)
node0.add(fancytext.HR(), style4, action)
doc.add(node0, style4, None)


node1 = fancytext.Block(style2)
node1.add(s1, style3, None)
node1.add(u"6789", style3, None)
doc.add(node1, None, None)
node1.bgcolor=0x55ff99


liststyle1 = fancytext.Style(font=font1, textcolor=0x0, bgcolor=0xeeffdd, 
    listitem=icon, margin_left=10, margin_bottom=30)

node = fancytext.Block(liststyle1)
doc.add(node, None, None)
node.add(s1, style1, None)

node = fancytext.Block(liststyle1)
doc.add(node, None, None)
node.add(s2, style1, None)
node.add(u"\n\n\n\n", style1, None)


headerstyle = fancytext.Style(font=font1, textcolor=0x0, bgcolor=None, 
    margin_left=5, margin_right=5, margin_top=5, margin_bottom=5, background=fancytext.RoundRectHeader())

node = fancytext.Block(headerstyle)
doc.add(node, None, None)
node.add(u"ヘッダーヘッダーヘッダーヘッダー", headerstyle, None)

node2 = fancytext.Block(style1)
node.add(node2, None, None)
node.add(u"abc abc abc abc abc abc ", style1, None)


footerstyle = fancytext.Style(font=font1, textcolor=0x0, bgcolor=None, 
    margin_left=5, margin_right=5, margin_top=5, margin_bottom=5, background=fancytext.RoundRectFooter())

node = fancytext.Block(footerstyle)
doc.add(node, None, None)
node.add(u"フッターフッターフッターフッターフッターフッターフッターフッター", footerstyle, None)






f = wnd.FrameWnd(size=(200, 500), pos=(100,100))
style = wnd.Wnd.STYLE(vscroll=True)
w = fancytext.FancyTextWnd(parent=f, anchor=wnd.Anchor(occupy=True),
        autocreate=True, style=style)
    
f.create()
w.setDocument(doc)


pymfc.app.run()




