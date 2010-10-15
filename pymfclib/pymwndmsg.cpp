// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "mmsystem.h"

#include "pymwndbase.h"
#include "pymutils.h"
#include "pymwin32funcs.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


//
// PyMFCWndMsgType members
//



PyTypeObject *PyMFCWndMsgType::getBaseType() {
	return NULL;
}

void PyMFCWndMsgType::initMethods(PyDTExtDef<PyMFCWndMsgType> &def) {
	def.setGC(traverse, clear);
	def.setDictOffset(offsetof(TypeInstance, x_attr));
	def.addMethod("getDict", getDict);
	def.addArgMethod("get", get);
}

int PyMFCWndMsgType::onInitObj(PyMFCWndMsgType::TypeInstance *obj, PyObject *args, PyObject *kwds) {
	PyMFC_PROLOGUE("PyMFCWndMsgType::onInitObj");
	
	PyDTObject wnd;
	DWORD msg = 0;
	WPARAM wParam = 0;
	LPARAM lParam = 0;
	
	if (!PyArg_ParseTuple(args, "|Oiii", 
			wnd.getBuf(), &msg, &wParam, &lParam))
		return -1;
	
	if (wnd.isNull()) {
		wnd = PyDTNone();
	}
	
	PyDTDict dict;
	dict.newObj();

	dict.setItem("wnd", wnd);
	dict.setItem("message", msg);
	dict.setItem("wparam", wParam);
	dict.setItem("lparam", lParam);

	obj->x_attr = dict.detach();

	return 0;

	PyMFC_EPILOGUE(-1);
}

void PyMFCWndMsgType::onDeallocObj(PyMFCWndMsgType::TypeInstance *obj) {
	PyMFC_PROLOGUE("PyMFC_WndStyleType::dealloc");

	clear(obj);

	PyMFC_VOID_EPILOGUE();
}


int PyMFCWndMsgType::traverse(PyMFCWndMsgType::TypeInstance *obj, visitproc visit, void *arg) {
	int err = 0;
	if (obj->x_attr) {
		err = visit(obj->x_attr, arg);
		if (err) {
			return err;
		}
	}
	return err;
}

int PyMFCWndMsgType::clear(PyMFCWndMsgType::TypeInstance *obj) {
	Py_XDECREF(obj->x_attr);
	obj->x_attr = NULL;
	return NULL;
}

PyDTObject PyMFCWndMsgType::getDict(PyDTObject &obj) {
	return PyDTObject(getDict((TypeInstance *)obj.get()), true);
}

PyObject *PyMFCWndMsgType::getDict(PyMFCWndMsgType::TypeInstance *obj) {
	PyMFC_PROLOGUE("PyMFCWndMsgType::onInitObj");
	
	PyDTDict ret(obj->x_attr, true);
	ret.incRef();
	return ret.detach();

	PyMFC_EPILOGUE(NULL);
}

PyObject *PyMFCWndMsgType::get(PyMFCWndMsgType::TypeInstance *obj, PyObject *args) {
	PyMFC_PROLOGUE("PyMFCWndMsgType::get");

	PyDTObject key, def;
	if (!PyArg_UnpackTuple(args, "get", 1, 2, key.getBuf(), def.getBuf())) {
		return NULL;
	}
	PyDTDict dict(obj->x_attr, false);
	PyDTObject ret = dict.getItem(key);
	if (ret.isNull()) {
		if (def.isNull()) {
			return PyDTNone().detach();
		}
		else {
			def.incRef();
			return def.detach();
		}
	}
	else {
		return ret.detach();
	}
	PyMFC_EPILOGUE(NULL);
}



static PyDTTuple buildRectTuple(const RECT &rc) {
	PyDTTuple ret(4);
	ret.setItem(0, rc.left);
	ret.setItem(1, rc.top);
	ret.setItem(2, rc.right);
	ret.setItem(3, rc.bottom);
	return ret;
}

static RECT encodeRectTuple(PyDTSequence &seq) {
	RECT rc;

	rc.left = seq.getItem(0).getInt();
	rc.top= seq.getItem(1).getInt();
	rc.right= seq.getItem(2).getInt();
	rc.bottom = seq.getItem(3).getInt();

	return rc;
}


