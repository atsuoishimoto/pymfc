// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pymwndbase.h"

#include "pymwnd.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


const TCHAR *pymRegisterWndClass(long nClassStyle, HANDLE hCursor, HANDLE hbrBackground, HANDLE hIcon) {
	PyMFC_PROLOGUE(pymFormatMessage);

	return AfxRegisterWndClass(nClassStyle, (HCURSOR)hCursor, (HBRUSH)hbrBackground, (HICON)hIcon);

	PyMFC_EPILOGUE(NULL);
}

//
// CWnd wrappers
//

void *new_CWnd(PyObject *obj) {
	PyMFC_PROLOGUE(new_CWnd);
	
	return static_cast<CWnd*>(new PyMFCWnd<CWnd, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}


int CWnd_Delete(void *o) {
	PyMFC_PROLOGUE(CWnd_Delete);

	PyMFCWndBase *wnd = getWndBase(o);
	CWnd *cwnd = getCWnd<CWnd>(o);
	
	if (wnd->isTemp()) {
		cwnd->UnsubclassWindow();
	}
	else {
		wnd->unlockObj();
	}

	{
		PyMFCLeavePython lp;

		// CWnd objects should be deleted in the main UI thread.
		// (ex: CFrame object manages a list of frames in the 
		// thread local storage.)
		if (wnd->m_threadId == GetCurrentThreadId()) {
			delete wnd;
		}
		else {
			PYMFC_AFX_DLLSTATE::RegisterDeleteWnd(cwnd);
		}
	}

	return 1;

	PyMFC_EPILOGUE(0);
}
/*
int CWnd_Lock(void *o, int lock) {
	PyMFC_PROLOGUE(CWnd_LockCWnd);

	PyMFCWndBase *wnd = getWndBase(o);
	if (lock) {
		wnd->lockObj();
	}
	else {
		wnd->unlockObj();
	}
	return 1;
	PyMFC_EPILOGUE(0);
}
*/

HWND CWnd_Hwnd(void *o) {
	PyMFC_PROLOGUE(CWnd_Hwnd);
	
	CWnd *wnd = getCWnd<CWnd>(o);
	return wnd->m_hWnd;

	PyMFC_EPILOGUE(0);
}

int CWnd_Create(void *o, long dwExStyle, TCHAR *lpszClassName, 
	TCHAR *lpszWindowName, long dwStyle, int x, int y, int nWidth, 
	int nHeight, HWND hwndParent, HMENU nIDorHMenu) {

	PyMFC_PROLOGUE(CWnd_Create);

	ASSERT(o);
	int ret;
	{
		PyMFCLeavePython lp;
		PyMFCWndBase *wnd = getWndBase(o);
		ret = wnd->createWindow(dwExStyle, lpszClassName, 
				lpszWindowName, dwStyle, x, y, nWidth, 
				nHeight, (HWND)hwndParent, (HMENU)nIDorHMenu);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
	}
	return ret;

	PyMFC_EPILOGUE(0);
}


PyObject *CWnd_FromHandle(HWND hwnd) {
	PyMFC_PROLOGUE(CWnd_FromHandle);

	CWnd *f = CWnd::FromHandlePermanent(hwnd);
	if (f) {
		PyMFCWndBase *pw = dynamic_cast<PyMFCWndBase*>(f);
		if (pw) {
			PyDTObject ret(pw->getPyObj());
			return ret.detach();
		}
	}
	PyMFC_RETNONE();

	PyMFC_EPILOGUE(0);
}


int CWnd_Destroy(void *o) {
	PyMFC_PROLOGUE(CWnd_Destroy);

	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		if (!wnd->DestroyWindow()) {
			throw PyMFC_WIN32ERR();
		}
	}
	return 1;

	PyMFC_EPILOGUE(0);
}

