# ListView control

cdef extern from "pymwnd.h":
    # Controls
    void *new_ListView(object obj) except NULL

    int LVM_APPROXIMATEVIEWRECT, LVM_ARRANGE, LVM_CREATEDRAGIMAGE
    int LVM_DELETEALLITEMS, LVM_DELETECOLUMN, LVM_DELETEITEM, LVM_EDITLABEL
    int LVM_ENSUREVISIBLE, LVM_FINDITEM, LVM_GETBKCOLOR, LVM_GETBKIMAGE
    int LVM_GETCALLBACKMASK, LVM_GETCOLUMN, LVM_GETCOLUMNORDERARRAY
    int LVM_GETCOLUMNWIDTH, LVM_GETCOUNTPERPAGE, LVM_GETEDITCONTROL
    int LVM_GETEXTENDEDLISTVIEWSTYLE, LVM_GETHEADER, LVM_GETHOTCURSOR
    int LVM_GETHOTITEM, LVM_GETHOVERTIME, LVM_GETIMAGELIST, LVM_GETISEARCHSTRING
    int LVM_GETITEM, LVM_GETITEMCOUNT, LVM_GETITEMPOSITION, LVM_GETITEMRECT
    int LVM_GETITEMSPACING, LVM_GETITEMSTATE, LVM_GETITEMTEXT, LVM_GETNEXTITEM
    int LVM_GETNUMBEROFWORKAREAS, LVM_GETORIGIN, LVM_GETSELECTEDCOUNT
    int LVM_GETSELECTIONMARK, LVM_GETSTRINGWIDTH, LVM_GETSUBITEMRECT
    int LVM_GETTEXTBKCOLOR, LVM_GETTEXTCOLOR, LVM_GETTOOLTIPS, LVM_GETTOPINDEX
    int LVM_GETUNICODEFORMAT, LVM_GETVIEWRECT, LVM_GETWORKAREAS, LVM_HITTEST
    int LVM_INSERTCOLUMN, LVM_INSERTITEM, LVM_REDRAWITEMS, LVM_SCROLL
    int LVM_SETBKCOLOR, LVM_SETBKIMAGE, LVM_SETCALLBACKMASK, LVM_SETCOLUMN
    int LVM_SETCOLUMNORDERARRAY, LVM_SETCOLUMNWIDTH, LVM_SETEXTENDEDLISTVIEWSTYLE
    int LVM_SETHOTCURSOR, LVM_SETHOTITEM, LVM_SETHOVERTIME, LVM_SETICONSPACING
    int LVM_SETIMAGELIST, LVM_SETITEM, LVM_SETITEMCOUNT, LVM_SETITEMPOSITION
    int LVM_SETITEMPOSITION32, LVM_SETITEMSTATE, LVM_SETITEMTEXT
    int LVM_SETSELECTIONMARK, LVM_SETTEXTBKCOLOR, LVM_SETTEXTCOLOR
    int LVM_SETTOOLTIPS, LVM_SETUNICODEFORMAT, LVM_SETWORKAREAS
    int LVM_SORTITEMS, LVM_SUBITEMHITTEST, LVM_UPDATE

    int LVSIL_NORMAL, LVSIL_SMALL, LVSIL_STATE

    int LVNI_ALL, LVNI_ABOVE, LVNI_BELOW, LVNI_TOLEFT, LVNI_TORIGHT
    int LVNI_CUT, LVNI_DROPHILITED, LVNI_FOCUSED, LVNI_SELECTED

cdef extern from *:
    # LVITEM mask flags
    int LVIF_TEXT, LVIF_IMAGE, LVIF_INDENT, LVIF_NORECOMPUTE
    int LVIF_PARAM, LVIF_STATE, LVIF_DI_SETITEM

    # LVITEM mask states
    int LVIS_ACTIVATING, LVIS_CUT, LVIS_DROPHILITED
    int LVIS_FOCUSED, LVIS_SELECTED, LVIS_OVERLAYMASK
    int LVIS_STATEIMAGEMASK

    ctypedef struct LVITEM:
        int mask
        int iItem
        int iSubItem
        int state
        int stateMask
        TCHAR *pszText
        int cchTextMax
        int iImage
        unsigned long lParam
        int iIndent

    void ListView_SetExtendedListViewStyleEx(HWND hwndLV, DWORD dwExMask, DWORD dwExStyle) nogil



