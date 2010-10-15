cdef extern from "pymgdi.h":

    # LoadImage
    HANDLE pymLoadImage(int type,  TCHAR *filename,
        int cx, int cy, int defaultcolor, int createdibsection,
        int defaultsize, int loadmap3dcolors, int loadtransparent,
        int monochrome, int vgacolor) except NULL

    int IMAGE_BITMAP, IMAGE_ICON

    int DeleteObject(void *obj) except 0
    

    int GetObject(HGDIOBJ hgdiobj, int cbBuffer, void* lpvObject)


cdef extern from "windows.h":
    int ANSI_FIXED_FONT, ANSI_VAR_FONT, DEVICE_DEFAULT_FONT, DEFAULT_GUI_FONT
    int OEM_FIXED_FONT, SYSTEM_FONT, DEFAULT_PALETTE
    
    HGDIOBJ GetStockObject(int fnObject)
    HFONT CreateFont(int nHeight, int nWidth, int nEscapement, 
        int nOrientation, int fnWeight, DWORD fdwItalic, 
        DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, 
        DWORD fdwOutputPrecision, DWORD fdwClipPrecision, 
        DWORD fdwQuality, DWORD fdwPitchAndFamily, TCHAR *lpszFace)

    HFONT CreateFontIndirect(LOGFONT *lf)

cdef class LogFont:
    cdef LOGFONT lf
    
    def __init__(self, object logfont=None, buffer=0, point=None, dc=None, **kwargs):
        cdef LOGFONT *p
        cdef LogFont lf
        cdef long wk
        
        if isinstance(logfont, LogFont):
            lf = logfont
            self.lf = lf.lf
        elif buffer:
             p = <LOGFONT*>PyMFCPtr_AsVoidPtr(buffer)
             self.lf = p[0]
        else:
            for name, value in kwargs.items():
                setattr(self, name, value)
        
        if point is not None:
            if dc is None:
                _dc = DesktopDC()
            else:
                _dc = dc
            
            try:
                self.lf.lfHeight = _dc.pointToLp(point)*-1
            finally:
                if dc is None:
                    _dc.release()
        
    property height:
        def __get__(self):
            return self.lf.lfHeight
        def __set__(self, int v):
            self.lf.lfHeight = v

    property width:
        def __get__(self):
            return self.lf.lfWidth
        def __set__(self, int v):
            self.lf.lfWidth = v

    property escapement:
        def __get__(self):
            return self.lf.lfEscapement
        def __set__(self, int v):
            self.lf.lfEscapement = v

    property orientation:
        def __get__(self):
            return self.lf.lfOrientation
        def __set__(self, int v):
            self.lf.lfOrientation = v

    property weight:
        def __get__(self):
            return self.lf.lfWeight
        def __set__(self, int v):
            self.lf.lfWeight = v

    property italic:
        def __get__(self):
            return self.lf.lfItalic
        def __set__(self, int v):
            self.lf.lfItalic = v

    property underline:
        def __get__(self):
            return self.lf.lfUnderline
        def __set__(self, int v):
            self.lf.lfUnderline = v

    property strikeout:
        def __get__(self):
            return self.lf.lfStrikeOut
        def __set__(self, int v):
            self.lf.lfStrikeOut = v

    property ansi_charset:
        def __get__(self):
            return self.lf.lfCharSet == ANSI_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = ANSI_CHARSET

    property baltic_charset:
        def __get__(self):
            return self.lf.lfCharSet == BALTIC_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = BALTIC_CHARSET

    property chinesebig5_charset:
        def __get__(self):
            return self.lf.lfCharSet == CHINESEBIG5_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = CHINESEBIG5_CHARSET

    property default_charset:
        def __get__(self):
            return self.lf.lfCharSet == DEFAULT_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = DEFAULT_CHARSET

    property easteurope_charset:
        def __get__(self):
            return self.lf.lfCharSet == EASTEUROPE_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = EASTEUROPE_CHARSET

    property gb2312_charset:
        def __get__(self):
            return self.lf.lfCharSet == GB2312_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = GB2312_CHARSET

    property greek_charset:
        def __get__(self):
            return self.lf.lfCharSet == GREEK_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = GREEK_CHARSET

    property hangul_charset:
        def __get__(self):
            return self.lf.lfCharSet == HANGUL_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = HANGUL_CHARSET

    property mac_charset:
        def __get__(self):
            return self.lf.lfCharSet == MAC_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = MAC_CHARSET

    property oem_charset:
        def __get__(self):
            return self.lf.lfCharSet == OEM_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = OEM_CHARSET

    property russian_charset:
        def __get__(self):
            return self.lf.lfCharSet == RUSSIAN_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = RUSSIAN_CHARSET

    property shiftjis_charset:
        def __get__(self):
            return self.lf.lfCharSet == SHIFTJIS_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = SHIFTJIS_CHARSET

    property symbol_charset:
        def __get__(self):
            return self.lf.lfCharSet == SYMBOL_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = SYMBOL_CHARSET

    property turkish_charset:
        def __get__(self):
            return self.lf.lfCharSet == TURKISH_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = TURKISH_CHARSET

    property johab_charset:
        def __get__(self):
            return self.lf.lfCharSet == JOHAB_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = JOHAB_CHARSET

    property hebrew_charset:
        def __get__(self):
            return self.lf.lfCharSet == HEBREW_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = HEBREW_CHARSET

    property arabic_charset:
        def __get__(self):
            return self.lf.lfCharSet == ARABIC_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = ARABIC_CHARSET

    property thai_charset:
        def __get__(self):
            return self.lf.lfCharSet == THAI_CHARSET
        def __set__(self, int v):
            if v:
                self.lf.lfCharSet = THAI_CHARSET


    property out_character_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_CHARACTER_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_CHARACTER_PRECIS

    property out_default_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_DEFAULT_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_DEFAULT_PRECIS

    property out_device_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_DEVICE_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_DEVICE_PRECIS

    property out_outline_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_OUTLINE_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_OUTLINE_PRECIS

    property out_raster_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_RASTER_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_RASTER_PRECIS

    property out_string_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_STRING_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_STRING_PRECIS

    property out_stroke_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_STROKE_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_STROKE_PRECIS

    property out_tt_only_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_TT_ONLY_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_TT_ONLY_PRECIS

    property out_tt_precis:
        def __get__(self):
            return self.lf.lfOutPrecision == OUT_TT_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfOutPrecision = OUT_TT_PRECIS

    property clip_default_precis:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_DEFAULT_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_DEFAULT_PRECIS

    property clip_character_precis:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_CHARACTER_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_CHARACTER_PRECIS

    property clip_stroke_precis:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_STROKE_PRECIS
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_STROKE_PRECIS
        
    property clip_mask:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_MASK
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_MASK
        
    property clip_embedded:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_EMBEDDED
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_EMBEDDED
        
    property clip_lh_angles:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_LH_ANGLES
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_LH_ANGLES
        
    property clip_tt_always:
        def __get__(self):
            return self.lf.lfClipPrecision == CLIP_TT_ALWAYS
        def __set__(self, int v):
            if v:
                self.lf.lfClipPrecision = CLIP_TT_ALWAYS

    property default_quality:
        def __get__(self):
            return self.lf.lfQuality == DEFAULT_QUALITY
        def __set__(self, int v):
            if v:
                self.lf.lfQuality = DEFAULT_QUALITY

    property draft_quality:
        def __get__(self):
            return self.lf.lfQuality == DRAFT_QUALITY
        def __set__(self, int v):
            if v:
                self.lf.lfQuality = DRAFT_QUALITY

    property proof_quality:
        def __get__(self):
            return self.lf.lfQuality == PROOF_QUALITY
        def __set__(self, int v):
            if v:
                self.lf.lfQuality = PROOF_QUALITY

    property default_pitch:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0x3 == DEFAULT_PITCH
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = (self.lf.lfPitchAndFamily & 0xfc) | DEFAULT_PITCH
    property fixed_pitch:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0x3 == FIXED_PITCH
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = (self.lf.lfPitchAndFamily & 0xfc) | FIXED_PITCH

    property variable_pitch:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0x3 == VARIABLE_PITCH
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = (self.lf.lfPitchAndFamily & 0xfc) | VARIABLE_PITCH

    property ff_decorative:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_DECORATIVE
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_DECORATIVE)

    property ff_dontcare:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_DONTCARE
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_DONTCARE)

    property ff_modern:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_MODERN
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_MODERN)

    property ff_roman:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_ROMAN
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_ROMAN)

    property ff_script:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_SCRIPT
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_SCRIPT)

    property ff_swiss:
        def __get__(self):
            return self.lf.lfPitchAndFamily & 0xf8 == FF_SWISS
        def __set__(self, int v):
            if v:
                self.lf.lfPitchAndFamily = <BYTE>((self.lf.lfPitchAndFamily & 0x7) | FF_SWISS)

    property facename:
        def __get__(self):
            return _fromWideChar(self.lf.lfFaceName)
        def __set__(self, v):
            if len(v) >= LF_FACESIZE:
                raise ValueError(" face name too long")
            _tcsncpy(self.lf.lfFaceName, PyUnicode_AsUnicode(v), LF_FACESIZE)

    def getLogFont(self):
        return PyMFCPtr_FromVoidPtr(&self.lf)

    def getBuffer(self):
        return PyMFCPtr_FromVoidPtr(&self.lf)


cdef class _Font:
    cdef HFONT _hFont
    cdef public int temp

    property hFont:
        def __get__(self):
            return PyMFCHandle_FromHandle(self._hFont)
        def __set__(self, value):
            self._hFont = PyMFCHandle_AsHandle(value)
        
    def __init__(self, hfont=None, int own=0, logfont=None,
            height=None, width=None, escapement=None, 
            orientation=None, weight=None, italic=None, 
            underline=None, strikeout=None,
            
            int ansi_charset=0, int baltic_charset=0, 
            int chinesebig5_charset=0, int default_charset=0, 
            int easteurope_charset=0, int gb2312_charset=0,
            int greek_charset=0, int hangul_charset=0, int mac_charset=0,
            int oem_charset=0, int russian_charset=0, int shiftjis_charset=0,
            int symbol_charset=0, int turkish_charset=0, int johab_charset=0,
            int hebrew_charset=0, int arabic_charset=0, int thai_charset=0,
            
            int out_character_precis=0, int out_default_precis=0,
            int out_device_precis=0, int out_outline_precis=0,
            int out_raster_precis=0, int out_string_precis=0,
            int out_stroke_precis=0, int out_tt_only_precis=0,
            int out_tt_precis=0,
            
            int clip_default_precis=0, int clip_character_precis=0,
            int clip_stroke_precis=0, int clip_mask=0, int clip_embedded=0,
            int clip_lh_angles=0, int clip_tt_always=0,
            
            int default_quality=0, int draft_quality=0, int proof_quality=0,

            int default_pitch=0, int fixed_pitch=0, int variable_pitch=0,

            int ff_decorative=0, int ff_dontcare=0, int ff_modern=0, 
            int ff_roman=0, int ff_script=0, int ff_swiss=0,

            family=0, face=None, point=None, dc=None):

        cdef LOGFONT lf
        cdef LogFont _logfont
        memset(&lf, 0, sizeof(lf))

        if hfont:
            self._hFont = PyMFCHandle_AsHandle(hfont)
            if not own:
                self.temp = True
            return
        
        if logfont:
            _logfont = logfont
            lf = _logfont.lf

        if height is not None:
            lf.lfHeight = height

        if point is not None:
            if dc is None:
                _dc = DesktopDC()
            else:
                _dc = dc
            
            try:
                lf.lfHeight = _dc.pointToLp(point)*-1
            finally:
                if dc is None:
                    _dc.release()

        if width is not None:
            lf.lfWidth = width

        if escapement is not None:
            lf.lfEscapement =escapement

        if orientation is not None:
            lf.lfOrientation = orientation

        if weight is not None:
            lf.lfWeight = weight

        if italic is not None:
            if italic:
                lf.lfItalic = 1
            else:
                lf.lfItalic = 0

        if underline is not None:
            if underline:
                lf.lfUnderline = 1
            else:
                lf.lfUnderline = 0

        if strikeout is not None:
            if strikeout:
                lf.lfStrikeOut = 1
            else:
                lf.lfStrikeOut = 0

        if ansi_charset:
            lf.lfCharSet = ANSI_CHARSET
        elif baltic_charset:
            lf.lfCharSet = BALTIC_CHARSET
        elif chinesebig5_charset:
            lf.lfCharSet = CHINESEBIG5_CHARSET
        elif default_charset:
            lf.lfCharSet = DEFAULT_CHARSET
        elif easteurope_charset:
            lf.lfCharSet = EASTEUROPE_CHARSET
        elif gb2312_charset:
            lf.lfCharSet = GB2312_CHARSET
        elif greek_charset:
            lf.lfCharSet = GREEK_CHARSET
        elif hangul_charset:
            lf.lfCharSet = HANGUL_CHARSET
        elif mac_charset:
            lf.lfCharSet = MAC_CHARSET
        elif oem_charset:
            lf.lfCharSet = OEM_CHARSET
        elif russian_charset:
            lf.lfCharSet = RUSSIAN_CHARSET
        elif shiftjis_charset:
            lf.lfCharSet = SHIFTJIS_CHARSET
        elif symbol_charset:
            lf.lfCharSet = SYMBOL_CHARSET
        elif turkish_charset :
            lf.lfCharSet = TURKISH_CHARSET 
        elif johab_charset :
            lf.lfCharSet = JOHAB_CHARSET 
        elif hebrew_charset:
            lf.lfCharSet = HEBREW_CHARSET
        elif arabic_charset :
            lf.lfCharSet = ARABIC_CHARSET 
        elif thai_charset :
            lf.lfCharSet = THAI_CHARSET 

        if out_character_precis:
            lf.lfOutPrecision = OUT_CHARACTER_PRECIS
        elif out_default_precis:
            lf.lfOutPrecision = OUT_DEFAULT_PRECIS
        elif out_device_precis:
            lf.lfOutPrecision = OUT_DEVICE_PRECIS
        elif out_outline_precis:
            lf.lfOutPrecision = OUT_OUTLINE_PRECIS
        elif out_raster_precis:
            lf.lfOutPrecision = OUT_RASTER_PRECIS
        elif out_string_precis:
            lf.lfOutPrecision = OUT_STRING_PRECIS
        elif out_stroke_precis:
            lf.lfOutPrecision = OUT_STROKE_PRECIS
        elif out_tt_only_precis:
            lf.lfOutPrecision = OUT_TT_ONLY_PRECIS
        elif out_tt_precis:
            lf.lfOutPrecision = OUT_TT_PRECIS

        if clip_default_precis:
            lf.lfClipPrecision = CLIP_DEFAULT_PRECIS
        elif clip_character_precis:
            lf.lfClipPrecision = CLIP_CHARACTER_PRECIS
        elif clip_stroke_precis:
            lf.lfClipPrecision = CLIP_STROKE_PRECIS
        elif clip_mask:
            lf.lfClipPrecision = CLIP_MASK
        elif clip_embedded:
            lf.lfClipPrecision = CLIP_EMBEDDED
        elif clip_lh_angles:
            lf.lfClipPrecision = CLIP_LH_ANGLES
        elif clip_tt_always:
            lf.lfClipPrecision = CLIP_TT_ALWAYS

        if default_quality:
            lf.lfQuality = DEFAULT_QUALITY
        elif draft_quality:
            lf.lfQuality = DRAFT_QUALITY
        elif proof_quality:
            lf.lfQuality = PROOF_QUALITY

        if default_pitch:
            lf.lfPitchAndFamily = DEFAULT_PITCH
        elif fixed_pitch:
            lf.lfPitchAndFamily = FIXED_PITCH
        elif variable_pitch:
            lf.lfPitchAndFamily = VARIABLE_PITCH 

        if ff_decorative:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_DECORATIVE)
        if ff_dontcare:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_DONTCARE)
        if ff_modern:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_MODERN)
        if ff_roman:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_ROMAN)
        if ff_script:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_SCRIPT)
        if ff_swiss:
            lf.lfPitchAndFamily = <BYTE>(lf.lfPitchAndFamily | FF_SWISS)

        if face is not None:
            _tcsncpy(lf.lfFaceName, PyUnicode_AsUnicode(face), LF_FACESIZE)

        self._hFont = CreateFontIndirect(&lf)
        if self._hFont == NULL:
            pymRaiseWin32Err()

    def __dealloc__(self):
        if self._hFont and not self.temp:
            DeleteObject(self._hFont)

    def detach(self):
        ret = PyMFCHandle_FromHandle(self._hFont)
        self._hFont = NULL
        return ret

    def getHandle(self):
        return PyMFCHandle_FromHandle(self._hFont)

    def getLogFont(self):
        cdef LogFont lf
        lf = LogFont()
        if not GetObject(self._hFont, sizeof(LOGFONT), <void *>(&(lf.lf))):
            pymRaiseWin32Err()
            
        return lf

    def getTextMetrics(self, dc=None):
        _dc = dc
        if dc is None:
            _dc = DesktopDC()
        try:
            _orgfont = _dc.selectObject(self)
            try:
                return _dc.getTextMetrics()
            finally:
                _dc.selectObject(_orgfont)
        finally:
            if dc is None:
                _dc.release()

