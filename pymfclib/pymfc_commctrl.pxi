
#
# Image list
#
cdef extern from *:

    ctypedef void *HIMAGELIST

    int ILC_COLOR, ILC_COLOR4, ILC_COLOR8, ILC_COLOR16
    int ILC_COLOR24, ILC_COLOR32, ILC_COLORDDB, ILC_MASK

    void *new_ImageList() except NULL
    int CImageList_Create(void *o, int cx, int cy, int nFlags, int nInitial, int nGrow) except 0
    int CImageList_Attach(void *o, HIMAGELIST himagelist) except 0
    int CImageList_Detach(void *o) except 0


    int CImageList_AddImage(void *o, HBITMAP bmp, HBITMAP maskbmp, COLORREF maskrgb, HICON hicon) except -1
    int CImageList_Delete(void *o) except 0
    void *CImageList_HANDLE(void *o) except NULL
    
    int CImageList_BeginDrag(void *o, int n, int x, int y) except 0
    int CImageList_EndDrag() except 0
    int CImageList_DragShowNolock(int f) except 0
    int CImageList_DragMove(int x, int y) except 0


    int ILD_BLEND25, ILD_FOCUS, ILD_BLEND50, ILD_SELECTED
    int ILD_BLEND, ILD_MASK, ILD_NORMAL, ILD_TRANSPARENT
    
    int CLR_NONE, CLR_DEFAULT

    UINT INDEXTOOVERLAYMASK(UINT iOverlay)
    BOOL ImageList_Draw(HIMAGELIST himl, int i, HDC hdcDst, int x, int y,UINT fStyle)
    BOOL ImageList_DrawEx(HIMAGELIST himl, int i, HDC hdcDst, int x, int y, int dx, int dy, unsigned long rgbBk, unsigned long rgbFg, UINT fStyle)
    HICON ImageList_GetIcon(HIMAGELIST himl, int i, UINT flags)
    BOOL ImageList_SetIconSize(HIMAGELIST himl, int cx, int cy)
    BOOL ImageList_GetIconSize(HIMAGELIST himl, int *cx, int *cy)
    COLORREF ImageList_SetBkColor(HIMAGELIST himl, COLORREF clrBk)
    COLORREF ImageList_GetBkColor(HIMAGELIST himl)
    BOOL ImageList_SetOverlayImage(HIMAGELIST himl, int iImage, int iOverlay)
    BOOL ImageList_Remove(HIMAGELIST himl, int i)
    int ImageList_GetImageCount(HIMAGELIST himl)
    