long CWnd_DefWndProc(void *o, PyObject *msg) {
//long CWnd_DefWndProc(void *o, int message, WPARAM wParam, LPARAM lParam, long ret) {
	PyMFC_PROLOGUE(CWnd_DefWndProc);

	PyMFCWndBase *wnd = getWndBase(o);
	PyDTObject msgobj(msg, false);

	UINT message = msgobj.getAttr("message").getInt();
	WPARAM wParam = msgobj.getAttr("wparam").getInt();
	LPARAM lParam = (LPARAM)msgobj.getAttr("lparam").asVoidPtr();
	LRESULT ret = (LPARAM)msgobj.getAttr("result").getInt();

	long retval = wnd->callDefaultMsgProc(message, wParam, lParam, ret);
	
	// parse message again
	PyDTDict dict(((PyMFCWndMsgType::TypeInstance *)msgobj.get())->x_attr, false);
	wnd->parseMsg(message, wParam, lParam, dict);

	return retval;

	PyMFC_EPILOGUE(-1);
}

int CWnd_SubclassWindow(void *o, HWND hwnd, int temp) {
	PyMFC_PROLOGUE(CWnd_SubclassWindow);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		BOOL ret = wnd->SubclassWindow((HWND)hwnd);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}

		PyMFCWndBase *base= getWndBase(o);
		if (!temp) {
			base->lockObj();
			base->setTemp(false);   // rename setTemp() to something other good name.
		}
		else {
			base->setTemp(true);
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

HWND CWnd_UnsubclassWindow(void *o) {
	PyMFC_PROLOGUE(CWnd_UnsubclassWindow);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		HWND ret = wnd->UnsubclassWindow();
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		PyMFCWndBase *base= getWndBase(o);
		
		if (!base->isTemp()) {
			base->unlockObj();
		}

		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_L_L(void *o, int msg, WPARAM wparam, LPARAM lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_L_L);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_L_L_0(void *o, int msg, WPARAM wparam, LPARAM lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_L_L_0);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_L_L_m1(void *o, int msg, WPARAM wparam, LPARAM lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_L_L_m1);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		if (ret == -1) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_P_L(void *o, int msg, WPARAM wparam, void* lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_P_L);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_P_L_0(void *o, int msg, WPARAM wparam, void* lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_P_L_0);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

long CWnd_SendMessage_L_P_L_m1(void *o, int msg, WPARAM wparam, void* lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_L_P_L_0);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, wparam, (LPARAM)lparam);
		if (ret == -1) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(-1);
}

long CWnd_SendMessage_P_P_L(void *o, int msg, void* wparam, void* lparam) {
	PyMFC_PROLOGUE(CWnd_SendMessage_P_P_L);
	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		long ret = wnd->SendMessage(msg, (WPARAM)wparam, (LPARAM)lparam);
		return ret;
	}
	PyMFC_EPILOGUE(0);
}


HWND CWnd_GetDlgItem(void *o, long childid) {
	PyMFC_PROLOGUE(CWnd_GetDlgItem);

	CWnd *wnd = getCWnd<CWnd>(o);
	{
		PyMFCLeavePython lp;
		HWND ret = GetDlgItem(wnd->m_hWnd, childid);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

PyObject *CWnd_GetNextDlgTabItem(void *o, HWND hwnd, int prev) {
	PyMFC_PROLOGUE(CWnd_GetNextDlgTabItem);

	CWnd *wnd = getCWnd<CWnd>(o);
	HWND next;
	{
		PyMFCLeavePython lp;
		next = GetNextDlgTabItem(wnd->m_hWnd, hwnd, prev);
	}

	if (next) {
	    CWnd *w = CWnd::FromHandlePermanent(next);
	    if (w) {
		    PyMFCWndBase *base = dynamic_cast<PyMFCWndBase *>(w);
		    if (base) {
			    PyDTObject ret(base->getPyObj());
			    return ret.detach();
		    }
	    }
	}
	
	return PyDTNone().detach();

	PyMFC_EPILOGUE(0);
}


int CWnd_SetMenu(void *o, HMENU hMenu) {
	PyMFC_PROLOGUE(CWnd_SetMenu);

	{
		PyMFCLeavePython lp;
		ASSERT(IsMenu((HMENU)hMenu));
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!SetMenu(wnd->m_hWnd, (HMENU)hMenu)) {
			throw PyMFC_WIN32ERR();
		}
	}
	return 1;

	PyMFC_EPILOGUE(0);
}

int CWnd_DrawMenuBar(void *o) {
	PyMFC_PROLOGUE(CWnd_DrawMenuBar);

	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		wnd->DrawMenuBar();
	}
	return 1;

	PyMFC_EPILOGUE(0);
}


