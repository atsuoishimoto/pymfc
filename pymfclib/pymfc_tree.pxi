# Tree control

cdef extern from "pymwnd.h":
    # types
    ctypedef void *HTREEITEM

    # Controls
    void *new_TreeView(object obj) except NULL

    # messages
    int TVM_CREATEDRAGIMAGE, TVM_DELETEITEM, TVM_EDITLABEL, TVM_ENDEDITLABELNOW
    int TVM_ENSUREVISIBLE, TVM_EXPAND, TVM_GETBKCOLOR, TVM_GETCOUNT
    int TVM_GETEDITCONTROL, TVM_GETIMAGELIST, TVM_GETINDENT, TVM_GETINSERTMARKCOLOR
    int TVM_GETISEARCHSTRING, TVM_GETITEM, TVM_GETITEMHEIGHT, TVM_GETITEMRECT
    int TVM_GETNEXTITEM, TVM_GETSCROLLTIME, TVM_GETTEXTCOLOR, TVM_GETTOOLTIPS
    int TVM_GETUNICODEFORMAT, TVM_GETVISIBLECOUNT, TVM_HITTEST, TVM_INSERTITEM
    int TVM_SELECTITEM, TVM_SETBKCOLOR, TVM_SETIMAGELIST, TVM_SETINDENT
    int TVM_SETINSERTMARK, TVM_SETINSERTMARKCOLOR, TVM_SETITEM, TVM_SETITEMHEIGHT
    int TVM_SETSCROLLTIME, TVM_SETTEXTCOLOR, TVM_SETTOOLTIPS, TVM_SETUNICODEFORMAT
    int TVM_SORTCHILDREN, TVM_SORTCHILDRENCB

    int TVE_COLLAPSE, TVE_EXPAND, TVE_TOGGLE, TVE_EXPANDPARTIAL, TVE_COLLAPSERESET

    int TVSIL_NORMAL, TVSIL_STATE


    int TVGN_ROOT, TVGN_NEXT, TVGN_PREVIOUS, TVGN_PARENT, TVGN_CHILD
    int TVGN_FIRSTVISIBLE, TVGN_NEXTVISIBLE, TVGN_PREVIOUSVISIBLE
    int TVGN_DROPHILITE, TVGN_CARET, TVGN_LASTVISIBLE


    int TVHT_NOWHERE, TVHT_ONITEMICON, TVHT_ONITEMLABEL, TVHT_ONITEM
    int TVHT_ONITEMINDENT, TVHT_ONITEMBUTTON, TVHT_ONITEMRIGHT, 
    int TVHT_ONITEMSTATEICON, TVHT_ABOVE, TVHT_BELOW, TVHT_TORIGHT, TVHT_TOLEFT




    HTREEITEM TVI_FIRST, TVI_LAST, TVI_ROOT, TVI_SORT 

    # TVITEMEX mask flags
    int TVIF_CHILDREN, TVIF_DI_SETITEM, TVIF_HANDLE, TVIF_IMAGE
    int TVIF_INTEGRAL, TVIF_PARAM, TVIF_SELECTEDIMAGE, TVIF_STATE
    int TVIF_TEXT

    # TVITEMEX item state flags
    int TVIS_BOLD, TVIS_CUT, TVIS_DROPHILITED, TVIS_EXPANDED, TVIS_EXPANDEDONCE,
    int TVIS_EXPANDPARTIAL, TVIS_SELECTED, TVIS_OVERLAYMASK, TVIS_STATEIMAGEMASK
    

cdef extern from *:
    
    ctypedef struct TVITEMEX:
        int mask
        HTREEITEM hItem
        int state
        int stateMask
        TCHAR *pszText
        int cchTextMax
        int iImage
        int iSelectedImage
        int cChildren
        LPARAM lParam
        int iIntegral
        
    ctypedef struct TVINSERTSTRUCT:
        HTREEITEM hParent
        HTREEITEM hInsertAfter
        TVITEMEX itemex

    ctypedef struct TVHITTESTINFO:
        POINT pt
        UINT flags
        HTREEITEM hItem

