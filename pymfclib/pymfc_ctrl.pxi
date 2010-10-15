cdef extern from "pymwnd.h":
    # Controls
    void *new_CEdit(object obj) except NULL
    void *new_CStatic(object obj) except NULL
    void *new_CButton(object obj) except NULL
    void *new_CListBox(object obj) except NULL
    void *new_CComboBox(object obj) except NULL
    void *new_CScrollBar(object obj) except NULL
    
#
# edit control
#

cdef extern from *:
    int EM_SCROLL,EM_SETTABSTOPS, 
    int EM_GETSEL, EM_SETSEL, EM_GETRECT, EM_SETRECT, EM_SETRECTNP
    int EM_LINESCROLL, EM_SCROLLCARET, EM_GETMODIFY, EM_SETMODIFY
    int EM_GETLINECOUNT, EM_LINEINDEX, EM_SETHANDLE, EM_GETHANDLE, EM_GETTHUMB
    int EM_LINELENGTH, EM_REPLACESEL, EM_GETLINE, EM_LIMITTEXT, EM_CANUNDO
    int EM_UNDO, EM_FMTLINES, EM_LINEFROMCHAR
    int EM_SETPASSWORDCHAR, EM_EMPTYUNDOBUFFER, EM_GETFIRSTVISIBLELINE
    int EM_SETREADONLY, EM_SETWORDBREAKPROC, EM_GETWORDBREAKPROC
    int EM_GETPASSWORDCHAR, EM_SETMARGINS, EM_GETMARGINS, EM_SETLIMITTEXT
    int EM_GETLIMITTEXT, EM_POSFROMCHAR, EM_CHARFROMPOS, EM_SETIMESTATUS
    int EM_GETIMESTATUS
    int WBF_WORDWRAP, WBF_WORDBREAK, WBF_OVERFLOW, WBF_LEVEL1, WBF_LEVEL2, WBF_CUSTOM
    int WM_UNDO, WM_COPY, WM_CUT, WM_PASTE
    
cdef class _edit(_WndBase):
    cdef void *newInstance(self):
        return new_CEdit(self)

    def scroll(self, linedown=0, lineup=0, pageup=0, pagedown=0):
        cdef WPARAM wparam
        cdef LRESULT ret
        
        if linedown:
            wparam = SB_LINEDOWN
        elif lineup:
            wparam = SB_LINEUP
        elif pagedown:
            wparam = SB_PAGEDOWN
        elif pageup:
            wparam = SB_PAGEUP
            
        ret = CWnd_SendMessage_L_L_L(self._cwnd, EM_SCROLL, wparam, 0)
        return HIWORD(ret), LOWORD(ret)

    def lineScroll(self, cx=0, cy=0):
        ret = CWnd_SendMessage_L_L_L(self._cwnd, EM_LINESCROLL, cx, cy)
        return ret
        
    def setTabStop(self, tabstop):
        cdef DWORD _tabstop
        _tabstop = tabstop
        return CWnd_SendMessage_L_P_L(self._cwnd, EM_SETTABSTOPS, 1, &_tabstop)
        
    def setSel(self, pos, noscroll=True):
        cdef int f, t
        f = pos[0]
        t = pos[1]
        
        CWnd_SendMessage_L_L_L(self._cwnd, EM_SETSEL, f, t)
        
        if not noscroll:
            CWnd_SendMessage_L_L_L(self._cwnd, EM_SCROLLCARET, 0, 0)
    
    def getSel(self):
        cdef DWORD f, t
        
        CWnd_SendMessage_P_P_L(self._cwnd, EM_GETSEL, &f, &t)
        return (f, t)
        
    def posFromChar(self, nchar):
        cdef DWORD ret
        cdef WPARAM n
        n = nchar
        
        ret = CWnd_SendMessage_L_L_L(self._cwnd, EM_POSFROMCHAR, n, 0)
        return <SHORT>LOWORD(ret), <SHORT>HIWORD(ret)
        
    def canUndo(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, EM_CANUNDO, 0, 0)
        
    def undo(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, WM_UNDO, 0, 0)
        
    def copy(self):
        CWnd_SendMessage_L_L_L(self._cwnd, WM_COPY, 0, 0)
        
    def cut(self):
        CWnd_SendMessage_L_L_L(self._cwnd, WM_CUT, 0, 0)
        
    def paste(self):
        CWnd_SendMessage_L_L_L(self._cwnd, WM_PASTE, 0, 0)
    
    def limitText(self, int nchars=0):
        CWnd_SendMessage_L_L_L(self._cwnd, EM_LIMITTEXT, nchars, 0)
        
    def setLimitText(self, UINT nmax):
        CWnd_SendMessage_L_L_L(self._cwnd, EM_SETLIMITTEXT, nmax, 0)

    def getLimitText(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, EM_GETLIMITTEXT, 0, 0)


