// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include <atlbase.h>

#include "pymwndbase.h"
#include "pymutils.h"
#include "pymwin32funcs.h"
#include <intshcut.h>

class PyMFCDropEffect:public PyDTFlagType<PyMFCDropEffect, DROPEFFECT_NONE> {
public:
	static void initFlags(EXTDEF &def) {
		addValueDef(def, "none", DROPEFFECT_NONE);
		addFlagDef(def, "copy", DROPEFFECT_COPY);
		addFlagDef(def, "move", DROPEFFECT_MOVE);
		addFlagDef(def, "link", DROPEFFECT_LINK);
		addFlagDef(def, "scroll", DROPEFFECT_SCROLL);
	}
	static EXTDEF def_dropeffect;
};

PyMFCDropEffect::EXTDEF PyMFCDropEffect::def_dropeffect;


class PyMFCFileDescriptor {
public:
	struct TypeInstance {
		PyObject_HEAD
		FILEDESCRIPTOR desc;
	};

	typedef PyDTExtDef<PyMFCFileDescriptor> EXTDEF;
	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addGetSet("filename", getFilename, NULL);
		def.addGetSet("filesize", getFilesize, NULL);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCFileDescriptor::onInitObj");
		
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		return 0;
	}
	
	static PyObject *getFilename(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFCFileDescriptor::getFilename");
		
		return PyDTUnicode(obj->desc.cFileName).detach();
		
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getFilesize(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFCFileDescriptor::getFilesize");
		
		LONGLONG size = Int32x32To64(obj->desc.nFileSizeHigh, obj->desc.nFileSizeLow);
		return PyDTLong(size).detach();
		
		PyMFC_EPILOGUE(NULL);
	}

	static EXTDEF def_filedescriptor;
};

PyMFCFileDescriptor::EXTDEF PyMFCFileDescriptor::def_filedescriptor;


class PyMFCStgMedium {
public:
	struct TypeInstance {
		PyObject_HEAD
		STGMEDIUM *medium;
	};

