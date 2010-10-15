# RichEdit control

cdef extern from "pymwnd.h":
    void *new_RichEdit(object obj) except NULL
    unsigned long RichEdit_StreamIn(void *o, object rtf, int flag) except 0
    unsigned long RichEdit_StreamOut(void *o, object rtf, int flag) except 0

cdef extern from "richedit.h":
    int EM_AUTOURLDETECT, EM_CANPASTE, EM_CANREDO, EM_DISPLAYBAND, EM_EXGETSEL,
    int EM_EXLIMITTEXT, EM_EXLINEFROMCHAR, EM_EXSETSEL, EM_FINDTEXT,
    int EM_FINDTEXTEX, EM_FINDTEXTEXW, EM_FINDTEXTW, EM_FINDWORDBREAK,
    int EM_FORMATRANGE, EM_GETAUTOURLDETECT, EM_GETBIDIOPTIONS,
    int EM_GETCHARFORMAT, EM_GETEDITSTYLE, EM_GETEVENTMASK, EM_GETIMECOLOR,
    int EM_GETIMECOMPMODE, EM_GETIMEOPTIONS, EM_GETLANGOPTIONS,
    int EM_GETOLEINTERFACE, EM_GETOPTIONS, EM_GETPARAFORMAT, EM_GETPUNCTUATION,
    int EM_GETREDONAME, EM_GETSCROLLPOS, EM_GETSELTEXT, EM_GETTEXTEX,
    int EM_GETTEXTLENGTHEX, EM_GETTEXTMODE, EM_GETTEXTRANGE,
    int EM_GETTYPOGRAPHYOPTIONS, EM_GETUNDONAME, EM_GETWORDBREAKPROCEX,
    int EM_GETWORDWRAPMODE, EM_GETZOOM, EM_HIDESELECTION, EM_PASTESPECIAL,
    int EM_RECONVERSION, EM_REDO, EM_REQUESTRESIZE, EM_SELECTIONTYPE,
    int EM_SETBIDIOPTIONS, EM_SETBKGNDCOLOR, EM_SETCHARFORMAT, EM_SETEDITSTYLE,
    int EM_SETEVENTMASK, EM_SETFONTSIZE, EM_SETIMECOLOR, EM_SETIMEOPTIONS,
    int EM_SETLANGOPTIONS, EM_SETOLECALLBACK, EM_SETOPTIONS, EM_SETPALETTE,
    int EM_SETPARAFORMAT, EM_SETPUNCTUATION, EM_SETSCROLLPOS,
    int EM_SETTARGETDEVICE, EM_SETTEXTEX, EM_SETTEXTMODE,
    int EM_SETTYPOGRAPHYOPTIONS, EM_SETUNDOLIMIT, EM_SETWORDBREAKPROCEX,
    int EM_SETWORDWRAPMODE, EM_SETZOOM, EM_SHOWSCROLLBAR, EM_STOPGROUPTYPING,
    int EM_STREAMIN, EM_STREAMOUT



    int EN_CORRECTTEXT, EN_DRAGDROPDONE, EN_DROPFILES, EN_IMECHANGE, EN_LINK,
    int EN_MSGFILTER, EN_OBJECTPOSITIONS, EN_PROTECTED, EN_REQUESTRESIZE,
    int EN_SELCHANGE, EN_ALIGNLTR, EN_ALIGNRTL, EN_OLEOPFAILED,
    int EN_SAVECLIPBOARD, EN_STOPNOUNDO 


    int ENM_CHANGE, ENM_CORRECTTEXT, ENM_DRAGDROPDONE, ENM_DROPFILES
    int ENM_IMECHANGE, ENM_KEYEVENTS, ENM_LINK, ENM_MOUSEEVENTS
    int ENM_OBJECTPOSITIONS, ENM_PROTECTED, ENM_REQUESTRESIZE, ENM_SCROLL
    int ENM_SCROLLEVENTS, ENM_SELCHANGE, ENM_UPDATE

    ctypedef struct EDITSTREAM:
        void *dwCookie
        DWORD dwError
        void *pfnCallback

    int SCF_DEFAULT, SCF_ALL, SCF_SELECTION, SCF_WORD

    int CFM_ALL2
    int CFM_BOLD, CFM_ITALIC, CFM_UNDERLINE, CFM_STRIKEOUT
    int CFM_PROTECTED, CFM_LINK, CFM_SIZE, CFM_COLOR, CFM_FACE
    int CFM_OFFSET, CFM_CHARSET
    int CFM_SMALLCAPS, CFM_ALLCAPS, CFM_HIDDEN, CFM_OUTLINE
    int CFM_SHADOW, CFM_EMBOSS, CFM_IMPRINT, CFM_DISABLED
    int CFM_REVISED, CFM_BACKCOLOR, CFM_LCID, CFM_UNDERLINETYPE
    int CFM_WEIGHT, CFM_SPACING, CFM_KERNING, CFM_STYLE
    int CFM_ANIMATION, CFM_REVAUTHOR, CFM_SUBSCRIPT, CFM_SUPERSCRIPT