class Font(_Font):
    pass

class StockFont(Font):
    def __init__(self, ansi_fixed=0, ansi_var=0, device_default=0, default_gui=0, oem_fixed=0, system=0):
        cdef int f
        cdef HGDIOBJ hobj
        f = 0
        if ansi_fixed:
            f = ANSI_FIXED_FONT
        elif ansi_var:
            f = ANSI_VAR_FONT
        elif device_default:
            f = DEVICE_DEFAULT_FONT
        elif default_gui:
            f = DEFAULT_GUI_FONT
        elif oem_fixed:
            f = OEM_FIXED_FONT
        elif system:
            f = SYSTEM_FONT

        self.hFont = PyMFCHandle_FromHandle(GetStockObject(f))
        if not self.hFont:
            pymRaiseWin32Err()
        self.temp=1


cdef void __init_font_charset():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.ansi = ANSI_CHARSET
    _const_gdi.baltic = BALTIC_CHARSET
    _const_gdi.chinesebig5 = CHINESEBIG5_CHARSET
    _const_gdi.default = DEFAULT_CHARSET
    _const_gdi.easteurope = EASTEUROPE_CHARSET
    _const_gdi.gb2312 = GB2312_CHARSET
    _const_gdi.greek = GREEK_CHARSET
    _const_gdi.hangul = HANGUL_CHARSET
    _const_gdi.mac = MAC_CHARSET
    _const_gdi.oem = OEM_CHARSET
    _const_gdi.russian = RUSSIAN_CHARSET
    _const_gdi.shiftjis = SHIFTJIS_CHARSET
    _const_gdi.symbol = SYMBOL_CHARSET
    _const_gdi.turkish = TURKISH_CHARSET
    _const_gdi.johab = JOHAB_CHARSET
    _const_gdi.hebrew = HEBREW_CHARSET
    _const_gdi.arabic = ARABIC_CHARSET
    _const_gdi.thai = THAI_CHARSET
    Font.charset =_const_gdi

cdef void __init_font_precis():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.character = OUT_CHARACTER_PRECIS
    _const_gdi.default = OUT_DEFAULT_PRECIS
    _const_gdi.device = OUT_DEVICE_PRECIS
    _const_gdi.outline = OUT_OUTLINE_PRECIS
    _const_gdi.raster = OUT_RASTER_PRECIS
    _const_gdi.string = OUT_STRING_PRECIS
    _const_gdi.stroke = OUT_STROKE_PRECIS
    _const_gdi.tt_only = OUT_TT_ONLY_PRECIS
    _const_gdi.tt = OUT_TT_PRECIS 
    Font.precis = _const_gdi

cdef void __init_font_clip():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.default = CLIP_DEFAULT_PRECIS
    _const_gdi.character = CLIP_CHARACTER_PRECIS
    _const_gdi.stroke = CLIP_STROKE_PRECIS
    _const_gdi.mask = CLIP_MASK
    _const_gdi.lh_angles = CLIP_LH_ANGLES
    _const_gdi.tt_always = CLIP_TT_ALWAYS
    _const_gdi.embedded = CLIP_EMBEDDED
    Font.clip = _const_gdi

cdef void __init_font_quality():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.default = DEFAULT_QUALITY
    _const_gdi.draft = DRAFT_QUALITY
    _const_gdi.proof = PROOF_QUALITY
    Font.quality = _const_gdi

cdef void __init_font_pitch():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.default = DEFAULT_PITCH
    _const_gdi.fixed = FIXED_PITCH
    _const_gdi.variable = VARIABLE_PITCH
    Font.pitch = _const_gdi

cdef void __init_font_family():
    cdef object _const_gdi
    _const_gdi = __CONSTDEF()
    _const_gdi.decorative = FF_DECORATIVE
    _const_gdi.dontcare = FF_DONTCARE
    _const_gdi.modern = FF_MODERN
    _const_gdi.roman = FF_ROMAN
    _const_gdi.script = FF_SCRIPT
    _const_gdi.swiss = FF_SWISS
    Font.family = _const_gdi

cdef void __init_font_consts():
    __init_font_charset()
    __init_font_precis()
    __init_font_clip()
    __init_font_quality()
    __init_font_pitch()
    __init_font_family()

__init_font_consts()



cdef extern from "windows.h":
    cdef unsigned long CLR_INVALID
    int DIB_PAL_COLORS, DIB_RGB_COLORS
    HDC GetDC(HWND hwnd)
    HDC GetWindowDC(HWND hwnd)
    HDC CreateDC(TCHAR *lpszDriver, TCHAR *lpszDevice, TCHAR *lpszOutput, DEVMODE *lpInitData)
    HDC CreateIC(TCHAR *lpszDriver, TCHAR *lpszDevice, TCHAR *lpszOutput, DEVMODE *lpInitData)
    int ReleaseDC(HWND hwnd, HDC hdc)
    HDC CreateCompatibleDC(HDC hdc)
    BOOL DeleteDC(HDC hdc)

    HGDIOBJ SelectObject(HDC hdc, HGDIOBJ obj)
    HPALETTE SelectPalette(HDC hdc, HPALETTE hPal, BOOL bForceBkgd)
    UINT RealizePalette(HDC hdc)

    
    
    
    HBITMAP CreateBitmap(int nWidth, int nHeight, UINT cPlanes, UINT cBitsPerPel, void *lpvBits)

    ctypedef struct BITMAP:
        int x
        LONG   bmType
        LONG   bmWidth
        LONG   bmHeight
        LONG   bmWidthBytes
        WORD   bmPlanes
        WORD   bmBitsPixel
        LPVOID bmBits

    ctypedef struct BITMAPINFOHEADER:
        DWORD      biSize
        LONG       biWidth
        LONG       biHeight
        WORD       biPlanes
        WORD       biBitCount
        DWORD      biCompression
        DWORD      biSizeImage
        LONG       biXPelsPerMeter
        LONG       biYPelsPerMeter
        DWORD      biClrUsed
        DWORD      biClrImportant

    ctypedef struct RGBQUAD:
        BYTE    rgbBlue
        BYTE    rgbGreen
        BYTE    rgbRed
        BYTE    rgbReserved

    ctypedef struct BITMAPINFO:
        BITMAPINFOHEADER    bmiHeader
        RGBQUAD             bmiColors[1]

    int BI_RGB, BI_RLE8, BI_RLE4, BI_BITFIELDS, BI_JPEG, BI_PNG
    int GetDIBits(HDC hdc, HBITMAP hbmp, UINT uStartScan, UINT cScanLines, void*lpvBits, BITMAPINFO *lpbi, UINT uUsage)
    int SetDIBitsToDevice(HDC hdc, int XDest, int YDest, DWORD dwWidth, DWORD dwHeight, int XSrc, int YSrc, 
        UINT uStartScan, UINT cScanLines, void *lpvBits, BITMAPINFO *lpbmi, UINT fuColorUse)



cdef class DIB:
    cdef public object header
    cdef public object bits

    cdef BITMAPINFO *_getbi(self):
        cdef char *p
        p = self.header
        return <BITMAPINFO *>p
        
    property height:
        def __get__(self):
            return self._getbi().bmiHeader.biHeight

    property width:
        def __get__(self):
            return self._getbi().bmiHeader.biWidth

    property bitcount:
        def __get__(self):
            return self._getbi().bmiHeader.biBitCount
    
    property compression:
        def __get__(self):
            return self._getbi().bmiHeader.biCompression


cdef class Bitmap:
    cdef HBITMAP _hBitmap
    cdef public int temp

    def __init__(self, hbmp=None, own=0, filename=None, cx=0, cy=0, 
            defaultcolor=0, createdibsection=0, defaultsize=0, 
            loadmap3dcolors=0, loadtransparent=0, monochrome=0, 
            vgacolor=0, panes=0, bitsperpel=0, bits=None):
        
        cdef void *newbmp
        cdef char *p
        
        if hbmp:
            self._hBitmap = PyMFCHandle_AsHandle(hbmp)
            if not own:
                self.temp = 1
            return
        
        if not filename:
            filename = unicode('')

        if bits:
            p = bits
            newbmp = CreateBitmap(cx, cy, panes, bitsperpel, p)
            if newbmp == NULL:
                pymRaiseWin32Err()

            self._hBitmap = newbmp
            return

        self._hBitmap = pymLoadImage(IMAGE_BITMAP, PyUnicode_AsUnicode(filename), cx, cy, defaultcolor, 
            createdibsection, defaultsize, loadmap3dcolors, loadtransparent,
            monochrome, vgacolor)

    def __dealloc__(self):
        if self._hBitmap and not self.temp:
            DeleteObject(self._hBitmap)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self._hBitmap)

    def detach(self):
        ret = PyMFCHandle_FromHandle(self._hBitmap)
        self._hBitmap = NULL
        self.temp = 0
        return ret

    cdef void getBITMAP(self, BITMAP *bmp):
        if 0 == GetObject(self._hBitmap, sizeof(BITMAP), <void*>bmp):
            pymRaiseWin32Err()
        
    def getSize(self):
        cdef BITMAP bmp
        self.getBITMAP(&bmp)
        return (bmp.bmWidth, bmp.bmHeight)

    def createDIB(self):
        cdef BITMAPINFO *bmpinfo
        cdef BITMAP bmp
        cdef long numcolor, headersize, nbits
        cdef HDC hDC
        cdef HPALETTE hPal, hOrgPal
        cdef int ret
        cdef char *c_buf
        cdef object buf, headerbuf
        cdef DIB dib
        
        hDC = NULL
        hOrgPal = NULL
        bmpinfo = NULL
        
        try:
            self.getBITMAP(&bmp)
            nbits = bmp.bmPlanes * bmp.bmBitsPixel
            if nbits > 8:
                numcolor = 0
            else:
                numcolor  = 1 << nbits
            
            headersize = sizeof(BITMAPINFOHEADER)+numcolor*sizeof(RGBQUAD)
            headerbuf = PyString_FromStringAndSize(NULL, headersize) 
            c_buf = headerbuf
            bmpinfo = <BITMAPINFO*>c_buf
            memset(bmpinfo, 0, headersize)
            
            bmpinfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
            bmpinfo.bmiHeader.biWidth = bmp.bmWidth
            bmpinfo.bmiHeader.biHeight = bmp.bmHeight
            bmpinfo.bmiHeader.biPlanes = 1
            bmpinfo.bmiHeader.biBitCount = nbits
            bmpinfo.bmiHeader.biCompression = BI_RGB

            hPal = <HPALETTE>GetStockObject(DEFAULT_PALETTE);
            hDC = GetDC(NULL);
            hOrgPal = SelectPalette(hDC, hPal, 0);
            RealizePalette(hDC);

            if 0 == GetDIBits(hDC, self._hBitmap, 0, bmpinfo.bmiHeader.biHeight, NULL, bmpinfo, DIB_RGB_COLORS):
                pymRaiseWin32Err()
                
            if not bmpinfo.bmiHeader.biSizeImage:
                bmpinfo.bmiHeader.biSizeImage = (
                    (((bmpinfo.bmiHeader.biWidth * bmpinfo.bmiHeader.biBitCount) + 31) & ~31) >> 3) * bmpinfo.bmiHeader.biHeight
        
            buf = PyString_FromStringAndSize(NULL, bmpinfo.bmiHeader.biSizeImage) 
            c_buf = buf
            if 0 == GetDIBits(hDC, self._hBitmap, 0L, bmpinfo.bmiHeader.biHeight, c_buf, bmpinfo, DIB_RGB_COLORS):
                pymRaiseWin32Err()

            dib = DIB()
            dib.bits = buf
            dib.header = headerbuf
            return dib

        finally:
            if hOrgPal: 
                SelectPalette(hDC, hOrgPal, 0)
            if hDC:
                ReleaseDC(NULL,hDC)

cdef extern from "windows.h":
    void *CreateCompatibleBitmap(HDC dc, int width, int height)
    
cdef class CompatibleBitmap(Bitmap):
    def __init__(self, dc, width, height):
        cdef HDC hdc
        hdc = PyMFCHandle_AsHandle(dc.getHandle())
        
        self._hBitmap = CreateCompatibleBitmap(hdc, width, height)
        if NULL == self._hBitmap:
            pymRaiseWin32Err()
        self.temp = 0


cdef extern from "windows.h":
    int BLACK_BRUSH, DKGRAY_BRUSH, DC_BRUSH, GRAY_BRUSH, HOLLOW_BRUSH
    int LTGRAY_BRUSH, NULL_BRUSH, WHITE_BRUSH 

    HBRUSH CreateSolidBrush(unsigned long color) except NULL

    int HS_BDIAGONAL, HS_CROSS, HS_DIAGCROSS, HS_FDIAGONAL, HS_HORIZONTAL, HS_VERTICAL
    HBRUSH CreateHatchBrush(int fnStyle, unsigned long clrref) except NULL
    HBRUSH CreatePatternBrush(HBITMAP hbmp) except NULL

    int BS_DIBPATTERN, BS_DIBPATTERNPT, BS_HATCHED, BS_HOLLOW, BS_NULL, BS_PATTERN, BS_SOLID

    ctypedef struct LOGBRUSH:
        int lbStyle
        COLORREF lbColor
        unsigned long lbHatch


