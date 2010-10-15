
cdef extern from "windows.h":
    # messages
    int WM_SETREDRAW


def getCursorPos():
    cdef POINT p
    if not GetCursorPos(&p):
        pymRaiseWin32Err()
        
    return (p.x, p.y)

cdef class __iterChildWindows # forward declaration

cdef class _WindowPlacement:
    cdef WINDOWPLACEMENT _wp
    
    def __init__(self):
        memset(&self._wp, 0, sizeof(self._wp))
        
    cdef void _setwp(self, WINDOWPLACEMENT *wp):
        self._wp = wp[0]


    property hide:
        def __get__(self):
            return self._wp.showCmd == SW_HIDE
    property maximize:
        def __get__(self):
            return self._wp.showCmd == SW_MAXIMIZE
    property minimize:
        def __get__(self):
            return self._wp.showCmd == SW_MINIMIZE
    property restore:
        def __get__(self):
            return self._wp.showCmd == SW_RESTORE
    property show:
        def __get__(self):
            return self._wp.showCmd == SW_SHOW
    property showmaximized:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWMAXIMIZED
    property showminimized:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWMINIMIZED
    property showminnoactive:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWMINNOACTIVE
    property showna:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWNA
    property shownoactivate:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWNOACTIVATE
    property shownormal:
        def __get__(self):
            return self._wp.showCmd == SW_SHOWNORMAL
    property position:
        def __get__(self):
            return (self._wp.rcNormalPosition.left, self._wp.rcNormalPosition.top, 
                self._wp.rcNormalPosition.right, self._wp.rcNormalPosition.bottom)

def msgbox(_WndBase w, msg, caption, 
        abortretryignore=0, ok=0, okcancel=0, retrycancel=0, yesno=0,
        yesnocancel=0, iconexclamation=0, iconwarning=0, iconinformation=0,
        iconasterisk=0, iconquestion=0, iconstop=0, iconerror=0, iconhand=0,
        defbutton1=0, defbutton2=0, defbutton3=0, defbutton4=0,
        applmodal=0, systemmodal=0, taskmodal=0,
        default_desktop_only=0, help=0, right=0, rtlreading=0,
        setforeground=0, topmost=0):

        cdef HWND hwnd
        cdef UINT f
        cdef TCHAR *_caption, *_msg

        if w:
            hwnd = w._getHwnd()
        else:
            hwnd = NULL
            
        _caption = PyUnicode_AsUnicode(caption)
        _msg = PyUnicode_AsUnicode(msg)

        f = 0
        if abortretryignore:
            f = f | MB_ABORTRETRYIGNORE
        if ok:
            f = f | MB_OK
        if okcancel:
            f = f | MB_OKCANCEL
        if retrycancel:
            f = f | MB_RETRYCANCEL
        if yesno:
            f = f | MB_YESNO
        if yesnocancel:
            f = f | MB_YESNOCANCEL
        if iconexclamation:
            f = f | MB_ICONEXCLAMATION
        if iconwarning:
            f = f | MB_ICONWARNING
        if iconinformation:
            f = f | MB_ICONINFORMATION
        if iconasterisk:
            f = f | MB_ICONASTERISK
        if iconquestion:
            f = f | MB_ICONQUESTION
        if iconstop:
            f = f | MB_ICONSTOP
        if iconerror:
            f = f | MB_ICONERROR
        if iconhand:
            f = f | MB_ICONHAND
        if defbutton1:
            f = f | MB_DEFBUTTON1
        if defbutton2:
            f = f | MB_DEFBUTTON2
        if defbutton3:
            f = f | MB_DEFBUTTON3
        if defbutton4:
            f = f | MB_DEFBUTTON4
        if applmodal:
            f = f | MB_APPLMODAL
        if applmodal:
            f = f | MB_APPLMODAL
        if systemmodal:
            f = f | MB_SYSTEMMODAL
        if taskmodal:
            f = f | MB_TASKMODAL
        if default_desktop_only:
            f = f | MB_DEFAULT_DESKTOP_ONLY
        if help:
            f = f | MB_HELP
        if right:
            f = f | MB_RIGHT
        if rtlreading:
            f = f | MB_RTLREADING
        if setforeground:
            f = f | MB_SETFOREGROUND
        if topmost:
            f = f | MB_TOPMOST

        return pymMessageBox(hwnd, _msg, _caption, f)

