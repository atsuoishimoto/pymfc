cdef extern from "malloc.h":
    enum:
        MAX_PATH

cdef extern from "malloc.h":
    ctypedef unsigned int size_t
    
    void *malloc(unsigned long size)
    void free(void *memblock)

ctypedef unsigned short PYMFC_WCHAR

cdef extern from "string.h":
    int memcmp(void *buf1, void *buf2, size_t count)
    void *memcpy(void *dest, void *src, unsigned long count)
    void *memset(void *dest, int c, unsigned long count)
    char *strncpy(char *string1, char *string2, unsigned long count)
    size_t strlen(char *string)
    size_t wcslen(PYMFC_WCHAR *string)


cdef extern from "tchar.h":
    PYMFC_WCHAR *_tcsncpy(PYMFC_WCHAR *string1, PYMFC_WCHAR *string2, unsigned long count)


cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *v, int len)
    object PyString_FromString(char *v)
    int PyString_AsStringAndSize(object obj, char **buffer, int *length) except -1
    object PyUnicode_FromWideChar(PYMFC_WCHAR *t, int size)
    PYMFC_WCHAR *PyUnicode_AsUnicode(object obj) except NULL
    
    object PyLong_FromLong(long)
    object PyLong_FromVoidPtr(void *)
    void *PyLong_AsVoidPtr(object)

    ctypedef struct PyThreadState
    PyThreadState* PyEval_SaveThread()
    void PyEval_RestoreThread(PyThreadState *tstate)


cdef extern from "pymmacros.h":
    object _fromWideChar(PYMFC_WCHAR *s)

