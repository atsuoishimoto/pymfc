// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMFCDEFS_H
#define PYMFCDEFS_H


#ifdef PYMFCDLL
#define PYMFC_API __declspec(dllexport)
#else
#define PYMFC_API __declspec(dllimport)
#endif



#ifdef __cplusplus

#include "pydt.h"

#define PYMFC_MODULENAME "_pymfclib"



class PYMFC_API PYMFC_AFX_DLLSTATE {
public:
	static AFX_MODULE_STATE* state;
	static PyObject *ref_pymfclib;
	static CRITICAL_SECTION delWndCS;
	static std::vector<CWnd *> delWnds;

	static void init() {
		ASSERT(!state);
		InitializeCriticalSection(&delWndCS);
		state = AfxGetStaticModuleState();
	}
	static AFX_MODULE_STATE* get() {
		ASSERT(state);
		return state;
	}
	static PyDTModule getModule() {
		return PyDTModule(ref_pymfclib, false);
	}
	static void RegisterDeleteWnd(CWnd *wnd) {
		EnterCriticalSection(&delWndCS);
		try {
			delWnds.push_back(wnd);
		}
		catch (...) {
			LeaveCriticalSection(&delWndCS);
			throw;
		}
		LeaveCriticalSection(&delWndCS);
	}

	static void DeleteSuspendedWnd() {
		EnterCriticalSection(&delWndCS);
		try {
			if (delWnds.size()) {
				std::vector<CWnd *>::iterator iter;
				for (iter = delWnds.begin(); iter < delWnds.end(); iter++) {
					delete *iter;
				}
				delWnds.clear();
			}
		}
		catch (...) {
			LeaveCriticalSection(&delWndCS);
			throw;
		}
		LeaveCriticalSection(&delWndCS);
	}

};


class PYMFC_API PyMFCException:public PyDTException {
public:
	PyMFCException(const char *err):PyDTException(m_errobj, err) {
		ASSERT(m_errobj);
	}
	
	static PyObject *init() {
		m_errobj = PyErr_NewException("pymfc.PyMFCException", NULL, NULL);
		if (m_errobj == NULL)
			return NULL;
		Py_INCREF(m_errobj);
		return m_errobj;
	}
	static PyObject *m_errobj;
};

class PYMFC_API PyMFCWin32Exception:public PyDTExc_Win32Err {
public:
	PyMFCWin32Exception(LPCSTR file=NULL, DWORD line=0, PyObject *exc=NULL, HRESULT code=0)
			:PyDTExc_Win32Err(file, line, exc) {

		ASSERT(m_errobj);
	}

	PyMFCWin32Exception(DWORD err, LPCSTR file=NULL, DWORD line=0, PyObject *exc=NULL)
			:PyDTExc_Win32Err(err, file, line, exc) {
		ASSERT(m_errobj);
	}

	static PyObject *init() {
		m_errobj = PyErr_NewException("pymfc.Win32Exception", PyMFCException::m_errobj, NULL);
		if (m_errobj == NULL)
			return NULL;
		Py_INCREF(m_errobj);
		return m_errobj;
	}
	static PyObject *m_errobj;
};

#define PyMFC_WIN32ERR() PyMFCWin32Exception(__FILE__, __LINE__, PyMFCWin32Exception::m_errobj)
#define PyMFC_WIN32ERRCODE(code) PyMFCWin32Exception(code, __FILE__, __LINE__, PyMFCWin32Exception::m_errobj)
#define PyMFC_RETNONE() {Py_INCREF(Py_None); return Py_None;}


class PyMFCCallTrace
{
public:
	PyMFCCallTrace(const TCHAR *s)
		:m_s(s)
	{
		TRACE("enter-%s\n", s);
	}
	~PyMFCCallTrace()
	{
		TRACE("exit-%s\n", (const TCHAR *)m_s);
	}
	CString m_s;
};

#ifndef PyMFCSHOWCALLTRACE
#	define PyMFCSHOWCALLTRACE 0
#endif

#if PyMFCSHOWCALLTRACE
#	define PyMFC_CallTrace(X) PyMFCCallTrace __pppp(X)
#else
#	define PyMFC_CallTrace(X)
#endif


#ifdef _WINDLL
#	define PyMFC_PROLOGUE(FUNC) \
		AFX_MANAGE_STATE(PYMFC_AFX_DLLSTATE::get());\
		PyMFC_CallTrace(FUNC); \
		try {
#else
#	define PyMFC_PROLOGUE(FUNC) \
		PyMFC_CallTrace(FUNC);\
		try {
#endif

// I know most stl containers don't raise std::bad_alloc, but ...
#define PyMFC_EPILOGUE(ERROR_VAL) \
 	} \
	catch (PyDTException &err) {\
		err.setError(); \
		return ERROR_VAL;\
	}\
	catch (CMemoryException *e) {\
		e->Delete();\
		PyErr_NoMemory(); \
		return ERROR_VAL;\
	}\
	catch (std::bad_alloc &) {\
		PyErr_NoMemory(); \
		return ERROR_VAL;\
	}

#define PyMFC_VOID_EPILOGUE() \
 	} \
	catch (PyDTException &err) {\
		err.setError(); \
		return;\
	}\
	catch (CMemoryException *e) {\
		e->Delete();\
		PyErr_NoMemory(); \
		return;\
	}\
	catch (std::bad_alloc &) {\
		PyErr_NoMemory(); \
		return;\
	}



class PyMFCLeavePython
{
public:
	PyMFCLeavePython() {
		m_save = PyEval_SaveThread();
	}
	~PyMFCLeavePython() {
		PyEval_RestoreThread(m_save);
	}
	PyThreadState *m_save;
};

class PyMFCEnterPython {
public:
	PyMFCEnterPython() {
		m_save = PyGILState_Ensure();
	}
	~PyMFCEnterPython() {
		PyGILState_Release(m_save);
	}
private:
	PyGILState_STATE m_save;
};


#endif // __cplusplus



#endif