cdef class _WndBase:
    cdef HWND _getHwnd(self):
        return <HWND>CWnd_Hwnd(self._cwnd)

    cdef void *newInstance(self):
        raise NotImplementedError('newInstance() is not implemented for %s' % self)
        return NULL

    def __init__(self):
        self._keymap = {}
        self._cwnd = self.newInstance()
        self.cwnd = PyMFCPtr_FromVoidPtr(self._cwnd)
        
    def __dealloc__(self):
        if self._cwnd:
            CWnd_Delete(self._cwnd)
            self._cwnd = NULL

    def wndReleased(self):
        ''' invoked just after window is destroyed.'''
        if self._keymap:
            self._keymap = None

    def getHwnd(self):
        return PyMFCHandle_FromHandle(self._getHwnd())

    def _create(self,
            style, className, windowName,
            x=None, y=None, w=None, h=None, 
            parent=None, idOrHMenu=0):

        if x is None: x = CW_USEDEFAULT
        if y is None: y = CW_USEDEFAULT
        if w is None: w = CW_USEDEFAULT
        if h is None: h = CW_USEDEFAULT
        
        cdef HWND hParent
        if parent is None:
            hParent = NULL
        elif PyMFCHandle_IsHandle(parent):
            hParent = PyMFCHandle_AsHandle(parent)
        else:
            hParent =  PyMFCHandle_AsHandle(parent.getHwnd())
    
        cdef void *hmenu
        if PyMFCHandle_IsHandle(idOrHMenu):
            hmenu = PyMFCHandle_AsHandle(idOrHMenu)
        else:
            hmenu = PyLong_AsVoidPtr(idOrHMenu)

        CWnd_Create(self._cwnd, style.exStyle, PyUnicode_AsUnicode(className),
            PyUnicode_AsUnicode(windowName), style.style, x, y, w, h, 
            hParent, hmenu)

    def destroy(self):
        CWnd_Destroy(self._cwnd)

    def destroyWindow(self):
        CWnd_Destroy(self._cwnd)

    def defWndProc(self, msg):