void PyMFCMsgParser::parse(CWnd *wnd, UINT message, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {

	switch (message) {
	case WM_ACTIVATE:	
		ret.setItem("active", LOWORD(wParam) == WA_ACTIVE ? 1:0);
		ret.setItem("clickactive", LOWORD(wParam) == WA_CLICKACTIVE ? 1:0);
		ret.setItem("inactive", LOWORD(wParam) == WA_INACTIVE ? 1:0);
		ret.setItem("minimized", HIWORD(wParam) != 0 ? 1:0);
		break;
	case WM_ACTIVATEAPP:break;
	case WM_APP:	break;
	case WM_ASKCBFORMATNAME:	break;
	case WM_CANCELJOURNAL:	break;
	case WM_CANCELMODE:	break;
	case WM_CAPTURECHANGED:	break;
	case WM_CHANGECBCHAIN:	break;
	case WM_CHAR: case WM_DEADCHAR:	
		ret.setItem("repeat", lParam && 0x0000ffff);
		ret.setItem("scan", (lParam >> 16) & 0x000000ff);
		ret.setItem("extend", lParam & 0x01000000);
		ret.setItem("context", lParam & 0x20000000);
		ret.setItem("previous", lParam & 0x40000000);
		ret.setItem("transition", lParam & 0x80000000);

		{
			wchar_t u[2];
			u[0] = (wchar_t)wParam;
			u[1] = 0;
			ret.setItem("char", u);
		}	
		break;
	case WM_CHARTOITEM:	break;
	case WM_CHILDACTIVATE:	break;
	case WM_CLEAR:	break;
	case WM_CLOSE:	break;
	case WM_COMPACTING:	break;
	case WM_COMPAREITEM:	break;
	case WM_CONTEXTMENU:	break;
	case WM_COPY:	break;
	case WM_COPYDATA:	break;
	case WM_CREATE:	break;
	case WM_CTLCOLORBTN:
	case WM_CTLCOLORDLG:
	case WM_CTLCOLOREDIT:
	case WM_CTLCOLORLISTBOX:
	case WM_CTLCOLORMSGBOX:
	case WM_CTLCOLORSCROLLBAR:
	case WM_CTLCOLORSTATIC:
		{
			CWnd *w = CWnd::FromHandlePermanent((HWND)lParam);
			PyMFCWndBase *pw = NULL;
			if (w) {
				pw = dynamic_cast<PyMFCWndBase *>(w);
			}

			ret.setItem("hdc", PyMFCHandle((HDC)wParam));
			ret.setItem("hwnd", PyMFCHandle((HWND)lParam));
			if (pw) {
				ret.setItem("control", pw->getPyObj());
			}
			else {
				ret.setItem("control", PyDTNone());
			}
		}
		break;
	case WM_CUT:	break;
	case WM_DELETEITEM:	break;
	case WM_DESTROY:	break;
	case WM_DESTROYCLIPBOARD:	break;
	case WM_DEVICECHANGE:	break;
	case WM_DEVMODECHANGE:	break;
	case WM_DISPLAYCHANGE:	break;
	case WM_DRAWCLIPBOARD:	break;
	case WM_DRAWITEM:	
		{
			ret.setItem("id", wParam);
			
			DRAWITEMSTRUCT *ds = (LPDRAWITEMSTRUCT)lParam;

			ret.setItem("isbutton", ds->CtlType == ODT_BUTTON);
			ret.setItem("iscombobox", ds->CtlType == ODT_COMBOBOX);
			ret.setItem("islistbox", ds->CtlType == ODT_LISTBOX);
			ret.setItem("islistview", ds->CtlType == ODT_LISTVIEW);
			ret.setItem("ismenu", ds->CtlType == ODT_MENU);
			ret.setItem("isstatic", ds->CtlType == ODT_STATIC);
			ret.setItem("istab", ds->CtlType == ODT_TAB);

			ret.setItem("ctlid", ds->CtlID);
			ret.setItem("itemid", ds->itemID);
			ret.setItem("drawentire", ds->itemAction & ODA_DRAWENTIRE);
			ret.setItem("focus", ds->itemAction & ODA_FOCUS);
			ret.setItem("select", ds->itemAction & ODA_SELECT);

			ret.setItem("checked", ds->itemState & ODS_CHECKED);
			ret.setItem("comboboxedit", ds->itemState & ODS_COMBOBOXEDIT);
			ret.setItem("default", ds->itemState & ODS_DEFAULT);
			ret.setItem("disabled", ds->itemState & ODS_DISABLED);
			ret.setItem("itemfocused", ds->itemState & ODS_FOCUS);
			ret.setItem("grayed", ds->itemState & ODS_GRAYED);
			ret.setItem("hotlight", ds->itemState & ODS_HOTLIGHT);
			ret.setItem("inactive", ds->itemState & ODS_INACTIVE);
//			ret.setItem("noaccel", ds->itemState & ODS_NOACCEL);
//			ret.setItem("nofocusrect", ds->itemState & ODS_NOFOCUSRECT);
			ret.setItem("itemselected", ds->itemState & ODS_SELECTED);
			
			ret.setItem("hwnditem", PyMFCHandle(ds->hwndItem));
			ret.setItem("hdc", PyMFCHandle(ds->hDC));
			

			PyDTTuple rc(buildRectTuple(ds->rcItem));
			ret.setItem("rcitem", rc);
			ret.setItem("itemdata", ds->itemData);
			
			PyMFCWndBase *pw = NULL;
			if (ds->CtlType != ODT_MENU) {
				CWnd *child = wnd->GetDlgItem(ds->CtlID);
				if (child) {
					pw = dynamic_cast<PyMFCWndBase *>(child);
				}
			}

			if (pw) {
				ret.setItem("control", pw->getPyObj());
			}
			else {
				ret.setItem("control", PyDTNone());
			}
		}
		break;
	case WM_DROPFILES:	break;
	case WM_ENABLE:	break;
	case WM_ENDSESSION:	break;
	case WM_ENTERIDLE:	break;
	case WM_ENTERMENULOOP:	break;
	case WM_ENTERSIZEMOVE:	break;
	case WM_ERASEBKGND:	
		ret.setItem("hdc", PyMFCHandle((HANDLE)wParam));
		break;
	case WM_EXITMENULOOP:	break;
	case WM_EXITSIZEMOVE:	break;
	case WM_FONTCHANGE:	break;
	case WM_GETDLGCODE: 
		ret.setItem("resultcode", PYMFC_AFX_DLLSTATE::getModule().getAttr("GETDLGCODERESULT"));
		break;
	case WM_GETFONT:	break;
	case WM_GETHOTKEY:	break;
	case WM_GETICON:
		ret.setItem("big", ICON_BIG==wParam);
		ret.setItem("small", ICON_SMALL==wParam);
		ret.setItem("hicon", PyDTNone());
		break;

	case WM_GETMINMAXINFO:	break;
	case WM_GETTEXT:	break;
	case WM_GETTEXTLENGTH:	break;
	case WM_HANDHELDFIRST:	break;
	case WM_HANDHELDLAST:	break;
	case WM_HELP:
		{
			HELPINFO *hi = (HELPINFO*)lParam;
			if (hi->iContextType == HELPINFO_MENUITEM) {
				ret.setItem("menuid", hi->iCtrlId);
				ret.setItem("ctrlid", PyDTNone());
				ret.setItem("ctrl", PyDTNone());
			}
			else {
				ret.setItem("menuid", PyDTNone());
				ret.setItem("ctrlid", hi->iCtrlId);
				PyMFCWndBase *pw = NULL;
				if (hi->hItemHandle) {
					CWnd *w = CWnd::FromHandlePermanent((HWND)hi->hItemHandle);
					if (w) {
						pw = dynamic_cast<PyMFCWndBase *>(w);
					}
				}
				if (pw) {
					ret.setItem("ctrl", pw->getPyObj());
				}
				else {
					ret.setItem("ctrl", PyDTNone());
				}
			}
		}	
		break;
	case WM_HOTKEY:	
		ret.setItem("snapdesktop", wParam == IDHOT_SNAPDESKTOP ? 1:0);
		ret.setItem("snapwindow", wParam == IDHOT_SNAPWINDOW ? 1:0);
		ret.setItem("alt", LOWORD(lParam) & MOD_ALT ? 1:0);
		ret.setItem("ctrl", LOWORD(lParam) & MOD_CONTROL ? 1:0);
		ret.setItem("shift", LOWORD(lParam) & MOD_SHIFT ? 1:0);
		ret.setItem("win", LOWORD(lParam) & MOD_WIN ? 1:0);
		ret.setItem("key", HIWORD(lParam));
		break;

	case WM_HSCROLL:	
		{
			int endscroll=0, left=0, right=0, lineleft=0, lineright=0, 
				pageleft=0, pageright=0, thumbposition=0, thumbtrack=0;
			
			switch(LOWORD(wParam)) {
			case SB_ENDSCROLL:	endscroll=1; break;
			case SB_LEFT:	left=1; break;
			case SB_RIGHT:	right=1; break;
			case SB_LINELEFT:	lineleft=1; break;
			case SB_LINERIGHT:	lineright=1; break;
			case SB_PAGELEFT:	pageleft=1; break;
			case SB_PAGERIGHT:	pageright=1; break;
			case SB_THUMBPOSITION:	
				thumbposition=1; 
				ret.setItem("pos", HIWORD(wParam));
				break;
			case SB_THUMBTRACK:	
				thumbtrack=1; 
				ret.setItem("pos", HIWORD(wParam));
				break;
			default:
				break;
			}
			ret.setItem("endscroll", endscroll);
			ret.setItem("left", left);
			ret.setItem("right", right);
			ret.setItem("lineleft", lineleft);
			ret.setItem("lineright", lineright);
			ret.setItem("pageleft", pageleft);
			ret.setItem("pageright", pageright);
			ret.setItem("thumbposition", thumbposition);
			ret.setItem("thumbtrack", thumbtrack);

			ret.setItem("hwndscrollbar", PyMFCHandle((HWND)lParam));
		}	
		break;
	case WM_HSCROLLCLIPBOARD:	break;
	case WM_ICONERASEBKGND:	break;
	case WM_IME_CHAR:
		ret.setItem("repeat", lParam && 0x0000ffff);
		ret.setItem("scan", (lParam >> 16) & 0x000000ff);
		ret.setItem("extend", lParam & 0x01000000);
		ret.setItem("context", lParam & 0x20000000);
		ret.setItem("previous", lParam & 0x40000000);
		ret.setItem("transition", lParam & 0x80000000);

		{
			wchar_t u[2];
			u[0] = (wchar_t)wParam;
			u[1] = 0;
			ret.setItem("char", u);
		}	
		break;
	
	case WM_IME_COMPOSITION:	
		{
//			ret.setItem("errorstr", lParam & GCR_ERRORSTR);
//			ret.setItem("infostr", lParam & GCR_INFOSTR);
			ret.setItem("compattr", lParam & GCS_COMPATTR);
			ret.setItem("compclause", lParam & GCS_COMPCLAUSE);
			ret.setItem("compreadattr", lParam & GCS_COMPREADATTR);
			ret.setItem("compreadclause", lParam & GCS_COMPREADCLAUSE);
			ret.setItem("compreadstr", lParam & GCS_COMPREADSTR);
			ret.setItem("compstr", lParam & GCS_COMPSTR);
			ret.setItem("resultclause", lParam & GCS_RESULTCLAUSE);
			ret.setItem("resultreadclause", lParam & GCS_RESULTREADCLAUSE);
			ret.setItem("resultreadstr", lParam & GCS_RESULTREADSTR);
			ret.setItem("resultstr", lParam & GCS_RESULTSTR);
//			ret.setItem("setcursorpos", lParam & GCS_SETCURSORPOS);
//			ret.setItem("typinginfo", lParam & GCS_TYPINGINFO);

			ret.setItem("insertchar", lParam & CS_INSERTCHAR);
			ret.setItem("nomovecaret", lParam & CS_NOMOVECARET);
		}
		break;
	case WM_IME_COMPOSITIONFULL:	break;
	case WM_IME_CONTROL:	break;
	case WM_IME_ENDCOMPOSITION:	break;
	case WM_IME_KEYDOWN:	break;
	case WM_IME_KEYUP:	break;
	case WM_IME_NOTIFY:	
		{
			ret.setItem("changecandidate", wParam == IMN_CHANGECANDIDATE);
			ret.setItem("closecandidate", wParam == IMN_CLOSECANDIDATE);
			ret.setItem("closestatuswindow", wParam == IMN_CLOSESTATUSWINDOW);
			ret.setItem("guideline", wParam == IMN_GUIDELINE);
			ret.setItem("opencandidate", wParam == IMN_OPENCANDIDATE);
			ret.setItem("openstatuswindow", wParam == IMN_OPENSTATUSWINDOW);
			ret.setItem("private", wParam == IMN_PRIVATE);
			ret.setItem("setcandidatepos", wParam == IMN_SETCANDIDATEPOS);
			ret.setItem("setcompositionfont", wParam == IMN_SETCOMPOSITIONFONT);
			ret.setItem("setcompositionwindow", wParam == IMN_SETCOMPOSITIONWINDOW);
			ret.setItem("setconversionmode", wParam == IMN_SETCONVERSIONMODE);
			ret.setItem("setopenstatus", wParam == IMN_SETOPENSTATUS);
			ret.setItem("setsentencemode ", wParam == IMN_SETSENTENCEMODE );
			ret.setItem("setstatuswindowpos", wParam == IMN_SETSTATUSWINDOWPOS);
		}
		break;
	case WM_IME_SELECT:	break;
	case WM_IME_SETCONTEXT:	break;
	case WM_IME_STARTCOMPOSITION:	break;
	case WM_INITDIALOG:	break;
	case WM_INITMENU:	break;
	case WM_INITMENUPOPUP:
		ret.setItem("hmenupopup", PyMFCHandle((HMENU)wParam));
		break;

	case WM_INPUTLANGCHANGE:	break;
	case WM_INPUTLANGCHANGEREQUEST:	break;

	case WM_KEYDOWN: case WM_KEYUP:
		ret.setItem("key", wParam);
		ret.setItem("repeat", lParam && 0x0000ffff);
		ret.setItem("scan", (lParam >> 16) & 0x000000ff);
		ret.setItem("extend", lParam & 0x01000000);
		ret.setItem("context", lParam & 0x20000000);
		ret.setItem("previous", lParam & 0x40000000);
		ret.setItem("transition", lParam & 0x80000000);
		break;

	case WM_KILLFOCUS:
		ret.setItem("getfocus", PyMFCHandle((HWND)wParam));
		break;
	case WM_LBUTTONDBLCLK:
	case WM_LBUTTONDOWN:
	case WM_LBUTTONUP:
	case WM_MBUTTONDBLCLK:
	case WM_MBUTTONDOWN:
	case WM_MBUTTONUP:
	case WM_RBUTTONDBLCLK:
	case WM_RBUTTONDOWN:
	case WM_RBUTTONUP:
	case WM_MOUSEACTIVATE:
	case WM_MOUSEHOVER:
	case WM_MOUSELEAVE:
	case WM_MOUSEMOVE:
		ret.setItem("control", MK_CONTROL & wParam);
		ret.setItem("lbutton", MK_LBUTTON & wParam);
		ret.setItem("mbutton", MK_MBUTTON & wParam);
		ret.setItem("rbutton", MK_RBUTTON & wParam);
		ret.setItem("shift", MK_SHIFT & wParam);
		ret.setItem("x", (short)LOWORD(lParam));
		ret.setItem("y", (short)HIWORD(lParam));
		break;

	case WM_MOUSEWHEEL:
		ret.setItem("control", MK_CONTROL & GET_KEYSTATE_WPARAM(wParam));
		ret.setItem("lbutton", MK_LBUTTON & GET_KEYSTATE_WPARAM(wParam));
		ret.setItem("mbutton", MK_MBUTTON & GET_KEYSTATE_WPARAM(wParam));
		ret.setItem("rbutton", MK_RBUTTON & GET_KEYSTATE_WPARAM(wParam));
		ret.setItem("shift", MK_SHIFT & wParam);
		ret.setItem("delta",GET_WHEEL_DELTA_WPARAM(wParam));
		break;

	case WM_MDIACTIVATE:	break;
	case WM_MDICASCADE:	break;
	case WM_MDICREATE:	break;
	case WM_MDIDESTROY:	break;
	case WM_MDIGETACTIVE:	break;
	case WM_MDIICONARRANGE:	break;
	case WM_MDIMAXIMIZE:	break;
	case WM_MDINEXT:	break;
	case WM_MDIREFRESHMENU:	break;
	case WM_MDIRESTORE:	break;
	case WM_MDISETMENU:	break;
	case WM_MDITILE:	break;
	case WM_MEASUREITEM:
		{
			MEASUREITEMSTRUCT *mi = (LPMEASUREITEMSTRUCT)lParam;

			ret.setItem("iscombobox", mi->CtlType == ODT_COMBOBOX);
			ret.setItem("islistbox", mi->CtlType == ODT_LISTBOX);
			ret.setItem("islistview", mi->CtlType == ODT_LISTVIEW);
			ret.setItem("ismenu", mi->CtlType == ODT_MENU);

			ret.setItem("ctlid", mi->CtlID);
			ret.setItem("itemid", mi->itemID);
			
			PyDTList size(2);
			size.setItem(0, mi->itemWidth);
			size.setItem(1, mi->itemHeight);

			ret.setItem("itemsize", size);
			ret.setItem("itemdata", mi->itemData);
			
			PyMFCWndBase *pw = NULL;
			if (mi->CtlType != ODT_MENU) {
				CWnd *child = wnd->GetDlgItem(mi->CtlID);
				if (child) {
					pw = dynamic_cast<PyMFCWndBase *>(child);
				}
			}

			if (pw) {
				ret.setItem("control", pw->getPyObj());
			}
			else {
				ret.setItem("control", PyDTNone());
			}
		}
		break;

	case WM_MENUCHAR:	break;
	case WM_MENUSELECT:	break;
	case WM_MOVE:	break;
	case WM_MOVING:	break;
	case WM_NCACTIVATE:	break;
	case WM_NCCALCSIZE:
		{
			if (wParam) {
				NCCALCSIZE_PARAMS *params = (NCCALCSIZE_PARAMS *)lParam;
				PyDTTuple newrect(buildRectTuple(params->rgrc[0]));
				PyDTTuple oldrect(buildRectTuple(params->rgrc[1]));
				PyDTTuple clientrect(buildRectTuple(params->rgrc[2]));

				ret.setItem("rect", newrect);
				ret.setItem("oldrect", oldrect);
				ret.setItem("clientrect", clientrect);
			}
			else {
				RECT *rc = (RECT *)lParam;
				PyDTTuple rect(buildRectTuple(*rc));
				ret.setItem("rect", rect);
				ret.setItem("oldrect", PyDTNone());
				ret.setItem("clientrect", PyDTNone());
			}
		}
		break;
	case WM_NCCREATE:	break;
	case WM_NCDESTROY:	break;
	case WM_NCHITTEST:
		{
			ret.setItem("x", LOWORD(lParam));
			ret.setItem("y", HIWORD(lParam));
		}
	
	break;
	case WM_NCLBUTTONDBLCLK:	break;
	case WM_NCLBUTTONDOWN:	break;
	case WM_NCLBUTTONUP:	break;
	case WM_NCMBUTTONDBLCLK:	break;
	case WM_NCMBUTTONDOWN:	break;
	case WM_NCMBUTTONUP:	break;
	case WM_NCMOUSEMOVE:	break;
	case WM_NCPAINT:	break;
	case WM_NCRBUTTONDBLCLK:	break;
	case WM_NCRBUTTONDOWN:	break;
	case WM_NCRBUTTONUP:	break;
	case WM_NEXTDLGCTL:	break;
	case WM_NEXTMENU:	break;
	case WM_NOTIFYFORMAT:	break;
	case WM_NULL:	break;
	case WM_PAINT:	break;
	case WM_PAINTCLIPBOARD:	break;
	case WM_PAINTICON:	break;
	case WM_PALETTECHANGED:	break;
	case WM_PALETTEISCHANGING:	break;
	case WM_PARENTNOTIFY:
		{
			WORD msg = LOWORD(wParam);
			if (msg == WM_CREATE) {
				CWnd *w = CWnd::FromHandlePermanent((HWND)lParam);
				PyMFCWndBase *pw = NULL;
				if (w) {
					pw = dynamic_cast<PyMFCWndBase *>(w);
				}
				ret.setItem("created", PyMFCHandle((HWND)lParam));
				if (pw) {
					ret.setItem("control", pw->getPyObj());
				}
				else {
					ret.setItem("control", PyDTNone());
				}
			}
			else if (msg == WM_DESTROY) {
				CWnd *w = CWnd::FromHandlePermanent((HWND)lParam);
				PyMFCWndBase *pw = NULL;
				if (w) {
					pw = dynamic_cast<PyMFCWndBase *>(w);
				}
				ret.setItem("destroyed", PyMFCHandle((HWND)lParam));
				if (pw) {
					ret.setItem("control", pw->getPyObj());
				}
				else {
					ret.setItem("control", PyDTNone());
				}
			}
			else if (msg == WM_LBUTTONDOWN) {
				ret.setItem("lbuttondown", pydtMakeTuple(LOWORD(lParam), HIWORD(lParam)));
			}
			else if (msg == WM_MBUTTONDOWN) {
				ret.setItem("mbuttondown", pydtMakeTuple(LOWORD(lParam), HIWORD(lParam)));
			}
			else if (msg == WM_RBUTTONDOWN) {
				ret.setItem("rbuttondown", pydtMakeTuple(LOWORD(lParam), HIWORD(lParam)));
			}
			else if (msg == WM_XBUTTONDOWN) {
				ret.setItem("xbuttondown", pydtMakeTuple(LOWORD(lParam), HIWORD(lParam)));
			}
		}
		break;

	case WM_PASTE:	break;
	case WM_POWER:	break;
	case WM_POWERBROADCAST:	break;
	case WM_PRINT:	break;
	case WM_PRINTCLIENT:	break;
	case WM_QUERYDRAGICON:	break;
	case WM_QUERYENDSESSION:	break;
	case WM_QUERYNEWPALETTE:	break;
	case WM_QUERYOPEN:	break;
	case WM_QUEUESYNC:	break;
	case WM_QUIT:	break;
	case WM_RENDERALLFORMATS:	break;
	case WM_RENDERFORMAT:	break;
	case WM_SETCURSOR:
		{
			UINT ht = LOWORD(lParam);
			ret.setItem("htborder", ht == HTBORDER);
			ret.setItem("htbottom", ht == HTBOTTOM);
			ret.setItem("htbottomleft", ht == HTBOTTOMLEFT);
			ret.setItem("htbottomright", ht == HTBOTTOMRIGHT);
			ret.setItem("htcaption", ht == HTCAPTION);
			ret.setItem("htclient", ht == HTCLIENT);
			ret.setItem("hterror", ht == HTERROR);
			ret.setItem("htgrowbox", ht == HTGROWBOX);
			ret.setItem("hthscroll", ht == HTHSCROLL);
			ret.setItem("htleft", ht == HTLEFT);
			ret.setItem("htmaxbutton", ht == HTMAXBUTTON);
			ret.setItem("htmenu", ht == HTMENU);
			ret.setItem("htminbutton", ht == HTMINBUTTON);
			ret.setItem("htnowhere", ht == HTNOWHERE);
			ret.setItem("htreduce", ht == HTREDUCE);
			ret.setItem("htright", ht == HTRIGHT);
			ret.setItem("htsize", ht == HTSIZE);
			ret.setItem("htsysmenu", ht == HTSYSMENU);
			ret.setItem("httop", ht == HTTOP);
			ret.setItem("httopleft", ht == HTTOPLEFT);
			ret.setItem("httopright", ht == HTTOPRIGHT);
			ret.setItem("httransparent", ht == HTTRANSPARENT);
		}
		break;
	
	case WM_SETFOCUS:
		ret.setItem("losefocus", PyMFCHandle((HWND)wParam));
		break;
	case WM_SETFONT:
		ret.setItem("hfont", PyMFCHandle((HFONT)wParam));
		ret.setItem("redraw", lParam);
		break;
	case WM_SETHOTKEY:	break;
	case WM_SETICON:	break;
	case WM_SETREDRAW:	break;
	case WM_SETTEXT:	break;
	case WM_SHOWWINDOW:	break;
	case WM_SIZE:	
		ret.setItem("maxhide", wParam == SIZE_MAXHIDE);
		ret.setItem("maximized", wParam == SIZE_MAXIMIZED);
		ret.setItem("maxshow", wParam == SIZE_MAXSHOW);
		ret.setItem("minimized", wParam == SIZE_MINIMIZED);
		ret.setItem("restored", wParam == SIZE_RESTORED);
		ret.setItem("width", LOWORD(lParam));
		ret.setItem("height", HIWORD(lParam));
		break;
	case WM_SIZECLIPBOARD:	break;
	case WM_SIZING:	break;
	case WM_SPOOLERSTATUS:	break;
	case WM_STYLECHANGED:	break;
	case WM_STYLECHANGING:	break;
	case WM_SYNCPAINT:	break;
	case WM_SYSCHAR:	break;
	case WM_SYSCOLORCHANGE:	break;
	case WM_SYSCOMMAND:	break;
	case WM_SYSDEADCHAR: case WM_SYSKEYDOWN: case WM_SYSKEYUP:
		ret.setItem("key", wParam);
		ret.setItem("repeat", lParam && 0x0000ffff);
		ret.setItem("scan", (lParam >> 16) & 0x000000ff);
		ret.setItem("extend", lParam & 0x01000000);
		ret.setItem("context", lParam & 0x20000000);
		ret.setItem("previous", lParam & 0x40000000);
		ret.setItem("transition", lParam & 0x80000000);
		break;
	case WM_TCARD:	break;
	case WM_TIMECHANGE:	break;
	case WM_TIMER:	
		ret.setItem("timerId", wParam);
		break;
	case WM_UNDO:	break;
	case WM_USER:	break;
	case WM_USERCHANGED:	break;
	case WM_VKEYTOITEM:	break;
	case WM_VSCROLL:
		{
			int bottom=0, endscroll=0, linedown=0, lineup=0, pageup=0, 
				pagedown=0, thumbtrack=0, thumbposition=0, top=0;

			switch (LOWORD(wParam)) {
			case SB_BOTTOM:		bottom=1;break;
			case SB_ENDSCROLL:	endscroll=1;break;
			case SB_LINEDOWN:	linedown=1;break;
			case SB_LINEUP:		lineup=1;break;
			case SB_PAGEUP:		pageup=1;break;
			case SB_PAGEDOWN:	pagedown=1;break;
			case SB_THUMBPOSITION: 
				thumbposition=1;
				ret.setItem("pos", HIWORD(wParam));
				break;
			case SB_THUMBTRACK:	
				thumbtrack=1; 
				ret.setItem("pos", HIWORD(wParam));
				break;
			case SB_TOP:		top=1; break;
			default:
				break;
			}
			ret.setItem("bottom", bottom);
			ret.setItem("endscroll", endscroll);
			ret.setItem("linedown", linedown);
			ret.setItem("lineup", lineup);
			ret.setItem("pageup", pageup);
			ret.setItem("pagedown", pagedown);
			ret.setItem("thumbtrack", thumbtrack);
			ret.setItem("thumbposition", thumbposition);
			ret.setItem("top", top);

			ret.setItem("hwndscrollbar", PyMFCHandle((HWND)lParam));
		}		
		break;
	case WM_VSCROLLCLIPBOARD:	break;
	case WM_WINDOWPOSCHANGED: case WM_WINDOWPOSCHANGING:
		{
			WINDOWPOS *pos = (WINDOWPOS*)lParam;
			ret.setItem("x", pos->x);
			ret.setItem("y", pos->y);
			ret.setItem("cx", pos->cx);
			ret.setItem("cy", pos->cy);
			
		}
		break;

	case WM_WININICHANGE:	break;

	case WM_COMMAND:
		parse_command(wnd, message, wParam, lParam, ret); 
		break;
	case WM_NOTIFY:
		parse_notify(wnd, message, wParam, lParam, ret); 
		break;
	}
}

void PyMFCMsgParser::parse_command(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
	ret.setItem("notifycode", HIWORD(wParam));
	ret.setItem("id", LOWORD(wParam));
	ret.setItem("hwndctrl", PyMFCHandle((HWND)lParam));

}

void PyMFCMsgParser::parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
	NMHDR *h = (LPNMHDR)lParam;
	ret.setItem("hwndfrom", PyMFCHandle(h->hwndFrom));
	ret.setItem("idfrom",  h->idFrom);
	ret.setItem("code",  h->code);
}