cdef class _lvitem:
    cdef LVITEM _item
    cdef object _text

    def __init__(self, *args, **kwargs):
        cdef _lvitem p

        l = len(args)
        if l == 0:
            pass
        elif l == 1:
            item = args[0]
            if isinstance(item, _lvitem):
                p = item
                self._item = p._item
                self._text = p._text
            else:
                raise TypeError("Invalid _lvitem")
        else:
            raise TypeError("Invalid _lvitem")
            
        for name, value in kwargs.items():
            setattr(self, name, value)
        
    property item:
        def __get__(self):
            return self._item.iItem
        def __set__(self, unsigned long value):
            self._item.iItem = value
    
    property subitem:
        def __get__(self):
            return self._item.iSubItem
        def __set__(self, unsigned long value):
            self._item.iSubItem = value

    property state:
        def __get__(self):
            return self._item.state
        def __set__(self, unsigned long value):
            self._item.state = value
        
    property statemask:
        def __get__(self):
            return self._item.stateMask
        def __set__(self, unsigned long value):
            self._item.stateMask = value
        

    property activating:
        def __get__(self):
            return self._item.state & LVIS_ACTIVATING != 0
        def __set__(self, value):
            if value:
                self._item.state = self._item.state | LVIS_ACTIVATING
            else:
                self._item.state = self._item.state & ~LVIS_ACTIVATING
            self._item.stateMask = self._item.stateMask | LVIS_ACTIVATING
            self._item.mask = self._item.mask | LVIF_STATE

    property cut:
        def __get__(self):
            return self._item.state & LVIS_CUT != 0
        def __set__(self, value):
            if value:
                self._item.state = self._item.state | LVIS_CUT
            else:
                self._item.state = self._item.state & ~LVIS_CUT
            self._item.stateMask = self._item.stateMask | LVIS_CUT
            self._item.mask = self._item.mask | LVIF_STATE

    property drophilited:
        def __get__(self):
            return self._item.state & LVIS_DROPHILITED != 0
        def __set__(self, value):
            if value:
                self._item.state = self._item.state | LVIS_DROPHILITED
            else:
                self._item.state = self._item.state & ~LVIS_DROPHILITED
            self._item.stateMask = self._item.stateMask | LVIS_DROPHILITED
            self._item.mask = self._item.mask | LVIF_STATE

    property focused:
        def __get__(self):
            return self._item.state & LVIS_FOCUSED != 0
        def __set__(self, value):
            if value:
                self._item.state = self._item.state | LVIS_FOCUSED
            else:
                self._item.state = self._item.state & ~LVIS_FOCUSED
            self._item.stateMask = self._item.stateMask | LVIS_FOCUSED
            self._item.mask = self._item.mask | LVIF_STATE

    property selected:
        def __get__(self):
            return self._item.state & LVIS_SELECTED != 0
        def __set__(self, value):
            if value:
                self._item.state = self._item.state | LVIS_SELECTED
            else:
                self._item.state = self._item.state & ~LVIS_SELECTED
            self._item.stateMask = self._item.stateMask | LVIS_SELECTED
            self._item.mask = self._item.mask | LVIF_STATE

    property overlayImage:
        def __get__(self):
            return ((self._item.state & LVIS_OVERLAYMASK) >> 8) & 0x0f

        def __set__(self, int value):
            self._item.state = (self._item.state & LVIS_OVERLAYMASK) | ((value << 8) & LVIS_OVERLAYMASK)
            self._item.stateMask = self._item.stateMask | LVIS_OVERLAYMASK
            self._item.mask = self._item.mask | LVIF_STATE

    property stateimage:
        def __get__(self):
            return ((self._item.state & LVIS_STATEIMAGEMASK) >> 12) & 0x0f

        def __set__(self, int value):
            self._item.state = (self._item.state & LVIS_STATEIMAGEMASK) | ((value << 12) & LVIS_STATEIMAGEMASK)
            self._item.stateMask = self._item.stateMask | LVIS_STATEIMAGEMASK
            self._item.mask = self._item.mask | LVIF_STATE

    property text:
        def __get__(self):
            return self._text

        def __set__(self, value):
            self._text = value
            self._item.pszText = PyUnicode_AsUnicode(self._text)
            self._item.cchTextMax = len(value)
            self._item.mask = self._item.mask | LVIF_TEXT

    property image:
        def __get__(self):
            return self._item.iImage
        
        def __set__(self, unsigned long value):
            self._item.iImage = value
            self._item.mask = self._item.mask | LVIF_IMAGE

    property lparam:
        def __get__(self):
            return self._item.lParam
        
        def __set__(self, unsigned long value):
            self._item.lParam = value
            self._item.mask = self._item.mask | LVIF_PARAM

    property indent:
        def __get__(self):
            return self._item.iIndent
        
        def __set__(self, unsigned long value):
            self._item.iIndent = value
            self._item.mask = self._item.mask | LVIF_INDENT