#        message = msg.message
#        wParam = msg.wparam
#        lParam = msg.lparam
#        result = msg.result
#        d = 
#        return CWnd_DefWndProc(self._cwnd, message, wParam, lParam, result)
        return CWnd_DefWndProc(self._cwnd, msg)

    def _subclassWindow(self, hwnd, temp=0):
        return CWnd_SubclassWindow(self._cwnd, PyMFCHandle_AsHandle(hwnd), temp)
    
    def _unsubclassWindow(self):
        return PyMFCHandle_FromHandle(CWnd_UnsubclassWindow(self._cwnd))

    def getClassName(self):
        cdef TCHAR name[MAX_PATH]
        if 0 == GetClassName(self._getHwnd(), name, MAX_PATH):
            pymRaiseWin32Err()
        name[MAX_PATH-1] = 0;
        return _fromWideChar(name)
        
    def postMessage(self, msg, wparam, lparam):
        cdef WPARAM c_wparam
        cdef LPARAM c_lparam
        
        if isinstance(wparam, (tuple, list)) and len(wparam) == 2:
            c_wparam = MAKEWPARAM(wparam[0], wparam[1])
        else:
            c_wparam = wparam

        if PyMFCHandle_IsHandle(lparam):
            c_lparam = <LPARAM>PyMFCHandle_AsHandle(lparam)
        elif isinstance(lparam, (tuple, list)) and len(lparam) == 2:
            c_lparam = MAKELPARAM(lparam[0], lparam[1])
        else:
            c_lparam = lparam

        pymPostMessage(self._getHwnd(), msg, c_wparam, c_lparam)

    def sendMessage(self, msg, wparam, lparam):
        cdef WPARAM c_wparam
        cdef LPARAM c_lparam
        
        if isinstance(wparam, (tuple, list)) and len(wparam) == 2:
            c_wparam = MAKEWPARAM(wparam[0], wparam[1])
        else:
            c_wparam = wparam

        if PyMFCHandle_IsHandle(lparam):
            c_lparam = <LPARAM>PyMFCHandle_AsHandle(lparam)
        elif isinstance(lparam, (tuple, list)) and len(lparam) == 2:
            c_lparam = MAKELPARAM(lparam[0], lparam[1])
        else:
            c_lparam = lparam
        
        return CWnd_SendMessage_L_L_L(self._cwnd, msg, c_wparam, c_lparam)

    def getWindowStyle(self):
        cdef DWORD style, exstyle
        cdef WndStyle ret
        
        style = GetWindowLong(self._getHwnd(), GWL_STYLE)
        exstyle = GetWindowLong(self._getHwnd(), GWL_EXSTYLE)
        
        ret = self.STYLE.dup()
        ret.style = style
        ret.exStyle = exstyle
        
        return ret

    def _getDlgItem(self, childid):
        return PyMFCHandle_FromHandle(CWnd_GetDlgItem(self._cwnd, childid))
    
    def _setMenu(self, hMenu):
        CWnd_SetMenu(self._cwnd, PyMFCHandle_AsHandle(hMenu))
    
    def _drawMenuBar(self):
        CWnd_DrawMenuBar(self._cwnd)

    def getNextDlgTabItem(self, ctl, prev=0):
        cdef HWND ret, hwnd

        if isinstance(ctl, (int, long)):
            hwnd = PyLong_AsVoidPtr(ctl)
        else:
            hwnd = PyMFCHandle_AsHandle(ctl.getHwnd())
        
        return CWnd_GetNextDlgTabItem(self._cwnd, hwnd, prev)
        
    def _enumChildWindows(self):
        return __iterChildWindows(self)
        
    def setTimer(self, eventid, elapse):
        cdef unsigned long ret
        ret = SetTimer(self._getHwnd(), eventid, elapse, NULL)
        if ret == 0:
            pymRaiseWin32Err()
        return ret

    def killTimer(self, eventid):
        cdef unsigned long ret
        ret = KillTimer(self._getHwnd(), eventid)
        if ret == 0:
            pymRaiseWin32Err()
        return ret

    def setText(self, text):
        CWnd_SendMessage_L_P_L(self._cwnd, WM_SETTEXT, 0, PyUnicode_AsUnicode(text))
        
    def getText(self):
        cdef TCHAR *p
        cdef long size

        size = CWnd_SendMessage_L_L_L(self._cwnd, WM_GETTEXTLENGTH, 0, 0)
        if not size:
            return unicode('')

        p = <TCHAR*>malloc((size+1)*sizeof(TCHAR))
        if p == NULL:
            raise MemoryError()
        try:
            size = CWnd_SendMessage_L_P_L(self._cwnd, WM_GETTEXT, size+1, p)
            ret = _fromWideChar(p)
        except:
            # cannot use finally here. (pyrex bug?)
            free(p)
            raise
        return ret
        
    def setActiveWindow(self):
        return CWnd_SetActiveWindow(self._cwnd)
        
    def setForegroundWindow(self):
        CWnd_SetForegroundWindow(self._cwnd)

    def setFocus(self):
        CWnd_SetFocus(self._cwnd)
        
    def setCapture(self):
        CWnd_SetCapture(self._cwnd)
    
    def releaseCapture(self):
        CWnd_ReleaseCapture()

    def getCursorPos(self):
        cdef POINT p
        if not GetCursorPos(&p):
            pymRaiseWin32Err()
            
        return self.screenToClient((p.x, p.y))

    def trackMouseEvent(self, cancel=0, hover=0, leave=0, nonclient=0, hoverTime=-1):
        CWnd_TrackMouseEvent(self._cwnd, cancel, hover, leave, nonclient, hoverTime)

    def getFont(self):
        cdef HFONT hfont
        hfont = CWnd_GetFont(self._cwnd)
        if hfont:
            return pymfc.gdi.Font(hfont=PyMFCHandle_FromHandle(hfont))

    def setFont(self, font, redraw=0):
        return CWnd_SetFont(self._cwnd, PyMFCHandle_AsHandle(font.hFont), redraw)

    def setIcon(self, big=None, small=None):
        cdef HANDLE lparam
        if big:
            lparam = PyMFCHandle_AsHandle(big.getHandle())
            CWnd_SendMessage_L_P_L(self._cwnd, WM_SETICON, 1, lparam)
        if small:
            lparam = PyMFCHandle_AsHandle(small.getHandle())
            CWnd_SendMessage_L_P_L(self._cwnd, WM_SETICON, 0, lparam)
            
    def screenToClient(self, pos):
        cdef POINT point
        ret = []
        for i in range(0, len(pos), 2):
            point.x = pos[i]
            point.y = pos[i+1]
            if ScreenToClient(self._getHwnd(), &point) == 0:
                pymRaiseWin32Err()
            ret.append(point.x)
            ret.append(point.y)
        return ret
            
    def clientToScreen(self, pos):
        cdef POINT point
        ret = []
        for i in range(0, len(pos), 2):
            point.x = pos[i]
            point.y = pos[i+1]
            if ClientToScreen(self._getHwnd(), &point) == 0:
                pymRaiseWin32Err()
            ret.append(point.x)
            ret.append(point.y)
        return ret
            
    def calcWindowRect(self, clientrc):
        cdef RECT rc
        rc.left = clientrc[0]
        rc.top = clientrc[1]
        rc.right = clientrc[2]
        rc.bottom = clientrc[3]
        
        if 0 == CWnd_CalcWindowRect(self._cwnd, &rc):
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.right, rc.bottom)

    def getClientRect(self):
        cdef RECT rc
        if 0 == GetClientRect(self._getHwnd(), &rc):
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.right, rc.bottom)
        
    def getWindowRect(self):
        cdef RECT rc
        if 0 == GetWindowRect(self._getHwnd(), &rc):
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.right, rc.bottom)
        
    def getWindowPlacement(self):
        cdef WINDOWPLACEMENT buf
        cdef _WindowPlacement wp
        cdef BOOL ret
        
        buf.length = sizeof(buf)
        ret = GetWindowPlacement(self._getHwnd(), &buf)
        if ret == 0:
            pymRaiseWin32Err()
        
        wp = _WindowPlacement()
        wp._setwp(&buf)
        
        return wp