#    int CFM_AUTOCOLOR, CFM_AUTOBACKCOLOR
    
    int CFE_BOLD, CFE_ITALIC, CFE_UNDERLINE, CFE_STRIKEOUT
    int CFE_PROTECTED, CFE_LINK, CFE_AUTOCOLOR, CFE_SUBSCRIPT
    int CFE_SUPERSCRIPT, CFE_SMALLCAPS, CFE_ALLCAPS, CFE_HIDDEN
    int CFE_OUTLINE, CFE_SHADOW, CFE_EMBOSS, CFE_IMPRINT, CFE_DISABLED
    int CFE_REVISED, CFE_AUTOBACKCOLOR

    int CFU_CF1UNDERLINE, CFU_INVERT, CFU_UNDERLINEDOTTED
    int CFU_UNDERLINEDOUBLE, CFU_UNDERLINEWORD, CFU_UNDERLINE
    int CFU_UNDERLINENONE

    ctypedef struct CHARFORMAT2:
        UINT cbSize
        DWORD dwMask
        DWORD dwEffects
        LONG yHeight
        LONG yOffset
        COLORREF crTextColor
        BYTE bCharSet
        BYTE bPitchAndFamily
        TCHAR szFaceName[LF_FACESIZE]
        _WPAD _wPad2
        WORD wWeight
        SHORT sSpacing
        COLORREF crBackColor
        LCID lcid
        DWORD dwReserved
        SHORT sStyle
        WORD wKerning
        BYTE bUnderlineType
        BYTE bAnimation
        BYTE bRevAuthor

    enum:
        MAX_TAB_STOPS

    int PFM_ALL2
    int PFM_STARTINDENT, PFM_RIGHTINDENT, PFM_OFFSET, PFM_ALIGNMENT
    int PFM_TABSTOPS, PFM_NUMBERING, PFM_OFFSETINDENT, PFM_SPACEBEFORE
    int PFM_SPACEAFTER, PFM_LINESPACING, PFM_STYLE, PFM_BORDER, PFM_SHADING
    int PFM_NUMBERINGSTYLE, PFM_NUMBERINGTAB, PFM_NUMBERINGSTART, PFM_DIR
    int PFM_RTLPARA, PFM_KEEP, PFM_KEEPNEXT, PFM_PAGEBREAKBEFORE
    int PFM_NOLINENUMBER, PFM_NOWIDOWCONTROL, PFM_DONOTHYPHEN
    int PFM_SIDEBYSIDE, PFM_TABLE
    
    int PFN_BULLET

    int PFE_DONOTHYPHEN, PFE_KEEP, PFE_KEEPNEXT, PFE_NOLINENUMBER
    int PFE_NOWIDOWCONTROL, PFE_PAGEBREAKBEFORE, PFE_RTLPARA
    int PFE_SIDEBYSIDE, PFE_TABLECELL, PFE_TABLECELLEND, PFE_TABLEROW

    int PFA_LEFT, PFA_RIGHT, PFA_CENTER, PFA_JUSTIFY


    ctypedef struct PARAFORMAT2:
        UINT cbSize
        _WPAD _wPad1
        DWORD dwMask
        WORD wNumbering
        WORD wReserved
        LONG dxStartIndent
        LONG dxRightIndent
        LONG dxOffset
        WORD wAlignment
        SHORT cTabCount
        LONG rgxTabs[MAX_TAB_STOPS]
        LONG dySpaceBefore
        LONG dySpaceAfter
        LONG dyLineSpacing
        SHORT sStyle
        BYTE bLineSpacingRule
        BYTE bCRC
        WORD wShadingWeight
        WORD wShadingStyle
        WORD wNumberingStart
        WORD wNumberingStyle
        WORD wNumberingTab
        WORD wBorderSpace
        WORD wBorderWidth
        WORD wBorders

    ctypedef struct CHARRANGE:
        LONG cpMin
        LONG cpMax

    int WB_ISDELIMITER, WB_LEFT, WB_LEFTBREAK, WB_MOVEWORDLEFT
    int WB_MOVEWORDRIGHT, WB_RIGHT, WB_RIGHTBREAK

    int SF_TEXT, SF_RTF, SF_RTFNOOBJS, SF_TEXTIZED, SF_UNICODE
    int SF_USECODEPAGE, SF_NCRFORNONASCII, SFF_WRITEXTRAPAR
    int SFF_SELECTION, SFF_PLAINRTF, SFF_PERSISTVIEWSCALE
    int SFF_KEEPDOCINFO, SFF_PWD, SF_RTFVAL


