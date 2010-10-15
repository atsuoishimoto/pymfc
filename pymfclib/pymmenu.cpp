// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pymwndbase.h"

#include "pymmenu.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif


int c_menu_ismenu(HMENU hMenu) {
	PyMFC_PROLOGUE(c_menu_ismenu);
	
	return IsMenu((HMENU)hMenu);

	PyMFC_EPILOGUE(-1);
}

HMENU c_menu_create() {
	PyMFC_PROLOGUE(c_menu_create);
	
	HMENU hMenu = CreateMenu();
	if (!hMenu) {
		throw PyMFC_WIN32ERR();
	}
	return hMenu;

	PyMFC_EPILOGUE(0);
}

HMENU c_menu_createPopup() {
	PyMFC_PROLOGUE(c_menu_createPopup);
	
	HMENU hMenu = CreatePopupMenu();
	if (!hMenu) {
		throw PyMFC_WIN32ERR();
	}
	return hMenu;

	PyMFC_EPILOGUE(0);
}

int c_menu_destroy(HMENU hMenu) {
	PyMFC_PROLOGUE(c_menu_destroy);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	if (!DestroyMenu((HMENU)hMenu)) 
		throw PyMFC_WIN32ERR();

	return TRUE;
	PyMFC_EPILOGUE(0);
}

int c_menu_insert(HMENU hMenu, int nPosition, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem) {
	PyMFC_PROLOGUE(c_menu_insert);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	if (!InsertMenu((HMENU)hMenu, nPosition, nFlags, (UINT_PTR)nIDNewItem, lpszNewItem))
		throw PyMFC_WIN32ERR();
	
	return TRUE;
	PyMFC_EPILOGUE(0);
}

int c_menu_append(HMENU hMenu, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem) {
	PyMFC_PROLOGUE(c_menu_append);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	if (!AppendMenu((HMENU)hMenu, nFlags, (UINT_PTR)nIDNewItem, lpszNewItem))
		throw PyMFC_WIN32ERR();
	
	return TRUE;
	PyMFC_EPILOGUE(0);
}

int c_menu_delete(HMENU hMenu, int nPosition, int nFlags) {
	PyMFC_PROLOGUE(c_menu_delete);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	if (!DeleteMenu((HMENU)hMenu, nPosition, nFlags))
		throw PyMFC_WIN32ERR();
	
	return TRUE;
	PyMFC_EPILOGUE(0);
}
int c_menu_remove(HMENU hMenu, int nPosition, int nFlags) {
	PyMFC_PROLOGUE(c_menu_remove);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	if (!RemoveMenu((HMENU)hMenu, nPosition, nFlags))
		throw PyMFC_WIN32ERR();
	
	return TRUE;
	PyMFC_EPILOGUE(0);
}

int c_menu_itemCount(HMENU hMenu) {
	PyMFC_PROLOGUE(c_menu_itemCount);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	return GetMenuItemCount((HMENU)hMenu);

	return TRUE;
	PyMFC_EPILOGUE(-1);
}

PyObject *c_menu_getString(HMENU hMenu, int nPosition, int nFlags) {
	PyMFC_PROLOGUE(c_menu_getString);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	int len = GetMenuString((HMENU)hMenu, nPosition, NULL, 0, nFlags);
	CString s;
	TCHAR *buf = s.GetBuffer(len+1);

	if (!GetMenuString((HMENU)hMenu, nPosition, buf, len+1, nFlags))
		throw PyMFC_WIN32ERR();
	
	return PyDTUnicode(buf, len).detach();
	PyMFC_EPILOGUE(NULL);
}

int c_menu_track_popup_menu(HMENU hMenu, int fuFlags, int x, int y, HWND hwnd, void *lptpm) {
	PyMFC_PROLOGUE(c_menu_track_popup_menu);
	
	if (!IsMenu((HMENU)hMenu))
		throw PyMFCException("Invalid hMenu");

	BOOL ret;
	{
		PyMFCLeavePython lp;
		ret = TrackPopupMenuEx((HMENU)hMenu, fuFlags|TPM_VERTICAL, x, y, (HWND)hwnd, (LPTPMPARAMS)lptpm);
	}
	return ret;

	PyMFC_EPILOGUE(NULL);
}
