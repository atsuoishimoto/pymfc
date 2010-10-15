# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, gdi

f = gdi.Font(face=u"Times New Roman", point=10)
print f.getLogFont()

for i in range(10):
    lf = gdi.LogFont(facename=u"Arial", point=20)
    dlg = wnd.FontDialog(logfont=lf)
    f = dlg.doModal()
    if f:
        print `f.facename`, f.height, f
        print dlg.selectedPoint, dlg.selectedColor

