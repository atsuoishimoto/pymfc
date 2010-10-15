// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pymwndbase.h"

#include "pymwnd.h"
#include "pymwin32funcs.h"
#include "pymutils.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


void *new_ImageList() {
	return new CImageList();
}

HIMAGELIST CImageList_HANDLE(void *o) {
	PyMFC_PROLOGUE(CImageList_HANDLE);
	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}
	return obj->m_hImageList;

	PyMFC_EPILOGUE(0);
}

int CImageList_Delete(void *o) {
	PyMFC_PROLOGUE(CImageList_Delete);
	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}
	delete obj;
	return 1;

	PyMFC_EPILOGUE(0);
}

int CImageList_Create(void *o, int cx, int cy, int nFlags, int nInitial, int nGrow) {
	PyMFC_PROLOGUE(CImageList_Create);
	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}

	if (!obj->Create(cx, cy, nFlags, nInitial, nGrow)) {
		throw PyMFC_WIN32ERR();
	}

	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CImageList_Attach(void *o, HIMAGELIST himagelist) {
	PyMFC_PROLOGUE(CImageList_Attach);

	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}
	return obj->Attach(himagelist);

	PyMFC_EPILOGUE(0);
}

int CImageList_Detach(void *o) {
	PyMFC_PROLOGUE(CImageList_Detach);

	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}

	obj->Detach();
	return 1;
	PyMFC_EPILOGUE(0);
}


int CImageList_AddImage(void *o, HBITMAP bmp, HBITMAP maskbmp, COLORREF maskrgb, HICON hicon) {
	PyMFC_PROLOGUE(CImageList_AddImage);

	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}
	if (hicon) {
		return obj->Add((HICON)hicon);
	}
	else {
		if (maskbmp) {
			return ImageList_Add(obj->m_hImageList, (HBITMAP)bmp, (HBITMAP)maskbmp);
//			return obj->Add((CBitmap *)bmp, (CBitmap *)maskbmp);
		}
		else {
			return ImageList_AddMasked(obj->m_hImageList, (HBITMAP)bmp, maskrgb);
//			return obj->Add((CBitmap *)bmp, maskrgb);
		}
	}
	PyMFC_EPILOGUE(-1);
}

int CImageList_BeginDrag(void *o, int n, int x, int y) {
	PyMFC_PROLOGUE(CImageList_BeginDrag);
	if (!o) {
		throw PyMFCException("NULL CImageList");
	}

	CImageList *obj= dynamic_cast<CImageList*>((CImageList*)o);
	if (!obj) {
		throw PyMFCException("Invalid CImageList");
	}

	return obj->BeginDrag(n, CPoint(x, y));
	PyMFC_EPILOGUE(0);
}

int CImageList_EndDrag() {
	PyMFC_PROLOGUE(CImageList_EndDrag);
	
	CImageList::EndDrag();
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CImageList_DragShowNolock(int f) {
	PyMFC_PROLOGUE(CImageList_DragShowNolock);

	return CImageList::DragShowNolock(f);

	PyMFC_EPILOGUE(0);
}

int CImageList_DragMove(int x, int y) {
	PyMFC_PROLOGUE(CImageList_DragMove);

	return CImageList::DragMove(CPoint(x, y));

	PyMFC_EPILOGUE(0);
}



class PyMFCTabMsgParser: public PyMFCMsgParser {
public:
	PyMFCTabMsgParser(){}
protected:
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		PyMFCMsgParser::parse_notify(wnd, msg, wParam, lParam, ret);

		NMHDR *h = (LPNMHDR)lParam;

		switch (h->code) {
		case TCN_KEYDOWN:break;
		case TCN_SELCHANGE:break;
		case TCN_SELCHANGING:break;
		case TCN_GETOBJECT:break;
		}
	}
};



