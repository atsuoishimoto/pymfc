// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include <vector>
#include <cderr.h>

#include "pymwndbase.h"
#include "pymwnd.h"

class DynDialogTemplate {
public:
	CString m_title;
	int m_style;
	int m_left, m_top, m_width, m_height;
	CString m_font;
	int m_fontsize;

	void init(const CString &title, int style, int left, int top, int width, int height, const CString &font, int fontsize) {
		m_title = title;
		m_style = style;
		m_left = left;
		m_top = top;
		m_width = width;
		m_height = height;
		m_font = font;
		m_fontsize = fontsize;
	}

	void getFontName(CString &fontName, int &fontSize) {
		// copied from CDialogTemplate::SetSystemFont()
		LPCTSTR pszFace = _T("System");
		WORD wDefSize = 10;
		HFONT hFont = (HFONT)::GetStockObject(DEFAULT_GUI_FONT);
		if (hFont == NULL)
			hFont = (HFONT)::GetStockObject(SYSTEM_FONT);
		if (hFont != NULL)
		{
			LOGFONT lf;
			if (::GetObject(hFont, sizeof(LOGFONT), &lf) != 0)
			{
				pszFace = lf.lfFaceName;
				HDC hDC = ::GetDC(NULL);
				if (lf.lfHeight < 0)
					lf.lfHeight = -lf.lfHeight;
				wDefSize = (WORD)MulDiv(lf.lfHeight, 72, GetDeviceCaps(hDC, LOGPIXELSY));
				::ReleaseDC(NULL, hDC);
			}
		}

		fontName = pszFace;
		fontSize = wDefSize;
	}
	
	void calcDialogUnit(const CString &fontName, int fontSize, double &xunit, double &yunit) {
		CDC *desktop = CWnd::GetDesktopWindow()->GetDC();

		CDC dc;
		BOOL ret = dc.CreateCompatibleDC(desktop);
		ASSERT(ret);

		CFont font;
		int fontsize = (-MulDiv(fontSize, dc.GetDeviceCaps(LOGPIXELSY), 72));
		ret = font.CreateFont(fontsize, 0, 0, 0, FW_NORMAL, 0, 0, 0, DEFAULT_CHARSET, 
  		  0, 0, 0, 0, fontName);
		
		ASSERT(ret);
		CFont *org = dc.SelectObject(&font);

		// Q145994 
		TEXTMETRIC tm;
		dc.GetTextMetrics( &tm );
		yunit = (double)tm.tmHeight/8.0; // 8 vertical units are the height of one character 

		CSize size;
		size = dc.GetTextExtent(
		   _T("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"), 52);
		xunit = ((size.cx / 26 + 1) / 2)/4.0;   // 4 horizontal units are the width of one character 

		dc.SelectObject(org);
		
		CWnd::GetDesktopWindow()->ReleaseDC(desktop);
	}
	
	void createTemplate(std::vector<BYTE> &buf) {

		if (m_font.GetLength() == 0) {
			getFontName(m_font, m_fontsize);
		}

		double xunit, yunit;
		calcDialogUnit(m_font, m_fontsize, xunit, yunit);
		
		DLGTEMPLATE dlgtmpl;
		memset(&dlgtmpl, 0, sizeof(dlgtmpl));

		dlgtmpl.cx = (short)(m_width / xunit);
		dlgtmpl.cy = (short)(m_height / yunit);  
		dlgtmpl.style = m_style | DS_SETFONT;
		dlgtmpl.dwExtendedStyle = 0; 
		dlgtmpl.x = (short)(m_left / xunit); 
		dlgtmpl.y = (short)(m_top / yunit); 
		dlgtmpl.cdit = 0;

		_bstr_t t(m_title);
		const wchar_t *utitle = t;
		int tlen = (t.length() + 1) * sizeof(wchar_t);

		_bstr_t f(m_font);
		const wchar_t *ufont = f;
		int flen = (f.length() + 1) * sizeof(wchar_t);

		int nBufferSize =  sizeof(DLGTEMPLATE) + (2 * sizeof(WORD))/*menu and class*/ + tlen; 
		nBufferSize += sizeof(WORD) + flen; /* font information*/
		nBufferSize = (nBufferSize + 3) & ~3;  // adjust size to make first control DWORD aligned
			
		buf.resize(nBufferSize);

		BYTE*   pBuffer = &buf[0];
		memset(pBuffer, 0, nBufferSize);
		BYTE*   pdest = pBuffer;
		// transfer DLGTEMPLATE structure to the buffer
		memcpy(pdest, &dlgtmpl, sizeof(DLGTEMPLATE));
		pdest += sizeof(DLGTEMPLATE);
		*(WORD*)pdest = 0; // no menu
		*(WORD*)(pdest + 1) = 0;  // use default window class
		pdest += 2 * sizeof(WORD);
		memcpy(pdest, utitle, tlen);
		pdest += tlen;

		*(WORD*)pdest = m_fontsize;  // font size
		pdest += sizeof(WORD);
		memcpy(pdest, ufont, flen);
	}
};


