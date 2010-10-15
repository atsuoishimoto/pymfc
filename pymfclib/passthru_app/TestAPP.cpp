// TestAPP.cpp: implementation of the CTestAPP class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "TestAPP.h"

STDMETHODIMP CTestSink::BeginningTransaction(
	/* [in] */ LPCWSTR szURL,
	/* [in] */ LPCWSTR szHeaders,
	/* [in] */ DWORD dwReserved,
	/* [out] */ LPWSTR *pszAdditionalHeaders)
{
	USES_CONVERSION;

	if (pszAdditionalHeaders)
	{
		*pszAdditionalHeaders = 0;
	}

	CComPtr<IHttpNegotiate> spHttpNegotiate;
	QueryServiceFromClient(&spHttpNegotiate);
	HRESULT hr = spHttpNegotiate ?
		spHttpNegotiate->BeginningTransaction(szURL, szHeaders,
			dwReserved, pszAdditionalHeaders) :
		S_OK;

	return hr;
	CComPtr<IWinInetHttpInfo> spWinInetHttpInfo;
	HRESULT hrTemp = m_spTargetProtocol->QueryInterface(IID_IWinInetHttpInfo,
		reinterpret_cast<void**>(&spWinInetHttpInfo));
	ATLASSERT(SUCCEEDED(hrTemp));
	DWORD size = 0;
	DWORD flags = 0;
	hrTemp = spWinInetHttpInfo->QueryInfo(
		HTTP_QUERY_RAW_HEADERS_CRLF | HTTP_QUERY_FLAG_REQUEST_HEADERS,
		0, &size, &flags, 0);
	ATLASSERT(SUCCEEDED(hrTemp));
	std::vector<char> vecBuf(size);
	LPSTR pbuf = &vecBuf.front();
	hrTemp = spWinInetHttpInfo->QueryInfo(
		HTTP_QUERY_RAW_HEADERS_CRLF | HTTP_QUERY_FLAG_REQUEST_HEADERS,
		pbuf, &size, &flags, 0);
	ATLASSERT(SUCCEEDED(hrTemp));

	tstring url = (szURL ? W2CT(szURL) : _T("???"));
	tstring request = _T("(Request for ") + url + _T(")\r\n");
	m_redirects = _T("(Response for ") + url + _T(")\r\n");

	request += A2CT(pbuf);
	EnsureCRLF(request);

	if (szHeaders)
	{
		request += W2CT(szHeaders);
		EnsureCRLF(request);
	}

	if (SUCCEEDED(hr) && pszAdditionalHeaders && *pszAdditionalHeaders)
	{
		request += W2CT(*pszAdditionalHeaders);
		EnsureCRLF(request);
	}
	request += _T("\r\n");
	return hr;
}

STDMETHODIMP CTestSink::OnResponse(
	/* [in] */ DWORD dwResponseCode,
	/* [in] */ LPCWSTR szResponseHeaders,
	/* [in] */ LPCWSTR szRequestHeaders,
	/* [out] */ LPWSTR *pszAdditionalRequestHeaders)
{
	USES_CONVERSION;

	if (pszAdditionalRequestHeaders)
	{
		*pszAdditionalRequestHeaders = 0;
	}

	CComPtr<IHttpNegotiate> spHttpNegotiate;
	QueryServiceFromClient(&spHttpNegotiate);
	HRESULT hr = spHttpNegotiate ?
		spHttpNegotiate->OnResponse(dwResponseCode, szResponseHeaders,
			szRequestHeaders, pszAdditionalRequestHeaders) :
		S_OK;

	tstring response = m_redirects;
	response += W2CT(szResponseHeaders);
	EnsureCRLF(response);
	if (szRequestHeaders)
	{
		response += _T("(Repeat request)\r\n");
		response += W2CT(szRequestHeaders);
		EnsureCRLF(response);
		if (SUCCEEDED(hr) && pszAdditionalRequestHeaders &&
			*pszAdditionalRequestHeaders)
		{
			response += W2CT(*pszAdditionalRequestHeaders);
			EnsureCRLF(response);
		}
	}
	response += _T("\r\n");
	TRACE(response.c_str());
	return hr;
}

STDMETHODIMP CTestSink::ReportProgress(
	/* [in] */ ULONG ulStatusCode,
	/* [in] */ LPCWSTR szStatusText)
{
	USES_CONVERSION;

	ATLASSERT(m_spInternetProtocolSink != 0);
	HRESULT hr = m_spInternetProtocolSink ?
		m_spInternetProtocolSink->ReportProgress(ulStatusCode, szStatusText) :
		S_OK;
	if (ulStatusCode == BINDSTATUS_REDIRECTING)
	{
		tstring url = (szStatusText ? W2CT(szStatusText) : _T("???"));
		m_redirects += _T("(Redirected to ") + url + _T(")\r\n");
	}
	return hr;
}

void CTestSink::EnsureCRLF(tstring& str)
{
	tstring::size_type len = str.length();
	if (len >= 4 && str.substr(len - 4) == _T("\r\n\r\n"))
	{
		str.erase(len - 2);
	}
	else if (len < 2 || str.substr(len - 2) != _T("\r\n"))
	{
		str += _T("\r\n");
	}
}