cdef class _charFormat:
    cdef CHARFORMAT2 _format
    
    def __init__(self, *args, **kwargs):
        cdef _charFormat p
        
        self._format.cbSize = sizeof(CHARFORMAT2)
        
        l = len(args)
        if l == 0:
            pass
        elif l == 1:
            format = args[0]
            if isinstance(format, _charFormat):
                p = format
                self._format = p._format
            else:
                raise TypeError("Invalid _charFormat")
        else:
            raise TypeError("Invalid _charFormat")
            
        for name, value in kwargs.items():
            setattr(self, name, value)

    property bold:
        def __get__(self):
            if self._format.dwMask & CFM_BOLD:
                return self._format.dwEffects & CFE_BOLD
            else:
                return None
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_BOLD
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_BOLD
            self._format.dwMask = self._format.dwMask | CFM_BOLD
            
    property italic:
        def __get__(self):
            if self._format.dwMask & CFM_ITALIC:
                return self._format.dwEffects & CFE_ITALIC
            else:
                return None
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_ITALIC
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_ITALIC
            self._format.dwMask = self._format.dwMask | CFM_ITALIC

    property underline:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINE:
                return self._format.dwEffects & CFE_UNDERLINE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_UNDERLINE
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_UNDERLINE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINE

    property strikeout:
        def __get__(self):
            if self._format.dwMask & CFM_STRIKEOUT:
                return self._format.dwEffects & CFE_STRIKEOUT
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_STRIKEOUT
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_STRIKEOUT
            self._format.dwMask = self._format.dwMask | CFM_STRIKEOUT

    property protected:
        def __get__(self):
            if self._format.dwMask & CFM_PROTECTED:
                return self._format.dwEffects & CFE_PROTECTED
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_PROTECTED
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_PROTECTED
            self._format.dwMask = self._format.dwMask | CFM_PROTECTED

    property link:
        def __get__(self):
            if self._format.dwMask & CFM_LINK:
                return self._format.dwEffects & CFE_LINK
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_LINK
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_LINK
            self._format.dwMask = self._format.dwMask | CFM_LINK

#    property autocolor:
#        def __get__(self):
#            if self._format.dwMask & CFM_AUTOCOLOR:
#                return self._format.dwEffects & CFE_AUTOCOLOR
#            else:
#                return None
#            
#        def __set__(self, value):
#            if value:
#                self._format.dwEffects = self._format.dwEffects | CFE_AUTOCOLOR
#            else:
#                self._format.dwEffects = self._format.dwEffects & ~CFE_AUTOCOLOR
#            self._format.dwMask = self._format.dwMask | CFM_AUTOCOLOR
#
    property subscript:
        def __get__(self):
            if self._format.dwMask & CFM_SUBSCRIPT:
                return self._format.dwEffects & CFE_SUBSCRIPT
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_SUBSCRIPT
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_SUBSCRIPT
            self._format.dwMask = self._format.dwMask | CFM_SUBSCRIPT

    property superscript:
        def __get__(self):
            if self._format.dwMask & CFM_SUPERSCRIPT:
                return self._format.dwEffects & CFE_SUPERSCRIPT
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_SUPERSCRIPT
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_SUPERSCRIPT
            self._format.dwMask = self._format.dwMask | CFM_SUPERSCRIPT

    property smallcaps:
        def __get__(self):
            if self._format.dwMask & CFM_SMALLCAPS:
                return self._format.dwEffects & CFE_SMALLCAPS
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_SMALLCAPS
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_SMALLCAPS
            self._format.dwMask = self._format.dwMask | CFM_SMALLCAPS

    property allcaps:
        def __get__(self):
            if self._format.dwMask & CFM_ALLCAPS:
                return self._format.dwEffects & CFE_ALLCAPS
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_ALLCAPS
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_ALLCAPS
            self._format.dwMask = self._format.dwMask | CFM_ALLCAPS

    property hidden:
        def __get__(self):
            if self._format.dwMask & CFM_HIDDEN:
                return self._format.dwEffects & CFE_HIDDEN
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_HIDDEN
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_HIDDEN
            self._format.dwMask = self._format.dwMask | CFM_HIDDEN

    property outline:
        def __get__(self):
            if self._format.dwMask & CFM_OUTLINE:
                return self._format.dwEffects & CFE_OUTLINE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_OUTLINE
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_OUTLINE
            self._format.dwMask = self._format.dwMask | CFM_OUTLINE

    property shadow:
        def __get__(self):
            if self._format.dwMask & CFM_SHADOW:
                return self._format.dwEffects & CFE_SHADOW
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_SHADOW
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_SHADOW
            self._format.dwMask = self._format.dwMask | CFM_SHADOW

    property emboss:
        def __get__(self):
            if self._format.dwMask & CFM_EMBOSS:
                return self._format.dwEffects & CFE_EMBOSS
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_EMBOSS
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_EMBOSS
            self._format.dwMask = self._format.dwMask | CFM_EMBOSS

    property imprint:
        def __get__(self):
            if self._format.dwMask & CFM_IMPRINT:
                return self._format.dwEffects & CFE_IMPRINT
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_IMPRINT
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_IMPRINT
            self._format.dwMask = self._format.dwMask | CFM_IMPRINT

    property disabled:
        def __get__(self):
            if self._format.dwMask & CFM_DISABLED:
                return self._format.dwEffects & CFE_DISABLED
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_DISABLED
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_DISABLED
            self._format.dwMask = self._format.dwMask | CFM_DISABLED

    property revised:
        def __get__(self):
            if self._format.dwMask & CFM_REVISED:
                return self._format.dwEffects & CFE_REVISED
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.dwEffects = self._format.dwEffects | CFE_REVISED
            else:
                self._format.dwEffects = self._format.dwEffects & ~CFE_REVISED
            self._format.dwMask = self._format.dwMask | CFM_REVISED