cdef class LogBrush:
    cdef LOGBRUSH logbrush

    property pattern:
        def __get__(self):
            return self.logbrush.lbStyle & BS_PATTERN
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_PATTERN
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_PATTERN

    property dibpatternpt:
        def __get__(self):
            return self.logbrush.lbStyle & BS_DIBPATTERNPT
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_DIBPATTERNPT
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_DIBPATTERNPT
                
    property hatched:
        def __get__(self):
            return self.logbrush.lbStyle & BS_HATCHED
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_HATCHED
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_HATCHED
                
    property hollow:
        def __get__(self):
            return self.logbrush.lbStyle & BS_HOLLOW
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_HOLLOW
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_HOLLOW
                
    property null:
        def __get__(self):
            return self.logbrush.lbStyle & BS_NULL
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_NULL
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_NULL
                
    property solid:
        def __get__(self):
            return self.logbrush.lbStyle & BS_SOLID
        def __set__(self, int v):
            if v:
                self.logbrush.lbStyle = self.logbrush.lbStyle | BS_SOLID
            else:
                self.logbrush.lbStyle = self.logbrush.lbStyle & ~BS_SOLID
    
    property color:
        def __get__(self):
            return self.logbrush.lbColor
#        def __set__(self, int v):
#            self.logbrush.lbColor = v

#    property hatch:
#        def __get__(self):
#            return self.logbrush.lbHatch
#        def __set__(self, int v):
#            self.logbrush.lbHatch = v

cdef class Brush:
    cdef HBRUSH hBrush
    cdef int temp

    def __init__(self, hbrush=None, color=None, own=0, black=0, dkgray=0, gray=0, null=0, ltgray=0, white=0):
        cdef int f
        f = 0
        if black:
            f = BLACK_BRUSH
        elif dkgray:
            f = DKGRAY_BRUSH
        elif gray:
            f = GRAY_BRUSH
        elif null:
            f = HOLLOW_BRUSH
        elif ltgray:
            f = LTGRAY_BRUSH
        elif white: 
            f = WHITE_BRUSH 

        if f:
            self.hBrush = GetStockObject(f)
            if NULL == self.hBrush:
                pymRaiseWin32Err()
            self.temp = 1
        elif hbrush:
            self.hBrush = PyMFCHandle_AsHandle(hbrush)
            if not own:
                self.temp = 1
        else:
            self.hBrush = CreateSolidBrush(color)
            if NULL == self.hBrush:
                pymRaiseWin32Err()

    def __dealloc__(self):
        if self.hBrush and not self.temp:
            DeleteObject(self.hBrush)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self.hBrush)

    def detach(self):
        ret = PyMFCHandle_FromHandle(self.hBrush)
        self.hBrush = NULL
        return ret

    def getLogBrush(self):
        cdef LogBrush ret
        ret = LogBrush()
        if 0 == GetObject(self.hBrush, sizeof(ret.logbrush), &ret.logbrush):
            pymRaiseWin32Err()
        return ret

cdef class HatchBrush(Brush):
    def __init__(self, bdiagonal=0, cross=0, diagcross=0, fdiagonal=0, horizontal=0, vertical=0, color=0):
        cdef unsigned long f
        
        if bdiagonal:
            f = HS_BDIAGONAL
        elif cross:
            f = HS_CROSS
        elif diagcross:
            f = HS_DIAGCROSS
        elif fdiagonal:
            f = HS_FDIAGONAL
        elif horizontal:
            f = HS_HORIZONTAL
        elif vertical:
            f = HS_VERTICAL
        else:
            raise ValueError("hatch style not specified")
        
        self.hBrush = CreateHatchBrush(f, color)
        if NULL == self.hBrush:
            pymRaiseWin32Err()

cdef class PatternBrush(Brush):
    def __init__(self, bmp):
        cdef void *hbmp
        if isinstance(bmp, (int, long)):
            hbmp = PyMFCHandle_AsHandle(bmp)
        else:
            hbmp = PyMFCHandle_AsHandle(bmp.getHandle())
            
        self.hBrush = CreatePatternBrush(hbmp)
        if NULL == self.hBrush:
            pymRaiseWin32Err()


cdef extern from "windows.h":

    int PS_GEOMETRIC, PS_COSMETIC
    int PS_SOLID, PS_DASH, PS_DOT, PS_DASHDOT, PS_DASHDOTDOT
    int PS_NULL, PS_INSIDEFRAME
    int PS_ENDCAP_ROUND, PS_ENDCAP_SQUARE, PS_ENDCAP_FLAT
    int PS_JOIN_BEVEL, PS_JOIN_MITER, PS_JOIN_ROUND 

    HPEN ExtCreatePen(DWORD dwPenStyle, DWORD dwWidth, LOGBRUSH *lplb, DWORD dwStyleCount, DWORD *lpStyle)

    ctypedef struct LOGPEN:
        UINT     lopnStyle
        POINT    lopnWidth
        COLORREF lopnColor

    int PS_STYLE_MASK
    ctypedef struct EXTLOGPEN:
        DWORD     elpPenStyle
        DWORD     elpWidth
        UINT      elpBrushStyle
        COLORREF  elpColor
        ULONG    *elpHatch
        DWORD     elpNumEntries
        DWORD     elpStyleEntry[1]

cdef class LogPen:
    cdef LOGPEN lp
    
    def __init__(self, object logpen=None, **kwargs):
        cdef LOGPEN *p
        cdef LogPen lp
        cdef long wk
        
        if isinstance(logpen, LogPen):
            lp = logpen
            self.lp = lp.lp
        else:
            for name, value in kwargs.items():
                setattr(self, name, value)
        
    property width:
        def __get__(self):
            return self.lp.lopnWidth.x
        def __set__(self, v):
            self.lp.lopnWidth.x = v

    property color:
        def __get__(self):
            return self.lp.lopnColor
        def __set__(self, v):
            self.lp.lopnColor = v

    property solid:
        def __get__(self):
            return self.lp.lopnStyle == PS_SOLID
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_SOLID

    property dash:
        def __get__(self):
            return self.lp.lopnStyle == PS_DASH
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_DASH

    property dot:
        def __get__(self):
            return self.lp.lopnStyle == PS_DOT
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_DOT

    property dashdot:
        def __get__(self):
            return self.lp.lopnStyle == PS_DASHDOT
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_DASHDOT

    property dashdotdot:
        def __get__(self):
            return self.lp.lopnStyle == PS_DASHDOTDOT
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_DASHDOTDOT

    property null:
        def __get__(self):
            return self.lp.lopnStyle == PS_NULL
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_NULL

    property insideframe :
        def __get__(self):
            return self.lp.lopnStyle == PS_INSIDEFRAME
        def __set__(self, v):
            if v:
                self.lp.lopnStyle = PS_INSIDEFRAME


cdef class ExtLogPen:
    cdef EXTLOGPEN *elp
    def __init__(self, buffer, bufferlen):
        cdef void *p

        self.elp = <EXTLOGPEN *>malloc(bufferlen*sizeof(BYTE))
        if self.elp == NULL:
            raise MemoryError()
        
        try:
            p = PyMFCPtr_AsVoidPtr(buffer)
            memcpy(self.elp, p, bufferlen)
        except:
            free(self.elp)
            self.elp = NULL
            raise

    def __dealloc__(self):
        if self.elp:
            free(self.elp)
        self.elp = NULL

    property width:
        def __get__(self):
            return self.elp.elpWidth

    property color:
        def __get__(self):
            return self.elp.elpColor

    property solid:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_SOLID

    property dash:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_DASH

    property dot:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_DOT

    property dashdot:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_DASHDOT

    property dashdotdot:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_DASHDOTDOT

    property null:
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_NULL

    property insideframe :
        def __get__(self):
            return (self.elp.elpPenStyle & PS_STYLE_MASK) == PS_INSIDEFRAME


cdef class Pen:
    cdef HPEN hPen
    cdef int temp
    
    def __init__(self, hpen=None, own=0, 
            geometric=0, cosmetic=0, solid=0, dash=0, dot=0, dashdot=0, 
            dashdotdot=0, null=0, insideframe=0, 
            endcap_round=0, endcap_square=0, endcap_flat=0,
            join_bevel=0, join_miter=0, join_round=0,
            width=0, color=0):
        
        cdef int f
        cdef LOGBRUSH logbrush
        
        if hpen:
            self.hPen = PyMFCHandle_AsHandle(hpen)
            if not own:
                self.temp = 1
        else:
            
            if dash:
                f = PS_DASH
            elif dot:
                f = PS_DOT
            elif dashdot:
                f = PS_DASHDOT
            elif dashdotdot:
                f = PS_DASHDOTDOT
            elif null:
                f = PS_NULL
            elif insideframe:
                f = PS_INSIDEFRAME
            else:
                f = PS_SOLID
            
            if cosmetic and not geometric:
                f = f | PS_COSMETIC
            else:
                f = f | PS_GEOMETRIC
            
            if endcap_round:
                f = f | PS_ENDCAP_ROUND
            elif endcap_square:
                f = f | PS_ENDCAP_SQUARE
            elif endcap_flat:
                f = f | PS_ENDCAP_FLAT

            if join_bevel:
                f = f | PS_JOIN_BEVEL
            elif join_miter:
                f = f | PS_JOIN_MITER
            elif join_round:
                f = f | PS_JOIN_ROUND

            memset(&logbrush, 0, sizeof(logbrush))
            logbrush.lbStyle = BS_SOLID
            logbrush.lbColor = color
            logbrush.lbHatch = 0
            self.hPen = ExtCreatePen(f, width, &logbrush, 0, NULL)
            if NULL == self.hPen:
                pymRaiseWin32Err()
    

    def __dealloc__(self):
        if self.hPen and not self.temp:
            DeleteObject(self.hPen)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self.hPen)

    def detach(self):
        ret = PyMFCHandle_FromHandle(self.hPen)
        self.hPen = NULL
        return ret


    cdef object _getExtLogPen(self, long buflen):
        cdef void *buf

        buf = malloc(buflen*sizeof(BYTE))
        if buf == NULL:
            raise MemoryError()
        try:
            if 0 == GetObject(self.hPen, buflen, buf):
                pymRaiseWin32Err()
            return ExtLogPen(PyMFCPtr_FromVoidPtr(buf), buflen)
        finally:
            free(buf)

    cdef object _getLogPen(self, long buflen):
        cdef LogPen ret
        ret = LogPen()
        if 0 == GetObject(self.hPen, sizeof(ret.lp), &ret.lp):
            pymRaiseWin32Err()
        return ret
        
    def getLogPen(self):
        cdef long buflen
        buflen = GetObject(self.hPen, 0, NULL)
        if 0 == buflen:
            pymRaiseWin32Err()
            
        if buflen == sizeof(LOGFONT):
            return self._getLogPen(buflen)
        else:
            return self._getExtLogPen(buflen)
#        ret = LogBrush()
#        if 0 == GetObject(<HGDIOBJ>self.hBrush, sizeof(ret.logbrush), &ret.logbrush):
#            pymRaiseWin32Err()
#        return ret

cdef class HatchPen(Pen):
    def __init__(self, 
            endcap_round=0, endcap_square=0, endcap_flat=0,
            join_bevel=0, join_miter=0, join_round=0,
            width=0, color=0,
            bdiagonal=0, cross=0, diagcross=0, fdiagonal=0, 
            horizontal=0, vertical=0):
        
        cdef int f
        cdef LOGBRUSH logbrush
        
        f = PS_GEOMETRIC | PS_SOLID

        if endcap_round:
            f = f | PS_ENDCAP_ROUND
        elif endcap_square:
            f = f | PS_ENDCAP_SQUARE
        elif endcap_flat:
            f = f | PS_ENDCAP_FLAT

        if join_bevel:
            f = f | PS_JOIN_BEVEL
        elif join_miter:
            f = f | PS_JOIN_MITER
        elif join_round:
            f = f | PS_JOIN_ROUND

        memset(&logbrush, 0, sizeof(logbrush))
        logbrush.lbStyle = BS_HATCHED
        logbrush.lbColor = color

        if bdiagonal:
            logbrush.lbHatch = HS_BDIAGONAL
        elif cross:
            logbrush.lbHatch = HS_CROSS
        elif diagcross:
            logbrush.lbHatch = HS_DIAGCROSS
        elif fdiagonal:
            logbrush.lbHatch = HS_FDIAGONAL
        elif horizontal:
            logbrush.lbHatch = HS_HORIZONTAL
        elif vertical:
            logbrush.lbHatch = HS_VERTICAL
        else:
            raise TypeError("Hatch pattern not specified")
        self.hPen = ExtCreatePen(f, width, &logbrush, 0, NULL)
        if NULL == self.hPen:
            pymRaiseWin32Err()


cdef extern from "windows.h":
    ctypedef struct ICONINFO:
        BOOL    fIcon
        DWORD   xHotspot
        DWORD   yHotspot
        HBITMAP hbmMask
        HBITMAP hbmColor

    BOOL GetIconInfo(HICON hIcon, ICONINFO *piconinfo)
    HICON DuplicateIcon(HINSTANCE hinst, HICON hicon)
    unsigned long DestroyIcon(void* hIcon)
    
    
cdef class Icon:
    cdef HICON hIcon
    cdef int temp
    
    def __init__(self, hIcon=None, filename=None, cx=0, cy=0, 
            defaultcolor=0, createdibsection=0, defaultsize=0, 
            loadmap3dcolors=0, loadtransparent=0, monochrome=0, 
            vgacolor=0, own=0):
        
        if hIcon:
            self.hIcon = PyMFCHandle_AsHandle(hIcon)
            if not own:
                self.temp = 1
        else:
            if not filename:
                filename = unicode('')
            self.hIcon = pymLoadImage(IMAGE_ICON, PyUnicode_AsUnicode(filename), cx, cy, defaultcolor, 
                createdibsection, defaultsize, loadmap3dcolors, loadtransparent,
                monochrome, vgacolor)

    def __dealloc__(self):
        if self.hIcon and not self.temp:
            if not DestroyIcon(self.hIcon):
                pymRaiseWin32Err()

    def getHandle(self):
        return PyMFCHandle_FromHandle(self.hIcon)
    
    def detach(self):
        ret = PyMFCHandle_FromHandle(self.hIcon)
        self.hIcon = NULL
        return ret
        
    def getBitmap(self):
        cdef ICONINFO ii
        if 0 == GetIconInfo(self.hIcon, &ii):
            pymRaiseWin32Err()
        
        if ii.hbmMask:
            DeleteObject(ii.hbmMask)
            
        ret = Bitmap(hbmp=PyMFCHandle_FromHandle(ii.hbmColor), own=1)
        return ret

    def getMaskBitmap(self):
        cdef ICONINFO ii
        if 0 == GetIconInfo(self.hIcon, &ii):
            pymRaiseWin32Err()
        
        if ii.hbmColor:
            DeleteObject(ii.hbmColor)
        ret = Bitmap(hbmp=PyMFCHandle_FromHandle(ii.hbmMask), own=1)
        return ret

    def duplicate(self):
        cdef HICON hIcon
        hIcon = DuplicateIcon(NULL, self.hIcon)
        if NULL == hIcon:
            pymRaiseWin32Err()
        ret = Icon(hIcon=PyMFCHandle_FromHandle(hIcon), own=1)
        return ret
        
cdef extern from "windows.h":

    void *LoadCursor(void* hInstance,  TCHAR *lpCursorName)
    unsigned long DestroyCursor(void *hCursor)
    void *SetCursor(void *hCursor)

    TCHAR *IDC_APPSTARTING, *IDC_ARROW, *IDC_CROSS, *IDC_HAND, *IDC_HELP
    TCHAR *IDC_IBEAM, *IDC_ICON, *IDC_NO, *IDC_SIZE, *IDC_SIZEALL
    TCHAR *IDC_SIZENESW, *IDC_SIZENS, *IDC_SIZENWSE, *IDC_SIZEWE
    TCHAR *IDC_UPARROW, *IDC_WAIT