void PyMFCMsgParser::encodeMsg(CWnd *wnd, UINT message, WPARAM wParam, LPARAM lParam, LRESULT result, PyDTDict &msgdict) {
	switch (message) {
	case WM_NCCALCSIZE:
			if (wParam) {
				PyDTSequence newrect(msgdict.getItem("rect"));
				PyDTSequence oldrect(msgdict.getItem("oldrect"));
				PyDTSequence clientrect(msgdict.getItem("clientrect"));

				NCCALCSIZE_PARAMS *params = (NCCALCSIZE_PARAMS *)lParam;
				params->rgrc[0] = encodeRectTuple(newrect);
				params->rgrc[1] = encodeRectTuple(oldrect);
				params->rgrc[2] = encodeRectTuple(clientrect);
			}
			else {
				RECT *rc = (RECT *)lParam;
				PyDTSequence rect(msgdict.getItem("rect"));
				*rc = encodeRectTuple(rect);
			}
			break;
	
	case WM_MEASUREITEM:
		if (result) {
			PyDTSequence size(msgdict.getItem("itemsize"));
			MEASUREITEMSTRUCT *mi = (LPMEASUREITEMSTRUCT)lParam;
			mi->itemWidth = size.getItem(0).getInt();
			mi->itemHeight = size.getItem(1).getInt();
		}
		break;
	}
}
