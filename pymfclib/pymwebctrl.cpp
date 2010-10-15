// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#import <shdocvw.dll>
#import <mshtml.tlb>
#include <mshtmdid.h>

#include "pymwndbase.h"

#include "pymwnd.h"
#include "pymwin32funcs.h"
#include "pymutils.h"
#include "CWebBrowser2.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


class PyMFCWndEventSink : public CCmdTarget
{
	DECLARE_DYNAMIC(PyMFCWndEventSink )

public:
	PyMFCWndEventSink ();
	virtual ~PyMFCWndEventSink ();

	BOOL advise(IUnknownPtr elem, REFIID iid) {
		m_srcunk = elem;
		m_srciid = iid;
		IUnknown *unk = GetIDispatch(FALSE);
		return AfxConnectionAdvise(elem, iid, unk, FALSE, &m_cookie);
	}

	void unAdvise() {
		m_eventdict = NULL;
		DWORD cookie = m_cookie;
		m_cookie = NULL;
		if (cookie) {
			IUnknown *unk = GetIDispatch(FALSE);
			AfxConnectionUnadvise(m_srcunk, m_srciid, unk, TRUE, cookie);
		}
	}

	BOOL callHandler(IDispatch *disp, const char *eventname);

	PyDTObject getEventHandler(const char *eventname) {
		if (!m_cookie || !m_eventdict) {
			return PyDTNone();
		}
		
		return PyDTDict(m_eventdict, false).getItem(eventname);
	}
protected:
	DECLARE_DISPATCH_MAP()
public:
	virtual void OnFinalRelease();
	IUnknownPtr m_srcunk;
	IID m_srciid;

	DWORD m_cookie;
	PyObject *m_eventdict;

	BOOL OnKeyPress(IDispatch *disp);
	BOOL OnClick(IDispatch *disp);
	BOOL OnDragStart(IDispatch *disp);
};

IMPLEMENT_DYNAMIC(PyMFCWndEventSink, CCmdTarget)


BEGIN_DISPATCH_MAP(PyMFCWndEventSink, CCmdTarget)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLDOCUMENTEVENTS2_ONKEYPRESS", DISPID_HTMLDOCUMENTEVENTS2_ONKEYPRESS, OnKeyPress, VT_BOOL, VTS_DISPATCH)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLELEMENTEVENTS2_ONKEYPRESS", DISPID_HTMLELEMENTEVENTS2_ONKEYPRESS, OnKeyPress, VT_BOOL, VTS_DISPATCH)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLDOCUMENTEVENTS2_ONCLICK", DISPID_HTMLDOCUMENTEVENTS2_ONCLICK, OnClick, VT_BOOL, VTS_DISPATCH)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLELEMENTEVENTS2_ONCLICK", DISPID_HTMLELEMENTEVENTS2_ONCLICK, OnClick, VT_BOOL, VTS_DISPATCH)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLDOCUMENTEVENTS2_ONDRAGSTART", DISPID_HTMLDOCUMENTEVENTS2_ONDRAGSTART, OnDragStart, VT_BOOL, VTS_DISPATCH)
	DISP_FUNCTION_ID(PyMFCWndEventSink, "HTMLELEMENTEVENTS2_ONDRAGSTART", DISPID_HTMLELEMENTEVENTS2_ONDRAGSTART, OnDragStart, VT_BOOL, VTS_DISPATCH)
END_DISPATCH_MAP()

PyMFCWndEventSink::PyMFCWndEventSink()
{
	EnableAutomation();
}

PyMFCWndEventSink::~PyMFCWndEventSink()
{
}

void PyMFCWndEventSink::OnFinalRelease()
{
	CCmdTarget::OnFinalRelease();
}

template <class T, class T_INTERFACE, REFIID T_EVENTIID>
class PyMFC_IHTMLElementBase {
public:
	struct TypeInstance {
		PyObject_HEAD
		T_INTERFACE *elem;
		PyMFCWndEventSink *sink;
		PyObject *eventmap;
	};

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void addCommonMethods(PyDTExtDef<T> &def) {
		def.setGC(traverse, clear);
		def.addObjMember("events", offsetof(TypeInstance, eventmap));
	}

