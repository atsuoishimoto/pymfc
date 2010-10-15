# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"

cdef extern from "htmlhelp.h":
    HWND HtmlHelpW(HWND hwndCaller, LPCWSTR  pszFile, UINT uCommand, DWORD dwData) nogil

    int HH_DISPLAY_TOPIC, HH_HELP_FINDER, HH_DISPLAY_TOC, HH_DISPLAY_INDEX
    int HH_DISPLAY_SEARCH, HH_SET_WIN_TYPE, HH_GET_WIN_TYPE, HH_GET_WIN_HANDLE
    int HH_ENUM_INFO_TYPE, HH_SET_INFO_TYPE, HH_SYNC, HH_RESERVED1, HH_RESERVED2
    int HH_RESERVED3, HH_KEYWORD_LOOKUP, HH_DISPLAY_TEXT_POPUP, HH_HELP_CONTEXT
    int HH_TP_HELP_CONTEXTMENU, HH_TP_HELP_WM_HELP, HH_CLOSE_ALL, HH_ALINK_LOOKUP
    int HH_GET_LAST_ERROR, HH_ENUM_CATEGORY, HH_ENUM_CATEGORY_IT, HH_RESET_IT_FILTER
    int HH_SET_INCLUSIVE_FILTER, HH_SET_EXCLUSIVE_FILTER, HH_INITIALIZE
    int HH_UNINITIALIZE, HH_SET_QUERYSERVICE, HH_PRETRANSLATEMESSAGE
    int HH_SET_GLOBAL_PROPERTY, HH_SAFE_DISPLAY_TOPIC

def htmlhelp_init():
    cdef HWND ret
    cdef DWORD dwCookie

    ret = NULL
    dwCookie = 0
    
    with nogil:
        ret = HtmlHelpW(NULL, NULL, HH_INITIALIZE, <DWORD>&dwCookie)
    return dwCookie

def htmlhelp_uninit(cookie):
    cdef DWORD dwCookie

    dwCookie = cookie
    
    with nogil:
        HtmlHelpW(NULL, NULL, HH_UNINITIALIZE, dwCookie)


def htmlhelp_display_topic(wnd, url):
    cdef PYMFC_WCHAR *u_url
    cdef HWND hWnd
    
    if PyMFCHandle_IsHandle(wnd):
        hWnd = PyMFCHandle_AsHandle(wnd)
    else:
        hWnd =  PyMFCHandle_AsHandle(wnd.getHwnd())
    
    u_url = PyUnicode_AsUnicode(url)

    with nogil:
        HtmlHelpW(hWnd, u_url, HH_DISPLAY_TOPIC, 0)