#    property autobackcolor:
#        def __get__(self):
#            if self._format.dwMask & CFM_AUTOBACKCOLOR:
#                return self._format.dwEffects & CFE_AUTOBACKCOLOR
#            else:
#                return None
#            
#        def __set__(self, value):
#            if value:
#                self._format.dwEffects = self._format.dwEffects | CFE_AUTOBACKCOLOR
#            else:
#                self._format.dwEffects = self._format.dwEffects & ~CFE_AUTOBACKCOLOR
#            self._format.dwMask = self._format.dwMask | CFM_AUTOBACKCOLOR
#
    property height:
        def __get__(self):
            if self._format.dwMask & CFM_SIZE:
                return self._format.yHeight
            else:
                return None
            
        def __set__(self, value):
            self._format.yHeight = value
            self._format.dwMask = self._format.dwMask | CFM_SIZE

    property offset:
        def __get__(self):
            if self._format.dwMask & CFM_OFFSET:
                return self._format.yOffset
            else:
                return None
            
        def __set__(self, value):
            self._format.yOffset = value
            self._format.dwMask = self._format.dwMask | CFM_OFFSET

    property textcolor:
        def __get__(self):
            if self._format.dwMask & CFM_COLOR:
                return self._format.crTextColor
            else:
                return None
            
        def __set__(self, value):
            self._format.crTextColor = value
            self._format.dwMask = self._format.dwMask | CFM_COLOR

    property charset:
        def __get__(self):
            if self._format.dwMask & CFM_CHARSET:
                return self._format.bCharSet
            else:
                return None
            
        def __set__(self, value):
            self._format.bCharSet = <BYTE>value
            self._format.dwMask = self._format.dwMask | CFM_CHARSET

    property pitchandfamily:
        def __get__(self):
            return self._format.bPitchAndFamily
        def __set__(self, value):
            self._format.bPitchAndFamily = <BYTE>value

    property default_pitch:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0x0f) == DEFAULT_PITCH
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0xf0
            self._format.bPitchAndFamily = self._format.bPitchAndFamily | DEFAULT_PITCH

    property fixed_pitch:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0x0f) == FIXED_PITCH
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0xf0
            self._format.bPitchAndFamily = self._format.bPitchAndFamily | FIXED_PITCH

    property variable_pitch:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0x0f) == VARIABLE_PITCH
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0xf0
            self._format.bPitchAndFamily = self._format.bPitchAndFamily | VARIABLE_PITCH

    property ff_decorative:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_DECORATIVE
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_DECORATIVE)

    property ff_dontcare:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_DONTCARE
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_DONTCARE)

    property ff_modern:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_MODERN
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_MODERN)

    property ff_roman:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_ROMAN
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_ROMAN)

    property ff_script:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_SCRIPT
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_SCRIPT)

    property ff_swiss:
        def __get__(self):
            return (self._format.bPitchAndFamily & 0xf0) == FF_SWISS
        def __set__(self, value):
            self._format.bPitchAndFamily = self._format.bPitchAndFamily & 0x0f
            if value:
                self._format.bPitchAndFamily = <BYTE>(self._format.bPitchAndFamily | FF_SWISS)

    property facename:
        def __get__(self):
            if self._format.dwMask & CFM_FACE:
                return _fromWideChar(self._format.szFaceName)
            else:
                return None
            
        def __set__(self, value):
            _tcsncpy(self._format.szFaceName, PyUnicode_AsUnicode(value), LF_FACESIZE)
            self._format.szFaceName[LF_FACESIZE] = 0
            self._format.dwMask = self._format.dwMask | CFM_FACE

    property weight:
        def __get__(self):
            if self._format.dwMask & CFM_WEIGHT:
                return self._format.wWeight
            else:
                return None
            
        def __set__(self, value):
            self._format.wWeight = <WORD>value
            self._format.dwMask = self._format.dwMask | CFM_WEIGHT

    property spacing:
        def __get__(self):
            if self._format.dwMask & CFM_SPACING:
                return self._format.sSpacing
            else:
                return None
            
        def __set__(self, value):
            self._format.sSpacing = <SHORT>value
            self._format.dwMask = self._format.dwMask | CFM_SPACING

    property backcolor:
        def __get__(self):
            if self._format.dwMask & CFM_BACKCOLOR:
                return self._format.crBackColor
            else:
                return None
            
        def __set__(self, value):
            self._format.crBackColor = value
            self._format.dwMask = self._format.dwMask | CFM_BACKCOLOR

    property lcid:
        def __get__(self):
            if self._format.dwMask & CFM_LCID:
                return self._format.lcid
            else:
                return None
            
        def __set__(self, value):
            self._format.lcid = value
            self._format.dwMask = self._format.dwMask | CFM_LCID

    property style:
        def __get__(self):
            if self._format.dwMask & CFM_STYLE:
                return self._format.sStyle
            else:
                return None
            
        def __set__(self, value):
            self._format.sStyle = <SHORT>value
            self._format.dwMask = self._format.dwMask | CFM_STYLE

    property kerning:
        def __get__(self):
            if self._format.dwMask & CFM_KERNING:
                return self._format.wKerning
            else:
                return None
            
        def __set__(self, value):
            self._format.wKerning = <WORD>value
            self._format.dwMask = self._format.dwMask | CFM_KERNING 

    property underlinetype:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType
            else:
                return None
            
        def __set__(self, value):
            self._format.bUnderlineType = <BYTE>value
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE

    property cf1underline:
        def __get__(self):
            if self._format.dwMask & CFM_ITALIC:
                return self._format.bUnderlineType == CFU_CF1UNDERLINE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_CF1UNDERLINE
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE

    property underlineinvert:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_INVERT
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_INVERT
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE
        
    property underlinesolid:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_UNDERLINE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINE
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE
        
    property underlinedotted:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_UNDERLINEDOTTED
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINEDOTTED
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE
        
    property underlinedouble:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_UNDERLINEDOUBLE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINEDOUBLE
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE
        
    property underlinenone:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_UNDERLINENONE
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE
        
    property underlineword:
        def __get__(self):
            if self._format.dwMask & CFM_UNDERLINETYPE:
                return self._format.bUnderlineType == CFU_UNDERLINEWORD
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINEWORD
            else:
                self._format.bUnderlineType = <BYTE>CFU_UNDERLINENONE
            self._format.dwMask = self._format.dwMask | CFM_UNDERLINETYPE

    property animation:
        def __get__(self):
            if self._format.dwMask & CFM_ANIMATION:
                return self._format.bAnimation
            else:
                return None
            
        def __set__(self, value):
            self._format.bAnimation = <BYTE>value
            self._format.dwMask = self._format.dwMask | CFM_ANIMATION

    property revauthor:
        def __get__(self):
            if self._format.dwMask & CFM_REVAUTHOR:
                return self._format.bRevAuthor
            else:
                return None
            
        def __set__(self, value):
            self._format.bRevAuthor = <BYTE>value
            self._format.dwMask = self._format.dwMask | CFM_REVAUTHOR