cdef class Cursor:
    cdef HCURSOR hCursor
    cdef int temp
    
    def __init__(self, appstarting=0, arrow=0, cross=0, hand=0, help=0,
            ibeam=0, icon=0, no=0, size=0, sizeall=0, sizenesw=0, 
            sizens=0, sizenwse=0, sizewe=0, uparrow=0, wait=0):

        cdef TCHAR *c
        c = NULL
        
        if appstarting:
            c = IDC_APPSTARTING
        elif arrow:
            c = IDC_ARROW
        elif cross:
            c = IDC_CROSS
        elif hand:
            c = IDC_HAND
        elif help:
            c = IDC_HELP
        elif ibeam:
            c = IDC_IBEAM
        elif icon:
            c = IDC_ICON
        elif no:
            c = IDC_NO
        elif size:
            c = IDC_SIZE
        elif sizeall:
            c = IDC_SIZEALL
        elif sizenesw:
            c = IDC_SIZENESW
        elif sizens:
            c = IDC_SIZENS
        elif sizenwse:
            c = IDC_SIZENWSE
        elif sizewe:
            c = IDC_SIZEWE
        elif uparrow:
            c = IDC_UPARROW
        elif wait:
            c = IDC_WAIT

        self.hCursor = LoadCursor(NULL, c)
        if self.hCursor == NULL:
            pymRaiseWin32Err()

        self.temp = 1

    def __dealloc__(self):
        if self.hCursor and not self.temp:
            DestroyCursor(<void*>self.hCursor)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self.hCursor)

    def detach(self):
        ret = PyMFCHandle_FromHandle(self.hCursor)
        self.hCursor = NULL
        return ret

    def setCursor(self):
        SetCursor(self.hCursor)




cdef extern from "windows.h":
    int NULLREGION, SIMPLEREGION, COMPLEXREGION, ERROR

    HRGN CreateEllipticRgn(int, int, int, int)
    HRGN CreateRectRgn(int, int, int, int)
    HRGN CreateRoundRectRgn(int, int, int, int, int, int)
    BOOL FillRgn(HDC dc, HRGN hrgn, HBRUSH hBrush)
    BOOL FrameRgn(HDC dc, HRGN hrgn, HBRUSH hBrush, int, int)
    BOOL InvertRgn(HDC, HRGN)
    int OffsetRgn(HRGN, int, int)
    BOOL PaintRgn(HDC, HRGN)
    BOOL PtInRegion(HRGN, int, int)
    BOOL RectInRegion(HRGN, RECT *)
    int GetRgnBox(HRGN, RECT *)


    int RGN_AND, RGN_COPY, RGN_DIFF, RGN_OR, RGN_XOR
    int CombineRgn(HRGN hrgnDest, HRGN hrgnSrc1, HRGN hrgnSrc2, int fnCombineMode)
    
cdef class Region:
    cdef HRGN hrgn
    cdef int temp
    
    def __init__(self, hrgn=0, own=1):
        if hrgn:
            self.hrgn = PyMFCHandle_AsHandle(hrgn)
        else:
            self.hrgn = NULL
        if not own:
            self.temp = 1

    def __dealloc__(self):
        if self.hrgn and not self.temp:
            DeleteObject(self.hrgn)

    def getHandle(self):
        return PyMFCHandle_FromHandle(self.hrgn)
        
    def detach(self):
        ret = PyMFCHandle_FromHandle(self.hrgn)
        self.hrgn = NULL
        return ret

    def fill(self, dc, brush):
        cdef HDC hdc
        cdef HBRUSH hbrush

        hdc = PyMFCHandle_AsHandle(dc.hDC)
        hbrush = PyMFCHandle_AsHandle(brush.getHandle())
        
        if 0 == FillRgn(hdc, self.hrgn, hbrush):
            pymRaiseWin32Err()
    
    def invert(self, dc):
        cdef HDC hdc
        hdc = PyMFCHandle_AsHandle(dc.hDC)
        
        if 0 == InvertRgn(hdc, self.hrgn):
            pymRaiseWin32Err()
    
    def paint(self, dc):
        cdef HDC hdc
        hdc = PyMFCHandle_AsHandle(dc.hDC)
        
        if 0 == PaintRgn(hdc, self.hrgn):
            pymRaiseWin32Err()
    
    def frame(self, dc, brush, width, height):
        cdef HDC hdc
        cdef HBRUSH hbrush

        hdc = PyMFCHandle_AsHandle(dc.hDC)
        hbrush = PyMFCHandle_AsHandle(brush.getHandle())
        
        if 0 == FrameRgn(hdc, self.hrgn, hbrush, width, height):
            pymRaiseWin32Err()
    
        
        
    def offset(self, offset):
        cdef x, y
        x = offset[0]
        y = offset[1]
        
        OffsetRgn(self.hrgn, x, y)
    
    def ptInRgn(self, pos):
        cdef x, y
        x = pos[0]
        y = pos[1]
        
        return PtInRegion(self.hrgn, x, y)
    
    def rectInRgn(self, rect):
        cdef RECT rc
        
        rc.left = rect[0]
        rc.top = rect[1]
        rc.right = rect[2]
        rc.bottom = rect[3]

        return RectInRegion(self.hrgn, &rc)

    def getRgnBox(self):
        cdef RECT rc
        if 0 == GetRgnBox(self.hrgn, &rc):
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.right, rc.bottom)

    def combine(self, Region src, intersect=0, diff=0, union=0, xor=0):
        cdef int f, v
        cdef Region ret
        cdef HRGN dest
        
        if intersect:
            f = RGN_AND
        elif diff:
            f = RGN_DIFF
        elif union:
            f = RGN_OR
        elif xor:
            f = RGN_XOR
        else:
            raise TypeError("Invalid combine mode")
        
        dest = CreateRectRgn(0, 0, 1, 1)
        if not dest:
            pymRaiseWin32Err()

        try:
            if ERROR == CombineRgn(dest, self.hrgn, src.hrgn, f):
                pymRaiseWin32Err()
            ret = Region()
            ret.hrgn = dest
            return ret
        except:
            DeleteObject(dest)
            raise

    def copy(self):
        cdef Region ret
        cdef HRGN dest
        
        dest = CreateRectRgn(0, 0, 1, 1)
        if not dest:
            pymRaiseWin32Err()

        try:
            if ERROR == CombineRgn(dest, self.hrgn, NULL, RGN_COPY):
                pymRaiseWin32Err()
            ret = Region()
            ret.hrgn = dest
            return ret
        except:
            DeleteObject(dest)
            raise

        
#    int RGN_AND, RGN_COPY, RGN_DIFF, RGN_OR, RGN_XOR
#    int CombineRgn(HRGN hrgnDest, HRGN hrgnSrc1, HRGN hrgnSrc2, int fnCombineMode)
        

cdef class EllipticRgn(Region):
    def __init__(self, rect):
        self.hrgn = CreateEllipticRgn(rect[0], rect[1], rect[2], rect[3])
        if self.hrgn == NULL:
            pymRaiseWin32Err()
            
cdef class RectRgn(Region):
    def __init__(self, rect):
        self.hrgn = CreateRectRgn(rect[0], rect[1], rect[2], rect[3])
        if self.hrgn == NULL:
            pymRaiseWin32Err()
            

cdef class RoundRectRgn(Region):
    def __init__(self, rect, ellipse):
        self.hrgn = CreateRoundRectRgn(rect[0], rect[1], rect[2], rect[3], ellipse[0], ellipse[1])
        if self.hrgn == NULL:
            pymRaiseWin32Err()
            


cdef extern from "windows.h":

    int GetClipBox(HDC hdc, RECT *lprc)
    int ExcludeClipRect(HDC hdc, int nLeftRect,int nTopRect, int nRightRect, int nBottomRect)
    int IntersectClipRect(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect)

    int CDC_PointToPixel(void *dc, double point)

    BOOL DPtoLP(HDC hdc, POINT *lpPoints, int nCount)
    BOOL LPtoDP(HDC hdc, POINT *lpPoints, int nCount)

    int MM_ANISOTROPIC, MM_HIENGLISH, MM_HIMETRIC, MM_ISOTROPIC
    int MM_LOENGLISH, MM_LOMETRIC, MM_TEXT, MM_TWIPS

    int SetMapMode(HDC hdc, int fnMapMode)


    cdef int TRANSPARENT, OPAQUE
    int SetBkMode(HDC hdc, int iBkMode)

    BOOL AbortPath(HDC)
    BOOL BeginPath(HDC)
    BOOL EndPath(HDC)
    BOOL FillPath(HDC)
    HRGN PathToRegion(HDC)
    BOOL StrokeAndFillPath(HDC)
    BOOL StrokePath(HDC)
    BOOL CloseFigure(HDC)
    
    cdef int BLACKNESS, CAPTUREBLT, DSTINVERT, MERGECOPY, MERGEPAINT
    cdef int NOMIRRORBITMAP, NOTSRCCOPY, NOTSRCERASE, PATCOPY
    cdef int PATINVERT, PATPAINT, SRCAND, SRCCOPY, SRCERASE
    cdef int SRCINVERT, SRCPAINT, WHITENESS

    BOOL BitBlt(HDC hdcDest, int nXDest, int nYDest, int nWidth, int nHeight,
        HDC hdcSrc, int nXSrc, int nYSrc, int dwRop)
    BOOL PatBlt(HDC hdc, int nXLeft, int nYLeft, int nWidth, int nHeight, DWORD dwRop)
    
    BOOL InvertRect(HDC hdc, RECT *rect)

    int GetTextMetrics(HDC hdc, TEXTMETRIC *lptm)
    BOOL GetTextExtentPoint32W(HDC hdc, TCHAR *lpString, int cbString, SIZE *lpSize)

    BOOL GetTextExtentExPointW(HDC hdc, LPCTSTR lpszStr, int cchString, int nMaxExtent,  
        LPINT lpnFit,  LPINT alpDx, LPSIZE lpSize)

    cdef int TA_BASELINE, TA_BOTTOM, TA_TOP, TA_CENTER, TA_LEFT
    cdef int TA_RIGHT, TA_NOUPDATECP, TA_RTLREADING, TA_UPDATECP

    int SetTextAlign(HDC hdc, UINT mode)
    COLORREF SetTextColor(HDC hdc, COLORREF crColor)
    COLORREF SetBkColor(HDC hdc, COLORREF crColor)
    
    BOOL TextOut(HDC hdc, int X, int Y, TCHAR *lpString, int cbCount)
    BOOL TextOutW(HDC hdc, int X, int Y, TCHAR *lpString, int cbCount)

    cdef int ETO_OPAQUE, ETO_CLIPPED, ETO_GLYPH_INDEX, ETO_RTLREADING
    cdef int ETO_NUMERICSLOCAL, ETO_NUMERICSLATIN, ETO_IGNORELANGUAGE, ETO_PDY

    BOOL ExtTextOut(HDC hdc, int X, int Y, int fuOptions, RECT* lprc, TCHAR *lpString,
            int cbCount, int* lpDx)
    BOOL ExtTextOutW(HDC hdc, int X, int Y, int fuOptions, RECT* lprc, TCHAR *lpString,
            int cbCount, int* lpDx)

    cdef int DT_BOTTOM, DT_CALCRECT, DT_CENTER, DT_EDITCONTROL
    cdef int DT_END_ELLIPSIS, DT_EXPANDTABS, DT_EXTERNALLEADING
    cdef int DT_HIDEPREFIX, DT_INTERNAL, DT_LEFT, DT_MODIFYSTRING
    cdef int DT_NOCLIP, DT_NOPREFIX
    cdef int DT_PATH_ELLIPSIS, DT_RIGHT, DT_RTLREADING
    cdef int DT_SINGLELINE, DT_TABSTOP, DT_TOP, DT_VCENTER
    cdef int DT_WORDBREAK, DT_WORD_ELLIPSIS

    ctypedef struct DRAWTEXTPARAMS:
          UINT cbSize
          int  iTabLength
          int  iLeftMargin
          int  iRightMargin
          UINT uiLengthDrawn
        
    int DrawTextEx(HDC hdc, TCHAR *lpchText, int cchText, RECT *lprc, 
            UINT dwDTFormat, void *lpDTParams)
    int DrawTextExW(HDC hdc, TCHAR *lpchText, int cchText, RECT *lprc, 
            UINT dwDTFormat, void *lpDTParams)

    BOOL MoveToEx(HDC hdc, int x, int y, POINT *p)
    BOOL LineTo(HDC hdc, int x, int y)

    BOOL Arc(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect, 
        int nXStartArc, int nYStartArc, int nXEndArc, int nYEndArc)
    BOOL ArcTo(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect, 
        int nXStartArc, int nYStartArc, int nXEndArc, int nYEndArc)

    BOOL SetArcDirection( HDC hdc, int ArcDirection)
    cdef int AD_COUNTERCLOCKWISE, AD_CLOCKWISE
    
    BOOL PolyBezier(HDC hdc, POINT* lppt, DWORD cPoints)
    BOOL PolyBezierTo(HDC hdc, POINT* lppt, DWORD cPoints)

    cdef int BDR_RAISEDOUTER, BDR_SUNKENOUTER, BDR_RAISEDINNER
    cdef int BDR_SUNKENINNER, BDR_OUTER, BDR_INNER

    cdef int EDGE_RAISED, EDGE_SUNKEN, EDGE_ETCHED, EDGE_BUMP

    cdef int BF_LEFT, BF_TOP, BF_RIGHT, BF_BOTTOM, BF_TOPLEFT
    cdef int BF_TOPRIGHT, BF_BOTTOMLEFT, BF_BOTTOMRIGHT, BF_RECT
    cdef int BF_DIAGONAL_ENDTOPRIGHT, BF_DIAGONAL_ENDTOPLEFT
    cdef int BF_DIAGONAL_ENDBOTTOMLEFT, BF_DIAGONAL_ENDBOTTOMRIGHT
    cdef int BF_MIDDLE, BF_SOFT, BF_ADJUST, BF_FLAT, BF_MONO

    BOOL Rectangle(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect)
    BOOL RoundRect(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect, int nWidth, int nHeight)
    BOOL Ellipse(HDC hdc, int nLeftRect, int nTopRect, int nRightRect, int nBottomRect)
    int FrameRect(HDC hDC, RECT *, HBRUSH hbr)
    int FillRect(HDC hDC, RECT *, HBRUSH hbr)
    int DrawEdge(HDC hdc, RECT *lpRect, int nEdge, int nFlags)
    int DrawFocusRect(HDC hdc, RECT *lpRect)

    BOOL DrawIcon(HDC hDC, int X, int Y, void *hIcon)

    cdef int DI_COMPAT, DI_DEFAULTSIZE, DI_IMAGE, DI_MASK, DI_NOMIRROR, DI_NORMAL
    BOOL DrawIconEx(HDC hdc, int xLeft, int yTop, HICON hIcon, int cxWidth, int cyWidth, UINT istepIfAniCur, HBRUSH hbrFlickerFreeDraw, UINT diFlags)

    int pymEnumFontFamiliesEx(HDC hdc, LOGFONT *lpLogfont, object f) except? -1

    ctypedef void *DRAWSTATEPROC
    BOOL DrawState(HDC hdc, HBRUSH hbr, DRAWSTATEPROC lpOutputFunc, LPARAM lData, WPARAM wData, int x, int y, int cx, int cy, UINT fuFlags)
    cdef int DST_BITMAP, DST_COMPLEX, DST_ICON, DST_PREFIXTEXT
    cdef int DST_TEXT, DSS_DISABLED, DSS_HIDEPREFIX, DSS_MONO
    cdef int DSS_NORMAL, DSS_PREFIXONLY, DSS_RIGHT, DSS_UNION


    BOOL SetWindowOrgEx(HDC hdc, int X, int Y, POINT *lpPoint)
    BOOL GetWindowOrgEx(HDC hdc, POINT *lpPoint)
    BOOL SetViewportOrgEx(HDC hdc, int X, int Y, POINT *lpPoint)
    BOOL GetViewportOrgEx(HDC hdc, POINT *lpPoint)
    BOOL SetWindowExtEx(HDC hdc, int nXExtent, int nYExtent, SIZE *lpSize)
    BOOL GetWindowExtEx(HDC hdc, SIZE *lpSize)
    BOOL SetViewportExtEx(HDC hdc, int nXExtent, int nYExtent, SIZE *lpSize)
    BOOL GetViewportExtEx(HDC hdc, SIZE *lpSize)

    int SelectClipRgn(HDC hdc, HRGN hrgn)
    int GetClipRgn(HDC hdc, HRGN hrgn)

    HDC CreateEnhMetaFile(HDC hdcRef, LPCTSTR lpFilename, RECT *lpRect, LPCTSTR lpDescription)
    HENHMETAFILE CloseEnhMetaFile(HDC hdc)
    BOOL DeleteEnhMetaFile(HENHMETAFILE hemf)
    BOOL PlayEnhMetaFile(HDC hdc, HENHMETAFILE hemf, RECT *lpRect)

    ctypedef struct ENHMETAHEADER:
        DWORD iType
        DWORD nSize
        RECTL rclBounds
        RECTL rclFrame
        DWORD dSignature
        DWORD nVersion
        DWORD nBytes
        DWORD nRecords
        WORD  nHandles
        WORD  sReserved
        DWORD nDescription
        DWORD offDescription
        DWORD nPalEntries
        SIZEL szlDevice
        SIZEL szlMillimeters
        DWORD cbPixelFormat
        DWORD offPixelFormat
        DWORD bOpenGL

    UINT GetEnhMetaFileHeader(HENHMETAFILE hemf, UINT cbBuffer, ENHMETAHEADER *lpemh)