	static int traverse(TypeInstance *obj, visitproc visit, void *arg) {
		int err = 0;
		if (obj->eventmap) {
			err = visit(obj->eventmap, arg);
			if (err) {
				return err;
			}
		}
		return err;
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElementBase::onInitObj");
		return 0;
		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->sink) {
			// Don't delete event sink here. The sink will be destroyed automatically.
			obj->sink->unAdvise();
			obj->sink = NULL;
		}
		if (obj->elem) {
			delete obj->elem;
			obj->elem = NULL;
		}
		if (obj->eventmap) {
			Py_XDECREF(obj->eventmap);
			obj->eventmap = NULL;
		}
		return 0;
	}

	static PyObject *newInstance(T_INTERFACE elem) {
		TypeInstance *ret = (TypeInstance *)PyObject_GC_New(
			TypeInstance, 
			(PyTypeObject *)&T::def_elemtype.getTypeObj());

		if (!ret) {
			throw PyDTExc_PythonError();
		}
		ret->elem = NULL;
		ret->eventmap = NULL;
		ret->sink = NULL;

		ret->elem = new T_INTERFACE(elem);
		PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
		ret->eventmap = msgtype.call("").detach();

		PyMFCWndEventSink *sink= new PyMFCWndEventSink();
		if (sink->advise(elem, T_EVENTIID)) {
			ret->sink = sink;
			ret->sink->m_eventdict = ((PyMFCWndMsgType::TypeInstance*)ret->eventmap)->x_attr;
		}
		PyObject_GC_Track((PyObject *)ret);
		return (PyObject *)ret;
	}

};