cdef class _paraFormat:
    cdef PARAFORMAT2 _format
    
    def __init__(self, *args, **kwargs):
        cdef _paraFormat p
        
        self._format.cbSize = sizeof(PARAFORMAT2)
        
        l = len(args)
        if l == 0:
            pass
        elif l == 1:
            format = args[0]
            if isinstance(format, _paraFormat):
                p = format
                self._format = p._format
            else:
                raise TypeError("Invalid _paraFormat")
        else:
            raise TypeError("Invalid _paraFormat")
            
        for name, value in kwargs.items():
            setattr(self, name, value)

    property numbering:
        def __get__(self):
            if self._format.dwMask & PFM_NUMBERING:
                return self._format.wNumbering
            else:
                return None

        def __set__(self, value):
            self._format.wNumbering = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_NUMBERING

    property bullet:
        def __get__(self):
            if self._format.dwMask & PFM_NUMBERING:
                return self._format.wNumbering == PFN_BULLET
            else:
                return None
            
        def __set__(self, value):
            if value:
                self._format.wNumbering = PFN_BULLET
            else:
                self._format.wNumbering = 0
            self._format.dwMask = self._format.dwMask | PFM_NUMBERING

    property startindent:
        def __get__(self):
            if self._format.dwMask & PFM_STARTINDENT:
                return self._format.dxStartIndent
            else:
                return None

        def __set__(self, value):
            self._format.dxStartIndent = value
            self._format.dwMask = self._format.dwMask |  PFM_STARTINDENT

    property rightindent:
        def __get__(self):
            if self._format.dwMask & PFM_RIGHTINDENT:
                return self._format.dxRightIndent
            else:
                return None
            
        def __set__(self, value):
            self._format.dxRightIndent = value
            self._format.dwMask = self._format.dwMask | PFM_RIGHTINDENT

    property offset:
        def __get__(self):
            if self._format.dwMask & PFM_OFFSET:
                return self._format.dxOffset
            else:
                return None
            
        def __set__(self, value):
            self._format.dxOffset = value
            self._format.dwMask = self._format.dwMask | PFM_OFFSET

    property alignment:
        def __get__(self):
            if self._format.dwMask & PFM_ALIGNMENT:
                return self._format.wAlignment
            else:
                return None
            
        def __set__(self, value):
            self._format.wAlignment = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_ALIGNMENT