	typedef PyDTExtDef<PyMFCStgMedium> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addMethod("getText", getText);
		def.addMethod("getUnicode", getUnicode);
		def.addMethod("getHDrop", getHDrop);
		def.addMethod("getFileDescriptor", getFileDescriptor);
		def.addObjArgMethod("getData", getData);
	}
	
	static HGLOBAL newTextGMem(const char *buf, long size) {
		HGLOBAL ret = GlobalAlloc(GMEM_SHARE, size+1);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		char *s = (char *)GlobalLock(ret);
		memcpy(s, buf, size);
		s[size] = 0;
		GlobalUnlock(ret);
		return ret;
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCStgMedium::onInitObj");
		
		char *buf=NULL;
		long buflen=0;
		char *filename=NULL;
		PyDTObject unk;

		static char *kwlist[] = {"buf", "filename", "unk", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|s#sO", kwlist, &buf, &buflen, &filename, unk.getBuf())) {
			return -1;
		}


		obj->medium = new STGMEDIUM;
		memset(obj->medium, 0, sizeof(STGMEDIUM));

		if (buf) {
			obj->medium->tymed = TYMED_HGLOBAL;
			obj->medium->hGlobal = newTextGMem(buf, buflen);
		}
		else if (filename) {
			obj->medium->tymed = TYMED_HGLOBAL;
			obj->medium->hGlobal = newTextGMem(buf, buflen);
		}
		
		if (!unk.isNull()) {
			obj->medium->pUnkForRelease = (IUnknown*)PyMFCPtr::asPtr(unk.get());
		}

		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->medium) {
			ReleaseStgMedium(obj->medium);
			delete obj->medium;
			obj->medium = NULL;
		}
		return 0;
	}

	static STGMEDIUM *detach(TypeInstance *obj) {
		STGMEDIUM *ret = obj->medium;
		obj->medium = NULL;
		return ret;
	}

	static PyObject *getText(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCStgMedium::getText");

		if (obj->medium->tymed == TYMED_HGLOBAL) {
			HGlobalPtr<char> p(obj->medium->hGlobal, true);
			if (!p.get()) {
				throw PyMFC_WIN32ERR();
			}
			size_t size = p.getSize();
			for (size_t i=0; i < size; i++) {
				if (p.get()[i] ==0) {
					size = i;
					break;
				}
			}
			return PyDTString(p.get(), size).detach();
		}
		else {
			throw PyDTExc_InvalidType("getText::Unsupported media type");
		}
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getUnicode(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCStgMedium::getUnicode");

		if (obj->medium->tymed == TYMED_HGLOBAL) {

			HGlobalPtr<wchar_t> p(obj->medium->hGlobal, true);
			if (!p.get()) {
				throw PyMFC_WIN32ERR();
			}
			size_t size = p.getSize() / sizeof(wchar_t);
			for (size_t i=0; i < size; i++) {
				if (p.get()[i] ==0) {
					size = i;
					break;
				}
			}
			return PyDTUnicode(p.get(), size).detach();
		}
		else {
			throw PyDTExc_InvalidType("getText::Unsupported media type");
		}
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getHDrop(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCStgMedium::getHDrop");
		
		if (obj->medium->tymed == TYMED_HGLOBAL) {
			HGlobalPtr<DROPFILES> p(obj->medium->hGlobal, false);
			
			PyDTList ret(0);
			if (!p->fWide) {
				// ANSI
				char *filename = (char *)p.get() + p->pFiles;
				while (*(filename) != 0) {
					UnicodeStr f(filename);
					ret.append(f.get());
					filename += strlen(filename);
				}
			}
			else {
				// UNICODE
				wchar_t *filename = (wchar_t*)((char *)p.get() + p->pFiles);
				while (*(filename) != 0) {
					ret.append(filename);
					filename += wcslen(filename)+1;
				}
			}
			return ret.detach();
		}
		else {
			throw PyDTExc_InvalidType("getHDrop::Unsupported media type");
		}
		PyMFC_EPILOGUE(NULL);
	}
	
	static PyObject *getFileDescriptor(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCStgMedium::getFileDescriptor");
		if (obj->medium->tymed == TYMED_HGLOBAL) {
			HGlobalPtr<FILEGROUPDESCRIPTOR> p(obj->medium->hGlobal, true);
			
			PyDTTuple ret(p->cItems);
			for (UINT n = 0; n < p->cItems; n++) {
				PyDTObject descobj(PyMFCFileDescriptor::def_filedescriptor.getDTTypeObj().call(""));
				PyMFCFileDescriptor::TypeInstance *desc = (PyMFCFileDescriptor::TypeInstance*)descobj.get();
				desc->desc = p->fgd[n];
				ret.setItem(n, descobj);
			}
			return ret.detach();
		}
		else {
			throw PyDTExc_InvalidType("getFileDescriptor::Unsupported media type");
		}
		PyMFC_EPILOGUE(NULL);

	}

	static PyObject *getData(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFCStgMedium::getData");

		PyDTObject cfobj(arg, false);
		int cf = cfobj.getInt();

		switch (cf) {
		case CF_TEXT:
			return getText(obj);
		
		case CF_UNICODETEXT:
			return getUnicode(obj);
		
		case CF_HDROP:
			return getHDrop(obj);
		}
		
		if (cf == RegisterClipboardFormat(CFSTR_SHELLURL)) {
			return getText(obj);
		}
		if (cf == RegisterClipboardFormat(CFSTR_INETURLW)) {
			return getUnicode(obj);
		}
		if (cf == RegisterClipboardFormat(CFSTR_FILEDESCRIPTORW)) {
			return getFileDescriptor(obj);
		}


		throw PyDTExc_InvalidValue("Unsupported clip format");

		PyMFC_EPILOGUE(NULL);
	}
	
	static EXTDEF def_stgmedium;
};

PyMFCStgMedium::EXTDEF PyMFCStgMedium::def_stgmedium;


class PyMFCFormatEtc {
public:
	struct TypeInstance {
		PyObject_HEAD
		FORMATETC formatetc;
	};

	typedef PyDTExtDef<PyMFCFormatEtc> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addIntMember("clipformat", offsetof(TypeInstance, formatetc.cfFormat), true);	
		def.addIntMember("lindex", offsetof(TypeInstance, formatetc.lindex), false);	
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onInitObj");
		
		PyDTObject format;
		PyDTObject stgmedium;

		long content=0, thumbnail=0, icon=0, docprint=0, index=-1;
		long tymed=0, hglobal=0, file=0, istream=0, istorage=0, gdi=0, mfpict=0, enhmf=0;

		static char *kwlist[] = {"stgmedium", "format", 
			"content", "thumbnail", "icon", "docprint", "lindex", 
			"tymed", "hglobal", "file", "istream", "istorage", "gdi", 
			"mfpict", "enhmf", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|OOiiiiiiiiiiiii", kwlist, stgmedium.getBuf(), format.getBuf(), &content, &thumbnail, &icon, &docprint, 
			&index, &tymed, &hglobal, &file, &istream, &istorage, &gdi, &mfpict, &enhmf)) {
			return -1;
		}

		memset(&obj->formatetc, 0, sizeof(obj->formatetc));
		obj->formatetc.dwAspect = DVASPECT_CONTENT;
		obj->formatetc.lindex = index;
		obj->formatetc.tymed = -1;
		

		if (!format.isNull()) {
			obj->formatetc.cfFormat = (CLIPFORMAT)format.getInt();	
		}

		if (content) {
			obj->formatetc.dwAspect |= DVASPECT_CONTENT;
		}
		else if (thumbnail) {
			obj->formatetc.dwAspect |= DVASPECT_THUMBNAIL;
		}
		else if (icon) {
			obj->formatetc.dwAspect |= DVASPECT_ICON;
		}
		else if (docprint) {
			obj->formatetc.dwAspect |= DVASPECT_DOCPRINT;
		}
		else {
			obj->formatetc.dwAspect |= DVASPECT_CONTENT;
		}

		if (!stgmedium.isNull()) {
			if (!stgmedium.isInstance(PyMFCStgMedium::def_stgmedium.getTypeObj())) {
				throw PyDTException(PyExc_TypeError, "invalid stgmedium type");
			}
			
			obj->formatetc.tymed = ((PyMFCStgMedium::TypeInstance *)stgmedium.get())->medium->tymed;
		}
		
		if (hglobal) {
			obj->formatetc.tymed |= TYMED_HGLOBAL;
		}
		else if (file) {
			obj->formatetc.tymed |= TYMED_FILE;
		}
		else if (istream) {
			obj->formatetc.tymed |= TYMED_ISTREAM;
		}
		else if (istorage) {
			obj->formatetc.tymed |= TYMED_ISTORAGE;
		}
		else if (gdi) {
			obj->formatetc.tymed |= TYMED_GDI;
		}
		else if (mfpict) {
			obj->formatetc.tymed |= TYMED_MFPICT;
		}
		else if (enhmf) {
			obj->formatetc.tymed |= TYMED_ENHMF;
		}

		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		return 0;
	}
	static EXTDEF def_formatetc;
};