class PyMFCDialog : public CDialog
{
	std::vector<BYTE> m_tmpl; //todo: use hGlobal instead.
	DynDialogTemplate m_dyndlg;
	bool m_center;
public:
	void initTemplate(const CString &title, int style, int left, int top, int width, 
			int height, const CString &font, int fontsize, bool center) {

		m_dyndlg.init(title, style, left, top, width, height, font, fontsize);
		m_center = center;
	}

	
	BOOL CreateIndirect(CWnd *parent) {
		m_dyndlg.createTemplate(m_tmpl);
		return CDialog::CreateIndirect(&m_tmpl[0], parent);
	}

	BOOL InitModalIndirect() {
		m_dyndlg.createTemplate(m_tmpl);
		return CDialog::InitModalIndirect(&m_tmpl[0]);
	}

	BOOL CheckAutoCenter() {
		return m_center;
	}
};


void *new_Dialog(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_Dialog);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCDialog, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}


int CDialog_Create(void *o, void *parent, int left, int top, int width, int height, 
				   int style, TCHAR *title, TCHAR *font, int fontsize, int center) {
	PyMFC_PROLOGUE(CDialog_DoModal);

	PyMFCDialog *dlg = getCWnd<PyMFCDialog>(o);
	dlg->initTemplate(title, style, left, top, width, height, font, fontsize, center?true:false);

	BOOL err=FALSE;
	int ret=0;
	{
		PyMFCLeavePython lp;
		CWnd * p = NULL;
		if (parent) {
			p = getCWnd<CWnd>(parent);
		}

		err = dlg->CreateIndirect(p);
		if (!err) {
			throw PyMFC_WIN32ERR();
		}
		
		return 0;
	}

	PyMFC_EPILOGUE(-1);
}

int CDialog_DoModal(void *o, int left, int top, int width, int height, 
				   int style, TCHAR *title, TCHAR *font, int fontsize, int center) {

	PyMFC_PROLOGUE(CDialog_DoModal);

	PyMFCDialog *dlg = getCWnd<PyMFCDialog>(o);
	dlg->initTemplate(title, style, left, top, width, height, font, fontsize, center?true:false);

	BOOL err=FALSE;
	int ret=0;
	{
		PyMFCLeavePython lp;
		err = dlg->InitModalIndirect();
		if (!err) {
			throw PyMFC_WIN32ERR();
		}
		
		ret = dlg->DoModal();
		return ret;
	}

	PyMFC_EPILOGUE(-1);
}

int CDialog_EndDialog(void *o, int result) {
	PyMFC_PROLOGUE(CDialog_EndDialog);

	{
		PyMFCLeavePython lp;
		PyMFCDialog *dlg = getCWnd<PyMFCDialog>(o);
		dlg->EndDialog(result);
	}
	return 1;
	
	PyMFC_EPILOGUE(0);
}

class PyMFCFileDialog:public CFileDialog {
public:
	std::vector<TCHAR> m_stdbuf;
	std::vector<TCHAR> m_extFiles;
	std::vector<TCHAR> m_extFolder;

	PyMFCFileDialog():CFileDialog(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, NULL, NULL, 0, FALSE){
	}

	~PyMFCFileDialog() {
	}

