// PyMFC_CustomProtocol.h : CPyMFC_CustomProtocol の宣言

#pragma once
#include "resource.h"       // メイン シンボル

#include "pymfclib_i.h"


#if defined(_WIN32_WCE) && !defined(_CE_DCOM) && !defined(_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA)
#error "DCOM の完全サポートを含んでいない Windows Mobile プラットフォームのような Windows CE プラットフォームでは、単一スレッド COM オブジェクトは正しくサポートされていません。ATL が単一スレッド COM オブジェクトの作成をサポートすること、およびその単一スレッド COM オブジェクトの実装の使用を許可することを強制するには、_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA を定義してください。ご使用の rgs ファイルのスレッド モデルは 'Free' に設定されており、DCOM Windows CE 以外のプラットフォームでサポートされる唯一のスレッド モデルと設定されていました。"
#endif



// CPyMFC_CustomProtocol

/* 
   Based on `From Asynchronous Pluggable Protocol Handler for data: URLs'
   By Rama Krishna Vavilala(http://www.codeproject.com/KB/IP/DataProtocol.aspx).
*/ 

class ATL_NO_VTABLE CPyMFC_CustomProtocol:
	public CComObjectRootEx<CComSingleThreadModel>,
	public CComCoClass<CPyMFC_CustomProtocol, &CLSID_PyMFC_CustomProtocol>,
	public IPyMFC_CustomProtocol,
	public IInternetProtocol
{
public:
	CPyMFC_CustomProtocol()
	{
	}
	static PyObject **mapfunc;

	

BEGIN_COM_MAP(CPyMFC_CustomProtocol)
	COM_INTERFACE_ENTRY(IPyMFC_CustomProtocol)
	COM_INTERFACE_ENTRY(IInternetProtocol)
	COM_INTERFACE_ENTRY(IInternetProtocolRoot)
END_COM_MAP()

	DECLARE_PROTECT_FINAL_CONSTRUCT()

	HRESULT FinalConstruct()
	{
		return S_OK;
	}

	void FinalRelease()
	{
	}

public:
// IInternetProtocol interface
public:
    STDMETHOD(Start)(
            LPCWSTR szUrl,
            IInternetProtocolSink *pIProtSink,
            IInternetBindInfo *pIBindInfo,
            DWORD grfSTI,
            DWORD dwReserved);
    STDMETHOD(Continue)(PROTOCOLDATA *pStateInfo);
    STDMETHOD(Abort)(HRESULT hrReason,DWORD dwOptions);
    STDMETHOD(Terminate)(DWORD dwOptions);
    STDMETHOD(Suspend)();
    STDMETHOD(Resume)();
    STDMETHOD(Read)(void *pv,ULONG cb,ULONG *pcbRead);
    STDMETHOD(Seek)(
            LARGE_INTEGER dlibMove,
            DWORD dwOrigin,
            ULARGE_INTEGER *plibNewPosition);
    STDMETHOD(LockRequest)(DWORD dwOptions);
    STDMETHOD(UnlockRequest)();


	bool doCallback(LPCWSTR url);


private:
	CComPtr<IInternetProtocolSink> m_spSink;
	CComPtr<IInternetBindInfo> m_spBindInfo;
	DWORD m_dwPos;
	CComBSTR m_mimetype;
	CAtlArray<BYTE> m_src;


};

//OBJECT_ENTRY_AUTO(__uuidof(PyMFC_CustomProtocol), CPyMFC_CustomProtocol)


class ATL_NO_VTABLE CPyMFC_CustomProtocolFactory :
	public CComClassFactory
{
public:
	STDMETHOD(CreateInstance)(LPUNKNOWN pUnkOuter, REFIID riid, void** ppvObj) {
		CComObject<CPyMFC_CustomProtocol> *cp;
		HRESULT hr = CComObject<CPyMFC_CustomProtocol>::CreateInstance(&cp);
		if (FAILED(hr )) {
			return hr;
		}
		hr = cp->QueryInterface(riid, ppvObj);
		if (FAILED(hr)) {
			delete cp;
		}
		return hr;
	}
 

};