void *new_TabCtrl(PyObject *obj) {
	PyMFC_PROLOGUE(new_TabCtrl);

	return static_cast<CWnd*>(new PyMFCWnd<CTabCtrl, PyMFCTabMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}

int CTabCtrl_AdjustRect(void *o, int larger, int *left, int *top, int *right, int *bottom) {
	PyMFC_PROLOGUE(CTabCtrl_AdjustRect);

	CTabCtrl *bar = getCWnd<CTabCtrl>(o);
	CRect rc;

	rc.left = *left;
	rc.top = *top;
	rc.right = *right;
	rc.bottom = *bottom;
	
	bar->AdjustRect(larger, &rc);

	*left = rc.left;
	*top = rc.top;
	*right = rc.right;
	*bottom = rc.bottom;
	
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int CTabCtrl_InsertItem(void *o, int idx, TCHAR *title) {
	PyMFC_PROLOGUE(CTabCtrl_InsertItem);

	CTabCtrl *bar = getCWnd<CTabCtrl>(o);
	{
		PyMFCLeavePython lp;
		if (bar->InsertItem(idx, title) == -1) {
			throw PyMFC_WIN32ERR();
		}
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}


class PyMFCTreeMsgParser: public PyMFCMsgParser {
public:
	PyMFCTreeMsgParser(){}
protected:
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		PyMFCMsgParser::parse_notify(wnd, msg, wParam, lParam, ret);

		NMHDR *h = (LPNMHDR)lParam;

		LPNMTREEVIEW tv;
		LPNMTVDISPINFO disp;
		
		switch (h->code) {
		case TVN_BEGINDRAG: break;
		case TVN_BEGINLABELEDIT: 
			disp = (LPNMTVDISPINFO)lParam;
			ret.setItem("hitem", PyMFCHandle(disp->item.hItem));
			ret.setItem("state", disp->item.state);
			ret.setItem("lparam", disp->item.lParam);
			ret.setItem("text", disp->item.pszText);
			break;
		case TVN_BEGINRDRAG: break;
		case TVN_DELETEITEM:
			tv = (LPNMTREEVIEW)lParam;
			ret.setItem("hitem",  PyMFCHandle(tv->itemOld.hItem));
			ret.setItem("lparam",  tv->itemOld.lParam);
			break;
		case TVN_ENDLABELEDIT: 
			disp = (LPNMTVDISPINFO)lParam;
			ret.setItem("hitem", PyMFCHandle(disp->item.hItem));
			ret.setItem("lparam", disp->item.lParam);
			if (disp->item.pszText) {
				ret.setItem("text", disp->item.pszText);
			}
			else {
				ret.setItem("text", PyDTNone());
			}
			break;
		case TVN_GETDISPINFO: break;
		case TVN_GETINFOTIP: break;
		case TVN_ITEMEXPANDED:
		case TVN_ITEMEXPANDING:
			tv = (LPNMTREEVIEW)lParam;
			ret.setItem("hitem",  PyMFCHandle(tv->itemNew.hItem));
			ret.setItem("state",  tv->itemNew.state);
			ret.setItem("lparam",  tv->itemNew.lParam);
			ret.setItem("collapse",  tv->action & TVE_COLLAPSE);
			ret.setItem("expand",  tv->action & TVE_EXPAND);
			break;
		case TVN_KEYDOWN: break;
		case TVN_SELCHANGED: 
		case TVN_SELCHANGING:
			tv = (LPNMTREEVIEW)lParam;
			ret.setItem("hitemold",  PyMFCHandle(tv->itemOld.hItem));
			ret.setItem("stateold",  tv->itemOld.state);
			ret.setItem("lparamold",  tv->itemOld.lParam);
			ret.setItem("hitemnew",  PyMFCHandle(tv->itemNew.hItem));
			ret.setItem("statenew",  tv->itemNew.state);
			ret.setItem("lparamnew",  tv->itemNew.lParam);
			
			switch (tv->action) {
			case TVC_BYKEYBOARD:
				ret.setItem("bykeyboard", 1);
				ret.setItem("bymouse",  0);
				break;
			case TVC_BYMOUSE:
				ret.setItem("bykeyboard", 0);
				ret.setItem("bymouse",  1);
				break;
			default:
				ret.setItem("bykeyboard", 0);
				ret.setItem("bymouse",  0);
				break;
			}
			break;
		case TVN_SETDISPINFO: break;
		case TVN_SINGLEEXPAND: break;

		}
	}
};

void *new_TreeView(PyObject *obj) {
	PyMFC_PROLOGUE(new_TreeCtrl);

	return static_cast<CWnd*>(new PyMFCWnd<CTreeCtrl, PyMFCTreeMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}



class PyMFCListViewMsgParser: public PyMFCMsgParser {
public:
	PyMFCListViewMsgParser(){}
protected:
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		PyMFCMsgParser::parse_notify(wnd, msg, wParam, lParam, ret);

		NMHDR *h = (LPNMHDR)lParam;

		LPNMLISTVIEW lv = (LPNMLISTVIEW)lParam;
		NMLVDISPINFO *disp;
		NMITEMACTIVATE *ia;

		switch (h->code) {
		case NM_CLICK: case NM_DBLCLK: case NM_RCLICK: case NM_RDBLCLK:
			ia = (NMITEMACTIVATE*)lParam;
			ret.setItem("item", ia->iItem);
			ret.setItem("x", ia->ptAction.x);
			ret.setItem("y", ia->ptAction.y);
			ret.setItem("alt", (ia->uKeyFlags & LVKF_ALT ? 1:0));
			ret.setItem("control", (ia->uKeyFlags & LVKF_CONTROL? 1:0));
			ret.setItem("shift", (ia->uKeyFlags & LVKF_SHIFT? 1:0));
			break;

		case LVN_BEGINLABELEDIT: 
			disp = (NMLVDISPINFO*)lParam;
			ret.setItem("item", disp->item.iItem);
			break;

		case LVN_ENDLABELEDIT: 
			disp = (NMLVDISPINFO*)lParam;
			ret.setItem("item", disp->item.iItem);
			ret.setItem("itemParam", disp->item.lParam);
			if (disp->item.pszText) {
				ret.setItem("text", disp->item.pszText);
			}
			else {
				ret.setItem("text", PyDTNone());
			}
			break;

		case LVN_KEYDOWN: 
                    break;

		case LVN_ODCACHEHINT: 
                    break;


		case LVN_ODFINDITEM: 
                    break;

		case LVN_ODSTATECHANGED: 
                    break;

		case LVN_SETDISPINFO: 
                    break;
                    
		case LVN_BEGINDRAG: 
		case LVN_BEGINRDRAG: 
		case LVN_COLUMNCLICK: 
		case LVN_DELETEALLITEMS:
		case LVN_DELETEITEM: 
		case LVN_GETDISPINFO: 
		case LVN_GETINFOTIP: 
		case LVN_HOTTRACK: 
		case LVN_INSERTITEM: 
		case LVN_ITEMACTIVATE: 
		case LVN_ITEMCHANGED:
		case LVN_ITEMCHANGING: 
		case LVN_MARQUEEBEGIN: 
			lv = (LPNMLISTVIEW)lParam;
			ret.setItem("item", lv->iItem);
			ret.setItem("itemParam", lv->lParam);
			break;
		}
	}
};

void *new_ListView(PyObject *obj) {
	PyMFC_PROLOGUE(new_ListView);

	return static_cast<CWnd*>(new PyMFCWnd<CListCtrl, PyMFCListViewMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}



void *new_ToolTip(PyObject *obj) {
	PyMFC_PROLOGUE(new_ToolTip);

	return static_cast<CWnd*>(new PyMFCWnd<CToolTipCtrl, PyMFCListViewMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}


int CToolTip_Create(void *o, void *parent, long style) {
	PyMFC_PROLOGUE(CToolTip_Create);

	ASSERT(o);
	
	int ret;
	{
		PyMFCLeavePython lp;

		CToolTipCtrl *wnd = getCWnd<CToolTipCtrl>(o);
		CWnd *parentWnd = NULL;
		if (parent) {
			parentWnd = getCWnd<CWnd>(parent);
		}
		ret = wnd->Create(parentWnd, style);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
	}
	return ret;

	PyMFC_EPILOGUE(0);
}


void *new_HotKeyCtrl(PyObject *obj) {
	PyMFC_PROLOGUE(new_HotKeyCtrl);

	return static_cast<CWnd*>(new PyMFCWnd<CHotKeyCtrl, PyMFCMsgParser>(obj));

	PyMFC_EPILOGUE(0);
}