
cdef extern from "pymwnd.h":
    # Frames
    void *new_Frame(object obj) except NULL
    void *new_MDIFrame(object obj) except NULL
    void *new_MDIChild(object obj) except NULL
    object CMDIFrame_GetActive(void *o)

    int CFrame_EnableDocking(void *o, int left, int top, int right, int bottom, int any) except 0
    int CFrame_DockControlBar(void *o, void *cbar, int left, int top, int right, int bottom) except 0
    void CFrame_ShowControlBar(void *o, void *bar, int show, int delay)
    
    # Dialog
    void *new_Dialog(object obj) except NULL
    int CDialog_DoModal(void *o, int left, int top, int width, int height, 
                   int style, TCHAR *title, TCHAR *font, int fontsize, int center) except *
    int CDialog_EndDialog(void *o, int result)
    int CDialog_Create(void *o, void *parent, int left, int top, int width, int height, 
                   int style, TCHAR *title, TCHAR *font, int fontsize, int center) except -1
    
    void *new_PropertyPage(object obj) except NULL
    int CPropertyPage_Create(void *o, int width, int height, int style, TCHAR *title, TCHAR *font, int fontsize)
    void *new_PropertySheet(object obj) except NULL
    int CPropertySheet_AddPage(void *o, void *page) except 0
    int CPropertySheet_DoModal(void *o, void *parent, TCHAR *title, int selpage) except *


    
cdef class _wnd(_WndBase):
    cdef void *newInstance(self):
        return new_CWnd(self)

cdef class _frame(_WndBase):
    cdef object controlbars
    
    cdef void *newInstance(self):
        return new_Frame(self)

    def enableDocking(self, left=0, top=0, right=0, bottom=0, any=1):
        CFrame_EnableDocking(self._cwnd, left, top, right, bottom, any)
    
    def dockControlBar(self, cbar, left=0, top=0, right=0, bottom=0):
        if not self.controlbars:
            self.controlbars = []
        CFrame_DockControlBar(self._cwnd, PyMFCPtr_AsVoidPtr(cbar.cwnd), left, top, right, bottom)

        # By MFC requirement, ControlBar objects should be survived until frame have destroyed.
        self.controlbars.append(cbar)

    def _create(self,
            style, className, windowName,
            x=None, y=None, w=None, h=None, 
            parent=None, idOrHMenu=0):
        
        if x is None: x = CW_USEDEFAULT
        if y is None: y = CW_USEDEFAULT
        if w is None: w = CW_USEDEFAULT
        if h is None: h = CW_USEDEFAULT
        
        cdef HWND hParent
        if parent is None:
            hParent = NULL
        elif PyMFCHandle_IsHandle(parent):
            hParent = PyMFCHandle_AsHandle(parent)
        else:
            hParent =  PyMFCHandle_AsHandle(parent.getHwnd())

        cdef void *hmenu
        if PyMFCHandle_IsHandle(idOrHMenu):
            hmenu = PyMFCHandle_AsHandle(idOrHMenu)
        else:
            hmenu = PyLong_AsVoidPtr(idOrHMenu)
        
        CFrame_CreateWnd(self._cwnd, style.exStyle, PyUnicode_AsUnicode(className), 
            PyUnicode_AsUnicode(windowName), style.style, x, y, w, h, 
            hParent, hmenu)

    def showControlBar(self, bar, show, delay):
        CFrame_ShowControlBar(self._cwnd, PyMFCPtr_AsVoidPtr(bar.cwnd), show, delay)
        

cdef class _mdiframe(_frame):
    cdef void *newInstance(self):
        return new_MDIFrame(self)

    def getActive(self):
        return CMDIFrame_GetActive(self._cwnd)

cdef class _mdichild(_frame):
    cdef void *newInstance(self):
        return new_MDIChild(self)

