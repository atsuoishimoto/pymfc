cdef extern from "windows.h":
    # constants
    int CW_USEDEFAULT
    
    # messages
    int WM_SETTEXT, WM_GETTEXT, WM_GETTEXTLENGTH
    int WM_COMMAND, WM_NOTIFY, WM_SETICON

    # types
    ctypedef int BOOL
    ctypedef unsigned int UINT
    ctypedef unsigned int UINT_PTR
    ctypedef unsigned int *PUINT
    ctypedef unsigned long DWORD # (xxxx: changed to unsigned again    ---- old comment:cannot use "unsinged long" here. pyrex now converts "unsinged long" to python long
    ctypedef DWORD *LPDWORD
    ctypedef int *LPINT
    ctypedef long LONG
    ctypedef unsigned long ULONG
    ctypedef unsigned char BYTE
    ctypedef BYTE *LPBYTE
    ctypedef unsigned short TCHAR
    ctypedef unsigned short WCHAR
    ctypedef short SHORT
    ctypedef unsigned short WORD
    ctypedef char *LPSTR
    ctypedef char *LPCSTR
    ctypedef TCHAR *LPTSTR
    ctypedef TCHAR *LPCTSTR
    ctypedef WCHAR *LPCWSTR
    ctypedef WCHAR *LPWSTR
    ctypedef void *LPCVOID
    ctypedef void *LPVOID
    ctypedef void *HGLOBAL
    ctypedef void *HINSTANCE
    ctypedef void* HANDLE
    ctypedef void* HWND
    ctypedef void *HMENU
    ctypedef void* HDC
    ctypedef void* HGDIOBJ
    ctypedef void* HRGN
    ctypedef void *HBRUSH
    ctypedef void *HICON
    ctypedef void *HCURSOR
    ctypedef void *HBITMAP
    ctypedef void *HPALETTE
    ctypedef void *HFONT
    ctypedef void *HPEN
    ctypedef void *HKEY
    ctypedef void *HMONITOR
    ctypedef void *HENHMETAFILE
    
    ctypedef long COLORREF

    ctypedef long HRESULT
    ctypedef long LONG_PTR
    ctypedef LONG_PTR LRESULT
    
    ctypedef unsigned long _WPAD
    ctypedef unsigned long LCID  # cannot use "unsinged long" here. pyrex now converts "unsinged long" to python long
    ctypedef unsigned long LPARAM  # cannot use "unsinged long" here. pyrex now converts "unsinged long" to python long
    ctypedef unsigned int  WPARAM

    ctypedef WORD LANGID
    
    int FAILED(HRESULT hr)
    DWORD MAKELONG(WORD low, WORD high)
    LPARAM MAKELPARAM(WORD low, WORD high)
    WPARAM MAKEWPARAM(WORD low, WORD hi)
    
    WORD LOWORD(DWORD w)
    WORD HIWORD(DWORD w)

    BYTE LOBYTE(WORD w)
    BYTE HIBYTE(WORD w)
    
    WORD MAKEWORD(BYTE low, BYTE hi)
    LPTSTR MAKEINTRESOURCE(WORD wInteger)

    enum:
        MAX_COMPUTERNAME_LENGTH


    cdef int GDI_ERROR, HGDI_ERROR

    ctypedef struct RECT:
        long left, top, right, bottom
    
    ctypedef struct POINT:
        long x, y
    
    ctypedef struct POINTL:
      LONG  x
      LONG  y

    ctypedef struct SIZE:
        long cx, cy
    ctypedef SIZE *LPSIZE
    
    ctypedef struct RECTL:
        LONG left
        LONG top
        LONG right
        LONG bottom

    ctypedef struct SIZEL:
        LONG cx
        LONG cy

    int ANSI_CHARSET, BALTIC_CHARSET, CHINESEBIG5_CHARSET, DEFAULT_CHARSET
    int EASTEUROPE_CHARSET, GB2312_CHARSET, GREEK_CHARSET, HANGUL_CHARSET
    int MAC_CHARSET, OEM_CHARSET, RUSSIAN_CHARSET, SHIFTJIS_CHARSET
    int SYMBOL_CHARSET, TURKISH_CHARSET, JOHAB_CHARSET, HEBREW_CHARSET
    int ARABIC_CHARSET, THAI_CHARSET

    int OUT_CHARACTER_PRECIS, OUT_DEFAULT_PRECIS, OUT_DEVICE_PRECIS
    int OUT_OUTLINE_PRECIS, OUT_RASTER_PRECIS, OUT_STRING_PRECIS, OUT_STROKE_PRECIS
    int OUT_TT_ONLY_PRECIS, OUT_TT_PRECIS 

    int CLIP_DEFAULT_PRECIS, CLIP_CHARACTER_PRECIS, CLIP_STROKE_PRECIS
    int CLIP_MASK, CLIP_LH_ANGLES, CLIP_TT_ALWAYS, CLIP_EMBEDDED

    int DEFAULT_QUALITY, DRAFT_QUALITY, PROOF_QUALITY

    int DEFAULT_PITCH, FIXED_PITCH, VARIABLE_PITCH

    int FF_DECORATIVE, FF_DONTCARE, FF_MODERN, FF_ROMAN, FF_SCRIPT, FF_SWISS

    enum:
        LF_FACESIZE

    ctypedef struct LOGFONT:
       LONG lfHeight
       LONG lfWidth
       LONG lfEscapement
       LONG lfOrientation
       LONG lfWeight
       BYTE lfItalic
       BYTE lfUnderline
       BYTE lfStrikeOut
       BYTE lfCharSet
       BYTE lfOutPrecision
       BYTE lfClipPrecision
       BYTE lfQuality
       BYTE lfPitchAndFamily
       PYMFC_WCHAR lfFaceName[LF_FACESIZE]


    ctypedef struct TEXTMETRIC:
          LONG tmHeight
          LONG tmAscent
          LONG tmDescent
          LONG tmInternalLeading
          LONG tmExternalLeading
          LONG tmAveCharWidth
          LONG tmMaxCharWidth
          LONG tmWeight
          LONG tmOverhang
          LONG tmDigitizedAspectX
          LONG tmDigitizedAspectY
          TCHAR tmFirstChar
          TCHAR tmLastChar
          TCHAR tmDefaultChar
          TCHAR tmBreakChar
          BYTE tmItalic
          BYTE tmUnderlined
          BYTE tmStruckOut
          BYTE tmPitchAndFamily
          BYTE tmCharSet

    ctypedef struct SYSTEMTIME:
        WORD wYear
        WORD wMonth
        WORD wDayOfWeek
        WORD wDay
        WORD wHour
        WORD wMinute
        WORD wSecond
        WORD wMilliseconds


    int CP_ACP, CP_OEMCP, CP_MACCP, CP_THREAD_ACP, CP_SYMBOL, CP_UTF7, CP_UTF8

    ctypedef struct CLSID:
        unsigned long  Data1
        unsigned short Data2
        unsigned short Data3
        unsigned char  Data4[8]

    enum:
        CCHFORMNAME, CCHDEVICENAME

    ctypedef struct DEVMODE:
        PYMFC_WCHAR  dmDeviceName[CCHDEVICENAME]
        WORD dmSpecVersion
        WORD dmDriverVersion
        WORD dmSize
        WORD dmDriverExtra
        DWORD dmFields
        short dmOrientation
        short dmPaperSize
        short dmPaperLength
        short dmPaperWidth
        short dmScale
        short dmCopies
        short dmDefaultSource
        short dmPrintQuality
        POINTL dmPosition
        DWORD  dmDisplayOrientation
        DWORD  dmDisplayFixedOutput
        short dmColor
        short dmDuplex
        short dmYResolution
        short dmTTOption
        short dmCollate
        WCHAR  dmFormName[CCHFORMNAME]
        WORD   dmLogPixels
        DWORD  dmBitsPerPel
        DWORD  dmPelsWidth
        DWORD  dmPelsHeight
        DWORD  dmDisplayFlags
        DWORD  dmNup
        DWORD  dmDisplayFrequency
        DWORD  dmICMMethod
        DWORD  dmICMIntent
        DWORD  dmMediaType
        DWORD  dmDitherType
        DWORD  dmReserved1
        DWORD  dmReserved2
        DWORD  dmPanningWidth
        DWORD  dmPanningHeight

    ctypedef struct DEVNAMES:
        WORD wDriverOffset
        WORD wDeviceOffset
        WORD wOutputOffset
        WORD wDefault

