
cdef extern from "pymapp.h":
    int App_Run() except *
    void App_Quit(int result) except *
    int App_SetIdleProc(object proc) except 0
    int App_SetTimerProcs(object proc) except 0
    int App_PumpMessage()

cdef class App:
    def run(self):
        return App_Run()
    
    def quit(self, result):
        App_Quit(result)

    def setIdleProc(self, proc):
        App_SetIdleProc(proc)
        
    def setTimerProcs(self, procs):
        App_SetTimerProcs(procs)
        
    def pumpMessage(self):
        return App_PumpMessage()

cdef class GlobalMemory:
    cdef void *hMem
    cdef readonly char *_ptr

    property ptr:
        def __get__(self):
            self._lock()
            return PyMFCPtr_FromVoidPtr(self._ptr)

    cdef void _lock(self):
        if not self._ptr:
            self._ptr = <char*>GlobalLock(self.hMem)
            if not self._ptr:
                pymRaiseWin32Err()
        
    cdef void _unlock(self):
        if self._ptr:
            if 0==GlobalUnlock(self.hMem):
                pymRaiseWin32Err()
            self._ptr = NULL

    def __init__(self, long size=0, long ghnd=0, long gmem_fixed=0, long gmem_moveable=0, long gmem_zeroinit=0, long gptr=0, text=None):
        cdef int f
        cdef void *hMem
        cdef char *buf
        cdef int buflen, ret

        f = 0
        
        if ghnd:
            f = f | GHND
        if gmem_fixed:
            f = f | GMEM_FIXED
        if gmem_moveable:
            f = f | GMEM_MOVEABLE
        if gmem_zeroinit:
            f = f | GMEM_ZEROINIT
        if gptr:
            f = f | GPTR

        if isinstance(text, str):
            PyString_AsStringAndSize(text, &buf, &buflen)
            hMem = GlobalAlloc(f, buflen+1)
            if hMem == NULL:
                pymRaiseWin32Err()
            self.hMem = hMem
            
            self._lock()
            memcpy(self._ptr, buf, buflen)
            self._ptr[buflen] = 0
            self._unlock()
        else:
            hMem = GlobalAlloc(f, size)
            if hMem == NULL:
                pymRaiseWin32Err()
            
            self.hMem = hMem
    
    def __dealloc__(self):
        self._unlock()
        if self.hMem:
            GlobalFree(<void*>self.hMem)

        
    def lock(self):
        self._lock()
        
    def unlock(self):
        self._unlock()


cdef extern from "windows.h":
    BOOL CloseHandle(HANDLE hObject)
    DWORD pymWaitForMultipleObjectsEx(DWORD nCount, HANDLE* lpHandles, BOOL bWaitAll, DWORD dwMilliseconds, BOOL bAlertable)
    cdef int INFINITE, WAIT_OBJECT_0, WAIT_ABANDONED_0, WAIT_IO_COMPLETION, WAIT_TIMEOUT

#    DWORD GetProcessId(HANDLE Process)
    HANDLE OpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId)

    cdef int PROCESS_ALL_ACCESS, PROCESS_CREATE_PROCESS, PROCESS_CREATE_THREAD, PROCESS_DUP_HANDLE
    cdef int PROCESS_QUERY_INFORMATION, PROCESS_SET_QUOTA, PROCESS_SET_INFORMATION, PROCESS_TERMINATE
    cdef int PROCESS_VM_OPERATION, PROCESS_VM_READ, PROCESS_VM_WRITE, SYNCHRONIZE



    
cdef class WinHandle:
    cdef HANDLE _handle
    cdef int temp

    def __init__(self, handle=None, own=0):
        if handle is not None:
            self._handle = PyMFCHandle_AsHandle(handle)
        if not own:
            self.temp = 1
    
    def __dealloc__(self):
        if self._handle and not self.temp:
            CloseHandle(self._handle)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self._handle)
        
    def wait(self, timeout=None):
        cdef DWORD milli
        cdef HANDLE handle
        
        if timeout is None:
            milli = INFINITE
        else:
            milli = int(timeout*1000)
        
        handle = self._handle
        ret = pymWaitForMultipleObjectsEx(1, &handle, 1, milli, 0)
        
        if ret == WAIT_TIMEOUT:
            return 0
        else:
            return 1

     # Use NtQueryInformationProcess()
#    def getProcessId(self):
#        cdef DWORD ret
#        ret = GetProcessId(self._handle)
#        if ret == 0:
#            pymRaiseWin32Err()
#        return ret

def openProcess(processid):
    cdef HANDLE handle
    handle = OpenProcess(SYNCHRONIZE, 1, processid)
    if not handle:
        pymRaiseWin32Err()

    return WinHandle(handle=PyMFCHandle_FromHandle(handle), own=1)

cdef extern from "windows.h":
    DWORD GetCurrentThreadId()
    DWORD GetCurrentProcessId()

def getCurrentThreadId():
    return PyLong_FromLong(GetCurrentThreadId())

def getCurrentProcessId():
    return PyLong_FromLong(GetCurrentProcessId())

def postMessage(hwnd, msg, wparam, lparam):
    return pymPostMessage(PyMFCHandle_AsHandle(hwnd), msg, wparam, lparam)

def postThreadMessage(idThread, msg, wparam, lparam):
    return pymPostThreadMessage(idThread, msg, wparam, lparam)

cdef extern from "windows.h":
    int GetSystemMetrics(int nIndex)
    
    cdef int SM_CXSCREEN, SM_CYSCREEN, SM_CXVSCROLL, SM_CYHSCROLL
    cdef int SM_CYCAPTION, SM_CXBORDER, SM_CYBORDER, SM_CXDLGFRAME
    cdef int SM_CYDLGFRAME, SM_CYVTHUMB, SM_CXHTHUMB, SM_CXICON
    cdef int SM_CYICON, SM_CXCURSOR, SM_CYCURSOR, SM_CYMENU, SM_CXFULLSCREEN
    cdef int SM_CYFULLSCREEN, SM_CYKANJIWINDOW, SM_MOUSEPRESENT, SM_CYVSCROLL
    cdef int SM_CXHSCROLL, SM_DEBUG, SM_SWAPBUTTON, SM_RESERVED1
    cdef int SM_RESERVED2, SM_RESERVED3, SM_RESERVED4, SM_CXMIN
    cdef int SM_CYMIN, SM_CXSIZE, SM_CYSIZE, SM_CXFRAME, SM_CYFRAME
    cdef int SM_CXMINTRACK, SM_CYMINTRACK, SM_CXDOUBLECLK, SM_CYDOUBLECLK
    cdef int SM_CXICONSPACING, SM_CYICONSPACING, SM_MENUDROPALIGNMENT
    cdef int SM_PENWINDOWS, SM_DBCSENABLED, SM_CMOUSEBUTTONS, SM_CXFIXEDFRAME
    cdef int SM_CYFIXEDFRAME, SM_CXSIZEFRAME, SM_CYSIZEFRAME, SM_SECURE
    cdef int SM_CXEDGE, SM_CYEDGE, SM_CXMINSPACING, SM_CYMINSPACING
    cdef int SM_CXSMICON, SM_CYSMICON, SM_CYSMCAPTION, SM_CXSMSIZE
    cdef int SM_CYSMSIZE, SM_CXMENUSIZE, SM_CYMENUSIZE, SM_ARRANGE
    cdef int SM_CXMINIMIZED, SM_CYMINIMIZED, SM_CXMAXTRACK, SM_CYMAXTRACK
    cdef int SM_CXMAXIMIZED, SM_CYMAXIMIZED, SM_NETWORK, SM_CLEANBOOT
    cdef int SM_CXDRAG, SM_CYDRAG, SM_SHOWSOUNDS, SM_CXMENUCHECK
    cdef int SM_CYMENUCHECK, SM_SLOWMACHINE, SM_MIDEASTENABLED, SM_MOUSEWHEELPRESENT
    cdef int SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN
    cdef int SM_CYVIRTUALSCREEN, SM_CMONITORS, SM_SAMEDISPLAYFORMAT