cdef extern from *:
    int LVCF_FMT, LVCF_IMAGE, LVCF_ORDER, LVCF_SUBITEM
    int LVCF_TEXT, LVCF_WIDTH

    int LVCFMT_BITMAP_ON_RIGHT, LVCFMT_CENTER, LVCFMT_COL_HAS_IMAGES
    int LVCFMT_IMAGE, LVCFMT_LEFT, LVCFMT_RIGHT

    ctypedef struct LVCOLUMN:
        int mask
        int fmt
        int cx
        TCHAR *pszText
        int cchTextMax
        int iSubItem
        int iImage
        int iOrder

cdef class _lvcolumn:
    cdef LVCOLUMN _column
    cdef object _text

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    property bitmap_on_right:
        def __get__(self):
            return self._column.fmt & LVCFMT_BITMAP_ON_RIGHT != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_BITMAP_ON_RIGHT
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_BITMAP_ON_RIGHT
            self._column.mask = self._column.mask | LVCF_FMT

    property center:
        def __get__(self):
            return self._column.fmt & LVCFMT_CENTER != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_CENTER
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_CENTER
            self._column.mask = self._column.mask | LVCF_FMT

    property col_has_images:
        def __get__(self):
            return self._column.fmt & LVCFMT_COL_HAS_IMAGES != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_COL_HAS_IMAGES
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_COL_HAS_IMAGES
            self._column.mask = self._column.mask | LVCF_FMT

    property col_disp_image:
        def __get__(self):
            return self._column.fmt & LVCFMT_IMAGE != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_IMAGE
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_IMAGE
            self._column.mask = self._column.mask | LVCF_FMT

    property left:
        def __get__(self):
            return self._column.fmt & LVCFMT_LEFT != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_LEFT
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_LEFT
            self._column.mask = self._column.mask | LVCF_FMT

    property right:
        def __get__(self):
            return self._column.fmt & LVCFMT_RIGHT != 0
        def __set__(self, value):
            if value:
                self._column.fmt = self._column.fmt | LVCFMT_RIGHT
            else:
                self._column.fmt = self._column.fmt & ~LVCFMT_RIGHT
            self._column.mask = self._column.mask | LVCF_FMT

    property cx:
        def __get__(self):
            return self._column.cx
        def __set__(self, value):
            self._column.cx = value
            self._column.mask = self._column.mask | LVCF_WIDTH

    property text:
        def __get__(self):
            return self._text
        def __set__(self, value):
            self._text = value
            self._column.pszText = PyUnicode_AsUnicode(self._text)
            self._column.cchTextMax = len(value)
            self._column.mask = self._column.mask | LVCF_TEXT

    property subitem:
        def __get__(self):
            return self._column.iSubItem
        def __set__(self, value):
            self._column.iSubItem = value
            self._column.mask = self._column.mask | LVCF_SUBITEM

    property image:
        def __get__(self):
            return self._column.iImage
        def __set__(self, value):
            self._column.iImage = value
            self._column.mask = self._column.mask | LVCF_IMAGE

    property order:
        def __get__(self):
            return self._column.iOrder
        def __set__(self, value):
            self._column.iOrder = value
            self._column.mask = self._column.mask | LVCF_ORDER