cdef extern from "COMMCTRL.H":
    pass


cdef extern from "pymwin32funcs.h":
    object PyMFCPtr_FromVoidPtr(HANDLE h)
    HANDLE PyMFCPtr_AsVoidPtr(object) except? NULL
    int PyMFCPtr_IsPtr(object) except -1

    object PyMFCHandle_FromHandle(HANDLE h)
    HANDLE PyMFCHandle_AsHandle(object) except? NULL
    int PyMFCHandle_IsHandle(object) except -1

    void pymRaiseWin32Err() except *
    void pymRaiseWin32Errcode(HRESULT hr) except *
    object pymFormatMessage(unsigned long err)
    unsigned long pymGetLastError()
    
cdef extern from "windows.h":
    UINT RegisterWindowMessage(TCHAR *name)
    SHORT GetKeyState(int nVirtKey)
    
    int GHND, GPTR, GMEM_FIXED, GMEM_MOVEABLE, GMEM_DDESHARE, GMEM_SHARE
    int GMEM_DISCARDABLE, GMEM_LOWER, GMEM_NOCOMPACT, GMEM_NODISCARD
    int GMEM_NOT_BANKED, GMEM_NOTIFY, GMEM_ZEROINIT
    
    HANDLE GlobalAlloc(UINT uFlags, DWORD dwBytes)
    HANDLE GlobalFree(HANDLE hMem)
    void *GlobalLock(HANDLE hBuf)
    BOOL GlobalUnlock(HANDLE hBuf)
    unsigned long GlobalSize(HANDLE hBuf)
    
    UINT SetTimer(HWND hWnd, UINT nIDEvent, UINT uElapse, void *lpTimerFunc)
    UINT KillTimer(HWND hWnd, UINT nIDEvent)

    BOOL InvalidateRect(HWND hWnd, RECT *lpRect, BOOL bErase) except 0

    int GWL_EXSTYLE, GWL_STYLE, GWL_WNDPROC, GWL_HINSTANCE, GWL_HWNDPARENT
    int GWL_ID, GWL_USERDATA, DWL_DLGPROC, DWL_MSGRESULT, DWL_USER

    DWORD GetClassLong(HWND hWnd, int nIndex)
    DWORD SetClassLong(HWND hWnd, int nIndex, unsigned long newLong)
    DWORD GetWindowLong(HWND hWnd, int nIndex)
    DWORD SetWindowLong(HWND hWnd, int nIndex, unsigned long newLong)
    int GetClassName(HWND hWnd, TCHAR *lpClassName, int nMaxCount)

    BOOL ScreenToClient(HWND hWnd, POINT *lpPoint)
    BOOL ClientToScreen(HWND hWnd, POINT *lpPoint)
    int GetClientRect(HWND hwnd, RECT *rect)
    int GetWindowRect(HWND hwnd, RECT *rect)

    int IsWindowEnabled(HWND hWnd)

    int CreateCaret(HWND hWnd, void *hBitmap, int nWidth, int nHeight)
    int DestroyCaret()
    int ShowCaret(HWND hWnd)
    int HideCaret(HWND hWnd)
    int SetCaretPos(int X, int Y)
    int GetCaretPos(POINT *lpPoint)
    BOOL GetCursorPos(POINT *p)
    
    int GetDlgCtrlID(HWND hWnd)


    cdef int ICC_ANIMATE_CLASS, ICC_BAR_CLASSES, ICC_COOL_CLASSES, ICC_DATE_CLASSES
    cdef int ICC_HOTKEY_CLASS, ICC_INTERNET_CLASSES, ICC_LINK_CLASS
    cdef int ICC_LISTVIEW_CLASSES, ICC_NATIVEFNTCTL_CLASS, ICC_PAGESCROLLER_CLASS
    cdef int ICC_PROGRESS_CLASS, ICC_STANDARD_CLASSES, ICC_TAB_CLASSES
    cdef int ICC_TREEVIEW_CLASSES, ICC_UPDOWN_CLASS, ICC_USEREX_CLASSES
    cdef int ICC_WIN95_CLASSES
    
    ctypedef struct INITCOMMONCONTROLSEX:
        DWORD dwSize
        DWORD dwICC

    BOOL InitCommonControlsEx(INITCOMMONCONTROLSEX *)
    

    cdef int SB_LINEDOWN, SB_LINEUP, SB_PAGEDOWN, SB_PAGEUP

    BOOL RegisterHotKey(HWND hWnd, int id, UINT fsModifiers, UINT vk)
    BOOL UnregisterHotKey( HWND hWnd,int id)
    cdef int MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN

cdef extern from "pymwnd.h":
    # clipboard
    cdef int CF_TEXT, CF_BITMAP, CF_METAFILEPICT, CF_SYLK, CF_DIF
    cdef int CF_TIFF, CF_OEMTEXT, CF_DIB, CF_PALETTE, CF_PENDATA
    cdef int CF_RIFF, CF_WAVE, CF_UNICODETEXT, CF_ENHMETAFILE
    cdef int CF_HDROP, CF_LOCALE

    cdef TCHAR *CFSTR_SHELLIDLIST, *CFSTR_SHELLIDLISTOFFSET
    cdef TCHAR *CFSTR_NETRESOURCES, *CFSTR_FILEDESCRIPTORA
    cdef TCHAR *CFSTR_FILEDESCRIPTORW, *CFSTR_FILECONTENTS
    cdef TCHAR *CFSTR_FILENAMEA, *CFSTR_FILENAMEW
    cdef TCHAR *CFSTR_PRINTERGROUP, *CFSTR_FILENAMEMAPA
    cdef TCHAR *CFSTR_FILENAMEMAPW, *CFSTR_SHELLURL
    cdef TCHAR *CFSTR_INETURLA, *CFSTR_INETURLW
    cdef TCHAR *CFSTR_PREFERREDDROPEFFECT
    cdef TCHAR *CFSTR_PERFORMEDDROPEFFECT, *CFSTR_PASTESUCCEEDED
    cdef TCHAR *CFSTR_INDRAGLOOP, *CFSTR_DRAGCONTEXT
    cdef TCHAR *CFSTR_MOUNTEDVOLUME, *CFSTR_PERSISTEDDATAOBJECT
    cdef TCHAR *CFSTR_TARGETCLSID
    cdef TCHAR *CFSTR_LOGICALPERFORMEDDROPEFFECT
    cdef TCHAR *CFSTR_AUTOPLAY_SHELLIDLIST
    cdef TCHAR *CFSTR_AUTOPLAY_SHELLIDLISTS



    BOOL pymOpenClipboard(HWND hWndNewOwner) except 0
    HANDLE pymGetClipboardData(UINT uFormat)
    BOOL pymIsClipboardFormatAvailable(UINT format)
    BOOL pymCloseClipboard() except 0
    HANDLE pymSetClipboardData(UINT uFormat, HANDLE hMem) except NULL
    BOOL pymEmptyClipboard()

    # Window functions
    int pymMessageBox(HWND hWnd, TCHAR *lpText, TCHAR *lpCaption, UINT uType)
    HWND GetDesktopWindow()
    void *new_CWnd(object obj) except NULL
    int CWnd_Delete(void *o)
    object CWnd_FromHandle(HWND hWnd)
    
    HWND CWnd_Hwnd(void *o) except *
    int CWnd_Create(void *o, unsigned long dwExStyle, TCHAR *lpszClassName, 
        TCHAR *lpszWindowName, unsigned long dwStyle, int x, int y, int nWidth, 
        int nHeight, void *hwndParent, HMENU nIDorHMenu) except 0
    int CFrame_CreateWnd(void *o, unsigned long dwExStyle, TCHAR *lpszClassName, 
        TCHAR *lpszWindowName, unsigned long dwStyle, int x, int y, int nWidth, 
        int nHeight, void *hwndParent, HMENU nIDorHMenu) except 0
    int CWnd_Destroy(void *o) except 0