class __CONSTDEF:
    pass


cdef class SystemMetrics:
    property CXSCREEN:
        def __get__(self):
            return GetSystemMetrics(SM_CXSCREEN)

    property CYSCREEN:
        def __get__(self):
            return GetSystemMetrics(SM_CYSCREEN)

    property CXVSCROLL:
        def __get__(self):
            return GetSystemMetrics(SM_CXVSCROLL)

    property CYHSCROLL:
        def __get__(self):
            return GetSystemMetrics(SM_CYHSCROLL)

    property CYCAPTION:
        def __get__(self):
            return GetSystemMetrics(SM_CYCAPTION)

    property CXBORDER:
        def __get__(self):
            return GetSystemMetrics(SM_CXBORDER)

    property CYBORDER:
        def __get__(self):
            return GetSystemMetrics(SM_CYBORDER)

    property CXDLGFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CXDLGFRAME)

    property CYDLGFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CYDLGFRAME)

    property CYVTHUMB:
        def __get__(self):
            return GetSystemMetrics(SM_CYVTHUMB)

    property CXHTHUMB:
        def __get__(self):
            return GetSystemMetrics(SM_CXHTHUMB)

    property CXICON:
        def __get__(self):
            return GetSystemMetrics(SM_CXICON)

    property CYICON:
        def __get__(self):
            return GetSystemMetrics(SM_CYICON)

    property CXCURSOR:
        def __get__(self):
            return GetSystemMetrics(SM_CXCURSOR)

    property CYCURSOR:
        def __get__(self):
            return GetSystemMetrics(SM_CYCURSOR)

    property CYMENU:
        def __get__(self):
            return GetSystemMetrics(SM_CYMENU)

    property CXFULLSCREEN:
        def __get__(self):
            return GetSystemMetrics(SM_CXFULLSCREEN)

    property CYFULLSCREEN:
        def __get__(self):
            return GetSystemMetrics(SM_CYFULLSCREEN)

    property CYKANJIWINDOW:
        def __get__(self):
            return GetSystemMetrics(SM_CYKANJIWINDOW)

    property MOUSEPRESENT:
        def __get__(self):
            return GetSystemMetrics(SM_MOUSEPRESENT)

    property CYVSCROLL:
        def __get__(self):
            return GetSystemMetrics(SM_CYVSCROLL)

    property CXHSCROLL:
        def __get__(self):
            return GetSystemMetrics(SM_CXHSCROLL)

    property DEBUG:
        def __get__(self):
            return GetSystemMetrics(SM_DEBUG)

    property SWAPBUTTON:
        def __get__(self):
            return GetSystemMetrics(SM_SWAPBUTTON)

    property RESERVED1:
        def __get__(self):
            return GetSystemMetrics(SM_RESERVED1)

    property RESERVED2:
        def __get__(self):
            return GetSystemMetrics(SM_RESERVED2)

    property RESERVED3:
        def __get__(self):
            return GetSystemMetrics(SM_RESERVED3)

    property RESERVED4:
        def __get__(self):
            return GetSystemMetrics(SM_RESERVED4)

    property CXMIN:
        def __get__(self):
            return GetSystemMetrics(SM_CXMIN)

    property CYMIN:
        def __get__(self):
            return GetSystemMetrics(SM_CYMIN)

    property CXSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CXSIZE)

    property CYSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CYSIZE)

    property CXFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CXFRAME)

    property CYFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CYFRAME)

    property CXMINTRACK:
        def __get__(self):
            return GetSystemMetrics(SM_CXMINTRACK)

    property CYMINTRACK:
        def __get__(self):
            return GetSystemMetrics(SM_CYMINTRACK)

    property CXDOUBLECLK:
        def __get__(self):
            return GetSystemMetrics(SM_CXDOUBLECLK)

    property CYDOUBLECLK:
        def __get__(self):
            return GetSystemMetrics(SM_CYDOUBLECLK)

    property CXICONSPACING:
        def __get__(self):
            return GetSystemMetrics(SM_CXICONSPACING)

    property CYICONSPACING:
        def __get__(self):
            return GetSystemMetrics(SM_CYICONSPACING)

    property MENUDROPALIGNMENT:
        def __get__(self):
            return GetSystemMetrics(SM_MENUDROPALIGNMENT)

    property PENWINDOWS:
        def __get__(self):
            return GetSystemMetrics(SM_PENWINDOWS)

    property DBCSENABLED:
        def __get__(self):
            return GetSystemMetrics(SM_DBCSENABLED)

    property CMOUSEBUTTONS:
        def __get__(self):
            return GetSystemMetrics(SM_CMOUSEBUTTONS)

    property CXFIXEDFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CXFIXEDFRAME)

    property CYFIXEDFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CYFIXEDFRAME)

    property CXSIZEFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CXSIZEFRAME)

    property CYSIZEFRAME:
        def __get__(self):
            return GetSystemMetrics(SM_CYSIZEFRAME)

    property SECURE:
        def __get__(self):
            return GetSystemMetrics(SM_SECURE)

    property CXEDGE:
        def __get__(self):
            return GetSystemMetrics(SM_CXEDGE)

    property CYEDGE:
        def __get__(self):
            return GetSystemMetrics(SM_CYEDGE)

    property CXMINSPACING:
        def __get__(self):
            return GetSystemMetrics(SM_CXMINSPACING)

    property CYMINSPACING:
        def __get__(self):
            return GetSystemMetrics(SM_CYMINSPACING)

    property CXSMICON:
        def __get__(self):
            return GetSystemMetrics(SM_CXSMICON)

    property CYSMICON:
        def __get__(self):
            return GetSystemMetrics(SM_CYSMICON)

    property CYSMCAPTION:
        def __get__(self):
            return GetSystemMetrics(SM_CYSMCAPTION)

    property CXSMSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CXSMSIZE)

    property CYSMSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CYSMSIZE)

    property CXMENUSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CXMENUSIZE)

    property CYMENUSIZE:
        def __get__(self):
            return GetSystemMetrics(SM_CYMENUSIZE)

    property ARRANGE:
        def __get__(self):
            return GetSystemMetrics(SM_ARRANGE)

    property CXMINIMIZED:
        def __get__(self):
            return GetSystemMetrics(SM_CXMINIMIZED)

    property CYMINIMIZED:
        def __get__(self):
            return GetSystemMetrics(SM_CYMINIMIZED)

    property CXMAXTRACK:
        def __get__(self):
            return GetSystemMetrics(SM_CXMAXTRACK)

    property CYMAXTRACK:
        def __get__(self):
            return GetSystemMetrics(SM_CYMAXTRACK)

    property CXMAXIMIZED:
        def __get__(self):
            return GetSystemMetrics(SM_CXMAXIMIZED)

    property CYMAXIMIZED:
        def __get__(self):
            return GetSystemMetrics(SM_CYMAXIMIZED)

    property NETWORK:
        def __get__(self):
            return GetSystemMetrics(SM_NETWORK)

    property CLEANBOOT:
        def __get__(self):
            return GetSystemMetrics(SM_CLEANBOOT)

    property CXDRAG:
        def __get__(self):
            return GetSystemMetrics(SM_CXDRAG)

    property CYDRAG:
        def __get__(self):
            return GetSystemMetrics(SM_CYDRAG)

    property SHOWSOUNDS:
        def __get__(self):
            return GetSystemMetrics(SM_SHOWSOUNDS)

    property CXMENUCHECK:
        def __get__(self):
            return GetSystemMetrics(SM_CXMENUCHECK)

    property CYMENUCHECK:
        def __get__(self):
            return GetSystemMetrics(SM_CYMENUCHECK)

    property SLOWMACHINE:
        def __get__(self):
            return GetSystemMetrics(SM_SLOWMACHINE)

    property MIDEASTENABLED:
        def __get__(self):
            return GetSystemMetrics(SM_MIDEASTENABLED)