cdef class _imagelist:
    cdef void *_cimagelist
    cdef public int _ownHandle
    def __init__(self, hImagelist=0):
        self._cimagelist = new_ImageList()
        self._ownHandle = 1
        
    def __dealloc__(self):
        if self._cimagelist:
            if self._ownHandle == 0:
                CImageList_Detach(self._cimagelist)
            CImageList_Delete(self._cimagelist)
            self._cimagelist = NULL

    def create(self, cx=0, cy=0, color=0, ddb=0, mask=0, initial=1, grow=1):
        cdef int flag
        flag = 0
        if color==0:
            flag = ILC_COLOR
        elif color==4:
            flag = ILC_COLOR4
        elif color==8:
            flag = ILC_COLOR8
        elif color==16:
            flag = ILC_COLOR16
        elif color==24:
            flag = ILC_COLOR24
        elif color==32:
            flag = ILC_COLOR32
        else:
            raise ValueError("Invalid color value %d" % color)
            
        if ddb:
            if color:
                raise ValueError("Cannot use color and ddb at same time")
            flag = ILC_COLORDDB

        if mask:
            flag = flag | ILC_MASK

        CImageList_Create(self._cimagelist, cx, cy, flag, initial, grow)

    def attach(self, hImageList, ownHandle=1):
        CImageList_Attach(self._cimagelist, PyMFCHandle_AsHandle(hImageList))
        if not ownHandle:
            self._ownHandle = 0

    def detach(self):
        CImageList_Detach(self._cimagelist)

    cdef HANDLE _getHandle(self):
        return CImageList_HANDLE(self._cimagelist)
    
    def getHandle(self):
        return PyMFCHandle_FromHandle(self._getHandle())

    def getCImageList(self):
        return PyMFCPtr_FromVoidPtr(self._cimagelist)
        
    def addBitmap(self, bmp, maskbmp=None, maskrgb=None):
        # Bitmap is copied to imagelist. So we don't have to retain bmp object.
        cdef HBITMAP _bmp, _maskbmp
        cdef COLORREF _maskrgb
        _bmp = _maskbmp = NULL
        _maskrgb = 0

        _bmp = PyMFCHandle_AsHandle(bmp.getHandle())
        if maskbmp is not None:
            _maskbmp = PyMFCHandle_AsHandle(maskbmp.getHandle())
        if maskrgb is not None:
            _maskrgb = maskrgb

        return CImageList_AddImage(self._cimagelist, _bmp, _maskbmp, _maskrgb, NULL)

    def addIcon(self, icon):
        # Icon is copied to imagelist. So we don't have to retain icon object.
        cdef HICON hicon

        if PyMFCHandle_IsHandle(icon):
            hicon = PyMFCHandle_AsHandle(icon)
        else:
            hicon = PyMFCHandle_AsHandle(icon.getHandle())
        return CImageList_AddImage(self._cimagelist, NULL, NULL, 0, hicon)
    
    def remove(self, int index):
        if 0 == ImageList_Remove(self._getHandle(), index):
            pymRaiseWin32Err()
        
    def getImageCount(self):
        return ImageList_GetImageCount(self._getHandle())
            
    def getIcon(self, int index, 
            int blend25=0, int focus=0, int blend50=0, int selected=0, int blend=0, 
            int mask=0, int normal=0, int transparent=0, overlay=0):
        
        cdef int flag
        cdef HICON hIcon
        
        flag = 0
        if overlay:
            flag = flag | INDEXTOOVERLAYMASK(overlay)
        if blend25:
            flag = flag | ILD_BLEND25
        if focus:
            flag = flag | ILD_FOCUS
        if blend50:
            flag = flag | ILD_BLEND50
        if selected:
            flag = flag | ILD_SELECTED
        if blend:
            flag = flag | ILD_BLEND
        if mask:
            flag = flag | ILD_MASK
        if normal:
            flag = flag | ILD_NORMAL
        if transparent:
            flag = flag | ILD_TRANSPARENT
        
        hIcon = ImageList_GetIcon(self._getHandle(), index, flag)
        if hIcon == NULL:
            pymRaiseWin32Err()
        ret = pymfc.gdi.Icon(hIcon=PyMFCHandle_FromHandle(hIcon), own=1)
        return ret
    
    def getIconSize(self):
        cdef int x, y
        if 0 == ImageList_GetIconSize(self._getHandle(), &x, &y):
            pymRaiseWin32Err()
        
        return x, y
        
    def setIconSize(self, size):
        cdef int x, y
        x, y = size
        if 0 == ImageList_SetIconSize(self._getHandle(), x, y):
            pymRaiseWin32Err()

    def setBkColor(self, COLORREF color):
        ImageList_SetBkColor(self._getHandle(), color)

    def getBkColor(self):
        return ImageList_GetBkColor(self._getHandle())

    def setOverlayImage(self, index, overlay):
        if 0 == ImageList_SetOverlayImage(self._getHandle(), index, overlay):
            pymRaiseWin32Err()

    def draw(self, index, dc, pos, size=None, bk=None, fg=None, 
            int blend25=0, int focus=0, int blend50=0, int selected=0, int blend=0, 
            int mask=0, int normal=0, int transparent=0, overlay=0):
        
        cdef int flag
        flag = 0
        if overlay:
            flag = flag | INDEXTOOVERLAYMASK(overlay)
        if blend25:
            flag = flag | ILD_BLEND25
        if focus:
            flag = flag | ILD_FOCUS
        if blend50:
            flag = flag | ILD_BLEND50
        if selected:
            flag = flag | ILD_SELECTED
        if blend:
            flag = flag | ILD_BLEND
        if mask:
            flag = flag | ILD_MASK
        if normal:
            flag = flag | ILD_NORMAL
        if transparent:
            flag = flag | ILD_TRANSPARENT
        
        cdef HDC hdc
        hdc = PyMFCHandle_AsHandle(dc.hDC)
        
        cdef int dx, dy
        if size:
            dx = size[0]
            dy = size[1]
        else:
            dx = 0
            dy = 0
        
        if bk is None:
            bk = CLR_DEFAULT
        if fg is None:
            fg = CLR_DEFAULT

        
        if 0 == ImageList_DrawEx(self._getHandle(), index, <HDC>hdc, pos[0], pos[1], 
                    dx, dy, bk, fg, flag):
            pymRaiseWin32Err()
            
    def beginDrag(self, n, hotspot):
        CImageList_BeginDrag(self._cimagelist, n, hotspot[0], hotspot[1])
    
    def endDrag(self):
        CImageList_EndDrag()
    
    def dragMove(self, pos):
        CImageList_DragMove(pos[0], pos[1])