/*
class PyMFC_IHTMLElement
*/
class PyMFC_IHTMLElement
	:public PyMFC_IHTMLElementBase<PyMFC_IHTMLElement, MSHTML::IHTMLElement2Ptr, __uuidof(MSHTML::HTMLElementEvents)> {
public:
	typedef PyDTExtDef<PyMFC_IHTMLElement> EXTDEF;

	static void initMethods(PyMFC_IHTMLElement::EXTDEF &def) {
		addCommonMethods(def);
		
		def.addGetSet("elemId", getElementId, NULL);
		def.addGetSet("innerHTML", getInnerHTML, NULL);
		def.addGetSet("innerText", getInnerText, NULL);
		def.addGetSet("tagName", getTagName, NULL);
		def.addGetSet("clientRect", getClientRect, NULL);
		def.addGetSet("scrollRect", getScrollRect, NULL);

		def.addMethod("getDocument", getDocument);
		def.addMethod("getParent", getParent);
		def.addKwdArgMethod("doScroll", doScroll);

	}
	
	static PyObject *getElementId(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getElementId");
		MSHTML::IHTMLElementPtr elem = *(obj->elem);
		if (elem) {
			_bstr_t s = elem->id;
			return PyDTUnicode(s).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getInnerHTML(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getInnerHTML");
		MSHTML::IHTMLElementPtr elem = *(obj->elem);
		if (elem) {
			_bstr_t s = elem->innerHTML;
			return PyDTUnicode(s).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getInnerText(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getInnerText");
		MSHTML::IHTMLElementPtr elem = *(obj->elem);
		if (elem) {
			_bstr_t s = elem->innerText;
			return PyDTUnicode(s).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getTagName(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getTagName");
		MSHTML::IHTMLElementPtr elem = *(obj->elem);
		if (elem) {
			_bstr_t s = elem->tagName;
			return PyDTUnicode(s).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}
	static PyObject *getClientRect(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getClientRect");
		MSHTML::IHTMLElement2Ptr elem = *(obj->elem);
		if (elem) {
			long left = elem->clientLeft;
			long top = elem->clientTop;
			long right = left + elem->clientWidth;
			long bottom = top + elem->clientHeight;
			return pydtMakeTuple(left, top, right, bottom).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}
	static PyObject *getScrollRect(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::getScrollRect");
		MSHTML::IHTMLElement2Ptr elem = *(obj->elem);
		if (elem) {
			long left = elem->scrollLeft;
			long top = elem->scrollTop;
			long right = elem->scrollWidth;
			long bottom = elem->scrollHeight;
			return pydtMakeTuple(left, top, right, bottom).detach();
		}
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(NULL);
	}


	static PyObject *doScroll(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFC_IHTMLElement::doScroll");

		static char *kwlist[] = {"pagedown", "pageup", NULL};
		int pagedown=0, pageup=0;

		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
				"|ii", kwlist, &pagedown, &pageup)) {
			return NULL;
		}		

		HRESULT hr;
		{
			PyMFCLeavePython lp;
			if (pagedown) {
				hr = (*(obj->elem))->doScroll(_bstr_t(L"pageDown"));
			}
			else {
				hr = (*(obj->elem))->doScroll(_bstr_t(L"pageUp"));
			}
		}
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}

		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}


	static PyObject *getDocument(TypeInstance *obj);
	static PyObject *getParent(TypeInstance *obj);
	static EXTDEF def_elemtype;
};

PyMFC_IHTMLElement::EXTDEF PyMFC_IHTMLElement::def_elemtype;



/*
class PyMFC_IHTMLDocument
*/
class PyMFC_IHTMLDocument
	:public PyMFC_IHTMLElementBase<PyMFC_IHTMLDocument, MSHTML::IHTMLDocument2Ptr, __uuidof(MSHTML::HTMLDocumentEvents2)> {
public:
	typedef PyDTExtDef<PyMFC_IHTMLDocument> EXTDEF;

	static void initMethods(PyMFC_IHTMLDocument::EXTDEF &def) {
		addCommonMethods(def);
		def.addArgMethod("setHTML", setHTML);
		def.addMethod("getBody", getBody);
		def.addGetSet("URL", getURL, setURL);
	}
	
	static PyObject *setHTML(TypeInstance *obj, PyObject *args) {
		PyMFC_PROLOGUE("PyMFC_IHTMLDocument::setHTML");

		PyDTUnicode html;
		if (!PyArg_ParseTuple(args, "O", html.getBuf()))
			return NULL;
		const Py_UNICODE *s = html.asUnicode();
		{	
			PyMFCLeavePython lp;

			VARIANT varColInfo;
			VariantInit(&varColInfo);

			varColInfo.vt = VT_BSTR;
			varColInfo.bstrVal = ::SysAllocString(s);

			COleSafeArray sa;
			sa.CreateOneDim(VT_VARIANT, 1, &varColInfo);

			HRESULT ret= (*(obj->elem))->write(sa.parray);
			if SUCCEEDED(ret) {
				ret= (*(obj->elem))->close();
			}
		}
		PyMFC_RETNONE();
		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getBody(TypeInstance *obj) {
		PyMFC_PROLOGUE("PyMFC_IHTMLDocument::getBody");


		MSHTML::IHTMLElement2Ptr body = (*(obj->elem))->body;
		
		if (body) {
			return PyMFC_IHTMLElement::newInstance(body);
		}
		else {
			PyMFC_RETNONE();
		}

		PyMFC_EPILOGUE(NULL);
	}

	static PyObject *getURL(TypeInstance *obj, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLDocument::getURL");
		_bstr_t url = (*(obj->elem))->url;
		return PyDTUnicode(url).detach();

		PyMFC_EPILOGUE(NULL);
	}

	static int setURL(TypeInstance *obj, PyObject *v, void *) {
		PyMFC_PROLOGUE("PyMFC_IHTMLDocument::setURL");
		PyDTUnicode url(v, false);
		const Py_UNICODE *s = url.asUnicode();
		{	
			PyMFCLeavePython lp;
			(*(obj->elem))->url = _bstr_t(s);
		}
		return 0;

		PyMFC_EPILOGUE(-1);
	}


	static EXTDEF def_elemtype;
};

PyMFC_IHTMLDocument::EXTDEF PyMFC_IHTMLDocument::def_elemtype;


class PyMFCOleCommandTarget {
public:
	struct TypeInstance {
		PyObject_HEAD
		IOleCommandTarget *cmdtarget;
	};

	typedef PyDTExtDef<PyMFCOleCommandTarget> EXTDEF;

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addKwdArgMethod("execCommand", execCommand);
		def.addKwdArgMethod("queryStatus", queryStatus);
	}
	
	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE("PyMFCOleCommandTarget::onInitObj");
		obj->cmdtarget = NULL;
		return 0;

		PyMFC_EPILOGUE(-1);
	}

	static void onDeallocObj(TypeInstance *obj) {
		clear(obj);
	}

	static int clear(TypeInstance *obj) {
		if (obj->cmdtarget) {
			obj->cmdtarget->Release();
			obj->cmdtarget = NULL;
		}
		return 0;
	}

	static PyObject *queryStatus(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE(execCommand)

		if (!obj->cmdtarget) {
			throw PyDTExc_InvalidValue("NULL IOleCommandTarget");
		}
		
		static char *kwlist[] = {"menuid", NULL};
		PyDTObject menuid;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O", kwlist, menuid.getBuf())) {
			return NULL;
		}
		
		if (!menuid.isTrue()) {
			throw PyDTExc_InvalidValue("Invarid menuid");
		}


		OLECMD olecmd;
		olecmd.cmdID = menuid.getULong();
	
		HRESULT hr = obj->cmdtarget->QueryStatus(NULL, 1, &olecmd, NULL);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		return PyDTInt(olecmd.cmdf).detach();

		PyMFC_EPILOGUE(0);
	}

	static PyObject *execCommand(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		PyMFC_PROLOGUE(execCommand)

		if (!obj->cmdtarget) {
			throw PyDTExc_InvalidValue("NULL IOleCommandTarget");
		}
		
		static char *kwlist[] = {"menuid", NULL};
		PyDTObject menuid;
		if (!PyArg_ParseTupleAndKeywords(args, kwds, 
			"O", kwlist, menuid.getBuf())) {
			return NULL;
		}
		
		if (!menuid.isTrue()) {
			throw PyDTExc_InvalidValue("Invarid menuid");
		}

		HRESULT hr = obj->cmdtarget->Exec(NULL, menuid.getULong(), OLECMDEXECOPT_DODEFAULT, NULL, NULL);
		if (FAILED(hr)) {
			throw PyMFC_WIN32ERRCODE(hr);
		}
		
		PyMFC_RETNONE();

		PyMFC_EPILOGUE(0);
	}

	static PyObject *newInstance(IOleCommandTarget *ct) {
		if (!ct) {
			throw PyDTExc_InvalidValue("NULL IOleCommandTarget");
		}
		TypeInstance *ret = (TypeInstance *)def_olecmdtarget.newObject();

		if (!ret) {
			throw PyDTExc_PythonError();
		}
		ret->cmdtarget = ct;
		return (PyObject *)ret;
	}
	
	static EXTDEF def_olecmdtarget;
};

PyMFCOleCommandTarget::EXTDEF PyMFCOleCommandTarget::def_olecmdtarget;


/* 
class PyMFCWebCtrl
*/

class PyMFCWebCtrl:public CWnd {
protected:
	DECLARE_DYNCREATE(PyMFCWebCtrl)
	PyDTObject getEventMap(const char *name);
protected:
	DECLARE_MESSAGE_MAP()
	DECLARE_EVENTSINK_MAP()


	BOOL CreateControlSite(COleControlContainer* pContainer, COleControlSite** ppSite, UINT nID, const IID &clsid);

public:
	void NavigateError(LPDISPATCH pDisp, VARIANT* URL, VARIANT* Frame, VARIANT* StatusCode, BOOL* Cancel);
	void DocumentComplete(LPDISPATCH pDisp, VARIANT* URL);
	void StatusTextChange(LPCTSTR text);
	HRESULT ShowContextMenu(DWORD dwID, LPPOINT ppt, LPUNKNOWN pcmdtReserved, LPDISPATCH pdispReserved);


	CWebBrowser2 m_ie;	
	HRESULT navigate(const LPCWSTR url);
	HRESULT setText(const LPCWSTR html);
public:
	PyMFCWndBase* getWndBase() {return dynamic_cast<PyMFCWndBase*>(this);}

	int OnCreate(LPCREATESTRUCT lpCreateStruct);
	afx_msg void OnSize(UINT nType, int cx, int cy);
	afx_msg void OnSetFocus(CWnd *pOldWnd);
	virtual BOOL OnAmbientProperty(COleControlSite* pSite, DISPID dispid, VARIANT* pvar);

	virtual BOOL PreTranslateMessage(MSG* pMsg);
};




class PyMFCWebOleClientSite : public COleControlSite {
public:
	PyMFCWebOleClientSite(COleControlContainer* pParentWnd)
		:COleControlSite(pParentWnd){}
	~PyMFCWebOleClientSite(){}

	PyMFCWebCtrl *getCtrl() {
		return STATIC_DOWNCAST(PyMFCWebCtrl, m_pCtrlCont->m_pWnd);
	}

	BEGIN_INTERFACE_PART(DocHostUIHandler, IDocHostUIHandler)
		STDMETHOD(ShowContextMenu)(DWORD, LPPOINT, LPUNKNOWN, LPDISPATCH);
		STDMETHOD(GetHostInfo)(DOCHOSTUIINFO*);
		STDMETHOD(ShowUI)(DWORD, LPOLEINPLACEACTIVEOBJECT,
			LPOLECOMMANDTARGET, LPOLEINPLACEFRAME, LPOLEINPLACEUIWINDOW);
		STDMETHOD(HideUI)(void);
		STDMETHOD(UpdateUI)(void);
		STDMETHOD(EnableModeless)(BOOL);
		STDMETHOD(OnDocWindowActivate)(BOOL);
		STDMETHOD(OnFrameWindowActivate)(BOOL);
		STDMETHOD(ResizeBorder)(LPCRECT, LPOLEINPLACEUIWINDOW, BOOL);
		STDMETHOD(TranslateAccelerator)(LPMSG, const GUID*, DWORD);
		STDMETHOD(GetOptionKeyPath)(OLECHAR **, DWORD);
		STDMETHOD(GetDropTarget)(LPDROPTARGET, LPDROPTARGET*);
		STDMETHOD(GetExternal)(LPDISPATCH*);
		STDMETHOD(TranslateUrl)(DWORD, OLECHAR*, OLECHAR **);
		STDMETHOD(FilterDataObject)(LPDATAOBJECT , LPDATAOBJECT*);
	END_INTERFACE_PART(DocHostUIHandler)

	DECLARE_INTERFACE_MAP()
};

BEGIN_INTERFACE_MAP(PyMFCWebOleClientSite, COleControlSite)
	INTERFACE_PART(PyMFCWebOleClientSite, IID_IDocHostUIHandler, DocHostUIHandler)
END_INTERFACE_MAP()

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::GetExternal(LPDISPATCH *lppDispatch)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}


STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::ShowContextMenu(
	DWORD dwID, LPPOINT ppt, LPUNKNOWN pcmdtReserved, LPDISPATCH pdispReserved)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)

	return pThis->getCtrl()->ShowContextMenu(dwID, ppt, pcmdtReserved, pdispReserved);
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::GetHostInfo(
	DOCHOSTUIINFO *pInfo)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::ShowUI(
	DWORD dwID, LPOLEINPLACEACTIVEOBJECT pActiveObject,
	LPOLECOMMANDTARGET pCommandTarget, LPOLEINPLACEFRAME pFrame,
	LPOLEINPLACEUIWINDOW pDoc)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)

	return S_FALSE;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::HideUI(void)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::UpdateUI(void)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::EnableModeless(BOOL fEnable)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::OnDocWindowActivate(BOOL fActivate)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::OnFrameWindowActivate(
	BOOL fActivate)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::ResizeBorder(
	LPCRECT prcBorder, LPOLEINPLACEUIWINDOW pUIWindow, BOOL fFrameWindow)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_OK;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::TranslateAccelerator(
	LPMSG lpMsg, const GUID* pguidCmdGroup, DWORD nCmdID)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::GetOptionKeyPath(
	LPOLESTR* pchKey, DWORD dwReserved)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::GetDropTarget(
	LPDROPTARGET pDropTarget, LPDROPTARGET* ppDropTarget)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::TranslateUrl(
	DWORD dwTranslate, OLECHAR* pchURLIn, OLECHAR** ppchURLOut)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::FilterDataObject(
	LPDATAOBJECT pDataObject, LPDATAOBJECT* ppDataObject)
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return S_FALSE;
}

