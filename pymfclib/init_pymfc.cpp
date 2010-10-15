// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"

#include "pymwndbase.h"
#include "pyminit.h"
#include "pymwin32funcs.h"
#include "pymutils.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


void init_shlobj(PyObject *module);
void init_oleobjs(PyObject *module);
void init_commodule(PyObject *module);
void init_webobjs(PyObject *module);
void init_webprotocol(PyObject *module);

extern "C" {
void init_pymfclib_menu(void);
void init_pymfclib_gdi(void);
void init_pymfclib_htmlhelp(void);
void init_pymfclib_system(void);
void init_pymfclib_editor(void);
void init_pymfclib_bufsre(void);
void init_pymfclib_winhttp(void);

PYMFC_API PyObject *PyMFCPtr_FromVoidPtr(void *h);
PYMFC_API void * PyMFCPtr_AsVoidPtr(PyObject *obj);
PYMFC_API int PyMFCPtr_IsPtr(PyObject *obj);

PYMFC_API PyObject *PyMFCHandle_FromHandle(HANDLE h);
PYMFC_API HANDLE PyMFCHandle_AsHandle(PyObject *obj);
PYMFC_API int PyMFCHandle_IsHandle(PyObject *obj);

}

class PyMFCPtrObj {
public:
	struct TypeInstance {
		PyObject_HEAD
		void *ptr;
	};

	typedef PyDTExtDef<PyMFCPtrObj> EXTDEF;
	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addGetSet("ptr", getPtr, NULL);
		def.setNumberMethods(
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		isNonZero);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCPtrObj::onInitObj");
		obj->ptr= NULL;
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
	}
	static int isNonZero(TypeInstance *obj) {
		return obj->ptr!= NULL;
	}
	static PyObject *getPtr(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFCPtrObj::getHandle");
		return PyDTObject::fromVoidPtr(obj->ptr).detach();
		PyMFC_EPILOGUE(NULL);
	}
	static EXTDEF def_pymfcptr;
};

PyMFCPtrObj::EXTDEF PyMFCPtrObj::def_pymfcptr;

int PyMFCPtr_IsPtr(PyObject *obj) {
	PyMFC_PROLOGUE("PyMFCPtr_IsPtr");
	if (obj->ob_type == &PyMFCPtrObj::def_pymfcptr.getTypeObj()) {
		return 1;
	}
	else {
		return 0;
	}
	PyMFC_EPILOGUE(-1);
}



extern "C" PYMFC_API 
PyObject *PyMFCPtr_FromVoidPtr(void *ptr) {
	PyMFC_PROLOGUE("PyMFCPtr_FromVoidPtr");

	return PyMFCPtr(ptr).detach();


	PyMFC_EPILOGUE(NULL);
}


void *PyMFCPtr_AsVoidPtr(PyObject *obj) {
	PyMFC_PROLOGUE("PyMFCPtr_AsVoidPtr");
	
	if (PyMFCPtr_IsPtr(obj)) {
		PyMFCPtrObj::TypeInstance *p = (PyMFCPtrObj::TypeInstance *)obj;
		return p->ptr;
	}
/*
	else {
		PyDTObject o(obj, false);
		if (o.isInt() || o.isLong()) {
			return o.asVoidPtr();
		}
	}
*/
	throw PyDTExc_InvalidType("PyMFCPtr");

	PyMFC_EPILOGUE(NULL);
}



class PyMFCHandleObj {
public:
	struct TypeInstance {
		PyObject_HEAD
		HANDLE handle;
	};

	typedef PyDTExtDef<PyMFCHandleObj> EXTDEF;
	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addGetSet("handle", getHandle, NULL);
		def.setNumberMethods(
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		isNonZero);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCHandleObj::onInitObj");
		obj->handle = NULL;
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
	}

	static PyObject *getHandle(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFCHandleObj::getHandle");
		return PyDTObject::fromVoidPtr(obj->handle).detach();
		PyMFC_EPILOGUE(NULL);
	}

	static int isNonZero(TypeInstance *obj) {
		return obj->handle != NULL;
	}
	static EXTDEF def_pymfchandle;
};

