# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

cdef extern from "mfcpragma.h":
    pass

include "pymfc_rtdef.pxi"
include "pymfc_win32def.pxi"


cdef extern from "pymeditor.h":
    ctypedef struct PymStyleFont:
        HANDLE hFont
        LOGFONT lf
        TEXTMETRIC tm
        int spcWidth

    ctypedef struct PymTextColorPair:
        unsigned long fore, back

    ctypedef struct PymStyleColor:
        PymTextColorPair text
        PymTextColorPair text_sel
        PymTextColorPair lf
        PymTextColorPair lf_sel
        PymTextColorPair tab
        PymTextColorPair tab_sel
        PymTextColorPair fullspc
        PymTextColorPair fullspc_sel

    ctypedef struct PymTextStyle:
        PymStyleFont latinFont
        PymStyleFont noLatinFont
        PymStyleColor color

    ctypedef struct PymScreenConf:
        int linegap	# gap between rows
        int tab		# tab width
        int wrap	# wrap line?
        int maxcol	# max column per row. wrap at leftmost of screen if 0
        int wordwrap	# word wrap?
        int indentwrap	# wrapped lines are indented?
        int forcewrap	# wrap always even if no white space is found
        PYMFC_WCHAR *nowrapchars_top	# chars cannot appear top of row
        PYMFC_WCHAR *nowrapchars_end	# chars cannot appear end of row
        int showtab	# show tab char?
        int showlf	# show linefeed?
        int showfullspc	# show double-size space?
        unsigned long bgcolor    # background color
        PYMFC_WCHAR *nowrapheaders	# lines start with these characters should not be wrapped.
        PYMFC_WCHAR *itemize  	# characters used as itemize header

    ctypedef struct PymScreenChar:
        PYMFC_WCHAR c	# character
        short col	# column width
        short width	# display width
        short height	# display height
        short style	# character style
        short selected	# is character selected?
        short latin	# is latin character?

    ctypedef struct PymScreenRow:
        long top
        long end
        long lineNo
        PymScreenChar *chars
        short height
        short ascent
        short indent
        short indentCol

    cdef object PymBuf_SplitRow(
        long pos, long posto, object rowType, long maxwidth, 
        HDC device, object buf, PymScreenConf *conf, int nStyles, PymTextStyle *styles)

    int PymEditor_PaintRow(object row, object dc, int x, int y, int width, 
        PymScreenConf *conf, int nStyles, PymTextStyle *styles) except 0




include "pymfc_editorbuf.pxi"
include "pymfc_editorconf.pxi"
include "pymfc_editorscreen.pxi"