#    property MOUSEWHEELPRESENT:
#        def __get__(self):
#            return GetSystemMetrics(SM_MOUSEWHEELPRESENT)

#    property XVIRTUALSCREEN:
#        def __get__(self):
#            return GetSystemMetrics(SM_XVIRTUALSCREEN)

#    property YVIRTUALSCREEN:
#        def __get__(self):
#            return GetSystemMetrics(SM_YVIRTUALSCREEN)

#    property CXVIRTUALSCREEN:
#        def __get__(self):
#            return GetSystemMetrics(SM_CXVIRTUALSCREEN)

#    property CYVIRTUALSCREEN:
#        def __get__(self):
#            return GetSystemMetrics(SM_CYVIRTUALSCREEN)

#    property CMONITORS:
#        def __get__(self):
#            return GetSystemMetrics(SM_CMONITORS)

#    property SAMEDISPLAYFORMAT:
#        def __get__(self):
#            return GetSystemMetrics(SM_SAMEDISPLAYFORMAT)



cdef extern from "windows.h":

    long GetSysColor(int index)
    
    cdef int COLOR_SCROLLBAR, COLOR_BACKGROUND, COLOR_ACTIVECAPTION
    cdef int COLOR_INACTIVECAPTION, COLOR_MENU, COLOR_WINDOW
    cdef int COLOR_WINDOWFRAME, COLOR_MENUTEXT, COLOR_WINDOWTEXT
    cdef int COLOR_CAPTIONTEXT, COLOR_ACTIVEBORDER, COLOR_INACTIVEBORDER
    cdef int COLOR_APPWORKSPACE, COLOR_HIGHLIGHT, COLOR_HIGHLIGHTTEXT
    cdef int COLOR_BTNFACE, COLOR_BTNSHADOW, COLOR_GRAYTEXT, COLOR_BTNTEXT
    cdef int COLOR_INACTIVECAPTIONTEXT, COLOR_BTNHIGHLIGHT, COLOR_3DDKSHADOW
    cdef int COLOR_3DLIGHT, COLOR_INFOTEXT, COLOR_INFOBK, COLOR_HOTLIGHT
    cdef int COLOR_GRADIENTACTIVECAPTION, COLOR_GRADIENTINACTIVECAPTION
    cdef int COLOR_DESKTOP, COLOR_3DFACE, COLOR_3DSHADOW, COLOR_3DHIGHLIGHT
    cdef int COLOR_3DHILIGHT, COLOR_BTNHILIGHT

cdef class SysColor:
    property scrollbar:
        def __get__(self):
            return GetSysColor(COLOR_SCROLLBAR)

    property background:
        def __get__(self):
            return GetSysColor(COLOR_BACKGROUND)

    property activecaption:
        def __get__(self):
            return GetSysColor(COLOR_ACTIVECAPTION)

    property inactivecaption:
        def __get__(self):
            return GetSysColor(COLOR_INACTIVECAPTION)

    property menu:
        def __get__(self):
            return GetSysColor(COLOR_MENU)

    property window:
        def __get__(self):
            return GetSysColor(COLOR_WINDOW)

    property windowframe:
        def __get__(self):
            return GetSysColor(COLOR_WINDOWFRAME)

    property menutext:
        def __get__(self):
            return GetSysColor(COLOR_MENUTEXT)

    property windowtext:
        def __get__(self):
            return GetSysColor(COLOR_WINDOWTEXT)

    property captiontext:
        def __get__(self):
            return GetSysColor(COLOR_CAPTIONTEXT)

    property activeborder:
        def __get__(self):
            return GetSysColor(COLOR_ACTIVEBORDER)

    property inactiveborder:
        def __get__(self):
            return GetSysColor(COLOR_INACTIVEBORDER)

    property appworkspace:
        def __get__(self):
            return GetSysColor(COLOR_APPWORKSPACE)

    property highlight:
        def __get__(self):
            return GetSysColor(COLOR_HIGHLIGHT)

    property highlighttext:
        def __get__(self):
            return GetSysColor(COLOR_HIGHLIGHTTEXT)

    property btnface:
        def __get__(self):
            return GetSysColor(COLOR_BTNFACE)

    property btnshadow:
        def __get__(self):
            return GetSysColor(COLOR_BTNSHADOW)

    property graytext:
        def __get__(self):
            return GetSysColor(COLOR_GRAYTEXT)

    property btntext:
        def __get__(self):
            return GetSysColor(COLOR_BTNTEXT)

    property inactivecaptiontext:
        def __get__(self):
            return GetSysColor(COLOR_INACTIVECAPTIONTEXT)

    property btnhighlight:
        def __get__(self):
            return GetSysColor(COLOR_BTNHIGHLIGHT)

    property threeddkshadow:
        def __get__(self):
            return GetSysColor(COLOR_3DDKSHADOW)

    property threedlight:
        def __get__(self):
            return GetSysColor(COLOR_3DLIGHT)

    property infotext:
        def __get__(self):
            return GetSysColor(COLOR_INFOTEXT)

    property infobk:
        def __get__(self):
            return GetSysColor(COLOR_INFOBK)

#    property hotlight:
#        def __get__(self):
#            return GetSysColor(COLOR_HOTLIGHT)
#
#    property gradientactivecaption:
#        def __get__(self):
#            return GetSysColor(COLOR_GRADIENTACTIVECAPTION)
#
#    property gradientinactivecaption:
#        def __get__(self):
#            return GetSysColor(COLOR_GRADIENTINACTIVECAPTION)
#
    property desktop:
        def __get__(self):
            return GetSysColor(COLOR_DESKTOP)

    property threedface:
        def __get__(self):
            return GetSysColor(COLOR_3DFACE)

    property threedshadow:
        def __get__(self):
            return GetSysColor(COLOR_3DSHADOW)

    property threedhighlight:
        def __get__(self):
            return GetSysColor(COLOR_3DHIGHLIGHT)

    property threedhilight:
        def __get__(self):
            return GetSysColor(COLOR_3DHILIGHT)

    property btnhilight:
        def __get__(self):
            return GetSysColor(COLOR_BTNHILIGHT)


cdef extern from "windows.h":
    UINT RegisterClipboardFormat(TCHAR *lpszFormat)






    
cdef extern from "windows.h":
    BOOL GetKeyboardState(char *)
    int GetKeyNameTextW(LONG lParam,LPTSTR lpString,int nSize)
    UINT MapVirtualKey(UINT uCode, UINT uMapType)

