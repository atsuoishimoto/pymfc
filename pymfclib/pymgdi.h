// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMFCGDI_H
#define PYMFCGDI_H

#ifdef __cplusplus
extern "C" {
#else
#	pragma warning(disable:4101 4102)
#endif

DL_EXPORT(void) init_pymfc_gdi(void);

PYMFC_API HANDLE pymLoadImage(UINT type,  TCHAR *filename,
	int cx, int cy,	int defaultcolor, int createdibsection,
	int defaultsize, int loadmap3dcolors, int loadtransparent,
	int monochrome,	int vgacolor);


//
// GDI Objects
//
PYMFC_API int GDIOBJ_Delete(void *gdiobj);
PYMFC_API int GDIOBJ_Attach(void * gdiobj, HANDLE hobj);
PYMFC_API HANDLE GDIOBJ_Detach(void * gdiobj);

PYMFC_API HANDLE GDIOBJ_GetHandle(void *gdiobj);


PYMFC_API void *new_CFont();
PYMFC_API void *new_CFontIndirect(int height, int width, int escapement, int orientation, 
    int weight, int italic, int underline, int strikeout, int charset, int outputprecision,
    int clipprecision, int quality, int pitch, int family, const TCHAR *face);



PYMFC_API void *CFont_FromHandle(HANDLE hobj);


PYMFC_API void *new_CBitmap();
PYMFC_API void *CBitmap_FromHandle(HANDLE hobj);

//
// CDC funcs
//
PYMFC_API int CDC_PointToPixel(void *dc, double point);
PYMFC_API int pymEnumFontFamiliesEx(HDC hdc, LOGFONT *lpLogfont, PyObject *func);


#ifdef __cplusplus
}
#endif


#endif

