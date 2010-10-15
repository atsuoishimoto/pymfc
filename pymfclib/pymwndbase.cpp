// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pymfclib.h"
#include "pymwndbase.h"
#include "pymutils.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

bool PyMFCWndBase::m_ime=false;


class PyMFCDispatchMessage {
protected:
	typedef PyMFCAutoVector<PyDTObject *> MSGKEYS;

	virtual void buildMessageKeys(UINT message, WPARAM wParam, LPARAM lParam, MSGKEYS &keys) {
		keys.push_back(new PyDTInt(message));
	}

	virtual void buildMessage(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam, LRESULT ret, PyDTObject &msgobj) {
		PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
		msgobj = PyDTObject(msgtype.call("Oiii", wnd->getPyObj().get(), message, wParam, lParam));

		PyDTDict dict(((PyMFCWndMsgType::TypeInstance *)msgobj.get())->x_attr, false);
		wnd->parseMsg(message, wParam, lParam, dict);
	}

	virtual bool callHandler(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam, 
									 PyDTObject &func, LRESULT &ret, BOOL &handled) {
		

		PyDTObject msgobj;
		buildMessage(wnd, message, wParam, lParam, ret, msgobj);
		
		PyDTTuple arg(1);
		arg.setItem(0, msgobj);

		PyDTDict dict(((PyMFCWndMsgType::TypeInstance *)msgobj.get())->x_attr, false);

		dict.setItem("result", ret);
		dict.setItem("cont", 1);
		dict.setItem("handled", 1);

		PyDTObject retval(PyObject_CallObject(func.get(), arg.get()), true);


		if (!retval.get()) {
//			printf("Error at PyMFCDispatchMessage::callHandler\n");
//			func.print();
			PyErr_Print();
			return false;
		}

		try {
			ret = retval.getULong();
		}
		catch (PyDTException &) {
			PyDTString func_repr(func.repr());
			std::string err(func_repr.asString());
			err += "\nshould return None or integer";
			PyErr_SetString(PyExc_ValueError, err.c_str());
			PyErr_Print();
			return false;
		}
		
		int cont;
		try {
			cont = dict.getItem("cont").getInt();
		}
		catch (PyDTException &) {
			PyDTString func_repr(func.repr());
			std::string err(func_repr.asString());
			err += "\nmsg.cont should be None or integer";
			PyErr_SetString(PyExc_ValueError, err.c_str());
			PyErr_Print();
			return false;
		}

		try {
			handled = dict.getItem("handled").getInt() || handled;
		}
		catch (PyDTException &) {
			PyDTString func_repr(func.repr());
			std::string err(func_repr.asString());
			err += "\nmsg.handled should be None or integer";
			PyErr_SetString(PyExc_ValueError, err.c_str());
			PyErr_Print();
			return false;
		}

		wnd->encodeMsg(message, wParam, lParam, ret, dict);
		if (cont) {
			return true;
		}
		else {
			return false;
		}
	}

	virtual bool dispatch_handler(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam, 
									 MSGKEYS &keys, LRESULT &ret, BOOL &handled) {
		

		PyDTSequence targetmaps(wnd->getPyObj().callMethod("_getMsgMap", ""));
		int len = targetmaps.getSize();
		for (int i = 0; i < len; i++) {
			PyDTDict targetmap(targetmaps.getItem(i));
			for (MSGKEYS::iterator iter = keys.begin(); iter != keys.end(); iter++) {
				if (!wnd->isLocked()) {
					// Window has been destroyed
					return false;
				}
				PyDTObject func(targetmap.getItem(**iter));
				if (!func.isNull()) {
					bool cont = callHandler(wnd, message, wParam, lParam, func, ret, handled);
					if (!cont) {
						return false;
					}
				}
			}
		}
		return true;
	}

	virtual void dispatch_listener(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam, 
									 MSGKEYS &keys, LRESULT &ret) {


		if (!wnd->isLocked()) {
			// Window has been destroyed
			return;
		}
		PyDTObject msgobj;

		PyDTSequence targetmaps(wnd->getPyObj().callMethod("_getListenerMap", ""));
		int len = targetmaps.getSize();
		for (int i = 0; i < len; i++) {
			PyDTDict targetmap(targetmaps.getItem(i));
			for (MSGKEYS::iterator iter = keys.begin(); iter != keys.end(); iter++) {
				PyDTList funcs(targetmap.getItem(**iter));
				if (!funcs.isNull()) {
					int l = funcs.getSize();
					for (int i=0; i < l; i++) {
						PyDTObject func(funcs.getItem(i));
						LRESULT r = ret;
						BOOL handled = FALSE;
						callHandler(wnd, message, wParam, lParam, func, r, handled);
						if (!wnd->isLocked()) {
							// Window has been destroyed
							return;
						}
					}
				}
			}
		}
		return;
	}

public:
	virtual LRESULT dispatch(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		LRESULT ret = 0;
		
		MSGKEYS msgkeys;
		buildMessageKeys(message, wParam, lParam, msgkeys);

		BOOL handled=FALSE;
		bool cont = dispatch_handler(wnd, message, wParam, lParam, msgkeys, ret, handled);
		if (cont) {
			if (!handled) {
				ret = wnd->callDefaultMsgProc(message, wParam, lParam);
			}
			dispatch_listener(wnd, message, wParam, lParam, msgkeys, ret);
		}
		return ret;
	}
};


