# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd
from pymfc.fstree import *

def test():
    dlg = wnd.Dialog(u"abcdefg", size=(500, 350), pos=(100,100))
#    trees = [FSTree(size=(300, 300), pos=(10+i, 10+i), parent=dlg) for i in range(50)]
    tree = FSTree(size=(300, 300), pos=(10, 10), parent=dlg)

    dlg.doModal()


for i in  range(1):
    test()
    