cdef class _text_metric:
    cdef TEXTMETRIC tm
    cdef readonly object pTEXTMETRIC
    
    def __init__(self):
        self.pTEXTMETRIC = PyMFCPtr_FromVoidPtr(&self.tm)
    
    def getBuffer(self):
        return PyMFCPtr_FromVoidPtr(&(self.tm))
        
    property _p_tm:
        def __get__(self):
            return PyMFCPtr_FromVoidPtr(&(self.tm))
            
    property tmHeight:
        def __get__(self):
            return self.tm.tmHeight
        def __set__(self, v):
            self.tm.tmHeight = v
    property tmAscent:
        def __get__(self):
            return self.tm.tmAscent
        def __set__(self, v):
            self.tm.tmAscent = v
    property tmDescent:
        def __get__(self):
            return self.tm.tmDescent
        def __set__(self, v):
            self.tm.tmDescent = v
    property tmInternalLeading:
        def __get__(self):
            return self.tm.tmInternalLeading
        def __set__(self, v):
            self.tm.tmInternalLeading = v
    property tmExternalLeading:
        def __get__(self):
            return self.tm.tmExternalLeading
        def __set__(self, v):
            self.tm.tmExternalLeading = v
    property tmAveCharWidth:
        def __get__(self):
            return self.tm.tmAveCharWidth
        def __set__(self, v):
            self.tm.tmAveCharWidth = v
    property tmMaxCharWidth:
        def __get__(self):
            return self.tm.tmMaxCharWidth
        def __set__(self, v):
            self.tm.tmMaxCharWidth = v
    property tmWeight:
        def __get__(self):
            return self.tm.tmWeight
        def __set__(self, v):
            self.tm.tmWeight = v
    property tmOverhang:
        def __get__(self):
            return self.tm.tmOverhang
        def __set__(self, v):
            self.tm.tmOverhang = v
    property tmDigitizedAspectX:
        def __get__(self):
            return self.tm.tmDigitizedAspectX
        def __set__(self, v):
            self.tm.tmDigitizedAspectX = v
    property tmDigitizedAspectY:
        def __get__(self):
            return self.tm.tmDigitizedAspectY
        def __set__(self, v):
            self.tm.tmDigitizedAspectY = v
    property tmFirstChar:
        def __get__(self):
            return self.tm.tmFirstChar
        def __set__(self, v):
            self.tm.tmFirstChar = <TCHAR>v
    property tmLastChar:
        def __get__(self):
            return self.tm.tmLastChar
        def __set__(self, v):
            self.tm.tmLastChar = <TCHAR>v
    property tmDefaultChar:
        def __get__(self):
            return self.tm.tmDefaultChar
        def __set__(self, v):
            self.tm.tmDefaultChar = <TCHAR>v
    property tmBreakChar:
        def __get__(self):
            return self.tm.tmBreakChar
        def __set__(self, v):
            self.tm.tmBreakChar = <TCHAR>v
    property tmItalic:
        def __get__(self):
            return self.tm.tmItalic
        def __set__(self, v):
            self.tm.tmItalic = <BYTE>v
    property tmUnderlined:
        def __get__(self):
            return self.tm.tmUnderlined
        def __set__(self, v):
            self.tm.tmUnderlined = <BYTE>v
    property tmStruckOut:
        def __get__(self):
            return self.tm.tmStruckOut
        def __set__(self, v):
            self.tm.tmStruckOut = <BYTE>v
    property tmPitchAndFamily:
        def __get__(self):
            return self.tm.tmPitchAndFamily
        def __set__(self, v):
            self.tm.tmPitchAndFamily = <BYTE>v
    property tmCharSet:
        def __get__(self):
            return self.tm.tmCharSet
        def __set__(self, v):
            self.tm.tmCharSet = <BYTE>v
    
cdef class DrawTextResult:
    cdef readonly int height
    cdef readonly object rc
    cdef readonly int lengthDrawn
        
cdef extern from "windows.h":
    int GetDeviceCaps(HDC hdc, int nIndex)
    
    int DRIVERVERSION, TECHNOLOGY, HORZSIZE, VERTSIZE, HORZRES, VERTRES
    int LOGPIXELSX, LOGPIXELSY, BITSPIXEL, PLANES, NUMBRUSHES, NUMPENS
    int NUMFONTS, NUMCOLORS, ASPECTX, ASPECTY, ASPECTXY, PDEVICESIZE
    int CLIPCAPS, SIZEPALETTE, NUMRESERVED, COLORRES, PHYSICALWIDTH
    int PHYSICALHEIGHT, PHYSICALOFFSETX, PHYSICALOFFSETY, VREFRESH
    int SCALINGFACTORX, SCALINGFACTORY, BLTALIGNMENT, SHADEBLENDCAPS
    int RASTERCAPS, CURVECAPS, LINECAPS, POLYGONALCAPS, TEXTCAPS
        
    ctypedef struct DOCINFO:
        int     cbSize
        LPCTSTR lpszDocName
        LPCTSTR lpszOutput
        LPCTSTR lpszDatatyp
        DWORD   fwType

    int StartDoc(HDC hDC, DOCINFO *docinfo) nogil
    int EndDoc(HDC hDC) nogil
    int AbortDoc(HDC hDC) nogil
    int StartPage(HDC hDC) nogil
    int EndPage(HDC hDC) nogil



cdef class _EnhMetaFile:
    cdef HANDLE _hEmf
    cdef ENHMETAHEADER _header
    property hEmf:
        def __get__(self):
            return PyMFCHandle_FromHandle(self._hEmf)
    property rclBounds:
        def __get__(self):
            return (self._header.rclBounds.left, self._header.rclBounds.top,
                    self._header.rclBounds.right, self._header.rclBounds.bottom)
    property rclFrame:
        def __get__(self):
            return (self._header.rclFrame.left, self._header.rclFrame.top,
                    self._header.rclFrame.right, self._header.rclFrame.bottom)
    property dSignature:
        def __get__(self):
            return self._header.dSignature
    property nVersion:
        def __get__(self):
            return self._header.nVersion
    property nBytes:
        def __get__(self):
            return self._header.nBytes
    property nRecords:
        def __get__(self):
            return self._header.nRecords
    property nHandles:
        def __get__(self):
            return self._header.nHandles
    property nDescription:
        def __get__(self):
            return self._header.nDescription
    property offDescription:
        def __get__(self):
            return self._header.offDescription
    property nPalEntries:
        def __get__(self):
            return self._header.nPalEntries
    property szlDevice:
        def __get__(self):
            return (self._header.szlDevice.cx, self._header.szlDevice.cy)
    property szlMillimeters:
        def __get__(self):
            return (self._header.szlMillimeters.cx, self._header.szlMillimeters.cy)
    property cbPixelFormat:
        def __get__(self):
            return self._header.cbPixelFormat
    property offPixelFormat:
        def __get__(self):
            return self._header.offPixelFormat
    property bOpenGL:
        def __get__(self):
            return self._header.bOpenGL

    def __dealloc__(self):
        if self._hEmf != NULL:
            DeleteEnhMetaFile(self._hEmf)
        self._hEmf = NULL



