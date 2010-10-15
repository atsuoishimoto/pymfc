// TestAPP.h: interface for the CTestAPP class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_TESTAPP_H__3D916FFB_17FD_424F_B91D_4CF63A10DF49__INCLUDED_)
#define AFX_TESTAPP_H__3D916FFB_17FD_424F_B91D_4CF63A10DF49__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "ProtocolImpl.h"

#include <string>
typedef std::basic_string<TCHAR> tstring;
#include <vector>

class CTestAPP;

class CTestSink :
	public PassthroughAPP::CInternetProtocolSinkWithSP<CTestSink>
//	public IHttpNegotiate
{
	typedef PassthroughAPP::CInternetProtocolSinkWithSP<CTestSink> BaseClass;
public:

//	BEGIN_COM_MAP(CTestSink)
//		COM_INTERFACE_ENTRY(IHttpNegotiate)
//		COM_INTERFACE_ENTRY_CHAIN(BaseClass)
//	END_COM_MAP()

//	BEGIN_SERVICE_MAP(CTestSink)
//		SERVICE_ENTRY(IID_IHttpNegotiate)
//	END_SERVICE_MAP()

	STDMETHODIMP BeginningTransaction(
		/* [in] */ LPCWSTR szURL,
		/* [in] */ LPCWSTR szHeaders,
		/* [in] */ DWORD dwReserved,
		/* [out] */ LPWSTR *pszAdditionalHeaders);

	STDMETHODIMP OnResponse(
		/* [in] */ DWORD dwResponseCode,
		/* [in] */ LPCWSTR szResponseHeaders,
		/* [in] */ LPCWSTR szRequestHeaders,
		/* [out] */ LPWSTR *pszAdditionalRequestHeaders);

	STDMETHODIMP ReportProgress(
		/* [in] */ ULONG ulStatusCode,
		/* [in] */ LPCWSTR szStatusText);

private:
	tstring m_redirects;

	static void EnsureCRLF(tstring& str);
};

class TestStartPolicy:public PassthroughAPP::CustomSinkStartPolicy<CTestAPP, CTestSink> {
};

class CTestAPP :
	public PassthroughAPP::CInternetProtocol<TestStartPolicy>
{
};

#endif // !defined(AFX_TESTAPP_H__3D916FFB_17FD_424F_B91D_4CF63A10DF49__INCLUDED_)
