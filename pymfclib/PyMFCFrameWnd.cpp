// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

// PyMFCFrameWnd.cpp : インプリメンテーション ファイル
//

#include "stdafx.h"
#include "pymfclib.h"
#include "pymfcdefs.h"
#include "pymwndbase.h"
#include "pymwnd.h"
#include "PyMFCFrameWnd.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// PyMFCFrameWnd

IMPLEMENT_DYNCREATE(PyMFCFrameWnd, CFrameWnd)

void * new_Frame(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_Frame);

	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCFrameWnd, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

int CFrame_CreateWnd(void *o, long dwExStyle, TCHAR *lpszClassName, 
	TCHAR *lpszWindowName, long dwStyle, int x, int y, int nWidth, 
	int nHeight, HWND hwndParent, HMENU nIDorHMenu) {

	PyMFC_PROLOGUE(Frame_CreateWnd);

	int ret;
	{
		PyMFCLeavePython lp;

		PyMFCFrameBase *f = getCWnd<PyMFCFrameBase>(o);
		ret = f->FrameCreate(dwExStyle, lpszClassName, 
				lpszWindowName, dwStyle, x, y, nWidth, 
				nHeight, (HWND)hwndParent, (HMENU)nIDorHMenu);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
	}
	return ret;

	PyMFC_EPILOGUE(0);

}