int CWnd_SetActiveWindow(void *o) {
	PyMFC_PROLOGUE(CWnd_SetActiveWindow);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		CWnd *ret = wnd->SetActiveWindow();
		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}

int CWnd_SetForegroundWindow(void *o) {
	PyMFC_PROLOGUE(CWnd_SetForegroundWindow);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!wnd->SetForegroundWindow()) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}

PyObject *CWnd_GetActiveWindow() {
	PyMFC_PROLOGUE(CWnd_GetActiveWindow);
	
	// todo: handle non-PyMFC window.
	CWnd *f = CWnd::GetActiveWindow();
	if (f) {
		PyMFCWndBase *pw = dynamic_cast<PyMFCWndBase*>(f);
		if (pw) {
			PyDTObject ret(pw->getPyObj());
			return ret.detach();
		}
	}
	PyMFC_RETNONE();
		
	PyMFC_EPILOGUE(0);
}



PyObject *CWnd_GetForegroundWindow() {
	PyMFC_PROLOGUE(CWnd_GetForegroundWindow);
	
	// todo: handle non-PyMFC window.
	CWnd *f = CWnd::GetForegroundWindow();
	if (f) {
		PyMFCWndBase *pw = dynamic_cast<PyMFCWndBase*>(f);
		if (pw) {
			PyDTObject ret(pw->getPyObj());
			return ret.detach();
		}
	}
	PyMFC_RETNONE();
		
	PyMFC_EPILOGUE(0);
}


BOOL CWnd_SetLayeredWindowAttributes(void *o, COLORREF crKey, BYTE bAlpha, DWORD dwFlags) {
	PyMFC_PROLOGUE(CWnd_SetLayeredWindowAttributes);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!wnd->SetLayeredWindowAttributes(crKey, bAlpha, dwFlags))
			throw PyMFC_WIN32ERR();

		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}

PyObject *CWnd_GetFocus() {
	PyMFC_PROLOGUE(CWnd_GetFocus);
	
	// todo: handle non-PyMFC window.
	CWnd *f = CWnd::GetFocus();
	if (f) {
		PyMFCWndBase *pw = dynamic_cast<PyMFCWndBase*>(f);
		if (pw) {
			PyDTObject ret(pw->getPyObj());
			return ret.detach();
		}
	}
	PyMFC_RETNONE();
		
	PyMFC_EPILOGUE(0);
}

int CWnd_SetFocus(void *o) {
	PyMFC_PROLOGUE(CWnd_SetFocus);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		wnd->SetFocus();
		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}

BOOL CWnd_SetCapture(void *o) {
	PyMFC_PROLOGUE(CWnd_SetCapture);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		wnd->SetCapture();
		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}

BOOL CWnd_ReleaseCapture() {
	PyMFC_PROLOGUE(CWnd_SetFocus);
	{
		ReleaseCapture();
		return TRUE;
	}

	PyMFC_EPILOGUE(0);
}


HFONT CWnd_GetFont(void *o) {
	PyMFC_PROLOGUE(CWnd_GetFont);

	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
        return (HFONT)wnd->SendMessage(WM_GETFONT, 0, 0);
	}

	PyMFC_EPILOGUE(0);
}

