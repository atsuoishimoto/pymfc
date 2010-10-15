// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"

#include "pymwndbase.h"
#include "pymgdi.h"
#include "pymutils.h"


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

HANDLE pymLoadImage(UINT type, TCHAR *filename,
	int cx, int cy,	int defaultcolor, int createdibsection,
	int defaultsize, int loadmap3dcolors, int loadtransparent,
	int monochrome,	int vgacolor) {

	PyMFC_PROLOGUE(pymLoadImage);

	UINT flag = 
			(defaultcolor ? LR_DEFAULTCOLOR:0) |
			(createdibsection ? LR_CREATEDIBSECTION:0) |
			(defaultsize ? LR_DEFAULTSIZE:0) |
			(loadmap3dcolors ? LR_LOADMAP3DCOLORS:0) |
			(loadtransparent ? LR_LOADTRANSPARENT:0) |
			(monochrome ? LR_MONOCHROME:0) |
			(vgacolor ? LR_VGACOLOR:0);

	HANDLE ret = LoadImage(NULL, filename, type, cx, cy, flag | LR_LOADFROMFILE);
	if (!ret)
		throw PyMFC_WIN32ERR();
	return ret;

	PyMFC_EPILOGUE(0);
}

inline
CGdiObject *getGDIObj(void *obj) {
	if (!obj) {
		throw PyMFCException("NULL CGdiObject");
	}
	
	CGdiObject *ret = dynamic_cast<CGdiObject*>((CGdiObject*)obj);
	if (!ret) {
		throw PyMFCException("Invalid CGdiObject");
	}
	return ret;
}

int GDIOBJ_Delete(void * gdiobj) {
	PyMFC_PROLOGUE(GDIOBJ_Delete);
	
	delete getGDIObj(gdiobj);
	return TRUE;

	PyMFC_EPILOGUE(0);
}

int GDIOBJ_Attach(void * gdiobj, HANDLE hobj) {
	PyMFC_PROLOGUE(GDIOBJ_Attach);
	
	if (getGDIObj(gdiobj)->Attach((HANDLE)hobj)) {
		return TRUE;
	}
	else {
		throw PyMFC_WIN32ERR();
	}

	PyMFC_EPILOGUE(0);
}

HANDLE GDIOBJ_GetHandle(void *gdiobj) {
	PyMFC_PROLOGUE(GDIOBJ_GetHandle);
	
	return getGDIObj(gdiobj)->m_hObject;

	PyMFC_EPILOGUE(0);
}

HANDLE GDIOBJ_Detach(void *gdiobj) {
	PyMFC_PROLOGUE(GDIOBJ_Detach);
	
	return getGDIObj(gdiobj)->Detach();

	PyMFC_EPILOGUE(0);
}

void *new_CFont() {
	PyMFC_PROLOGUE(new_CFont);

	return new CFont();

	PyMFC_EPILOGUE(0);
}

void *new_CFontIndirect(int height, int width, int escapement, int orientation, 
    int weight, int italic, int underline, int strikeout, int charset, int outputprecision,
    int clipprecision, int quality, int pitch, int family, const TCHAR *face) {

	PyMFC_PROLOGUE(new_CFontIndirect);
	
	LOGFONT lf;
	memset(&lf, 0, sizeof(lf));

	lf.lfHeight = height;
	lf.lfWidth = width;
	lf.lfEscapement = escapement;
	lf.lfOrientation = orientation;
	lf.lfWeight = weight;
	lf.lfItalic = italic;
	lf.lfUnderline = underline;
	lf.lfStrikeOut = strikeout;
	lf.lfCharSet = charset;
	lf.lfOutPrecision = outputprecision;
	lf.lfClipPrecision = clipprecision;
	lf.lfQuality = quality;
	lf.lfPitchAndFamily = pitch | family;
	_tcsncpy(lf.lfFaceName, face, LF_FACESIZE);

	CFont *f = new CFont();
	if (!f->CreateFontIndirect(&lf)) {
		delete f;
		throw PyMFC_WIN32ERR();
	}
	return f;

	PyMFC_EPILOGUE(0);

}

void *CFont_FromHandle(HFONT hobj) {
	PyMFC_PROLOGUE(CFont_FromHandle);
	
	CFont *ret = CFont::FromHandle(hobj);
	if (!ret) {
		throw PyMFC_WIN32ERR();
	}
	return ret;

	PyMFC_EPILOGUE(0);
}


void *new_CBitmap() {
	PyMFC_PROLOGUE(new_CBitmap);
	
	return new CBitmap();

	PyMFC_EPILOGUE(0);
}

void *CBitmap_FromHandle(HANDLE hobj) {
	PyMFC_PROLOGUE(CBitmap_FromHandle);
	
	CBitmap *ret = CBitmap::FromHandle((HBITMAP)hobj);
	if (!ret) {
		throw PyMFC_WIN32ERR();
	}
	return ret;

	PyMFC_EPILOGUE(0);
}
/*
int CDC_PointToPixel(long dc, double point) {
	PyMFC_PROLOGUE(CDC_PointToPixel);
	
	point *= 10;
	HDC hDC=NULL;
	if (dc) {
		hDC = ((CDC*)dc)->m_hAttribDC;
	}
	else {
		hDC = ::GetDC(NULL);
	}
	POINT pt;
	pt.y = (long)(::GetDeviceCaps(hDC, LOGPIXELSY) * point / 720);
	::DPtoLP(hDC, &pt, 1);
	POINT ptOrg = { 0, 0 };
	::DPtoLP(hDC, &ptOrg, 1);
	int ret = -abs(pt.y - ptOrg.y);

	if (!dc) {
		ReleaseDC(NULL, hDC);
	}
	return ret;

	PyMFC_EPILOGUE(0);
}
*/
int CALLBACK pymEnumFontFamiliesExProc(const LOGFONT* logfont, const TEXTMETRIC *tm,
									   DWORD fontType, LPARAM lParam) {

	try {
		PyDTModule gdi("pymfc.gdi");

		PyDTObject tmObj = gdi.getAttr("TextMetric").call("");
		TEXTMETRIC *pTmObj = (TEXTMETRIC *)PyMFCPtr::asPtr(tmObj.getAttr("pTEXTMETRIC").get());
		*pTmObj = *tm;

		PyDTObject lfObj = gdi.getAttr("LogFont").call("OO", 
			PyDTNone().get(), PyMFCPtr((void*)logfont).get());


		PyDTObject func((PyObject *)lParam, false);
		return func.call("OOi", tmObj.get(), lfObj.get(), fontType==TRUETYPE_FONTTYPE?1:0).getInt();
	}
	catch (PyDTException &err) {
		err.setError();
		return -1;
	}
	return 1;
}


int pymEnumFontFamiliesEx(HDC hdc, LOGFONT *lpLogfont, PyObject *func) {
	PyMFC_PROLOGUE(pymEnumFontFamiliesEx);
	return EnumFontFamiliesEx(hdc, lpLogfont, pymEnumFontFamiliesExProc, (LPARAM)func, 0); 
	PyMFC_EPILOGUE(-1);
}