PyMFCFormatEtc::EXTDEF PyMFCFormatEtc::def_formatetc;


class CPyMFCOleDataSource:public COleDataSource {
public:	
	bool DoDragDrop(DROPEFFECT &ret, DWORD dwEffects, UINT dragMinDist, UINT dragDelay);
};


class CPyMFCOleDropSource:public COleDropSource {
public:
// Nasty Hacks!
	CRect &getStartRect() {
		return m_rectStartDrag;
	}
	UINT &getDragDelay() {
		return nDragDelay;
	}
	SCODE GiveFeedback(DROPEFFECT dropEffect) {
		return COleDropSource::GiveFeedback(dropEffect);
	}

};

bool CPyMFCOleDataSource::DoDragDrop(DROPEFFECT &ret, DWORD dwEffects, UINT dragMinDist, UINT dragDelay)
{

	CPyMFCOleDropSource dropSource;

	CPoint ptCursor;
	GetCursorPos(&ptCursor);
	dropSource.getStartRect().SetRect(
		ptCursor.x, ptCursor.y, ptCursor.x, ptCursor.y);

	
	const TCHAR szWindows[] = _T("windows");
	const TCHAR szDragMinDist[] = _T("DragMinDist");
	const TCHAR szDragDelay[] = _T("DragDelay");

	if (!dragMinDist) {	
		dragMinDist = GetProfileInt(szWindows, szDragMinDist, DD_DEFDRAGMINDIST);
	}

	dropSource.getStartRect().InflateRect(dragMinDist , dragMinDist);

	if (!dragDelay) {
		dragDelay = GetProfileInt(szWindows, szDragDelay, DD_DEFDRAGDELAY);
	}
	dropSource.getDragDelay() = dragDelay;
	
	ASSERT_VALID(AfxGetMainWnd());
	if (!dropSource.OnBeginDrag(AfxGetMainWnd())) {
		ret = 0;
		return false;
	}
	
	// call global OLE api to do the drag drop
	LPDATAOBJECT lpDataObject = (LPDATAOBJECT)GetInterface(&IID_IDataObject);
	LPDROPSOURCE lpDropSource =
		(LPDROPSOURCE)dropSource.GetInterface(&IID_IDropSource);
	DWORD dwResultEffect = DROPEFFECT_NONE;
	::DoDragDrop(lpDataObject, lpDropSource, dwEffects, &dwResultEffect);

	ret = dwResultEffect;
	return true;
}



