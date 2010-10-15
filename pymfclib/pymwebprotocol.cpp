// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include <urlmon.h>

#include "pymwndbase.h"
#include "pymwnd.h"
#include "pymutils.h"

#include "passthru_app/ProtocolCF.h"
#include "passthru_app/ProtocolImpl.h"
#include "PyMFC_CustomProtocol.h"


class PyMFC_WebProtocolApp;

class PyMFC_WebProtocolSink :
	public PassthroughAPP::CInternetProtocolSinkWithSP<PyMFC_WebProtocolSink>
{
	typedef PassthroughAPP::CInternetProtocolSinkWithSP<PyMFC_WebProtocolSink> BaseClass;
public:
};

class PyMFC_WebProtocolPolicy:public PassthroughAPP::CustomSinkStartPolicy<PyMFC_WebProtocolApp, PyMFC_WebProtocolSink> {
public:
  HRESULT OnStart(LPCWSTR szUrl,
    IInternetProtocolSink *pOIProtSink, IInternetBindInfo *pOIBindInfo,
    DWORD grfPI, HANDLE_PTR dwReserved,
	IInternetProtocol* pTargetProtocol) const;

  HRESULT OnStartEx(IUri *pUri,
    IInternetProtocolSink *pOIProtSink, IInternetBindInfo *pOIBindInfo,
    DWORD grfPI, HANDLE_PTR dwReserved,
	IInternetProtocolEx* pTargetProtocol) const;

  bool callFilter(LPCWSTR url, std::wstring &newuri) const;
};

class PyMFC_WebProtocolApp:
	public PassthroughAPP::CInternetProtocol<PyMFC_WebProtocolPolicy>
{
};


class PyMFCWebProtocol {
public:
	struct TypeInstance {
		PyObject_HEAD
		PyObject *filterfunc;
		PyObject *customprotocolfunc;
	};

//	static IClassFactory *cf_http;
//	static IClassFactory *cf_https;
	static TypeInstance *webprotocol;

	typedef PyDTExtDef<PyMFCWebProtocol> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.setGC(traverse, clear);
		def.addKwdArgMethod("register", registerProtocol);
		def.addKwdArgMethod("registerCustomProtocol", registerCustomProtocol);
		def.addObjMember("filter", offsetof(TypeInstance, filterfunc));
		def.addKwdArgMethod("customprotocolfunc", customprotocolfunc);
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCWebProtocol::onInitObj");

		if (webprotocol) {
			throw PyDTExc_RuntimeError("WebProtocol instance already exists");
		}
		obj->filterfunc = NULL;
		obj->customprotocolfunc = NULL;
		webprotocol = obj;
		CPyMFC_CustomProtocol::mapfunc = &(obj->customprotocolfunc);
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int traverse(TypeInstance *obj, visitproc visit, void *arg) {
		int err = 0;
		if (obj->filterfunc) {
			err = visit(obj->filterfunc, arg);
			if (err) {
				return err;
			}
		}
		if (obj->customprotocolfunc) {
			err = visit(obj->customprotocolfunc, arg);
			if (err) {
				return err;
			}
		}
		return err;
	}

	static int clear(TypeInstance *obj) {
		if (obj->filterfunc) {
			Py_XDECREF(obj->filterfunc);
			obj->filterfunc = NULL;
		}
		if (obj->customprotocolfunc) {
			Py_XDECREF(obj->customprotocolfunc);
			obj->customprotocolfunc = NULL;
		}
		return 0;
	}

	typedef PassthroughAPP::CMetaFactory<PassthroughAPP::CComClassFactoryProtocol,
		PyMFC_WebProtocolApp> MetaFactory;

	static PyObject *registerProtocol(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE(PyMFCWebCtrl_registerProtocol)

			static char *kwlist[] = {"protocol", "http", "https", NULL};
		PyDTUnicode protocol;
		int http=0, https=0;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O|ii", kwlist, protocol.getBuf(), &http, &https)) {
			return NULL;
		}
		
		if (http == https) {
			throw PyDTExc_InvalidValue("invalid target protocol");
		}

		CComPtr<IInternetSession> spSession;
		HRESULT hr = CoInternetGetSession(0, &spSession, 0);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		CLSID dest;
		if (http) {
			dest = CLSID_HttpProtocol;
		}
		else {
			dest = CLSID_HttpSProtocol;
		}