# Edit styles
cdef extern from *:
    int ES_LEFT, ES_CENTER, ES_RIGHT, ES_MULTILINE, ES_UPPERCASE, ES_LOWERCASE
    int ES_PASSWORD, ES_AUTOVSCROLL, ES_AUTOHSCROLL, ES_NOHIDESEL, ES_OEMCONVERT
    int ES_READONLY, ES_WANTRETURN, ES_NUMBER

cdef __init_edit_styles():
    ret = {
        "left":ES_LEFT, 
        "center":ES_CENTER, 
        "right":ES_RIGHT, 
        "multiline":ES_MULTILINE, 
        "uppercase":ES_UPPERCASE, 
        "lowercase":ES_LOWERCASE,
        "password":ES_PASSWORD, 
        "autovscroll":ES_AUTOVSCROLL, 
        "autohscroll":ES_AUTOHSCROLL, 
        "nohidesel":ES_NOHIDESEL, 
        "oemconvert":ES_OEMCONVERT,
        "readonly":ES_READONLY, 
        "wantreturn":ES_WANTRETURN, 
        "number":ES_NUMBER,
    }
    ret.update(_std_styles)
    return ret
_edit_styles = __init_edit_styles()

cdef class EditStyle(WndStyle):
    def _initTable(self):
        self._styles = _edit_styles

# Edit messages
cdef extern from *:
    int EN_SETFOCUS, EN_KILLFOCUS, EN_CHANGE, EN_UPDATE, EN_ERRSPACE
    int EN_MAXTEXT, EN_HSCROLL, EN_VSCROLL

cdef __init_editmsg():
    ret = {
        "SETFOCUS": (WM_COMMAND, EN_SETFOCUS),
        "KILLFOCUS": (WM_COMMAND, EN_KILLFOCUS),
        "CHANGE": (WM_COMMAND, EN_CHANGE),
        "UPDATE": (WM_COMMAND, EN_UPDATE),
        "ERRSPACE": (WM_COMMAND, EN_ERRSPACE),
        "MAXTEXT": (WM_COMMAND, EN_MAXTEXT),
        "HSCROLL": (WM_COMMAND, EN_HSCROLL),
        "VSCROLL": (WM_COMMAND, EN_VSCROLL)
    }
    ret.update(_msgdict)
    return ret
    
_editmsg = __init_editmsg()

# 
# Static control
#
cdef class _static(_WndBase):
    cdef void *newInstance(self):
        return new_CStatic(self)

# Static styles
cdef extern from *:
    int SS_LEFT, SS_CENTER, SS_RIGHT, SS_ICON, SS_BLACKRECT, SS_GRAYRECT
    int SS_WHITERECT, SS_BLACKFRAME, SS_GRAYFRAME, SS_WHITEFRAME, SS_USERITEM
    int SS_SIMPLE, SS_LEFTNOWORDWRAP, SS_OWNERDRAW, SS_BITMAP, SS_ENHMETAFILE
    int SS_ETCHEDHORZ, SS_ETCHEDVERT, SS_ETCHEDFRAME, SS_TYPEMASK, SS_NOPREFIX
    int SS_NOTIFY, SS_CENTERIMAGE, SS_RIGHTJUST, SS_REALSIZEIMAGE, SS_SUNKEN
    int SS_ENDELLIPSIS, SS_PATHELLIPSIS, SS_WORDELLIPSIS, SS_ELLIPSISMASK