def pymfc_Imagelist_dragShowNoLock(f):
    CImageList_DragShowNolock(f)


#
# Tab control
#
cdef extern from "pymwnd.h":
    # Controls
    void *new_TabCtrl(object obj) except NULL
    int CTabCtrl_AdjustRect(void *o, int larger, int *left, int *top, int *right, int *bottom) except 0
    int CTabCtrl_InsertItem(void *o, int idx, TCHAR *title) except 0

    int TCM_GETIMAGELIST, TCM_SETIMAGELIST, TCM_GETITEMCOUNT, TCM_GETITEM
    int TCM_SETITEM, TCM_INSERTITEM, TCM_DELETEITEM, TCM_DELETEALLITEMS
    int TCM_GETITEMRECT, TCM_GETCURSEL, TCM_SETCURSEL, TCM_HITTEST
    int TCM_SETITEMEXTRA, TCM_ADJUSTRECT, TCM_SETITEMSIZE, TCM_REMOVEIMAGE
    int TCM_SETPADDING, TCM_GETROWCOUNT, TCM_GETTOOLTIPS, TCM_SETTOOLTIPS
    int TCM_GETCURFOCUS, TCM_SETCURFOCUS, TCM_SETMINTABWIDTH, TCM_DESELECTALL
    int TCM_HIGHLIGHTITEM, TCM_SETEXTENDEDSTYLE, TCM_GETEXTENDEDSTYLE
    int TCM_SETUNICODEFORMAT, TCM_GETUNICODEFORMAT

    ctypedef struct TCITEM:
        UINT mask
        DWORD dwState
        DWORD dwStateMask
        LPSTR pszText
        int cchTextMax
        int iImage
        LPARAM lParam


cdef class _tabctrl(_WndBase):
    cdef void *newInstance(self):
        return new_TabCtrl(self)
    
    def adjustRect(self, larger, rc):
        cdef int l, t, r, b
        l, t, r, b = rc
        CTabCtrl_AdjustRect(self._cwnd, larger, &l, &t, &r, &b)
        return (l, t, r, b)

    def insertItem(self, idx, title):
        CTabCtrl_InsertItem(self._cwnd, idx, PyUnicode_AsUnicode(title))
    
    def deleteItem(self, idx):
        return CWnd_SendMessage_L_L_L_0(self._cwnd, TCM_DELETEITEM, 0, 0)
    
    def deleteAllItems(self):
        return CWnd_SendMessage_L_L_L_0(self._cwnd, TCM_DELETEALLITEMS, 0, 0)
    
    def getCurSel(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, TCM_GETCURSEL, 0, 0)
        
    def setCurSel(self, n):
        return CWnd_SendMessage_L_L_L_m1(self._cwnd, TCM_SETCURSEL, n, 0)
        

# TabCtrl styles

