// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMCOM_H
#define PYMCOM_H

#include "pymwin32funcs.h"

template <class T, class T_INTERFACE, REFIID T_IID=__uuidof(T_INTERFACE)>
class PyMFC_COMRef {
public:
	struct TypeInstance {
		PyObject_HEAD
		T_INTERFACE *obj;
	};

	template <class DEFTYPE>
	static void initBaseMethods(DEFTYPE &def) {
		def.addObjArgMethod("queryInterface", queryInterface);
		def.addObjArgMethod("queryFrom", queryFrom);
		def.addKwdArgMethod("createInstance", createInstance);
		def.addMethod("detach", detach);
		def.addMethod("addRef", addRef);
		def.addMethod("release", release);
		def.addGetSet("ptr", getPtr, NULL);
	}

	static void checkObj(TypeInstance *obj) {
		if (!obj->obj) {
			throw PyDTExc_InvalidValue("COM object not specified");
		}
	}


	static int initComObject(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_COMRef::initComObject");

		PyDTObject ptrObj;
		static char *kwlist[] = {"ptr", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|O", kwlist, ptrObj.getBuf())) {
			return -1;
		}
		if (ptrObj.get()) {
			obj->obj = (T_INTERFACE*)PyMFCPtr::asPtr(ptrObj.get());
		}
		else {
			obj->obj = NULL;
		}
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_COMRef::onInitObj");
		
		obj->obj = NULL;

		PyDTSequence seq(args, false);
		PyDTDict dict(kwds, false);
		
		if (seq.getSize() == 1 && dict.isNull()) {
			obj->obj = (T_INTERFACE*)PyMFCPtr::asPtr(seq.getItem(0).get());
			return 0;
		}
		else if (seq.getSize() == 0 && !dict.isNull() && dict.getSize() == 1) {
			PyDTObject ptr(dict.getItem("ptr"));
			if (!ptr.isNull()) {
				obj->obj = (T_INTERFACE*)PyMFCPtr::asPtr(seq.getItem(0).get());
				return 0;
			}
		}
		else if (seq.getSize() == 0 || dict.getSize() == 0) {
			return 0;
		}
		
		return T::initComObject(obj, args, kwds);

		PyMFC_EPILOGUE(-1);
	}

	static int commonInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_COMRef::commonInitObj");
		
		obj->obj = NULL;

		PyDTObject ptrObj;
		static char *kwlist[] = {"ptr", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|O", kwlist, ptrObj.getBuf())) {
			return -1;
		}
		if (ptrObj.get()) {
			obj->obj = (T_INTERFACE*)PyMFCPtr_AsVoidPtr(ptrObj.get());
		}
		else {
			obj->obj = NULL;
		}
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

	static PyObject *getIID(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_COMRef::getIID");

		return PyDTString((const char *)&(T_IID), sizeof(IID)).detach();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getPtr(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_COMRef::getPtr");
		return PyMFCPtr(obj->obj).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *createInstance(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_COMRef::createInstance");
		
		static char *kwlist[] = {"clsid", "unkouter", "inproc", "local", NULL};
		PyDTString clsidObj;
		PyDTObject unkouterObj;
		int inproc=0;
		int local=0;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"O|Oii", kwlist, clsidObj.getBuf(), unkouterObj.getBuf(), &inproc, &local)) {
			return NULL;
		}
		CLSID *clsid = (CLSID*)clsidObj.asString();
		IUnknown *outer = NULL;
		if (unkouterObj.get()) {
			outer = (IUnknown *)outer;
		}
		CLSCTX ctx = CLSCTX_INPROC_SERVER;
		if (local) {
			ctx = CLSCTX_LOCAL_SERVER;
		}
		
		LPVOID ppv;
		HRESULT hr = CoCreateInstance(*clsid, outer, ctx, T_IID, &ppv);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		clear(obj);
		obj->obj = (T_INTERFACE*)ppv;

		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *detach(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_COMRef::detach");
		PyDTObject ret = PyMFCPtr(obj->obj);
		obj->obj = NULL;
		return ret.detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *queryInterface(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFC_COMRef::queryInterface");

		checkObj(obj);

		PyDTString iidObj(arg, false);
		IID *iid = (IID*)iidObj.asString();
		void *p;
		HRESULT hr = obj->obj->QueryInterface(*iid, &p);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		return PyMFCPtr(p).detach();
	
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *queryFrom(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFC_COMRef::queryFrom");

		PyDTObject unk(arg, false);
		
		void *p;
		if (unk.isInt() || unk.isLong()) {
			HRESULT hr = static_cast<IUnknown *>(PyMFCPtr::asPtr(unk.get()))->QueryInterface(T_IID, &p);
			if (FAILED(hr)) {
				throw PyMFC_WIN32ERRCODE(hr);
			}
		}
		else {
			PyDTString iid(getIID(obj), true);
			p = PyMFCPtr::asPtr(unk.callMethod("queryInterface", "O", iid.get()).get());
		}
		clear(obj);
		obj->obj = (T_INTERFACE*)p;

		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *addRef(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_COMRef::addRef");

		checkObj(obj);
		ULONG ret = obj->obj->AddRef();		
		return PyDTInt(ret).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *release(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_COMRef::release");
		
		checkObj(obj);
		obj->obj->Release();		
		obj->obj = NULL;

		PyMFC_RETNONE();
		
		PyMFC_EPILOGUE(NULL);
	}
};

#endif
