


cdef extern from "shellapi.h":
    int NIF_ICON, NIF_MESSAGE, NIF_TIP, NIF_STATE, NIF_INFO, NIF_GUID
    int NOTIFYICON_VERSION

    ctypedef struct NOTIFYICONDATA:
        DWORD cbSize
        HWND hWnd
        UINT uID
        UINT uFlags
        UINT uCallbackMessage
        HICON hIcon
        TCHAR szTip[128]
        DWORD dwState
        DWORD dwStateMask
        TCHAR szInfo[256]
        UINT uTimeout  # uTimeout and uVersion are union
        UINT uVersion
        TCHAR szInfoTitle[64]
        DWORD dwInfoFlags

    int NIM_ADD, NIM_DELETE, NIM_MODIFY, NIM_SETFOCUS, NIM_SETVERSION
    BOOL Shell_NotifyIcon(DWORD dwMessage, NOTIFYICONDATA *lpdata)
    int _WIN32_IE

cdef class _TrayNotify:
    cdef NOTIFYICONDATA _icondata

    cdef _setdata(self, icon, tip):
        if icon:
            self._icondata.hIcon=PyMFCHandle_AsHandle(icon.getHandle())
            self._icondata.uFlags = self._icondata.uFlags | NIF_ICON
        else:
            self._icondata.uFlags = self._icondata.uFlags & (~NIF_ICON)
            
        if tip:
            _tcsncpy(self._icondata.szTip, PyUnicode_AsUnicode(tip), sizeof(self._icondata.szTip))
            self._icondata.uFlags = self._icondata.uFlags | NIF_TIP
        else:
            self._icondata.uFlags = self._icondata.uFlags & (~NIF_TIP)
            

    def __init__(self, notifyid, icon=None, tip=None):
        self._icondata.cbSize = sizeof(NOTIFYICONDATA)
        self._icondata.uID = notifyid
        self._icondata.uFlags = NIF_MESSAGE
        self._icondata.uCallbackMessage = notifyid
        
        self._setdata(icon, tip)
        
    def addIcon(self, wnd):
        self._icondata.hWnd = PyMFCHandle_AsHandle(wnd.getHwnd())
        if not Shell_NotifyIcon(NIM_ADD, &self._icondata):
            pymRaiseWin32Err()

    def deleteIcon(self):
        if not Shell_NotifyIcon(NIM_DELETE, &self._icondata):
            pymRaiseWin32Err()

    def setIcon(self, icon=None, tip=None):
        self._setdata(icon, tip)
        if not Shell_NotifyIcon(NIM_MODIFY, &self._icondata):
            pymRaiseWin32Err()
        