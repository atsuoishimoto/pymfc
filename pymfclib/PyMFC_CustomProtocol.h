// PyMFC_CustomProtocol.h : CPyMFC_CustomProtocol �̐錾

#pragma once
#include "resource.h"       // ���C�� �V���{��

#include "pymfclib_i.h"


#if defined(_WIN32_WCE) && !defined(_CE_DCOM) && !defined(_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA)
#error "DCOM �̊��S�T�|�[�g���܂�ł��Ȃ� Windows Mobile �v���b�g�t�H�[���̂悤�� Windows CE �v���b�g�t�H�[���ł́A�P��X���b�h COM �I�u�W�F�N�g�͐������T�|�[�g����Ă��܂���BATL ���P��X���b�h COM �I�u�W�F�N�g�̍쐬���T�|�[�g���邱�ƁA����т��̒P��X���b�h COM �I�u�W�F�N�g�̎����̎g�p�������邱�Ƃ���������ɂ́A_CE_ALLOW_SINGLE_THREADED_OBJECTS_IN_MTA ���`���Ă��������B���g�p�� rgs �t�@�C���̃X���b�h ���f���� 'Free' �ɐݒ肳��Ă���ADCOM Windows CE �ȊO�̃v���b�g�t�H�[���ŃT�|�[�g�����B��̃X���b�h ���f���Ɛݒ肳��Ă��܂����B"
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
