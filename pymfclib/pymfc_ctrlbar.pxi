cdef extern from "pymwnd.h":
    int CControlBar_EnableDocking(void *o, int left, int top, int right, int bottom, int any, int multi) except 0
    
    void *new_CStatusBar(object obj) except NULL
    int CStatusBar_Create(void *o, void *parent, object lens) except 0
    int CStatusBar_SetPaneText(void *o, int idx, TCHAR *s) except 0
    int CStatusBar_CalcFixedSize(void *o, SIZE *size) except 0
    
    void *new_CToolBar(object obj) except NULL
    int CToolBar_Create(void *o, void *parent, TCHAR *title, int id, int left, int top, int right, int bottom) except 0
    int CToolBar_SetButtons(void *o, object buttonIds) except 0
    int CToolBar_SetBitmap(void *o, void *hbmp) except 0
    int CToolBar_SetImageList(void *o, void *imageList) except 0
    int CToolBar_SetButtonInfo(void *o, int index, int id, int style, int iImage)
    object CToolBar_GetButtonInfo(void *o, int index)
    int CToolBar_GetButtonIndex(void *o, int id)
    object CToolBar_GetItemRect(void *o, int index)

    int CToolBar_GetButtonStyle(void *o, int index)
    void CToolBar_SetButtonStyle(void *o, int index, int style, int checked, int indeterminate, int disabled, int pressed)
    
    int TBSTYLE_BUTTON, TBSTYLE_SEP, TBSTYLE_CHECK, TBSTYLE_GROUP
    int TBSTYLE_CHECKGROUP, TBSTYLE_DROPDOWN, TBSTYLE_AUTOSIZE
    int TBSTYLE_NOPREFIX

    int TBSTATE_CHECKED, TBSTATE_INDETERMINATE, TBSTATE_ENABLED, TBSTATE_PRESSED
    


cdef class _controlbar(_WndBase):
    cdef void *newInstance(self):
        assert 0 # _controlbar is abstract base class

    def enableDocking(self, left=0, top=0, right=0, bottom=0, any=1, multi=0):
        CControlBar_EnableDocking(self._cwnd, left, top, right, bottom, any, multi)

cdef class _statusbar(_controlbar):
    cdef void *newInstance(self):
        return new_CStatusBar(self)

    def _create(self, parent, lens): 
        CStatusBar_Create(self._cwnd, PyMFCPtr_AsVoidPtr(parent.cwnd), lens)

    def setPaneText(self, idx, s):
        CStatusBar_SetPaneText(self._cwnd, idx, PyUnicode_AsUnicode(s))

    def calcFixedSize(self):
        cdef SIZE size
        CStatusBar_CalcFixedSize(self._cwnd, &size)
        return size.cx, size.cy
        
cdef class _toolbar(_controlbar):
    cdef void *newInstance(self):
        return new_CToolBar(self)
        
    def _create(self, parent, title, id, left, top, right, bottom):
        CToolBar_Create(self._cwnd, PyMFCPtr_AsVoidPtr(parent.cwnd), PyUnicode_AsUnicode(title), id, left, top, right, bottom)
    
    def setButtons(self, buttonids):
        CToolBar_SetButtons(self._cwnd, buttonids)

    def setBitmap(self, bmp):
        CToolBar_SetBitmap(self._cwnd, PyMFCHandle_AsHandle(bmp.detach()))

    def setImageList(self, imglist):
        CToolBar_SetImageList(self._cwnd, PyMFCPtr_AsVoidPtr(imglist.getCImageList()))

    def getButtonInfo(self, int index):
        return CToolBar_GetButtonInfo(self._cwnd, index)

    def setButtonInfo(self, int index, int cmdId, int iImage, int style=0,
            int separator=0, int checkbox=0, int group=0, int checkgroup=0, int dropdown=0,
            checked=None, indeterminate=None, enabled=None, pressed=None):

        cdef int _style
        _style = style

        if separator:
            _style = _style | TBSTYLE_SEP
        if checkbox:
            _style = _style | TBSTYLE_CHECK
        if group:
            _style = _style | TBSTYLE_GROUP
        if checkgroup:
            _style = _style | TBSTYLE_CHECKGROUP
        if dropdown:
            _style = _style | TBSTYLE_DROPDOWN

        if checked is not None:
            if checked:
                _style = _style | (TBSTATE_CHECKED << 16)
            else:
                _style = _style & (TBSTATE_CHECKED << 16)

        if indeterminate is not None:
            if indeterminate:
                _style = _style | (TBSTATE_INDETERMINATE << 16)
            else:
                _style = _style & (TBSTATE_INDETERMINATE << 16)

        if enabled is not None:
            if enabled:
                _style = _style | (TBSTATE_ENABLED << 16)
            else:
                _style = _style & (TBSTATE_ENABLED << 16)

        if pressed is not None:
            if pressed:
                _style = _style | (TBSTATE_PRESSED << 16)
            else:
                _style = _style & (TBSTATE_PRESSED << 16)

        return CToolBar_SetButtonInfo(self._cwnd, index, cmdId, _style, iImage)

    def getButtonStyle(self, int index):
        return CToolBar_GetButtonStyle(self._cwnd, index)
        
    def setButtonStyle(self, int index, int style=0,
            checked=-1, indeterminate=-1, disabled=-1, pressed=-1):
        CToolBar_SetButtonStyle(self._cwnd, index, style, checked, indeterminate, disabled, pressed)
        
    def getButtonIndex(self, int cmdId):
        cdef int ret
        ret = CToolBar_GetButtonIndex(self._cwnd, cmdId)
        if ret == -1:
            raise ValueError()
        return ret

    def getButtonRect(self, int index):
        return CToolBar_GetItemRect(self._cwnd, index)


# Toolbar messages
#cdef extern from "COMMCTRL.H":
#    int TTN_GETDISPINFO, TTN_SHOW, TTN_POP, TTN_NEEDTEXTA

cdef __init_toolbarmsg():
    ret = {
#        "GETDISPINFO":(WM_NOTIFY, TTN_GETDISPINFO),
#        "SHOW":(WM_NOTIFY, TTN_SHOW),
#        "POP":(WM_NOTIFY, TTN_POP),
#        "NEEDTEXT":(WM_NOTIFY, TTN_NEEDTEXTA),
    }
    ret.update(_msgdict)
    return ret

_toolbarmsg = __init_toolbarmsg()