class PyMFCDispatchParentNotify:public PyMFCDispatchMessage {
protected:
	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam)=0;

	PyMFCWndBase *getWndFromHwnd(HWND hWnd) {
		CWnd *w = CWnd::FromHandlePermanent(hWnd);
		if (w) {
			return dynamic_cast<PyMFCWndBase *>(w);
		}
		return NULL;
	}

	PyMFCWndBase *getWndFromChildId(PyMFCWndBase *wnd, UINT childId) {
		CWnd *self = dynamic_cast<CWnd *>(wnd);
		CWnd *child = self->GetDlgItem(childId);
		if (child) {
			return dynamic_cast<PyMFCWndBase *>(child);
		}
		return NULL;
	}
public:
	virtual LRESULT dispatch(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		LRESULT ret = 0;

		
		MSGKEYS msgkeys;
		buildMessageKeys(message, wParam, lParam, msgkeys);

		PyMFCWndBase *src = getSourceWnd(wnd, message, wParam, lParam);
		
		bool cont = true;
		BOOL handled = FALSE;

		if (src) {
			cont = dispatch_handler(src, message, wParam, lParam, msgkeys, ret, handled);
		}
		if (cont) {
			cont = dispatch_handler(wnd, message, wParam, lParam, msgkeys, ret, handled);
		}
		
		if (!handled && cont) {
			ret = wnd->callDefaultMsgProc(message, wParam, lParam);
		}

		if (!wnd->isLocked()) {
			// Window has been destroyed.
			return ret;
		}

		if (cont) {
			if (src) {
				dispatch_listener(src, message, wParam, lParam, msgkeys, ret);
			}
			dispatch_listener(wnd, message, wParam, lParam, msgkeys, ret);
		}		
		return ret;
	}
};

class PyMFCDispatchWMCommand:public PyMFCDispatchParentNotify {
protected:
	virtual void buildMessageKeys(UINT message, WPARAM wParam, LPARAM lParam, MSGKEYS &keys) {
		if (lParam) {
			// from control
			int code = HIWORD(wParam);
			PyDTTuple *key  = new PyDTTuple(2);
			key->setItem(0, PyDTInt(WM_COMMAND));
			key->setItem(1, PyDTInt(code));
			keys.push_back(key);
		}


		// check function by command id
		if (HIWORD(wParam) == 0 || HIWORD(wParam) == 1) {
			PyDTTuple *key = new PyDTTuple(3);
			key->setItem(0, WM_COMMAND);
			key->setItem(1, PyDTNone());
			key->setItem(2, LOWORD(wParam));
			keys.push_back(key);
		}
		PyMFCDispatchParentNotify::buildMessageKeys(message, wParam, lParam, keys);
	}

	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		if (lParam) {
			return getWndFromHwnd((HWND)lParam);
		}
		return NULL;
	}
};

class PyMFCDispatchWMNotify:public PyMFCDispatchParentNotify {
protected:
	virtual void buildMessageKeys(UINT message, WPARAM wParam, LPARAM lParam, MSGKEYS &keys) {

		// check function by command id
		PyDTTuple *key = new PyDTTuple(2);
		key->setItem(0, PyDTInt(WM_NOTIFY));
		key->setItem(1, PyDTInt(((NMHDR *)lParam)->code));

		keys.push_back(key);

		PyMFCDispatchParentNotify::buildMessageKeys(message, wParam, lParam, keys);
	}

	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		NMHDR *h = (NMHDR *)lParam;
		return getWndFromHwnd(h->hwndFrom);
	}
};

class PyMFCDispatchWMCtlColor:public PyMFCDispatchParentNotify {
protected:
	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		return getWndFromHwnd((HWND)lParam);
	}
};

class PyMFCDispatchWMDrawItem:public PyMFCDispatchParentNotify {
protected:
	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		DRAWITEMSTRUCT *ds = (LPDRAWITEMSTRUCT)lParam;
		if (ds->CtlType != ODT_MENU) {
			return getWndFromChildId(wnd, ds->CtlID);
		}
		return NULL;
	}
};

