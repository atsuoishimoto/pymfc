# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"

class __CONSTDEF:
    pass

include "pymfc_gdi.pxi"