PyMFCHandleObj::EXTDEF PyMFCHandleObj::def_pymfchandle;

int PyMFCHandle_IsHandle(PyObject *obj) {
	PyMFC_PROLOGUE("PyMFCHandle_IsHandle");
	if (obj->ob_type == &PyMFCHandleObj::def_pymfchandle.getTypeObj()) {
		return 1;
	}
	else {
		return 0;
	}
	PyMFC_EPILOGUE(-1);
}

extern "C" PYMFC_API 
PyObject *PyMFCHandle_FromHandle(HANDLE h) {
	PyMFC_PROLOGUE("PyMFCHandle_FromHandle");

	return PyMFCHandle(h).detach();

	PyMFC_EPILOGUE(NULL);
}


HANDLE PyMFCHandle_AsHandle(PyObject *obj) {
	PyMFC_PROLOGUE("PyMFCHandle_AsHandle");
	if (PyMFCHandle_IsHandle(obj)) {
		PyMFCHandleObj::TypeInstance *p = (PyMFCHandleObj::TypeInstance *)obj;
		return p->handle;
	}
	throw PyDTExc_InvalidType("PyMFCHandle");
	PyMFC_EPILOGUE(NULL);
}

PyMFCPtr::PyMFCPtr(void *p) {
	PyMFCPtrObj::TypeInstance *obj = PyMFCPtrObj::def_pymfcptr.newObject();
	if (!obj) {
		throw PyDTExc_PythonError();
	}
	obj->ptr = p;
	set((PyObject*)obj, true);
}

bool PyMFCPtr::isPtr(PyObject *p) {
	if (p->ob_type == &PyMFCPtrObj::def_pymfcptr.getTypeObj()) {
		return true;
	}
	else {
		return false;
	}
}

void *PyMFCPtr::asPtr(PyObject *obj) {
	if (isPtr(obj)) {
		PyMFCPtrObj::TypeInstance *p = (PyMFCPtrObj::TypeInstance *)obj;
		return p->ptr;
	}
	throw PyDTExc_InvalidType("PyMFCPtr");
}

PyMFCHandle::PyMFCHandle(void *p) {
	PyMFCHandleObj::TypeInstance *obj = PyMFCHandleObj::def_pymfchandle.newObject();
	if (!obj) {
		throw PyDTExc_PythonError();
	}
	obj->handle= p;
	set((PyObject*)obj, true);
}

bool PyMFCHandle::isHandle(PyObject *p) {
	if (p->ob_type == &PyMFCHandleObj::def_pymfchandle.getTypeObj()) {
		return true;
	}
	else {
		return false;
	}
}

void *PyMFCHandle::asHandle(PyObject *obj) {
	if (isHandle(obj)) {
		PyMFCHandleObj::TypeInstance *p = (PyMFCHandleObj::TypeInstance *)obj;
		return p->handle;
	}
	throw PyDTExc_InvalidType("PyMFCHandle");
}


int pymInit(PyObject *module) {
	PYMFC_AFX_DLLSTATE::init();
	PYMFC_AFX_DLLSTATE::ref_pymfclib = module;

	Py_Initialize();
	PyEval_InitThreads();

	PyDTModule m(module, false);
	PyDTRegType(m, "_pymfclib.PyMFCPtrObj", "PyMFCPtrObj", PyMFCPtrObj::def_pymfcptr);
	PyDTRegType(m, "_pymfclib.PyMFCHandleObj", "PyMFCHandleObj", PyMFCHandleObj::def_pymfchandle);

	init_pymfclib_menu();
	init_pymfclib_gdi();
	init_pymfclib_htmlhelp();
	init_pymfclib_system();
	init_pymfclib_editor();
	init_pymfclib_bufsre();
	init_pymfclib_winhttp();

	init_shlobj(module);
	init_oleobjs(module);
	init_commodule(module);
	init_webobjs(module);
	init_webprotocol(module);
	return 1;
}

