// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef _PYMWNDBASE_H
#define _PYMWNDBASE_H

#include "pymfcdefs.h"
#include "pydt.h"

//*****************************************************
// PyMFCWndBase:
//     Base class for all Window objects. Provides
//     communication between Window and Python object.
//*****************************************************

class PYMFC_API PyMFCWndBase {
public:
	PyMFCWndBase()
		:m_lockObj(false), m_tempWnd(false), m_threadId(GetCurrentThreadId()) {
	}
	void init(PyObject *obj) {
		m_obj.set(obj, false);
	}
	virtual ~PyMFCWndBase(){
	}
	
	CWnd *getCWnd() {
		return dynamic_cast<CWnd *>(this);
	}

	// todo: should return const PyDTObject &
	PyDTObject &getPyObj() {
		return m_obj;
	}

	void lockObj() {
		if (!m_lockObj) {
			m_obj.incRef(true);
			m_lockObj = true;
		}
	}

	void unlockObj() {
		if (m_lockObj) {
			m_obj.free();
			m_lockObj = false;
		}
	}
	bool isLocked() {
		return m_lockObj;
	}

	void setTemp(bool f) {
		m_tempWnd = f;
	}
	bool isTemp() {
		return m_tempWnd;
	}

	virtual void onWindowDestroyed();

	virtual BOOL createWindow(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu)=0;

	virtual LRESULT callDefaultMsgProc(UINT message, WPARAM wParam, LPARAM lParam, 
		LRESULT ret=0)=0;

	DWORD m_threadId;
	virtual void parseMsg(UINT message, WPARAM wParam, LPARAM lParam, PyDTDict &ret)=0;
	virtual void encodeMsg(UINT message, WPARAM wParam, LPARAM lParam, LRESULT lresult, PyDTDict &ret)=0;
protected:
	virtual LRESULT dispatch_winmsg(PyMFCWndBase *wnd, 
		UINT message, WPARAM wParam, LPARAM lParam);
/*
	virtual bool dispatch_winmsg(PyMFCWndBase *wnd, 
		UINT message, WPARAM wParam, LPARAM lParam, LRESULT &ret);
	virtual void listen_winmsg(PyMFCWndBase *wnd, 
		UINT message, WPARAM wParam, LPARAM lParam, LRESULT ret);
	virtual void call_listener(PyMFCWndBase *wnd, PyMFCWndBase *target, PyDTDict &map, 
		PyDTObject &msgkey, UINT message, WPARAM wParam, LPARAM lParam, LRESULT ret);

*/	


protected:
/*	
	PyDTObject buildMsgKey(UINT message, WPARAM wParam, LPARAM lParam);

	void callHandler(PyMFCWndBase *wnd, PyDTObject &func, 
		UINT message, WPARAM wParam, LPARAM lParam, LRESULT &ret);
	virtual void parseMsg(UINT message, WPARAM wParam, LPARAM lParam, PyDTDict &ret)=0;
	virtual void set_result(UINT message, WPARAM wParam, LPARAM lParam, LRESULT result, 
		PyDTDict &msgdict)=0;
*/
protected:
	PyDTObject m_obj;	// Stores Python object corresponding to this window.
	bool m_lockObj;
	static bool m_ime;
	bool m_tempWnd;
protected:
	struct KeyValue {
		bool alt;
		bool ctrl;
		bool shift;
		char key;
		bool ascii;
	};
	typedef std::vector<KeyValue> KEYVALUELIST;
	KEYVALUELIST m_curKey;
	bool onKeyDown(CWnd *wnd, UINT nVirtKey, UINT keyData);
};

inline
PyMFCWndBase *getWndBase(void *obj) {
	if (!obj) {
		throw PyMFCException("NULL CWnd");
	}
	
	PyMFCWndBase *ret = dynamic_cast<PyMFCWndBase *>((CWnd*)obj);
	if (!ret) {
		throw PyMFCException("Invalid CWnd");
	}
	return ret;
}


template <class T> inline
T *getCWnd(void *obj) {
	CWnd *w = getWndBase(obj)->getCWnd();
	T *ret = dynamic_cast<T*>(w);
	if (!ret) {
		throw PyMFCException("Invalid CWnd");
	}
	return ret;
}




//*****************************************************
// PyMFCWnd<T, P>:
//     Template class to inject PyMFCWndBase class into
//     existing MFC classes.
//     ex:
//        class PyMFCEdit:public PyMFCWnd<CEdit, PyMFCMsgParser> {
//        }
//*****************************************************
template <class T, class P>
class PyMFCWnd:public T, public PyMFCWndBase {
public:
	PyMFCWnd(PyObject *obj):T() {
		init(obj);
	}
	virtual ~PyMFCWnd() {
	}

