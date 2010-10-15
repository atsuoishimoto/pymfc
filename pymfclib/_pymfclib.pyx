# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass


    
import _pymfclib

cdef extern from "pyminit.h":
    int pymInit(object)
    object pymInitPyMFCException()
    object pymInitPyMFCWin32Exception()
    object pymInitWndMsgType()
    object pymInitKeyDict()
    object pymInitMessageDict()




pymInit(_pymfclib)

PyMFCException = pymInitPyMFCException()
Win32Exception = pymInitPyMFCWin32Exception()
_wndmsg = pymInitWndMsgType() 
_keydict = pymInitKeyDict()
_msgdict = pymInitMessageDict()

class __CONSTDEF:
    pass

include "pymfc_app.pxi"
include "pymfc_wndclass.pxi"
include "pymfc_wndstyle.pxi"
include "pymfc_vkeydef.pxi"
include "pymfc_wndbase.pxi"
include "pymfc_wnd.pxi"
include "pymfc_ctrl.pxi"
include "pymfc_ctrlbar.pxi"
include "pymfc_commctrl.pxi"
include "pymfc_tree.pxi"
include "pymfc_listview.pxi"
include "pymfc_richedit.pxi"
include "pymfc_traynotify.pxi"
include "pymfc_webctrl.pxi"


include "pymfc_imm.pxi"

import datetime

import _pymfclib_menu

import pymfc.gdi
import _pymfclib_system
import _pymfclib_editor


cdef _import_submodules():
    for name in dir(_pymfclib_system):
        if not name.startswith('_'):
            setattr(_pymfclib, name, getattr(_pymfclib_system, name))

_import_submodules()


