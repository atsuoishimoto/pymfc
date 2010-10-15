// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMFCMENU_H
#define PYMFCMENU_H


#ifdef __cplusplus
extern "C" {
#endif

PYMFC_API int c_menu_ismenu(HMENU hMenu);
PYMFC_API HMENU c_menu_create();
PYMFC_API HMENU c_menu_createPopup();
PYMFC_API int c_menu_destroy(HMENU hMenu);
PYMFC_API int c_menu_insert(HMENU hMenu, int nPosition, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem);
PYMFC_API int c_menu_append(HMENU hMenu, int nFlags, void *nIDNewItem, TCHAR* lpszNewItem);
PYMFC_API int c_menu_delete(HMENU hMenu, int nPosition, int nFlags);
PYMFC_API int c_menu_remove(HMENU hMenu, int nPosition, int nFlags);
PYMFC_API int c_menu_itemCount(HMENU hMenu);
PYMFC_API PyObject *c_menu_getString(HMENU hMenu, int nPosition, int nFlags);
PYMFC_API int c_menu_track_popup_menu(HMENU hMenu, int fuFlags, int x, int y, HWND hwnd, void *lptpm);


#ifdef __cplusplus
}
#endif



#endif