STDMETHODIMP_(ULONG) PyMFCWebOleClientSite::XDocHostUIHandler::AddRef()
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return pThis->ExternalAddRef();
}

STDMETHODIMP_(ULONG) PyMFCWebOleClientSite::XDocHostUIHandler::Release()
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return pThis->ExternalRelease();
}

STDMETHODIMP PyMFCWebOleClientSite::XDocHostUIHandler::QueryInterface(
		  REFIID iid, LPVOID far* ppvObj)     
{
	METHOD_PROLOGUE_EX_(PyMFCWebOleClientSite, DocHostUIHandler)
	return pThis->ExternalQueryInterface(&iid, ppvObj);
}


IMPLEMENT_DYNCREATE(PyMFCWebCtrl, CWnd)

BEGIN_MESSAGE_MAP(PyMFCWebCtrl, CWnd)
	ON_WM_CREATE()
	ON_WM_SIZE()
	ON_WM_SETFOCUS()
END_MESSAGE_MAP()

BEGIN_EVENTSINK_MAP(PyMFCWebCtrl, CDialog)
	ON_EVENT(PyMFCWebCtrl, AFX_IDW_PANE_FIRST, DISPID_NAVIGATEERROR, PyMFCWebCtrl::NavigateError, VTS_DISPATCH VTS_PVARIANT VTS_PVARIANT VTS_PVARIANT VTS_PBOOL)
	ON_EVENT(PyMFCWebCtrl, AFX_IDW_PANE_FIRST, DISPID_DOCUMENTCOMPLETE, PyMFCWebCtrl::DocumentComplete, VTS_DISPATCH VTS_PVARIANT)
	ON_EVENT(PyMFCWebCtrl, AFX_IDW_PANE_FIRST, DISPID_STATUSTEXTCHANGE, PyMFCWebCtrl::StatusTextChange, VTS_BSTR)
