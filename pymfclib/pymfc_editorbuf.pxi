cdef extern from "pymeditor.h":
    void *PymBuf_New() except NULL
    long PymBuf_Free(void *buf) except 0

    long PymBuf_Insert(void *buf, long pos, object s) except 0
    long PymBuf_Dele(void *buf, long pos, long posto) except 0
    long PymBuf_Replace(void *buf, long pos, long posto, object s) except 0
    object PymBuf_GetChar(void *buf, long pos, long posto)
    object PymBuf_GetStyle(void *buf, long pos, long posto)
    long PymBuf_SetStyle(void *buf, long pos, long posto, UINT idx) except 0
    long PymBuf_GetLineNo(void *buf, long pos) except -1
    long PymBuf_GetLineNoPos(void *o, long lineno)
    long PymBuf_GetTOL(void *buf, long pos) except -1
    long PymBuf_GetEOL(void *buf, long pos) except -1
    long PymBuf_GetLineFeed(void *buf, long pos) except -1
    long PymBuf_GetSize(void *buf) except -1

    long PymBuf_Find(void *o, long pos, long to, PYMFC_WCHAR c)
    long PymBuf_Find_back(void *o, long pos, long to, PYMFC_WCHAR c)
    long PymBuf_Find_i(void *o, long pos, long to, PYMFC_WCHAR c)
    long PymBuf_Find_i_back(void *o, long pos, long to, PYMFC_WCHAR c)
    object PymBuf_FindOneOf(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    object PymBuf_FindOneOf_back(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    long PymBuf_FindString(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    long PymBuf_FindString_i(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    long PymBuf_FindString_back(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    long PymBuf_FindString_i_back(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t)
    long PymBuf_FindString_esc(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t, PYMFC_WCHAR esc)
    long PymBuf_FindString_i_esc(void *o, long pos, long to, PYMFC_WCHAR *c, PYMFC_WCHAR *t, PYMFC_WCHAR esc)
    long PymBuf_FindStyle(void *o, long pos, long to, UINT idx)
    long PymBuf_FindStyle_back(void *o, long pos, long to, UINT idx)
    object PymBuf_FindStyleOneOf(void *o, long pos, long to, long *f, long *t)
    object PymBuf_FindStyleOneOf_back(void *o, long pos, long to, long *f, long *t)
    object PymBuf_GetStyleRange(void *o, long pos)
    
cdef class Buffer:
    cdef void *p_buf

    
    def __init__(self):
        self.p_buf = PymBuf_New()
        
    def getBuffer(self):
        return PyMFCPtr_FromVoidPtr(self.p_buf)

    def __dealloc__(self):
        if self.p_buf != NULL:
            PymBuf_Free(self.p_buf)
    
    def __len__(self):
        return PymBuf_GetSize(self.p_buf)

    def __getitem__(self, int n):
        return PymBuf_GetChar(self.p_buf, n, n+1)

    def __getslice__(self, int i, int j):
        return PymBuf_GetChar(self.p_buf, i, j)

    def ins(self, long pos, s):
        if pos > PymBuf_GetSize(self.p_buf):
            raise IndexError()
        PymBuf_Insert(self.p_buf, pos, s)

    def delete(self, long pos, long posto):
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        if pos > size:
            raise IndexError()
        if posto > size:
            raise IndexError()
        if posto < pos:
            raise ValueError()
        PymBuf_Dele(self.p_buf, pos, posto)

    def replace(self, long pos, long posto, s):
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        if pos > size:
            raise IndexError()
        if posto > size:
            raise IndexError()
        if posto < pos:
            raise ValueError()
        PymBuf_Replace(self.p_buf, pos, posto, s)
        
    cdef object _get(self, long pos, long posto):
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        if pos > size:
            raise IndexError()
        if posto > size:
            raise IndexError()
        if posto < pos:
            raise ValueError()
        return PymBuf_GetChar(self.p_buf, pos, posto)
        
    def get(self, long pos, long posto):
        return self._get(pos, posto)
        
    def getStyle(self, long pos, long posto):
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        if pos > size:
            raise IndexError()
        if posto > size:
            raise IndexError()
        if posto < pos:
            raise ValueError()
        return PymBuf_GetStyle(self.p_buf, pos, posto)
    
    def setStyle(self, long pos, long posto, idx):
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        if pos > size:
            raise IndexError()
        if posto > size:
            raise IndexError()
        if posto < pos:
            raise ValueError()

        #todo: check idx value
        PymBuf_SetStyle(self.p_buf, pos, posto, idx)
    
    def setStyles(self, styles):
        cdef long pos, posto
        cdef UINT idx
        cdef long size
        size = PymBuf_GetSize(self.p_buf)
        for idx, pos, posto in styles:
            if pos > size:
                raise IndexError()
            if posto > size:
                raise IndexError()
            if posto < pos:
                raise ValueError()
            PymBuf_SetStyle(self.p_buf, pos, posto, idx)

    def getLineNo(self, long pos):
        if pos > PymBuf_GetSize(self.p_buf):
            raise IndexError()
        return PymBuf_GetLineNo(self.p_buf, pos)
    
    def getLineNoPos(self, long lineno):
        return PymBuf_GetLineNoPos(self.p_buf, lineno)

    def getTOL(self, long pos):
        if pos > PymBuf_GetSize(self.p_buf):
            raise IndexError()
        return PymBuf_GetTOL(self.p_buf, pos)
    
    def getEOL(self, long pos):
        if pos > PymBuf_GetSize(self.p_buf):
            raise IndexError()
        return PymBuf_GetEOL(self.p_buf, pos)

    def getLineFeed(self, long pos):
        if pos > PymBuf_GetSize(self.p_buf):
            raise IndexError()
        return PymBuf_GetLineFeed(self.p_buf, pos)
        
    def getSize(self):
        return PymBuf_GetSize(self.p_buf)

    def find(self, pos, posto, c, case=1, forward=1):
        cdef long w_c
        w_c = ord(c)
        
        if case:
            if forward:
                return PymBuf_Find(self.p_buf, pos, posto, <PYMFC_WCHAR>w_c)
            else:
                return PymBuf_Find_back(self.p_buf, pos, posto, <PYMFC_WCHAR>w_c)
        else:
            if forward:
                return PymBuf_Find_i(self.p_buf, pos, posto, <PYMFC_WCHAR>w_c)
            else:
                return PymBuf_Find_i_back(self.p_buf, pos, posto, <PYMFC_WCHAR>w_c)
                
    def findOneOf(self, pos, posto, c, forward=1):
        cdef PYMFC_WCHAR *p_c
        cdef long l
        p_c = PyUnicode_AsUnicode(c)
        l = len(c)
        
        if forward:
            return PymBuf_FindOneOf(self.p_buf, pos, posto, p_c, p_c+l)
        else:
            return PymBuf_FindOneOf_back(self.p_buf, pos, posto, p_c, p_c+l)
                
    def findString(self, pos, posto, s, case=1, forward=1):
        cdef PYMFC_WCHAR *p_s
        cdef long l
        p_s = PyUnicode_AsUnicode(s)
        l = len(s)

        if case:
            if forward:
                return PymBuf_FindString(self.p_buf, pos, posto, p_s, p_s+l)
            else:
                return PymBuf_FindString_back(self.p_buf, pos, posto, p_s, p_s+l)
        else:
            if forward:
                return PymBuf_FindString_i(self.p_buf, pos, posto, p_s, p_s+l)
            else:
                return PymBuf_FindString_i_back(self.p_buf, pos, posto, p_s, p_s+l)

    def findStyle(self, pos, posto, style, forward=1):
        cdef long w_c
        cdef long stylelen
        cdef long *buf
        cdef long n
        
        if isinstance(style, int):
            if forward:
                return PymBuf_FindStyle(self.p_buf, pos, posto, style)
            else:
                return PymBuf_FindStyle_back(self.p_buf, pos, posto, style)
        else:
            stylelen = len(style)
            buf = <long*>malloc(stylelen*sizeof(long))
            if buf == NULL:
                raise MemoryError()
            n = 0
            for s in style:
                w_c = s
                buf[n] = w_c
                n = n + 1
            try:
                if forward:
                    ret = PymBuf_FindStyleOneOf(self.p_buf, pos, posto, buf, buf+stylelen)
                else:
                    ret = PymBuf_FindStyleOneOf_back(self.p_buf, pos, posto, buf, buf+stylelen)
            except:
                free(buf)
                raise
                
            free(buf)
            return ret

    def getStyleRange(self, pos):
        return PymBuf_GetStyleRange(self.p_buf, pos)
        