	virtual int createWindow(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {


		return CWnd::CreateEx(dwExStyle, lpszClassName, 
				lpszWindowName, dwStyle, x, y, nWidth, 
				nHeight, hwndParent, nIDorHMenu);

	}

	virtual void parseMsg(UINT message, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		m_msgParser.parse(this, message, wParam, lParam, ret);
	}
	virtual void encodeMsg(UINT message, WPARAM wParam, LPARAM lParam, LRESULT lresult, PyDTDict &ret) {
		m_msgParser.encodeMsg(this, message, wParam, lParam, lresult, ret);
	}

/*
	int callCreate(DWORD dwExStyle, LPCTSTR lpszClassName, 
		LPCTSTR lpszWindowName, DWORD dwStyle, int x, int y, int nWidth, 
		int nHeight, HWND hwndParent, HMENU nIDorHMenu) {


		return T::CreateEx(dwExStyle, lpszClassName, 
				lpszWindowName, dwStyle, x, y, nWidth, 
				nHeight, hwndParent, nIDorHMenu);

	}
*/

	BOOL PreTranslateMessage(MSG* pMsg) {
		if (pMsg->hwnd == m_hWnd) {
			if (pMsg->message == WM_KEYDOWN 
				|| pMsg->message == WM_SYSKEYDOWN) {
				
				if (onKeyDown(this, pMsg->wParam, pMsg->lParam)) {
					return TRUE;
				}
			}
		}
		return T::PreTranslateMessage(pMsg);
	}

	LRESULT WindowProc(UINT message, WPARAM wParam, LPARAM lParam) {
		// Ignore MFC private messages
		if ((message >= 0x0360 && message <= 0x037F && message != 0x036A) // Ignore MFC private messages but WM_KICKIDLE
			|| (message == 0x0118)        // Ignore WM_SYSTIMER
			|| (message == WM_USER+3174))  // ?
			return T::WindowProc(message, wParam, lParam);

		if (message == WM_NCCREATE) {
			PyMFCEnterPython e;
			lockObj();	// Object shouldn't be destructed until window are destroyed.
		}

		if (message == WM_IME_STARTCOMPOSITION) {
			m_ime = true;
		}
		else if (message == WM_IME_ENDCOMPOSITION) {
			m_ime = false;
		}

		LRESULT ret=0;
		{
			PyMFCEnterPython e;
			PyDTObject wobj(m_obj);	// ensure Window is not destructed.

			try {
				ret = dispatch_winmsg(this, message, wParam, lParam);
			}
			catch (PyDTException &exc) {
//				const char *s = exc.m_err.c_str();
//				printf("*** Uncaught exception: %s\n", s);
				exc.setError();
				PyErr_Print();

			}

			if (message == WM_NCDESTROY) {
				onWindowDestroyed();
			}
		}
		return ret;
	}

	virtual LRESULT callDefaultMsgProc(UINT message, WPARAM wParam, 
						LPARAM lParam, LRESULT ret) {
		if (!m_hWnd) {
			return 0;
		}

		{
			PyMFCLeavePython lp;
			ret = T::WindowProc(message, wParam, lParam);
		}
		return ret;
	}
/*
	virtual void parseMsg(UINT message, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
		m_msgParser.parse(this, message, wParam, lParam, ret);
	}
	virtual void set_result(UINT message, WPARAM wParam, LPARAM lParam, LRESULT result, PyDTDict &msgdict) {
		m_msgParser.set_result(message, wParam, lParam, result, msgdict);
	}
*/
	P m_msgParser;
};

//*****************************************************
//*  WndMsg
//*****************************************************

class PYMFC_API PyMFCWndMsgType {
public:
	struct TypeInstance {
		PyObject_HEAD
		PyObject *x_attr;
	};
	
	typedef PyDTExtDef<PyMFCWndMsgType> EXTDEF;

	static PyTypeObject *getBaseType();
	static void initMethods(PyMFCWndMsgType::EXTDEF &def);
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds);
	static void onDeallocObj(TypeInstance *obj);

	static int traverse(TypeInstance *obj, visitproc visit, void *arg);
	static int clear(TypeInstance *obj);

	static PyDTObject getDict(PyDTObject &obj);
	static PyObject *getDict(TypeInstance *obj);
	static PyObject *get(TypeInstance *obj, PyObject *args);

	static PyObject *MSGTYPE;
};


//*****************************************************
// PyMFCMsgParser:
//     Parse window message and build dictionary.
//*****************************************************
class PYMFC_API PyMFCMsgParser {
public:
	virtual void parse(CWnd *wnd, UINT message, WPARAM wParam, LPARAM lParam, 
		PyDTDict &ret);
	virtual void encodeMsg(CWnd *wnd, UINT message, WPARAM wParam, LPARAM lParam, LRESULT lresult, PyDTDict &ret);
//	virtual void set_result(UINT message, WPARAM wParam, LPARAM lParam, LRESULT result, 
//		PyDTDict &msgdict);
protected:
	virtual void parse_command(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, 
		PyDTDict &ret);
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, 
		PyDTDict &ret);
};

#endif