cdef class _dialog(_WndBase):
    cdef void *newInstance(self):
        return new_Dialog(self)

    def _doModal(self, style, title, width, height, left, top, font, fontsize):
        if left is None or top is None:
            left = top = 0
            center = 1
        else:
            center = 0
        
        return CDialog_DoModal(self._cwnd, left,  top, width, height, 
                   style, PyUnicode_AsUnicode(title), PyUnicode_AsUnicode(font), fontsize, center)
    
    def endDialog(self, result):
        CDialog_EndDialog(self._cwnd, result)


    def _createDialog(self, parent, style, title, width, height, left, top, font, fontsize):
        cdef void * p
        
        
        if left is None or top is None:
            left = top = 0
            center = 1
        else:
            center = 0

        p = NULL
        if parent:  
            p = PyMFCPtr_AsVoidPtr(parent.cwnd)
            
        return CDialog_Create(self._cwnd, p, left, top, width, height, 
                   style, PyUnicode_AsUnicode(title), PyUnicode_AsUnicode(font), fontsize, center)
    
        
cdef extern from *:
    # Dialog styles
    int DS_ABSALIGN, DS_MODALFRAME, DS_NOIDLEMSG, DS_SETFOREGROUND
    int DS_3DLOOK, DS_FIXEDSYS, DS_NOFAILCREATE, DS_CONTROL, DS_CENTER
    int DS_CENTERMOUSE, DS_CONTEXTHELP

cdef __init_dialog_styles():
    ret = {
    "absalign":DS_ABSALIGN,
    "modalframe":DS_MODALFRAME,
    "noidlemsg":DS_NOIDLEMSG,
    "setforeground":DS_SETFOREGROUND,
    "threedlook":DS_3DLOOK,
    "fixedsys":DS_FIXEDSYS,
    "nofailcreate":DS_NOFAILCREATE,
    "control":DS_CONTROL,
    "center":DS_CENTER,
    "centermouse":DS_CENTERMOUSE,
    "contexthelp":DS_CONTEXTHELP,
    }
    
    ret.update(_std_styles)
    return ret
_dialog_styles = __init_dialog_styles()

cdef class DlgStyle(WndStyle):
    def _initTable(self):
        self._styles = _dialog_styles



cdef extern from "pymwnd.h":
    void *new_FileDialog(object obj) except NULL
    object CFileDialog_DoModal(void *o, int open, void *parent,
            TCHAR *title, TCHAR *filename, TCHAR *defext,
            TCHAR *initdir, TCHAR *filter, 
            int filterindex,
            int height, int readonly, int overwriteprompt, int hidereadonly, 
            int nochangedir, int showhelp, int novalidate, int allowmultiselect, 
            int extensiondifferent, int pathmustexist, int filemustexist, 
            int createprompt, int shareaware, int noreadonlyreturn, int notestfilecreate, 
            int nonetworkbutton, int nodereferencelinks, 
            int enableincludenotify, int enablesizing)

cdef class _filedialog(_WndBase):
    cdef void *newInstance(self):
        return new_FileDialog(self)

    def _doModal(self, open=1, parent=None,
        title='', filename='', defext='', 
        initdir='', filter='', 
        filterindex=0, height=0, readonly=0, overwriteprompt=0, 
        hidereadonly=0, nochangedir=0, showhelp=0, novalidate=0, allowmultiselect=0,
        extensiondifferent=0, pathmustexist=0, filemustexist=0, 
        createprompt=0, shareaware=0, noreadonlyreturn=0, notestfilecreate=0,
        nonetworkbutton=0, nodereferencelinks=0, 
        enableincludenotify=0, enablesizing=0):
        
        cdef void *p
        
        if not parent:
            p = NULL
        else:
            p = PyMFCPtr_AsVoidPtr(parent.cwnd)

        if not title: title = unicode('')
        if not filename: filename = unicode('')
        if not defext: defext = unicode('')
        if not initdir: initdir = unicode('')
        if not filter: filter = unicode('')

        return CFileDialog_DoModal(self._cwnd, open, p,
            PyUnicode_AsUnicode(title), PyUnicode_AsUnicode(filename), 
            PyUnicode_AsUnicode(defext), PyUnicode_AsUnicode(initdir), PyUnicode_AsUnicode(filter), 
            filterindex, height, readonly, overwriteprompt, 
            hidereadonly, nochangedir, showhelp, novalidate, allowmultiselect,
            extensiondifferent, pathmustexist, filemustexist, 
            createprompt, shareaware, noreadonlyreturn, notestfilecreate,
            nonetworkbutton, nodereferencelinks, 
            enableincludenotify, enablesizing)

