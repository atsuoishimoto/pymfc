cdef extern from "pymwnd.h":
    # Controls
    void *new_WebCtrl(object obj) except NULL
    int PyMFCWebCtrl_Navigate(void *o, TCHAR *url) except 0
    object PyMFCWebCtrl_GetDocument(void *o)
    int PyMFCWebCtrl_UIDeactivate(void *) except 0
    int PyMFCWebCtrl_ExecCommand(void *, DWORD commandid) except 0
    
cdef class _webctrl(_WndBase):
    cdef void *newInstance(self):
        return new_WebCtrl(self)

    def getDocument(self):
        return PyMFCWebCtrl_GetDocument(self._cwnd)
        
    def navigate(self, url):
        PyMFCWebCtrl_Navigate(self._cwnd, PyUnicode_AsUnicode(url))

    def UIDeactivate(self):
        PyMFCWebCtrl_UIDeactivate(self._cwnd)
            
    def execCommand(self, cmdid):
        PyMFCWebCtrl_ExecCommand(self._cwnd, cmdid)
        
    
    
cdef __init_webwnd_styles():
    ret = {
    }

    ret.update(_std_styles)
    return ret

_webwnd_styles = __init_webwnd_styles()

cdef class WebCtrlStyle(WndStyle):
    def _initTable(self):
        self._styles = _webwnd_styles


cdef __init_webwndmsg():
    ret = {
    }
    ret.update(_msgdict)
    return ret

_webwndwmsg = __init_webwndmsg()




