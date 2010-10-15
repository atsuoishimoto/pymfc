// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMWIN32FUNCS_H
#define PYMWIN32FUNCS_H

#include "pymfcdefs.h"

#ifdef __cplusplus
extern "C" {
#else
#	pragma warning(disable:4101 4102 4290)
#   include <windows.h>
#endif

#ifndef __cplusplus
PYMFC_API PyObject *PyMFCPtr_FromVoidPtr(void *h);
PYMFC_API void * PyMFCPtr_AsVoidPtr(PyObject *obj);
PYMFC_API int PyMFCPtr_IsPtr(PyObject *obj);
#endif

#ifndef __cplusplus
PYMFC_API PyObject *PyMFCHandle_FromHandle(HANDLE h);
PYMFC_API HANDLE PyMFCHandle_AsHandle(PyObject *obj);
PYMFC_API int PyMFCHandle_IsHandle(PyObject *obj);
#endif



PYMFC_API long pymGetLastError();
PYMFC_API PyObject *pymFormatMessage(long err);
PYMFC_API void pymRaiseWin32Err();
PYMFC_API void pymRaiseWin32Errcode(HRESULT hr);

PYMFC_API HIMC pymImmGetContext(HWND hWnd);
PYMFC_API BOOL pymImmReleaseContext(HWND hWnd, HIMC hIMC);
PYMFC_API BOOL pymImmSetOpenStatus(HIMC hIMC, int fopen);
PYMFC_API BOOL pymImmGetOpenStatus(HIMC hIMC);
PYMFC_API BOOL pymImmSetCompositionWindow(HIMC hIMC, COMPOSITIONFORM *lpCompForm);
PYMFC_API BOOL pymImmSetCompositionFont(HIMC hIMC, LOGFONT *lplf);
PYMFC_API long pymImmGetCompositionString(HIMC hIMC, long dwIndex, void *lpBuf, long dwBufLen);

PYMFC_API BOOL pymOpenClipboard(HWND hWndNewOwner);
PYMFC_API HANDLE pymGetClipboardData(UINT uFormat);
PYMFC_API BOOL pymIsClipboardFormatAvailable(UINT format);
PYMFC_API BOOL pymCloseClipboard();
PYMFC_API HANDLE pymSetClipboardData(UINT uFormat, HANDLE hMem);
PYMFC_API BOOL pymEmptyClipboard();

PYMFC_API BOOL pymPostMessage(HWND hWnd, UINT Msg, WPARAM wParam, LPARAM lParam);
PYMFC_API BOOL pymPostThreadMessage(DWORD idThread, UINT Msg, WPARAM wParam, LPARAM lParam);

PYMFC_API int pymMessageBox(HWND hWnd, TCHAR *lpText, TCHAR *lpCaption, UINT uType);
 
PYMFC_API BOOL pymShGetSpecialFolderPath(HWND hWnd, TCHAR *buf, int nFolder, BOOL fCreate);
PYMFC_API BOOL pymShellExecute(SHELLEXECUTEINFO *se);

PYMFC_API DWORD pymWaitForMultipleObjectsEx(DWORD nCount, HANDLE* lpHandles, BOOL bWaitAll, DWORD dwMilliseconds, BOOL bAlertable);


#ifdef __cplusplus
}
#endif

#endif