END_EVENTSINK_MAP()

BOOL PyMFCWebCtrl::PreTranslateMessage(MSG* pMsg)
{
   if(IsDialogMessage(pMsg))
       return TRUE;
   else
       return CWnd::PreTranslateMessage(pMsg);
}

BOOL PyMFCWebCtrl::OnAmbientProperty(COleControlSite* pSite, DISPID dispid, VARIANT* pvar)
{
	
	if (dispid == DISPID_AMBIENT_DLCONTROL) {
		pvar->vt = VT_I4;
		pvar->lVal = DLCTL_DLIMAGES|DLCTL_NO_BEHAVIORS|DLCTL_NO_CLIENTPULL|DLCTL_NO_SCRIPTS|DLCTL_NO_DLACTIVEXCTLS
					|DLCTL_NO_FRAMEDOWNLOAD|DLCTL_NO_JAVA|DLCTL_NO_RUNACTIVEXCTLS;
		return TRUE;
	}

	return CWnd::OnAmbientProperty(pSite, dispid, pvar);
}

int PyMFCWebCtrl::OnCreate(LPCREATESTRUCT lpCreateStruct) {
	if (CWnd::OnCreate(lpCreateStruct) == -1)
		return -1;
	m_ie.Create(NULL, L"", WS_CHILD|WS_VISIBLE, CRect(0,0,0,0), this, AFX_IDW_PANE_FIRST, NULL);
	return 0;
}