def getKeyboardState():
    cdef char buf[256]
    GetKeyboardState(buf)
    ret = []
    for i from 0 <= i < 256: 
        ret.append(buf[i])
    return ret

def mapVirtualKey(virtualkey=None, scancode=None):
    cdef UINT uCode, uMapType
    
    if virtualkey is not None:
        uCode = virtualkey
        uMapType = 0
    elif scancode is not None:
        uCode = scancode
        uMapType = 1
    else:
        raise ValueError()
    
    return MapVirtualKey(uCode, uMapType)

def getKeynameText(scancode, extended, dontcare):
    cdef LPARAM lparam
    cdef PYMFC_WCHAR name[256]
    cdef int retlen
    
    lparam = scancode
    lparam = (lparam << 16) & 0x00ff0000
    if extended:
        lparam = lparam | 0x01000000
    if dontcare:
        lparam = lparam | 0x02000000

    retlen = GetKeyNameTextW(lparam, name, 256)
    if not retlen:
        return None
    return PyUnicode_FromWideChar(name, retlen)
    

cdef extern from "windows.h":
    int ToAscii(UINT uVirtKey, UINT uScanCode, char *lpKeyState, WORD *lpChar, UINT uFlags)

def toAscii(virtKey, scanCode, keyState, isMenu):
    cdef WORD c
    cdef char state[256], c1
    cdef char c2[2]
    cdef int char_state, convlen
    
    for i from 0 <= i < 256: 
        char_state = keyState[i]
        state[i] = <char>char_state
    
    convlen = ToAscii(virtKey, scanCode, state, &c, isMenu)
    if convlen == 1:
        c1 = <char>(c & 0xff)
        return PyString_FromStringAndSize(&c1, 1)
    elif convlen == 2:
        c2[0] = <char>((c >> 8) & 0xff)
        c2[1] = <char>(c & 0xff)
        return PyString_FromStringAndSize(c2, 2)


def setTimer(elapse, wnd=0, idEvent=0):
    cdef HWND hWnd
    if wnd:
        hWnd = PyMFCHandle_AsHandle(wnd.getHwnd())
    else:
        hWnd = NULL
    
    ret = SetTimer(hWnd, idEvent, elapse, NULL)
    if not ret:
        pymRaiseWin32Err()
    return ret
    
def killTimer(wnd=0, idEvent=0):
    cdef HWND hWnd
    if wnd:
        hWnd = PyMFCHandle_AsHandle(wnd.getHwnd())
    else:
        hWnd = NULL
    
    return KillTimer(hWnd, idEvent)




cdef class ClipFormat:
    cdef public int format

    property text:
        def __get__(self):
            return self.format == CF_TEXT
        def __set__(self, v):
            if v:
                self.format = CF_TEXT
            else:
                self.format = 0

    property bitmap:
        def __get__(self):
            return self.format == CF_BITMAP
        def __set__(self, v):
            if v:
                self.format = CF_BITMAP
            else:
                self.format = 0

    property metafilepict:
        def __get__(self):
            return self.format == CF_METAFILEPICT
        def __set__(self, v):
            if v:
                self.format = CF_METAFILEPICT
            else:
                self.format = 0

    property sylk:
        def __get__(self):
            return self.format == CF_SYLK
        def __set__(self, v):
            if v:
                self.format = CF_SYLK
            else:
                self.format = 0

    property dif:
        def __get__(self):
            return self.format == CF_DIF
        def __set__(self, v):
            if v:
                self.format = CF_DIF
            else:
                self.format = 0

    property tiff:
        def __get__(self):
            return self.format == CF_TIFF
        def __set__(self, v):
            if v:
                self.format = CF_TIFF
            else:
                self.format = 0

    property oemtext:
        def __get__(self):
            return self.format == CF_OEMTEXT
        def __set__(self, v):
            if v:
                self.format = CF_OEMTEXT
            else:
                self.format = 0

    property dib:
        def __get__(self):
            return self.format == CF_DIB
        def __set__(self, v):
            if v:
                self.format = CF_DIB
            else:
                self.format = 0

    property palette:
        def __get__(self):
            return self.format == CF_PALETTE
        def __set__(self, v):
            if v:
                self.format = CF_PALETTE
            else:
                self.format = 0

    property pendata:
        def __get__(self):
            return self.format == CF_PENDATA
        def __set__(self, v):
            if v:
                self.format = CF_PENDATA
            else:
                self.format = 0

    property riff:
        def __get__(self):
            return self.format == CF_RIFF
        def __set__(self, v):
            if v:
                self.format = CF_RIFF
            else:
                self.format = 0

    property wave:
        def __get__(self):
            return self.format == CF_WAVE
        def __set__(self, v):
            if v:
                self.format = CF_WAVE
            else:
                self.format = 0

    property unicodetext:
        def __get__(self):
            return self.format == CF_UNICODETEXT
        def __set__(self, v):
            if v:
                self.format = CF_UNICODETEXT
            else:
                self.format = 0

    property enhmetafile:
        def __get__(self):
            return self.format == CF_ENHMETAFILE
        def __set__(self, v):
            if v:
                self.format = CF_ENHMETAFILE
            else:
                self.format = 0

    property hdrop:
        def __get__(self):
            return self.format == CF_HDROP
        def __set__(self, v):
            if v:
                self.format = CF_HDROP
            else:
                self.format = 0

    property locale:
        def __get__(self):
            return self.format == CF_LOCALE
        def __set__(self, v):
            if v:
                self.format = CF_LOCALE
            else:
                self.format = 0

    property shellidlist:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_SHELLIDLIST)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_SHELLIDLIST)
            else:
                self.format = 0

    property shellidlistoffset:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_SHELLIDLISTOFFSET)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_SHELLIDLISTOFFSET)
            else:
                self.format = 0

    property netresources:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_NETRESOURCES)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_NETRESOURCES)
            else:
                self.format = 0

    property filedescriptor:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_FILEDESCRIPTORW)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_FILEDESCRIPTORW)
            else:
                self.format = 0

    property filecontents:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_FILECONTENTS)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_FILECONTENTS)
            else:
                self.format = 0

    property filename:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_FILENAMEW)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_FILENAMEW)
            else:
                self.format = 0

    property printergroup:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_PRINTERGROUP)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_PRINTERGROUP)
            else:
                self.format = 0

    property filenamemap:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_FILENAMEMAPW)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_FILENAMEMAPW)
            else:
                self.format = 0

    property shellurl:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_SHELLURL)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_SHELLURL)
            else:
                self.format = 0

    property ineturl:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_INETURLW)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_INETURLW)
            else:
                self.format = 0

    property preferreddropeffect:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_PREFERREDDROPEFFECT)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_PREFERREDDROPEFFECT)
            else:
                self.format = 0

    property performeddropeffect:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_PERFORMEDDROPEFFECT)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_PERFORMEDDROPEFFECT)
            else:
                self.format = 0

    property pastesucceeded:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_PASTESUCCEEDED)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_PASTESUCCEEDED)
            else:
                self.format = 0

    property indragloop:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_INDRAGLOOP)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_INDRAGLOOP)
            else:
                self.format = 0

    property mountedvolume:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_MOUNTEDVOLUME)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_MOUNTEDVOLUME)
            else:
                self.format = 0

    property persisteddataobject:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_PERSISTEDDATAOBJECT)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_PERSISTEDDATAOBJECT)
            else:
                self.format = 0

    property targetclsid:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_TARGETCLSID)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_TARGETCLSID)
            else:
                self.format = 0

    property logicalperformeddropeffect:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_LOGICALPERFORMEDDROPEFFECT)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_LOGICALPERFORMEDDROPEFFECT)
            else:
                self.format = 0

    property autoplay_shellidlists:
        def __get__(self):
            return self.format == RegisterClipboardFormat(CFSTR_AUTOPLAY_SHELLIDLISTS)
        def __set__(self, v):
            if v:
                self.format = RegisterClipboardFormat(CFSTR_AUTOPLAY_SHELLIDLISTS)
            else:
                self.format = 0

    def __init__(self, **kwargs):
        if len(kwargs) != 1:
            raise TypeError("ClipFormat() takes exactly one argument");
        
        for name, value in kwargs.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                name = unicode(name, "mbcs")
                self.format = RegisterClipboardFormat(PyUnicode_AsUnicode(name))

    def __int__(self):
        return self.format