cdef extern from *:
    ctypedef struct LVHITTESTINFO:
        POINT pt
        UINT flags
        int iItem
        int iSubItem

    int LVHT_ABOVE, LVHT_BELOW, LVHT_NOWHERE, LVHT_ONITEMICON
    int LVHT_ONITEMLABEL, LVHT_ONITEMSTATEICON, LVHT_ONITEM, LVHT_TOLEFT
    int LVHT_TORIGHT



cdef class _listview(_WndBase):
    cdef object _image_normal, image_small, _image_state
    
    cdef void *newInstance(self):
        return new_ListView(self)

    def setBkColor(self, color):
        CWnd_SendMessage_L_L_L(self._cwnd, LVM_SETBKCOLOR, 0, color)

    def setTextBkColor(self, color):
        CWnd_SendMessage_L_L_L(self._cwnd, LVM_SETTEXTBKCOLOR, 0, color)

    def setTextColor(self, color):
        CWnd_SendMessage_L_L_L(self._cwnd, LVM_SETTEXTCOLOR, 0, color)

    def setImageList(self, normal=None, small=None, state=None):
        cdef HIMAGELIST himg
        if normal is not None:
            if PyMFCHandle_IsHandle(normal):
                himg = PyMFCHandle_AsHandle(normal)
            else:
                himg = PyMFCHandle_AsHandle(normal.getHandle())
            CWnd_SendMessage_L_P_L(self._cwnd, LVM_SETIMAGELIST, 
                LVSIL_NORMAL, himg)
            self._image_normal = normal

        if small is not None:
            if PyMFCHandle_IsHandle(small):
                himg = PyMFCHandle_AsHandle(small)
            else:
                himg = PyMFCHandle_AsHandle(small.getHandle())
            CWnd_SendMessage_L_P_L(self._cwnd, LVM_SETIMAGELIST, 
                LVSIL_SMALL, himg)
            self._image_small = small

        if state:
            if PyMFCHandle_IsHandle(state):
                himg = PyMFCHandle_AsHandle(state)
            else:
                himg = PyMFCHandle_AsHandle(state.getHandle())
            CWnd_SendMessage_L_P_L(self._cwnd, LVM_SETIMAGELIST, 
                LVSIL_STATE, himg)
            self._image_state = state

    def setExtendedStyle(self, checkboxes=None, flatsb=None, fullrowselect=None,
            gridlines=None, headerdragdrop=None, infotip=None, multiworkareas=None,
            oneclickactivate=None, regional=None, subitemimages=None, trackselect=None,
            twoclickactivate=None, underlinecold=None, underlinehot=None):

        cdef DWORD mask, style
        cdef HWND hwnd
        
        mask = style = 0
        
        if checkboxes is not None:
            mask = mask | LVS_EX_CHECKBOXES
            if checkboxes:
                style = style | LVS_EX_CHECKBOXES

        if flatsb is not None:
            mask = mask | LVS_EX_FLATSB
            if flatsb:
                style = style | LVS_EX_FLATSB


        if fullrowselect is not None:
            mask = mask | LVS_EX_FULLROWSELECT
            if fullrowselect:
                style = style | LVS_EX_FULLROWSELECT

        if gridlines is not None:
            mask = mask | LVS_EX_GRIDLINES
            if gridlines:
                style = style | LVS_EX_GRIDLINES

        if headerdragdrop is not None:
            mask = mask | LVS_EX_HEADERDRAGDROP
            if headerdragdrop:
                style = style | LVS_EX_HEADERDRAGDROP

        if infotip is not None:
            mask = mask | LVS_EX_INFOTIP
            if infotip:
                style = style | LVS_EX_INFOTIP

        if multiworkareas is not None:
            mask = mask | LVS_EX_MULTIWORKAREAS
            if multiworkareas:
                style = style | LVS_EX_MULTIWORKAREAS

        if oneclickactivate is not None:
            mask = mask | LVS_EX_ONECLICKACTIVATE
            if oneclickactivate:
                style = style | LVS_EX_ONECLICKACTIVATE

        if regional is not None:
            mask = mask | LVS_EX_REGIONAL
            if regional:
                style = style | LVS_EX_REGIONAL

        if subitemimages is not None:
            mask = mask | LVS_EX_SUBITEMIMAGES
            if subitemimages:
                style = style | LVS_EX_SUBITEMIMAGES

        if trackselect is not None:
            mask = mask | LVS_EX_TRACKSELECT
            if trackselect:
                style = style | LVS_EX_TRACKSELECT

        if twoclickactivate is not None:
            mask = mask | LVS_EX_TWOCLICKACTIVATE
            if twoclickactivate:
                style = style | LVS_EX_TWOCLICKACTIVATE

        if underlinecold is not None:
            mask = mask | LVS_EX_UNDERLINECOLD
            if underlinecold:
                style = style | LVS_EX_UNDERLINECOLD

        if underlinehot is not None:
            mask = mask | LVS_EX_UNDERLINEHOT
            if underlinehot:
                style = style | LVS_EX_UNDERLINEHOT
        
        hwnd = self._getHwnd()
        with nogil:
            ListView_SetExtendedListViewStyleEx(hwnd, mask, style)
            

    def insertColumn(self, pos, _lvcolumn col):
        cdef LVCOLUMN *p
        p = &(col._column)
        return CWnd_SendMessage_L_P_L_m1(self._cwnd, LVM_INSERTCOLUMN, pos, p)
        
    def setColumnWidth(self, i, width):
        return CWnd_SendMessage_L_L_L_0(self._cwnd, LVM_SETCOLUMNWIDTH, i, MAKELPARAM(width, 0))

    def insert(self, _lvitem item):
        cdef LVITEM *p
        p = &(item._item)
        return CWnd_SendMessage_L_P_L_m1(self._cwnd, LVM_INSERTITEM, 0, p)
    
    def deleteItem(self, item=0, all=0):
        if not all:
            CWnd_SendMessage_L_L_L_0(self._cwnd, LVM_DELETEITEM, item, 0)
        else:
            CWnd_SendMessage_L_L_L_0(self._cwnd, LVM_DELETEALLITEMS, 0, 0)
    

    def setItem(self, _lvitem item):
        return CWnd_SendMessage_L_P_L_0(self._cwnd, LVM_SETITEM, 0, &(item._item))
        
    def setItemText(self, item, subitem, text):
        cdef LVITEM lv
        lv.mask = LVIF_TEXT
        lv.iItem = item
        lv.iSubItem = subitem
        lv.pszText = PyUnicode_AsUnicode(text)
        return CWnd_SendMessage_L_P_L_0(self._cwnd, LVM_SETITEMTEXT, item, &lv)

    def getItemCount(self):
        return CWnd_SendMessage_L_L_L(self._cwnd, LVM_GETITEMCOUNT, 0, 0)
        
    cdef object _getItemText(self, int iItem, int iSubItem):
        cdef LVITEM p
        cdef long clen
        cdef void *buf
        
        memset(&p, sizeof(p), 0)
        p.iItem = iItem
        p.iSubItem = iSubItem

        clen = 256
        while 1:
            buf = malloc(clen*sizeof(TCHAR))
            if buf == NULL:
                raise MemoryError()

            p.pszText = <TCHAR*>buf
            p.cchTextMax = clen

            if (clen - 1) != CWnd_SendMessage_L_P_L(self._cwnd, LVM_GETITEMTEXT, p.iItem, &p):
                try:
                    s = _fromWideChar(p.pszText)
                except:
                    free(buf)
                    raise

                free(buf)
                return s

            free(buf)
            clen = clen + 256
            

    def getItemText(self, int item, int subitem=0):
        return self._getItemText(item, subitem)
    
    def getItem(self, item):
        cdef _lvitem ret
        ret = _lvitem()

        if hasattr(item, 'item'):
            ret._item.iItem = item.item
            ret._item.iSubItem = item.subitem
        else:
            ret._item.iItem = item
            ret._item.iSubItem = 0
        
        ret._item.stateMask = -1

        ret._item.mask = LVIF_IMAGE | LVIF_INDENT | LVIF_PARAM | LVIF_STATE
        CWnd_SendMessage_L_P_L_0(self._cwnd, LVM_GETITEM, 0, &ret._item)

        return ret

    def getNextItem(self, item=-1, next=0, above=0, below=0, left=0, right=0, cut=0, drophilited=0, focused=0, selected=0):
        cdef int flag, ret
        cdef unsigned long hitem
        
        if hasattr(item, 'item'):
            hitem = item.item
        else:
            hitem = item
        
        flag = LVNI_ALL
        if above:
            flag = LVNI_ABOVE
        elif below:
            flag = LVNI_BELOW
        elif left:
            flag = LVNI_TOLEFT
        elif right:
            flag = LVNI_TORIGHT
        elif cut:
            flag = LVNI_CUT
        elif drophilited:
            flag = LVNI_DROPHILITED
        elif focused:
            flag = LVNI_FOCUSED
        elif selected:
            flag = LVNI_SELECTED

        ret = CWnd_SendMessage_L_L_L(self._cwnd, LVM_GETNEXTITEM, hitem, flag)
        return ret

    def getFocusedItem(self):
        return self.getNextItem(item=-1, focused=1)
        
    def editLabel(self, item):
        cdef WPARAM iItem 
        if hasattr(item, 'item'):
            iItem = item.item
        else:
            iItem = item
            
        CWnd_SendMessage_L_L_L_0(self._cwnd, LVM_EDITLABEL, iItem, 0)

    def _getEditControl(self, editcls):
        cdef HWND hwnd
        
        hwnd = <HWND>CWnd_SendMessage_L_L_L_0(self._cwnd, LVM_GETEDITCONTROL, 0, 0)
        ret = editcls()
        ret._subclassWindow(PyMFCHandle_FromHandle(hwnd), temp=1)
        return ret

    def hitTest(self, pos, above=0, below=0, nowhere=0, onitemicon=0,
            onitemlabel=0, onitemstateicon=0, onitem=0, toleft=0, toright=0):
        
        cdef LVHITTESTINFO ht
        cdef int x, y
        cdef LONG ret
        x, y = pos
        memset(&ht, 0, sizeof(ht))
        
        ht.pt.x = x
        ht.pt.y = y
        ht.flags = 0

        if above:
            ht.flags = ht.flags | LVHT_ABOVE
        if below:
            ht.flags = ht.flags | LVHT_BELOW
        if nowhere:
            ht.flags = ht.flags | LVHT_NOWHERE
        if onitemicon:
            ht.flags = ht.flags | LVHT_ONITEMICON
        if onitemlabel:
            ht.flags = ht.flags | LVHT_ONITEMLABEL
        if onitemstateicon:
            ht.flags = ht.flags | LVHT_ONITEMSTATEICON
        if onitem:
            ht.flags = ht.flags | LVHT_ONITEM
        if toleft:
            ht.flags = ht.flags | LVHT_TOLEFT
        if toright:
            ht.flags = ht.flags | LVHT_TORIGHT

        
        ret = CWnd_SendMessage_L_P_L(self._cwnd, LVM_HITTEST, 0, &ht)
        if ret == -1:
            return
        return <unsigned long>ht.iItem