int CFrame_EnableDocking(void *o, int left, int top, int right, int bottom, int any) {
	PyMFC_PROLOGUE(Frame_EnableDocking);

	CFrameWnd *wnd = getCWnd<CFrameWnd>(o);

	DWORD flag=0;
	if (left) {
		flag |= CBRS_ALIGN_LEFT;
	}
	if (top) {
		flag |= CBRS_ALIGN_TOP;
	}
	if (right) {
		flag |= CBRS_ALIGN_RIGHT;
	}
	if (bottom) {
		flag |= CBRS_ALIGN_BOTTOM;
	}
	if (any) {
		flag |= CBRS_ALIGN_ANY;
	}

	{
		PyMFCLeavePython lp;
		wnd->EnableDocking(flag);
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CFrame_DockControlBar(void *o, void *cbar, int left, int top, int right, int bottom) {
	PyMFC_PROLOGUE(Frame_DockControlBar);

	CFrameWnd *wnd = getCWnd<CFrameWnd>(o);
	CControlBar *ctrl = getCWnd<CControlBar>(cbar);
	DWORD flag=0;
	if (left) {
		flag |= AFX_IDW_DOCKBAR_LEFT;
	}
	if (top) {
		flag |= AFX_IDW_DOCKBAR_TOP;
	}
	if (right) {
		flag |= AFX_IDW_DOCKBAR_RIGHT;
	}
	if (bottom) {
		flag |= AFX_IDW_DOCKBAR_BOTTOM;
	}

	{
		PyMFCLeavePython lp;
		wnd->DockControlBar(ctrl, flag);
	}

	return TRUE;
	PyMFC_EPILOGUE(0);
}

void CFrame_ShowControlBar(void *o, void *cbar, int show, int delay) {
	PyMFC_PROLOGUE(CFrame_ShowControlBar);

	CFrameWnd *wnd = getCWnd<CFrameWnd>(o);
	CControlBar *ctrl = getCWnd<CControlBar>(cbar);
	wnd->ShowControlBar(ctrl, show, delay);

	PyMFC_VOID_EPILOGUE();
}


PyMFCFrameWnd::PyMFCFrameWnd()
{
	m_bAutoMenuEnable = FALSE;
}

PyMFCFrameWnd::~PyMFCFrameWnd()
{
}





BEGIN_MESSAGE_MAP(PyMFCFrameWnd, CFrameWnd)
	//{{AFX_MSG_MAP(PyMFCFrameWnd)
	ON_WM_DESTROY()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

BOOL PyMFCFrameWnd::FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {
	
	m_strTitle = lpszWindowName;    // save title for later
	m_hMenuDefault = nIDorHMenu;
	if (!CFrameWnd::CreateEx(dwExStyle, lpszClassName, lpszWindowName, dwStyle,
		x, y, nWidth, nHeight,
		hwndParent, nIDorHMenu, NULL))
	{
		if (nIDorHMenu != NULL)
			DestroyMenu(nIDorHMenu);
		return FALSE;
	}
	
	// Without this, toolbars aren't positioned correct.
	ModifyStyleEx(WS_EX_CLIENTEDGE, 0, SWP_FRAMECHANGED);	
	return TRUE;
}

void PyMFCFrameWnd::PostNcDestroy() 
{
	// does nothing.
}

void PyMFCFrameWnd::OnDestroy() 
{
	m_hMenuDefault = NULL;
	SetMenu(NULL);	// Don't let menu destroy
	CFrameWnd::OnDestroy();
}


void *new_MDIFrame(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_MDIFrame);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCMDIFrame, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

PyObject *CMDIFrame_GetActive(void *o) {
	PyMFC_PROLOGUE(MDIFrame_GetActive);

	CWnd *wnd = getCWnd<CWnd>(o);
	CWnd *active = dynamic_cast<CMDIFrameWnd *>(wnd)->MDIGetActive();
	if (active) {
		PyMFCWndBase *wnd = dynamic_cast<PyMFCWndBase *>(active);
		if (wnd) {
			PyDTObject ret(wnd->getPyObj());
			if (ret.get()) {
				return ret.detach();
			}
		}
	}
	
	return PyDTNone().detach();

	PyMFC_EPILOGUE(NULL);
}



IMPLEMENT_DYNCREATE(PyMFCMDIFrame, CMDIFrameWnd)

PyMFCMDIFrame::PyMFCMDIFrame()
{
	m_bAutoMenuEnable = FALSE;
}

PyMFCMDIFrame::~PyMFCMDIFrame()
{
}


BEGIN_MESSAGE_MAP(PyMFCMDIFrame, CMDIFrameWnd)
	//{{AFX_MSG_MAP(PyMFCMDIFrame)
	ON_WM_DESTROY()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

BOOL PyMFCMDIFrame::FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {
	
	m_strTitle = lpszWindowName;    // save title for later
	m_hMenuDefault = nIDorHMenu;

	if (!CMDIFrameWnd::CreateEx(dwExStyle, lpszClassName, lpszWindowName, dwStyle,
		x, y, nWidth, nHeight,
		hwndParent, nIDorHMenu, NULL))
	{
		if (nIDorHMenu != NULL)
			DestroyMenu(nIDorHMenu);
		return FALSE;
	}

	ModifyStyleEx(WS_EX_CLIENTEDGE, 0, SWP_FRAMECHANGED);
	return TRUE;
}


void PyMFCMDIFrame::PostNcDestroy() 
{
	// does nothing
}

void PyMFCMDIFrame::OnDestroy() 
{
	SetMenu(NULL);	// Don't let menu destroy
	m_hMenuDefault = NULL;
	CMDIFrameWnd::OnDestroy();
}


/////////////////////////////////////////////////////////////////////////////
// PyMFCMDIChild

void *new_MDIChild(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_MDIChild);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCMDIChild, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

IMPLEMENT_DYNCREATE(PyMFCMDIChild, CMDIChildWnd)

PyMFCMDIChild::PyMFCMDIChild()
{
}

PyMFCMDIChild::~PyMFCMDIChild()
{
}


BEGIN_MESSAGE_MAP(PyMFCMDIChild, CMDIChildWnd)
	//{{AFX_MSG_MAP(PyMFCMDIChild)
	ON_WM_DESTROY()
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

BOOL PyMFCMDIChild::FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {
	
	CMDIFrameWnd *p = (CMDIFrameWnd*)CWnd::FromHandle(hwndParent);
	if (!dynamic_cast<CMDIFrameWnd *>(p)) {
		throw PyMFCException("Incorrect parent window.");
	}

	m_hMenuShared = nIDorHMenu;
	return CMDIChildWnd::Create(NULL, lpszWindowName, dwStyle, 
		CRect(x, y, x+nWidth, y+nHeight), p, NULL);

	return TRUE;
}


void PyMFCMDIChild::PostNcDestroy() 
{
	// does nothing
}

void PyMFCMDIChild::OnDestroy() 
{
	m_hMenuDefault = NULL;
	m_hMenuShared = NULL;
	SetMenu(NULL);	// Prevent menu being destroyed by mfc. Menu will be destroyed by pymfc

	CMDIChildWnd::OnDestroy();
}


