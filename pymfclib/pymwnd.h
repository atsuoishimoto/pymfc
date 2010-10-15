// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMFCWND_H
#define PYMFCWND_H

#include "tchar.h"
#include <windows.h>
#include <CommCtrl.h>

#include "pymfcdefs.h"

#ifdef __cplusplus
extern "C" {
#else
#	pragma warning(disable:4101 4102)
#endif


PYMFC_API const TCHAR *pymRegisterWndClass(long nClassStyle, HANDLE hCursor, HANDLE hbrBackground, HANDLE hIcon);
PYMFC_API void *new_CWnd(PyObject *pyobj);
PYMFC_API int CWnd_Delete(void *o);
PYMFC_API int CWnd_Lock(void *o, int lock);

PYMFC_API HWND CWnd_Hwnd(void *o);

PYMFC_API int CWnd_Create(void *o, long dwExStyle, TCHAR *lpszClassName, 
	TCHAR *lpszWindowName, long dwStyle, int x, int y, int nWidth, 
	int nHeight, HWND hwndParent, HMENU nIDorHMenu);
PYMFC_API int CWnd_Destroy(void *o);

//PYMFC_API long CWnd_DefWndProc(void *o, int message, WPARAM wParam, LPARAM lParam, long ret);
PYMFC_API long CWnd_DefWndProc(void *o, PyObject *msg);

PYMFC_API int CWnd_SubclassWindow(void *o, HWND hwnd, int temp);
PYMFC_API HWND CWnd_UnsubclassWindow(void *o);

PYMFC_API PyObject *CWnd_FromHandle(HWND hwnd);

PYMFC_API HWND CWnd_GetDlgItem(void *o, long childid);

PYMFC_API PyObject *CWnd_GetNextDlgTabItem(void *o, HWND hwnd, int prev);

PYMFC_API int CWnd_SetMenu(void *o, HMENU hMenu);
PYMFC_API int CWnd_DrawMenuBar(void *o);

PYMFC_API int CWnd_SetActiveWindow(void *o);
PYMFC_API BOOL CWnd_SetForegroundWindow(void *o);

PYMFC_API PyObject *CWnd_GetActiveWindow();
PYMFC_API PyObject *CWnd_GetForegroundWindow();

PYMFC_API BOOL CWnd_SetLayeredWindowAttributes(void *o, COLORREF crKey, BYTE bAlpha, DWORD dwFlags);


PYMFC_API PyObject *CWnd_GetFocus();
PYMFC_API int CWnd_SetFocus(void *o);

PYMFC_API BOOL CWnd_SetCapture(void *o);
PYMFC_API BOOL CWnd_ReleaseCapture();


PYMFC_API HFONT CWnd_GetFont(void * o);
PYMFC_API int CWnd_SetFont(void * o, HFONT hfont, int redraw);


PYMFC_API long CWnd_SendMessage_L_L_L(void *o, int msg, WPARAM wparam, LPARAM lparam);
PYMFC_API long CWnd_SendMessage_L_L_L_0(void *o, int msg, WPARAM wparam, LPARAM lparam);
PYMFC_API long CWnd_SendMessage_L_L_L_m1(void *o, int msg, WPARAM wparam, LPARAM lparam);
PYMFC_API long CWnd_SendMessage_L_P_L(void * o, int msg, WPARAM wparam, void* lparam);
PYMFC_API long CWnd_SendMessage_L_P_L_0(void *o, int msg, WPARAM wparam, void* lparam);
PYMFC_API long CWnd_SendMessage_L_P_L_m1(void *o, int msg, WPARAM wparam, void* lparam);
PYMFC_API long CWnd_SendMessage_P_P_L(void *o, int msg, void* wparam, void* lparam);



PYMFC_API int CWnd_ShowWindow(void *o, int uFlags);
PYMFC_API int CWnd_SetWindowPos(void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags);
PYMFC_API int CWnd_SetWindowRgn(void *o, HRGN rgn, BOOL redraw);
PYMFC_API HDWP CWnd_BeginDeferWindowPos(long n);
PYMFC_API BOOL CWnd_EndDeferWindowPos(HDWP hdwp);
PYMFC_API HDWP CWnd_DeferWindowPos(HDWP hdwp, void *o, HWND hWndInsertAfter, int X, int Y, int cx, int cy, int uFlags);
PYMFC_API int CWnd_CalcWindowRect(void *o, RECT *rc);

PYMFC_API int CWnd_EnableWindow(void *o, int enable);


PYMFC_API int CWnd_ScrollWindowEx(void *o, int dx, int dy,
  RECT *prcScroll, RECT *prcClip,
  HRGN hrgnUpdate, RECT *prcUpdate,  
  int erase, int invalidate, int scrollchildren, int smooth);

PYMFC_API int CWnd_ShowScrollBar(void *o, int horz, int vert, int show);
PYMFC_API int CWnd_SetScrollInfo(void *o, PyObject *horz, PyObject *vert, PyObject *min, PyObject *max, PyObject *page, PyObject *pos, PyObject *disablenoscroll, PyObject *redraw);
PYMFC_API PyObject *CWnd_GetScrollInfo(void *o, PyObject *horz, PyObject *vert);

PYMFC_API BOOL CWnd_UpdateWindow(void *o);

PYMFC_API BOOL CWnd_TrackMouseEvent(void *o, int cancel, int hover, int leave, int nonclient, int hoverTime);


//
// Controls
//
PYMFC_API void *new_CEdit(PyObject *pyobj);
PYMFC_API void *new_CStatic(PyObject *pyobj);
PYMFC_API void *new_CButton(PyObject *obj);
PYMFC_API void *new_CListBox(PyObject *obj);
PYMFC_API void *new_CComboBox(PyObject *obj);


PYMFC_API void *new_CScrollBar(PyObject *obj);

// Imagelist
PYMFC_API void *new_ImageList();
PYMFC_API int CImageList_Create(void *o, int cx, int cy, int nFlags, int nInitial, int nGrow);
PYMFC_API int CImageList_Attach(void *o, HIMAGELIST himagelist);
PYMFC_API int CImageList_Detach(void *o);
PYMFC_API int CImageList_AddImage(void *o, HBITMAP bmp, HBITMAP maskbmp, COLORREF maskrgb, HICON hicon);
PYMFC_API int CImageList_Delete(void *o);
PYMFC_API HIMAGELIST CImageList_HANDLE(void *o);

PYMFC_API int CImageList_BeginDrag(void *o, int n, int x, int y);
PYMFC_API int CImageList_EndDrag();
PYMFC_API int CImageList_DragShowNolock(int f);
PYMFC_API int CImageList_DragMove(int x, int y);


// TabCtrl
PYMFC_API void *new_TabCtrl(PyObject *obj);
PYMFC_API int CTabCtrl_AdjustRect(void *o, int larger, int *left, int *top, int *right, int *bottom);
PYMFC_API int CTabCtrl_InsertItem(void *o, int idx, TCHAR *title);

// TreeView
PYMFC_API void *new_TreeView(PyObject *obj);

// ListView
PYMFC_API void *new_ListView(PyObject *obj);

// RichEdit
PYMFC_API void *new_RichEdit(PyObject *obj);
PYMFC_API long RichEdit_StreamIn(void *o, PyObject *rtf, int flag);
PYMFC_API long RichEdit_StreamOut(void *o, PyObject *rtf, int flag);




//
// Frame
//

PYMFC_API void *new_Frame(PyObject *pyobj);
PYMFC_API void *new_MDIFrame(PyObject *obj);
PYMFC_API void *new_MDIChild(PyObject *obj);

PYMFC_API int CFrame_CreateWnd(void *o, long dwExStyle, TCHAR *lpszClassName, 
	TCHAR *lpszWindowName, long dwStyle, int x, int y, int nWidth, 
	int nHeight, HWND hwndParent, HMENU nIDorHMenu);

PYMFC_API int CFrame_EnableDocking(void *o, int left, int top, int right, int bottom, int any);
PYMFC_API int CFrame_DockControlBar(void *o, void *cbar, int left, int top, int right, int bottom);

PYMFC_API PyObject *CMDIFrame_GetActive(void *o);
PYMFC_API void CFrame_ShowControlBar(void *o, void *bar, int show, int delay);

//
// Dialogs
//

PYMFC_API void *new_Dialog(PyObject *pyobj);
PYMFC_API int CDialog_DoModal(void *o, int left, int top, int width, int height, 
				   int style, TCHAR *title, TCHAR *font, int fontsize, int center);
PYMFC_API int CDialog_EndDialog(void *o, int result);
PYMFC_API int CDialog_Create(void *o, void *parent, int left, int top, int width, int height, 
				   int style, TCHAR *title, TCHAR *font, int fontsize, int center);



PYMFC_API void *new_FileDialog(PyObject *pyobj);
PYMFC_API PyObject *CFileDialog_DoModal(void *o, int open, void *parent,
		const TCHAR *title, const TCHAR *filename, const TCHAR *defext, 
		const TCHAR *initdir, const TCHAR *filter, 
		int filterindex,
		int height, int readonly, int overwriteprompt, int hidereadonly, 
		int nochangedir, int showhelp, int novalidate, int allowmultiselect, 
		int extensiondifferent, int pathmustexist, int filemustexist, 
		int createprompt, int shareaware, int noreadonlyreturn, int notestfilecreate, 
		int nonetworkbutton, int nodereferencelinks, 
		int enableincludenotify, int enablesizing);

PYMFC_API void *new_ColorDialog(PyObject *obj);
PYMFC_API PyObject *CColorDialog_DoModal(void *o, void *parent,
        COLORREF color, int rgbinit, int anycolor, int fullopen, int preventfullopen, 
        int showhelp, int solidcolor, int height);

PYMFC_API void *new_FontDialog(PyObject *obj);
PYMFC_API PyObject *CFontDialog_DoModal(void *o, void *parent, HDC hdc, LOGFONT *logfont,
    long flag, long color, TCHAR *style, long sizemin, long sizemax,
	LOGFONT *ret, long *retColor, long *retPoint);

PYMFC_API void *new_PrintDialog(PyObject *);
PYMFC_API PRINTDLG *CPrintDialog_DoModal(void *o, void *parent,
    HGLOBAL devmode, HGLOBAL devnames, DWORD flags, WORD frompage,
    WORD topage, WORD minpage, WORD maxpage, WORD copies);




PYMFC_API void *new_PropertyPage(PyObject *pyobj);
PYMFC_API int CPropertyPage_Create(void *o, int width, int height, int style, TCHAR *title, TCHAR *font, int fontsize);
PYMFC_API void *new_PropertySheet(PyObject *pyobj);
PYMFC_API int CPropertySheet_AddPage(void *o, void *page);
PYMFC_API int CPropertySheet_DoModal(void *o, void *parent, TCHAR *title, int selpage);


//
// Control Bars
//

PYMFC_API int CControlBar_EnableDocking(void *o, int left, int top, int right, int bottom, int any, int multi);

PYMFC_API void *new_CStatusBar(PyObject *obj);
PYMFC_API int CStatusBar_Create(void *o, void *parent, PyObject *lens);
PYMFC_API int CStatusBar_SetPaneText(void *o, int idx, TCHAR *s);
PYMFC_API int CStatusBar_CalcFixedSize(void *o, SIZE *size);

PYMFC_API void *new_CToolBar(PyObject *obj);
PYMFC_API int CToolBar_Create(void *o, void *parent, TCHAR *title, int id, int left, int top, int right, int bottom);
PYMFC_API int CToolBar_SetButtons(void *o, PyObject *buttonIds);
PYMFC_API int CToolBar_SetBitmap(void *o, HBITMAP hbmp);
PYMFC_API int CToolBar_SetImageList(void *o, void *imageList);
PYMFC_API int CToolBar_SetButtonInfo(void *o, int index, int id, int style, int iImage);
PYMFC_API PyObject *CToolBar_GetButtonInfo(void *o, int index);
PYMFC_API int CToolBar_GetButtonIndex(void *o, int id);
PYMFC_API PyObject *CToolBar_GetItemRect(void *o, int index);
PYMFC_API int CToolBar_GetButtonStyle(void *o, int index);
PYMFC_API void CToolBar_SetButtonStyle(void *o, int index, int style, int checked, int indeterminate, int disabled, int pressed);

PYMFC_API void *new_CSizingBar(PyObject *);
PYMFC_API int CSizingBar_Create(void *o, void *parent, TCHAR *title, int id, int left, int top, int right, int bottom, int resizechild, int showedge);

PYMFC_API void *new_ToolTip(PyObject *);
PYMFC_API int CToolTip_Create(void *o, void *parent, long style);


//
// CHotKeyCtrl
//

PYMFC_API void *new_HotKeyCtrl(PyObject *obj);

//
// IWebBrowser2
//
PYMFC_API void *new_WebCtrl(PyObject *pyobj);
PYMFC_API int PyMFCWebCtrl_Navigate(void *o, TCHAR *url);
PYMFC_API PyObject *PyMFCWebCtrl_GetDocument(void *o);
PYMFC_API int PyMFCWebCtrl_UIDeactivate(void *o);
PYMFC_API int PyMFCWebCtrl_ExecCommand(void *, DWORD commandid);

#ifdef __cplusplus
}
#endif


#endif

