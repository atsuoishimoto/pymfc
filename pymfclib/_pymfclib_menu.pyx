# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass
cdef extern from "pymfcdefs.h":
    pass

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"


cdef extern from "pymmenu.h":
    int c_menu_ismenu(HMENU hMenu) except -1
    HMENU c_menu_create() except NULL
    HMENU c_menu_createPopup() except NULL
    int c_menu_destroy(HMENU hMenu) except 0
    int c_menu_insert(HMENU hMenu, int nPosition, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem) except 0
    int c_menu_append(HMENU hMenu, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem) except 0
    int c_menu_delete(HMENU hMenu, int nPosition, int nFlags) except 0
    int c_menu_remove(HMENU hMenu, int nPosition, int nFlags) except 0
    int c_menu_itemCount(HMENU hMenu) except -1
    object c_menu_getString(HMENU hMenu, int nPosition, int nFlags)
    int EnableMenuItem(HMENU hMenu, int uIDEnableItem, int uEnable)

    int c_menu_track_popup_menu(HMENU hmenu, int fuFlags, int x, int y, void *hwnd, void *lptpm) except *
    int TPM_NONOTIFY, TPM_RETURNCMD

    ctypedef struct TPMPARAMS:
        UINT cbSize
        RECT rcExclude

cdef extern from "windows.h":
    int MF_INSERT
    int MF_CHANGE
    int MF_APPEND
    int MF_DELETE
    int MF_REMOVE
    int MF_BYCOMMAND
    int MF_BYPOSITION
    int MF_SEPARATOR
    int MF_ENABLED
    int MF_GRAYED
    int MF_DISABLED
    int MF_UNCHECKED
    int MF_CHECKED
    int MF_USECHECKBITMAPS
    int MF_STRING
    int MF_BITMAP
    int MF_OWNERDRAW
    int MF_POPUP
    int MF_MENUBARBREAK
    int MF_MENUBREAK
    int MF_UNHILITE
    int MF_HILITE
    int MF_DEFAULT
    int MF_SYSMENU
    int MF_HELP
    int MF_RIGHTJUSTIFY
    int MF_MOUSESELECT
    int MF_END
    int MFT_STRING
    int MFT_BITMAP
    int MFT_MENUBARBREAK
    int MFT_MENUBREAK
    int MFT_OWNERDRAW
    int MFT_RADIOCHECK
    int MFT_SEPARATOR
    int MFT_RIGHTORDER
    int MFT_RIGHTJUSTIFY
    int MFS_GRAYED
    int MFS_DISABLED
    int MFS_CHECKED
    int MFS_HILITE
    int MFS_ENABLED
    int MFS_UNCHECKED
    int MFS_UNHILITE
    int MFS_DEFAULT

class __MENUCONSTS:
    pass

_const_menu = __MENUCONSTS()
cdef object __const_menu
__const_menu = _const_menu

__const_menu.MF_INSERT = MF_INSERT
__const_menu.MF_CHANGE = MF_CHANGE
__const_menu.MF_APPEND = MF_APPEND
__const_menu.MF_DELETE = MF_DELETE
__const_menu.MF_REMOVE = MF_REMOVE
__const_menu.MF_BYCOMMAND = MF_BYCOMMAND
__const_menu.MF_BYPOSITION = MF_BYPOSITION
__const_menu.MF_SEPARATOR = MF_SEPARATOR
__const_menu.MF_ENABLED = MF_ENABLED
__const_menu.MF_GRAYED = MF_GRAYED
__const_menu.MF_DISABLED = MF_DISABLED
__const_menu.MF_UNCHECKED = MF_UNCHECKED
__const_menu.MF_CHECKED = MF_CHECKED
__const_menu.MF_USECHECKBITMAPS = MF_USECHECKBITMAPS
__const_menu.MF_STRING = MF_STRING
__const_menu.MF_BITMAP = MF_BITMAP
__const_menu.MF_OWNERDRAW = MF_OWNERDRAW
__const_menu.MF_POPUP = MF_POPUP
__const_menu.MF_MENUBARBREAK = MF_MENUBARBREAK
__const_menu.MF_MENUBREAK = MF_MENUBREAK
__const_menu.MF_UNHILITE = MF_UNHILITE
__const_menu.MF_HILITE = MF_HILITE
__const_menu.MF_DEFAULT = MF_DEFAULT
__const_menu.MF_SYSMENU = MF_SYSMENU
__const_menu.MF_HELP = MF_HELP
__const_menu.MF_RIGHTJUSTIFY = MF_RIGHTJUSTIFY
__const_menu.MF_MOUSESELECT = MF_MOUSESELECT
__const_menu.MF_END = MF_END
__const_menu.MFT_STRING = MFT_STRING
__const_menu.MFT_BITMAP = MFT_BITMAP
__const_menu.MFT_MENUBARBREAK = MFT_MENUBARBREAK
__const_menu.MFT_MENUBREAK = MFT_MENUBREAK
__const_menu.MFT_OWNERDRAW = MFT_OWNERDRAW
__const_menu.MFT_RADIOCHECK = MFT_RADIOCHECK
__const_menu.MFT_SEPARATOR = MFT_SEPARATOR
__const_menu.MFT_RIGHTORDER = MFT_RIGHTORDER
__const_menu.MFT_RIGHTJUSTIFY = MFT_RIGHTJUSTIFY
__const_menu.MFS_GRAYED = MFS_GRAYED
__const_menu.MFS_DISABLED = MFS_DISABLED
__const_menu.MFS_CHECKED = MFS_CHECKED
__const_menu.MFS_HILITE = MFS_HILITE
__const_menu.MFS_ENABLED = MFS_ENABLED
__const_menu.MFS_UNCHECKED = MFS_UNCHECKED
__const_menu.MFS_UNHILITE = MFS_UNHILITE
__const_menu.MFS_DEFAULT = MFS_DEFAULT