cdef class _tvitem:
    cdef TVITEMEX _item
    cdef object _text
    
    def __init__(self, *args, **kwargs):
        cdef _tvitem p

        l = len(args)
        if l == 0:
            pass
        elif l == 1:
            item = args[0]
            if isinstance(item, _tvitem):
                p = item
                self._item = p._item
                self._text = p._text
            else:
                raise TypeError("Invalid _tvitem")
        else:
            raise TypeError("Invalid _tvitem")
            
        for name, value in kwargs.items():
            setattr(self, name, value)


    def __call__(self, *args, **kwargs):
        ret = _tvitem(self, *args, **kwargs)
        return ret
        
    property hitem:
        def __get__(self):
            return PyMFCHandle_FromHandle(self._item.hItem)
            
        def __set__(self, value):
            self._item.hItem = PyMFCHandle_AsHandle(value)
            self._item.mask = self._item.mask | TVIF_HANDLE
    
    property bold:
        def __get__(self):
            return (self._item.state & TVIS_BOLD) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_BOLD
            else:
                self._item.state = self._item.state & ~TVIS_BOLD
            self._item.stateMask = self._item.stateMask | TVIS_BOLD
            self._item.mask = self._item.mask | TVIF_STATE
            
    property cut:
        def __get__(self):
            return (self._item.state & TVIS_CUT) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_CUT
            else:
                self._item.state = self._item.state & ~TVIS_CUT
            self._item.stateMask = self._item.stateMask | TVIS_CUT
            self._item.mask = self._item.mask | TVIF_STATE
        
    property drophilited:
        def __get__(self):
            return (self._item.state & TVIS_DROPHILITED) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_DROPHILITED
            else:
                self._item.state = self._item.state & ~TVIS_DROPHILITED
            self._item.stateMask = self._item.stateMask | TVIS_DROPHILITED
            self._item.mask = self._item.mask | TVIF_STATE
        
    property expanded:
        def __get__(self):
            return (self._item.state & TVIS_EXPANDED) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_EXPANDED
            else:
                self._item.state = self._item.state & ~TVIS_EXPANDED
            self._item.stateMask = self._item.stateMask | TVIS_EXPANDED
            self._item.mask = self._item.mask | TVIF_STATE
        
    property expandedonce:
        def __get__(self):
            return (self._item.state & TVIS_EXPANDEDONCE) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_EXPANDEDONCE
            else:
                self._item.state = self._item.state & ~TVIS_EXPANDEDONCE
            self._item.stateMask = self._item.stateMask | TVIS_EXPANDEDONCE
            self._item.mask = self._item.mask | TVIF_STATE
        
    property expandpartial:
        def __get__(self):
            return (self._item.state & TVIS_EXPANDPARTIAL) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_EXPANDPARTIAL
            else:
                self._item.state = self._item.state & ~TVIS_EXPANDPARTIAL
            self._item.stateMask = self._item.stateMask | TVIS_EXPANDPARTIAL
            self._item.mask = self._item.mask | TVIF_STATE
        
    property selected:
        def __get__(self):
            return (self._item.state & TVIS_SELECTED) != 0

        def __set__(self, value):
            if value:
                self._item.state = self._item.state | TVIS_SELECTED
            else:
                self._item.state = self._item.state & ~TVIS_SELECTED
            self._item.stateMask = self._item.stateMask | TVIS_SELECTED
            self._item.mask = self._item.mask | TVIF_STATE

    property overlayimage:
        def __get__(self):
            return ((self._item.state & TVIS_OVERLAYMASK) >> 8) & 0x0f

        def __set__(self, int value):
            self._item.state = (self._item.state & TVIS_OVERLAYMASK) | ((value << 8) & TVIS_OVERLAYMASK)
            self._item.stateMask = self._item.stateMask | TVIS_OVERLAYMASK
            self._item.mask = self._item.mask | TVIF_STATE

    property stateimage:
        def __get__(self):
            return ((self._item.state & TVIS_STATEIMAGEMASK) >> 12) & 0x0f

        def __set__(self, int value):
            self._item.state = (self._item.state & TVIS_STATEIMAGEMASK) | ((value << 12) & TVIS_STATEIMAGEMASK)
            self._item.stateMask = self._item.stateMask | TVIS_STATEIMAGEMASK
            self._item.mask = self._item.mask | TVIF_STATE
    
    property text:
        def __get__(self):
            return self._text

        def __set__(self, value):
            self._text = value
            self._item.pszText = PyUnicode_AsUnicode(self._text)
            self._item.cchTextMax = len(value)
            self._item.mask = self._item.mask | TVIF_TEXT
    
    property image:
        def __get__(self):
            return self._item.iImage
        
        def __set__(self, long value):
            self._item.iImage = value
            self._item.mask = self._item.mask | TVIF_IMAGE
    
    property selectedimage:
        def __get__(self):
            return self._item.iSelectedImage
        
        def __set__(self, long value):
            self._item.iSelectedImage = value
            self._item.mask = self._item.mask | TVIF_SELECTEDIMAGE

    property children:
        def __get__(self):
            return self._item.cChildren
        
        def __set__(self, long value):
            self._item.cChildren = value
            self._item.mask = self._item.mask | TVIF_CHILDREN

    property lparam:
        def __get__(self):
            return self._item.lParam
        
        def __set__(self, value):
            self._item.lParam = value
            self._item.mask = self._item.mask | TVIF_PARAM

    property integral:
        def __get__(self):
            return self._item.iIntegral
        
        def __set__(self, long value):
            self._item.iIntegral = value
            self._item.mask = self._item.mask | TVIF_INTEGRAL

