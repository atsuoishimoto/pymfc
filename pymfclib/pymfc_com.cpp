// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include <atlbase.h>
#include <vector>

#include "pymwndbase.h"
#include "pymutils.h"
#include "pymcom.h"
#include "pymwin32funcs.h"

class PyMFC_IUnknownRef:public PyMFC_COMRef<PyMFC_IUnknownRef, IUnknown> {
public:

	typedef PyDTExtDef<PyMFC_IUnknownRef> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		initBaseMethods(def);
	}

	static EXTDEF def_iunknown;
};

PyMFC_IUnknownRef::EXTDEF PyMFC_IUnknownRef::def_iunknown;

class PyMFC_IStreamRef:public PyMFC_COMRef<PyMFC_IStreamRef, IStream> {
public:
	typedef PyDTExtDef<PyMFC_IStreamRef> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		initBaseMethods(def);
		def.addMethod("clone", clone);
		def.addKwdArgMethod("read", read);
		def.addKwdArgMethod("write", write);
		def.addKwdArgMethod("seek", seek);
	}

	static int initComObject(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IStreamRef::initComObject");

		PyDTString buf;
		static char *kwlist[] = {"buf", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O", kwlist, buf.getBuf())) {
			return -1;
		}
		buf.check();

		DWORD len = buf.size();
		HGLOBAL hGlobal = GlobalAlloc(GMEM_SHARE, len);
		if (!hGlobal) {
			throw PyMFC_WIN32ERR();
		}
		const char *p = buf.asString();
		char *s = (char *)GlobalLock(hGlobal);
		memcpy(s, p, len);
		GlobalUnlock(hGlobal);

		LPSTREAM stream;
		HRESULT hr = CreateStreamOnHGlobal(hGlobal, TRUE, &stream);
		if (FAILED(hr)) {
			GlobalFree(hGlobal);
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		ULARGE_INTEGER ulen = {len, 0};
		hr = stream->SetSize(ulen);			
		
		if (FAILED(hr)) {
			stream->Release();
			throw PyMFC_WIN32ERRCODE(hr);
		}
		obj->obj = stream;
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static PyObject *read(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IStreamRef::read");
			
		checkObj(obj);

		ULONG size;
		static char *kwlist[] = {"size",  NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"i", kwlist, &size)) {
			return NULL;
		}
		
		std::vector<char> buf;
		buf.resize(size);
		
		ULONG read;
		HRESULT hr = obj->obj->Read(&(*buf.begin()), size, &read);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		return PyDTString(&(*buf.begin()), read).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *write(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IStreamRef::write");
			
		checkObj(obj);

		PyDTString buf;
		static char *kwlist[] = {"buf",  NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O", kwlist, buf.getBuf())) {
			return NULL;
		}
		
		ULONG written;
		HRESULT hr = obj->obj->Write(buf.asString(), buf.size(), &written);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		return PyDTInt(written).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *seek(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IStreamRef::seek");
			
		checkObj(obj);

		int offset;
		int whence = 0;

		static char *kwlist[] = {"offset", "whence", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"i|i", kwlist, &offset, &whence)) {
			return NULL;
		}
		
		DWORD origin=0;
		switch (whence) {
		case 0:
			origin = STREAM_SEEK_SET;
			break;
		case 1:
			origin = STREAM_SEEK_CUR;
			break;
		case 2:
			origin = STREAM_SEEK_END;
			break;
		}

		LARGE_INTEGER li = {offset, 0};
		ULARGE_INTEGER pos;
		HRESULT hr = obj->obj->Seek(li, origin, &pos);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		return PyDTInt(pos.LowPart).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *clone(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IStreamRef::clone");
			
		checkObj(obj);

		IStream *p;
		HRESULT hr = obj->obj->Clone(&p);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		try {
			PyDTObject ret = PyDTType(obj->ob_type).call("O", PyMFCPtr(p).get());
			return ret.detach();
		}
		catch (...) {
			p->Release();
			throw;
		}

		PyMFC_EPILOGUE(NULL);
	}

	static EXTDEF def_istream;
};


PyMFC_IStreamRef::EXTDEF PyMFC_IStreamRef::def_istream;


class PyMFC_IPersistFileRef:public PyMFC_COMRef<PyMFC_IPersistFileRef, IPersistFile> {
public:
	typedef PyDTExtDef<PyMFC_IPersistFileRef> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		initBaseMethods(def);
		def.addMethod("isDirty", isDirty);
		def.addKwdArgMethod("load", load);
		def.addKwdArgMethod("save", save);
		def.addMethod("getCurFile", getCurFile);
	}

	static PyObject *isDirty(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IPersistFileRef::isDirty");
			
		checkObj(obj);

		if (SUCCEEDED(obj->obj->IsDirty())) {
			return PyDTTrue().detach();
		}
		else {
			return PyDTFalse().detach();
		}
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *load(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IPersistFileRef::load");
			
		checkObj(obj);

		static char *kwlist[] = {"filename", NULL};
		wchar_t *filename;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"u", kwlist, &filename)) {
			return NULL;
		}
		
		HRESULT hr = obj->obj->Load(filename, STGM_READ);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *save(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IPersistFileRef::save");
			
		checkObj(obj);

		static char *kwlist[] = {"filename", "remember", NULL};
		char *filename=NULL;
		int remember=0;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|si", kwlist, &filename, &remember)) {
			return NULL;
		}
		
		UnicodeStr fname(filename);
		HRESULT hr = obj->obj->Save(fname.get(), remember);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getCurFile(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IPersistFileRef::getCurFile");

		checkObj(obj);

		LPOLESTR curfile;
		HRESULT hr = obj->obj->GetCurFile(&curfile);
		
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		PyDTUnicode ret(curfile);

		IMalloc* pMalloc;
		hr = SHGetMalloc(&pMalloc); 
		
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		pMalloc->Free(curfile);
		pMalloc->Release();
		return ret.detach();

		PyMFC_EPILOGUE(NULL);
	}


	static EXTDEF def_ipersistfile;
};

PyMFC_IPersistFileRef::EXTDEF PyMFC_IPersistFileRef::def_ipersistfile;


class PyMFC_IPictureRef:public PyMFC_COMRef<PyMFC_IPictureRef, IPicture> {
public:
	typedef PyDTExtDef<PyMFC_IPictureRef> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		initBaseMethods(def);
		def.addMethod("getDC", getdc);
		def.addKwdArgMethod("render", render);
		def.addKwdArgMethod("saveAsFile", saveAsFile);
		def.addGetSet("width", getWidth, NULL);
		def.addGetSet("height", getHeight, NULL);
	}

	static int initComObject(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::initComObject");

		PyDTObject filename, icon;
		static char *kwlist[] = {"filename", "icon", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|OO", kwlist, filename.getBuf(), icon.getBuf())) {
			return -1;
		}
		
		if (!filename.isNull()) {
			bstr_t fname;
			if (filename.isUnicode()) {
				fname = PyDTUnicode(filename).asUnicode();
			}
			else if (filename.isString()) {
				fname = PyDTString(filename).asString();
			}
			else {
				throw PyDTExc_InvalidValue("Invalid filename value");
			}

			IPicture *p;
			HRESULT hr = OleLoadPicturePath(fname, NULL, NULL, 0, IID_IPicture, (void**)&p);
			if (FAILED(hr)) {
				throw PyMFC_WIN32ERRCODE(hr);
			}

			obj->obj = p;
		}
		else if (!icon.isNull()) {
			PICTDESC pd;
			memset(&pd, 0, sizeof(pd));
			pd.cbSizeofstruct = sizeof(pd);
			pd.picType =  PICTYPE_ICON;

			pd.icon.hicon = (HICON)PyMFCHandle::asHandle(icon.callMethod("getHandle", "").get());

			IPicture *p;
			HRESULT hr = OleCreatePictureIndirect(&pd, IID_IPicture, FALSE, (VOID**)&p);
			if (FAILED(hr)) {
				throw PyMFC_WIN32ERRCODE(hr);
			}
			obj->obj = p;
		}
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	
	static PyObject *render(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::render");
		
		PyDTObject dc;
		PyDTSequence destrc, srcrc;

    	static char *kwlist[] = {"dc", "destrc", "srcrc", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"OOO", kwlist, dc.getBuf(), destrc.getBuf(), srcrc.getBuf())) {
			return NULL;
		}
		
		destrc.check();
		srcrc.check();

		HDC hdc = (HDC)PyMFCHandle::asHandle(dc.callMethod("getHandle", "").get());
		
		long x = destrc.getItem(0).getInt();
		long y = destrc.getItem(1).getInt();
		long cx = abs(destrc.getItem(2).getInt() - x);
		long cy = abs(destrc.getItem(3).getInt() - y);
		OLE_XPOS_HIMETRIC xSrc = srcrc.getItem(0).getInt();
		OLE_YPOS_HIMETRIC ySrc = srcrc.getItem(1).getInt();
		OLE_XSIZE_HIMETRIC cxSrc = abs(srcrc.getItem(2).getInt() - xSrc);
		OLE_YSIZE_HIMETRIC cySrc = abs(srcrc.getItem(3).getInt() - ySrc);

		HRESULT hr = obj->obj->Render(hdc, x, y, cx, cy, xSrc, ySrc, cxSrc, cySrc, NULL);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *saveAsFile(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::saveAsFile");
		
		
		PyDTObject stream;
		int savememcopy = 0;

    	static char *kwlist[] = {"stream", "savememcopy", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"O|i", kwlist, stream.getBuf(), &savememcopy)) {
			return NULL;
		}
		
		stream.check();

		PyDTObject ptr = stream.getAttr("ptr");
		IStream *istream = (IStream *)PyMFCPtr::asPtr(ptr.get());
		LONG size=100000;

		HRESULT hr = obj->obj->SaveAsFile(istream, savememcopy, &size);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		return PyDTLong(size).detach();


		PyMFC_EPILOGUE(NULL);
	}

	
	
	static PyObject *getdc(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::getdc");

		HDC hdc;
		HRESULT hr = obj->obj->get_CurDC(&hdc);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		LONG size=0;
		hr = obj->obj->get_Width(&size);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		PyDTObject dctype(PYMFC_AFX_DLLSTATE::getModule().getAttr("DC"));
		PyDTObject handle = PyMFCPtr(hdc);
		return dctype.call("O", handle.get()).detach();
		
		PyMFC_EPILOGUE(NULL);
	}
	
	static PyObject *getWidth(TypeInstance *obj, void*) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::getWidth");
		
		LONG w;
		HRESULT hr = obj->obj->get_Width(&w);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		return PyDTInt(w).detach();
		
		PyMFC_EPILOGUE(NULL);
	}
	
	static PyObject *getHeight(TypeInstance *obj, void*) {
		PyMFC_PROLOGUE("PyMFC_IPictureRef::getHeight");
		
		LONG h;
		HRESULT hr = obj->obj->get_Height(&h);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		return PyDTInt(h).detach();
		
		PyMFC_EPILOGUE(NULL);
	}
	static EXTDEF def_ipicture;
};

