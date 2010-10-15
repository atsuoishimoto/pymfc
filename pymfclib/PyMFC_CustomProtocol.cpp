// PyMFC_CustomProtocol.cpp : CPyMFC_CustomProtocol ‚ÌŽÀ‘•

#include "stdafx.h"

#include "pymwndbase.h"

#include "pymwnd.h"
#include "pymwin32funcs.h"
#include "pymutils.h"

#include "PyMFC_CustomProtocol.h"

// CPyMFC_CustomProtocol
PyObject **CPyMFC_CustomProtocol::mapfunc;

STDMETHODIMP CPyMFC_CustomProtocol::Start(
	LPCWSTR szUrl,
	IInternetProtocolSink *pIProtSink,
	IInternetBindInfo *pIBindInfo,
	DWORD grfSTI,
	DWORD dwReserved)
{
	HRESULT hr = S_OK;
	
	bool ret = doCallback(szUrl);
	if (!ret) {
		return INET_E_CANNOT_CONNECT;
	}

	pIProtSink->ReportProgress(BINDSTATUS_FINDINGRESOURCE, szUrl);
	pIProtSink->ReportProgress(BINDSTATUS_CONNECTING, szUrl);
	pIProtSink->ReportProgress(BINDSTATUS_SENDINGREQUEST, szUrl);
	pIProtSink->ReportProgress(BINDSTATUS_VERIFIEDMIMETYPEAVAILABLE, m_mimetype);
	pIProtSink->ReportData(BSCF_FIRSTDATANOTIFICATION, 0, 1000);
	pIProtSink->ReportData(BSCF_LASTDATANOTIFICATION | BSCF_DATAFULLYAVAILABLE, 1000, 1000);
		
/*	}
	else
	{
		if (grfSTI & PI_PARSE_URL)
			hr = S_FALSE;
	}
*/
	return hr;
}

STDMETHODIMP CPyMFC_CustomProtocol::Continue(PROTOCOLDATA *pStateInfo)
{
	return S_OK;
}

STDMETHODIMP CPyMFC_CustomProtocol::Abort(HRESULT hrReason,DWORD dwOptions)
{
	return S_OK;
}

STDMETHODIMP CPyMFC_CustomProtocol::Terminate(DWORD dwOptions)
{
	return S_OK;
}

STDMETHODIMP CPyMFC_CustomProtocol::Suspend()
{
	return E_NOTIMPL;
}

STDMETHODIMP CPyMFC_CustomProtocol::Resume()
{
	return E_NOTIMPL;
}

STDMETHODIMP CPyMFC_CustomProtocol::LockRequest(DWORD dwOptions)
{
	ATLTRACE(_T("LockRequest\n"));


	return S_OK;
}

STDMETHODIMP CPyMFC_CustomProtocol::UnlockRequest()
{
	ATLTRACE(_T("UnlockRequest\n"));
	
	//m_dwPos = 0;
	return S_OK;
}

//const char *html = "<html> <body> <A href='#today'>link</A> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> <A NAME='today'><H2>===============================================</H2>";

STDMETHODIMP CPyMFC_CustomProtocol::Read(void *pv, ULONG cb, ULONG *pcbRead)
{
	ATLTRACE(_T("READ  - requested=%8d\n"), cb);
	
	HRESULT hr = S_OK;
	
	size_t size = m_src.GetCount();
	if (m_dwPos >= size)
		return S_FALSE;

	const BYTE *pbData = m_src.GetData()+m_dwPos;
	DWORD cbAvail = min(cb, size - m_dwPos);

	memcpy_s(pv, cbAvail, pbData, cbAvail);
	m_dwPos += cbAvail;
	*pcbRead = cbAvail;
	
	return hr;
}

STDMETHODIMP CPyMFC_CustomProtocol::Seek(
	LARGE_INTEGER dlibMove,
	DWORD dwOrigin,
	ULARGE_INTEGER *plibNewPosition)
{
	return E_NOTIMPL;
}

bool CPyMFC_CustomProtocol::doCallback(LPCWSTR url) {
	PyMFCEnterPython e;
	{
		if (!mapfunc | !*mapfunc) {
			return false;
		}

		PyDTObject f(*mapfunc, true);
		f.incRef();
		
		PyDTUnicode s(url);
		try {
			PyDTObject ret = f.call("O", s.get());
			if (!ret.isTrue()) {
				return false;
			}
			m_dwPos = 0;
	
			PyDTDict d(ret);
			PyDTUnicode mimetype(d.getItem("mimetype"));

			m_mimetype = mimetype.asUnicode();
			PyDTString src(d.getItem("src"));
			
			m_src.SetCount(src.size());
			memcpy(m_src.GetData(), src.asString(), src.size());

		}
		catch (PyDTException &exc) {
			exc.setError();
			PyErr_Print();
			return false;
		}

	}
	return true;
}