#        
#
#		WINDOWPLACEMENT wp;
#		GetWindowPlacement(&wp);
#		
#		AfxGetApp()->WriteProfileInt("FramePos","Maximized", wp.showCmd == SW_SHOWMAXIMIZED);
#		AfxGetApp()->WriteProfileInt("FramePos","x",wp.rcNormalPosition.left);
#		AfxGetApp()->WriteProfileInt("FramePos","y", wp.rcNormalPosition.top);
#		AfxGetApp()->WriteProfileInt("FramePos","Height",
#			wp.rcNormalPosition.bottom - wp.rcNormalPosition.top);
#		AfxGetApp()->WriteProfileInt("FramePos", "Width", 
#			wp.rcNormalPosition.right - wp.rcNormalPosition.left);
			
			
			
    def showWindow(self, hide=0, minimize=0, maximize=0, restore=0, show=0, showdefault=0, showmaximized=0, showminimized=0, showminnoactive=0, showna=0, shownoactivate=0, shownormal=0):
        cdef int flag
        if hide:
            flag = SW_HIDE
        elif minimize:
            flag = SW_MINIMIZE
        elif maximize:
            flag = SW_MAXIMIZE
        elif restore:
            flag = SW_RESTORE
        elif show:
            flag = SW_SHOW
        elif showdefault:
            flag = SW_SHOWDEFAULT
        elif showmaximized:
            flag = SW_SHOWMAXIMIZED
        elif showminimized:
            flag = SW_SHOWMINIMIZED
        elif showminnoactive:
            flag = SW_SHOWMINNOACTIVE
        elif showna:
            flag = SW_SHOWNA
        elif shownoactivate:
            flag = SW_SHOWNOACTIVATE
        elif shownormal:
            flag = SW_SHOWNORMAL

        CWnd_ShowWindow(self._cwnd, flag)
        
    def setWindowPos(self, 
            placebottom=0, placenotopmost=0, placetop=0, placetopmost=0,
            after=None, pos=None, size=None,
            rect=None, show=None, framechanged=0, activate=1, redraw=1):
        
        cdef unsigned long flag
        cdef long cx, cy
        cdef HWND hwndafter
        cdef long x, y

        flag = 0

        hwndafter = NULL
        if placebottom:
            hwndafter = HWND_BOTTOM
        elif placenotopmost:
            hwndafter = HWND_NOTOPMOST
        elif placetop:
            hwndafter = HWND_TOP
        elif placetopmost:
            hwndafter = HWND_TOPMOST
        elif after:
            hwndafter = PyMFCHandle_AsHandle(after.getHwnd())
        
        if not (placebottom or placenotopmost or placetop or placetopmost or after):
            flag = flag | SWP_NOZORDER

        x = y = 0
        cx = cy = 0

        if rect is not None:
            x = rect[0]
            y = rect[1]
            cx = rect[2] - rect[0]
            cy = rect[3] - rect[1]
        else:
            if pos is not None:
                x = pos[0]
                y = pos[1]
            else:
                flag = flag | SWP_NOMOVE
            
            if size is not None:
                cx = size[0]
                cy = size[1]
            else:
                flag = flag | SWP_NOSIZE
        
        if show is not None:
            if show:
                flag = flag | SWP_SHOWWINDOW
            else:
                flag = flag | SWP_HIDEWINDOW


        if framechanged:
            flag = flag | SWP_FRAMECHANGED

        if not activate:
            flag = flag | SWP_NOACTIVATE

        if not redraw:
            flag = flag | SWP_NOREDRAW

        CWnd_SetWindowPos(self._cwnd, hwndafter, 
            x, y, cx, cy, flag)

    def setLayeredWindowAttributes(self, color=None, alpha=None):
        cdef int _alpha, _color
        _color = _alpha = 0
        if color is not None:
            flag = LWA_COLORKEY
            _color = color
        elif alpha is not None:
            flag = LWA_ALPHA
            _alpha = alpha
        else:
            raise ValueError()

        CWnd_SetLayeredWindowAttributes(self._cwnd, _color, <BYTE>_alpha, flag)
        
    def setWindowRgn(self, rgn, redraw=1):
        CWnd_SetWindowRgn(self._cwnd, PyMFCHandle_AsHandle(rgn.getHandle()), redraw)
        

    def beginDeferWindowPos(self, n):
        return PyMFCHandle_FromHandle(CWnd_BeginDeferWindowPos(n))
        
    def endDeferWindowPos(self, defer):
        return CWnd_EndDeferWindowPos(PyMFCHandle_AsHandle(defer))
        
    def deferWindowPos(self, defer,
            bottom=0, notopmost=0, top=0, topmost=0,
            after=None, pos=None, size=None,
            rect=None, show=None):
        
        cdef unsigned long flag
        cdef long cx, cy
        cdef HWND hwndafter
        cdef long x, y

        flag = 0

        hwndafter = NULL
        if bottom:
            hwndafter = HWND_BOTTOM
        elif notopmost:
            hwndafter = HWND_NOTOPMOST
        elif top:
            hwndafter = HWND_TOP
        elif topmost:
            hwndafter = HWND_TOPMOST
        elif after:
            hwndafter = PyMFCHandle_AsHandle(after.getHwnd())
        
        if not (bottom or notopmost or top or topmost or after):
            flag = flag | SWP_NOZORDER

        x = y = 0
        cx = cy = 0

        if rect is not None:
            x = rect[0]
            y = rect[1]
            cx = rect[2] - rect[0]
            cy = rect[3] - rect[1]
        else:
            if pos is not None:
                x = pos[0]
                y = pos[1]
            else:
                flag = flag | SWP_NOMOVE
            
            if size is not None:
                cx = size[0]
                cy = size[1]
            else:
                flag = flag | SWP_NOSIZE
        
        if show is not None:
            if show:
                flag = flag | SWP_SHOWWINDOW
            else:
                flag = flag | SWP_HIDEWINDOW

        return PyMFCHandle_FromHandle(CWnd_DeferWindowPos(PyMFCHandle_AsHandle(defer), self._cwnd, hwndafter, 
            x, y, cx, cy, flag))



    def enableWindow(self, enable):
        CWnd_EnableWindow(self._cwnd, enable)
    
    def isWindowEnabled(self):
        return IsWindowEnabled(self._getHwnd())
        
    def createCaret(self, width=0, height=0):
        if 0 == CreateCaret(self._getHwnd(), NULL, width, height):
            pymRaiseWin32Err()
        
    def setCaretPos(self, pos):
        cdef int x, y
        x, y = pos
        if 0 == SetCaretPos(x, y):
            pymRaiseWin32Err()

    def getCaretPos(self):
        cdef POINT pos
        if 0 == GetCaretPos(&pos):
            pymRaiseWin32Err()
        return pos.x, pos.y
        
    def showCaret(self):
        if 0 == ShowCaret(self._getHwnd()):
            pymRaiseWin32Err()

    def hideCaret(self):
        if 0 == HideCaret(self._getHwnd()):
            pymRaiseWin32Err()

    def destroyCaret(self):
        if 0 == DestroyCaret():
            pymRaiseWin32Err()

    def getUpdateRect(self, erase=False):
        cdef RECT rc
        cdef BOOL ret
        cdef BOOL bErase
        cdef HWND hwnd

        hwnd = self._getHwnd()
        bErase = erase
        
        with nogil:
            ret = GetUpdateRect(hwnd, &rc, bErase)
        
        if 0 == ret:
            return None
        return (rc.left, rc.top, rc.right, rc.bottom)


    def setRedraw(self, int redraw):
        CWnd_SendMessage_L_L_L(self._cwnd, WM_SETREDRAW, redraw, 0)
        
    def scrollWindow(self, dx, dy, scroll=None, clip=None, 
            erase=0, invalidate=0, scrollchildren=0, smooth=0):
        
        cdef RECT rscroll, rclip, *p_scroll, *p_clip
        
        p_scroll = NULL
        p_clip = NULL
        
        if scroll:
            rscroll.left = scroll[0]
            rscroll.top = scroll[1]
            rscroll.right = scroll[2]
            rscroll.bottom = scroll[3]
            p_scroll = &rscroll
            
        if clip:
            rclip.left = clip[0]
            rclip.top = clip[1]
            rclip.right = clip[2]
            rclip.bottom = clip[3]
            p_clip = &rclip
            
        CWnd_ScrollWindowEx(self._cwnd, dx, dy,
          p_scroll, p_clip, NULL, NULL,  
          erase, invalidate, scrollchildren, smooth)
        

    def showScrollBar(self, horz=0, vert=0, show=0):
        CWnd_ShowScrollBar(self._cwnd, horz, vert, show)
        
    def setScrollInfo(self, horz=0, vert=0, min=None, max=None, page=None, pos=None, disablenoscroll=0, redraw=1):
        CWnd_SetScrollInfo(self._cwnd, horz, vert, min, max, page, pos, disablenoscroll, redraw)
    
    def getScrollInfo(self, horz=0, vert=0):
        info = CWnd_GetScrollInfo(self._cwnd, horz, vert)
        ret = __CONSTDEF()
        ret.min = info[0]
        ret.max = info[1]
        ret.page = info[2]
        ret.pos = info[3]
        ret.trackpos = info[4]
        return ret
        
    def invalidateRect(self, rc, erase=True):
        cdef RECT rect, *p_rect
        
        p_rect = NULL
        if rc:
            rect.left = rc[0]
            rect.top = rc[1]
            rect.right = rc[2]
            rect.bottom = rc[3]
            p_rect = &rect
        InvalidateRect(self._getHwnd(), p_rect, erase)
        
    def updateWindow(self):
        CWnd_UpdateWindow(self._cwnd)
        
    def openClipboard(self):
        return pymOpenClipboard(self._getHwnd())

    def isClipboardFormatAvailable(self, format):
        if hasattr(format, "format"):
            format = format.format
        return pymIsClipboardFormatAvailable(format)

    def setClipboardData(self, format, data):
        cdef char *s, *buf
        cdef long size
        cdef HANDLE hmem

        if hasattr(format, "format"):
            format = format.format
        
        s = data
        size = len(data)
        hmem = GlobalAlloc(GMEM_MOVEABLE | GMEM_DDESHARE, size)
        if hmem == NULL:
            pymRaiseWin32Err()
        try:
            buf = <char *>GlobalLock(hmem)
            if not buf:
                pymRaiseWin32Err()

            memcpy(buf, s, size)
            GlobalUnlock(hmem)
            
            pymSetClipboardData(format, hmem)
        except:
            GlobalFree(hmem)
            raise

    def setClipboardText(self, text):
        cdef PYMFC_WCHAR *buf
        cdef long size
        cdef HANDLE hmem

        
        size = len(text)
        hmem = GlobalAlloc(GMEM_MOVEABLE | GMEM_DDESHARE, (size+1)*sizeof(PYMFC_WCHAR))
        if hmem == NULL:
            pymRaiseWin32Err()
        try:
            buf = <PYMFC_WCHAR *>GlobalLock(hmem)
            if not buf:
                pymRaiseWin32Err()

            memcpy(buf, PyUnicode_AsUnicode(text), size*sizeof(PYMFC_WCHAR))
            buf[size] = 0
            
            GlobalUnlock(hmem)
            
            pymSetClipboardData(CF_UNICODETEXT, hmem)
        except:
            GlobalFree(hmem)
            raise

    def getClipboardData(self, format):
        cdef HANDLE hmem
        cdef char *buf

        if hasattr(format, "format"):
            format = format.format
        
        hmem = pymGetClipboardData(format)
        if hmem == NULL:
            return None
        size = GlobalSize(hmem)

        buf = <char *>GlobalLock(hmem)
        if not buf:
            pymRaiseWin32Err()
            
        try:
            ret = PyString_FromStringAndSize(buf, size)
        finally:
            GlobalUnlock(hmem)
        return ret

    def getClipboardText(self):
        cdef HANDLE hmem
        cdef PYMFC_WCHAR *buf

        hmem = pymGetClipboardData(CF_UNICODETEXT)
        if hmem == NULL:
            return None

        buf = <PYMFC_WCHAR *>GlobalLock(hmem)
        if not buf:
            pymRaiseWin32Err()
            
        try:
            ret = PyUnicode_FromWideChar(buf, wcslen(buf))
        finally:
            GlobalUnlock(hmem)
        return ret

    def emptyClipboard(self):
        pymEmptyClipboard()

    def closeClipboard(self):
        pymCloseClipboard()
        
    def getDlgCtrlID(self):
        return GetDlgCtrlID(self._getHwnd())

    def msgbox(self, msg, caption, 
        abortretryignore=0, ok=0, okcancel=0, retrycancel=0, yesno=0,
        yesnocancel=0, iconexclamation=0, iconwarning=0, iconinformation=0,
        iconasterisk=0, iconquestion=0, iconstop=0, iconerror=0, iconhand=0,
        defbutton1=0, defbutton2=0, defbutton3=0, defbutton4=0,
        applmodal=0, systemmodal=0, taskmodal=0,
        default_desktop_only=0, help=0, right=0, rtlreading=0,
        setforeground=0, topmost=0):

        return msgbox(self, msg, caption, 
            abortretryignore, ok, okcancel, retrycancel, yesno,
            yesnocancel, iconexclamation, iconwarning, iconinformation,
            iconasterisk, iconquestion, iconstop, iconerror, iconhand,
            defbutton1, defbutton2, defbutton3, defbutton4,
            applmodal, systemmodal, taskmodal,
            default_desktop_only, help, right, rtlreading,
            setforeground, topmost)
        