cdef __init_static_styles():
    ret = {
        "left":SS_LEFT,
        "center":SS_CENTER,
        "right":SS_RIGHT,
        "icon":SS_ICON,
        "blackrect":SS_BLACKRECT,
        "grayrect":SS_GRAYRECT,
        "whiterect":SS_WHITERECT,
        "blackframe":SS_BLACKFRAME,
        "grayframe":SS_GRAYFRAME,
        "whiteframe":SS_WHITEFRAME,
        "useritem":SS_USERITEM,
        "simple":SS_SIMPLE,
        "leftnowordwrap":SS_LEFTNOWORDWRAP,
        "ownerdraw":SS_OWNERDRAW,
        "bitmap":SS_BITMAP,
        "enhmetafile":SS_ENHMETAFILE,
        "etchedhorz":SS_ETCHEDHORZ,
        "etchedvert":SS_ETCHEDVERT,
        "etchedframe":SS_ETCHEDFRAME,
        "typemask":SS_TYPEMASK,
        "noprefix":SS_NOPREFIX,
        "notify":SS_NOTIFY,
        "centerimage":SS_CENTERIMAGE,
        "rightjust":SS_RIGHTJUST,
        "realsizeimage":SS_REALSIZEIMAGE,
        "sunken":SS_SUNKEN,
        "endellipsis":SS_ENDELLIPSIS,
        "pathellipsis":SS_PATHELLIPSIS,
        "wordellipsis":SS_WORDELLIPSIS,
        "ellipsismask":SS_ELLIPSISMASK,
    }
    ret.update(_std_styles)
    return ret
    
_static_styles = __init_static_styles()

cdef class StaticStyle(WndStyle):
    def _initTable(self):
        self._styles = _static_styles

# Static messages
cdef extern from *:
    int STN_CLICKED, STN_DBLCLK, STN_ENABLE, STN_DISABLE

cdef __init_staticmsg():
    ret = {
        "CLICKED":(WM_COMMAND, STN_CLICKED),
        "DBLCLK":(WM_COMMAND, STN_DBLCLK),
        "ENABLE":(WM_COMMAND, STN_ENABLE),
        "DISABLE":(WM_COMMAND, STN_DISABLE),
    }
    ret.update(_msgdict)
    return ret
    
_staticmsg = __init_staticmsg()


#
# button 
#

cdef extern from *:
    int BM_GETCHECK, BM_SETCHECK, BM_GETSTATE, BM_SETSTATE
    int BM_SETSTYLE, BM_CLICK, BM_GETIMAGE, BM_SETIMAGE
    int BST_UNCHECKED, BST_CHECKED, BST_INDETERMINATE, BST_PUSHED, BST_FOCUS



cdef class _button(_WndBase):
    cdef void *newInstance(self):
        return new_CButton(self)

    def isChecked(self):
        cdef long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, BM_GETCHECK, 0, 0)
        if ret == BST_CHECKED:
            return 1
        return 0
        
    def setChecked(self, checked=0, indeterminate=0):
        cdef long f
        if checked:
            f = BST_CHECKED
        elif indeterminate:
            f = BST_INDETERMINATE
        else:
            f = BST_UNCHECKED
        CWnd_SendMessage_L_L_L(self._cwnd, BM_SETCHECK, f, 0)
        
    def isIndeterminate(self):
        cdef long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, BM_GETCHECK, 0, 0)
        if ret == BST_INDETERMINATE:
            return 1
        return 0

        
# Button styles
cdef extern from *:
    int BS_PUSHBUTTON, BS_DEFPUSHBUTTON, BS_CHECKBOX, BS_AUTOCHECKBOX,
    int BS_RADIOBUTTON, BS_3STATE, BS_AUTO3STATE, BS_GROUPBOX, BS_USERBUTTON,
    int BS_AUTORADIOBUTTON, BS_OWNERDRAW, BS_LEFTTEXT, BS_TEXT, BS_ICON,
    int BS_BITMAP, BS_LEFT, BS_RIGHT, BS_CENTER, BS_TOP, BS_BOTTOM, BS_VCENTER,
    int BS_PUSHLIKE, BS_MULTILINE, BS_NOTIFY, BS_FLAT, BS_RIGHTBUTTON,

