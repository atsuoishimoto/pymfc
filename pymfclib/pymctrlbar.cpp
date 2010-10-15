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


int CControlBar_EnableDocking(void *o, int left, int top, 
							  int right, int bottom, int any, int multi) {

	PyMFC_PROLOGUE(CWnd_SetFont);
	{
		PyMFCLeavePython lp;
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
		
		CControlBar *bar = getCWnd<CControlBar>(o);
		bar->EnableDocking(flag);
		return 1;
	}
	PyMFC_EPILOGUE(0);
}




void *new_CStatusBar(PyObject *obj) {
	PyMFC_PROLOGUE(new_CStatusBar);

	return static_cast<CWnd*>(new PyMFCWnd<CStatusBar, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

int CStatusBar_Create(void *o, void *parent, PyObject *lens) {
	PyMFC_PROLOGUE(CStatusBar_Create);
	
	CStatusBar *bar = getCWnd<CStatusBar>(o);
	CWnd *p = getCWnd<CWnd>(parent);
	
	PyDTSequence panes(lens, false);

	int n = panes.getSize();
	std::vector<int> width;
	for (int i = 0; i < n; i++) 
	{
		width.push_back(panes.getItem(i).getInt());
	}

	{
		PyMFCLeavePython lp;
		BOOL ret = bar->Create(p);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}

		// set numbers of pane
		std::vector<UINT> ids(n, 0);
		ret = bar->SetIndicators(&ids[0], n);

		HFONT hFont = (HFONT)bar->SendMessage(WM_GETFONT);
		CClientDC dcScreen(NULL);
		HGDIOBJ hOldFont = NULL;
		if (hFont != NULL)
			hOldFont = dcScreen.SelectObject(hFont);

		// set pane width
		for (int i = 0; i < n; i++) 
		{
			UINT nID, nStyle;
			int cxWidth;
			bar->GetPaneInfo(i, nID, nStyle, cxWidth);

			cxWidth = dcScreen.GetTextExtent(std::string(width[i], 'A').c_str()).cx;
			bar->SetPaneInfo(i, nID, nStyle, cxWidth);
		}

		if (hOldFont != NULL) {
			dcScreen.SelectObject(hOldFont);
		}
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CStatusBar_SetPaneText(void *o, int idx, TCHAR *s) {
	PyMFC_PROLOGUE(CStatusBar_SetPaneText);

	CStatusBar *bar = getCWnd<CStatusBar>(o);
	{
		PyMFCLeavePython lp;
		if (!bar->SetPaneText(idx, s)) {
			throw PyMFC_WIN32ERR();
		}
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CStatusBar_CalcFixedSize(void *o, SIZE *size) {
	PyMFC_PROLOGUE(CStatusBar_CalcFixedSize);

	CStatusBar *bar = getCWnd<CStatusBar>(o);
	{
		PyMFCLeavePython lp;
		CSize s = bar->CalcFixedLayout(FALSE, TRUE);
		size->cx = s.cx;
		size->cy = s.cy;
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}


class PyMFCToolBar:public PyMFCWnd<CToolBar, PyMFCMsgParser> {
public:
	PyMFCToolBar(PyObject *p):PyMFCWnd<CToolBar, PyMFCMsgParser>(p) {}
	~PyMFCToolBar() {
		int a = 0;
	}
	void OnUpdateCmdUI(CFrameWnd* pTarget, BOOL bDisableIfNoHndler) {
		// does nothing
	}
};

void *new_CToolBar(PyObject *obj) {
	PyMFC_PROLOGUE(new_CToolBar);

	return static_cast<CWnd*>(new PyMFCToolBar(obj));

	PyMFC_EPILOGUE(0);
}


int CToolBar_Create(void *o, void *parent, TCHAR *title, int id,
					int left, int top, int right, int bottom) {

	PyMFC_PROLOGUE(CToolBar_Create);

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

	CToolBar *bar = getCWnd<CToolBar>(o);
	CWnd *p = getCWnd<CWnd>(parent);

	BOOL ret;
	{
		PyMFCLeavePython lp;
		ret = bar->CreateEx(p, TBSTYLE_FLAT, CBRS_TOP| WS_CHILD | WS_VISIBLE
			| CBRS_GRIPPER | CBRS_TOOLTIPS | CBRS_FLYBY | CBRS_SIZE_DYNAMIC, CRect(0,0,0,0), id);

		bar->SetBarStyle(bar->GetBarStyle() |
			CBRS_TOOLTIPS | CBRS_FLYBY | CBRS_SIZE_DYNAMIC);
	}
	
	return ret;
	PyMFC_EPILOGUE(0);
}


int CToolBar_SetButtons(void *o, PyObject *buttonIds){
	PyMFC_PROLOGUE(CToolBar_SetButtons);

	PyDTSequence idlist(buttonIds, false);

	int n = idlist.getSize();
	std::vector<UINT> v_buttonIds;
	for (int i = 0; i < n; i++) 
	{
		v_buttonIds.push_back(idlist.getItem(i).getInt());
	}

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	{
		PyMFCLeavePython lp;
		BOOL ret = bar->SetButtons(&(v_buttonIds[0]), v_buttonIds.size());
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
	}

	return TRUE;
	PyMFC_EPILOGUE(0);
}

int CToolBar_SetBitmap(void *o, HBITMAP hbmp) {
	PyMFC_PROLOGUE(CToolBar_SetBitmap);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	{
		PyMFCLeavePython lp;
		BOOL ret = bar->SetBitmap((HBITMAP)hbmp);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
	}

	return TRUE;
	PyMFC_EPILOGUE(0);
}

int CToolBar_SetImageList(void *o, void *imageList) {
	PyMFC_PROLOGUE(CToolBar_SetImageList);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	{
		PyMFCLeavePython lp;
		CImageList *cimg = (CImageList *)imageList;
		CToolBarCtrl &ctrl = bar->GetToolBarCtrl();

		ctrl.SetImageList(cimg);
	}

	return TRUE;
	PyMFC_EPILOGUE(0);
}

int CToolBar_SetButtonInfo(void *o, int index, int id, int style, int iImage) {
	PyMFC_PROLOGUE(CToolBar_SetButtonInfo);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	{
		PyMFCLeavePython lp;
		bar->SetButtonInfo(index, id, style, iImage);
	}

	return TRUE;
	PyMFC_EPILOGUE(0);
}

PyObject *CToolBar_GetButtonInfo(void *o, int index) {
	PyMFC_PROLOGUE(CToolBar_GetButtonInfo);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	UINT id, style;
	int iImage;
	{
		PyMFCLeavePython lp;
		bar->GetButtonInfo(index, id, style, iImage);
	}
	PyDTTuple ret(3);
	ret.setItem(0, id);
	ret.setItem(1, iImage);
	ret.setItem(2, style);

	return ret.detach();
	PyMFC_EPILOGUE(0);
}

int CToolBar_GetButtonIndex(void *o, int id) {
	PyMFC_PROLOGUE(CToolBar_GetButtonIndex);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	return bar->CommandToIndex(id);
	
	PyMFC_EPILOGUE(0);
}

PyObject *CToolBar_GetItemRect(void *o, int index) {
	PyMFC_PROLOGUE(CToolBar_GetItemRect);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	RECT rc;
	{
		PyMFCLeavePython lp;
		bar->GetItemRect(index, &rc);
	}
	PyDTTuple ret(4);
	ret.setItem(0, rc.left);
	ret.setItem(1, rc.top);
	ret.setItem(2, rc.right);
	ret.setItem(3, rc.bottom);

	return ret.detach();
	
	PyMFC_EPILOGUE(0);
}

int CToolBar_GetButtonStyle(void *o, int index) {
	PyMFC_PROLOGUE(CToolBar_GetButtonStyle);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	return bar->GetButtonStyle(index);
	
	PyMFC_EPILOGUE(0);
}

void CToolBar_SetButtonStyle(void *o, int index, int style, int checked, 
							int indeterminate, int disabled, int pressed) {
	PyMFC_PROLOGUE(CToolBar_SetButtonStyle);

	CToolBar *bar = getCWnd<PyMFCToolBar>(o);
	
	if (checked != -1) {
		if (checked) {
			style |= TBBS_CHECKED;
		}
		else {
			style &= ~TBBS_CHECKED;
		}
	}
	
	if (indeterminate != -1) {
		if (indeterminate) {
			style |= TBBS_INDETERMINATE;
		}
		else {
			style &= ~TBBS_INDETERMINATE;
		}
	}
	
	if (disabled != -1) {
		if (disabled) {
			style |= TBBS_DISABLED;
		}
		else {
			style &= ~TBBS_DISABLED;
		}
	}
	
	if (pressed != -1) {
		if (pressed) {
			style |= TBBS_PRESSED;
		}
		else {
			style &= ~TBBS_PRESSED;
		}
	}
	
	bar->SetButtonStyle(index, style);
	
	PyMFC_VOID_EPILOGUE();
}