cdef extern from *:
    int TCS_SCROLLOPPOSITE, TCS_BOTTOM, TCS_RIGHT, TCS_MULTISELECT
    int TCS_FLATBUTTONS, TCS_FORCEICONLEFT, TCS_FORCELABELLEFT
    int TCS_HOTTRACK, TCS_VERTICAL, TCS_TABS, TCS_BUTTONS, TCS_SINGLELINE
    int TCS_MULTILINE, TCS_RIGHTJUSTIFY, TCS_FIXEDWIDTH, TCS_RAGGEDRIGHT
    int TCS_FOCUSONBUTTONDOWN, TCS_OWNERDRAWFIXED, TCS_TOOLTIPS
    int TCS_FOCUSNEVER, TCS_EX_FLATSEPARATORS, TCS_EX_REGISTERDROP

cdef __init_tabctrl_styles():
    ret = {
        "scrollopposite":TCS_SCROLLOPPOSITE,
        "bottom":TCS_BOTTOM,
        "right":TCS_RIGHT,
        "multiselect":TCS_MULTISELECT,
        "flatbuttons":TCS_FLATBUTTONS,
        "forceiconleft":TCS_FORCEICONLEFT,
        "forcelabelleft":TCS_FORCELABELLEFT,
        "hottrack":TCS_HOTTRACK,
        "vertical":TCS_VERTICAL,
        "tabs":TCS_TABS,
        "buttons":TCS_BUTTONS,
        "singleline":TCS_SINGLELINE,
        "multiline":TCS_MULTILINE,
        "rightjustify":TCS_RIGHTJUSTIFY,
        "fixedwidth":TCS_FIXEDWIDTH,
        "raggedright":TCS_RAGGEDRIGHT,
        "focusonbuttondown":TCS_FOCUSONBUTTONDOWN,
        "ownerdrawfixed":TCS_OWNERDRAWFIXED,
        "tooltips":TCS_TOOLTIPS,
        "focusnever":TCS_FOCUSNEVER,
    }
    ret.update(_std_styles)
    return ret

_tabctrl_styles = __init_tabctrl_styles()

cdef __init_tabctrl_ex_styles():
    ret = {
        "flatseparators":TCS_EX_FLATSEPARATORS,
        "registerdrop":TCS_EX_REGISTERDROP,
    }
    ret.update(_std_ex_styles)
    return ret

_tabctrl_ex_styles = __init_tabctrl_ex_styles()


cdef class TabCtrlStyle(WndStyle):
    def _initTable(self):
        self._styles = _tabctrl_styles
        self._exStyles = _tabctrl_ex_styles
    
# TabCtrl messages
cdef extern from *:
    int TCN_KEYDOWN, TCN_SELCHANGE, TCN_SELCHANGING, TCN_GETOBJECT,

cdef __init_tabctrlmsg():
    ret = {
    "KEYDOWN":(WM_NOTIFY, TCN_KEYDOWN),
    "SELCHANGE":(WM_NOTIFY, TCN_SELCHANGE),
    "SELCHANGING":(WM_NOTIFY, TCN_SELCHANGING),
    "GETOBJECT":(WM_NOTIFY, TCN_GETOBJECT),
    }
    ret.update(_msgdict)
    return ret

_tabctrlmsg = __init_tabctrlmsg()





#
# Date and Time Picker control
#
cdef extern from "pymwnd.h":
    # Controls
    int DTM_GETSYSTEMTIME, DTM_SETSYSTEMTIME, DTM_GETRANGE, DTM_SETRANGE,
    int DTM_SETFORMAT, DTM_SETMCCOLOR, DTM_GETMCCOLOR, DTM_GETMONTHCAL,
    int DTM_SETMCFONT, DTM_GETMCFONT
    int GDT_NONE, GDT_VALID, GDT_ERROR