cdef __init_button_styles():
    ret = {
        "pushbutton":BS_PUSHBUTTON,
        "defpushbutton":BS_DEFPUSHBUTTON,
        "checkbox":BS_CHECKBOX,
        "autocheckbox":BS_AUTOCHECKBOX,
        "radiobutton":BS_RADIOBUTTON,
        "tristate":BS_3STATE,
        "auto3state":BS_AUTO3STATE,
        "groupbox":BS_GROUPBOX,
        "userbutton":BS_USERBUTTON,
        "autoradiobutton":BS_AUTORADIOBUTTON,
        "ownerdraw":BS_OWNERDRAW,
        "lefttext":BS_LEFTTEXT,
        "text":BS_TEXT, 
        "icon":BS_ICON,
        "bitmap":BS_BITMAP,
        "left":BS_LEFT,
        "right":BS_RIGHT,
        "center":BS_CENTER,
        "top":BS_TOP,
        "bottom":BS_BOTTOM,
        "vcenter":BS_VCENTER,
        "pushlike":BS_PUSHLIKE,
        "multiline":BS_MULTILINE,
        "notify":BS_NOTIFY,
        "flat":BS_FLAT,
        "rightbutton":BS_RIGHTBUTTON,
    }
    ret.update(_std_styles)
    return ret
    
_button_styles = __init_button_styles()

cdef class ButtonStyle(WndStyle):
    def _initTable(self):
        self._styles = _button_styles

# Button messages
cdef extern from *:
    int BN_CLICKED, BN_PAINT, BN_HILITE, BN_UNHILITE, BN_DISABLE,
    int BN_DOUBLECLICKED, BN_PUSHED, BN_UNPUSHED, BN_DBLCLK,
    int BN_SETFOCUS, BN_KILLFOCUS,

cdef __init_buttonmsg():
    ret = {
        "CLICKED":(WM_COMMAND, BN_CLICKED),
        "PAINT":(WM_COMMAND, BN_PAINT),
        "HILITE":(WM_COMMAND, BN_HILITE),
        "UNHILITE":(WM_COMMAND, BN_UNHILITE),
        "DISABLE":(WM_COMMAND, BN_DISABLE),
        "DOUBLECLICKED":(WM_COMMAND, BN_DOUBLECLICKED),
        "PUSHED":(WM_COMMAND, BN_PUSHED),
        "UNPUSHED":(WM_COMMAND, BN_UNPUSHED),
        "DBLCLK":(WM_COMMAND, BN_DBLCLK),
        "SETFOCUS":(WM_COMMAND, BN_SETFOCUS),
        "KILLFOCUS":(WM_COMMAND, BN_KILLFOCUS),
    }
    ret.update(_msgdict)
    return ret
    
_buttonmsg = __init_buttonmsg()






#
# Listbox
#

cdef extern from *:
    int LB_ADDFILE, LB_ADDSTRING, LB_DELETESTRING, LB_DIR, LB_FINDSTRING
    int LB_FINDSTRINGEXACT, LB_GETANCHORINDEX, LB_GETCARETINDEX, LB_GETCOUNT
    int LB_GETCURSEL, LB_GETHORIZONTALEXTENT, LB_GETITEMDATA, LB_GETITEMHEIGHT
    int LB_GETITEMRECT, LB_GETLISTBOXINFO, LB_GETLOCALE, LB_GETSEL
    int LB_GETSELCOUNT, LB_GETSELITEMS, LB_GETTEXT, LB_GETTEXTLEN
    int LB_GETTOPINDEX, LB_INITSTORAGE, LB_INSERTSTRING, LB_ITEMFROMPOINT
    int LB_MSGMAX, LB_MULTIPLEADDSTRING, LB_RESETCONTENT, LB_SELECTSTRING
    int LB_SELITEMRANGE, LB_SELITEMRANGEEX, LB_SETANCHORINDEX, LB_SETCARETINDEX
    int LB_SETCOLUMNWIDTH, LB_SETCOUNT, LB_SETCURSEL, LB_SETHORIZONTALEXTENT
    int LB_SETITEMDATA, LB_SETITEMHEIGHT, LB_SETLOCALE, LB_SETSEL
    int LB_SETTABSTOPS, LB_SETTOPINDEX

    int LB_OKAY, LB_ERR, LB_ERRSPACE


