# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import gc, sys
from pymfc import wnd

def test():
    dlg = wnd.Dialog(u"abcdefg", (200, 400), pos=(100,100))
    combo1 = wnd.ComboBox(u"def", size=(100, 125), pos=(10, 10), parent=dlg)
    dlg.doModal()


for i in  range(10):
    print i
    test()