cdef class _datetimectrl(_WndBase):
    cdef void *newInstance(self):
        cdef INITCOMMONCONTROLSEX ic
        ic.dwSize = sizeof(ic)
        ic.dwICC = ICC_DATE_CLASSES

        if 0 == InitCommonControlsEx(&ic):
            pymRaiseWin32Err()
        return new_CWnd(self)

    def getTime(self):
        cdef SYSTEMTIME systime
        ret = CWnd_SendMessage_L_P_L(self._cwnd, DTM_GETSYSTEMTIME, 0, &systime)
        if ret == GDT_ERROR:
            pymRaiseWin32Err()
        elif ret == GDT_NONE:
            return None
        else:
            tz = _pymfclib.Win32TZInfo()
            return datetime.datetime(systime.wYear, systime.wMonth, systime.wDay, 
                systime.wHour, systime.wMinute, systime.wSecond, systime.wMilliseconds)

    def setTime(self, time):
        cdef SYSTEMTIME systime
        cdef long v
        
        if time is None:
            ret = CWnd_SendMessage_L_L_L(self._cwnd, DTM_SETSYSTEMTIME, GDT_NONE, 0)
            if ret == 0:
                pymRaiseWin32Err()
        else:
            # use temporally var to prevent compiler's warning
            v = time.year
            systime.wYear = <WORD>v

            v = time.month
            systime.wMonth = <WORD>v

            v = time.day
            systime.wDay = <WORD>v

            if hasattr(time, 'hour'):
                v = getattr(time, 'hour')
            else:
                v = 0
            systime.wHour = <WORD>v

            if hasattr(time, 'minute'):
                v = getattr(time, 'minute')
            else:
                v = 0
            systime.wMinute = <WORD>v

            if hasattr(time, 'second'):
                v = getattr(time, 'second')
            else:
                v = 0
            systime.wSecond = <WORD>v

            if hasattr(time, 'microsecond'):
                v = getattr(time, 'microsecond')
            else:
                v = 0
            systime.wMilliseconds = <WORD>v

            ret = CWnd_SendMessage_L_P_L(self._cwnd, DTM_SETSYSTEMTIME, GDT_VALID, &systime)
            if ret == 0:
                pymRaiseWin32Err()

    def setFormat(self, fmt):
        cdef TCHAR *p
        p = PyUnicode_AsUnicode(fmt)
        ret = CWnd_SendMessage_L_P_L(self._cwnd, DTM_SETFORMAT, 0, p)
        if 0 == ret:
            pymRaiseWin32Err()

# Date and Time Picker styles

cdef extern from *:
    int DTS_UPDOWN, DTS_SHOWNONE, DTS_SHORTDATEFORMAT, DTS_LONGDATEFORMAT,
    int DTS_TIMEFORMAT, DTS_APPCANPARSE, DTS_RIGHTALIGN
    
cdef __init_datetimectrl_styles():
    ret = {
        "updown":DTS_UPDOWN,
        "shownone":DTS_SHOWNONE,
        "shortdateformat":DTS_SHORTDATEFORMAT,
        "longdateformat":DTS_LONGDATEFORMAT,
        "timeformat":DTS_TIMEFORMAT,
        "appcanparse":DTS_APPCANPARSE,
        "rightalig":DTS_RIGHTALIGN
    }
    ret.update(_std_styles)
    return ret

_datetimectrl_styles = __init_datetimectrl_styles()

cdef __init_datetime_ex_styles():
    ret = {
    }
    ret.update(_std_ex_styles)
    return ret

_datetimectrl_ex_styles = __init_datetime_ex_styles()


cdef class DateTimeCtrlStyle(WndStyle):
    def _initTable(self):
        self._styles = _datetimectrl_styles
        self._exStyles = _datetimectrl_ex_styles
    
# Date and Time Picker messages
cdef extern from *:
    int DTN_DATETIMECHANGE, DTN_USERSTRING, DTN_WMKEYDOWN, DTN_FORMAT
    int DTN_FORMATQUERY, DTN_DROPDOWN, DTN_CLOSEUP

cdef __init_datetimectrlmsg():
    ret = {
        "DATETIMECHANGE":(WM_NOTIFY, DTN_DATETIMECHANGE),
        "USERSTRING":(WM_NOTIFY, DTN_USERSTRING),
        "WMKEYDOWN":(WM_NOTIFY, DTN_WMKEYDOWN),
        "FORMAT":(WM_NOTIFY, DTN_FORMAT),
        "FORMATQUERY":(WM_NOTIFY, DTN_FORMATQUERY),
        "DROPDOWN":(WM_NOTIFY, DTN_DROPDOWN),
        "CLOSEUP":(WM_NOTIFY, DTN_CLOSEUP),
    }
    ret.update(_msgdict)
    return ret