cdef extern from "pymwnd.h":
    void *new_ColorDialog(object obj) except NULL
    object CColorDialog_DoModal(void *o, void *parent,
            COLORREF color, int rgbinit, int anycolor, int fullopen, int preventfullopen, 
            int showhelp, int solidcolor, int height)


cdef class _colordialog(_WndBase):
    cdef void *newInstance(self):
        return new_ColorDialog(self)

    def _doModal(self, parent=None,
        color=None, int anycolor=0, int fullopen=0, int preventfullopen=0, 
        int showhelp=0, int solidcolor=0, height=0):
        
        cdef int rgbinit
        cdef void *p
        
        if not parent:
            p = NULL
        else:
            p = PyMFCPtr_AsVoidPtr(parent.cwnd)
        
        if color is None:
            color = 0
            rgbinit = 0
        else:
            rgbinit = 1

        return CColorDialog_DoModal(self._cwnd, p,
            color, rgbinit, anycolor, fullopen, preventfullopen,
            showhelp, solidcolor, height)

cdef extern from "pymwnd.h":
    void *new_FontDialog(object obj) except NULL
    object CFontDialog_DoModal(void *o, void *parent, HDC hdc, LOGFONT *logfont,
        unsigned long flag, unsigned long color, TCHAR *style, long sizemin, long sizemax,
        LOGFONT *ret, unsigned long *retColor, long *retPoint)

    int CF_APPLY, CF_ANSIONLY, CF_BOTH, CF_TTONLY, CF_EFFECTS
    int CF_ENABLEHOOK, CF_ENABLETEMPLATE, CF_ENABLETEMPLATEHANDLE
    int CF_FIXEDPITCHONLY, CF_FORCEFONTEXIST
    int CF_INITTOLOGFONTSTRUCT, CF_LIMITSIZE, CF_NOOEMFONTS
    int CF_NOFACESEL, CF_NOSCRIPTSEL, CF_NOSTYLESEL, CF_NOSIZESEL
    int CF_NOSIMULATIONS, CF_NOVECTORFONTS, CF_NOVERTFONTS
    int CF_PRINTERFONTS, CF_SCALABLEONLY, CF_SCREENFONTS
    int CF_SCRIPTSONLY, CF_SELECTSCRIPT, CF_SHOWHELP, CF_USESTYLE
    int CF_WYSIWYG
    