class PyMFCOleDataSource {
public:
	struct TypeInstance {
		PyObject_HEAD
		CPyMFCOleDataSource *datasrc;
	};

	typedef PyDTExtDef<PyMFCOleDataSource> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addKwdArgMethod("cacheData", cacheData);
		def.addKwdArgMethod("doDragDrop", doDragDrop);
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::onInitObj");
		
		obj->datasrc = new CPyMFCOleDataSource();
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->datasrc) {
			delete obj->datasrc;
			obj->datasrc = NULL;
		}
		return 0;
	}

	static PyObject *cacheData(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::cacheData");
		
	
		PyDTObject medium, formatetc;
		
		static char *kwlist[] = {"medium", "formatetc", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"OO", kwlist, medium.getBuf(), formatetc.getBuf()))
			return NULL;


		if (!medium.isInstance(PyMFCStgMedium::def_stgmedium.getTypeObj())) {
			throw PyDTException(PyExc_TypeError, "invalid stgmedium type");
		}

		if (!formatetc.isInstance(PyMFCFormatEtc::def_formatetc.getTypeObj())) {
			throw PyDTException(PyExc_TypeError, "invalid formatetc type");
		}


		PyMFCStgMedium::TypeInstance *o = (PyMFCStgMedium::TypeInstance *)medium.get();
		STGMEDIUM *stg = PyMFCStgMedium::detach(o);
		FORMATETC *fmt = &(((PyMFCFormatEtc::TypeInstance*)formatetc.get())->formatetc);
		
		// todo: possible resource leak?
		obj->datasrc->CacheData(fmt->cfFormat, stg, fmt);

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *doDragDrop(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::doDragDrop");

		
		static char *kwlist[] = {"effect", "mindist", "delay", NULL};

		PyDTObject effect;
		int mindist=0, dragdelay=0;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|Oii", kwlist, effect.getBuf(), &mindist, &dragdelay))
			return NULL;

		DROPEFFECT f;
		if (effect.isNull()) {
			f = DROPEFFECT_COPY;
		}
		else {
			f =effect.getAttr("value").getInt();
		}

		DROPEFFECT de;
		bool ret;
		{
			PyMFCLeavePython lp;
			ret = obj->datasrc->DoDragDrop(de, f, mindist, dragdelay);
		}
		if (ret) {
			PyDTObject result = PyMFCDropEffect::def_dropeffect.getDTTypeObj().call("");
			result.setAttr("value", ret);

			return result.detach();
		}
		else {
			PyMFC_RETNONE();
		}
		PyMFC_EPILOGUE(NULL);
	}
	static EXTDEF def_oledatasrc;
};

PyMFCOleDataSource::EXTDEF PyMFCOleDataSource::def_oledatasrc;


class PyMFCOleDataObject {
public:
	struct TypeInstance {
		PyObject_HEAD
		COleDataObject *dataobj;
	};

	typedef PyDTExtDef<PyMFCOleDataObject> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addObjArgMethod("isDataAvailable", isDataAvailable);
		def.addObjArgMethod("getData", getData);
		def.addObjArgMethod("getMedium", getMedium);
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::onInitObj");
		
		obj->dataobj = new COleDataObject();
		
		PyDTObject idataobj;
		BOOL release=FALSE;