#    property tabcount:
#        def __get__(self):
#            return self._format.cTabCount
#        def __set__(self, value):
#            self._format.cTabCount = value
#            self._format.dwMask = self._format.dwMask | CFM_REVAUTHOR
#        SHORT cTabCount
#    property tabs:
#        def __get__(self):
#            return self._format.rgxTabs
#        def __set__(self, value):
#            self._format.rgxTabs = value
#            self._format.dwMask = self._format.dwMask | CFM_REVAUTHOR
#        LONG rgxTabs[MAX_TAB_STOPS]

    property spacebefore:
        def __get__(self):
            if self._format.dwMask & PFM_SPACEBEFORE:
                return self._format.dySpaceBefore
            else:
                return None
            
        def __set__(self, value):
            self._format.dySpaceBefore = value
            self._format.dwMask = self._format.dwMask | PFM_SPACEBEFORE

    property spaceafter:
        def __get__(self):
            if self._format.dwMask & PFM_SPACEAFTER:
                return self._format.dySpaceAfter
            else:
                return None
            
        def __set__(self, value):
            self._format.dySpaceAfter = value
            self._format.dwMask = self._format.dwMask | PFM_SPACEAFTER

    property linespacing:
        def __get__(self):
            if self._format.dwMask & PFM_SPACEAFTER:
                return self._format.dyLineSpacing
            else:
                return None
            
        def __set__(self, value):
            self._format.dyLineSpacing = value
            self._format.dwMask = self._format.dwMask | PFM_SPACEAFTER

    property style:
        def __get__(self):
            if self._format.dwMask & PFM_STYLE:
                return self._format.sStyle
            else:
                return None
            
        def __set__(self, value):
            self._format.sStyle = <SHORT>value
            self._format.dwMask = self._format.dwMask |  PFM_STYLE

    property linespacingrule:
        def __get__(self):
            if self._format.dwMask & PFM_SPACEAFTER:
                return self._format.bLineSpacingRule
            else:
                return None
            
        def __set__(self, value):
            self._format.bLineSpacingRule = <BYTE>value
            self._format.dwMask = self._format.dwMask | PFM_SPACEAFTER

    property shadingweight:
        def __get__(self):
            if self._format.dwMask & PFM_SHADING:
                return self._format.wShadingWeight
            else:
                return None
            
        def __set__(self, value):
            self._format.wShadingWeight = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_SHADING

    property shadingstyle:
        def __get__(self):
            if self._format.dwMask & PFM_SHADING:
                return self._format.wShadingStyle
            else:
                return None
            
        def __set__(self, value):
            self._format.wShadingStyle = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_SHADING

    property numberingstart:
        def __get__(self):
            if self._format.dwMask & PFM_NUMBERINGSTART:
                return self._format.wNumberingStart
            else:
                return None
            
        def __set__(self, value):
            self._format.wNumberingStart = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_NUMBERINGSTART

    property numberingstyle:
        def __get__(self):
            if self._format.dwMask & PFM_NUMBERINGSTYLE:
                return self._format.wNumberingStyle
            else:
                return None
            
        def __set__(self, value):
            self._format.wNumberingStyle = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_NUMBERINGSTYLE

    property numberingtab:
        def __get__(self):
            if self._format.dwMask & PFM_NUMBERINGTAB:
                return self._format.wNumberingTab
            else:
                return None
            
        def __set__(self, value):
            self._format.wNumberingTab = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_NUMBERINGTAB

    property borderspace:
        def __get__(self):
            if self._format.dwMask & PFM_BORDER:
                return self._format.wBorderSpace
            else:
                return None
            
        def __set__(self, value):
            self._format.wBorderSpace = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_BORDER

    property borderwidth:
        def __get__(self):
            if self._format.dwMask & PFM_BORDER:
                return self._format.wBorderWidth
            else:
                return None
            
        def __set__(self, value):
            self._format.wBorderWidth = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_BORDER

    property borders:
        def __get__(self):
            if self._format.dwMask & PFM_BORDER:
                return self._format.wBorders
            else:
                return None
            
        def __set__(self, value):
            self._format.wBorders = <WORD>value
            self._format.dwMask = self._format.dwMask | PFM_BORDER