cdef extern from "windows.h":

    ctypedef struct SHFILEINFO:
        void *hIcon
        int   iIcon 
        DWORD dwAttributes
        TCHAR szDisplayName[MAX_PATH]
        TCHAR szTypeName[80]

    DWORD SHGetFileInfo(TCHAR *pszPath, DWORD dwFileAttributes, SHFILEINFO *psfi, UINT cbFileInfo, UINT uFlags)

    int SHGFI_ATTR_SPECIFIED, SHGFI_ATTRIBUTES, SHGFI_DISPLAYNAME
    int SHGFI_EXETYPE, SHGFI_ICON, SHGFI_ICONLOCATION, SHGFI_LARGEICON
    int SHGFI_LINKOVERLAY, SHGFI_OPENICON, SHGFI_PIDL, SHGFI_SELECTED
    int SHGFI_SHELLICONSIZE, SHGFI_SMALLICON, SHGFI_SYSICONINDEX
    int SHGFI_TYPENAME, SHGFI_USEFILEATTRIBUTES


def shGetFileInfo(path, 
    int largeicon=0, int smallicon=0, int usefileattributes=0, 
    int sysiconindex=0, int displayname=0, int typename=0,
    int exetype=0):

    cdef UINT f
    cdef SHFILEINFO fi
    cdef DWORD ret
    
    f = 0
    if largeicon != 0:
        f = f | SHGFI_LARGEICON
    if smallicon != 0:
        f = f | SHGFI_SMALLICON
    if (largeicon != 0 or smallicon != 0) and (sysiconindex == 0):
        f = f | SHGFI_ICON
    if usefileattributes != 0:
        f = f | SHGFI_USEFILEATTRIBUTES
    if displayname != 0:
        f = f | SHGFI_DISPLAYNAME
    if typename != 0:
        f = f | SHGFI_TYPENAME
    if sysiconindex != 0:
        f = f | SHGFI_SYSICONINDEX
    if exetype != 0:
        f = f | SHGFI_EXETYPE
    ret = SHGetFileInfo(PyUnicode_AsUnicode(path), 0, &fi, sizeof(fi), f)
    
    if exetype==0 and sysiconindex==0 and ret==0:
        pymRaiseWin32Err()
        
    if sysiconindex != 0:
        return fi.iIcon
        
    if (largeicon != 0 or smallicon != 0) and (sysiconindex == 0):
        import pymfc
        iconobj = pymfc.gdi.Icon(hIcon=PyMFCHandle_FromHandle(fi.hIcon), own=1)
#        iconobj = pymfc.gdi.Icon(hIcon=<unsigned long>fi.hIcon, own=1)
        return iconobj
    
    if displayname != 0:
        return _fromWideChar(fi.szDisplayName)
    
    if typename != 0:
        return _fromWideChar(fi.szTypeName)

    if exetype != 0:
        return ret != 0
        
cdef extern from "shlobj.h":

    BOOL pymShGetSpecialFolderPath(HWND hWnd, TCHAR *buf, int nFolder, BOOL fCreate) except 0
    # CSIDL
    cdef ULONG CSIDL_DESKTOP, CSIDL_INTERNET, CSIDL_PROGRAMS
    cdef ULONG CSIDL_CONTROLS, CSIDL_PRINTERS, CSIDL_PERSONAL
    cdef ULONG CSIDL_FAVORITES, CSIDL_STARTUP, CSIDL_RECENT, CSIDL_SENDTO
    cdef ULONG CSIDL_BITBUCKET, CSIDL_STARTMENU, CSIDL_DESKTOPDIRECTORY
    cdef ULONG CSIDL_DRIVES, CSIDL_NETWORK, CSIDL_NETHOOD, CSIDL_FONTS
    cdef ULONG CSIDL_TEMPLATES, CSIDL_COMMON_STARTMENU
    cdef ULONG CSIDL_COMMON_PROGRAMS, CSIDL_COMMON_STARTUP
    cdef ULONG CSIDL_COMMON_DESKTOPDIRECTORY, CSIDL_APPDATA
    cdef ULONG CSIDL_PRINTHOOD, CSIDL_ALTSTARTUP, CSIDL_COMMON_ALTSTARTUP
    cdef ULONG CSIDL_COMMON_FAVORITES, CSIDL_INTERNET_CACHE, CSIDL_COOKIES
    cdef ULONG CSIDL_HISTORY


cdef void __init_csidl(obj):
    obj.desktop = CSIDL_DESKTOP
    obj.internet = CSIDL_INTERNET
    obj.programs = CSIDL_PROGRAMS
    obj.controls = CSIDL_CONTROLS
    obj.printers = CSIDL_PRINTERS
    obj.personal = CSIDL_PERSONAL
    obj.favorites = CSIDL_FAVORITES
    obj.startup = CSIDL_STARTUP
    obj.recent = CSIDL_RECENT
    obj.sendto = CSIDL_SENDTO
    obj.bitbucket = CSIDL_BITBUCKET
    obj.startmenu = CSIDL_STARTMENU
    obj.desktopdirectory = CSIDL_DESKTOPDIRECTORY
    obj.drives = CSIDL_DRIVES
    obj.network = CSIDL_NETWORK
    obj.nethood = CSIDL_NETHOOD
    obj.fonts = CSIDL_FONTS
    obj.templates = CSIDL_TEMPLATES
    obj.common_startmenu = CSIDL_COMMON_STARTMENU
    obj.common_programs = CSIDL_COMMON_PROGRAMS
    obj.common_startup = CSIDL_COMMON_STARTUP
    obj.common_desktopdirectory = CSIDL_COMMON_DESKTOPDIRECTORY
    obj.appdata = CSIDL_APPDATA
    obj.printhood = CSIDL_PRINTHOOD
    obj.altstartup = CSIDL_ALTSTARTUP
    obj.common_altstartup = CSIDL_COMMON_ALTSTARTUP
    obj.common_favorites = CSIDL_COMMON_FAVORITES
    obj.internet_cache = CSIDL_INTERNET_CACHE
    obj.cookies = CSIDL_COOKIES
    obj.history = CSIDL_HISTORY

CSIDL = __CONSTDEF()
__init_csidl(CSIDL)


def shGetSpecialFolderPath(wnd, csidl, create):
    cdef HWND hwnd
    cdef TCHAR ret[MAX_PATH]
    
    hwnd = NULL
    if wnd:
        hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
    
    pymShGetSpecialFolderPath(hwnd, ret, csidl, create)
    return _fromWideChar(ret)