		static char *kwlist[] = {"dataobj", "release", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"|Oi", kwlist, idataobj.getBuf(), &release)) {
			return -1;
		}
		
		if (idataobj.get()) {
			obj->dataobj->Attach((IDataObject*)PyMFCPtr::asPtr(idataobj.get()), release);
		}
		
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->dataobj) {
			delete obj->dataobj;
			obj->dataobj = NULL;
		}
		return 0;
	}

	static FORMATETC _buildFormatEtc(PyDTObject &fmtval) {
		FORMATETC fmt;
		if (fmtval.isInstance(PyMFCFormatEtc::def_formatetc.getTypeObj())) {
			fmt= ((PyMFCFormatEtc::TypeInstance*)fmtval.get())->formatetc;
		}
		else {
			memset(&fmt, 0, sizeof(fmt));
			fmt.cfFormat = (CLIPFORMAT)fmtval.getInt();
			fmt.dwAspect = DVASPECT_CONTENT;
			fmt.lindex = -1;
			fmt.tymed = -1;
		}
		return fmt;
	}

	static PyObject *isDataAvailable(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::isDataAvailable");

		PyDTObject format(arg, false);

		FORMATETC fmt = _buildFormatEtc(format);
		
		SCODE ret = obj->dataobj->m_lpDataObject->QueryGetData(&fmt);
		if (ret == S_OK) {
			return PyDTInt(1).detach();
		}

		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyDTObject _getStgMedium(IDataObject *obj, FORMATETC &fmt) {

		PyDTObject stgmobj(PyMFCStgMedium::def_stgmedium.getDTTypeObj().call(""));
		PyMFCStgMedium::TypeInstance *stgm = (PyMFCStgMedium::TypeInstance*)stgmobj.get();

		SCODE result = obj->GetData(&fmt, stgm->medium);
		if (FAILED(result)) {
			throw PyMFC_WIN32ERRCODE(result);
		}
		return stgmobj;
	}

	static PyObject *getData(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::getData");

		PyDTObject format(arg, false);

		FORMATETC fmt = _buildFormatEtc(format);

		PyDTObject stgmobj = _getStgMedium(obj->dataobj->m_lpDataObject, fmt);
		PyMFCStgMedium::TypeInstance *stgm = (PyMFCStgMedium::TypeInstance*)stgmobj.get();

		return PyMFCStgMedium::getData(stgm, PyDTInt(fmt.cfFormat).get());

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getHGlobal(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::getData");

		PyDTObject format(arg, false);

		FORMATETC fmt = _buildFormatEtc(format);
		fmt.tymed = TYMED_HGLOBAL;

		PyDTObject stgmobj = _getStgMedium(obj->dataobj->m_lpDataObject, fmt);
		PyMFCStgMedium::TypeInstance *stgm = (PyMFCStgMedium::TypeInstance*)stgmobj.get();
		stgm->medium->hGlobal;

		return PyMFCStgMedium::getData(stgm, PyDTInt(fmt.cfFormat).get());

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getMedium(TypeInstance *obj, PyObject *arg) {
		PyMFC_PROLOGUE("PyMFCOleDataSource::getMedium");

		PyDTObject format(arg, false);
		FORMATETC fmt = _buildFormatEtc(format);

		PyDTObject stgmobj = _getStgMedium(obj->dataobj->m_lpDataObject, fmt);
		return stgmobj.detach();

		PyMFC_EPILOGUE(NULL);
	}

	static EXTDEF def_oledataobj;
};

PyMFCOleDataObject::EXTDEF PyMFCOleDataObject::def_oledataobj;



class PyMFCOleDropTarget {
public:

	class DropTargetImpl:public COleDropTarget {
		PyObject *m_obj;
		BOOL m_isRbutton;
	public:
		DropTargetImpl(PyObject *obj) {
			m_obj = obj;
			m_isRbutton = FALSE;
		}

		DROPEFFECT OnDragEnter(CWnd* pWnd, COleDataObject* pDataObject, DWORD dwKeyState, CPoint point) {
			PyMFCEnterPython ep;
			DROPEFFECT ret = DROPEFFECT_NONE;
			try {
				m_isRbutton = dwKeyState & MK_RBUTTON;
				
				PyDTObject param = buildParam(pWnd, pDataObject, dwKeyState, 0, point);
				ret = PyDTObject(m_obj, false).callMethod("onDragEnter", "O", param.get()).getInt();
			}
			catch (PyDTException &err) {
//				PyDTObject o(m_obj, false);
//				PyDTString s(o.repr());
//				printf("%s\n", s.asString());
				err.setError();
				PyErr_Print();
				return DROPEFFECT_NONE;
			}

			return ret;
		}

		DROPEFFECT OnDragOver(CWnd* pWnd, COleDataObject* pDataObject, DWORD dwKeyState, CPoint point) {
			
			PyMFCEnterPython ep;
			DROPEFFECT ret = DROPEFFECT_NONE;
			try {
				PyDTObject param = buildParam(pWnd, pDataObject, dwKeyState, 0, point);
				ret = PyDTObject(m_obj, false).callMethod("onDragOver", "O", param.get()).getInt();
			}
			catch (PyDTException &err) {
				err.setError();
				PyErr_Print();
				return DROPEFFECT_NONE;
			}
			return ret;
		}

		void OnDragLeave(CWnd* pWnd) {
			
			PyMFCEnterPython ep;
			try {
				PyDTObject param = buildParam(pWnd, NULL, 0, 0, CPoint(0,0));
				PyDTObject(m_obj, false).callMethod("onDragLeave", "O", param.get()).getInt();
			}
			catch (PyDTException &err) {
				err.setError();
				PyErr_Print();
			}
		}


		BOOL OnDrop(CWnd* pWnd, COleDataObject* pDataObject, DROPEFFECT dropeffect, CPoint point) {
			ASSERT(0);
			return FALSE;
		}

		DROPEFFECT OnDropEx(CWnd* pWnd, COleDataObject* pDataObject, DROPEFFECT dropDefault, DROPEFFECT dropList, CPoint point) {
			PyMFCEnterPython ep;
			DROPEFFECT ret = DROPEFFECT_NONE;
			try {
				PyDTObject param = buildParam(pWnd, pDataObject, 0, dropDefault, point);
				PyDTObject result = PyDTObject(m_obj, false).callMethod("onDrop", "O", param.get());
				if (!result.isNone()) {
					ret = result.getInt();
				}
				
			}
			catch (PyDTException &err) {
				err.setError();
				PyErr_Print();
			}
			return ret;
		}
	

		DROPEFFECT OnDragScroll(CWnd* pWnd, DWORD dwKeyState, CPoint point)
		{
			PyMFCEnterPython ep;

			// Almost copied from COleDropTarget::OnDragScroll()
			ASSERT_VALID(this);
			ASSERT_VALID(pWnd);

			// get client rectangle of destination window
			CRect rectClient;
			pWnd->GetClientRect(&rectClient);
			CRect rect = rectClient;

			// hit-test against inset region
			UINT nTimerID = 0xffff;
			rect.InflateRect(-nScrollInset, -nScrollInset);
			BOOL lineup=FALSE, linedown=FALSE, lineleft=FALSE, lineright=FALSE;

			if (rectClient.PtInRect(point) && !rect.PtInRect(point))
			{
				// determine which way to scroll along both X & Y axis
				if (point.x < rect.left) {
					nTimerID = MAKEWORD(SB_LINEUP, HIBYTE(nTimerID));
					lineleft=TRUE;
				}
				else if (point.x >= rect.right) {
					nTimerID = MAKEWORD(SB_LINEDOWN, HIBYTE(nTimerID));
					lineright=TRUE;
				}

				if (point.y < rect.top) {
					nTimerID = MAKEWORD(LOBYTE(nTimerID), SB_LINEUP);
					lineup = TRUE;
				}
				else if (point.y >= rect.bottom) {
					nTimerID = MAKEWORD(LOBYTE(nTimerID), SB_LINEDOWN);
					linedown = TRUE;
				}
				ASSERT(nTimerID != 0xffff);

				// check for valid scroll first
				try {
					PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
					PyDTObject ev(msgtype.call(""));
					PyDTDict dict = ev.callMethod("getDict", "");
					
					dict.setItem("lineleft", lineleft);
					dict.setItem("lineright", lineright);
					dict.setItem("lineup", lineup);
					dict.setItem("linedown", linedown);

					PyDTObject result = PyDTObject(m_obj, false).callMethod("onDropScrollCheck", "O", ev.get());
					
					if (!result.getInt())
						nTimerID = 0xffff;
				}
				catch (PyDTException &err) {
					err.setError();
					PyErr_Print();
					return DROPEFFECT_NONE;
				}
			}

			if (nTimerID == 0xffff)
			{
				if (m_nTimerID != 0xffff)
				{
					// send fake OnDragEnter when transition from scroll->normal
					COleDataObject dataObject;
					dataObject.Attach(m_lpDataObject, FALSE);
					OnDragEnter(pWnd, &dataObject, dwKeyState, point);
					m_nTimerID = 0xffff;
				}
				return DROPEFFECT_NONE;
			}

			// save tick count when timer ID changes
			DWORD dwTick = GetTickCount();
			if (nTimerID != m_nTimerID)
			{
				m_dwLastTick = dwTick;
				m_nScrollDelay = nScrollDelay;
			}

			DROPEFFECT dropEffect = DROPEFFECT_NONE;
			// scroll if necessary
			if (dwTick - m_dwLastTick > m_nScrollDelay)
			{
				try {
					PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
					PyDTObject ev(msgtype.call(""));
					PyDTDict dict = ev.callMethod("getDict", "");
					
					dict.setItem("lineleft", lineleft);
					dict.setItem("lineright", lineright);
					dict.setItem("lineup", lineup);
					dict.setItem("linedown", linedown);

					PyDTObject result = PyDTObject(m_obj, false).callMethod("onDropScroll", "O", ev.get());
					if (!result.isNone()) {
						dropEffect = result.getInt();
					}
				}
				catch (PyDTException &err) {
					err.setError();
					PyErr_Print();
					return DROPEFFECT_NONE;
				}

				m_dwLastTick = dwTick;
				m_nScrollDelay = nScrollInterval;
			}
			if (m_nTimerID == 0xffff)
			{
				// send fake OnDragLeave when transitioning from normal->scroll
				OnDragLeave(pWnd);
			}

			m_nTimerID = nTimerID;
			return dropEffect;
		}

		PyDTObject buildParam(CWnd* pWnd, COleDataObject* pDataObject, DWORD dwKeyState, DROPEFFECT dropEffect, CPoint point) {
			
			PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
			PyDTObject ev(msgtype.call(""));
			PyDTDict dict = ev.callMethod("getDict", "");

			if (pWnd) {
				PyMFCWndBase *ret = dynamic_cast<PyMFCWndBase *>(pWnd);
				if (ret) {
					dict.setItem("wnd", ret->getPyObj());
				}
				else {
					dict.setItem("wnd", PyDTNone()); // hWnd?
				}
			}
			else {
				dict.setItem("wnd", PyDTNone());
			}
		

			if (pDataObject) {
				PyDTObject oledatatype = PyMFCOleDataObject::def_oledataobj.getDTTypeObj();
				PyDTObject ptr(PyMFCPtr(pDataObject->m_lpDataObject));
				dict.setItem("dataobj", oledatatype.call("Oi", ptr.get(), 0));
			}
			else {
				dict.setItem("dataobj", PyDTNone());
			}


			if (dwKeyState & MK_CONTROL) {
				dict.setItem("control", 1);
			}
			else {
				dict.setItem("control", 0);
			}

			if (dwKeyState & MK_SHIFT) {
				dict.setItem("shift", 1);
			}
			else {
				dict.setItem("shift", 0);
			}

			if (dwKeyState & MK_ALT) {
				dict.setItem("alt", 1);
			}
			else {
				dict.setItem("alt", 0);
			}

			if (dwKeyState & MK_LBUTTON) {
				dict.setItem("lbutton", 1);
			}
			else {
				dict.setItem("lbutton", 0);
			}

			if (dwKeyState & MK_MBUTTON) {
				dict.setItem("mbutton", 1);
			}
			else {
				dict.setItem("mbutton", 0);
			}

			dict.setItem("rbutton", m_isRbutton);

			PyDTObject effect = PyMFCDropEffect::def_dropeffect.getDTTypeObj().call("");
			effect.setAttr("value", dropEffect);
			dict.setItem("dropeffect", effect);
			
			PyDTTuple p(2);
			p.setItem(0, point.x);
			p.setItem(1, point.y);
			
			dict.setItem("pos", p);
			return ev;
		}

	
	};

	struct TypeInstance {
		PyObject_HEAD
		DropTargetImpl *target;
		PyDTObject *wnd;
	};

	typedef PyDTExtDef<PyMFCOleDropTarget> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.setGC(traverse, clear);

		def.addArgMethod("register", registerWnd);
//		def.addMethod("revoke", revokeWnd);
		def.addArgMethod("onDragEnter", onDragEnter);
		def.addArgMethod("onDragOver", onDragOver);
		def.addArgMethod("onDragLeave", onDragLeave);
		def.addArgMethod("onDrop", onDrop);
		def.addArgMethod("onDropScrollCheck", onDropScrollCheck);
		def.addArgMethod("onDropScroll", onDropScroll);
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCOleDroptarget::onInitObj");
		
		obj->target = new DropTargetImpl((PyObject *)obj);
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int traverse(TypeInstance *obj, visitproc visit, void *arg) {
		int err = 0;
		if (obj->wnd) {
			err = visit(obj->wnd->get(), arg);
			if (err) {
				return err;
			}
		}
		return err;
	}

	static int clear(TypeInstance *obj) {
		if (obj->target) {
			DropTargetImpl *p = obj->target;
			obj->target = NULL;
			delete p;
			
		}
		if (obj->wnd) {
			PyDTObject *p = obj->wnd;
			obj->wnd = NULL;
			delete p;
		}
		return 0;
	}

	static PyObject *registerWnd(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::registerWnd");

		PyDTObject wnd;
		
		if (!PyArg_ParseTuple(args, "O", wnd.getBuf()))
			return NULL;
		
		CWnd *cwnd = getCWnd<CWnd>(PyMFCPtr::asPtr(wnd.getAttr("cwnd").get()));
		obj->target->Register(cwnd);
		if (obj->wnd) {
			delete obj->wnd;
			obj->wnd = NULL;
		}
		obj->wnd = new PyDTObject(wnd);

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *revokeWnd(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::revokeWnd");

		obj->target->Revoke();

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}


	static PyObject *onDragEnter(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDragEnter");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDragEnter", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *onDragOver(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDragOver");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDragOver", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *onDragLeave(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDragLeave");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDragLeave", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *onDrop(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDrop");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDrop", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *onDropScrollCheck(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDropScrollCheck");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDropScrollCheck", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}


	static PyObject *onDropScroll(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFCFormatEtc::onDropScroll");

		PyDTObject msg;
		
		if (!PyArg_ParseTuple(args, "O", msg.getBuf()))
			return NULL;
		
		if (obj->wnd) {
			return obj->wnd->callMethod("onDropScroll", "O", msg.get()).detach();
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static EXTDEF def_oledroptarget;
};

PyMFCOleDropTarget::EXTDEF PyMFCOleDropTarget::def_oledroptarget;



void init_oleobjs(PyObject *module) {

//	AfxOleInit();

	// Todo: MFC doesn't initialize Ole for DLL.
	// Do I need to build .exe to call AfxOleInit()?
	::OleInitialize(NULL);
	
	PyDTModule m(module, false);
	PyDTRegType(m, "_pymfclib.DropEffect", "DropEffect", PyMFCDropEffect::def_dropeffect);

	PyDTRegType(m, "_pymfclib.StgMedium", "StgMedium", PyMFCStgMedium::def_stgmedium);
	PyDTRegType(m, "_pymfclib.FileDescriptor", "FileDescriptor", PyMFCFileDescriptor::def_filedescriptor);
	PyDTRegType(m, "_pymfclib.FormatEtc", "FormatEtc", PyMFCFormatEtc::def_formatetc);
	PyDTRegType(m, "_pymfclib.OleDataSource", "OleDataSource", PyMFCOleDataSource::def_oledatasrc);
	PyDTRegType(m, "_pymfclib.OleDataObject", "OleDataObject", PyMFCOleDataObject::def_oledataobj);
	PyDTRegType(m, "_pymfclib.OleDropTarget", "OleDropTarget", PyMFCOleDropTarget::def_oledroptarget);
}