cdef class _treeview(_WndBase):
    cdef object _image_normal, _image_state
    
    cdef void *newInstance(self):
        return new_TreeView(self)
    
    def setImageList(self, normal=None, state=None):
        cdef HIMAGELIST himg
        himg = NULL
        
        if normal is not None:
            if hasattr(normal, 'getHandle'):
                himg = PyMFCHandle_AsHandle(normal.getHandle())
            else:
                himg = PyMFCHandle_AsHandle(normal)
                
            CWnd_SendMessage_L_P_L(self._cwnd, TVM_SETIMAGELIST,
                TVSIL_NORMAL, himg)
            self._image_normal = normal
        if state is not None:
            if hasattr(state, 'getHandle'):
                himg = PyMFCHandle_AsHandle(state.getHandle())
            else:
                himg = PyMFCHandle_AsHandle(state)
            CWnd_SendMessage_L_P_L(self._cwnd, TVM_SETIMAGELIST,
                TVSIL_STATE, himg)
            self._image_state = state

    def setBkColor(self, color):
        CWnd_SendMessage_L_L_L(self._cwnd, TVM_SETBKCOLOR, 0, color)
        
    def setTextColor(self, color):
        CWnd_SendMessage_L_L_L(self._cwnd, TVM_SETTEXTCOLOR, 0, color)
        
    def setItemHeight(self, height):
        CWnd_SendMessage_L_L_L(self._cwnd, TVM_SETITEMHEIGHT, height, 0)
    
    def getItemHeight(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, TVM_GETITEMHEIGHT, 0, 0)
    
    def insert(self, _tvitem item, parent=None, after=None, first=0, last=1, root=0, sort=0):
        cdef TVINSERTSTRUCT ins
        cdef HTREEITEM p
        
        if parent:
            if isinstance(parent, _tvitem):
                p = PyMFCHandle_AsHandle(parent.hitem)
            else:
                p = PyMFCHandle_AsHandle(parent)
            ins.hParent = p
        else:
            ins.hParent = NULL
        
        if after:
            p = PyMFCHandle_AsHandle(after.hItem)
            ins.hInsertAfter = p
        elif first:
            ins.hInsertAfter = TVI_FIRST
        elif root:
            ins.hInsertAfter = TVI_ROOT
        elif sort:
            ins.hInsertAfter = TVI_SORT
        elif last:
            ins.hInsertAfter = TVI_LAST
        else:
            raise ValueError("Insert position is not specified")
    
        ins.itemex = item._item
        item._item.hItem = <HTREEITEM>CWnd_SendMessage_L_P_L_0(
                                self._cwnd, TVM_INSERTITEM, 0, &ins)
        return PyMFCHandle_FromHandle(item._item.hItem)
        
    def deleteItem(self, hitem=None, all=0):
        cdef HTREEITEM _hitem
        if all:
            _hitem = TVI_ROOT
        elif hitem:
            _hitem =  PyMFCHandle_AsHandle(hitem)
        else:
            raise ValueError("No item specified")

        return CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_DELETEITEM, 0, _hitem)


    def ensureVisible(self, hitem):
        CWnd_SendMessage_L_P_L(self._cwnd, TVM_ENSUREVISIBLE, 0, PyMFCHandle_AsHandle(hitem))
        
    def selectCaretItem(self, hitem, caret=1, drophilite=1):
        if hitem:
            CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_SELECTITEM, TVGN_CARET, PyMFCHandle_AsHandle(hitem))
        else:
            CWnd_SendMessage_L_L_L_0(self._cwnd, TVM_SELECTITEM, TVGN_CARET, 0)
            
    def selectDropHiliteItem(self, hitem):
        if hitem:
            CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_SELECTITEM, TVGN_DROPHILITE, PyMFCHandle_AsHandle(hitem))
        else:
            CWnd_SendMessage_L_L_L_0(self._cwnd, TVM_SELECTITEM, TVGN_DROPHILITE, 0)

    def editLabel(self, hitem):
        return CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_EDITLABEL, 0, PyMFCHandle_AsHandle(hitem))

    def _getEditControl(self, editcls):
        cdef HWND hwnd
        hwnd = <HWND>CWnd_SendMessage_L_L_L_0(self._cwnd, TVM_GETEDITCONTROL, 0, 0)
        ret = editcls()
        ret._subclassWindow(PyMFCHandle_FromHandle(hwnd), temp=1)
        return ret

    def expandItem(self, hitem, int collapse=0, int collapsereset=0, int expand=0, int expandpartial=0, int toggle=0):
        cdef int f
        f = 0
        if collapse:
            f = TVE_COLLAPSE
        elif collapsereset:
            f = TVE_COLLAPSERESET
        elif expand:
            f = TVE_EXPAND
        elif expandpartial:
            f = TVE_EXPANDPARTIAL
        elif toggle:
            f = TVE_TOGGLE
        else:
            raise ValueError("expandItem: action not specified")
        
        ret = CWnd_SendMessage_L_P_L(self._cwnd, TVM_EXPAND, f, PyMFCHandle_AsHandle(hitem))
        return ret

    def setItem(self, _tvitem item):
        CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_SETITEM, 0, &item._item)

    cdef object _getNextItem(self, void *cwnd, int flag, HTREEITEM hitem):
        cdef HTREEITEM ret
        ret = <HTREEITEM>CWnd_SendMessage_L_P_L(cwnd, TVM_GETNEXTITEM, flag, hitem)
        if ret == NULL:
            return None
        else:
            return PyMFCHandle_FromHandle(ret)

    def getRootItem(self):
        return self._getNextItem(self._cwnd, TVGN_ROOT, NULL)

    def getNextItem(self, hitem):
        return self._getNextItem(self._cwnd, TVGN_NEXT, PyMFCHandle_AsHandle(hitem))
        
    def getPrevItem(self, hitem):
        return self._getNextItem(self._cwnd, TVGN_PREVIOUS, PyMFCHandle_AsHandle(hitem))
        
    def getParentItem(self, hitem):
        return self._getNextItem(self._cwnd, TVGN_PARENT, PyMFCHandle_AsHandle(hitem))
        
    def getChildItem(self, hitem):
        return self._getNextItem(self._cwnd, TVGN_CHILD, PyMFCHandle_AsHandle(hitem))
        
    cdef object _getItemText(self, HTREEITEM hitem):
        cdef TVITEMEX p
        cdef long clen
        cdef TCHAR *buf
        
        memset(&p, 0, sizeof(p));
        p.hItem = hitem
        clen = 256
        while 1:
            buf = <TCHAR *>malloc(clen*sizeof(BYTE))
            if buf == NULL:
                raise MemoryError()
            
            p.mask = TVIF_TEXT;
            p.pszText = buf
            p.cchTextMax = clen

            if (clen - 1) != CWnd_SendMessage_L_P_L(self._cwnd, TVM_GETITEM, 0, &p):
                try:
                    s = _fromWideChar(p.pszText)
                except:
                    free(buf)
                    raise

                free(buf)
                return s

            free(buf)
            clen = clen + 256

    def getItemText(self, hitem):
        return self._getItemText(PyMFCHandle_AsHandle(hitem))
    
    def hitTest(self, pos, above=0, below=0, nowhere=0, onitem=0, 
            onitembutton=0, onitemicon=0, onitemindent=0,
            onitemlabel=0, onitemright=0, onitemstateicon=0,
            toleft=0, toright=0):
        
        cdef TVHITTESTINFO ht
        cdef HTREEITEM ret
        cdef int x, y
        x, y = pos
        
        ht.pt.x = x
        ht.pt.y = y
        ht.flags = 0
        
        if above:
            ht.flags = ht.flags | TVHT_ABOVE
        if below:
            ht.flags = ht.flags | TVHT_BELOW
        if nowhere:
            ht.flags = ht.flags | TVHT_NOWHERE
        if onitem:
            ht.flags = ht.flags | TVHT_ONITEM
        if onitembutton:
            ht.flags = ht.flags | TVHT_ONITEMBUTTON
        if onitemicon:
            ht.flags = ht.flags | TVHT_ONITEMICON
        if onitemindent:
            ht.flags = ht.flags | TVHT_ONITEMINDENT
        if onitemlabel:
            ht.flags = ht.flags | TVHT_ONITEMLABEL
        if onitemright:
            ht.flags = ht.flags | TVHT_ONITEMRIGHT
        if onitemstateicon:
            ht.flags = ht.flags | TVHT_ONITEMSTATEICON
        if toleft:
            ht.flags = ht.flags | TVHT_TOLEFT
        if toright:
            ht.flags = ht.flags | TVHT_TORIGHT
        
        ht.hItem = NULL
        
        ret = <HTREEITEM>CWnd_SendMessage_L_P_L(self._cwnd, TVM_HITTEST, 0, &ht)
        if ret == NULL:
            return
        
        return PyMFCHandle_FromHandle(ht.hItem)

    def getCaretItem(self):
        cdef HTREEITEM ret
        ret = <HTREEITEM>CWnd_SendMessage_L_L_L(self._cwnd, TVM_GETNEXTITEM, TVGN_CARET, 0)

        if ret == NULL:
            return
        return PyMFCHandle_FromHandle(ret)

    def getDropHilight(self):
        cdef HTREEITEM ret
        ret = <HTREEITEM>CWnd_SendMessage_L_L_L(self._cwnd, TVM_GETNEXTITEM, TVGN_DROPHILITE, 0)
        if ret == NULL:
            return
        return PyMFCHandle_FromHandle(ret)

    def getItemRect(self, hitem):
        cdef HTREEITEM ret, _hitem
        cdef RECT rc
        cdef HTREEITEM *p
        
        memset(&rc, 0, sizeof(rc))
        p = <HTREEITEM*>&rc
        p[0] = PyMFCHandle_AsHandle(hitem)
        if CWnd_SendMessage_L_P_L_0(self._cwnd, TVM_GETITEMRECT, 0, p):
            return (rc.left, rc.top, rc.right, rc.bottom)
        else:
            return None