cdef class _listbox(_WndBase):
    cdef void *newInstance(self):
        return new_CListBox(self)

    def insertItem(self, int index=-1, text=None):
        cdef unsigned long ret
        if not text:
            text = unicode("")

        ret = CWnd_SendMessage_L_P_L(self._cwnd, LB_INSERTSTRING, index, PyUnicode_AsUnicode(text))
        if ret == LB_ERR or ret == LB_ERRSPACE:
            pymRaiseWin32Err()
        return ret
        
    def addItem(self, text):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_P_L(self._cwnd, LB_ADDSTRING, 0, PyUnicode_AsUnicode(text))
        if ret == LB_ERR or ret == LB_ERRSPACE:
            pymRaiseWin32Err()
        return ret
        
    def setItemData(self, int index, int data):
        if LB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, LB_SETITEMDATA, index, data):
            pymRaiseWin32Err()
        
    def getItemData(self, int index):
        return CWnd_SendMessage_L_L_L(self._cwnd, LB_GETITEMDATA, index, 0)

    def deleteString(self, int index):
        if LB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, LB_DELETESTRING, index, 0):
            pymRaiseWin32Err()

    def resetContent(self):
        if LB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, LB_RESETCONTENT, 0, 0):
            pymRaiseWin32Err()

    def getItemCount(self):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, LB_GETCOUNT, 0, 0)
        if ret == LB_ERR:
            pymRaiseWin32Err()
        return ret
        
    def getCurSel(self):
        cdef long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, LB_GETCURSEL, 0, 0)
        if ret == LB_ERR:
            return None
        return ret
        
    def setCurSel(self, int index):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, LB_SETCURSEL, index, 0)
        if (index != -1) and (ret == LB_ERR):
            pymRaiseWin32Err()
        return ret
        
    def selectString(self, start, string):
        cdef unsigned long ret
        cdef TCHAR *p
        p = PyUnicode_AsUnicode(string)
        ret = CWnd_SendMessage_L_P_L(self._cwnd, LB_SELECTSTRING, start, p)
        if ret == LB_ERR:
            return -1
        else:
            return ret
        
    def getItemFromPos(self, pos):
        cdef int x, y
        cdef LRESULT lresult
        
        x, y = pos
        lresult = CWnd_SendMessage_L_L_L(self._cwnd, LB_ITEMFROMPOINT, 0, MAKELPARAM(x, y))
        return LOWORD(lresult), HIWORD(lresult)
        
    def getItemRect(self, idx):
        cdef RECT rc
        cdef LRESULT lresult

        lresult = CWnd_SendMessage_L_P_L(self._cwnd, LB_GETITEMRECT, idx, &rc)
        if lresult == LB_ERR:
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.bottom, rc.right)
        
    def getItemText(self, idx):
        cdef size
        cdef TCHAR *p
        
        size = CWnd_SendMessage_L_L_L(self._cwnd, LB_GETTEXTLEN, idx, 0)
        if size == LB_ERR:
            pymRaiseWin32Err()
        if not size:
            return unicode("")

        p = <TCHAR*>malloc((size+1)*sizeof(TCHAR))
        if p == NULL:
            raise MemoryError()
        try:
            size = CWnd_SendMessage_L_P_L(self._cwnd, LB_GETTEXT, idx, p)
            ret = _fromWideChar(p)
        finally:
            free(p)
        return ret
        

