// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include <intshcut.h>
#include <atlbase.h>
#include <vector>
#include "pymfcdefs.h"
#include "pydt.h"
#include "pymutils.h"
#include "pymcom.h"

static
int pidl_size(ITEMIDLIST *pidl) {
	int ret = 0;
	while(pidl->mkid.cb) {
		ret += pidl->mkid.cb;
		pidl = (ITEMIDLIST*)(((ULONG)pidl) + pidl->mkid.cb);
	}
	return ret;
}

static
ITEMIDLIST *pidl_clone(IMalloc *im, ITEMIDLIST *pidl) { 
	int size = pidl_size(pidl); 
	ITEMIDLIST *ret = (LPITEMIDLIST)im->Alloc(size+sizeof(SHITEMID)); 
	if(!ret) {
		throw PyMFC_WIN32ERR();
	}
	memset(ret, 0, size+sizeof(SHITEMID));
	memcpy(ret, pidl, size); 
	return ret;
}

static
ITEMIDLIST *pidl_concat(IMalloc *im, ITEMIDLIST *pidl1, ITEMIDLIST *pidl2) { 
	int size1 = pidl_size(pidl1); 
	int size2 = pidl_size(pidl2); 

	ITEMIDLIST *ret = (LPITEMIDLIST)im->Alloc(size1+size2+sizeof(SHITEMID)); 
	if(!ret) {
		return NULL;
	}
	memset(ret, 0, size1+size2+sizeof(SHITEMID));
	memcpy(ret, pidl1, size1); 
	memcpy(((BYTE*)ret)+size1, pidl2, size2); 
	return ret;
}



class PyMFCPIDL {
public:
	static IMalloc *m_malloc;
	static IShellFolder *m_desktopFolder;
	static PyObject *m_typeobj;

	class initCO{
	public:
		initCO() {
			CoInitialize(NULL);
			SHGetMalloc(&PyMFCPIDL::m_malloc);
			if (FAILED(SHGetDesktopFolder(&PyMFCPIDL::m_desktopFolder))) {
				throw std::runtime_error("Failed to get Desktop folder.");
			}
		}
		~initCO() {
			PyMFCPIDL::m_desktopFolder->Release();
			PyMFCPIDL::m_malloc->Release();
			CoUninitialize();
		}
	};
	
	static initCO initco;

	struct TypeInstance {
		PyObject_HEAD
		ITEMIDLIST *pidl;
	};
	typedef PyDTExtDef<PyMFCPIDL> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(PyMFCPIDL::EXTDEF &def) {
		def.addIntMember("pidl", offsetof(TypeInstance, pidl), true);	

		def.addMethod("getDisplayName", getDispName);
		def.addMethod("getFilename", getFilename);
		def.addKwdArgMethod("getSubItems", getSubItems);
		def.addKwdArgMethod("getSysIconIndex", getSysIconIndex);
		def.addKwdArgMethod("getSysImageList", getSysImageList);

		def.addGetSet("filesystem", checkAttr, NULL, NULL, (void*)SFGAO_FILESYSTEM);
		def.addGetSet("folder", checkAttr, NULL, NULL, (void*)SFGAO_FOLDER);
		def.addGetSet("filesystemancestor", checkAttr, NULL, NULL, (void*)SFGAO_FILESYSANCESTOR);
		def.addGetSet("link", checkAttr, NULL, NULL, (void*)SFGAO_LINK);
		def.addGetSet("hassubfolder", checkAttr, NULL, NULL, (void*)SFGAO_HASSUBFOLDER);
	}
	
	static DWORD getAttribute(TypeInstance *obj, DWORD attr) {
		SHFILEINFO fi;
		fi.dwAttributes = attr;
		if (!SHGetFileInfo((TCHAR*)obj->pidl, SFGAO_FILESYSANCESTOR, &fi, sizeof(fi), 
				SHGFI_ATTRIBUTES|SHGFI_PIDL|SHGFI_ATTR_SPECIFIED)) {
			throw PyMFC_WIN32ERR();
		}
		return fi.dwAttributes;
	}

