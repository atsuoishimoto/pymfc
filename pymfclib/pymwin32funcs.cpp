// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"

#include "pymwndbase.h"
#include "pymwin32funcs.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif



void pymRaiseWin32Err() {
	PyMFC_PROLOGUE(pymRaiseWin32Err);
		
	throw PyMFC_WIN32ERR();
	
	PyMFC_VOID_EPILOGUE();
}

void pymRaiseWin32Errcode(HRESULT hr) {
	PyMFC_PROLOGUE(pymRaiseWin32Errcode);
		
	throw PyMFC_WIN32ERRCODE(hr);
	
	PyMFC_VOID_EPILOGUE();
}

long pymGetLastError() {
	PyMFC_PROLOGUE(pymFormatMessage);

	return GetLastError();
	
	PyMFC_EPILOGUE(IMM_ERROR_GENERAL);
}

PyObject *pymFormatMessage(long err) {
	PyMFC_PROLOGUE(pymFormatMessage);

	char *buf;
	DWORD ret = FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
			NULL, err, LANG_NEUTRAL,
			(LPTSTR)&buf,
			0,
			NULL);
	
	if (ret) {
		PyObject *ret = PyString_FromString(buf);
		LocalFree(buf);
		return ret;
	}
	return NULL;

	PyMFC_EPILOGUE(0);
}


HIMC pymImmGetContext(HWND hWnd) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmGetContext(hWnd);
	}
	PyMFC_EPILOGUE(0);
}
BOOL pymImmReleaseContext(HWND hWnd, HIMC hIMC) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmReleaseContext(hWnd, hIMC);
	}
	PyMFC_EPILOGUE(0);
}
BOOL pymImmSetOpenStatus(HIMC hIMC, int fopen) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmSetOpenStatus(hIMC, fopen);
	}
	PyMFC_EPILOGUE(0);
}
BOOL pymImmGetOpenStatus(HIMC hIMC) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmGetOpenStatus(hIMC);
	}
	PyMFC_EPILOGUE(0);
}
BOOL pymImmSetCompositionWindow(HIMC hIMC, COMPOSITIONFORM *lpCompForm) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmSetCompositionWindow(hIMC, lpCompForm);
	}
	PyMFC_EPILOGUE(0);
}
BOOL pymImmSetCompositionFont(HIMC hIMC, LOGFONT *lplf) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		return ImmSetCompositionFont(hIMC, lplf);
	}
	PyMFC_EPILOGUE(0);
}
long pymImmGetCompositionString(HIMC hIMC, long dwIndex, void *lpBuf, long dwBufLen) {
	PyMFC_PROLOGUE(pymFormatMessage);
	{
		PyMFCLeavePython lp;
		LONG ret = ImmGetCompositionString(hIMC, dwIndex, lpBuf, dwBufLen);
		if (ret == IMM_ERROR_NODATA || ret == IMM_ERROR_GENERAL) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(-1);
}



BOOL pymOpenClipboard(HWND hWndNewOwner) {
	PyMFC_PROLOGUE(pymOpenClipboard);
	{
		PyMFCLeavePython lp;
		if (!OpenClipboard(hWndNewOwner)) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

HANDLE pymGetClipboardData(UINT uFormat) {
	PyMFC_PROLOGUE(pymGetClipboardData);
	{
		PyMFCLeavePython lp;
		return GetClipboardData(uFormat);
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymIsClipboardFormatAvailable(UINT format) {
	PyMFC_PROLOGUE(pymIsClipboardFormatAvailable);
	{
		PyMFCLeavePython lp;
		BOOL ret = IsClipboardFormatAvailable(format);
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymCloseClipboard() {
	PyMFC_PROLOGUE(pymCloseClipboard);
	{
		PyMFCLeavePython lp;
		if (!CloseClipboard()) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

HANDLE pymSetClipboardData(UINT uFormat, HANDLE hMem) {
	PyMFC_PROLOGUE(pymSetClipboardData);
	{
		PyMFCLeavePython lp;
		HANDLE ret = SetClipboardData(uFormat, hMem);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return ret;
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymEmptyClipboard() {
	PyMFC_PROLOGUE(pymEmptyClipboard);
	{
		PyMFCLeavePython lp;
		if (!EmptyClipboard()) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymPostMessage(HWND hWnd, UINT Msg, WPARAM wParam, LPARAM lParam) {
	PyMFC_PROLOGUE(pymPostMessage);
	{
		PyMFCLeavePython lp;
		BOOL ret = PostMessage(hWnd, Msg, wParam, lParam);
		if (!ret) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymPostThreadMessage(DWORD idThread, UINT Msg, WPARAM wParam, LPARAM lParam) {
	PyMFC_PROLOGUE(pymPostThreadMessage);
	{
		PyMFCLeavePython lp;
		if (!PostThreadMessage(idThread, Msg, wParam, lParam)) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}


int pymMessageBox(HWND hWnd, TCHAR *lpText, TCHAR *lpCaption, UINT uType) {
	PyMFC_PROLOGUE(pymMessageBox);
	{
		PyMFCLeavePython lp;
		return MessageBox(hWnd, lpText, lpCaption, uType);
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymShGetSpecialFolderPath(HWND hWnd, TCHAR *buf, int nFolder, BOOL fCreate) {
	PyMFC_PROLOGUE(pymShGetSpecialFolderPath);
	{
		PyMFCLeavePython lp;
		if (!SHGetSpecialFolderPath(hWnd, buf, nFolder, fCreate)) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

BOOL pymShellExecute(SHELLEXECUTEINFO *se) {
	PyMFC_PROLOGUE(pymShellExecute);
	{
		PyMFCLeavePython lp;
		if (!ShellExecuteEx(se)) {
			throw PyMFC_WIN32ERR();
		}
		return TRUE;
	}
	PyMFC_EPILOGUE(0);
}

DWORD pymWaitForMultipleObjectsEx(DWORD nCount, HANDLE* lpHandles, BOOL bWaitAll, DWORD dwMilliseconds, BOOL bAlertable) {
	PyMFC_PROLOGUE(pymShellExecute);
	{
		PyMFCLeavePython lp;
		DWORD ret = WaitForMultipleObjectsEx(nCount, lpHandles, bWaitAll, dwMilliseconds, bAlertable);

		if (ret == WAIT_FAILED) {
			throw PyMFC_WIN32ERR();
		}

		return ret;
	}
	PyMFC_EPILOGUE(0);
}