		IClassFactory *cf;
		hr = MetaFactory::CreateInstance(dest, &cf);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		hr = spSession->RegisterNameSpace(cf, CLSID_NULL, protocol.asUnicode(), 0, 0, 0);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
			
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(0);
	}

	static PyObject *customprotocolfunc(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE(customprotocolfunc)
		static char *kwlist[] = {"protocol", NULL};
		PyDTObject f;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O", kwlist, f.getBuf())) {
			return NULL;
		}
		
		if (obj->customprotocolfunc) {
			Py_XDECREF(obj->customprotocolfunc);
			obj->customprotocolfunc = NULL;
		}

		if (f.get()) {
			f.incRef();
			obj->customprotocolfunc = f.detach();
		}
			
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(0);
	}

	static PyObject *registerCustomProtocol(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE(registerCustomProtocol)
		static char *kwlist[] = {"protocol", NULL};
		const char *s;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"s", kwlist, &s)) {
			return NULL;
		}

		CComPtr<IInternetSession> spSession;
		HRESULT hr = CoInternetGetSession(0, &spSession, 0);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		UnicodeStr protocol(s);
/*
		IClassFactory *p;
		hr = CoGetClassObject(CLSID_PyMFC_CustomProtocol, CLSCTX_INPROC_SERVER, NULL, IID_IClassFactory, (void**)&p);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
*/
		CComObject<CPyMFC_CustomProtocolFactory> *cf;
		CComObject<CPyMFC_CustomProtocolFactory>::CreateInstance(&cf);
		
		hr = spSession->RegisterNameSpace(cf, CLSID_NULL, protocol.get(), 0, 0, 0);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(0);
	}

	static EXTDEF def_webprotocol;
};

PyMFCWebProtocol::TypeInstance *PyMFCWebProtocol::webprotocol = NULL;
PyMFCWebProtocol::EXTDEF PyMFCWebProtocol::def_webprotocol;


HRESULT PyMFC_WebProtocolPolicy::OnStart(LPCWSTR szUrl,
	IInternetProtocolSink *pOIProtSink, IInternetBindInfo *pOIBindInfo,
	DWORD grfPI, HANDLE_PTR dwReserved,
	IInternetProtocol* pTargetProtocol) const {
	
	std::wstring newuri;
	if (!callFilter(szUrl, newuri)) {
		return INET_E_INVALID_URL;
	}
	if (newuri.size() && newuri != szUrl) {
		szUrl = &(newuri[0]);
	}
	return PassthroughAPP::CustomSinkStartPolicy<PyMFC_WebProtocolApp, PyMFC_WebProtocolSink>::
		OnStart(szUrl, pOIProtSink, pOIBindInfo, grfPI, dwReserved, pTargetProtocol);
}

/*
HRESULT PyMFC_WebProtocolPolicy::OnStartEx(IUri *pUri,
	IInternetProtocolSink *pOIProtSink, IInternetBindInfo *pOIBindInfo,
	DWORD grfPI, HANDLE_PTR dwReserved,
	IInternetProtocolEx* pTargetProtocol) const {

	BSTR uri;
	HRESULT hr = pUri->GetAbsoluteUri(&uri);
	if (FAILED(hr)) {
		return hr;
	}
	
	std::wstring newuri;
	bool ret = callFilter(uri, newuri);

	if (uri != newuri) {
//		pUri = CreateUri();
	}

	SysFreeString(uri);

	if (!ret) {
		return INET_E_INVALID_URL;
	}


	return PassthroughAPP::CustomSinkStartPolicy<PyMFC_WebProtocolApp, PyMFC_WebProtocolSink>::
		OnStartEx(pUri, pOIProtSink, pOIBindInfo, grfPI, dwReserved, pTargetProtocol);
}
*/
bool PyMFC_WebProtocolPolicy::callFilter(LPCWSTR url, std::wstring &newuri) const {
{
	PyMFCEnterPython e;
	if (!PyMFCWebProtocol::webprotocol) {
		return true;
	}

	if (!PyMFCWebProtocol::webprotocol->filterfunc) {
		return true;
	}

	PyDTObject f(PyMFCWebProtocol::webprotocol->filterfunc, true);
	f.incRef();
	if (!f.isTrue())
		return true;
	
	PyDTUnicode s(url);
	try {
		PyDTObject ret = f.call("O", s.get());
		if (ret.isTrue()) {
			if (ret.isUnicode()) {
				PyDTUnicode uriobj(ret);
				newuri.assign(uriobj.asUnicode());
			}
			return true;
		}
		else {
			return false;
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
		return false;
	}

}
}



void init_webprotocol(PyObject *module) {
	PyDTModule m(module, false);
	PyDTRegType(m, "_pymfclib.WebProtocol", "WebProtocol", PyMFCWebProtocol::def_webprotocol);
}