cdef class DC:
    cdef HDC _hDC
    cdef int temp
    property hDC:
        def __get__(self):
            return PyMFCHandle_FromHandle(self._hDC)
        
    property DRIVERVERSION:
        def __get__(self):
            return GetDeviceCaps(self._hDC, DRIVERVERSION)
    property TECHNOLOGY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, TECHNOLOGY)
    property HORZSIZE:
        def __get__(self):
            return GetDeviceCaps(self._hDC, HORZSIZE)
    property VERTSIZE:
        def __get__(self):
            return GetDeviceCaps(self._hDC, VERTSIZE)
    property HORZRES:
        def __get__(self):
            return GetDeviceCaps(self._hDC, HORZRES)
    property VERTRES:
        def __get__(self):
            return GetDeviceCaps(self._hDC, VERTRES)
    property LOGPIXELSX:
        def __get__(self):
            return GetDeviceCaps(self._hDC, LOGPIXELSX)
    property LOGPIXELSY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, LOGPIXELSY)
    property BITSPIXEL:
        def __get__(self):
            return GetDeviceCaps(self._hDC, BITSPIXEL)
    property PLANES:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PLANES)
    property NUMBRUSHES:
        def __get__(self):
            return GetDeviceCaps(self._hDC, NUMBRUSHES)
    property NUMPENS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, NUMPENS)
    property NUMFONTS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, NUMFONTS)
    property NUMCOLORS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, NUMCOLORS)
    property ASPECTX:
        def __get__(self):
            return GetDeviceCaps(self._hDC, ASPECTX)
    property ASPECTY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, ASPECTY)
    property ASPECTXY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, ASPECTXY)
    property PDEVICESIZE:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PDEVICESIZE)
    property CLIPCAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, CLIPCAPS)
    property SIZEPALETTE:
        def __get__(self):
            return GetDeviceCaps(self._hDC, SIZEPALETTE)
    property NUMRESERVED:
        def __get__(self):
            return GetDeviceCaps(self._hDC, NUMRESERVED)
    property COLORRES:
        def __get__(self):
            return GetDeviceCaps(self._hDC, COLORRES)
    property PHYSICALWIDTH:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PHYSICALWIDTH)
    property PHYSICALHEIGHT:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PHYSICALHEIGHT)
    property PHYSICALOFFSETX:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PHYSICALOFFSETX)
    property PHYSICALOFFSETY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, PHYSICALOFFSETY)
    property VREFRESH:
        def __get__(self):
            return GetDeviceCaps(self._hDC, VREFRESH)
    property SCALINGFACTORX:
        def __get__(self):
            return GetDeviceCaps(self._hDC, SCALINGFACTORX)
    property SCALINGFACTORY:
        def __get__(self):
            return GetDeviceCaps(self._hDC, SCALINGFACTORY)
    property BLTALIGNMENT:
        def __get__(self):
            return GetDeviceCaps(self._hDC, BLTALIGNMENT)
    property SHADEBLENDCAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, SHADEBLENDCAPS)
    property RASTERCAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, RASTERCAPS)
    property CURVECAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, CURVECAPS)
    property LINECAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, LINECAPS)
    property POLYGONALCAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, POLYGONALCAPS)
    property TEXTCAPS:
        def __get__(self):
            return GetDeviceCaps(self._hDC, TEXTCAPS)

    def __init__(self, hdc=0, own=0, driver=None, device=None, devmode=None):
        cdef TCHAR *c_driver
        cdef TCHAR *c_device
        cdef DEVMODE *pdevmode
        
        self._hDC = NULL
        if hdc:
            self._hDC = PyMFCHandle_AsHandle(hdc)
            if not own:
                self.temp = 1
        else:
            c_driver = NULL
            if driver is not None:
                c_driver = PyUnicode_AsUnicode(driver)

            c_device = NULL
            if device is not None:
                c_device = PyUnicode_AsUnicode(device)
            
            pdevmode = NULL
            if devmode:
                pdevmode = <DEVMODE*>PyMFCPtr_AsVoidPtr(devmode.getPtr())
                
            if c_driver or c_device or pdevmode:
                self._hDC = CreateDC(c_driver, c_device, NULL, pdevmode)
                if self._hDC == NULL:
                    pymRaiseWin32Err()
                self.temp=0

    def __dealloc__(self):
        self._release()

    cdef _release(self):
        if not self.temp:
            if self._hDC != NULL:
                DeleteDC(self._hDC)
        self._hDC = NULL
    
    def release(self):
        self._release()

    def getHandle(self):
        return PyMFCHandle_FromHandle(self._hDC)
        
    def detach(self):
        ret = PyMFCHandle_FromHandle(self._hDC)
        self._hDC = NULL
        return ret

    def startDoc(self, docname):
        cdef DOCINFO docinfo
        cdef int ret
        
        memset(&docinfo, 0, sizeof(DOCINFO))
        docinfo.cbSize = sizeof(DOCINFO)
        docinfo.lpszDocName = PyUnicode_AsUnicode(docname)
        
        with nogil:
            ret = StartDoc(self._hDC, &docinfo)
        if ret <= 0:
            pymRaiseWin32Err()
            
        return ret
        
    def endDoc(self):
        cdef int ret
        with nogil:
            ret = EndDoc(self._hDC)
        if ret <= 0:
            pymRaiseWin32Err()
        
    def abortDoc(self):
        cdef int ret
        with nogil:
            ret = AbortDoc(self._hDC)
        if ret <= 0:
            pymRaiseWin32Err()
        
    def startPage(self):
        cdef int ret
        with nogil:
            ret = StartPage(self._hDC)
        if ret <= 0:
            pymRaiseWin32Err()
        
    def endPage(self):
        cdef int ret
        with nogil:
            ret = EndPage(self._hDC)
        if ret <= 0:
            pymRaiseWin32Err()
        
    def createCompatibleDC(self):
        return CompatibleDC(self)
    
    def createCompatibleBitmap(self, width, height):
        return CompatibleBitmap(self, width, height)
        
    def getClipBox(self):
        cdef int ret
        cdef RECT rc
        ret = GetClipBox(self._hDC, &rc)
        if ret == ERROR:
            pymRaiseWin32Err()
        return (rc.left, rc.top, rc.right, rc.bottom)

    def excludeClipRect(self, rc):
        cdef int ret
        ret = ExcludeClipRect(self._hDC, rc[0], rc[1], rc[2], rc[3])
        if ret == ERROR:
            pymRaiseWin32Err()
        
    def intersectClipRect(self, rc):
        cdef int ret
        ret = IntersectClipRect(self._hDC, rc[0], rc[1], rc[2], rc[3])
        if ret == ERROR:
            pymRaiseWin32Err()
        
    cdef object _selectObject(self, obj):
        cdef HGDIOBJ hobj
        if PyMFCHandle_IsHandle(obj):
            hobj = PyMFCHandle_AsHandle(obj)
        else:
            hobj = PyMFCHandle_AsHandle(obj.getHandle())

        return PyMFCHandle_FromHandle(SelectObject(self._hDC, hobj))
    
        
    def selectObject(self, obj):
        if isinstance(obj, (tuple, list)):
            ret = []
            for o in obj:
                ret.append(self._selectObject(o))
        else:
            ret = self._selectObject(obj)
        return ret
    
    def getTextMetrics(self):
        cdef TEXTMETRIC *lptm
        tm = _text_metric()
        lptm = <TEXTMETRIC*>PyMFCPtr_AsVoidPtr(tm._p_tm)
        if 0 == GetTextMetrics(self._hDC, lptm):
            pymRaiseWin32Err()
        return tm

    def getTextExtent(self, s):
        cdef SIZE ret
        if 0 == GetTextExtentPoint32W(self._hDC, PyUnicode_AsUnicode(s), len(s), &ret):
            pymRaiseWin32Err()
            
        return (ret.cx, ret.cy)
    
    def getTextExtentEx(self, s, maxextent):
        cdef int slen, nfit, *dx, i
        cdef SIZE size
        
        slen = len(s)
        dx = <int *>malloc(slen * sizeof(int))
        if dx == NULL:
            raise MemoryError()
        try:
            if 0 == GetTextExtentExPointW(self._hDC, PyUnicode_AsUnicode(s), slen, 
                    maxextent, &nfit, dx, &size):
                pymRaiseWin32Err()

            l = []
            for i from 0 <= i < nfit: 
                l.append(dx[i])
            return l, (size.cx, size.cy)
        finally:
            free(dx)
    
    def EnumFontFamilies(self,
            func, face = None,
            int ansi_charset=0, int baltic_charset=0, 
            int chinesebig5_charset=0, int default_charset=0, 
            int easteurope_charset=0, int gb2312_charset=0,
            int greek_charset=0, int hangul_charset=0, int mac_charset=0,
            int oem_charset=0, int russian_charset=0, int shiftjis_charset=0,
            int symbol_charset=0, int turkish_charset=0, int johab_charset=0,
            int hebrew_charset=0, int arabic_charset=0, int thai_charset=0):

        cdef LOGFONT lf
        memset(&lf, 0, sizeof(lf))

        cdef object f
        
        if ansi_charset:
            lf.lfCharSet = BALTIC_CHARSET
        elif baltic_charset:
            lf.lfCharSet = BALTIC_CHARSET
        elif chinesebig5_charset:
            lf.lfCharSet = CHINESEBIG5_CHARSET
        elif default_charset:
            lf.lfCharSet = DEFAULT_CHARSET
        elif easteurope_charset:
            lf.lfCharSet = EASTEUROPE_CHARSET
        elif gb2312_charset:
            lf.lfCharSet = GB2312_CHARSET
        elif greek_charset:
            lf.lfCharSet = GREEK_CHARSET
        elif hangul_charset:
            lf.lfCharSet = HANGUL_CHARSET
        elif mac_charset:
            lf.lfCharSet = MAC_CHARSET
        elif oem_charset:
            lf.lfCharSet = OEM_CHARSET
        elif russian_charset:
            lf.lfCharSet = RUSSIAN_CHARSET
        elif shiftjis_charset:
            lf.lfCharSet = SHIFTJIS_CHARSET
        elif symbol_charset:
            lf.lfCharSet = SYMBOL_CHARSET
        elif turkish_charset :
            lf.lfCharSet = TURKISH_CHARSET 
        elif johab_charset :
            lf.lfCharSet = JOHAB_CHARSET 
        elif hebrew_charset:
            lf.lfCharSet = HEBREW_CHARSET
        elif arabic_charset :
            lf.lfCharSet = ARABIC_CHARSET 
        elif thai_charset :
            lf.lfCharSet = THAI_CHARSET 
        else:
            lf.lfCharSet = DEFAULT_CHARSET

        if face is not None:
            _tcsncpy(lf.lfFaceName, PyUnicode_AsUnicode(face), LF_FACESIZE)
        
        return pymEnumFontFamiliesEx(self._hDC, &lf, func)
        

    def dpToLp(self, points):
        cdef long npoints, i
        cdef long *buf
        
        npoints = len(points)
        if npoints % 2:
            raise ValueError("Invalid points length")
        
        buf = <long *>malloc(sizeof(long) * npoints)
        if buf == NULL:
            raise MemoryError()

        try:
            for i from 0 <= i < npoints:
                buf[i] = points[i]
            
            if 0 == DPtoLP(self._hDC, <POINT *>buf, npoints/2):
                pymRaiseWin32Err()
            
            ret = []
            for i from 0 <= i < npoints:
                ret.append(buf[i])
            return ret

        finally:
            free(buf)
        
    def lpToDp(self, points):
        cdef long npoints, i
        cdef long *buf
        
        npoints = len(points)
        if npoints % 2:
            raise ValueError("Invalid points length")
        
        buf = <long *>malloc(sizeof(long) * npoints)
        if buf == NULL:
            raise MemoryError()

        try:
            for i from 0 <= i < npoints:
                buf[i] = points[i]
            
            if 0 == LPtoDP(self._hDC, <POINT *>buf, npoints/2):
                pymRaiseWin32Err()
            
            ret = []
            for i from 0 <= i < npoints:
                ret.append(buf[i])
            return ret

        finally:
            free(buf)
        

    def pointToLp(self, point):
        cdef POINT pt
        pos = self.dpToLp((0, self.LOGPIXELSY * point / 72))
        org = self.dpToLp((0, 0))
        h = abs(pos[1]-org[1])
        return h
        
    def pointToPixel(self, point):
        return (GetDeviceCaps(self._hDC, LOGPIXELSY) * point) / 72.0
    
    def pixelToPoint(self, pixel):
        return pixel * 72.0 / GetDeviceCaps(self._hDC, LOGPIXELSY)
        
    def setMapMode(self, mode=None,
            anisotropic=0, hienglish=0, himetric=0, isotropic=0,
            loenglish=0, lometric=0, text=0, twips=0):
        
        cdef int f, ret
        if anisotropic:
            f = MM_ANISOTROPIC
        elif hienglish:
            f = MM_HIENGLISH
        elif himetric:
            f = MM_HIMETRIC
        elif isotropic:
            f = MM_ISOTROPIC
        elif loenglish:
            f = MM_LOENGLISH
        elif lometric:
            f = MM_LOMETRIC
        elif text:
            f = MM_TEXT
        elif twips:
            f = MM_TWIPS
        elif mode is not None:
            f = mode
        else:
            raise TypeError("Map mode is not specified.")
    
        ret = SetMapMode(self._hDC, f)
        if 0 == ret:
            pymRaiseWin32Err()
        return ret
        

    def setWindowOrg(self, pos):
        cdef int x, y
        cdef POINT org

        x = pos[0]
        y = pos[1]

        if 0 == SetWindowOrgEx(self._hDC, x, y, &org):
            pymRaiseWin32Err()
        
        return org.x, org.y

    def getWindowOrg(self):
        cdef POINT org
        if 0 == GetWindowOrgEx(self._hDC, &org):
            pymRaiseWin32Err()
        
        return org.x, org.y

    def setViewportOrg(self, pos):
        cdef int x, y
        cdef POINT org

        x = pos[0]
        y = pos[1]

        if 0 == SetViewportOrgEx(self._hDC, x, y, &org):
            pymRaiseWin32Err()
        
        return org.x, org.y

    def getViewportOrg(self):
        cdef POINT org
        if 0 == GetViewportOrgEx(self._hDC, &org):
            pymRaiseWin32Err()
        
        return org.x, org.y
    
    def setWindowExt(self, size):
        cdef int cx, cy
        cdef SIZE org

        cx = size[0]
        cy = size[1]

        if 0 == SetWindowExtEx(self._hDC, cx, cy, &org):
            pymRaiseWin32Err()

        return org.cx, org.cy

    def getWindowExt(self):
        cdef SIZE org
        if 0 == GetWindowExtEx(self._hDC, &org):
            pymRaiseWin32Err()
        
        return org.cx, org.cy

    def setViewportExt(self, size):
        cdef int cx, cy
        cdef SIZE org

        cx = size[0]
        cy = size[1]

        if 0 == SetViewportExtEx(self._hDC, cx, cy, &org):
            pymRaiseWin32Err()
        
        return org.cx, org.cy

    def getViewportExt(self):
        cdef SIZE org
        if 0 == GetViewportExtEx(self._hDC, &org):
            pymRaiseWin32Err()
        
        return org.cx, org.cy

    def beginPath(self):
        if not BeginPath(self._hDC):
            pymRaiseWin32Err()
    
    def endPath(self):
        if not EndPath(self._hDC):
            pymRaiseWin32Err()
    
    def abortPath(self):
        if not AbortPath(self._hDC):
            pymRaiseWin32Err()

    def fillPath(self):
        if not FillPath(self._hDC):
            pymRaiseWin32Err()
    
    def closeFigure(self):
        if not CloseFigure(self._hDC):
            pymRaiseWin32Err()
        
    def strokeAndFillPath(self):
        if not StrokeAndFillPath(self._hDC):
            pymRaiseWin32Err()
    
    def strokePath(self):
        if not StrokePath(self._hDC):
            pymRaiseWin32Err()
        
    def pathToRegion(self):
        cdef HRGN hrgn
        hrgn = PathToRegion(self._hDC)
        if not hrgn:
            pymRaiseWin32Err()
        return Region(PyMFCHandle_FromHandle(hrgn), own=1)

    def bitBlt(self, destrc, srcdc, srcpos, srccopy=0):
        cdef HDC srchdc
        cdef DWORD f
        
        if srccopy:
            f = SRCCOPY
        else:
            raise TypeError("raster op not specified")
            
        srchdc = PyMFCHandle_AsHandle(srcdc.hDC)
        
        if 0 == BitBlt(self._hDC, destrc[0], destrc[1], destrc[2]-destrc[0], destrc[3]-destrc[1],
                srchdc, srcpos[0], srcpos[1], f):
            pymRaiseWin32Err()

    def patBlt(self, rc, copy=0, invert=0, dstinvert=0, blackness=0, whiteness=0):
        cdef DWORD f
        f = 0
        if copy:
            f = PATCOPY
        elif invert:
            f = PATINVERT
        elif dstinvert:
            f = DSTINVERT
        elif blackness:
            f = BLACKNESS
        elif whiteness:
            f = WHITENESS
        else:
            raise TypeError("raster op not specified")
            
        if 0 == PatBlt(self._hDC, rc[0], rc[1], rc[2]-rc[0], rc[3]-rc[1], f):
            pymRaiseWin32Err()

    def playEnhMetaFile(self, _EnhMetaFile emf, rc):
        cdef RECT rect
        rect.left = rc[0]
        rect.top = rc[1]
        rect.right = rc[2]
        rect.bottom = rc[3]

        if 0 == PlayEnhMetaFile(self._hDC, PyMFCHandle_AsHandle(emf.hEmf), &rect):
            pymRaiseWin32Err()

    def invertRect(self, rc):
        cdef RECT rect
        rect.left = rc[0]
        rect.top = rc[1]
        rect.right = rc[2]
        rect.bottom = rc[3]

        if 0 == InvertRect(self._hDC, &rect):
            pymRaiseWin32Err()
        
    def moveTo(self, pos):
        cdef POINT p
        cdef int x, y
        x, y = pos
        if 0 == MoveToEx(self._hDC, x, y, &p):
            pymRaiseWin32Err()
        return (p.x, p.y)

    def lineTo(self, pos):
        cdef POINT p
        cdef int x, y
        x, y = pos
        if 0 == LineTo(self._hDC, x, y):
            pymRaiseWin32Err()
        return

    def arc(self, rc, start, end):
        if 0 == Arc(self._hDC, rc[0], rc[1], rc[2], rc[3], 
                    start[0], start[1], end[0], end[1]):
            pymRaiseWin32Err()
        
    def arcTo(self, rc, start, end):
        if 0 == ArcTo(self._hDC, rc[0], rc[1], rc[2], rc[3], 
                    start[0], start[1], end[0], end[1]):
            pymRaiseWin32Err()

    def setArcDirection(self, clockwise):
        cdef int direction
        if clockwise:
            direction = AD_CLOCKWISE
        else:
            direction = AD_COUNTERCLOCKWISE
        
        if 0 == SetArcDirection(self._hDC, direction):
            pymRaiseWin32Err()

    def polyBezier(self, points):
        cdef DWORD cPoints, i, x, y
        cdef POINT *lppt
        
        cPoints = len(points)
        lppt = <POINT*>malloc(cPoints*sizeof(POINT))
        if lppt == NULL:
            raise MemoryError()
        
        for i from 0 <= i < cPoints:
            x, y = points[i]
            lppt[i].x = x
            lppt[i].y = y
        
        if 0 == PolyBezier(self._hDC, lppt, cPoints):
            pymRaiseWin32Err()
        
    def polyBezierTo(self, points):
        cdef DWORD cPoints, i, x, y
        cdef POINT *lppt
        
        cPoints = len(points)
        lppt = <POINT*>malloc(cPoints*sizeof(POINT))
        if lppt == NULL:
            raise MemoryError()
        
        for i from 0 <= i < cPoints:
            x, y = points[i]
            lppt[i].x = x
            lppt[i].y = y
        
        if 0 == PolyBezierTo(self._hDC, lppt, cPoints):
            pymRaiseWin32Err()
        
    def setTextAlign(self, int baseline=0, int bottom=0, int top=0, int center=0, 
            int left=0, int right=0, int noupdatecp=0, int updatecp=0, int rtlreading=0):
        
        cdef UINT flag
        flag = 0

        if baseline:	flag = flag | TA_BASELINE
        if bottom:	flag = flag | TA_BOTTOM
        if top:		flag = flag | TA_TOP
        if center:	flag = flag | TA_CENTER
        if left:	flag = flag | TA_LEFT
        if right:	flag = flag | TA_RIGHT
        if noupdatecp:	flag = flag | TA_NOUPDATECP
        if rtlreading:	flag = flag | TA_RTLREADING
        if updatecp:	flag = flag | TA_UPDATECP
            
        if GDI_ERROR == SetTextAlign(self._hDC, flag):
            pymRaiseWin32Err()
    
    def setTextColor(self, unsigned long crColor):
        cdef COLORREF ret
        ret = SetTextColor(self._hDC, crColor)
        if CLR_INVALID == ret:
            pymRaiseWin32Err()
        return ret
        
    def setBkColor(self, unsigned long crColor):
        cdef COLORREF ret
        ret = SetBkColor(self._hDC, crColor)
        if CLR_INVALID == ret:
            pymRaiseWin32Err()
        return ret
        
    def setBkMode(self, mode=0, opaque=0, transparent=0):
        cdef int f
        if opaque:
            f = OPAQUE
        elif transparent:
            f = TRANSPARENT
        else:
            f = mode

        return SetBkMode(self._hDC, f)

    def textOut(self, text, pos, rc=None, clipped=0, opaque=0):
        cdef RECT r
        cdef int flag
        cdef int x, y
        cdef BOOL ret
        x, y = pos
        
        if rc:
            r.left = rc[0]
            r.top = rc[1]
            r.right = rc[2]
            r.bottom = rc[3]

            flag = 0
            if clipped: flag = flag | ETO_CLIPPED
            if opaque: flag = flag | ETO_OPAQUE
                
            ret = ExtTextOutW(self._hDC, x, y, flag, &r, PyUnicode_AsUnicode(text), len(text), NULL)

            if not ret:
                pymRaiseWin32Err()

        else:
            ret = TextOutW(self._hDC, x, y, PyUnicode_AsUnicode(text), len(text))

            if not ret:
                pymRaiseWin32Err()
    
    def drawText(self, text, rc, 
            int bottom=0, int calcrect=0, int center=0, int editcontrol=0,
            int end_ellipsis=0, int expandtabs=0, int externalleading=0,
            int internal=0, int left=0, 
            int noclip=0, int noprefix=1,
            int path_ellipsis=0, int right=0, int rtlreading=0,
            int singleline=0, int tabstop=0, int top=0, int vcenter=0,
            int wordbreak=0, int word_ellipsis=0, int margin_left=0, int margin_right=0,
            int tablen=8):

        cdef int flag, ret
        cdef RECT r
        cdef DRAWTEXTPARAMS extparam
        cdef DrawTextResult result
        
        if not text:
            return
        
        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]
        
        flag = 0
        if bottom != 0:		flag = flag | DT_BOTTOM
        if calcrect != 0:	flag = flag | DT_CALCRECT
        if center != 0:		flag = flag | DT_CENTER
        if editcontrol != 0:	flag = flag | DT_EDITCONTROL
        if end_ellipsis != 0:	flag = flag | DT_END_ELLIPSIS
        if expandtabs != 0:	flag = flag | DT_EXPANDTABS
        if externalleading != 0:flag = flag | DT_EXTERNALLEADING
        if internal != 0:	flag = flag | DT_INTERNAL
        if left != 0:		flag = flag | DT_LEFT
        if noclip != 0:		flag = flag | DT_NOCLIP
        if noprefix != 0:	flag = flag | DT_NOPREFIX
        if path_ellipsis != 0:	flag = flag | DT_PATH_ELLIPSIS
        if right != 0:		flag = flag | DT_RIGHT
        if rtlreading != 0:	flag = flag | DT_RTLREADING
        if singleline != 0:	flag = flag | DT_SINGLELINE
        if tabstop != 0:	flag = flag | DT_TABSTOP
        if top != 0:		flag = flag | DT_TOP
        if vcenter != 0:
            flag = flag | DT_VCENTER
            flag = flag | DT_SINGLELINE
        if wordbreak != 0:	flag = flag | DT_WORDBREAK
        if word_ellipsis != 0:	flag = flag | DT_WORD_ELLIPSIS
        

        extparam.cbSize = sizeof(extparam)
        extparam.iTabLength = tablen
        extparam.iLeftMargin = margin_left
        extparam.iRightMargin = margin_right
        extparam.uiLengthDrawn = 0

        ret = DrawTextExW(self._hDC, PyUnicode_AsUnicode(text), len(text), &r, flag, &extparam)
        if 0 == ret:
            pymRaiseWin32Err()
        
        result = DrawTextResult()
        result.height = ret
        result.rc = (r.left, r.top, r.right, r.bottom)
        result.lengthDrawn = extparam.uiLengthDrawn
        return result

    def rectangle(self, rc):
        if 0 == Rectangle(self._hDC, rc[0], rc[1], rc[2], rc[3]):
            pymRaiseWin32Err()
        
    def roundRect(self, rc, ellipse):
        if 0 == RoundRect(self._hDC, rc[0], rc[1], rc[2], rc[3], ellipse[0], ellipse[1]):
            pymRaiseWin32Err()
        
    def ellipse(self, rc):
        if 0 == Ellipse(self._hDC, rc[0], rc[1], rc[2], rc[3]):
            pymRaiseWin32Err()
    
    def frameRect(self, rc, brush):
        cdef RECT r
        cdef HBRUSH hbrush
        
        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]

        hbrush = PyMFCHandle_AsHandle(brush.getHandle())
        if 0 == FrameRect(self._hDC, &r, hbrush):
            pymRaiseWin32Err()

    def fillRect(self, rc, brush):
        cdef RECT r
        cdef HBRUSH hbrush
        
        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]

        hbrush = PyMFCHandle_AsHandle(brush.getHandle())
        if 0 == FillRect(self._hDC, &r, hbrush):
            pymRaiseWin32Err()
        
    def fillSolidRect(self, rc, color):
        cdef RECT r
        cdef TCHAR s
        
        s = 0
        
        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]
        
        SetBkColor(self._hDC, color)
        
        
        if 0 == ExtTextOut(self._hDC, rc[0], rc[1], ETO_OPAQUE, &r, &s, 0, NULL):
            pymRaiseWin32Err()