cdef extern from "windows.h":
    cdef ULONG SEE_MASK_CLASSNAME, SEE_MASK_CLASSKEY, SEE_MASK_IDLIST,
    cdef ULONG SEE_MASK_INVOKEIDLIST, SEE_MASK_ICON, SEE_MASK_HOTKEY,
    cdef ULONG SEE_MASK_NOCLOSEPROCESS, SEE_MASK_CONNECTNETDRV,
    cdef ULONG SEE_MASK_FLAG_DDEWAIT, SEE_MASK_DOENVSUBST,
    cdef ULONG SEE_MASK_FLAG_NO_UI, SEE_MASK_UNICODE, SEE_MASK_NO_CONSOLE,
    cdef ULONG SEE_MASK_ASYNCOK, SEE_MASK_HMONITOR

    ctypedef struct SHELLEXECUTEINFOW:
        DWORD cbSize
        ULONG fMask
        HWND hwnd
        LPCTSTR   lpVerb
        LPCTSTR   lpFile
        LPCTSTR   lpParameters
        LPCTSTR   lpDirectory
        int nShow
        HINSTANCE hInstApp
        LPVOID lpIDList
        LPCSTR   lpClass
        HKEY hkeyClass
        DWORD dwHotKey
        HANDLE hIconMonitor
        HANDLE hMonitor
        HANDLE hProcess

    BOOL pymShellExecute(SHELLEXECUTEINFOW *se) except 0

def shellExecute(verb, file, param, dir, wnd=None,
        hide=0, maximize=0, minimize=0, restore=0, show=0,
        showdefault=0, showmaximized=0, showminimized=0,
        showminnoactive=0, showna=0, shownoactivate=0, shownormal=0,
        classname=0, classkey=0, idlist=0, invokeidlist=0, icon=0,
        hotkey=0, nocloseprocess=0, connectnetdrv=0, ddewait=0,
        doenvsubst=0, noui=0, unicode=0, noconsole=0, asyncok=0, 
        hmonitor=0):
    
    cdef SHELLEXECUTEINFOW se

    memset(&se, 0, sizeof(se))
    se.cbSize = sizeof(se)
    if classname:
        se.fMask = se.fMask|SEE_MASK_CLASSNAME
        se.lpClass = <LPCSTR>PyUnicode_AsUnicode(classname)

    if classkey:
        se.fMask = se.fMask | SEE_MASK_CLASSKEY
        se.hkeyClass = PyLong_AsVoidPtr(int(classkey))
        
    if idlist:
        se.fMask = se.fMask| SEE_MASK_IDLIST
    if invokeidlist:
        se.fMask = se.fMask| SEE_MASK_INVOKEIDLIST
    if icon:
        se.fMask = se.fMask| SEE_MASK_ICON
    if hotkey:
        se.fMask = se.fMask| SEE_MASK_HOTKEY
    if nocloseprocess:
        se.fMask = se.fMask| SEE_MASK_NOCLOSEPROCESS
    if connectnetdrv:
        se.fMask = se.fMask| SEE_MASK_CONNECTNETDRV
    if ddewait:
        se.fMask = se.fMask| SEE_MASK_FLAG_DDEWAIT
    if doenvsubst:
        se.fMask = se.fMask| SEE_MASK_DOENVSUBST
    if noui:
        se.fMask = se.fMask| SEE_MASK_FLAG_NO_UI
    if unicode:
        se.fMask = se.fMask| SEE_MASK_UNICODE
    if noconsole:
        se.fMask = se.fMask| SEE_MASK_NO_CONSOLE
    if asyncok:
        se.fMask = se.fMask| SEE_MASK_ASYNCOK
    if hmonitor:
        se.fMask = se.fMask| SEE_MASK_HMONITOR

    if wnd:
        hwnd = wnd.getHwnd()
        se.hwnd = PyMFCHandle_AsHandle(hwnd)

    se.lpVerb = PyUnicode_AsUnicode(verb)
    se.lpFile = PyUnicode_AsUnicode(file)
    se.lpParameters = PyUnicode_AsUnicode(param)
    se.lpDirectory = PyUnicode_AsUnicode(dir)

    if hide:
        se.nShow = SW_HIDE
    elif maximize:
        se.nShow = SW_MAXIMIZE
    elif minimize:
        se.nShow = SW_MINIMIZE
    elif restore:
        se.nShow = SW_RESTORE
    elif show:
        se.nShow = SW_SHOW
    elif showdefault:
        se.nShow = SW_SHOWDEFAULT
    elif showmaximized:
        se.nShow = SW_SHOWMAXIMIZED
    elif showminimized:
        se.nShow = SW_SHOWMINIMIZED
    elif showminnoactive:
        se.nShow = SW_SHOWMINNOACTIVE
    elif showna:
        se.nShow = SW_SHOWNA
    elif shownoactivate:
        se.nShow = SW_SHOWNOACTIVATE
    elif shownormal:
        se.nShow = SW_SHOWNORMAL

    pymShellExecute(&se)

    if nocloseprocess:
        if se.hProcess:
            return WinHandle(handle=PyMFCHandle_FromHandle(se.hProcess), own=1)


cdef extern from "windows.h":
#    cdef ULONG SEE_MASK_CLASSNAME, SEE_MASK_CLASSKEY, SEE_MASK_IDLIST,

    ctypedef struct SECURITY_ATTRIBUTES:
        DWORD nLength
        LPVOID lpSecurityDescriptor
        BOOL bInheritHandle
    
    ctypedef SECURITY_ATTRIBUTES *LPSECURITY_ATTRIBUTES
    
    ctypedef struct STARTUPINFO:
        DWORD cb
        LPTSTR lpReserved
        LPTSTR lpDesktop
        LPTSTR lpTitle
        DWORD dwX
        DWORD dwY
        DWORD dwXSize
        DWORD dwYSize
        DWORD dwXCountChars
        DWORD dwYCountChars
        DWORD dwFillAttribute
        DWORD dwFlags
        WORD wShowWindow
        WORD cbReserved2
        LPBYTE lpReserved2
        HANDLE hStdInput
        HANDLE hStdOutput
        HANDLE hStdError
    ctypedef STARTUPINFO *LPSTARTUPINFO
    
    
    ctypedef struct PROCESS_INFORMATION:
        HANDLE hProcess
        HANDLE hThread
        DWORD dwProcessId
        DWORD dwThreadId

    ctypedef PROCESS_INFORMATION *LPPROCESS_INFORMATION

    BOOL CreateProcessW(
        LPCTSTR lpApplicationName,
        LPTSTR lpCommandLine,
        LPSECURITY_ATTRIBUTES lpProcessAttributes,
        LPSECURITY_ATTRIBUTES lpThreadAttributes,
        BOOL bInheritHandles,
        DWORD dwCreationFlags,
        LPVOID lpEnvironment,
        LPCTSTR lpCurrentDirectory,
        LPSTARTUPINFO lpStartupInfo,
        LPPROCESS_INFORMATION lpProcessInformation
    ) nogil