	virtual void OnFileNameChange( ) {
        int fbuflen = GetParent()->SendMessage(CDM_GETSPEC, NULL, 0);
		m_extFiles.resize(fbuflen+1);
		GetParent()->SendMessage(CDM_GETSPEC, fbuflen, (LPARAM)&m_extFiles[0]);

        int pbuflen = GetParent()->SendMessage(CDM_GETFOLDERPATH, NULL, 0);
		m_extFolder.resize(pbuflen+1);
		GetParent()->SendMessage(CDM_GETFOLDERPATH, pbuflen, (LPARAM)&m_extFolder[0]);
	}


	virtual int DoModal(BOOL open, CWnd *p) {
		m_bOpenFileDialog = open;
		m_pParentWnd = p;
		return CFileDialog::DoModal();
	}

};

void *new_FileDialog(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_FileDialog);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCFileDialog, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

PyObject *CFileDialog_DoModal(void *o, int open, void *parent,
		const TCHAR *title, const TCHAR *filename, const TCHAR *defext, 
		const TCHAR *initdir, const TCHAR *filter, 
		int filterindex,
		int height, int readonly, int overwriteprompt, int hidereadonly, 
		int nochangedir, int showhelp, int novalidate, int allowmultiselect, 
		int extensiondifferent, int pathmustexist, int filemustexist, 
		int createprompt, int shareaware, int noreadonlyreturn, int notestfilecreate, 
		int nonetworkbutton, int nodereferencelinks, 
		int enableincludenotify, int enablesizing) {

	PyMFC_PROLOGUE(FileDialog_DoModal);

	PyMFCFileDialog *dlg = getCWnd<PyMFCFileDialog>(o);
	PyMFCWndBase *wbase = getWndBase(o);

	CWnd *pWnd = NULL;
	if (parent) {
		pWnd = getCWnd<CWnd>(parent);
	}

	UINT flag = OFN_EXPLORER;

	if (readonly)
		flag |= OFN_READONLY;
	if (overwriteprompt)
		flag |= OFN_OVERWRITEPROMPT;
	if (hidereadonly)
		flag |= OFN_HIDEREADONLY;
	if (nochangedir)
		flag |= OFN_NOCHANGEDIR;
	if (showhelp)
		flag |= OFN_SHOWHELP;
	if (novalidate)
		flag |= OFN_NOVALIDATE;
	if (allowmultiselect)
		flag |= OFN_ALLOWMULTISELECT;
	if (extensiondifferent)
		flag |= OFN_EXTENSIONDIFFERENT;
	if (pathmustexist)
		flag |= OFN_PATHMUSTEXIST;
	if (filemustexist)
		flag |= OFN_FILEMUSTEXIST;
	if (createprompt)
		flag |= OFN_CREATEPROMPT;
	if (shareaware)
		flag |= OFN_SHAREAWARE;
	if (noreadonlyreturn)
		flag |= OFN_NOREADONLYRETURN;
	if (notestfilecreate)
		flag |= OFN_NOTESTFILECREATE;
	if (nonetworkbutton)
		flag |= OFN_NONETWORKBUTTON;
	if (nodereferencelinks)
		flag |= OFN_NODEREFERENCELINKS;
	if (enableincludenotify)
		flag |= OFN_ENABLEINCLUDENOTIFY;
	if (enablesizing)
		flag |= OFN_ENABLESIZING;

	dlg->m_ofn.lpstrTitle = title;
	dlg->m_ofn.nFilterIndex = filterindex;


	int bufsize=4096;

	dlg->m_stdbuf.resize(bufsize);
	TCHAR *pbuf = &dlg->m_stdbuf[0];
	dlg->m_ofn.lpstrFile = pbuf;
	memset(dlg->m_ofn.lpstrFile, 0, bufsize);
	if (filename)
		_tcsncpy(dlg->m_ofn.lpstrFile, filename, bufsize);

	dlg->m_ofn.nMaxFile = bufsize;
	dlg->m_ofn.lpstrFilter = filter;
	dlg->m_ofn.lpstrInitialDir = initdir;
	dlg->m_ofn.lpstrTitle = title;
	dlg->m_ofn.Flags |= flag;
	dlg->m_ofn.lpstrDefExt = defext;

	

	std::vector<BYTE> templ;
	if (height) {
		DynDialogTemplate ddd;
		ddd.init("", 
			WS_CHILD | WS_VISIBLE | DS_3DLOOK | DS_CONTROL | WS_CLIPSIBLINGS,
			0,0,10000, height,"", 0);	// todo: determin min width value.
										// todo: support dialog unit.
		dlg->m_ofn.Flags |= OFN_ENABLETEMPLATEHANDLE;

		ddd.createTemplate(templ);
		
		dlg->m_ofn.hInstance = (HINSTANCE)&templ[0];
	}
	
	
	int ret;
	{
		PyMFCLeavePython lp;
		// Since MFC doesn't handle WM_NCCREATE for CFileDialog window,
		// python object should be incref'ed here explicitly.
		// WM_NCDESTROY will be handled as usual, so unlocking 
		// windows is done by normal PyMFC gimmics.
		wbase->lockObj();
		ret = dlg->DoModal(open, pWnd);
	}
	
	if (wbase->isLocked()) {
		// WM_NCDESTROY wasn't sent to the dialog.
		wbase->onWindowDestroyed();
	}

	if (ret == IDCANCEL && allowmultiselect) {
		DWORD err = CommDlgExtendedError();
		if (err == FNERR_BUFFERTOOSMALL && dlg->m_extFiles.size()) {
			
			PyDTList ret(0);
			const TCHAR *fname = &(*dlg->m_extFolder.begin());
			std::wstring folder(fname);
			int lenfolder = folder.size();
			if (!lenfolder 
				|| folder[lenfolder -1] != _T('\\')) {
				
				folder += _T("\\");
			}
			std::vector<TCHAR>::iterator top = dlg->m_extFiles.begin();
			while (top < dlg->m_extFiles.end()) {
				std::vector<TCHAR>::iterator end = top + 1;
				while (end < dlg->m_extFiles.end()) {
					if (*end == '"') {
						*end = 0;
						std::wstring f = folder + std::wstring(&(*(top+1)));
						ret.append(f.c_str());
						break;
					}
					end += 1;
				}
				top = end;
				while (top < dlg->m_extFiles.end()) {
					if (*top == '"') {
						break;
					}
					top++;
				}
			}
			return ret.detach();
		}
	}
	else if (ret == IDOK) {
		if (allowmultiselect) {
			PyDTList ret(0);
			POSITION p = dlg->GetStartPosition();
			while (p) {
				CString s = dlg->GetNextPathName(p);
				ret.append(s);
			}
			return ret.detach();
		}
		else {
			PyDTList ret(0);
			ret.append(PyDTUnicode(dlg->GetPathName()));
			return ret.detach();
		}
	}
	return PyDTList(0).detach();

	PyMFC_EPILOGUE(NULL);
}