cdef class _richedit(_edit):
    cdef void *newInstance(self):
        return new_RichEdit(self)

    def setEventMask(self, change=False, correcttext=False, dragdropdone=False, 
            dropfiles=False, imechange=False, keyevents=False, link=False, 
            mouseevents=False, objectpositions=False, protected=False, requestresize=False,
            scroll=False, scrollevents=False, selchange=False, update=False):
        
        cdef WPARAM mask
        mask = 0
        if change:
            mask = mask | ENM_CHANGE
        if correcttext:
            mask = mask | ENM_CORRECTTEXT
        if dragdropdone:
            mask = mask | ENM_DRAGDROPDONE
        if dropfiles:
            mask = mask | ENM_DROPFILES
        if imechange:
            mask = mask | ENM_IMECHANGE
        if keyevents:
            mask = mask | ENM_KEYEVENTS
        if link:
            mask = mask | ENM_LINK
        if mouseevents:
            mask = mask | ENM_MOUSEEVENTS
        if objectpositions:
            mask = mask | ENM_OBJECTPOSITIONS
        if protected:
            mask = mask | ENM_PROTECTED
        if requestresize:
            mask = mask | ENM_REQUESTRESIZE
        if scroll:
            mask = mask | ENM_SCROLL
        if scrollevents:
            mask = mask | ENM_SCROLLEVENTS
        if selchange:
            mask = mask | ENM_SELCHANGE
        if update:
            mask = mask | ENM_UPDATE
        
        CWnd_SendMessage_L_L_L(self._cwnd, EM_SETEVENTMASK, 0, mask)
    
    def streamIn(self, infile):
        RichEdit_StreamIn(self._cwnd, infile, SF_RTF)

    def streamOut(self, outfile, text=0, utf8=0):
        cdef long flag
        if text:
            flag = SF_TEXT
        else:
            flag = SF_RTF
        
        if utf8:
            flag = flag | (CP_UTF8 << 16) | SF_USECODEPAGE

        RichEdit_StreamOut(self._cwnd, outfile, flag)

    def getCharFormat(self, selection=0, default=0):
        cdef CHARFORMAT2 cf2
        cdef _charFormat ret
        cdef WPARAM wParam
        
        if selection:
            wParam = SCF_SELECTION
        elif default:
            wParam = SCF_DEFAULT
        else:
            raise ValueError("No range specified")
            
        memset(&cf2, 0, sizeof(cf2))
        cf2.cbSize = sizeof(cf2)
        cf2.dwMask = CFM_ALL2
        
        CWnd_SendMessage_L_P_L(self._cwnd, EM_GETCHARFORMAT, wParam, &cf2)
        
        ret = _charFormat()
        ret._format = cf2
        
        return ret

    def setCharFormat(self, _charFormat format, all=0, selection=0, word=0):
        cdef int f
        f = 0
        if all:
            f = SCF_ALL
        elif selection:
            f = SCF_SELECTION
        elif word:
            f = SCF_WORD | SCF_SELECTION
        else:
            raise ValueError("No range specified")
            
        CWnd_SendMessage_L_P_L_0(self._cwnd, EM_SETCHARFORMAT, f, &(format._format))
        
    def getParaFormat(self):
        cdef PARAFORMAT2 pf2
        cdef _paraFormat ret
        
        memset(&pf2, 0, sizeof(pf2))
        pf2.cbSize = sizeof(pf2)
        pf2.dwMask = PFM_ALL2
        
        CWnd_SendMessage_L_P_L(self._cwnd, EM_GETPARAFORMAT, 0, &pf2)
        
        ret = _paraFormat()
        ret._format = pf2
        
        return ret

    def setParaFormat(self, _paraFormat format):
        CWnd_SendMessage_L_P_L_0(self._cwnd, EM_SETPARAFORMAT, 0, &(format._format))


    def autoUrlDetect(self, detect):
        CWnd_SendMessage_L_L_L(self._cwnd, EM_AUTOURLDETECT, detect, 0)

    def readOnly(self, readonly):
        CWnd_SendMessage_L_L_L(self._cwnd, EM_SETREADONLY, readonly, 0)

    def setWordWrapMode(self, wordwrap=0, wordbreak=0, overflow=0, level1=0, level2=0, custom=0):
        cdef WPARAM mode
        mode = 0
        if wordwrap:
            mode = mode | WBF_WORDWRAP
        if wordbreak:
            mode = mode | WBF_WORDBREAK
        if overflow:
            mode = mode | WBF_OVERFLOW
        if level1:
            mode = mode | WBF_LEVEL1
        if level2:
            mode = mode | WBF_LEVEL2
        if custom:
            mode = mode | WBF_CUSTOM
        
        CWnd_SendMessage_L_L_L(self._cwnd, EM_SETWORDWRAPMODE, mode, 0)
        
    def getSel(self):
        cdef CHARRANGE charrange
        CWnd_SendMessage_L_P_L(self._cwnd, EM_EXGETSEL, 0, &charrange)
        return charrange.cpMin, charrange.cpMax

    def setSel(self, charrange):
        cdef CHARRANGE _charrange
        _charrange.cpMin = charrange[0]
        _charrange.cpMax = charrange[1]

        return CWnd_SendMessage_L_P_L(self._cwnd, EM_EXSETSEL, 0, &_charrange)

    def lineFromChar(self, pos):
        return CWnd_SendMessage_L_L_L(self._cwnd, EM_EXLINEFROMCHAR, 0, pos)
    
    def findWordBreak(self, pos, isdelimiter=0, left=0, leftbreak=0, 
            movewordleft=0, movewordright=0, right=0, rightbreak=0):
        
        cdef int f
        if isdelimiter:
            f = WB_ISDELIMITER
        elif left:
            f = WB_LEFT
        elif leftbreak:
            f = WB_LEFTBREAK
        elif movewordleft:
            f = WB_MOVEWORDLEFT
        elif movewordright:
            f = WB_MOVEWORDRIGHT
        elif right:
            f = WB_RIGHT
        elif rightbreak:
            f = WB_RIGHTBREAK
        else:
            raise ValueError("No operation is specified")
        
        return CWnd_SendMessage_L_L_L(self._cwnd, EM_FINDWORDBREAK, f, pos)
    
    def replaceSel(self, text, undone):
        return CWnd_SendMessage_L_P_L(self._cwnd, EM_REPLACESEL, undone, PyUnicode_AsUnicode(text))
    
    def setBkgndColor(self, color):
        cdef WPARAM wparam
        cdef int c
        
        if color is None:
            wparam = 1
            c = 0
        else:
            wparam = 0
            c = color
        
        return CWnd_SendMessage_L_L_L(self._cwnd, EM_SETBKGNDCOLOR , wparam, c)
    