#        cdef HWND hwnd
#        cdef UINT f
#        cdef TCHAR *_caption, *_msg
#
#        hwnd = self._getHwnd()
#        _caption = PyUnicode_AsUnicode(caption)
#        _msg = PyUnicode_AsUnicode(msg)
#
#        f = 0
#        if abortretryignore:
#            f = f | MB_ABORTRETRYIGNORE
#        if ok:
#            f = f | MB_OK
#        if okcancel:
#            f = f | MB_OKCANCEL
#        if retrycancel:
#            f = f | MB_RETRYCANCEL
#        if yesno:
#            f = f | MB_YESNO
#        if yesnocancel:
#            f = f | MB_YESNOCANCEL
#        if iconexclamation:
#            f = f | MB_ICONEXCLAMATION
#        if iconwarning:
#            f = f | MB_ICONWARNING
#        if iconinformation:
#            f = f | MB_ICONINFORMATION
#        if iconasterisk:
#            f = f | MB_ICONASTERISK
#        if iconquestion:
#            f = f | MB_ICONQUESTION
#        if iconstop:
#            f = f | MB_ICONSTOP
#        if iconerror:
#            f = f | MB_ICONERROR
#        if iconhand:
#            f = f | MB_ICONHAND
#        if defbutton1:
#            f = f | MB_DEFBUTTON1
#        if defbutton2:
#            f = f | MB_DEFBUTTON2
#        if defbutton3:
#            f = f | MB_DEFBUTTON3
#        if defbutton4:
#            f = f | MB_DEFBUTTON4
#        if applmodal:
#            f = f | MB_APPLMODAL
#        if applmodal:
#            f = f | MB_APPLMODAL
#        if systemmodal:
#            f = f | MB_SYSTEMMODAL
#        if taskmodal:
#            f = f | MB_TASKMODAL
#        if default_desktop_only:
#            f = f | MB_DEFAULT_DESKTOP_ONLY
#        if help:
#            f = f | MB_HELP
#        if right:
#            f = f | MB_RIGHT
#        if rtlreading:
#            f = f | MB_RTLREADING
#        if setforeground:
#            f = f | MB_SETFOREGROUND
#        if topmost:
#            f = f | MB_TOPMOST
#
#        return pymMessageBox(hwnd, _msg, _caption, f)

    def registerHotKey(self, id, alt, ctrl, shift, win, key):
        cdef UINT mod
        mod = 0
        if alt: mod = mod | MOD_ALT
        if ctrl: mod = mod | MOD_CONTROL
        if shift: mod = mod | MOD_SHIFT
        if win: mod = mod | MOD_WIN

        if 0 == RegisterHotKey (self._getHwnd(), id, mod, key):
            pymRaiseWin32Err()

    def unRegisterHotKey(self, id):
        if 0 == UnregisterHotKey (self._getHwnd(), id):
            pymRaiseWin32Err()