PyObject *pymInitPyMFCException() {
	return PyMFCException::init();
}

PyObject *pymInitPyMFCWin32Exception() {
	return PyMFCWin32Exception::init();
}

PyObject *PyMFCWndMsgType::MSGTYPE = NULL;

PyObject *pymInitWndMsgType() {
	static PyMFCWndMsgType::EXTDEF def;

	if (!PyMFCWndMsgType::MSGTYPE) {
		def.initType("_pymfclib._wndmsg");
		PyMFCWndMsgType::MSGTYPE = (PyObject *)&def.getTypeObj();
	}
	return PyMFCWndMsgType::MSGTYPE;
}

PyObject *pymInitKeyDict() {

	PyDTDict dict;
	dict.newObj();
	
	dict.setItem("LBUTTON", VK_LBUTTON);
	dict.setItem("RBUTTON", VK_RBUTTON);
	dict.setItem("CANCEL", VK_CANCEL);
	dict.setItem("MBUTTON", VK_MBUTTON);
	dict.setItem("BACKSPACE", VK_BACK);
	dict.setItem("TAB", VK_TAB);
	dict.setItem("CLEAR", VK_CLEAR);
	dict.setItem("ENTER", VK_RETURN);
	dict.setItem("SHIFT", VK_SHIFT);
	dict.setItem("CONTROL", VK_CONTROL);
	dict.setItem("MENU", VK_MENU);
	dict.setItem("PAUSE", VK_PAUSE);
	dict.setItem("CAPITAL", VK_CAPITAL);
	dict.setItem("KANA", VK_KANA);
	dict.setItem("HANGUL", VK_HANGUL);
	dict.setItem("JUNJA", VK_JUNJA);
	dict.setItem("FINAL", VK_FINAL);
	dict.setItem("HANJA", VK_HANJA);
	dict.setItem("KANJI", VK_KANJI);
	dict.setItem("ESC", VK_ESCAPE);
	dict.setItem("CONVERT", VK_CONVERT);
	dict.setItem("NONCONVERT", VK_NONCONVERT);
	dict.setItem("ACCEPT", VK_ACCEPT);
	dict.setItem("MODECHANGE", VK_MODECHANGE);
	dict.setItem("SPACE", VK_SPACE);
	dict.setItem("PGUP", VK_PRIOR);
	dict.setItem("PGDN", VK_NEXT);
	dict.setItem("END", VK_END);
	dict.setItem("HOME", VK_HOME);
	dict.setItem("LEFT", VK_LEFT);
	dict.setItem("UP", VK_UP);
	dict.setItem("RIGHT", VK_RIGHT);
	dict.setItem("DOWN", VK_DOWN);
	dict.setItem("SELECT", VK_SELECT);
	dict.setItem("PRINT", VK_PRINT);
	dict.setItem("EXECUTE", VK_EXECUTE);
	dict.setItem("SNAPSHOT", VK_SNAPSHOT);
	dict.setItem("INSERT", VK_INSERT);
	dict.setItem("DELETE", VK_DELETE);
	dict.setItem("HELP", VK_HELP);
	dict.setItem("LWIN", VK_LWIN);
	dict.setItem("RWIN", VK_RWIN);
	dict.setItem("APPS", VK_APPS);
	dict.setItem("NUMPAD0", VK_NUMPAD0);
	dict.setItem("NUMPAD1", VK_NUMPAD1);
	dict.setItem("NUMPAD2", VK_NUMPAD2);
	dict.setItem("NUMPAD3", VK_NUMPAD3);
	dict.setItem("NUMPAD4", VK_NUMPAD4);
	dict.setItem("NUMPAD5", VK_NUMPAD5);
	dict.setItem("NUMPAD6", VK_NUMPAD6);
	dict.setItem("NUMPAD7", VK_NUMPAD7);
	dict.setItem("NUMPAD8", VK_NUMPAD8);
	dict.setItem("NUMPAD9", VK_NUMPAD9);
	dict.setItem("MULTIPLY", VK_MULTIPLY);
	dict.setItem("ADD", VK_ADD);
	dict.setItem("SEPARATOR", VK_SEPARATOR);
	dict.setItem("SUBTRACT", VK_SUBTRACT);
	dict.setItem("DECIMAL", VK_DECIMAL);
	dict.setItem("DIVIDE", VK_DIVIDE);
	dict.setItem("F1", VK_F1);
	dict.setItem("F2", VK_F2);
	dict.setItem("F3", VK_F3);
	dict.setItem("F4", VK_F4);
	dict.setItem("F5", VK_F5);
	dict.setItem("F6", VK_F6);
	dict.setItem("F7", VK_F7);
	dict.setItem("F8", VK_F8);
	dict.setItem("F9", VK_F9);
	dict.setItem("F10", VK_F10);
	dict.setItem("F11", VK_F11);
	dict.setItem("F12", VK_F12);
	dict.setItem("F13", VK_F13);
	dict.setItem("F14", VK_F14);
	dict.setItem("F15", VK_F15);
	dict.setItem("F16", VK_F16);
	dict.setItem("F17", VK_F17);
	dict.setItem("F18", VK_F18);
	dict.setItem("F19", VK_F19);
	dict.setItem("F20", VK_F20);
	dict.setItem("F21", VK_F21);
	dict.setItem("F22", VK_F22);
	dict.setItem("F23", VK_F23);
	dict.setItem("F24", VK_F24);
	dict.setItem("NUMLOCK", VK_NUMLOCK);
	dict.setItem("SCROLL", VK_SCROLL);
	dict.setItem("LSHIFT", VK_LSHIFT);
	dict.setItem("RSHIFT", VK_RSHIFT);
	dict.setItem("LCONTROL", VK_LCONTROL);
	dict.setItem("RCONTROL", VK_RCONTROL);
	dict.setItem("LMENU", VK_LMENU);
	dict.setItem("RMENU", VK_RMENU);
	dict.setItem("PROCESSKEY", VK_PROCESSKEY);
	dict.setItem("ATTN", VK_ATTN);
	dict.setItem("CRSEL", VK_CRSEL);
	dict.setItem("EXSEL", VK_EXSEL);
	dict.setItem("EREOF", VK_EREOF);
	dict.setItem("PLAY", VK_PLAY);
	dict.setItem("ZOOM", VK_ZOOM);
	dict.setItem("NONAME", VK_NONAME);
	dict.setItem("PA1", VK_PA1);
	dict.setItem("OEM_CLEAR", VK_OEM_CLEAR);
	
	return dict.detach();
}