# Listview styles
cdef extern from *:
    int LVS_ALIGNLEFT, LVS_ALIGNTOP, LVS_AUTOARRANGE, LVS_EDITLABELS
    int LVS_ICON, LVS_LIST, LVS_NOCOLUMNHEADER, LVS_NOLABELWRAP
    int LVS_NOSCROLL, LVS_NOSORTHEADER, LVS_OWNERDATA, LVS_OWNERDRAWFIXED
    int LVS_REPORT, LVS_SHAREIMAGELISTS, LVS_SHOWSELALWAYS, LVS_SINGLESEL
    int LVS_SMALLICON, LVS_SORTASCENDING, LVS_SORTDESCENDING

    int LVS_EX_CHECKBOXES, LVS_EX_FLATSB, LVS_EX_FULLROWSELECT
    int LVS_EX_GRIDLINES, LVS_EX_HEADERDRAGDROP, LVS_EX_INFOTIP
    int LVS_EX_MULTIWORKAREAS, LVS_EX_ONECLICKACTIVATE
    int LVS_EX_REGIONAL, LVS_EX_SUBITEMIMAGES, LVS_EX_TRACKSELECT
    int LVS_EX_TWOCLICKACTIVATE, LVS_EX_UNDERLINECOLD, LVS_EX_UNDERLINEHOT