cdef extern from "richedit.h":
    int ES_DISABLENOSCROLL, ES_EX_NOCALLOLEINIT, ES_NOIME,
    int ES_SELFIME, ES_SUNKEN, ES_VERTICAL 

cdef __init_richedit_styles():
    ret = {
        "left":ES_LEFT, 
        "center":ES_CENTER, 
        "right":ES_RIGHT, 
        "multiline":ES_MULTILINE, 
        "password":ES_PASSWORD, 
        "autovscroll":ES_AUTOVSCROLL, 
        "autohscroll":ES_AUTOHSCROLL, 
        "nohidesel":ES_NOHIDESEL, 
        "readonly":ES_READONLY, 
        "wantreturn":ES_WANTRETURN, 
        "number":ES_NUMBER,
        "disablenoscroll":ES_DISABLENOSCROLL,
        "noime":ES_NOIME,
        "selfime":ES_SELFIME,
        "sunken":ES_SUNKEN,
        "vertical": ES_VERTICAL,
    }
    ret.update(_std_styles)
    return ret

_richedit_styles = __init_richedit_styles()

cdef __init_richedit_ex_styles():
    ret = {
        "nocalloleinit":ES_EX_NOCALLOLEINIT,   # Todo: see KB Q238989
    }
    ret.update(_std_ex_styles)
    return ret

_richedit_ex_styles = __init_richedit_ex_styles()


cdef class RichEditStyle(WndStyle):
    def _initTable(self):
        self._styles = _richedit_styles
        self._exStyles = _richedit_ex_styles



# RichEdit messages

cdef __init_richeditmsg():
    ret = {
        "CORRECTTEXT": (WM_NOTIFY, EN_CORRECTTEXT),
        "DRAGDROPDONE": (WM_NOTIFY, EN_DRAGDROPDONE),
        "DROPFILES": (WM_NOTIFY, EN_DROPFILES),
        "IMECHANGE": (WM_NOTIFY, EN_IMECHANGE),
        "LINK": (WM_NOTIFY, EN_LINK),
        "MSGFILTER": (WM_NOTIFY, EN_MSGFILTER),
        "OBJECTPOSITIONS": (WM_NOTIFY, EN_OBJECTPOSITIONS),
        "PROTECTED": (WM_NOTIFY, EN_PROTECTED),
        "REQUESTRESIZE": (WM_NOTIFY, EN_REQUESTRESIZE),
        "SELCHANGE": (WM_NOTIFY, EN_SELCHANGE),
#        "ALIGNLTR": (WM_NOTIFY, EN_ALIGNLTR),
#        "ALIGNRTL": (WM_NOTIFY, EN_ALIGNRTL),
        "OLEOPFAILED": (WM_NOTIFY, EN_OLEOPFAILED),
        "SAVECLIPBOARD": (WM_NOTIFY, EN_SAVECLIPBOARD),
        "STOPNOUNDO" : (WM_NOTIFY, EN_STOPNOUNDO),
    }
    ret.update(__init_editmsg()) # derive from Edit control
    return ret
    
_richeditmsg = __init_richeditmsg()


