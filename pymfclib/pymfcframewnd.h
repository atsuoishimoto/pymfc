// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#if !defined(AFX_PYMFCFRAMEWND_H__A16E456C_F652_4267_A092_1B36BBA95349__INCLUDED_)
#define AFX_PYMFCFRAMEWND_H__A16E456C_F652_4267_A092_1B36BBA95349__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000


class PyMFCFrameBase {
public:
	virtual BOOL FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) = 0;


};

class PyMFCFrameWnd : public CFrameWnd, public PyMFCFrameBase
{
	DECLARE_DYNCREATE(PyMFCFrameWnd)
protected:
	PyMFCFrameWnd();

public:
	LRESULT WindowProc(UINT message, WPARAM wParam, LPARAM lParam) {
		LRESULT ret = CFrameWnd::WindowProc(message, wParam, lParam);
		return ret;
	}
	virtual BOOL FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu);

	virtual void GetMessageString(UINT nID, CString &rMessage)const {
/*
		// for application title (defaults to EXE name or name in constructor)
		#define AFX_IDS_APP_TITLE               0xE000
		// idle message bar line
		#define AFX_IDS_IDLEMESSAGE             0xE001
		// message bar line when in shift-F1 help mode
		#define AFX_IDS_HELPMODEMESSAGE         0xE002
		// document title when editing OLE embedding
		#define AFX_IDS_APP_TITLE_EMBEDDING     0xE003
		// company name
		#define AFX_IDS_COMPANY_NAME            0xE004
		// object name when server is inplace
		#define AFX_IDS_OBJ_TITLE_INPLACE       0xE005
*/
/*
		char b[10];
		sprintf(b, "===%d", nID);
		rMessage = b;
*/		
	}

	//{{AFX_VIRTUAL(PyMFCFrameWnd)
	public:
	protected:
	virtual void PostNcDestroy();
	//}}AFX_VIRTUAL

protected:
	virtual ~PyMFCFrameWnd();

	//{{AFX_MSG(PyMFCFrameWnd)
	afx_msg void OnDestroy();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////

class PyMFCMDIFrame : public CMDIFrameWnd, public PyMFCFrameBase
{
	DECLARE_DYNCREATE(PyMFCMDIFrame)
protected:
	PyMFCMDIFrame();

public:

public:
	virtual BOOL FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu);

	//{{AFX_VIRTUAL(PyMFCMDIFrame)
	protected:
	virtual void PostNcDestroy();
	//}}AFX_VIRTUAL

protected:
	virtual ~PyMFCMDIFrame();

	//{{AFX_MSG(PyMFCMDIFrame)
	afx_msg void OnDestroy();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

class PyMFCMDIChild : public CMDIChildWnd, public PyMFCFrameBase
{
	DECLARE_DYNCREATE(PyMFCMDIChild)
protected:
	PyMFCMDIChild();

public:

public:
	virtual BOOL FrameCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu);


	//{{AFX_VIRTUAL(PyMFCMDIChild)
	protected:
	virtual void PostNcDestroy();
	//}}AFX_VIRTUAL

protected:
	virtual ~PyMFCMDIChild();

	//{{AFX_MSG(PyMFCMDIChild)
	afx_msg void OnDestroy();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

/////////////////////////////////////////////////////////////////////////////
//{{AFX_INSERT_LOCATION}}

#endif // !defined(AFX_PYMFCFRAMEWND_H__A16E456C_F652_4267_A092_1B36BBA95349__INCLUDED_)