cdef __init_listview_styles():
    ret = {
        "alignleft":LVS_ALIGNLEFT,
        "aligntop":LVS_ALIGNTOP,
        "autoarrange":LVS_AUTOARRANGE,
        "editlabels":LVS_EDITLABELS,
        "icon":LVS_ICON,
        "list":LVS_LIST,
        "nocolumnheader":LVS_NOCOLUMNHEADER,
        "nolabelwrap":LVS_NOLABELWRAP,
        "noscroll":LVS_NOSCROLL,
        "nosortheader":LVS_NOSORTHEADER,
        "ownerdata":LVS_OWNERDATA,
        "ownerdrawfixed":LVS_OWNERDRAWFIXED,
        "report":LVS_REPORT,
        "shareimagelists":LVS_SHAREIMAGELISTS,
        "showselalways":LVS_SHOWSELALWAYS,
        "singlesel":LVS_SINGLESEL,
        "smallicon":LVS_SMALLICON,
        "sortascending":LVS_SORTASCENDING,
        "sortdescending":LVS_SORTDESCENDING,
    }
    ret.update(_std_styles)
    return ret

_listview_styles = __init_listview_styles()


cdef class ListViewStyle(WndStyle):
    def _initTable(self):
        self._styles = _listview_styles

#cdef __init_listview_ex_styles():
#    ret = {
#        "checkboxes":LVS_EX_CHECKBOXES,
#        "flatsb":LVS_EX_FLATSB,
#        "fullrowselect":LVS_EX_FULLROWSELECT,
#        "gridlines":LVS_EX_GRIDLINES,
#        "headerdragdrop":LVS_EX_HEADERDRAGDROP,
#        "infotip":LVS_EX_INFOTIP,
#        "multiworkareas":LVS_EX_MULTIWORKAREAS,
#        "oneclickactivate":LVS_EX_ONECLICKACTIVATE,
#        "regional":LVS_EX_REGIONAL,
#        "subitemimages":LVS_EX_SUBITEMIMAGES,
#        "trackselect":LVS_EX_TRACKSELECT,
#        "twoclickactivate":LVS_EX_TWOCLICKACTIVATE,
#        "underlinecold":LVS_EX_UNDERLINECOLD,
#        "underlinehot":LVS_EX_UNDERLINEHOT,
#    }
#    return ret
#
#_listview_ex_styles = __init_listview_ex_styles()
#
#cdef class ListViewStyle(WndStyle):
#    cdef object _exListStyles
#    cdef int exListStyle
#    
#    def __init__(self, *args, **kwargs):
#        self.exListStyle = 0
#        WndStyle.__init__(self, *args, **kwargs)
#        
#    def _copyfrom(self, ListViewStyle _from):
#        self.exListStyle = _from.exListStyle
#        WndStyle._copyfrom(self, _from)
#
#    def _initTable(self):
#        self._styles = _listview_styles
#        self._exListStyles = _listview_ex_styles
#
#    def __getattr__(self, name):
#        # XXX: cannot call WndStyle.__getattr__. Pyrex bug?
#
#        v = self._styles.get(name)
#        if v is not None:
#            return (self.style & v) != 0
#
#        v = self._exStyles.get(name)
#        if v is not None:
#            return (self.exStyle & v) != 0
#
#        v = self._exListStyles.get(name)
#        if v is not None:
#            return (self.exListStyle & v) != 0
#
#        raise AttributeError(name)
#
#    def __setattr__(self, name, value):
#        # XXX: cannot call WndStyle.__setattr__. Pyrex bug?
#        v = self._styles.get(name)
#        if v is not None:
#            if value:
#                self.style = self.style | v
#            else:
#                self.style = self.style & ~v
#        else:
#            v = self._exStyles.get(name)
#            if v is not None:
#                if value:
#                    self.exStyle = self.exStyle | v
#                else:
#                    self.exStyle = self.exStyle & ~v
#            else:
#                v = self._exListStyles.get(name)
#                if v is not None:
#                    if value:
#                        self.exListStyle = self.exListStyle | v
#                    else:
#                        self.exListStyle = self.exListStyle & ~v
#                else:
#                    raise AttributeError(name)