class PyMFCColorDialog:public CColorDialog {
public:
	virtual int DoModal(CWnd *p) {
		m_pParentWnd = p;
		return CColorDialog::DoModal();
	}

};


void *new_ColorDialog(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_ColorDialog);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCColorDialog, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

PyObject *CColorDialog_DoModal(void *o, void *parent,
        COLORREF color, int rgbinit, int anycolor, int fullopen, int preventfullopen, 
        int showhelp, int solidcolor, int height) {

	PyMFC_PROLOGUE(CColorDialog_DoModal);

	PyMFCColorDialog *dlg = getCWnd<PyMFCColorDialog>(o);
	PyMFCWndBase *wbase = getWndBase(o);

	CWnd *pWnd = NULL;
	if (parent) {
		pWnd = getCWnd<CWnd>(parent);
	}

	UINT flag = 0;
	if (anycolor) 
		flag |= CC_ANYCOLOR;
	if (fullopen) 
		flag |= CC_FULLOPEN;
	if (preventfullopen) 
		flag |= CC_PREVENTFULLOPEN;
	if (rgbinit) 
		flag |= CC_RGBINIT;
	if (showhelp) 
		flag |= CC_SHOWHELP;
	if (solidcolor) 
		flag |= CC_SOLIDCOLOR;
	
	dlg->m_cc.rgbResult = color;
	dlg->m_cc.Flags |= flag;
	
	std::vector<BYTE> templ;
	if (height) {
		DynDialogTemplate ddd;
		ddd.init("", 
			WS_CHILD | WS_VISIBLE | DS_3DLOOK | DS_CONTROL | WS_CLIPSIBLINGS,
			0,0,10000, height,"", 0);	// todo: determin min width value.
										// todo: support dialog unit.
		dlg->m_cc.Flags |= CC_ENABLETEMPLATEHANDLE;

		ddd.createTemplate(templ);
		
		dlg->m_cc.hInstance = (HWND)&templ[0];
	}

	int ret;
	{
		PyMFCLeavePython lp;
		// Since MFC doesn't handle WM_NCCREATE for CColorDialog window,
		// python object should be incref'ed here explicitly.
		// WM_NCDESTROY will be handled as usual, so unlocking 
		// windows is done by normal PyMFC gimmics.
		wbase->lockObj();
		ret = dlg->DoModal(pWnd);
	}

	if (wbase->isLocked()) {
		// WM_NCDESTROY wasn't sent to the dialog.
		wbase->onWindowDestroyed();
	}

	if (IDCANCEL == ret) {
		DWORD err = CommDlgExtendedError();
		PyMFC_RETNONE();
	}
	else {
		return PyDTInt(dlg->GetColor()).detach();
	}

	PyMFC_EPILOGUE(NULL);
}