# ListBox styles
cdef extern from *:
    int LBS_NOTIFY, LBS_SORT, LBS_NOREDRAW, LBS_MULTIPLESEL, LBS_OWNERDRAWFIXED,
    int LBS_OWNERDRAWVARIABLE, LBS_HASSTRINGS, LBS_USETABSTOPS, LBS_NOINTEGRALHEIGHT,
    int LBS_MULTICOLUMN, LBS_WANTKEYBOARDINPUT, LBS_EXTENDEDSEL, LBS_DISABLENOSCROLL,
    int LBS_NODATA, LBS_NOSEL,

cdef __init_listbox_styles():
    ret = {
        "notify":LBS_NOTIFY,
        "sort":LBS_SORT,
        "noredraw":LBS_NOREDRAW,
        "multiplesel":LBS_MULTIPLESEL,
        "ownerdrawfixed":LBS_OWNERDRAWFIXED,
        "ownerdrawvariable":LBS_OWNERDRAWVARIABLE,
        "hasstrings":LBS_HASSTRINGS,
        "usetabstops":LBS_USETABSTOPS,
        "nointegralheight":LBS_NOINTEGRALHEIGHT,
        "multicolumn":LBS_MULTICOLUMN,
        "wantkeyboardinput":LBS_WANTKEYBOARDINPUT,
        "extendedsel":LBS_EXTENDEDSEL,
        "disablenoscroll":LBS_DISABLENOSCROLL,
        "nodata":LBS_NODATA,
        "nosel":LBS_NOSEL,
    }
    ret.update(_std_styles)
    return ret
    
_listbox_styles = __init_listbox_styles()

cdef class ListBoxStyle(WndStyle):
    def _initTable(self):
        self._styles = _listbox_styles

# ListBox messages
cdef extern from *:
    int LBN_ERRSPACE, LBN_SELCHANGE, LBN_DBLCLK, LBN_SELCANCEL, 
    int LBN_SETFOCUS, LBN_KILLFOCUS, 

cdef __init_listboxmsg():
    ret = {
        "ERRSPACE":(WM_COMMAND, LBN_ERRSPACE),
        "SELCHANGE":(WM_COMMAND, LBN_SELCHANGE),
        "DBLCLK":(WM_COMMAND, LBN_DBLCLK),
        "SELCANCEL":(WM_COMMAND, LBN_SELCANCEL),
        "SETFOCUS":(WM_COMMAND, LBN_SETFOCUS),
        "KILLFOCUS":(WM_COMMAND, LBN_KILLFOCUS),
    }
    ret.update(_msgdict)
    return ret
    
_listboxmsg = __init_listboxmsg()


#
# ComboBox
#

cdef extern from *:
    int CB_GETEDITSEL, CB_LIMITTEXT, CB_SETEDITSEL, CB_ADDSTRING
    int CB_DELETESTRING, CB_DIR, CB_GETCOUNT, CB_GETCURSEL, CB_GETLBTEXT
    int CB_GETLBTEXTLEN, CB_INSERTSTRING, CB_RESETCONTENT, CB_FINDSTRING
    int CB_SELECTSTRING, CB_SETCURSEL, CB_SHOWDROPDOWN, CB_GETITEMDATA
    int CB_SETITEMDATA, CB_GETDROPPEDCONTROLRECT, CB_SETITEMHEIGHT
    int CB_GETITEMHEIGHT, CB_SETEXTENDEDUI, CB_GETEXTENDEDUI, CB_GETDROPPEDSTATE
    int CB_FINDSTRINGEXACT, CB_SETLOCALE, CB_GETLOCALE, CB_GETTOPINDEX
    int CB_SETTOPINDEX, CB_GETHORIZONTALEXTENT, CB_SETHORIZONTALEXTENT
    int CB_GETDROPPEDWIDTH, CB_SETDROPPEDWIDTH, CB_INITSTORAGE
    int CB_ERR, CB_ERRSPACE