cdef class _fontdialog(_WndBase):
    cdef public int selectedColor
    cdef void *newInstance(self):
        return new_FontDialog(self)

    def _doModal(self, parent=None, dc=None, logfont=None, color=0, style=None,
        int apply=0, int both=0, int ttonly=0, int effects=0, int fixedpitchonly=0, 
        int forcefontexist=0, int nooemfonts=0, int nofacesel=0, int noscriptsel=0, 
        int nostylesel=0, int nosizesel=0, int nosimulations=0, int novectorfonts=0, 
        int novertfonts=0, int printerfonts=0, int scalableonly=0, int screenfonts=0,
        int scriptsonly=0, int selectscript=0, int showhelp=0, int wysiwyg=0, 
        limitsize=None):
        
        cdef HDC hdc
        cdef unsigned long flag, retcolor
        cdef long sizemax, sizemin, retpoint
        cdef LOGFONT lf, ret, *plogfont
        cdef void *pparent
        
        if not parent:
            pparent = NULL
        else:
            pparent = PyMFCPtr_AsVoidPtr(parent.cwnd)
        
        if not style:
            style = unicode("", "ascii")
        hdc = NULL
        if dc:
            hdc = PyMFCHandle_AsHandle(dc.getHandle())

        flag = 0
        if apply:
            flag = flag | CF_APPLY
        if both:
            flag = flag | CF_BOTH
        if ttonly:
            flag = flag | CF_TTONLY
        if effects:
            flag = flag | CF_EFFECTS
        if fixedpitchonly:
            flag = flag | CF_FIXEDPITCHONLY
        if forcefontexist:
            flag = flag | CF_FORCEFONTEXIST
        if nooemfonts:
            flag = flag | CF_NOOEMFONTS
        if nofacesel:
            flag = flag | CF_NOFACESEL
        if noscriptsel:
            flag = flag | CF_NOSCRIPTSEL
        if nostylesel:
            flag = flag | CF_NOSTYLESEL
        if nosizesel:
            flag = flag | CF_NOSIZESEL
        if nosimulations:
            flag = flag | CF_NOSIMULATIONS
        if novectorfonts:
            flag = flag | CF_NOVECTORFONTS
        if novertfonts:
            flag = flag | CF_NOVERTFONTS
        if printerfonts:
            flag = flag | CF_PRINTERFONTS
        if scalableonly:
            flag = flag | CF_SCALABLEONLY
        if screenfonts:
            flag = flag | CF_SCREENFONTS
        if scriptsonly:
            flag = flag | CF_SCRIPTSONLY
        if selectscript:
            flag = flag | CF_SELECTSCRIPT
        if showhelp:
            flag = flag | CF_SHOWHELP
        if wysiwyg:
            flag = flag | CF_WYSIWYG

        sizemin = 0
        sizemax = 0
        if limitsize:
            sizemin = limitsize[0]
            sizemax = limitsize[1]
            flag = flag | CF_LIMITSIZE

        plogfont = NULL
        if logfont:
            plogfont = <LOGFONT *>PyMFCPtr_AsVoidPtr(logfont.getLogFont())
            flag = flag | CF_INITTOLOGFONTSTRUCT

        if style:
            flag = flag | CF_USESTYLE
        
        if CFontDialog_DoModal(self._cwnd, pparent,
            hdc, plogfont, flag, color, PyUnicode_AsUnicode(style), sizemin, sizemax,
            &ret, &retcolor, &retpoint):
            
            self.selectedColor = retcolor
            self.selectedPoint = retpoint/10
            return pymfc.gdi.LogFont(buffer=PyMFCPtr_FromVoidPtr(&ret))

cdef extern from "pymwnd.h":
    ctypedef struct PRINTDLG:
        DWORD lStructSize
        HWND hwndOwner
        HGLOBAL hDevMode
        HGLOBAL hDevNames
        HDC hDC
        DWORD Flags
        WORD nFromPage
        WORD nToPage
        WORD nMinPage
        WORD nMaxPage
        WORD nCopies
        HINSTANCE hInstance
        LPARAM lCustData
        void *lpfnPrintHook
        void *lpfnSetupHook
        LPCTSTR lpPrintTemplateName
        LPCTSTR lpSetupTemplateName
        HGLOBAL hPrintTemplate
        HGLOBAL hSetupTemplate

    void *new_PrintDialog(object obj) except NULL
    PRINTDLG *CPrintDialog_DoModal(void *o, void *parent,
        HGLOBAL devmode, HGLOBAL devnames, DWORD flags, WORD frompage,
        WORD topage, WORD minpage, WORD maxpage, WORD copies) except *

    int PD_ALLPAGES, PD_SELECTION, PD_PAGENUMS, PD_NOSELECTION, PD_NOPAGENUMS,
    int PD_COLLATE, PD_PRINTTOFILE, PD_PRINTSETUP, PD_NOWARNING, PD_RETURNDC,
    int PD_RETURNIC, PD_RETURNDEFAULT, PD_SHOWHELP, PD_ENABLEPRINTHOOK,
    int PD_ENABLESETUPHOOK, PD_ENABLEPRINTTEMPLATE, PD_ENABLESETUPTEMPLATE,
    int PD_ENABLEPRINTTEMPLATEHANDLE, PD_ENABLESETUPTEMPLATEHANDLE,
    int PD_USEDEVMODECOPIES, PD_USEDEVMODECOPIESANDCOLLATE,
    int PD_DISABLEPRINTTOFILE, PD_HIDEPRINTTOFILE, PD_NONETWORKBUTTON




