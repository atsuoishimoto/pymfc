cdef extern from "windows.h":
    # types
    ctypedef void *HIMC

    ctypedef struct COMPOSITIONFORM:
        unsigned long  dwStyle
        POINT  ptCurrentPos
        RECT   rcArea

    int CFS_DEFAULT, CFS_RECT, CFS_POINT, CFS_FORCE_POSITION
    int CFS_CANDIDATEPOS, CFS_EXCLUDE

    int GCS_COMPREADSTR, GCS_COMPREADATTR, GCS_COMPREADCLAUSE, GCS_COMPSTR
    int GCS_COMPATTR, GCS_COMPCLAUSE, GCS_CURSORPOS, GCS_DELTASTART
    int GCS_RESULTREADSTR, GCS_RESULTREADCLAUSE, GCS_RESULTSTR, GCS_RESULTCLAUSE


    
    HIMC pymImmGetContext(HWND hWnd) except NULL
    BOOL pymImmReleaseContext(HWND hWnd, HIMC hIMC)
    BOOL pymImmSetOpenStatus(HIMC hIMC, int fopen)
    BOOL pymImmGetOpenStatus(HIMC hIMC)
    BOOL pymImmSetCompositionWindow(HIMC hIMC, COMPOSITIONFORM *lpCompForm)
    BOOL pymImmSetCompositionFont(HIMC hIMC, LOGFONT *lplf)
    long pymImmGetCompositionString(HIMC hIMC, long dwIndex, void *lpBuf, long dwBufLen) except -1
#
# TODO: These functions should release GIL before calling Imm* APIs.
#

cdef class ImmContext:
    cdef HIMC hIMC
    cdef object wnd
    
    def __init__(self, wnd):
        cdef HWND hwnd
        hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
        self.hIMC = pymImmGetContext(hwnd)
        self.wnd = wnd

    def __dealloc__(self):
        self._release()

    cdef void _release(self):
        cdef HWND hwnd
        if self.hIMC:
            hwnd = PyMFCHandle_AsHandle(self.wnd.getHwnd())
            
            pymImmReleaseContext(hwnd, self.hIMC)
            self.hIMC = NULL
            self.wnd = None

    def release(self):
        self._release()
        
    def open(self):
        pymImmSetOpenStatus(self.hIMC, 1)

    def close(self):
        pymImmSetOpenStatus(self.hIMC, 0)

    def isOpen(self):
        return pymImmGetOpenStatus(self.hIMC)
    
    def setCompWndPos(self, pos):
        cdef COMPOSITIONFORM cf
        cdef int x, y
        x, y = pos
        cf.dwStyle = CFS_POINT
        cf.ptCurrentPos.x = x
        cf.ptCurrentPos.y = y

        pymImmSetCompositionWindow(self.hIMC, &cf)
        
    def setCompFont(self, logfont):
        cdef LOGFONT *lplf
        lplf = <LOGFONT *>PyMFCPtr_AsVoidPtr(logfont.getLogFont())
        pymImmSetCompositionFont(self.hIMC, lplf)
        
    def getResultString(self):
        cdef TCHAR *buf
        cdef long clen
        
        clen = pymImmGetCompositionString(self.hIMC, GCS_RESULTSTR, NULL, 0)+sizeof(TCHAR)
        buf = <TCHAR*>malloc(clen*sizeof(BYTE))
        if buf == NULL:
            raise MemoryError()
        try:
            memset(buf, 0, clen)
            pymImmGetCompositionString(self.hIMC, GCS_RESULTSTR, buf, clen)
            return _fromWideChar(buf)
        finally:
            free(buf)


#todo: pyrex bug?
#        try:
#            ret = PyString_FromStringAndSize(<char*>buf, clen)
#        except:
#            free(buf)
#            raise
#
#        free(buf)
#        return ret


#            int len = ImmGetCompositionString(obj->hIMC, GCS_RESULTSTR, NULL, 0);
#    if (len > 0) {
#            char *buf = str.GetBuffer(len);
#            len = ImmGetCompositionString(obj->hIMC, GCS_RESULTSTR, buf, len);
#            str.ReleaseBuffer();
#    }