def _menu_ismenu(hMenu):
    return c_menu_ismenu(PyMFCHandle_AsHandle(hMenu))

def _menu_create():
    return PyMFCHandle_FromHandle(c_menu_create())

def _menu_createPopup():
    return PyMFCHandle_FromHandle(c_menu_createPopup())
    
def _menu_destroy(hMenu):
    c_menu_destroy(PyMFCHandle_AsHandle(hMenu))

def _menu_insert(hMenu, nPosition, nFlags, nIDNewItem, lpszNewItem):
    cdef void *newitem
    cdef long n
    if PyMFCHandle_IsHandle(nIDNewItem):
        newitem = PyMFCHandle_AsHandle(nIDNewItem)
    else:
        n = nIDNewItem
        newitem = <void *>n

    c_menu_insert(PyMFCHandle_AsHandle(hMenu), nPosition, nFlags, newitem, PyUnicode_AsUnicode(lpszNewItem))

def _menu_append(hMenu, nFlags, nIDNewItem, lpszNewItem):
    cdef void *newitem
    cdef long n
    if PyMFCHandle_IsHandle(nIDNewItem):
        newitem = PyMFCHandle_AsHandle(nIDNewItem)
    else:
        n = nIDNewItem
        newitem = <void *>n
        
    c_menu_append(PyMFCHandle_AsHandle(hMenu), nFlags, newitem, PyUnicode_AsUnicode(lpszNewItem))

def _menu_delete(hMenu, nPosition, nFlags):
    c_menu_delete(PyMFCHandle_AsHandle(hMenu), nPosition, nFlags)

def _menu_remove(hMenu, nPosition, nFlags):
    c_menu_remove(PyMFCHandle_AsHandle(hMenu), nPosition, nFlags)

def _menu_itemCount(hMenu):
    return c_menu_itemCount(PyMFCHandle_AsHandle(hMenu))

def _menu_getString(hMenu, nPosition, nFlags):
    return c_menu_getString(PyMFCHandle_AsHandle(hMenu), nPosition, nFlags)

def _menu_enable_menu_item(hMenu, uIDEnableItem, uEnable):
    cdef HMENU hmenu
    hmenu = PyMFCHandle_AsHandle(hMenu)
    EnableMenuItem(hmenu, uIDEnableItem, uEnable)


def _menu_track_popup_menu(hMenu, long x, long y, wnd, exclude=None, long nonotify=0, long returncmd=0):
    cdef int f
    cdef HWND w
    cdef TPMPARAMS tpm
    cdef TPMPARAMS *ptpm
    
    if getattr(wnd, 'getHwnd'):
        w = PyMFCHandle_AsHandle(wnd.getHwnd())
    else:
        w = PyMFCHandle_AsHandle(wnd)
    f = 0
    if nonotify:
        f = f | TPM_NONOTIFY
    if returncmd:
        f = f | TPM_RETURNCMD
    
    ptpm = NULL
    if exclude:
        ptpm = &tpm
        tpm.cbSize = sizeof(tpm)
        tpm.rcExclude.left = exclude[0]
        tpm.rcExclude.top = exclude[1]
        tpm.rcExclude.right = exclude[2]
        tpm.rcExclude.bottom = exclude[3]

    return c_menu_track_popup_menu(PyMFCHandle_AsHandle(hMenu), f, x, y, w, ptpm)