#        BOOL ExtTextOut(HDC hdc, int X, int Y, int fuOptions, RECT* lprc, char *lpString,
#            int cbCount, int* lpDx)



    def drawEdge(self, rc,
            raisedouter=0, sunkenouter=0, raisedinner=0, sunkeninner=0, 
            raised=0, sunken=0, etched=0, bump=0,
            left=0, top=0, right=0, bottom=0, topleft=0,
            topright=0, bottomleft=0, bottomright=0, rect=0,
            middle=0, soft=0, adjust=0, flat=0, mono=0):
        
        cdef int edge, flag
        cdef RECT r

        edge = 0
        if raisedouter: edge = edge | BDR_RAISEDOUTER
        if sunkenouter: edge = edge | BDR_SUNKENOUTER
        if raisedinner: edge = edge | BDR_RAISEDINNER
        if sunkeninner: edge = edge | BDR_SUNKENINNER
        if raised: edge = edge | EDGE_RAISED
        if sunken: edge = edge | EDGE_SUNKEN
        if etched: edge = edge | EDGE_ETCHED
        if bump: edge = edge | EDGE_BUMP

        flag = 0
        if left:	flag = flag | BF_LEFT
        if top:		flag = flag | BF_TOP
        if right:	flag = flag | BF_RIGHT
        if bottom:	flag = flag | BF_BOTTOM
        if topleft:	flag = flag | BF_TOPLEFT
        if topright:	flag = flag | BF_TOPRIGHT
        if bottomleft:	flag = flag | BF_BOTTOMLEFT
        if bottomright:	flag = flag | BF_BOTTOMRIGHT
        if rect:	flag = flag | BF_RECT
        if middle:	flag = flag | BF_MIDDLE
        if soft:	flag = flag | BF_SOFT
        if adjust:	flag = flag | BF_ADJUST
        if flat:	flag = flag | BF_FLAT
        if mono:	flag = flag | BF_MONO

        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]
        
        if 0 == DrawEdge(self._hDC, &r, edge, flag):
            pymRaiseWin32Err()

    def drawFocusRect(self, rc):
        cdef RECT r
        r.left = rc[0]
        r.top = rc[1]
        r.right = rc[2]
        r.bottom = rc[3]

        if 0 == DrawFocusRect(self._hDC, &r):
            pymRaiseWin32Err()

    def drawIcon(self, pos, icon, size=None, defaultsize=0, image=0, mask=0, normal=0):
        cdef HICON hicon
        cdef int f
        cdef int x, y, width, height
        
        x, y = pos
        if size:
            width, height = size
        else:
            width = 0
            height = 0

        hicon = PyMFCHandle_AsHandle(icon.getHandle())
        
        f = 0
        if defaultsize:
            f = f | DI_DEFAULTSIZE
        if image:
            f = f | DI_IMAGE
        if mask:
            f = f | DI_MASK
        if normal:
            f = f | DI_NORMAL

        if 0 == DrawIconEx(self._hDC, x, y, hicon, width, height, 0, NULL, f):
            pymRaiseWin32Err()

    def drawDIB(self, pos, DIB dib, size=None, srcpos=None, range=None):
        cdef char *bits
        cdef BITMAPINFO *bi
        cdef char *p
        cdef int x, y, xsrc, ysrc
        cdef DWORD width, height
        cdef UINT startscan, scanlines
        
        x, y = pos

        bits = dib.header
        bi = <BITMAPINFO *>bits
        bits = dib.bits
        
        if size:
            width, height = size
        else:
            width = bi.bmiHeader.biWidth
            height = bi.bmiHeader.biHeight
        
        if srcpos:
            xsrc, ysrc = srcpos
        else:
            xsrc = ysrc = 0
        
        if range:
            startscan = range[0]
            scanlines = range[1] - range[0]
        else:
            startscan = 0
            scanlines = bi.bmiHeader.biHeight
        
        if not SetDIBitsToDevice(self._hDC, x, y, width, height,
                xsrc, ysrc, startscan, scanlines, bits, bi, DIB_RGB_COLORS):
            pymRaiseWin32Err()

    def drawState(self, pos, size, image, disabled=0, hideprefix=0, mono=0, prefixonly=0, right=0, union=0):
        cdef int flags
        cdef LPARAM ldata
        cdef WPARAM wdata
        cdef int x, y, cx, cy
        
        x, y = pos
        cx, cy = size
        
        ldata = 0
        wdata = 0
        
        if isinstance(image, unicode):
            flags = DST_TEXT
            ldata = <LPARAM>PyUnicode_AsUnicode(image)
            wdata = len(image)
        elif isinstance(image, Icon):
            flags = DST_ICON
            ldata = <LPARAM>PyMFCHandle_AsHandle(image.getHandle())
        elif isinstance(image, Bitmap):
            flags = DST_BITMAP
            ldata =  <LPARAM>PyMFCHandle_AsHandle(image.getHandle())
        else:
            raise ValueError("Invalid data type")
        
        if disabled:
            flags = flags | DSS_DISABLED
        if hideprefix:
            flags = flags | DSS_HIDEPREFIX
        if mono:
            flags = flags | DSS_MONO
        if prefixonly:
            flags = flags | DSS_PREFIXONLY
        if right:
            flags = flags | DSS_RIGHT
        if union:
            flags = flags | DSS_UNION
        
        if 0 == DrawState(self._hDC, NULL, NULL, ldata, wdata, x, y, cx, cy, flags):
            pymRaiseWin32Err()
            
    def selectClipRgn(self, Region rgn=None):
        cdef int ret
        if not rgn:
            ret = SelectClipRgn(self._hDC, NULL)
        else:
            ret = SelectClipRgn(self._hDC, rgn.hrgn)
        if ret == ERROR:
            pymRaiseWin32Err()

    def getClipRgn(self):
        cdef RectRgn rgn
        cdef int ret
        
        rgn = RectRgn((0,0,0,0))
        ret = GetClipRgn(self._hDC, rgn.hrgn)
        if ret == 1:
            return rgn
        elif ret == 0:
            return None
        else:
            pymRaiseWin32Err()
        
        

cdef class ClientDC(DC):
    cdef HWND _hwnd
    def __init__(self, wnd):
        if not PyMFCHandle_IsHandle(wnd):
            self._hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
        else:
            self._hwnd = PyMFCHandle_AsHandle(wnd)
        self._hDC = GetDC(self._hwnd)
        if not self._hDC:
            pymRaiseWin32Err()

    cdef _release(self):
        if self._hDC:
            if 0 == ReleaseDC(self._hwnd, self._hDC):
                pymRaiseWin32Err()
        self._hDC = NULL
        
cdef class WindowDC(DC):
    cdef HWND _hwnd
    def __init__(self, wnd):
        if not PyMFCHandle_IsHandle(wnd):
            self._hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
        else:
            self._hwnd = PyMFCHandle_AsHandle(wnd)
        self._hDC = GetWindowDC(self._hwnd)
        if not self._hDC:
            pymRaiseWin32Err()

    cdef _release(self):
        if self._hDC:
            if 0 == ReleaseDC(self._hwnd, self._hDC):
                pymRaiseWin32Err()
        self._hDC = NULL
        
cdef class DesktopDC(DC):
    def __init__(self):
        self._hDC = GetDC(NULL)
        if not self._hDC:
            pymRaiseWin32Err()

    cdef _release(self):
        if self._hDC:
            if 0 == ReleaseDC(NULL, self._hDC):
                pymRaiseWin32Err()
        self._hDC = NULL
        

__DEVICE_DISPLAY = unicode("DISPLAY")

cdef class DisplayDC(DC):
    def __init__(self):
        self._hDC = CreateDC(PyUnicode_AsUnicode(__DEVICE_DISPLAY), NULL, NULL, NULL)
        if not self._hDC:
            pymRaiseWin32Err()

cdef extern from "windows.h":
    ctypedef struct PAINTSTRUCT:
        HDC  hdc
        BOOL fErase
        RECT rcPaint

    HDC BeginPaint(HWND hwnd, PAINTSTRUCT *lpPaint)
    BOOL EndPaint(HWND hwnd, PAINTSTRUCT *lpPaint)

cdef class PaintDC(DC):
    cdef HWND _hwnd
    cdef PAINTSTRUCT ps
    
    def __init__(self, wnd):
        if not PyMFCHandle_IsHandle(wnd):
            self._hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
        else:
            self._hwnd = PyMFCHandle_AsHandle(wnd)
        self._hDC = BeginPaint(self._hwnd, &self.ps)
        if self._hDC == NULL:
            pymRaiseWin32Err()

    def __dealloc__(self):
        if self._hDC != NULL:
            if 0 == EndPaint(self._hwnd, &self.ps):
                pymRaiseWin32Err()
            self._hDC = NULL

    def endPaint(self):
        if self._hDC != NULL:
            if 0 == EndPaint(self._hwnd, &self.ps):
                pymRaiseWin32Err()
            self._hDC = NULL
    
    property rc:
        def __get__(self):
            cdef RECT *rc
            rc = &self.ps.rcPaint
            return rc.left, rc.top, rc.right, rc.bottom



cdef extern from "windows.h":
    void test_comp(HDC dc)

cdef class CompatibleDC(DC):
    def __init__(self, dc):
        cdef RECT r
        cdef void *hdc, *hbmp, *ret, *oooo

        if PyMFCHandle_IsHandle(dc):
            hdc = PyMFCHandle_AsHandle(dc)
        else:
            hdc = PyMFCHandle_AsHandle(dc.hDC)

        self._hDC = CreateCompatibleDC(hdc)
        if self._hDC == NULL:
            pymRaiseWin32Err()

cdef class IC(DC):
    def __init__(self, driver=None, device=None):
        cdef TCHAR *c_driver
        cdef TCHAR *c_device

        c_driver = NULL
        if driver is not None:
            c_driver = PyUnicode_AsUnicode(driver)

        c_device = NULL
        if device is not None:
            c_device = PyUnicode_AsUnicode(device)
        
        self._hDC = CreateIC(c_driver, c_device, NULL, NULL)
        if self._hDC == NULL:
            pymRaiseWin32Err()