def createProcess(appname, commandline=None, curdir=None):
    cdef STARTUPINFO si
    cdef PROCESS_INFORMATION pi
    cdef LPTSTR lpappname, lpcommandline, lpcurdir
    cdef int cmdlen
    cdef BOOL ret
    
    memset(&si, 0, sizeof(si))
    si.cb = sizeof(si)
    memset(&pi, 0, sizeof(pi))
    
    lpcurdir = NULL
    if curdir is not None:
        lpcurdir = PyUnicode_AsUnicode(appname)
        
    lpappname = NULL
    if appname is not None:
        lpappname = PyUnicode_AsUnicode(appname)

    lpcommandline = NULL
    if commandline is not None:
        cmdlen = len(commandline)
        lpcommandline = <LPTSTR>malloc((cmdlen+1)*sizeof(TCHAR))
        if not lpcommandline:
            raise MemoryError()
        memcpy(lpcommandline, PyUnicode_AsUnicode(commandline), cmdlen*sizeof(TCHAR))
        lpcommandline[cmdlen] = 0

    try:
        with nogil:
            ret = CreateProcessW(lpappname, lpcommandline, NULL, NULL, 0, 0, NULL, lpcurdir, &si, &pi)
        if not ret:
            pymRaiseWin32Err()

        hprocess = WinHandle(handle=PyMFCHandle_FromHandle(pi.hProcess), own=1)
        hthread = WinHandle(handle=PyMFCHandle_FromHandle(pi.hThread), own=1)
        
        return (hprocess, hthread)
        
    finally:
        free(lpcommandline)
    
    
cdef extern from "objbase.h":
    HRESULT GetClassFile(LPTSTR filename, CLSID *pclsid)
    HRESULT ProgIDFromCLSID(CLSID *clsid, LPTSTR *lplpszProgID)
    HRESULT OleRegGetUserType(CLSID *clsid, DWORD dwFormOfType, LPTSTR * pszUserType)
    cdef int USERCLASSTYPE_FULL, USERCLASSTYPE_SHORT, USERCLASSTYPE_APPNAME

    void *CoTaskMemAlloc(ULONG cb)
    void CoTaskMemFree(void *pv)
    
    
def getClassFile(filename):
    cdef HRESULT hr
    cdef CLSID clsid
    
    hr = GetClassFile(PyUnicode_AsUnicode(filename), &clsid)
    if FAILED(hr):
        pymRaiseWin32Errcode(hr)
    return PyString_FromStringAndSize(<char *>(&clsid), sizeof(CLSID))

def progIDFromCLSID(clsid):
    cdef HRESULT hr
    cdef CLSID _clsid
    cdef char *buf
    cdef int length
    cdef PYMFC_WCHAR *progid
    
    PyString_AsStringAndSize(clsid, &buf, &length)
    memcpy(&_clsid, buf, sizeof(_clsid))
    
    hr = ProgIDFromCLSID(&_clsid, &progid)
    if FAILED(hr):
        pymRaiseWin32Errcode(hr)
    try:
        ret = PyUnicode_FromWideChar(progid, wcslen(progid))
    finally:
        CoTaskMemFree(progid)
    return ret
    

def oleRegGetUserType(clsid, fullname=0, shortname=0, appname=0):
    cdef DWORD formOfType
    cdef HRESULT hr
    cdef CLSID _clsid
    cdef char *buf
    cdef int length
    cdef PYMFC_WCHAR *userType
    
    if fullname:
        formOfType = USERCLASSTYPE_FULL
    elif shortname:
        formOfType = USERCLASSTYPE_SHORT
    else:
        formOfType = USERCLASSTYPE_APPNAME
    
    PyString_AsStringAndSize(clsid, &buf, &length)
    memcpy(&_clsid, buf, sizeof(_clsid))

    hr = OleRegGetUserType(&_clsid, formOfType, &userType)
    if FAILED(hr):
        pymRaiseWin32Errcode(hr)
    try:
        ret = PyUnicode_FromWideChar(userType, wcslen(userType))
    finally:
        CoTaskMemFree(userType)
    return ret
    

cdef extern from "windows.h":
    ctypedef struct TIME_ZONE_INFORMATION:
        LONG Bias
        WCHAR StandardName[32]
        SYSTEMTIME StandardDate
        LONG StandardBias
        WCHAR DaylightName[32]
        SYSTEMTIME DaylightDate
        LONG DaylightBias

    DWORD GetTimeZoneInformation(TIME_ZONE_INFORMATION *lpTimeZoneInformation)

    cdef int TIME_ZONE_ID_INVALID, TIME_ZONE_ID_UNKNOWN, TIME_ZONE_ID_STANDARD, TIME_ZONE_ID_DAYLIGHT

from datetime import tzinfo, timedelta
class Win32TZInfo(tzinfo):
    def __init__(self):
        cdef TIME_ZONE_INFORMATION tz
        ret = GetTimeZoneInformation(&tz)
        if ret ==  TIME_ZONE_ID_INVALID:
            pymRaiseWin32Err()
        
        self._offset = timedelta(minutes=tz.Bias*-1)
        if ret == TIME_ZONE_ID_DAYLIGHT:
            self._dstoffset = minutes=timedelta(minutes=tz.DaylightBias*-1)
            self._tzname = PyUnicode_FromWideChar(tz.StandardName, wcslen(tz.DaylightName)).encode("mbcs")
        else:
            self._dstoffset = timedelta(minutes=0)
            self._tzname = PyUnicode_FromWideChar(tz.StandardName, wcslen(tz.StandardName)).encode("mbcs")

    def utcoffset(self, dt):
        return self._offset+self._dstoffset
        
    def dst(self, dt):
        return self._dstoffset
        
    def tzname(self, dt):
        return self._tzname

cdef extern from "windows.h":
    BOOL GetComputerName(TCHAR *buffer, DWORD *size)
    BOOL GetUserName(TCHAR *buffer, DWORD *size)
    
def getComputerName():
    cdef WCHAR buffer[MAX_COMPUTERNAME_LENGTH+1]
    cdef DWORD size

    size = MAX_COMPUTERNAME_LENGTH+1
    if 0 == GetComputerName(buffer, &size):
        pymRaiseWin32Err()
    return PyUnicode_FromWideChar(buffer, wcslen(buffer))
    

def getUserName():
    cdef WCHAR buffer[MAX_COMPUTERNAME_LENGTH+1]
    cdef DWORD size

    size = MAX_COMPUTERNAME_LENGTH+1
    if 0 == GetUserName(buffer, &size):
        pymRaiseWin32Err()
    return PyUnicode_FromWideChar(buffer, wcslen(buffer))
    

cdef extern from "windows.h":
    DWORD GetFileAttributes(LPTSTR lpFileName)
    DWORD SetFileAttributes(LPTSTR lpFileName, DWORD dwFileAttributes)

    cdef int FILE_ATTRIBUTE_ARCHIVE, FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_NORMAL
    cdef int FILE_ATTRIBUTE_NOT_CONTENT_INDEXED, FILE_ATTRIBUTE_OFFLINE, FILE_ATTRIBUTE_READONLY
    cdef int FILE_ATTRIBUTE_SYSTEM, FILE_ATTRIBUTE_TEMPORARY
    cdef int INVALID_FILE_ATTRIBUTES

def getFileAttribute(filename):
    cdef DWORD ret
    ret = GetFileAttributes(PyUnicode_AsUnicode(filename)) 
    if ret == INVALID_FILE_ATTRIBUTES:
        pymRaiseWin32Err()
    return ret
    
