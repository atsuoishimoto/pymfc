# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd

for i in range(10):
    dlg = wnd.ColorDialog(color=0xff0000, anycolor=True, height=300)
    f = dlg.doModal()
    print f