void PyMFCWebCtrl::OnSize(UINT nType, int cx, int cy)
{
	CWnd::OnSize(nType, cx, cy);
	m_ie.SetWindowPos(NULL, 0, 0, cx, cy, 0);
}

void PyMFCWebCtrl::OnSetFocus(CWnd *pOldWnd) {
	m_ie.SetFocus();
}


BOOL PyMFCWebCtrl::CreateControlSite(COleControlContainer* pContainer, COleControlSite** ppSite, UINT nID, const IID &clsid) {
	*ppSite = new PyMFCWebOleClientSite(pContainer);
	return True;
//	return CWnd::CreateControlSite(pContainer, ppSite, nID, clsid);
}

PyDTObject PyMFCWebCtrl::getEventMap(const char *name) {
	PyDTObject wobj(getWndBase()->getPyObj());
	PyDTObject eventmap;
	wobj.getAttr("events", eventmap);

	return eventmap.callMethod("_getHandler", "s", name);
}

void PyMFCWebCtrl::DocumentComplete(LPDISPATCH pDisp, VARIANT* url) {
	PyMFCEnterPython e;
	try {
		PyDTObject f = getEventMap("DocumentComplete");
		if (f.get() && !f.isNone()) {
			PyDTObject s_url = PyDTNone();
			if (url->vt == VT_BSTR) {
				s_url = PyDTUnicode(url->bstrVal, SysStringLen(url->bstrVal));
			}
			f.call("O", s_url.get());
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
	}
}

void PyMFCWebCtrl::StatusTextChange(LPCTSTR text) {
	PyMFCEnterPython e;
	try {
		PyDTObject f = getEventMap("StatusTextChange");
		if (f.get() && !f.isNone()) {
			PyDTUnicode t(text);
			f.call("O", t.get());
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
	}
}

void PyMFCWebCtrl::NavigateError(LPDISPATCH pDisp, VARIANT* url, VARIANT* Frame, VARIANT* StatusCode, BOOL* Cancel) {
	PyMFCEnterPython e;
	try {
		PyDTObject wobj(getWndBase()->getPyObj());
		PyDTObject eventmap;
		wobj.getAttr("events", eventmap);

		PyDTObject f = eventmap.callMethod("_getHandler", "s", "NavigateError");
		if (f.get() && !f.isNone()) {
			PyDTObject s_url = PyDTNone();
			if (url->vt == VT_BSTR) {
				s_url = PyDTUnicode(url->bstrVal, SysStringLen(url->bstrVal));
			}
			f.call("O", s_url.get());
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
	}
}

HRESULT PyMFCWebCtrl::ShowContextMenu(DWORD dwID, LPPOINT ppt, LPUNKNOWN pcmdtReserved, LPDISPATCH pdispReserved) {
	PyMFCEnterPython e;
	try {
		PyDTObject wobj(getWndBase()->getPyObj());
		PyDTObject eventmap;
		wobj.getAttr("events", eventmap);

		PyDTObject f = eventmap.callMethod("_getHandler", "s", "ShowContextMenu");
		if (f.get() && !f.isNone()) {

			PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
			PyDTObject msg = msgtype.call("");
			PyDTDict dict(((PyMFCWndMsgType::TypeInstance*)msg.get())->x_attr, false);

			dict.setItem("default", (dwID & (0x1 << CONTEXT_MENU_DEFAULT))?1:0);
			dict.setItem("control", (dwID & (0x1 << CONTEXT_MENU_CONTROL))?1:0);
			dict.setItem("table", (dwID & (0x1 << CONTEXT_MENU_TABLE))?1:0);
			dict.setItem("textselect", (dwID & (0x1 << CONTEXT_MENU_TEXTSELECT))?1:0);
			dict.setItem("anchor", (dwID & (0x1 << CONTEXT_MENU_ANCHOR))?1:0);
			dict.setItem("unknown", (dwID & (0x1 << CONTEXT_MENU_UNKNOWN))?1:0);

			MSHTML::IHTMLElement2Ptr src = pdispReserved;
			if (src) {
				PyDTObject srcelem(PyMFC_IHTMLElement::newInstance(src), true);
				dict.setItem("srcElement", srcelem);
			}
			else {
				dict.setItem("srcElement", PyDTNone());
			}
	
			IOleCommandTargetPtr ct = pcmdtReserved;
			PyDTObject target(PyMFCOleCommandTarget::newInstance(ct), true);
			target.incRef();
			ct->AddRef();

			dict.setItem("cmdTarget", target);

			PyDTObject ret = f.call("O", msg.get());
			
			if (ret.isTrue()) {
				return S_OK;
			}
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
	}

	return S_FALSE;
}


class PyMFCWebCtrlParser: public PyMFCMsgParser {
public:
	PyMFCWebCtrlParser(){}
protected:
	virtual void parse_notify(CWnd *wnd, DWORD msg, WPARAM wParam, LPARAM lParam, PyDTDict &ret) {
	}
};

void *new_WebCtrl(PyObject *obj) {
	PyMFC_PROLOGUE(new_WebCtrl);

	return static_cast<CWnd*>(new PyMFCWnd<PyMFCWebCtrl, PyMFCWebCtrlParser>(obj));

	PyMFC_EPILOGUE(0);
}

int PyMFCWebCtrl_Navigate(void *o, TCHAR *url) {
	PyMFC_PROLOGUE(CWebCtrl_Navigate);

	PyMFCWebCtrl *web= getCWnd<PyMFCWebCtrl >(o);
	{
		PyMFCLeavePython lp;
		
		IOleInPlaceObjectPtr ip = web->m_ie.GetControlUnknown();
		ip->UIDeactivate();

		web->m_ie.Navigate(url, NULL, NULL, NULL, NULL);
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int PyMFCWebCtrl_UIDeactivate(void *o) {
	PyMFC_PROLOGUE(PyMFCWebCtrl_UIDeactivate);

	PyMFCWebCtrl *web= getCWnd<PyMFCWebCtrl >(o);
	HRESULT hr;
	{
		PyMFCLeavePython lp;
		
		IOleInPlaceObjectPtr ip = web->m_ie.GetControlUnknown();
		hr = ip->UIDeactivate();
	}

	if (FAILED(hr)) {
		throw PyMFC_WIN32ERRCODE(hr);
	}
	return TRUE;

	PyMFC_EPILOGUE(0);
}

PyObject *PyMFCWebCtrl_GetDocument(void *o) {
	PyMFC_PROLOGUE(PyMFCWebCtrl_GetDocument);

	PyMFCWebCtrl *web= getCWnd<PyMFCWebCtrl >(o);
	{
		MSHTML::IHTMLDocument2Ptr doc = web->m_ie.get_Document();
		MSHTML::IHTMLElement2Ptr d = doc;
		if (doc) {
			return PyMFC_IHTMLDocument::newInstance(doc);
		}
		else {
			PyMFC_RETNONE();
		}
	}
	PyMFC_EPILOGUE(0);
}

int PyMFCWebCtrl_ExecCommand(void *o, DWORD cmdid) {
	PyMFC_PROLOGUE(PyMFCWebCtrl_ExecCommand);

	PyMFCWebCtrl *web= getCWnd<PyMFCWebCtrl >(o);
	{
		PyMFCLeavePython lp;
		web->m_ie.ExecWB(cmdid, OLECMDEXECOPT_DODEFAULT, NULL, NULL);
	}
	return TRUE;
	PyMFC_EPILOGUE(0);
}

PyObject *PyMFCWebCtrl_Deactivate(void *o) {
	PyMFC_PROLOGUE(PyMFCWebCtrl_Deactivate);

	PyMFCWebCtrl *web= getCWnd<PyMFCWebCtrl >(o);
	{
		MSHTML::IHTMLDocument2Ptr doc = web->m_ie.get_Document();
		MSHTML::IHTMLElement2Ptr d = doc;
		if (doc) {
			return PyMFC_IHTMLDocument::newInstance(doc);
		}
		else {
			PyMFC_RETNONE();
		}
	}
	PyMFC_EPILOGUE(0);
}

BOOL PyMFCWndEventSink::callHandler(IDispatch *disp, const char *eventname) {
	PyDTObject handler = getEventHandler(eventname);
	if (!handler.isTrue()) 
		return TRUE;

	PyDTObject msgtype(PyMFCWndMsgType::MSGTYPE, false);
	PyDTObject msg = msgtype.call("");
	PyDTDict dict(((PyMFCWndMsgType::TypeInstance*)msg.get())->x_attr, false);

	MSHTML::IHTMLEventObjPtr ev = disp;
	dict.setItem("keyCode", ev->keyCode);
	dict.setItem("altKey", ev->altKey);
	dict.setItem("shiftKey", ev->shiftKey);
	dict.setItem("ctrlKey", ev->ctrlKey);
	MSHTML::IHTMLElement2Ptr src = ev->srcElement;
	if (src) {
		PyDTObject srcelem(PyMFC_IHTMLElement::newInstance(src), true);
		dict.setItem("srcElement", srcelem);
	}
	else {
		dict.setItem("srcElement", PyDTNone());
	}
	
	try {
		PyDTObject retval = handler.call("O", msg.get());
		if (!retval.get()) {
			PyErr_Print();
			return FALSE;
		}

		try {
			DWORD ret = retval.getULong();
			return ret;
		}
		catch (PyDTException &) {
			PyDTString func_repr(handler.repr());
			std::string err(func_repr.asString());
			err += "\nshould return None or integer";
			PyErr_SetString(PyExc_ValueError, err.c_str());
			PyErr_Print();
			return FALSE;
		}
	}
	catch (PyDTException &exc) {
		exc.setError();
		PyErr_Print();
		return FALSE;
	}
}

BOOL PyMFCWndEventSink::OnKeyPress(IDispatch *disp) {
	PyMFCEnterPython e;
	{
		return callHandler(disp, "KeyPress");
	}
}

BOOL PyMFCWndEventSink::OnClick(IDispatch *disp) {
	PyMFCEnterPython e;
	{
		return callHandler(disp, "Click");
	}
}

BOOL PyMFCWndEventSink::OnDragStart(IDispatch *disp) {
	PyMFCEnterPython e;
	{
		return callHandler(disp, "DragStart");
	}
}

PyObject *PyMFC_IHTMLElement::getDocument(TypeInstance *obj) {
	PyMFC_PROLOGUE("PyMFC_IHTMLElement::getDocument");
	
	MSHTML::IHTMLElementPtr elem;
	MSHTML::IHTMLDocumentPtr doc;
	{
		PyMFCLeavePython clp;
		elem = *(obj->elem);
		doc = elem->document;
	}

	if (doc) {
		return PyMFC_IHTMLDocument::newInstance(doc);
	}
	else {
		PyMFC_RETNONE();
	}

	PyMFC_EPILOGUE(NULL);
}


PyObject *PyMFC_IHTMLElement::getParent(TypeInstance *obj) {
	PyMFC_PROLOGUE("PyMFC_IHTMLElement::getParent");
	
	MSHTML::IHTMLElementPtr elem, parent;
	{
		PyMFCLeavePython clp;
		elem = *(obj->elem);
		parent = elem->parentElement;
	}

	if (parent) {
		return PyMFC_IHTMLElement::newInstance(parent);
	}
	else {
		PyMFC_RETNONE();
	}

	PyMFC_EPILOGUE(NULL);
}



void init_webobjs(PyObject *module) {
	PyDTModule m(module, false);
	PyDTRegType(m, "_pymfclib.IHTMLDocument", "IHTMLDocument", PyMFC_IHTMLDocument::def_elemtype);
	PyDTRegType(m, "_pymfclib.IHTMLElement", "IHTMLElement", PyMFC_IHTMLElement::def_elemtype);
	PyDTRegType(m, "_pymfclib.IOleCommandTarget", "IOleCommandTarget", PyMFCOleCommandTarget::def_olecmdtarget);
}