#    unsigned long CWnd_DefWndProc(void *o, int message, WPARAM wParam, LPARAM lParam, unsigned long ret)
    unsigned long CWnd_DefWndProc(void *o, object msg)

    int CWnd_SubclassWindow(void *o, HWND hwnd, int temp) except 0
    HWND CWnd_UnsubclassWindow(void *o) except NULL
    
    HWND CWnd_GetDlgItem(void *o, unsigned long childid) except NULL
    object CWnd_GetNextDlgTabItem(void *o, HWND hwnd, int prev)

    ctypedef int (*grail)(int, char *) except -1
    int holly(grail g)
    
#    TODO: Cython bug? WNDENUMPROC should return BOOL, but cython 0.13 reports error!
#    ctypedef BOOL (*WNDENUMPROC)(HWND, LPARAM) nogil
    ctypedef int (__stdcall *WNDENUMPROC)(HWND, LPARAM) nogil

    BOOL EnumChildWindows(HWND hWndParent, WNDENUMPROC lpEnumFunc, LPARAM lParam) nogil

    int CWnd_SetMenu(void *o, HMENU hMenu) except 0
    int CWnd_DrawMenuBar(void *o) except 0


    int CWnd_SetActiveWindow(void *o)
    object CWnd_GetActiveWindow()
    BOOL CWnd_SetForegroundWindow(void *o) except 0
    object CWnd_GetForegroundWindow()


    object CWnd_GetFocus()
    int CWnd_SetFocus(void *o) except 0
    
    BOOL CWnd_SetCapture(void *o)
    BOOL CWnd_ReleaseCapture()

    HFONT CWnd_GetFont(void *o)
    int CWnd_SetFont(void *o, HFONT hfont, int redraw) except 0

    unsigned long CWnd_SendMessage_L_L_L(void *o, int msg, WPARAM wparam, LPARAM lparam)
    unsigned long CWnd_SendMessage_L_L_L_0(void *o, int msg, long wparam, long lparam) except 0
    unsigned long CWnd_SendMessage_L_L_L_m1(void *o, int msg, long wparam, long lparam) except -1
    unsigned long CWnd_SendMessage_L_P_L(void *o, int msg, long wparam, void* lparam)
    unsigned long CWnd_SendMessage_L_P_L_0(void *o, int msg, long wparam, void* lparam) except 0
    unsigned long CWnd_SendMessage_L_P_L_m1(void *o, int msg, long wparam, void* lparam) except -1
    unsigned long CWnd_SendMessage_P_P_L(void *o, int msg, void* wparam, void* lparam)

    BOOL pymPostMessage(HWND hWnd, UINT Msg, WPARAM wParam, LPARAM lParam) except 0
    BOOL pymPostThreadMessage(unsigned long idThread, UINT Msg, WPARAM wParam, LPARAM lParam) except 0


    # ShowWindow
    int SW_HIDE, SW_MAXIMIZE, SW_MINIMIZE, SW_RESTORE, SW_SHOW
    int SW_SHOWDEFAULT, SW_SHOWMAXIMIZED, SW_SHOWMINIMIZED
    int SW_SHOWMINNOACTIVE, SW_SHOWNA, SW_SHOWNOACTIVATE
    int SW_SHOWNORMAL
    
    # SetWindowPos
    HWND HWND_BOTTOM, HWND_NOTOPMOST, HWND_TOP, HWND_TOPMOST
    int SWP_ASYNCWINDOWPOS, SWP_DEFERERASE, SWP_DRAWFRAME, SWP_FRAMECHANGED
    int SWP_HIDEWINDOW, SWP_NOACTIVATE, SWP_NOCOPYBITS, SWP_NOMOVE
    int SWP_NOOWNERZORDER, SWP_NOREDRAW, SWP_NOREPOSITION, SWP_NOSENDCHANGING
    int SWP_NOSIZE, SWP_NOZORDER, SWP_SHOWWINDOW

    int CWnd_ShowWindow(void *o, int uFlags) except -1
    int CWnd_SetWindowPos(void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags) except -1
    int CWnd_SetWindowRgn(void *o, HRGN rgn, BOOL redraw) except 0
    
    ctypedef void *HDWP
    HDWP CWnd_BeginDeferWindowPos(unsigned long) except NULL
    BOOL CWnd_EndDeferWindowPos(HDWP) except 0
    HDWP CWnd_DeferWindowPos(HDWP defer, void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags) except NULL

    
    ctypedef struct WINDOWPLACEMENT:
        UINT length
        UINT flags
        UINT showCmd
        POINT ptMinPosition
        POINT ptMaxPosition
        RECT rcNormalPosition

    BOOL GetWindowPlacement(HWND hWnd, WINDOWPLACEMENT *lpwndpl)

    cdef DWORD LWA_COLORKEY, LWA_ALPHA
    
    BOOL CWnd_SetLayeredWindowAttributes(void *o, COLORREF crKey, BYTE bAlpha, DWORD dwFlags) except 0


    int GetUpdateRect(HWND hWnd, RECT *rc, int bErase) nogil
    int CWnd_CalcWindowRect(void *o, RECT *rc)
    
    int CWnd_EnableWindow(void *o, int enable) except 0

    int CWnd_ScrollWindowEx(void *o, int dx, int dy,
      RECT *prcScroll, RECT *prcClip,
      HRGN hrgnUpdate, RECT *prcUpdate,  
      int erase, int invalidate, int scrollchildren, int smooth) except 0


    int CWnd_ShowScrollBar(void *o, int horz, int vert, int show)
    int CWnd_SetScrollInfo(void *o, object horz, object vert, object min, object max, object page, object pos, object disablenoscroll, object redraw) except 0
    object CWnd_GetScrollInfo(void *o, object horz, object vert)
    
    BOOL CWnd_UpdateWindow(void *o) except 0


    # MessageBox
    cdef UINT MB_ABORTRETRYIGNORE, MB_OK, MB_OKCANCEL, MB_RETRYCANCEL
    cdef UINT MB_YESNO, MB_YESNOCANCEL, MB_ICONEXCLAMATION
    cdef UINT MB_ICONWARNING, MB_ICONINFORMATION, MB_ICONASTERISK
    cdef UINT MB_ICONQUESTION, MB_ICONSTOP, MB_ICONERROR, MB_ICONHAND
    cdef UINT MB_DEFBUTTON1, MB_DEFBUTTON2, MB_DEFBUTTON3
    cdef UINT MB_DEFBUTTON4, MB_APPLMODAL, MB_SYSTEMMODAL
    cdef UINT MB_TASKMODAL, MB_DEFAULT_DESKTOP_ONLY, MB_HELP, MB_RIGHT
    cdef UINT MB_RTLREADING, MB_SETFOREGROUND, MB_TOPMOST

    BOOL CWnd_TrackMouseEvent(void *o, int cancel, int hover, int leave, int nonclient, int hoverTime) except 0

    cdef int DLGC_BUTTON, DLGC_DEFPUSHBUTTON, DLGC_HASSETSEL, DLGC_RADIOBUTTON
    cdef int DLGC_STATIC, DLGC_UNDEFPUSHBUTTON, DLGC_WANTALLKEYS, DLGC_WANTARROWS
    cdef int DLGC_WANTCHARS, DLGC_WANTMESSAGE, DLGC_WANTTAB