_datetimectrlmsg = __init_datetimectrlmsg()


#
# Tab control
#

cdef extern from "pymwnd.h":
    # Controls
    void *new_ToolTip(object obj) except NULL
    int CToolTip_Create(void *o, void *parent, unsigned long style) except 0
    
    
    int TTM_ACTIVATE, TTM_ADDTOOL, TTM_ADJUSTRECT
    int TTM_DELTOOL, TTM_ENUMTOOLS, TTM_GETBUBBLESIZE
    int TTM_GETCURRENTTOOL, TTM_GETDELAYTIME
    int TTM_GETMARGIN, TTM_GETMAXTIPWIDTH, TTM_GETTEXT
    int TTM_GETTIPBKCOLOR, TTM_GETTIPTEXTCOLOR
    int TTM_GETTITLE, TTM_GETTOOLCOUNT, TTM_GETTOOLINFO
    int TTM_HITTEST, TTM_NEWTOOLRECT, TTM_POP, TTM_POPUP
    int TTM_RELAYEVENT, TTM_SETDELAYTIME, TTM_SETMARGIN
    int TTM_SETMAXTIPWIDTH, TTM_SETTIPBKCOLOR
    int TTM_SETTIPTEXTCOLOR, TTM_SETTITLE
    int TTM_SETTOOLINFO, TTM_SETWINDOWTHEME
    int TTM_TRACKACTIVATE, TTM_TRACKPOSITION, TTM_UPDATE
    int TTM_UPDATETIPTEXT, TTM_WINDOWFROMPOINT

    ctypedef struct TOOLINFO:
        UINT      cbSize
        UINT      uFlags
        HWND      hwnd
        UINT_PTR  uId
        RECT      rect
        HINSTANCE hinst
        TCHAR *lpszText
        LPARAM lParam

    int TTF_ABSOLUTE, TTF_CENTERTIP, TTF_IDISHWND, TTF_RTLREADING
    int TTF_SUBCLASS, TTF_TRACK, TTF_TRANSPARENT

cdef class _tooltip(_WndBase):
    cdef void *newInstance(self):
        return new_ToolTip(self)

    def _createToolTip(self, style, parent):
        cdef void *parentwnd
        parentwnd = NULL
        if parent:
            parentwnd = PyMFCPtr_AsVoidPtr(parent.cwnd)
        CToolTip_Create(self._cwnd, parentwnd, style.style)
        
        
    def activate(self, fActivate):
        CWnd_SendMessage_L_L_L(self._cwnd, TTM_ACTIVATE, fActivate, 0)
        
    def addTool(self, id, _WndBase wnd, rc, text, subclass=0):
        cdef TOOLINFO toolinfo

        memset(&toolinfo, 0, sizeof(toolinfo))
        toolinfo.cbSize = sizeof(toolinfo)
        toolinfo.uFlags = 0
        if subclass:
            toolinfo.uFlags = toolinfo.uFlags | TTF_SUBCLASS
        toolinfo.hwnd = wnd._getHwnd()
        toolinfo.uId = id
        toolinfo.rect.left = rc[0]
        toolinfo.rect.top = rc[1]
        toolinfo.rect.right = rc[2]
        toolinfo.rect.bottom = rc[3]
        toolinfo.hinst = NULL
        toolinfo.lpszText = PyUnicode_AsUnicode(text)
        
        CWnd_SendMessage_L_P_L_0(self._cwnd, TTM_ADDTOOL, 0, &toolinfo)
        
    def delTool(self, id, _WndBase wnd):
        cdef TOOLINFO toolinfo

        memset(&toolinfo, 0, sizeof(toolinfo))
        toolinfo.cbSize = sizeof(toolinfo)
        toolinfo.hwnd = wnd._getHwnd()
        toolinfo.uId = id
        
        CWnd_SendMessage_L_P_L(self._cwnd, TTM_DELTOOL, 0, &toolinfo)
    
    def getToolCount(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, TTM_GETTOOLCOUNT, 0, 0)
    