class PyMFCFontDialog:public CFontDialog {
public:
	virtual int DoModal(CWnd *p) {
		m_pParentWnd = p;
		return CFontDialog::DoModal();
	}

};
void *new_FontDialog(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_FontDialog);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCFontDialog, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

PyObject *CFontDialog_DoModal(void *o, void *parent, HDC hdc, LOGFONT *logfont,
							  long flag, long color, TCHAR *style, 
							  long sizemin, long sizemax,
							  LOGFONT *retLogfont, long *retColor, long *retPoint) {

	PyMFC_PROLOGUE(CFontDialog_DoModal);

	PyMFCFontDialog *dlg = getCWnd<PyMFCFontDialog>(o);
	PyMFCWndBase *wbase = getWndBase(o);

	CWnd *pWnd = NULL;
	if (parent) {
		pWnd = getCWnd<CWnd>(parent);
	}

	LOGFONT lf;
	memset(&lf, 0, sizeof(lf));

	if (logfont) {
		lf = *((LOGFONT*)logfont);
	}

	TCHAR stylename[LF_FACESIZE+1];
	memset(stylename, 0, sizeof(stylename));
	if (style && *style) {
		_tcsncpy(stylename, style, LF_FACESIZE);
	}

	dlg->m_cf.hDC = (HDC)hdc;
	dlg->m_cf.lpLogFont = &lf;
	dlg->m_cf.Flags &= ~CF_EFFECTS;
	dlg->m_cf.Flags |= flag;
	dlg->m_cf.rgbColors = color;
	dlg->m_cf.lpszStyle = stylename;
	dlg->m_cf.nSizeMin = sizemin;
	dlg->m_cf.nSizeMax = sizemax;
	
	int ret;
	{
		PyMFCLeavePython lp;
		// Since MFC doesn't handle WM_NCCREATE for CFontDialog window,
		// python object should be incref'ed here explicitly.
		// WM_NCDESTROY will be handled as usual, so unlocking 
		// windows is done by normal PyMFC gimmics.
		wbase->lockObj();
		ret = dlg->DoModal(pWnd);
	}

	if (wbase->isLocked()) {
		// WM_NCDESTROY wasn't sent to the dialog.
		wbase->onWindowDestroyed();
	}

	if (IDCANCEL == ret) {
		DWORD err = CommDlgExtendedError();
		PyMFC_RETNONE();
	}
	else {
		*retLogfont= *dlg->m_cf.lpLogFont;
		*retColor = dlg->GetColor();
		*retPoint = dlg->m_cf.iPointSize;
		return PyDTInt(1).detach();
	}

	PyMFC_EPILOGUE(NULL);

}


class PyMFCPrintDialog:public CPrintDialog {
public:
	PyMFCPrintDialog():CPrintDialog(FALSE){
	}

	~PyMFCPrintDialog() {
	}
	virtual int DoModal(CWnd *p) {
		m_pParentWnd = p;
		return CPrintDialog::DoModal();
	}

};
void *new_PrintDialog(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_PrintDialog);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCPrintDialog, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}