	static void getSpecialFolderPidl(TypeInstance *obj, int nFolder) {
		HRESULT ret = SHGetSpecialFolderLocation(NULL, nFolder, &obj->pidl);
		if (FAILED(ret)) {
			throw PyMFC_WIN32ERRCODE(ret);
		}
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCPIDL::onInitObj");
		
		obj->pidl = NULL;
		
		PyDTObject pidl;
		int desktop = 0;
		int appdata = 0;
		const char *filename=NULL;

		static char *kwlist[] = {"pidl", "desktop", "appdata", "filename", NULL};


		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|Oiis", kwlist, pidl.getBuf(), &desktop, &appdata, &filename))
			return -1;
		
		if (!pidl.isNull()) {
			if (!pidl.isInstance(m_typeobj)) {
				obj->pidl = (ITEMIDLIST*)pidl.getInt(0);
			}
			else {
				TypeInstance *src = (TypeInstance*)pidl.get();
				obj->pidl = pidl_clone(m_malloc, src->pidl);
			}
		}
		else if (desktop) {
			getSpecialFolderPidl(obj, CSIDL_DESKTOP);
		}
		else if (appdata) {
			getSpecialFolderPidl(obj, CSIDL_APPDATA);
		}
		else if (filename) {
			CComPtr<IShellFolder> folder;
			UnicodeStr fname(filename);
			ULONG chEaten, attr;
			HRESULT err = m_desktopFolder->ParseDisplayName(0, NULL, fname.m_wstr, 
				&chEaten, &obj->pidl, &attr);
			if FAILED(err) {
				throw PyMFC_WIN32ERRCODE(err);
			}
		}
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->pidl) {
			m_malloc->Free(obj->pidl);
			obj->pidl = NULL;
		}
		return 0;
	}


	static TypeInstance *newInstance(ITEMIDLIST *pidl) {
		TypeInstance *ret = (TypeInstance *)PyObject_NEW(TypeInstance, 
								(PyTypeObject *)m_typeobj);
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		ret->pidl = pidl;
		return ret;
	}
	
	static PyObject *checkAttr(TypeInstance *obj, void *closure) {
		PyMFC_PROLOGUE("PyMFCPIDL::checkAttr");
		
		DWORD attr = getAttribute(obj, (DWORD)closure);
		return PyDTInt((attr & (DWORD)closure)?1:0).detach();

		PyMFC_EPILOGUE(NULL);
	}
	
	static PyObject *getFilename(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCPIDL::getFilename");
		
		TCHAR fname[MAX_PATH];

		if (!SHGetPathFromIDList(obj->pidl, fname)) {
			throw PyMFC_WIN32ERR();
		}
		return PyDTUnicode(fname).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getDispName(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFCPIDL::getDispName");
		
		SHFILEINFO fi;

		HRESULT ret = SHGetFileInfo((const TCHAR *)obj->pidl, 0, &fi, sizeof(fi), SHGFI_DISPLAYNAME|SHGFI_PIDL);
		return PyDTUnicode(fi.szDisplayName).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getSysImageList(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCPIDL::getSysImageList");
		
		BOOL smallIcon=FALSE;
		static char *kwlist[] = {"small", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|i", kwlist, &smallIcon))
			return NULL;

		UINT f = SHGFI_PIDL | SHGFI_SYSICONINDEX;
		if (smallIcon) {
			f |= SHGFI_SMALLICON;
		}

		SHFILEINFO fi;
		HIMAGELIST himg = (HIMAGELIST)SHGetFileInfo((const TCHAR *)obj->pidl, 0, &fi, sizeof(fi), f);
		if (NULL == himg) {
			throw PyMFC_WIN32ERR();
		}
		
		PyDTModule pymfclib(PYMFC_MODULENAME);
		PyDTObject imagelist(pymfclib.getAttr("_imagelist").call(""));

		PyMFCHandle himgobj(himg);
		imagelist.callMethod("attach", "Oi", himgobj.get(), 0);

		return imagelist.detach();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getSysIconIndex(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCPIDL::getSysIconIndex");
		
		BOOL smallIcon=FALSE;
		static char *kwlist[] = {"small", NULL};

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|i", kwlist, &smallIcon))
			return NULL;

		UINT f = SHGFI_PIDL | SHGFI_SYSICONINDEX;
		if (smallIcon) {
			f |= SHGFI_SMALLICON;
		}

		SHFILEINFO fi;
		if (NULL ==SHGetFileInfo((const TCHAR *)obj->pidl, 0, &fi, sizeof(fi), f)) {
			throw PyMFC_WIN32ERR();
		}
		
		return PyDTInt(fi.iIcon).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getSubItems(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCPIDL::getSubItems");

//todo: release GIL.

		BOOL folder=1, nonfolder=0, hidden=0;
		PyDTObject wnd;
		static char *kwlist[] = {"folder", "nonfolder", "hidden", "wnd", NULL};


		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|iiiO", kwlist, &folder, &nonfolder, &hidden, wnd.getBuf()))
			return NULL;
		DWORD attr = getAttribute(obj, SFGAO_FILESYSANCESTOR|SFGAO_HASSUBFOLDER);
		if (!(attr)) {
			// No sub folder
			return PyDTTuple(0).detach();
		}

		int f = 0;
		f |= folder ? SHCONTF_FOLDERS:0;
		f |= nonfolder ? SHCONTF_NONFOLDERS:0;
		f |= hidden ? SHCONTF_INCLUDEHIDDEN:0;

		CComPtr<IShellFolder> ifolder;
		if (!obj->pidl->mkid.cb) {
			// Desktop folder
			ifolder = m_desktopFolder;
		}
		else{
			HRESULT err = m_desktopFolder->BindToObject(
					obj->pidl, NULL, IID_IShellFolder, (void**)&ifolder);
			if (err == E_NOTIMPL) {
				// This object doesn't support IShellFolder.
				return PyDTTuple(0).detach();
			}
			if (FAILED(err)) {
				throw PyMFC_WIN32ERRCODE(err);
			}
		}

		HWND hWnd = NULL;
		if (!wnd.isNull()) {
			hWnd = (HWND)PyMFCHandle::asHandle(wnd.callMethod("getHwnd", "").get());
		}

		std::vector<ITEMIDLIST *> ids;
		{
			PyMFCLeavePython clp;

			CComPtr<IEnumIDList> ienum;
			HRESULT err = ifolder->EnumObjects(hWnd, f, &ienum);
			if (FAILED(err)) {
				throw PyMFC_WIN32ERRCODE(err);
			}
			
			ITEMIDLIST *child;
			while (true) {
				err = ienum->Next(1, &child, NULL);
				if (err == S_FALSE) {
					break;
				}
				if (FAILED(err)) {
					throw PyMFC_WIN32ERRCODE(err);
				}
				
				ITEMIDLIST *absid = pidl_concat(m_malloc, obj->pidl, child);
				ids.push_back(absid);

				m_malloc->Free(child);
			}
		}

		PyDTTuple ret(ids.size());
		int i = 0;
		for (std::vector<ITEMIDLIST *>::iterator iter = ids.begin(); iter != ids.end(); iter++, i++) {
			PyDTObject o((PyObject *)newInstance(*iter), true); // newInstance() steals ITEMIDLIST.
			ret.setItem(i, o);
		}
		return ret.detach();
		
		PyMFC_EPILOGUE(NULL);
	}
	static EXTDEF def_shitemidlist;
};


PyMFCPIDL::EXTDEF PyMFCPIDL::def_shitemidlist;
PyObject *PyMFCPIDL::m_typeobj=NULL;
IMalloc *PyMFCPIDL::m_malloc=NULL;
IShellFolder *PyMFCPIDL::m_desktopFolder=NULL;
PyMFCPIDL::initCO PyMFCPIDL::initco;



class PyMFC_IUniformResourceLocator:
		public PyMFC_COMRef<PyMFC_IUniformResourceLocator, 
		IUniformResourceLocator, IID_IUniformResourceLocator> {

public:
	typedef PyDTExtDef<PyMFC_IUniformResourceLocator> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		initBaseMethods(def);
		def.addMethod("getUrl", getUrl);
	}

	static PyObject *getUrl(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IUniformResourceLocator::getUrl");
			
		checkObj(obj);

		LPTSTR lpTemp;
		HRESULT hr = obj->obj->GetURL(&lpTemp);

		if (SUCCEEDED(hr)) {
			PyDTUnicode ret(lpTemp);
			IMalloc* pMalloc;
			hr = SHGetMalloc(&pMalloc); 
			if (SUCCEEDED(hr)){
				pMalloc->Free(lpTemp);
				pMalloc->Release();
				return ret.detach();
			}
		}
		throw PyMFC_WIN32ERRCODE(hr);
		PyMFC_EPILOGUE(NULL);
	}

	static EXTDEF def_iuniformresourcelocator;
};

PyMFC_IUniformResourceLocator::EXTDEF PyMFC_IUniformResourceLocator::def_iuniformresourcelocator;
















void init_shlobj(PyObject *module) {

	PyDTModule m(module, false);

	PyDTRegType(m, "_pymfclib.SHItemIdList", "SHItemIdList", PyMFCPIDL::def_shitemidlist);
	PyMFCPIDL::m_typeobj = (PyObject *)&PyMFCPIDL::def_shitemidlist.getTypeObj();
	
	
	PyDTRegType(m, "_pymfclib.IUniformResourceLocator", "IUniformResourceLocator", PyMFC_IUniformResourceLocator::def_iuniformresourcelocator);
}