def setFileAttribute(filename, attr=0, archive=None, normal=None, readonly=None, hidden=None, system=None, temporary=None):
    cdef DWORD newattr
    newattr = attr

    if normal is not None:
        newattr = FILE_ATTRIBUTE_NORMAL
    else:
        if archive is not None:
            if archive:
                newattr = newattr | FILE_ATTRIBUTE_ARCHIVE
            else:
                newattr = newattr & ~FILE_ATTRIBUTE_ARCHIVE

        if hidden is not None:
            if hidden:
                newattr = newattr | FILE_ATTRIBUTE_HIDDEN
            else:
                newattr = newattr & ~FILE_ATTRIBUTE_HIDDEN

        if readonly is not None:
            if readonly:
                newattr = newattr | FILE_ATTRIBUTE_READONLY
            else:
                newattr = newattr & ~FILE_ATTRIBUTE_READONLY

        if system is not None:
            if system:
                newattr = newattr | FILE_ATTRIBUTE_SYSTEM
            else:
                newattr = newattr & ~FILE_ATTRIBUTE_SYSTEM

        if temporary is not None:
            if temporary:
                newattr = newattr | FILE_ATTRIBUTE_TEMPORARY
            else:
                newattr = newattr & ~FILE_ATTRIBUTE_TEMPORARY

    if not SetFileAttributes(PyUnicode_AsUnicode(filename), newattr):
        pymRaiseWin32Err()
        



cdef extern from "windows.h":
    enum:
        STARTF_USESHOWWINDOW
        
    void GetStartupInfo(STARTUPINFO *si)

cdef class StartupInfo:
    cdef STARTUPINFO _si
    
    property hide:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_HIDE)
    property maximize:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_MAXIMIZE)
    property minimize:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_MINIMIZE)
    property restore:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_RESTORE)
    property show:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOW)
    property showmaximized:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWMAXIMIZED)
    property showminimized:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWMINIMIZED)
    property showminnoactive:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWMINNOACTIVE)
    property showna:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWNA)
    property shownoactivate:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWNOACTIVATE)
    property shownormal:
        def __get__(self):
            return (self._si.dwFlags & STARTF_USESHOWWINDOW) and (self._si.wShowWindow == SW_SHOWNORMAL)

    def __init__(self):
        self._si.cb = sizeof(self._si)
        
def getStartupInfo():
    cdef StartupInfo si
    si = StartupInfo()
    
    GetStartupInfo(&si._si)
    return si


cdef extern from "windows.h":
    DWORD ExpandEnvironmentStringsW(LPCTSTR lpSrc, LPTSTR lpDst, DWORD nSize)
    LANGID GetUserDefaultLangID()
    DWORD GetFileVersionInfoSizeW(LPCTSTR lptstrFilename, LPDWORD lpdwHandle)
    BOOL GetFileVersionInfoW(LPCTSTR lptstrFilename, DWORD dwHandle, DWORD dwLen, LPVOID lpData)
    BOOL VerQueryValueW(LPCVOID pBlock, LPCTSTR lpSubBlock, LPVOID *lplpBuffer,PUINT puLen)
    
def expandEnvironmentStrings(src):
    cdef PYMFC_WCHAR *wsrc
    cdef DWORD ret
    cdef LPTSTR dest
    
    wsrc = PyUnicode_AsUnicode(src)
    ret = ExpandEnvironmentStringsW(wsrc, NULL, 0)
    if ret == 0:
        pymRaiseWin32Err()
    
    dest = <LPTSTR>malloc((ret+1)*sizeof(TCHAR))
    if dest == NULL:
        raise MemoryError()
    try:
        ret = ExpandEnvironmentStringsW(wsrc, dest, ret)
        if ret == 0:
            pymRaiseWin32Err()
        return _fromWideChar(dest)
    finally:
        free(dest)
    
def getUserDefaultLangID():
    return GetUserDefaultLangID()


#def getFileVersionInfo(filename, subblock):
#    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#    # Doesn't work for "\VarFileInfo\Translation" subblock
#    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#    
#    cdef DWORD size, handle
#    cdef BOOL ret
#    cdef void *data
#    cdef LPTSTR fname
#    cdef void *buf
#    cdef unsigned int retlen
#    
#    fname = PyUnicode_AsUnicode(filename)
#    handle = 0
#    
#    size = GetFileVersionInfoSizeW(fname, &handle)
#    if not size:
#        pymRaiseWin32Err()
#    
#    data = <LPTSTR>malloc(size)
#    if data == NULL:
#        raise MemoryError()
#    try:
#        ret = GetFileVersionInfoW(fname, handle, size, data)
#        if ret == 0:
#            pymRaiseWin32Err()
#        
#        ret = VerQueryValueW(data, PyUnicode_AsUnicode(subblock), &buf, &retlen)
#        if not ret:
#            pymRaiseWin32Err()
#        return PyUnicode_FromWideChar(<TCHAR*>buf, retlen)
#    finally:
#        free(data)
#    
#    
#    return ret

cdef extern from "windows.h":
    BOOL OpenPrinter(LPTSTR pPrinterName, HANDLE *phPrinter, void* pDefault)
    BOOL ClosePrinter(HANDLE hPrinter)
    LONG DocumentProperties(HWND hWnd, HANDLE hPrinter, LPTSTR pDeviceName,
                    DEVMODE *pDevModeOutput, DEVMODE *pDevModeInput, DWORD fMode)

    cdef int DM_IN_BUFFER, DM_IN_PROMPT, DM_OUT_BUFFER
    cdef int IDOK

cdef class Printer:
    cdef HANDLE _handle

    def __init__(self, printername):
        if OpenPrinter(PyUnicode_AsUnicode(printername), &self._handle, NULL) == 0:
            pymRaiseWin32Err()
    
    def __dealloc__(self):
        if self._handle:
            if ClosePrinter(self._handle) == 0:
                pymRaiseWin32Err()
            self._handle = NULL

    def getHandle(self):
        return PyMFCHandle_FromHandle(self._handle)
    
def documentProperties(printer, wnd=None, devicename=None, devmode=None, prompt=False):
    cdef HWND hWnd
    cdef HANDLE hPrinter
    cdef LPTSTR pDeviceName
    cdef DEVMODE *pDevModeOutput
    cdef DEVMODE *pDevModeInput
    cdef DWORD fMode
    cdef LONG ret
        
    hPrinter = PyMFCHandle_AsHandle(printer.getHandle())
    
    if wnd is None:
        hWnd = NULL
    elif PyMFCHandle_IsHandle(wnd):
        hWnd = PyMFCHandle_AsHandle(wnd)
    else:
        hWnd = PyMFCHandle_AsHandle(wnd.getHwnd())

    if devicename is None:
        pDeviceName = NULL
    else:
        pDeviceName = PyUnicode_AsUnicode(devicename)
        
    if devmode is None:
        pDevModeInput = NULL
    else:
        pDevModeInput = <DEVMODE*>PyMFCPtr_AsVoidPtr(devmode.getPtr())
    
    fMode = DM_OUT_BUFFER
    if prompt:
        fMode |= DM_IN_PROMPT
    if devmode:
        fMode |= DM_IN_BUFFER

    ret = DocumentProperties(hWnd, hPrinter, pDeviceName, NULL, NULL, 0)
    if ret < 0:
        pymRaiseWin32Err()

    pDevModeOutput = <DEVMODE*>malloc(ret)
    if pDevModeOutput == NULL:
        raise MemoryError()
    try:
        ret = DocumentProperties(hWnd, hPrinter, pDeviceName, pDevModeOutput, pDevModeInput, fMode)
        if ret == IDOK:
            return pymfc.gdi.DevMode(ptr=PyMFCPtr_FromVoidPtr(pDevModeOutput))
        elif prompt:
            return None
        else:
            pymRaiseWin32Err()
    finally:
        free(pDevModeOutput)

