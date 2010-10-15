/*

// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include <stdafx.h>
#include <atlbase.h>

#include "pymwndbase.h"
#include "pymutils.h"

class PyMFC_IUnknown {
public:
	struct TypeInstance {
		PyObject_HEAD
		IUnknown *obj;
	};

	typedef PyDTExtDef<PyMFC_IUnknown> EXTDEF;


	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
//		def.addMethod("getText", getText);
	}
	
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IUnknown::onInitObj");
		
		obj->obj = NULL;

		IUnknown *unk = NULL;
		char *buf = NULL;
		IUnknown *ptr = NULL;

		static char *kwlist[] = {"ptr", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|i", kwlist, &ptr)) {
			return -1;
		}

		obj->obj = ptr;
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->obj) {
			obj->obj->Release();
			obj->obj = NULL;
		}
		return 0;
	}

	static PyObject *queryInterface(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IUnknown::queryInterface");
		

		IUnknown *unk = NULL;
		char *buf = NULL;
		PyDTObject klass;


		static char *kwlist[] = {"obj", "iid", "klass", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|isi", kwlist, &unk, &buf, klass.getBuf())) {
			return NULL;
		}

		if (obj && buf) {
			IID *iid = (IID*)buf;
			IUnknown *p = NULL;
			HRESULT hr = unk->QueryInterface(*iid, (void **)&p);
			if (FAILED(hr)) {
				throw PyMFC_WIN32ERRCODE(hr);
			}
			
			PyDTObject ret = klass.call("O", PyD);
			return ret.detach();
		}
		else if (obj || buf) {
			throw PyDTExc_InvalidType("obj and iid should be specified");
		}

		return 0;
	
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *addRef(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IUnknown::addRef");

		if (obj->obj) {
			ULONG ret = obj->obj->AddRef();		
			return PyDTInt(ret).detach();
		} 
		else {
			throw PyDTExc_InvalidValue("Invalid object ptr");
		}

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *release(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IUnknown::release");
		
		if (obj->obj) {
			obj->obj->Release();		
			obj->obj = NULL;
	
			PyMFC_RETNONE();
		} 
		else {
			throw PyDTExc_InvalidValue("Invalid object ptr");
		}
		
		PyMFC_EPILOGUE(NULL);
	}

};












extern "C"
void init_oleobjs(PyObject *module) {

	PyDTModule m(module, false);
}
*/