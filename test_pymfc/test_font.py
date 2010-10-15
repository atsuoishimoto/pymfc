# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import gdi
dc = gdi.DisplayDC()


def f(tm, lf, isTrueType):
    print lf.facename, tm.tmHeight, isTrueType
    return 1
    
dc.EnumFontFamilies(f, shiftjis_charset=True)