# Tree styles
cdef extern from *:
    int TVS_HASBUTTONS, TVS_HASLINES, TVS_LINESATROOT, TVS_EDITLABELS
    int TVS_DISABLEDRAGDROP, TVS_SHOWSELALWAYS, TVS_RTLREADING
    int TVS_NOTOOLTIPS, TVS_CHECKBOXES, TVS_TRACKSELECT, TVS_SINGLEEXPAND
    int TVS_INFOTIP, TVS_FULLROWSELECT, TVS_NOSCROLL, TVS_NONEVENHEIGHT

cdef __init_treeview_styles():
    ret = {
        "hasbuttons":TVS_HASBUTTONS,
        "haslines":TVS_HASLINES,
        "linesatroot":TVS_LINESATROOT,
        "editlabels":TVS_EDITLABELS,
        "disabledragdrop":TVS_DISABLEDRAGDROP,
        "showselalways":TVS_SHOWSELALWAYS,
        "rtlreading":TVS_RTLREADING,
        "notooltips":TVS_NOTOOLTIPS,
        "checkboxes":TVS_CHECKBOXES,
        "trackselect":TVS_TRACKSELECT,
        "singleexpand":TVS_SINGLEEXPAND,
        "infotip":TVS_INFOTIP,
        "fullrowselect":TVS_FULLROWSELECT,
        "noscroll":TVS_NOSCROLL,
        "nonevenheight":TVS_NONEVENHEIGHT,
    }

    ret.update(_std_styles)
    return ret