class PyMFCDispatchWMMeasureItem:public PyMFCDispatchParentNotify {
protected:
	virtual PyMFCWndBase *getSourceWnd(PyMFCWndBase *wnd, UINT message, WPARAM wParam, LPARAM lParam) {
		MEASUREITEMSTRUCT *mi= (LPMEASUREITEMSTRUCT)lParam;
		if (mi->CtlType != ODT_MENU) {
			return getWndFromChildId(wnd, mi->CtlID);
		}
		return NULL;
	}
};


LRESULT PyMFCWndBase::dispatch_winmsg(PyMFCWndBase *wnd, UINT message, 
									  WPARAM wParam, LPARAM lParam) {

//	printf("%x/%x\n", wnd->getCWnd()->m_hWnd, message);
	LRESULT ret = 0;

	
	switch (message) {
	case WM_COMMAND:		
		ret = PyMFCDispatchWMCommand().dispatch(wnd, message, wParam, lParam);
		break;
	case WM_CTLCOLORBTN:
	case WM_CTLCOLORDLG:
	case WM_CTLCOLOREDIT:
	case WM_CTLCOLORLISTBOX:
	case WM_CTLCOLORMSGBOX:
	case WM_CTLCOLORSCROLLBAR:
	case WM_CTLCOLORSTATIC:
		ret = PyMFCDispatchWMCtlColor().dispatch(wnd, message, wParam, lParam);
		break;
	case WM_DRAWITEM:
		ret = PyMFCDispatchWMDrawItem().dispatch(wnd, message, wParam, lParam);
		break;

	case WM_MEASUREITEM:
		ret = PyMFCDispatchWMMeasureItem().dispatch(wnd, message, wParam, lParam);
		break;

	case WM_NOTIFY:
		ret = PyMFCDispatchWMNotify().dispatch(wnd, message, wParam, lParam);
		break;

	default:
		ret = PyMFCDispatchMessage().dispatch(wnd, message, wParam, lParam);
		break;
	}


#define WM_KICKIDLE         0x036A
	if (message == WM_KICKIDLE) {
		CPymfclibApp *app = dynamic_cast<CPymfclibApp *>(AfxGetApp());
//		ret = app->OnKickIdle(lParam);
		ret = app->OnIdle(lParam);
//		printf("%d\n", lParam);
	}

	if (message == WM_ENTERIDLE) {
		CPymfclibApp *app = dynamic_cast<CPymfclibApp *>(AfxGetApp());
//		ret = app->OnKickIdle(lParam);
		ret = app->OnIdle(lParam);
	}


	return ret;
}

void PyMFCWndBase::onWindowDestroyed() {
	if (m_obj.isNull()) {
		return;
	}

	try {
		m_obj.callMethod("wndReleased", "");
	}
	catch (PyDTException &err) {
		err.setError();
//		printf("Error at PyMFCWndBase::onWindowDestroyed\n");
		PyErr_Print();
	}
	{
		PyMFCEnterPython e;	// Todo:??????? Why do I get GIL here?
		unlockObj();
	}
}

static DWORD t1=0, t2=0, t3=0, nn=0;

bool PyMFCWndBase::onKeyDown(CWnd *wnd, UINT nVirtKey, UINT keyData) {

	if (m_ime
		|| nVirtKey == VK_CONTROL
		|| nVirtKey == VK_MENU
		|| nVirtKey == VK_SHIFT) {
		
		return false;
	}
	if (nVirtKey == 'Z') {
//		printf("%d %d %d %d\n", nn, t1, t2, t3);
	}
	timeBeginPeriod(1);
	DWORD t = timeGetTime();

	{
		PyMFCEnterPython ep;
		try {
			PyDTObject ret = m_obj.callMethod(
					"_onKeyTranslate", "ii", nVirtKey, keyData);
			if (!ret.get()) {
				PyErr_Print();
			}
			else {
				CWnd *cwnd = getCWnd();
				if (!cwnd->m_hWnd) {	
					// stop MFC's message handling if window has been destroyed.
					return true;
				}
				// If function returns non-null value, then continue 
				// MFC's message handling.

				try {
					return ret.getInt() == 0;
				}
				catch (PyDTException &) {
					std::string err = "_onKeyTranslate should return None or integer";
					PyErr_SetString(PyExc_ValueError, err.c_str());
					PyErr_Print();
				}
			}
			t = timeGetTime() - t;
//			printf("***** %d\n", t);
			if (t >= 15) {
				t1++;
			}
			else if (t>=10) {
				t2++;
			}
			else if (t >= 5) {
				t3++;
			}
			nn += 1;			
		    timeEndPeriod(1);
		}
		catch (PyDTException) {
			PyErr_Print();
		}
	}
	return true;

}