PRINTDLG *CPrintDialog_DoModal(void *o, void *parent,
    HGLOBAL devmode, HGLOBAL devnames, DWORD flags, WORD frompage,
    WORD topage, WORD minpage, WORD maxpage, WORD copies) {

	PyMFC_PROLOGUE(CPrintDialog_DoModal);

	PyMFCPrintDialog *dlg = getCWnd<PyMFCPrintDialog>(o);
	PyMFCWndBase *wbase = getWndBase(o);

	CWnd *pWnd = NULL;
	if (parent) {
		pWnd = getCWnd<CWnd>(parent);
	}

	dlg->m_pd.Flags = flags;
	dlg->m_pd.hDevMode = devmode;
	dlg->m_pd.hDevNames = devnames;
	dlg->m_pd.nFromPage = frompage;
	dlg->m_pd.nToPage = topage;
	dlg->m_pd.nMinPage = minpage;
	dlg->m_pd.nMaxPage = maxpage;
	dlg->m_pd.nCopies = copies;

	int ret;
	{
		PyMFCLeavePython lp;
		// Since MFC doesn't handle WM_NCCREATE for CPrintDialog window,
		// python object should be incref'ed here explicitly.
		// WM_NCDESTROY will be handled as usual, so unlocking 
		// windows is done by normal PyMFC gimmics.
		wbase->lockObj();
		ret = dlg->DoModal(pWnd);
	}

	if (wbase->isLocked()) {
		// WM_NCDESTROY wasn't sent to the dialog.
		wbase->onWindowDestroyed();
	}

	if (IDCANCEL == ret) {
		DWORD err = CommDlgExtendedError();
		return NULL;
	}
	else {
		return &dlg->m_pd;
	}
	return NULL;
	PyMFC_EPILOGUE(NULL);
}




class PyMFCPropertyPage: public CPropertyPage
{
	std::vector<BYTE> m_tmpl; //todo: use hGlobal instead.
	DynDialogTemplate m_dyndlg;
	bool m_center;
public:
	void initTemplate(const CString &title, int style, int left, int top, int width, 
			int height, const CString &font, int fontsize) {

		m_dyndlg.init(title, style, left, top, width, height, font, fontsize);
		m_dyndlg.createTemplate(m_tmpl);

		m_psp.dwFlags |= PSP_DLGINDIRECT |PSP_USETITLE;
		m_psp.pResource = (DLGTEMPLATE*)&m_tmpl[0];
		m_psp.pszTitle = m_dyndlg.m_title;
	}

};

void *new_PropertyPage(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_PropertyPage);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<PyMFCPropertyPage, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

int CPropertyPage_Create(void *o, int width, int height, int style, TCHAR *title, TCHAR *font, int fontsize) {
	PyMFC_PROLOGUE(CPropertyPage_Create);

	PyMFCPropertyPage *wnd = getCWnd<PyMFCPropertyPage>(o);
	wnd->initTemplate(title, style, 0, 0, width, height, font, fontsize);

	return TRUE;

	PyMFC_EPILOGUE(0);
}

void *new_PropertySheet(PyObject *pyobj) {
	PyMFC_PROLOGUE(new_PropertySheet);
	
	return static_cast<CWnd*>(
			new PyMFCWnd<CPropertySheet, PyMFCMsgParser>(pyobj));

	PyMFC_EPILOGUE(0);
}

int CPropertySheet_AddPage(void *o, void *page) {
	PyMFC_PROLOGUE(PropertySheet_AddPage);

	CPropertySheet *sheet = getCWnd<CPropertySheet>(o);
	CPropertyPage *p= getCWnd<CPropertyPage>(page);
	sheet->AddPage(p);
	return TRUE;

	PyMFC_EPILOGUE(0);
}


int CPropertySheet_DoModal(void *o, void *parent, TCHAR *title, int selpage) {
	PyMFC_PROLOGUE(PropertySheet_DoModal);

	CPropertySheet *sheet = getCWnd<CPropertySheet>(o);
	CWnd *p = NULL;
	if (parent) {
		p = getCWnd<CWnd>(parent);
	}
	sheet->Construct(title, p, selpage);

	int ret;
	{
		PyMFCLeavePython lp;
		ret = sheet->DoModal();
	}

	return ret;

	PyMFC_EPILOGUE(-1);
}