# ToolTip styles

cdef extern from *:
    int TTS_ALWAYSTIP, TTS_BALLOON, TTS_NOANIMATE, TTS_NOFADE, TTS_NOPREFIX

cdef __init_tooltip_styles():
    ret = {
        "alwaystip":TTS_ALWAYSTIP,
        "balloon":TTS_BALLOON,
        "noanimate":TTS_NOANIMATE,
        "nofade":TTS_NOFADE,
        "noprefix":TTS_NOPREFIX,
    }
    ret.update(_std_styles)
    return ret

_tooltip_styles = __init_tooltip_styles()

cdef __init_tooltip_ex_styles():
    ret = {
    }
    ret.update(_std_ex_styles)
    return ret

_tooltip_ex_styles = __init_tooltip_ex_styles()


cdef class ToolTipStyle(WndStyle):
    def _initTable(self):
        self._styles = _tooltip_styles
        self._exStyles = _tooltip_ex_styles
    
# ToolTip messages
cdef extern from *:
    int TTN_GETDISPINFO, TTN_LINKCLICK, TTN_NEEDTEXT
    int TTN_POP, TTN_SHOW

cdef __init_tooltipmsg():
    ret = {
        "GETDISPINFO":(WM_NOTIFY, TTN_GETDISPINFO),
        "LINKCLICK":(WM_NOTIFY, TTN_LINKCLICK),
        "WMKEYDOWN":(WM_NOTIFY, DTN_WMKEYDOWN),
        "NEEDTEXT":(WM_NOTIFY, TTN_NEEDTEXT),
        "POP":(WM_NOTIFY, TTN_POP),
        "SHOW":(WM_NOTIFY, TTN_SHOW),
    }
    ret.update(_msgdict)
    return ret

_tooltipmsg = __init_tooltipmsg()


#
# HotKey control
#
cdef extern from "pymwnd.h":
    # Controls
    void *new_HotKeyCtrl(object obj) except NULL
    int HKM_GETHOTKEY, HKM_SETHOTKEY
    int HOTKEYF_ALT, HOTKEYF_CONTROL, HOTKEYF_EXT, HOTKEYF_SHIFT
    
cdef class _hotkeyctrl(_WndBase):
    cdef void *newInstance(self):
        return new_HotKeyCtrl(self)

    def getHotKey(self):
        cdef LRESULT ret
        cdef BYTE mod
        cdef int alt, ctrl, shift, ext
        
        ret = CWnd_SendMessage_L_L_L(self._cwnd, HKM_GETHOTKEY, 0, 0) 
        vkey = LOBYTE(ret)
        mod = HIBYTE(ret)
        alt = ctrl = shift = ext = 0
        if mod & HOTKEYF_ALT: alt = 1
        if mod & HOTKEYF_CONTROL: ctrl = 1
        if mod & HOTKEYF_SHIFT: shift = 1
        if mod & HOTKEYF_EXT: ext = 1
        
        return (alt, ctrl, shift, ext, vkey)
        
        
    def setHotKey(self, alt, ctrl, shift, ext, key):
        cdef WPARAM wparam
        cdef WORD mod
        
        mod = 0
        if alt: mod = mod | HOTKEYF_ALT
        if ctrl: mod = mod | HOTKEYF_CONTROL
        if shift: mod = mod | HOTKEYF_SHIFT
        if ext: mod = mod | HOTKEYF_EXT
        
        CWnd_SendMessage_L_L_L(self._cwnd, HKM_SETHOTKEY, MAKEWORD(key, mod), 0) 

cdef __init_hotkeymsg():
    ret = {
        "CHANGE": (WM_COMMAND, EN_CHANGE),
    }
    ret.update(_msgdict)
    return ret
    
_hotkeymsg = __init_hotkeymsg()


