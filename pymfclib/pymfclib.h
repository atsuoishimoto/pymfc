// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#if !defined(AFX_PYMFCLIB_H__D98BD5DB_C877_450A_8C4B_00D0EE5B923F__INCLUDED_)
#define AFX_PYMFCLIB_H__D98BD5DB_C877_450A_8C4B_00D0EE5B923F__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"

#include "pydt.h"
#include "pymfclib_i.h"

/////////////////////////////////////////////////////////////////////////////
// CPymfclibApp

class CPymfclibApp : public CWinApp
{
public:
	CPymfclibApp();
	~CPymfclibApp();
	void setIdleProc(PyObject *proc);
	void setTimerProcs(PyObject *proc);
	BOOL OnKickIdle(LONG lCount);

	//{{AFX_VIRTUAL(CPymfclibApp)
	public:
	virtual int Run();
	virtual BOOL OnIdle(LONG lCount);
	virtual int ExitInstance();
	//}}AFX_VIRTUAL

	//{{AFX_MSG(CPymfclibApp)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()

	BOOL PreTranslateMessage(MSG* pMsg);
	PyDTObject m_idleProc;
	PyDTDict m_timerProcs;
	int m_runningIdleProc;




	virtual BOOL IsIdleMessage(MSG* pMsg); 
	virtual BOOL InitInstance();
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}

#endif // !defined(AFX_PYMFCLIB_H__D98BD5DB_C877_450A_8C4B_00D0EE5B923F__INCLUDED_)