int CWnd_SetFont(void *o, HFONT hfont, int redraw) {
	PyMFC_PROLOGUE(CWnd_SetFont);

	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		SendMessage(wnd->m_hWnd, WM_SETFONT, (WPARAM)hfont, redraw);
	}
	return 1;

	PyMFC_EPILOGUE(0);
}

int CWnd_ShowWindow(void *o, int uFlags) {
	PyMFC_PROLOGUE(CWnd_ShowWindow);
	{
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!wnd->m_hWnd) {
			throw PyMFCException("Invalid CWnd");
		}
		{
			PyMFCLeavePython lp;
			return ::ShowWindow(wnd->m_hWnd, uFlags);
		}
	}
	PyMFC_EPILOGUE(-1);
}

int CWnd_SetWindowPos(void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags) {
	PyMFC_PROLOGUE(CWnd_SetWindowPos);
	{
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!wnd->m_hWnd) {
			throw PyMFCException("Invalid CWnd");
		}
		{
			PyMFCLeavePython lp;
			return ::SetWindowPos(wnd->m_hWnd, hWndInsertAfter, X, Y, cx, cy, uFlags);
		}
		return 1;
	}
	PyMFC_EPILOGUE(-1);
}

int CWnd_SetWindowRgn(void *o, HRGN rgn, BOOL redraw) {
	PyMFC_PROLOGUE(CWnd_SetWindowPos);
	{
		PyMFCLeavePython lp;
		CWnd *wnd = getCWnd<CWnd>(o);
		if (!::SetWindowRgn(wnd->m_hWnd, rgn, redraw)) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}


/*
PYMFC_API int CWnd_BeginDeferWindowPos(long);
PYMFC_API int CWnd_EndDeferWindowPos(long);
PYMFC_API int CWnd_DeferWindowPos(long defer, long o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags);
*/

HDWP CWnd_BeginDeferWindowPos(long n) {
	PyMFC_PROLOGUE(CWnd_BeginDeferWindowPos);
	{
		PyMFCLeavePython lp;
		
		HDWP ret = BeginDeferWindowPos(n);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;		
	}
	PyMFC_EPILOGUE(0);
}

BOOL CWnd_EndDeferWindowPos(HDWP hdwp) {
	PyMFC_PROLOGUE(CWnd_EndDeferWindowPos);
	{
		PyMFCLeavePython lp;
		
		long ret = EndDeferWindowPos((HDWP)hdwp);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;		
	}
	PyMFC_EPILOGUE(0);
}

HDWP CWnd_DeferWindowPos(HDWP defer, void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags) {
	PyMFC_PROLOGUE(CWnd_DeferWindowPos);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		HDWP ret = ::DeferWindowPos(defer, wnd->m_hWnd, hWndInsertAfter, X, Y, cx, cy, uFlags);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

int CWnd_CalcWindowRect(void *o, RECT *rc) {
	PyMFC_PROLOGUE(CWnd_CalcWindowRect);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		wnd->CalcWindowRect(rc);
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

int CWnd_EnableWindow(void *o, int enable) {
	PyMFC_PROLOGUE(CWnd_EnableWindow);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		::EnableWindow(wnd->m_hWnd, enable);
		return 1;
	}
	PyMFC_EPILOGUE(0);
}


int CWnd_ScrollWindowEx(void *o, int dx, int dy,
  RECT *prcScroll, RECT *prcClip,
  HRGN hrgnUpdate, RECT *prcUpdate,  
  int erase, int invalidate, int scrollchildren, int smooth) {

	PyMFC_PROLOGUE(CWnd_ScrollWindowEx);
	
	UINT flag = 0;
	if (erase)
		flag |= SW_ERASE;
	if (invalidate)
		flag |= SW_INVALIDATE;
	if (scrollchildren)
		flag |= SW_SCROLLCHILDREN;
//	if (smooth)
//		flag |= SW_SMOOTHSCROLL;

	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		int ret = ::ScrollWindowEx(wnd->m_hWnd, dx, dy, prcScroll, prcClip,
			hrgnUpdate, prcUpdate, flag);

		if (ret == ERROR) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}


int CWnd_ShowScrollBar(void *o, int horz, int vert, int show) {
	PyMFC_PROLOGUE(CWnd_ShowScrollBar);

	CWnd *wnd = getCWnd<CWnd>(o);

    UINT f = SB_CTL;
    if (horz && vert) {
        f = SB_BOTH;
    }
    else if (horz) {
        f = SB_HORZ;
    }
    else if (vert) {
        f = SB_VERT;
    }
	{
		PyMFCLeavePython lp;
		wnd->ShowScrollBar(f, show);
	}
	return 1;
	
	PyMFC_EPILOGUE(0);
}

int CWnd_SetScrollInfo(void *o, PyObject *horz, PyObject *vert, PyObject *min, PyObject *max, 
					   PyObject *page, PyObject *pos, PyObject *disablenoscroll, PyObject *redraw) {
	PyMFC_PROLOGUE(CWnd_SetScrollInfo);

	CWnd *wnd = getCWnd<CWnd>(o);
	
	
	int nBar = SB_CTL;
	if (PyDTObject(horz, false).getInt()) {
		nBar= SB_HORZ;
	}
	else if (PyDTObject(vert, false).getInt()) {
		nBar= SB_VERT;
	}
	
	BOOL fRedraw = PyDTObject(redraw, false).getInt();
	
	SCROLLINFO si;
	memset(&si, 0, sizeof(si));
	si.cbSize = sizeof(si);

	PyDTObject p_min(min, false), p_max(max, false);
	if (!p_min.isNone() && !p_max.isNone()) {
		si.fMask |= SIF_RANGE;
		si.nMin = p_min.getInt();
		si.nMax = p_max.getInt();
	}

	PyDTObject p_page(page, false);
	if (!p_page.isNone()) {
		si.fMask |= SIF_PAGE;
		si.nPage= p_page.getInt();
	}

	PyDTObject p_pos(pos, false);
	if (!p_pos.isNone()) {
		si.fMask |= SIF_POS;
		si.nPos= p_pos.getInt();
	}

	if (!PyDTObject(disablenoscroll, false).isNone()) {
		si.fMask |= SIF_DISABLENOSCROLL;
	}

//	printf("+++++++++\n");
//	printf("horz:%d vert:%d\n", nBar==SB_HORZ, nBar=SB_VERT);
//	printf("pos:%d min:%d max:%d\n", si.nPos, si.nMin, si.nMax);

	{
		PyMFCLeavePython lp;
		wnd->SetScrollInfo(nBar, &si, fRedraw);
	}
	return TRUE;
	
	PyMFC_EPILOGUE(0);
}

PyObject *CWnd_GetScrollInfo(void *o, PyObject *horz, PyObject *vert) {
	PyMFC_PROLOGUE(CWnd_GetScrollInfo);

	CWnd *wnd = getCWnd<CWnd>(o);
	
	int nBar = SB_CTL;
	if (PyDTObject(horz, false).getInt()) {
		nBar= SB_HORZ;
	}
	else if (PyDTObject(vert, false).getInt()) {
		nBar= SB_VERT;
	}
	
	SCROLLINFO si;
	memset(&si, 0, sizeof(si));

	si.cbSize = sizeof(si);
	si.fMask = SIF_ALL;
	
	if (!wnd->GetScrollInfo(nBar, &si)) {
		throw PyMFC_WIN32ERR();
	}

	PyDTTuple ret(5);
	ret.setItem(0, PyDTInt(si.nMin));
	ret.setItem(1, PyDTInt(si.nMax));
	ret.setItem(2, PyDTInt(si.nPage));
	ret.setItem(3, PyDTInt(si.nPos));
	ret.setItem(4, PyDTInt(si.nTrackPos));
	
	return ret.detach();
	
	PyMFC_EPILOGUE(0);
}


BOOL CWnd_UpdateWindow(void *o) {
	PyMFC_PROLOGUE(CWnd_UpdateWindow);
	{
		PyMFCLeavePython lp;

		CWnd *wnd = getCWnd<CWnd>(o);
		int ret = ::UpdateWindow(wnd->m_hWnd);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}


BOOL CWnd_TrackMouseEvent(void *o, int cancel, int hover, int leave, int nonclient, int hoverTime) {
	PyMFC_PROLOGUE(CWnd_TrackMouseEvent);
	{
		CWnd *wnd = getCWnd<CWnd>(o);

		TRACKMOUSEEVENT ev;
		memset(&ev, 0, sizeof(ev));
		ev.cbSize = sizeof(ev);
		ev.dwFlags = 0;
		if (cancel)
			ev.dwFlags |= TME_CANCEL;
		if (hover)
			ev.dwFlags |= TME_HOVER;
		if (leave)
			ev.dwFlags |= TME_LEAVE;
//		if (nonclient)
//			ev.dwFlags |= TME_NONCLIENT;
		ev.dwHoverTime = hoverTime;
		ev.hwndTrack = wnd->m_hWnd;

		{
			PyMFCLeavePython lp;
			BOOL ret = _TrackMouseEvent(&ev);
			if (!ret) {
				throw PyMFC_WIN32ERR();
			}
			return TRUE;
		}
	}
	PyMFC_EPILOGUE(0);
}


void *new_CEdit(PyObject *obj) {
	PyMFC_PROLOGUE(new_CEdit);
	
	return static_cast<CWnd*>(new PyMFCWnd<CEdit, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}





class PyMFCRichEditMsgParser: public PyMFCMsgParser {
public:
	PyMFCRichEditMsgParser(){}
protected:
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		PyMFCMsgParser::parse_notify(wnd, msg, wParam, lParam, ret);

		NMHDR *h = (LPNMHDR)lParam;
		ENLINK *enlink;

		switch (h->code) {
			case EN_MSGFILTER: break;
			case EN_REQUESTRESIZE: break;
			case EN_SELCHANGE: break;
			case EN_DROPFILES: break;
			case EN_PROTECTED: break;
			case EN_CORRECTTEXT: break;
			case EN_STOPNOUNDO: break;
			case EN_IMECHANGE: break;
			case EN_SAVECLIPBOARD: break;
			case EN_OLEOPFAILED: break;
			case EN_OBJECTPOSITIONS: break;
			case EN_LINK:
				{
					enlink = (ENLINK *)lParam;
					
					// set message dict of the message caused EN_LINK notification
					PyMFCMsgParser::parse(wnd, enlink->msg, enlink->wParam, enlink->lParam, ret);
					
					ret.setItem("cause", enlink->msg);
					ret.setItem("min", enlink->chrg.cpMin);
					ret.setItem("max", enlink->chrg.cpMax);
				}
				break;
			case EN_DRAGDROPDONE: break;
			case EN_PARAGRAPHEXPANDED: break;
			case EN_PAGECHANGE: break;
			case EN_LOWFIRTF: break;
			case EN_ALIGNLTR: break;
			case EN_ALIGNRTL: break;
		}
	}
};


class PyMFCRichEditCtrl:public PyMFCWnd<CRichEditCtrl, PyMFCRichEditMsgParser> {
public:
	PyMFCRichEditCtrl(PyObject *obj):PyMFCWnd<CRichEditCtrl, PyMFCRichEditMsgParser>(obj) {
	}

	virtual int createWindow(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {

		if (!AfxInitRichEdit2())
			return FALSE;

		return PyMFCWnd<CRichEditCtrl, PyMFCRichEditMsgParser>::createWindow(
			dwExStyle, lpszClassName, lpszWindowName, dwStyle, x, y, nWidth, nHeight, 
			hwndParent, nIDorHMenu);
	}
};

void *new_RichEdit(PyObject *obj) {
	PyMFC_PROLOGUE(new_RichEdit);

	return static_cast<CWnd*>(new PyMFCRichEditCtrl(obj));

	PyMFC_EPILOGUE(0);
}


static 
DWORD CALLBACK richEditStreamIn(DWORD dwCookie, LPBYTE pbBuff, LONG cb, LONG *pcb) {

	PyMFCEnterPython ep;
	PyDTObject stream((PyObject *)dwCookie, false);

	try {
		PyDTString ret = stream.callMethod("read", "i", cb);
		size_t readlen = ret.size();
		*pcb = readlen;

		if (readlen) {
			int len;
			const char *buf = ret.asStringAndSize(len);
			memcpy(pbBuff, buf, readlen);
		}
	}
	catch(PyDTException &) {
		return 1;
	}
	return 0;
}

long RichEdit_StreamIn(void *o, PyObject *rtf, int flag) {
	PyMFC_PROLOGUE(RichEdit_StreamIn);

	CRichEditCtrl *richedit = getCWnd<CRichEditCtrl>(o);

	EDITSTREAM es;
	memset(&es, 0, sizeof(es));
	es.dwCookie = (DWORD)rtf;
	es.pfnCallback = richEditStreamIn;

	long ret;
	{
		PyMFCLeavePython lp;
		ret = richedit->StreamIn(flag, es);
	}
	
	if (es.dwError) {
		return 0;
	}
	else {
		return TRUE;
	}
	
	PyMFC_EPILOGUE(0);
}

static 
DWORD CALLBACK richEditStreamOut(DWORD dwCookie, LPBYTE pbBuff, LONG cb, LONG *pcb) {

	PyMFCEnterPython ep;
	PyDTObject stream((PyObject *)dwCookie, false);

	try {
		PyDTString s((char*)pbBuff, cb);
		stream.callMethod("write", "O", s.get());
		*pcb = cb;
	}
	catch(PyDTException &) {
		return 1;
	}
	return 0;
}


long RichEdit_StreamOut(void *o, PyObject *rtf, int flag) {
	PyMFC_PROLOGUE(RichEdit_StreamOut);

	CRichEditCtrl *richedit = getCWnd<CRichEditCtrl>(o);

	EDITSTREAM es;
	memset(&es, 0, sizeof(es));
	es.dwCookie = (DWORD)rtf;
	es.pfnCallback = richEditStreamOut;

	long ret;
	{
		PyMFCLeavePython lp;
		ret = richedit->StreamOut(flag, es);
	}
	
	if (es.dwError) {
		return 0;
	}
	else {
		return TRUE;
	}
	
	PyMFC_EPILOGUE(0);
}


void *new_CStatic(PyObject *obj) {
	PyMFC_PROLOGUE(new_CStatic);
	
	return static_cast<CWnd*>(new PyMFCWnd<CStatic, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

void *new_CButton(PyObject *obj) {
	PyMFC_PROLOGUE(new_CButton);
	
	return static_cast<CWnd*>(new PyMFCWnd<CButton, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

void *new_CListBox(PyObject *obj) {
	PyMFC_PROLOGUE(new_CListBox);
	
	return static_cast<CWnd*>(new PyMFCWnd<CListBox, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

void *new_CComboBox(PyObject *obj) {
	PyMFC_PROLOGUE(new_CComboBox);
	
	return static_cast<CWnd*>(new PyMFCWnd<CComboBox, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

void *new_CScrollBar(PyObject *obj) {
	PyMFC_PROLOGUE(new_CScrollBar);
	
	return static_cast<CWnd*>(new PyMFCWnd<CScrollBar, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