_treeview_styles = __init_treeview_styles()


cdef class TreeViewStyle(WndStyle):
    def _initTable(self):
        self._styles = _treeview_styles
    


# Tree messages
cdef extern from *:
    int TVN_BEGINDRAG, TVN_BEGINLABELEDIT, TVN_BEGINRDRAG, TVN_DELETEITEM
    int TVN_ENDLABELEDIT, TVN_GETDISPINFO, TVN_GETINFOTIP, TVN_ITEMEXPANDED
    int TVN_ITEMEXPANDING, TVN_KEYDOWN, TVN_SELCHANGED, TVN_SELCHANGING
    int TVN_SETDISPINFO, TVN_SINGLEEXPAND

cdef __init_treeviewmsg():
    ret = {
        "BEGINDRAG":(WM_NOTIFY, TVN_BEGINDRAG),
        "BEGINLABELEDIT":(WM_NOTIFY, TVN_BEGINLABELEDIT),
        "BEGINRDRAG":(WM_NOTIFY, TVN_BEGINRDRAG),
        "ITEMDELETED":(WM_NOTIFY, TVN_DELETEITEM),
        "ENDLABELEDIT":(WM_NOTIFY, TVN_ENDLABELEDIT),
        "GETDISPINFO":(WM_NOTIFY, TVN_GETDISPINFO),
        "GETINFOTIP":(WM_NOTIFY, TVN_GETINFOTIP),
        "ITEMEXPANDED":(WM_NOTIFY, TVN_ITEMEXPANDED),
        "ITEMEXPANDING":(WM_NOTIFY, TVN_ITEMEXPANDING),
        "KEYPRESSED":(WM_NOTIFY, TVN_KEYDOWN),
        "SELCHANGED":(WM_NOTIFY, TVN_SELCHANGED),
        "SELCHANGING":(WM_NOTIFY, TVN_SELCHANGING),
        "SETDISPINFO":(WM_NOTIFY, TVN_SETDISPINFO),
        "SINGLEEXPAND":(WM_NOTIFY, TVN_SINGLEEXPAND),
    }
    ret.update(_msgdict)
    return ret

_treeviewmsg = __init_treeviewmsg()