cdef class EnhMetaFileDC(DC):
    def __init__(self, dc, filename, rc, description):
        cdef HDC hdc
        cdef TCHAR *fname
        cdef RECT rect
        cdef TCHAR *desc

        if PyMFCHandle_IsHandle(dc):
            hdc = PyMFCHandle_AsHandle(dc)
        else:
            hdc = PyMFCHandle_AsHandle(dc.hDC)

        if filename:
            fname = PyUnicode_AsUnicode(filename)
        else:
            fname = NULL

        rect.left = rc[0]
        rect.top = rc[1]
        rect.right = rc[2]
        rect.bottom = rc[3]

        if description:
            desc = PyUnicode_AsUnicode(description)
        else:
            desc = NULL

        self._hDC = CreateEnhMetaFile(hdc, fname, &rect, desc)
        if self._hDC == NULL:
            pymRaiseWin32Err()

    def __dealloc__(self):
        if self._hDC:
            self.close()

    def close(self):
        cdef HANDLE hemf
        cdef _EnhMetaFile ret

        if self._hDC:
            ret = _EnhMetaFile()
            ret._hEmf = CloseEnhMetaFile(self._hDC)
            if ret._hEmf == NULL:
                pymRaiseWin32Err()
                
            if GetEnhMetaFileHeader(ret._hEmf, sizeof(ENHMETAHEADER), &ret._header) != sizeof(ENHMETAHEADER):
                pymRaiseWin32Err()

            self._hDC = NULL
            return ret
        else:
            raise ValueError("empty metafile dc")

cdef extern from "windows.h":
    
    HMONITOR MonitorFromWindow(HWND hwnd, DWORD dwFlags)
    HMONITOR MonitorFromPoint(POINT pt, DWORD dwFlags)


    enum:
        MONITOR_DEFAULTTONEAREST, MONITOR_DEFAULTTONULL, MONITOR_DEFAULTTOPRIMARY 

    ctypedef struct MONITORINFO:
        DWORD  cbSize
        RECT   rcMonitor
        RECT   rcWork
        DWORD  dwFlags

    ctypedef struct MONITORINFOEX:
        DWORD  cbSize
        RECT   rcMonitor
        RECT   rcWork
        DWORD  dwFlags
        TCHAR  szDevice[CCHDEVICENAME]

    ctypedef MONITORINFO *LPMONITORINFO
    BOOL GetMonitorInfo(HMONITOR hMonitor, LPMONITORINFO lpmi)


cdef class Monitor:
    cdef HMONITOR _hMonitor
    cdef MONITORINFOEX mi

    def __init__(self, wnd=None, pos=None):
        cdef HWND hwnd
        cdef POINT pt

        self.mi.cbSize = sizeof(MONITORINFOEX)
        
        if wnd:
            hwnd = NULL
            if not PyMFCHandle_IsHandle(wnd):
                hwnd = PyMFCHandle_AsHandle(wnd.getHwnd())
            else:
                hwnd = PyMFCHandle_AsHandle(wnd)
            self._hMonitor = MonitorFromWindow(hwnd, MONITOR_DEFAULTTONULL)
        elif pos:
            pt.x = pos[0]
            pt.y = pos[1]
            self._hMonitor = MonitorFromPoint(pt, MONITOR_DEFAULTTONULL)
        
        if self._hMonitor == NULL:
            raise ValueError("Not contained within any display monitor")

        
        if not GetMonitorInfo(self._hMonitor, <MONITORINFO *>&self.mi):
            pymRaiseWin32Err()


    property rcwork:
        def __get__(self):
            return (self.mi.rcWork.left, self.mi.rcWork.top, 
                self.mi.rcWork.right, self.mi.rcWork.bottom)
            

cdef extern from "windows.h":
    int DM_ORIENTATION, DM_PAPERSIZE, DM_PAPERLENGTH, DM_PAPERWIDTH, DM_SCALE, DM_COPIES, DM_DEFAULTSOURCE
    int DM_PRINTQUALITY, DM_POSITION, DM_DISPLAYORIENTATION, DM_DISPLAYFIXEDOUTPUT
    int DM_COLOR, DM_DUPLEX, DM_YRESOLUTION, DM_TTOPTION, DM_COLLATE, DM_FORMNAME, DM_LOGPIXELS
    int DM_BITSPERPEL, DM_PELSWIDTH, DM_PELSHEIGHT, DM_DISPLAYFLAGS, DM_NUP, DM_DISPLAYFREQUENCY
    int DM_ICMMETHOD ,DM_ICMINTENT ,DM_MEDIATYPE ,DM_DITHERTYPE ,DM_PANNINGWIDTH ,DM_PANNINGHEIGHT

cdef class DevMode:
    cdef DEVMODE *devmode
    property devicename:
        def __get__(self):
            return _fromWideChar(self.devmode.dmDeviceName)
        def __set__(self, v):
            if len(v) >= CCHDEVICENAME:
                raise ValueError("devicename too long")
            _tcsncpy(self.devmode.dmDeviceName, PyUnicode_AsUnicode(v), CCHDEVICENAME)
    property specversion:
        def __get__(self):
            return self.devmode.dmSpecVersion
        def __set__(self, v):
            cdef int i
            i = v
            self.devmode.dmSpecVersion = <WORD>i
    property driverversion:
        def __get__(self):
            return self.devmode.dmDriverVersion
        def __set__(self, v):
            cdef int i
            i = v
            self.devmode.dmDriverVersion = <WORD>i
    property orientation:
        def __get__(self):
            return self.devmode.dmOrientation
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmOrientation = 0
                self.devmode.dmFields ^= DM_ORIENTATION
            else:
                i = v
                self.devmode.dmOrientation = <short>i
                self.devmode.dmFields |= DM_ORIENTATION
    property papersize:
        def __get__(self):
            return self.devmode.dmPaperSize
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPaperSize = 0
                self.devmode.dmFields ^= DM_PAPERSIZE
            else:
                i = v
                self.devmode.dmPaperSize = <short>i
                self.devmode.dmFields |= DM_PAPERSIZE
    property paperlength:
        def __get__(self):
            return self.devmode.dmPaperLength
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPaperLength = 0
                self.devmode.dmFields ^= DM_PAPERLENGTH
            else:
                i = v
                self.devmode.dmPaperLength = <short>i
                self.devmode.dmFields |= DM_PAPERLENGTH
    property paperwidth:
        def __get__(self):
            return self.devmode.dmPaperWidth
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPaperWidth = 0
                self.devmode.dmFields ^= DM_PAPERWIDTH
            else:
                i = v
                self.devmode.dmPaperWidth = <short>i
                self.devmode.dmFields |= DM_PAPERWIDTH
    property scale:
        def __get__(self):
            return self.devmode.dmScale
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmScale = 0
                self.devmode.dmFields ^= DM_SCALE
            else:
                i = v
                self.devmode.dmScale = <short>i
                self.devmode.dmFields |= DM_SCALE
    property copies:
        def __get__(self):
            return self.devmode.dmCopies
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmCopies = 0
                self.devmode.dmFields ^= DM_COPIES
            else:
                i = v
                self.devmode.dmCopies = <short>i
                self.devmode.dmFields |= DM_COPIES
    property defaultsource:
        def __get__(self):
            return self.devmode.dmDefaultSource
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmDefaultSource = 0
                self.devmode.dmFields ^= DM_DEFAULTSOURCE
            else:
                i = v
                self.devmode.dmDefaultSource = <short>i
                self.devmode.dmFields |= DM_DEFAULTSOURCE
    property printquality:
        def __get__(self):
            return self.devmode.dmPrintQuality
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPrintQuality = 0
                self.devmode.dmFields ^= DM_PRINTQUALITY
            else:
                i = v
                self.devmode.dmPrintQuality = <short>i
                self.devmode.dmFields |= DM_PRINTQUALITY
    property position:
        def __get__(self):
            return (self.devmode.dmPosition.x, self.devmode.dmPosition.y)
        def __set__(self, v):
            if v is None:
                self.devmode.dmPosition.x = 0
                self.devmode.dmPosition.y = 0
                self.devmode.dmFields ^= DM_POSITION
            else:
                self.devmode.dmPosition.x = v[0]
                self.devmode.dmPosition.y = v[1]
                self.devmode.dmFields |= DM_POSITION
#    property displayorientation:
#        def __get__(self):
#            return self.devmode.dmDisplayOrientation
#        def __set__(self, v):
#            if v is None:
#                self.devmode.dmDisplayOrientation = 0
#                self.devmode.dmFields ^= DM_DISPLAYORIENTATION
#            else:
#                self.devmode.dmDisplayOrientation = <DWORD>v
#                self.devmode.dmFields |= DM_DISPLAYORIENTATION
#    property displayfixedoutput:
#        def __get__(self):
#            return self.devmode.dmDisplayFixedOutput
#        def __set__(self, v):
#            if v is None:
#                self.devmode.dmDisplayFixedOutput = 0
#                self.devmode.dmFields ^= DM_DISPLAYFIXEDOUTPUT
#            else:
#                self.devmode.dmDisplayFixedOutput = <DWORD>v
#                self.devmode.dmFields |= DM_DISPLAYFIXEDOUTPUT
    property color:
        def __get__(self):
            return self.devmode.dmColor
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmColor = 0
                self.devmode.dmFields ^= DM_COLOR
            else:
                i = v
                self.devmode.dmColor = <short>i
                self.devmode.dmFields |= DM_COLOR
    property duplex:
        def __get__(self):
            return self.devmode.dmDuplex
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmDuplex = 0
                self.devmode.dmFields ^= DM_DUPLEX
            else:
                i = v
                self.devmode.dmDuplex = <short>i
                self.devmode.dmFields |= DM_DUPLEX
    property yresolution:
        def __get__(self):
            return self.devmode.dmYResolution
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmYResolution = 0
                self.devmode.dmFields ^= DM_YRESOLUTION
            else:
                i = v
                self.devmode.dmYResolution = <short>i
                self.devmode.dmFields |= DM_YRESOLUTION
    property ttoption:
        def __get__(self):
            return self.devmode.dmTTOption
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmTTOption = 0
                self.devmode.dmFields ^= DM_TTOPTION
            else:
                i = v
                self.devmode.dmTTOption = <short>i
                self.devmode.dmFields |= DM_TTOPTION
    property collate:
        def __get__(self):
            return self.devmode.dmCollate
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmCollate = 0
                self.devmode.dmFields ^= DM_COLLATE
            else:
                i = v
                self.devmode.dmCollate = <short>i
                self.devmode.dmFields |= DM_COLLATE
    property formname:
        def __get__(self):
            return _fromWideChar(self.devmode.dmFormName)
        def __set__(self, v):
            if v is None:
                memset(self.devmode.dmFormName, 0, sizeof(WCHAR)*CCHFORMNAME)
                self.devmode.dmFields ^= DM_FORMNAME
            else:
                if len(v) >= CCHFORMNAME:
                    raise ValueError("formname too long")
                _tcsncpy(self.devmode.dmFormName, PyUnicode_AsUnicode(v), CCHFORMNAME)
                self.devmode.dmFields |= DM_FORMNAME
    property logpixels:
        def __get__(self):
            return self.devmode.dmLogPixels
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmLogPixels = 0
                self.devmode.dmFields ^= DM_LOGPIXELS
            else:
                i = v
                self.devmode.dmLogPixels = <WORD>i
                self.devmode.dmFields |= DM_LOGPIXELS
    property bitsperpel:
        def __get__(self):
            return self.devmode.dmBitsPerPel
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmBitsPerPel = 0
                self.devmode.dmFields ^= DM_BITSPERPEL
            else:
                i = v
                self.devmode.dmBitsPerPel = <DWORD>i
                self.devmode.dmFields |= DM_BITSPERPEL
    property pelswidth:
        def __get__(self):
            return self.devmode.dmPelsWidth
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPelsWidth = 0
                self.devmode.dmFields ^= DM_PELSWIDTH
            else:
                i = v
                self.devmode.dmPelsWidth = <DWORD>i
                self.devmode.dmFields |= DM_PELSWIDTH
    property pelsheight:
        def __get__(self):
            return self.devmode.dmPelsHeight
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPelsHeight = 0
                self.devmode.dmFields ^= DM_PELSHEIGHT
            else:
                i = v
                self.devmode.dmPelsHeight = <DWORD>i
                self.devmode.dmFields |= DM_PELSHEIGHT
    property displayflags:
        def __get__(self):
            return self.devmode.dmDisplayFlags
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmDisplayFlags = 0
                self.devmode.dmFields ^= DM_DISPLAYFLAGS
            else:
                i = v
                self.devmode.dmDisplayFlags = <DWORD>i
                self.devmode.dmFields |= DM_DISPLAYFLAGS
    property nup:
        def __get__(self):
            return self.devmode.dmNup
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmNup = 0
                self.devmode.dmFields ^= DM_NUP
            else:
                i = v
                self.devmode.dmNup = <DWORD>i
                self.devmode.dmFields |= DM_NUP
    property displayfrequency:
        def __get__(self):
            return self.devmode.dmDisplayFrequency
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmDisplayFrequency = 0
                self.devmode.dmFields ^= DM_DISPLAYFREQUENCY
            else:
                i = v
                self.devmode.dmDisplayFrequency = <DWORD>i
                self.devmode.dmFields |= DM_DISPLAYFREQUENCY
    property icmmethod:
        def __get__(self):
            return self.devmode.dmICMMethod
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmICMMethod = 0
                self.devmode.dmFields ^= DM_ICMMETHOD
            else:
                i = v
                self.devmode.dmICMMethod = <DWORD>i
                self.devmode.dmFields |= DM_ICMMETHOD
    property icmintent:
        def __get__(self):
            return self.devmode.dmICMIntent
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmICMIntent = 0
                self.devmode.dmFields ^= DM_ICMINTENT
            else:
                i = v
                self.devmode.dmICMIntent = <DWORD>i
                self.devmode.dmFields |= DM_ICMINTENT
    property mediatype:
        def __get__(self):
            return self.devmode.dmMediaType
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmMediaType = 0
                self.devmode.dmFields ^= DM_MEDIATYPE
            else:
                i = v
                self.devmode.dmMediaType = <DWORD>i
                self.devmode.dmFields |= DM_MEDIATYPE
    property dithertype:
        def __get__(self):
            return self.devmode.dmDitherType
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmDitherType = 0
                self.devmode.dmFields ^= DM_DITHERTYPE
            else:
                i = v
                self.devmode.dmDitherType = <DWORD>i
                self.devmode.dmFields |= DM_DITHERTYPE
    property panningwidth:
        def __get__(self):
            return self.devmode.dmPanningWidth
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPanningWidth = 0
                self.devmode.dmFields ^= DM_PANNINGWIDTH
            else:
                i = v
                self.devmode.dmPanningWidth = <DWORD>i
                self.devmode.dmFields |= DM_PANNINGWIDTH
    property panningheight:
        def __get__(self):
            return self.devmode.dmPanningHeight
        def __set__(self, v):
            cdef int i
            if v is None:
                self.devmode.dmPanningHeight = 0
                self.devmode.dmFields ^= DM_PANNINGHEIGHT
            else:
                i = v
                self.devmode.dmPanningHeight = <DWORD>i
                self.devmode.dmFields |= DM_PANNINGHEIGHT

    def __init__(self, ptr):
        cdef DEVMODE *pdevmode
        
        if not ptr:
            raise ValueError("Invalid DEVMOVE pointer")

        pdevmode = <DEVMODE*>PyMFCPtr_AsVoidPtr(ptr)
        self.devmode = <DEVMODE*>malloc(pdevmode.dmSize+pdevmode.dmDriverExtra)
        if not self.devmode:
            raise MemoryError()
        memcpy(self.devmode, pdevmode, pdevmode.dmSize+pdevmode.dmDriverExtra)
    
    def __dealloc__(self):
        if self.devmode:
            free(self.devmode)
            self.devmode = NULL

    def getPtr(self):
        return PyMFCPtr_FromVoidPtr(self.devmode)