cdef class _combobox(_WndBase):
    cdef void *newInstance(self):
        return new_CComboBox(self)
    
    def insertItem(self, int index=-1, text=None):
        cdef unsigned long ret
        if not text:
            text = unicode("")

        ret = CWnd_SendMessage_L_P_L(self._cwnd, CB_INSERTSTRING, index, PyUnicode_AsUnicode(text))
        if ret == CB_ERR or ret == CB_ERRSPACE:
            pymRaiseWin32Err()
        return ret
        
    def addItem(self, text):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_P_L(self._cwnd, CB_ADDSTRING, 0, PyUnicode_AsUnicode(text))
        if ret == CB_ERR or ret == CB_ERRSPACE:
            pymRaiseWin32Err()
        return ret
        
    def setItemData(self, int index, int data):
        if CB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, CB_SETITEMDATA, index, data):
            pymRaiseWin32Err()
        
    def getItemData(self, int index):
        return CWnd_SendMessage_L_L_L(self._cwnd, CB_GETITEMDATA, index, 0)

    def deleteString(self, int index):
        if CB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, CB_DELETESTRING, index, 0):
            pymRaiseWin32Err()

    def resetContent(self):
        if CB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, CB_RESETCONTENT, 0, 0):
            pymRaiseWin32Err()

    def getItemCount(self):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, CB_GETCOUNT, 0, 0)
        if ret == CB_ERR:
            pymRaiseWin32Err()
        return ret
        
    def getCurSel(self):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, CB_GETCURSEL, 0, 0)
        if ret == CB_ERR:
            return None
        return ret
        
    def setCurSel(self, int index):
        cdef unsigned long ret
        ret = CWnd_SendMessage_L_L_L(self._cwnd, CB_SETCURSEL, index, 0)
        if (index != -1) and (ret == CB_ERR):
            pymRaiseWin32Err()
        return ret
        
    def selectString(self, start, string):
        cdef unsigned long ret
        cdef TCHAR *p
        p = PyUnicode_AsUnicode(string)
        ret = CWnd_SendMessage_L_P_L(self._cwnd, CB_SELECTSTRING, start, p)
        if ret == CB_ERR:
            return -1
        else:
            return ret
        
    def getDroppedState(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, CB_GETDROPPEDSTATE, 0, 0)
        
    def getEditSel(self):
        cdef unsigned long start, end
        CWnd_SendMessage_P_P_L(self._cwnd, CB_GETEDITSEL, &start, &end)
        return (start, end)

    def setEditSel(self, start, end):
        CWnd_SendMessage_L_L_L(self._cwnd, CB_SETEDITSEL, 0, MAKELPARAM(start, end))
        return (start, end)

    def setExtendedUI(self, int extended):
        if CB_ERR == CWnd_SendMessage_L_L_L(self._cwnd, CB_SETEXTENDEDUI, extended, 0):
            pymRaiseWin32Err()

    def showDropDown(self, int show):
        CWnd_SendMessage_L_L_L(self._cwnd, CB_SHOWDROPDOWN, show, 0)
        
    def getLBText(self, idx):
        cdef size
        cdef TCHAR *p
        
        size = CWnd_SendMessage_L_L_L(self._cwnd, CB_GETLBTEXTLEN, idx, 0)
        if size == CB_ERR:
            pymRaiseWin32Err()
        if not size:
            return unicode("")

        p = <TCHAR*>malloc((size+1)*sizeof(TCHAR))
        if p == NULL:
            raise MemoryError()
        try:
            size = CWnd_SendMessage_L_P_L(self._cwnd, CB_GETLBTEXT, idx, p)
            ret = _fromWideChar(p)
        finally:
            free(p)
        return ret
        
    def limitText(self, int nmaxchars):
        return CWnd_SendMessage_L_L_L(self._cwnd, CB_LIMITTEXT, nmaxchars, 0)
        
# ComboBox styles
cdef extern from *:
    int CBS_SIMPLE, CBS_DROPDOWN, CBS_DROPDOWNLIST, CBS_OWNERDRAWFIXED
    int CBS_OWNERDRAWVARIABLE, CBS_AUTOHSCROLL, CBS_OEMCONVERT, CBS_SORT
    int CBS_HASSTRINGS, CBS_NOINTEGRALHEIGHT, CBS_DISABLENOSCROLL
    int CBS_UPPERCASE, CBS_LOWERCASE