_GETDLGCODERESULT = {
}


    

        

cdef BOOL __stdcall _iterchildproc(HWND hwnd, LPARAM lparam) with gil:
    cdef __iterChildWindows obj
    obj = <object>lparam
    
    wnd = PyMFCHandle_FromHandle(hwnd)
    obj._hwnds.append(wnd)

    return 1
    
cdef class __iterChildWindows:
    cdef object _hwnds
    
    def __init__(self, _WndBase wnd):
        cdef LPARAM lparam
        cdef HWND hwnd
        lparam = <LPARAM>self

        self._hwnds = []
        hwnd = wnd._getHwnd()
        with nogil:
            EnumChildWindows(hwnd, _iterchildproc, lparam)
        
    def __next__(self):
        if not self._hwnds:
            raise StopIteration
        return self._hwnds.pop(0)
    
    def __iter__(self):
        return self

def _fromHandle(hwnd):
    return CWnd_FromHandle(PyMFCHandle_AsHandle(hwnd))
    
def _getFocus():
    return CWnd_GetFocus()

def _getActiveWindow():
    return CWnd_GetActiveWindow()

def _getForegroundWindow():
    return CWnd_GetForegroundWindow()

def getKeyState(int key):
    cdef short state
    state = GetKeyState(key)
    ret = __CONSTDEF()
    ret.down = (state < 0)
    ret.toggled = (state & 1)
    return ret


def registerWindowMessage(s):
    ret = RegisterWindowMessage(PyUnicode_AsUnicode(s))
    if not ret:
        pymRaiseWin32Err()
    return ret


cdef void __init_getdigcoderesult():

    cdef object _const
    _const = __CONSTDEF()
    
    _const.button 	= DLGC_BUTTON
    _const.defpushbutton = DLGC_DEFPUSHBUTTON
    _const.hassetsel 	= DLGC_HASSETSEL
    _const.radiobutton 	= DLGC_RADIOBUTTON
    _const.static 	= DLGC_STATIC
    _const.undefpushbutton = DLGC_UNDEFPUSHBUTTON
    _const.wantallkeys	= DLGC_WANTALLKEYS
    _const.wantarrows	= DLGC_WANTARROWS
    _const.wantchars 	= DLGC_WANTCHARS
    _const.wantmessage	= DLGC_WANTMESSAGE
    _const.wanttab 	= DLGC_WANTTAB

    global GETDLGCODERESULT
    GETDLGCODERESULT = _const
    
__init_getdigcoderesult()