# ListView messages
cdef extern from *:
    int LVN_BEGINDRAG, LVN_BEGINLABELEDIT, LVN_BEGINRDRAG, LVN_COLUMNCLICK
    int LVN_DELETEALLITEMS, LVN_DELETEITEM, LVN_ENDLABELEDIT, LVN_GETDISPINFO
    int LVN_GETINFOTIP, LVN_HOTTRACK, LVN_INSERTITEM, LVN_ITEMACTIVATE
    int LVN_ITEMCHANGED, LVN_ITEMCHANGING, LVN_KEYDOWN, LVN_MARQUEEBEGIN
    int LVN_ODCACHEHINT, LVN_ODFINDITEM, LVN_ODSTATECHANGED, LVN_SETDISPINFO

cdef __init_listviewmsg():
    ret = {
        "BEGINDRAG":(WM_NOTIFY, LVN_BEGINDRAG),
        "BEGINLABELEDIT":(WM_NOTIFY, LVN_BEGINLABELEDIT),
        "BEGINRDRAG":(WM_NOTIFY, LVN_BEGINRDRAG),
        "COLUMNCLICK":(WM_NOTIFY, LVN_COLUMNCLICK),
        "ALLITEMSDELETED":(WM_NOTIFY, LVN_DELETEALLITEMS),
        "ITEMDELETED":(WM_NOTIFY, LVN_DELETEITEM),
        "ENDLABELEDIT":(WM_NOTIFY, LVN_ENDLABELEDIT),
        "GETDISPINFO":(WM_NOTIFY, LVN_GETDISPINFO),
        "GETINFOTIP":(WM_NOTIFY, LVN_GETINFOTIP),
        "HOTTRACK":(WM_NOTIFY, LVN_HOTTRACK),
        "INSERTITEM":(WM_NOTIFY, LVN_INSERTITEM),
        "ITEMACTIVATE":(WM_NOTIFY, LVN_ITEMACTIVATE),
        "ITEMCHANGED":(WM_NOTIFY, LVN_ITEMCHANGED),
        "ITEMCHANGING":(WM_NOTIFY, LVN_ITEMCHANGING),
        "KEYDOWN":(WM_NOTIFY, LVN_KEYDOWN),
        "MARQUEEBEGIN":(WM_NOTIFY, LVN_MARQUEEBEGIN),
        "ODCACHEHINT":(WM_NOTIFY, LVN_ODCACHEHINT),
        "ODFINDITEM":(WM_NOTIFY, LVN_ODFINDITEM),
        "ODSTATECHANGED":(WM_NOTIFY, LVN_ODSTATECHANGED),
        "SETDISPINFO":(WM_NOTIFY, LVN_SETDISPINFO),
    }
    ret.update(_msgdict)
    return ret

_listviewmsg = __init_listviewmsg()




