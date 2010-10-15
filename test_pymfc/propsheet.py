# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc import wnd



for j in range(1):
    dlg = wnd.PropertySheet()
    for i in range(10):
        page = wnd.PropertyPage(u"aaaa", parent=dlg, size=(100, 100))
        dlg.addPage(page)

    dlg.doModal()


