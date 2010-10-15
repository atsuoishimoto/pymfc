# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, gdi

dlg = wnd.PrintDialog(returndc=True)
ret = dlg.doModal()
if ret:
    print ret.devmode.devicename
    print ret.dc
    font = font=gdi.Font(face=u"ＭＳ ゴシック", dc=ret.dc, point=20, shiftjis_charset=True)
    ret.dc.selectObject(font)
    ret.dc.startDoc(u"テストドキュメント")
    ret.dc.startPage()
    ret.dc.textOut(u"あいうえお", (100,100))
    ret.dc.endPage()
    ret.dc.endDoc()
    