cdef class _printdialog(_WndBase):
    cdef readonly object dc
    cdef readonly object devmove, devicename
    cdef readonly int allpages, selection, pagenums, frompage, topage, ncopies, defaultprinter
    
    cdef void *newInstance(self):
        return new_PrintDialog(self)

    def _doModal(self, parent=None, devmode=None, devicename=None,
        allpages=1, selection=0, pagenums=0, noselection=1, nopagenums=1,
        collate=0, printtofile=0, printsetup=0, nowarning=0, returndc=0,
        returnic=0, returndefault=0, showhelp=0,
        usedevmodecopies=1, disableprinttofile=0, hideprinttofile=1, 
        nonetworkbutton=0,
        frompage=0, topage=0, minpage=0, maxpage=0, ncopies=1):
        
        cdef unsigned long flags
        cdef PRINTDLG *printdlg
        cdef void *pparent
        cdef HANDLE hdevmode
        cdef HANDLE hdevnames
        cdef DEVMODE *pdevmode, *psrcdevmode
        cdef DEVNAMES *pdevnames
        cdef int devnamessize
        
        if not parent:
            pparent = NULL
        else:
            pparent = PyMFCPtr_AsVoidPtr(parent.cwnd)
        
        flags = 0
        if allpages:
            flags = flags | PD_ALLPAGES
        if selection:
            flags = flags | PD_SELECTION
        if pagenums:
            flags = flags | PD_PAGENUMS
        if noselection:
            flags = flags | PD_NOSELECTION
        if nopagenums:
            flags = flags | PD_NOPAGENUMS
        if collate:
            flags = flags | PD_COLLATE
        if printtofile:
            flags = flags | PD_PRINTTOFILE
        if printsetup:
            flags = flags | PD_PRINTSETUP
        if nowarning:
            flags = flags | PD_NOWARNING
        if returndc:
            flags = flags | PD_RETURNDC
        if returnic:
            flags = flags | PD_RETURNIC
        if returndefault:
            flags = flags | PD_RETURNDEFAULT
        if showhelp:
            flags = flags | PD_SHOWHELP
        if usedevmodecopies:
            flags = flags | PD_USEDEVMODECOPIES
        if disableprinttofile:
            flags = flags | PD_DISABLEPRINTTOFILE
        if hideprinttofile:
            flags = flags | PD_HIDEPRINTTOFILE
        if nonetworkbutton:
            flags = flags | PD_NONETWORKBUTTON
        
        hdevmode = NULL
        hdevnames = NULL
        try:
            if devmode:
                psrcdevmode = <DEVMODE*>PyMFCPtr_AsVoidPtr(devmode.getPtr())
                hdevmode = <HANDLE>GlobalAlloc(GMEM_MOVEABLE, psrcdevmode.dmSize)
                if hdevmode == NULL:
                    pymRaiseWin32Err()
                pdevmode = <DEVMODE*>GlobalLock(hdevmode)
                if not pdevmode:
                    pymRaiseWin32Err()
                try:
                    memcpy(pdevmode, psrcdevmode, psrcdevmode.dmSize)
                finally:
                    GlobalUnlock(hdevmode)
            if devicename:
                devnamessize = sizeof(DEVNAMES)+(len(devicename)+3)*sizeof(TCHAR)
                hdevnames = <HANDLE>GlobalAlloc(GMEM_MOVEABLE, devnamessize)
                if hdevnames == NULL:
                    pymRaiseWin32Err()
                pdevnames = <DEVNAMES*>GlobalLock(hdevnames)
                if not pdevnames:
                    pymRaiseWin32Err()
                try:
                    memset(pdevnames, 0, devnamessize)
                    pdevnames.wDriverOffset = sizeof(DEVNAMES)/sizeof(TCHAR)
                    pdevnames.wDeviceOffset = pdevnames.wDriverOffset+1
                    pdevnames.wOutputOffset = pdevnames.wDeviceOffset+len(devicename)+1
                    memcpy((<LPTSTR>pdevnames)+pdevnames.wDeviceOffset,
                        PyUnicode_AsUnicode(devicename), len(devicename)*sizeof(TCHAR))
                finally:
                    GlobalUnlock(hdevnames)

            printdlg = CPrintDialog_DoModal(self._cwnd, pparent,
                hdevmode, hdevnames, flags, frompage, topage, minpage, maxpage, ncopies)

            if printdlg:
                hdevmode = printdlg.hDevMode
                pdevmode = <DEVMODE*>GlobalLock(hdevmode)
                try:
                    self.devmode = pymfc.gdi.DevMode(ptr=PyMFCPtr_FromVoidPtr(pdevmode))
                finally:
                    GlobalUnlock(hdevmode)
                
                hdevnames = printdlg.hDevNames
                if hdevnames:
                    pdevnames = <DEVNAMES*>GlobalLock(hdevnames)
                    if not pdevnames:
                        pymRaiseWin32Err()

                    try:
                        self.devicename = _fromWideChar((<LPCTSTR>pdevnames)+pdevnames.wDeviceOffset)
                        self.defaultprinter = pdevnames.wDefault
                    finally:
                        GlobalUnlock(hdevnames)

                self.allpages = printdlg.Flags & PD_ALLPAGES
                self.selection = printdlg.Flags & PD_SELECTION
                self.pagenums = printdlg.Flags & PD_PAGENUMS
                self.frompage = printdlg.nFromPage
                self.topage = printdlg.nToPage
                self.ncopies = printdlg.nCopies

                if printdlg.hDC:
                    self.dc = pymfc.gdi.DC(hdc=PyMFCHandle_FromHandle(printdlg.hDC), own=1)
                else:
                    self.dc = None
                
                return self
        finally:
            if hdevmode:
                GlobalFree(hdevmode)
            if hdevnames:
                GlobalFree(hdevnames)
                

cdef class _propertypage(_WndBase):
    cdef void *newInstance(self):
        return new_PropertyPage(self)
    
    def _create(self, width, height, style, title, font, fontsize):
        CPropertyPage_Create(self._cwnd, width, height, style.style, 
            PyUnicode_AsUnicode(title), PyUnicode_AsUnicode(font), fontsize)


cdef class _propertysheet(_WndBase):
    cdef void *newInstance(self):
        return new_PropertySheet(self)
    
    def addPage(self, page):
        CPropertySheet_AddPage(self._cwnd, PyMFCPtr_AsVoidPtr(page.cwnd))
    
    def _doModal(self, parent, title, selpage=0):
        cdef void *p
        if parent:
            p = PyMFCPtr_AsVoidPtr(parent.cwnd)
        else:
            p = NULL
        return CPropertySheet_DoModal(self._cwnd, p, PyUnicode_AsUnicode(title), selpage)


def _getDesktopWindow():
    return PyMFCHandle_FromHandle(GetDesktopWindow())