PyMFC_IPictureRef::EXTDEF PyMFC_IPictureRef::def_ipicture;

static
PyDTString iid2pystr(const IID &iid) {
	return PyDTString((const char *)(&iid), sizeof(IID));
}

static
void registerIId(PyDTObject &module) {
	
#define regiid(NAME) module.setAttr(#NAME, iid2pystr(NAME))

	regiid(IID_IUnknown);
	regiid(IID_IStream);

#undef regiid
}


static
void registerClsId(PyDTObject &module) {
	
#define regclsid(NAME) module.setAttr(#NAME, iid2pystr(NAME))

	regclsid(CLSID_ShellLink);
	regclsid(CLSID_InternetShortcut);
#undef regclsid
}



void init_commodule(PyObject *module) {

	PyDTModule m(module, false);
	
	PyDTModule iids(PyDTModule::create("_pymfclib_iid", ""));
	registerIId(iids);

	m.add("IID", iids);
	
	PyDTModule clsids(PyDTModule::create("_pymfclib_clsid", ""));
	registerClsId(clsids);

	m.add("CLSID", clsids);
	
	PyDTRegType(m, "_pymfclib.IUnknown", "IUnknown", PyMFC_IUnknownRef::def_iunknown);
	PyDTRegType(m, "_pymfclib.IStream", "IStream", PyMFC_IStreamRef::def_istream);
	PyDTRegType(m, "_pymfclib.IPersistFile", "IPersistFile", PyMFC_IPersistFileRef::def_ipersistfile);
	PyDTRegType(m, "_pymfclib.IPicture", "IPicture", PyMFC_IPictureRef::def_ipicture);
}
