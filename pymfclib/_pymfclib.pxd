# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"



cdef class WndStyle:
    cdef public int style, exStyle
    cdef public object _styles
    cdef public object _exStyles


cdef class _WndBase:
    cdef void *_cwnd
    cdef readonly object cwnd
    cdef public object _keymap
#    cdef public object _msgs, _listeners, _keymap

    cdef HWND _getHwnd(self)
    cdef void * newInstance(self)