PyObject *pymInitMessageDict() {
	PyDTDict dict;
	dict.newObj();

	dict.setItem("ACTIVATE", WM_ACTIVATE);
	dict.setItem("ACTIVATEAPP", WM_ACTIVATEAPP);
	dict.setItem("APP", WM_APP);
	dict.setItem("ASKCBFORMATNAME", WM_ASKCBFORMATNAME);
	dict.setItem("CANCELJOURNAL", WM_CANCELJOURNAL);
	dict.setItem("CANCELMODE", WM_CANCELMODE);
	dict.setItem("CAPTURECHANGED", WM_CAPTURECHANGED);
	dict.setItem("CHANGECBCHAIN", WM_CHANGECBCHAIN);
	dict.setItem("CHAR", WM_CHAR);
	dict.setItem("CHARTOITEM", WM_CHARTOITEM);
	dict.setItem("CHILDACTIVATE", WM_CHILDACTIVATE);
	dict.setItem("CLEAR", WM_CLEAR);
	dict.setItem("CLOSE", WM_CLOSE);
	dict.setItem("COMMAND", WM_COMMAND);
	dict.setItem("COMPACTING", WM_COMPACTING);
	dict.setItem("COMPAREITEM", WM_COMPAREITEM);
	dict.setItem("CONTEXTMENU", WM_CONTEXTMENU);
	dict.setItem("COPY", WM_COPY);
	dict.setItem("COPYDATA", WM_COPYDATA);
	dict.setItem("CREATE", WM_CREATE);
	dict.setItem("CTLCOLORBTN", WM_CTLCOLORBTN);
	dict.setItem("CTLCOLORDLG", WM_CTLCOLORDLG);
	dict.setItem("CTLCOLOREDIT", WM_CTLCOLOREDIT);
	dict.setItem("CTLCOLORLISTBOX", WM_CTLCOLORLISTBOX);
	dict.setItem("CTLCOLORMSGBOX", WM_CTLCOLORMSGBOX);
	dict.setItem("CTLCOLORSCROLLBAR", WM_CTLCOLORSCROLLBAR);
	dict.setItem("CTLCOLORSTATIC", WM_CTLCOLORSTATIC);
	dict.setItem("CUT", WM_CUT);
	dict.setItem("DEADCHAR", WM_DEADCHAR);
	dict.setItem("DELETEITEM", WM_DELETEITEM);
	dict.setItem("DESTROY", WM_DESTROY);
	dict.setItem("DESTROYCLIPBOARD", WM_DESTROYCLIPBOARD);
	dict.setItem("DEVICECHANGE", WM_DEVICECHANGE);
	dict.setItem("DEVMODECHANGE", WM_DEVMODECHANGE);
	dict.setItem("DISPLAYCHANGE", WM_DISPLAYCHANGE);
	dict.setItem("DRAWCLIPBOARD", WM_DRAWCLIPBOARD);
	dict.setItem("DRAWITEM", WM_DRAWITEM);
	dict.setItem("DROPFILES", WM_DROPFILES);
	dict.setItem("ENABLE", WM_ENABLE);
	dict.setItem("ENDSESSION", WM_ENDSESSION);
	dict.setItem("ENTERIDLE", WM_ENTERIDLE);
	dict.setItem("ENTERMENULOOP", WM_ENTERMENULOOP);
	dict.setItem("ENTERSIZEMOVE", WM_ENTERSIZEMOVE);
	dict.setItem("ERASEBKGND", WM_ERASEBKGND);
	dict.setItem("EXITMENULOOP", WM_EXITMENULOOP);
	dict.setItem("EXITSIZEMOVE", WM_EXITSIZEMOVE);
	dict.setItem("FONTCHANGE", WM_FONTCHANGE);
	dict.setItem("GETDLGCODE", WM_GETDLGCODE);
	dict.setItem("GETFONT", WM_GETFONT);
	dict.setItem("GETHOTKEY", WM_GETHOTKEY);
	dict.setItem("GETICON", WM_GETICON);
	dict.setItem("GETMINMAXINFO", WM_GETMINMAXINFO);
	dict.setItem("GETTEXT", WM_GETTEXT);
	dict.setItem("GETTEXTLENGTH", WM_GETTEXTLENGTH);
	dict.setItem("HANDHELDFIRST", WM_HANDHELDFIRST);
	dict.setItem("HANDHELDLAST", WM_HANDHELDLAST);
	dict.setItem("HELP", WM_HELP);
	dict.setItem("HOTKEY", WM_HOTKEY);
	dict.setItem("HSCROLL", WM_HSCROLL);
	dict.setItem("HSCROLLCLIPBOARD", WM_HSCROLLCLIPBOARD);
	dict.setItem("ICONERASEBKGND", WM_ICONERASEBKGND);
	dict.setItem("IME_CHAR", WM_IME_CHAR);
	dict.setItem("IME_COMPOSITION", WM_IME_COMPOSITION);
	dict.setItem("IME_COMPOSITIONFULL", WM_IME_COMPOSITIONFULL);
	dict.setItem("IME_CONTROL", WM_IME_CONTROL);
	dict.setItem("IME_ENDCOMPOSITION", WM_IME_ENDCOMPOSITION);
	dict.setItem("IME_KEYDOWN", WM_IME_KEYDOWN);
	dict.setItem("IME_KEYLAST", WM_IME_KEYLAST);
	dict.setItem("IME_KEYUP", WM_IME_KEYUP);
	dict.setItem("IME_NOTIFY", WM_IME_NOTIFY);
	dict.setItem("IME_SELECT", WM_IME_SELECT);
	dict.setItem("IME_SETCONTEXT", WM_IME_SETCONTEXT);
	dict.setItem("IME_STARTCOMPOSITION", WM_IME_STARTCOMPOSITION);
	dict.setItem("INITDIALOG", WM_INITDIALOG);
	dict.setItem("INITMENU", WM_INITMENU);
	dict.setItem("INITMENUPOPUP", WM_INITMENUPOPUP);
	dict.setItem("INPUTLANGCHANGE", WM_INPUTLANGCHANGE);
	dict.setItem("INPUTLANGCHANGEREQUEST", WM_INPUTLANGCHANGEREQUEST);
	dict.setItem("KEYDOWN", WM_KEYDOWN);
	dict.setItem("KEYFIRST", WM_KEYFIRST);
	dict.setItem("KEYLAST", WM_KEYLAST);
	dict.setItem("KEYUP", WM_KEYUP);
	dict.setItem("KILLFOCUS", WM_KILLFOCUS);
	dict.setItem("LBUTTONDBLCLK", WM_LBUTTONDBLCLK);
	dict.setItem("LBUTTONDOWN", WM_LBUTTONDOWN);
	dict.setItem("LBUTTONUP", WM_LBUTTONUP);
	dict.setItem("MBUTTONDBLCLK", WM_MBUTTONDBLCLK);
	dict.setItem("MBUTTONDOWN", WM_MBUTTONDOWN);
	dict.setItem("MBUTTONUP", WM_MBUTTONUP);
	dict.setItem("MDIACTIVATE", WM_MDIACTIVATE);
	dict.setItem("MDICASCADE", WM_MDICASCADE);
	dict.setItem("MDICREATE", WM_MDICREATE);
	dict.setItem("MDIDESTROY", WM_MDIDESTROY);
	dict.setItem("MDIGETACTIVE", WM_MDIGETACTIVE);
	dict.setItem("MDIICONARRANGE", WM_MDIICONARRANGE);
	dict.setItem("MDIMAXIMIZE", WM_MDIMAXIMIZE);
	dict.setItem("MDINEXT", WM_MDINEXT);
	dict.setItem("MDIREFRESHMENU", WM_MDIREFRESHMENU);
	dict.setItem("MDIRESTORE", WM_MDIRESTORE);
	dict.setItem("MDISETMENU", WM_MDISETMENU);
	dict.setItem("MDITILE", WM_MDITILE);
	dict.setItem("MEASUREITEM", WM_MEASUREITEM);
	dict.setItem("MENUCHAR", WM_MENUCHAR);
	dict.setItem("MENUSELECT", WM_MENUSELECT);
	dict.setItem("MOUSEACTIVATE", WM_MOUSEACTIVATE);
	dict.setItem("MOUSEFIRST", WM_MOUSEFIRST);
	dict.setItem("MOUSEHOVER", WM_MOUSEHOVER);
	dict.setItem("MOUSELAST", WM_MOUSELAST);
	dict.setItem("MOUSELAST", WM_MOUSELAST);
	dict.setItem("MOUSELEAVE", WM_MOUSELEAVE);
	dict.setItem("MOUSEMOVE", WM_MOUSEMOVE);
	dict.setItem("MOUSEWHEEL", WM_MOUSEWHEEL);
	dict.setItem("MOVE", WM_MOVE);
	dict.setItem("MOVING", WM_MOVING);
	dict.setItem("NCACTIVATE", WM_NCACTIVATE);
	dict.setItem("NCCALCSIZE", WM_NCCALCSIZE);
	dict.setItem("NCCREATE", WM_NCCREATE);
	dict.setItem("NCDESTROY", WM_NCDESTROY);
	dict.setItem("NCHITTEST", WM_NCHITTEST);
	dict.setItem("NCLBUTTONDBLCLK", WM_NCLBUTTONDBLCLK);
	dict.setItem("NCLBUTTONDOWN", WM_NCLBUTTONDOWN);
	dict.setItem("NCLBUTTONUP", WM_NCLBUTTONUP);
	dict.setItem("NCMBUTTONDBLCLK", WM_NCMBUTTONDBLCLK);
	dict.setItem("NCMBUTTONDOWN", WM_NCMBUTTONDOWN);
	dict.setItem("NCMBUTTONUP", WM_NCMBUTTONUP);
	dict.setItem("NCMOUSEMOVE", WM_NCMOUSEMOVE);
	dict.setItem("NCPAINT", WM_NCPAINT);
	dict.setItem("NCRBUTTONDBLCLK", WM_NCRBUTTONDBLCLK);
	dict.setItem("NCRBUTTONDOWN", WM_NCRBUTTONDOWN);
	dict.setItem("NCRBUTTONUP", WM_NCRBUTTONUP);
	dict.setItem("NEXTDLGCTL", WM_NEXTDLGCTL);
	dict.setItem("NEXTMENU", WM_NEXTMENU);
	dict.setItem("NOTIFY", WM_NOTIFY);
	dict.setItem("NOTIFYFORMAT", WM_NOTIFYFORMAT);
	dict.setItem("NULL", WM_NULL);
	dict.setItem("PAINT", WM_PAINT);
	dict.setItem("PAINTCLIPBOARD", WM_PAINTCLIPBOARD);
	dict.setItem("PAINTICON", WM_PAINTICON);
	dict.setItem("PALETTECHANGED", WM_PALETTECHANGED);
	dict.setItem("PALETTEISCHANGING", WM_PALETTEISCHANGING);
	dict.setItem("PARENTNOTIFY", WM_PARENTNOTIFY);
	dict.setItem("PASTE", WM_PASTE);
	dict.setItem("PENWINFIRST", WM_PENWINFIRST);
	dict.setItem("PENWINLAST", WM_PENWINLAST);
	dict.setItem("POWER", WM_POWER);
	dict.setItem("POWERBROADCAST", WM_POWERBROADCAST);
	dict.setItem("PRINT", WM_PRINT);
	dict.setItem("PRINTCLIENT", WM_PRINTCLIENT);
	dict.setItem("QUERYDRAGICON", WM_QUERYDRAGICON);
	dict.setItem("QUERYENDSESSION", WM_QUERYENDSESSION);
	dict.setItem("QUERYNEWPALETTE", WM_QUERYNEWPALETTE);
	dict.setItem("QUERYOPEN", WM_QUERYOPEN);
	dict.setItem("QUEUESYNC", WM_QUEUESYNC);
	dict.setItem("QUIT", WM_QUIT);
	dict.setItem("RBUTTONDBLCLK", WM_RBUTTONDBLCLK);
	dict.setItem("RBUTTONDOWN", WM_RBUTTONDOWN);
	dict.setItem("RBUTTONUP", WM_RBUTTONUP);
	dict.setItem("RENDERALLFORMATS", WM_RENDERALLFORMATS);
	dict.setItem("RENDERFORMAT", WM_RENDERFORMAT);
	dict.setItem("SETCURSOR", WM_SETCURSOR);
	dict.setItem("SETFOCUS", WM_SETFOCUS);
	dict.setItem("SETFONT", WM_SETFONT);
	dict.setItem("SETHOTKEY", WM_SETHOTKEY);
	dict.setItem("SETICON", WM_SETICON);
	dict.setItem("SETREDRAW", WM_SETREDRAW);
	dict.setItem("SETTEXT", WM_SETTEXT);
	dict.setItem("SETTINGCHANGE", WM_SETTINGCHANGE);
	dict.setItem("SHOWWINDOW", WM_SHOWWINDOW);
	dict.setItem("SIZE", WM_SIZE);
	dict.setItem("SIZECLIPBOARD", WM_SIZECLIPBOARD);
	dict.setItem("SIZING", WM_SIZING);
	dict.setItem("SPOOLERSTATUS", WM_SPOOLERSTATUS);
	dict.setItem("STYLECHANGED", WM_STYLECHANGED);
	dict.setItem("STYLECHANGING", WM_STYLECHANGING);
	dict.setItem("SYNCPAINT", WM_SYNCPAINT);
	dict.setItem("SYSCHAR", WM_SYSCHAR);
	dict.setItem("SYSCOLORCHANGE", WM_SYSCOLORCHANGE);
	dict.setItem("SYSCOMMAND", WM_SYSCOMMAND);
	dict.setItem("SYSDEADCHAR", WM_SYSDEADCHAR);
	dict.setItem("SYSKEYDOWN", WM_SYSKEYDOWN);
	dict.setItem("SYSKEYUP", WM_SYSKEYUP);
	dict.setItem("TCARD", WM_TCARD);
	dict.setItem("TIMECHANGE", WM_TIMECHANGE);
	dict.setItem("TIMER", WM_TIMER);
	dict.setItem("UNDO", WM_UNDO);
	dict.setItem("USER", WM_USER);
	dict.setItem("USERCHANGED", WM_USERCHANGED);
	dict.setItem("VKEYTOITEM", WM_VKEYTOITEM);
	dict.setItem("VSCROLL", WM_VSCROLL);
	dict.setItem("VSCROLLCLIPBOARD", WM_VSCROLLCLIPBOARD);
	dict.setItem("WINDOWPOSCHANGED", WM_WINDOWPOSCHANGED);
	dict.setItem("WINDOWPOSCHANGING", WM_WINDOWPOSCHANGING);
	dict.setItem("WININICHANGE", WM_WININICHANGE);

	dict.setItem("ONOUTOFMEMORY", pydtMakeTuple(WM_NOTIFY, NM_OUTOFMEMORY));
	dict.setItem("ONCLICK", pydtMakeTuple(WM_NOTIFY, NM_CLICK));
	dict.setItem("ONDBLCLK", pydtMakeTuple(WM_NOTIFY, NM_DBLCLK));
	dict.setItem("ONRETURN", pydtMakeTuple(WM_NOTIFY, NM_RETURN));
	dict.setItem("ONRCLICK", pydtMakeTuple(WM_NOTIFY, NM_RCLICK));
	dict.setItem("ONRDBLCLK", pydtMakeTuple(WM_NOTIFY, NM_RDBLCLK));
	dict.setItem("ONSETFOCUS", pydtMakeTuple(WM_NOTIFY, NM_SETFOCUS));
	dict.setItem("ONKILLFOCUS", pydtMakeTuple(WM_NOTIFY, NM_KILLFOCUS));
	dict.setItem("ONCUSTOMDRAW", pydtMakeTuple(WM_NOTIFY, NM_CUSTOMDRAW));
	dict.setItem("ONHOVER", pydtMakeTuple(WM_NOTIFY, NM_HOVER));
	dict.setItem("ONNCHITTEST", pydtMakeTuple(WM_NOTIFY, NM_NCHITTEST));
	dict.setItem("ONKEYDOWN", pydtMakeTuple(WM_NOTIFY, NM_KEYDOWN));
	dict.setItem("ONRELEASEDCAPTURE", pydtMakeTuple(WM_NOTIFY, NM_RELEASEDCAPTURE));
	dict.setItem("ONSETCURSOR", pydtMakeTuple(WM_NOTIFY, NM_SETCURSOR));
	dict.setItem("ONCHAR", pydtMakeTuple(WM_NOTIFY, NM_CHAR));

	return dict.detach();
}