cdef __init_combobox_styles():
    ret = {
        "simple":CBS_SIMPLE,
        "dropdown":CBS_DROPDOWN,
        "dropdownlist":CBS_DROPDOWNLIST,
        "ownerdrawfixed":CBS_OWNERDRAWFIXED,
        "ownerdrawvariable":CBS_OWNERDRAWVARIABLE,
        "autohscroll":CBS_AUTOHSCROLL,
        "oemconvert":CBS_OEMCONVERT,
        "sort":CBS_SORT,
        "hasstrings":CBS_HASSTRINGS,
        "nointegralheight":CBS_NOINTEGRALHEIGHT,
        "disablenoscroll":CBS_DISABLENOSCROLL,
        "uppercase":CBS_UPPERCASE,
        "lowercase":CBS_LOWERCASE,
    }
    ret.update(_std_styles)
    return ret
    
_combobox_styles = __init_combobox_styles()

cdef class ComboBoxStyle(WndStyle):
    def _initTable(self):
        self._styles = _combobox_styles

# ComboBox messages
cdef extern from *:
    int CBN_ERRSPACE, CBN_SELCHANGE, CBN_DBLCLK, CBN_SETFOCUS
    int CBN_KILLFOCUS, CBN_EDITCHANGE, CBN_EDITUPDATE, CBN_DROPDOWN
    int CBN_CLOSEUP, CBN_SELENDOK, CBN_SELENDCANCEL, 

cdef __init_comboboxmsg():
    ret = {
        "ERRSPACE":(WM_COMMAND, CBN_ERRSPACE),
        "SELCHANGE":(WM_COMMAND, CBN_SELCHANGE),
        "DBLCLK":(WM_COMMAND, CBN_DBLCLK),
        "SETFOCUS":(WM_COMMAND, CBN_SETFOCUS),
        "KILLFOCUS":(WM_COMMAND, CBN_KILLFOCUS),
        "EDITCHANGE":(WM_COMMAND, CBN_EDITCHANGE),
        "EDITUPDATE":(WM_COMMAND, CBN_EDITUPDATE),
        "DROPDOWN":(WM_COMMAND, CBN_DROPDOWN),
        "CLOSEUP":(WM_COMMAND, CBN_CLOSEUP),
        "SELENDOK":(WM_COMMAND, CBN_SELENDOK),
        "SELENDCANCEL":(WM_COMMAND, CBN_SELENDCANCEL),
    }
    ret.update(_msgdict)
    return ret
    
_comboboxmsg = __init_comboboxmsg()



#
# ScrollBar
#

cdef class _scrollbar(_WndBase):
    cdef void *newInstance(self):
        return new_CScrollBar(self)


# ScrollBar styles
cdef extern from *:
    int SBS_BOTTOMALIGN, SBS_HORZ, SBS_LEFTALIGN, SBS_RIGHTALIGN
    int SBS_SIZEBOX, SBS_SIZEBOXBOTTOMRIGHTALIGN, SBS_SIZEBOXTOPLEFTALIGN
    int SBS_SIZEGRIP, SBS_TOPALIGN, SBS_VERT

cdef __init_scrollbar_styles():
    ret = {
        "bottomalign":SBS_BOTTOMALIGN,
        "horz":SBS_HORZ,
        "leftalign":SBS_LEFTALIGN,
        "rightalign":SBS_RIGHTALIGN,
        "sizebox":SBS_SIZEBOX,
        "sizeboxbottomrightalign":SBS_SIZEBOXBOTTOMRIGHTALIGN,
        "sizeboxtopleftalign":SBS_SIZEBOXTOPLEFTALIGN,
        "sizegrip":SBS_SIZEGRIP,
        "topalign":SBS_TOPALIGN,
        "vert":SBS_VERT,
    }
    ret.update(_std_styles)
    return ret
    
_scrollbar_styles = __init_scrollbar_styles()

cdef class ScrollBarStyle(WndStyle):
    def _initTable(self):
        self._styles = _scrollbar_styles

cdef __init_scrollbarmsg():
    ret = {}
    ret.update(_msgdict)
    return ret
    
_scrollbarmsg = __init_scrollbarmsg()

