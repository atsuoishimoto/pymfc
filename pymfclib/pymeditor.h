// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMEDITOR_H
#define PYMEDITOR_H

#ifdef __cplusplus
extern "C" {
#else
#	pragma warning(disable:4101 4102)
#endif

void init_pymeditor_sre();

typedef struct {
    HANDLE hFont;
    LOGFONT lf;
    TEXTMETRIC tm;
	int spcWidth;
} PymStyleFont;


typedef struct {
	long fore,back;
} PymTextColorPair;

typedef struct {
	PymTextColorPair text;
	PymTextColorPair text_sel;
	PymTextColorPair lf;
	PymTextColorPair lf_sel;
	PymTextColorPair tab;
	PymTextColorPair tab_sel;
	PymTextColorPair fullspc;
	PymTextColorPair fullspc_sel;
} PymStyleColor;

typedef struct {
    PymStyleFont latinFont;
    PymStyleFont noLatinFont;
    PymStyleColor color;
} PymTextStyle;

typedef struct {
	int linegap;
	int tab;
	int wrap;
	int maxcol;
	int wordwrap;
	int indentwrap;
	int forcewrap;
	wchar_t *nowrapchars_top;
	wchar_t *nowrapchars_end;
	int showtab;
	int showlf;
	int showfullspc;
	long bgcolor;
	wchar_t *nowrapheaders;
	wchar_t *itemize;
} PymScreenConf;

typedef struct {
	wchar_t c;
	short col;
	short width;
	short height;
	short style;
	short selected;
	short latin;
} PymScreenChar;

typedef struct {
	long top;
	long end;
	long lineNo;
	PymScreenChar *chars;
	short height;
	short ascent;
	short indent;
	short indentCol;
} PymScreenRow;

void *PymBuf_New();
long PymBuf_Free(void *buf);

long PymBuf_Insert(void *buf, long pos, PyObject *s);
long PymBuf_Dele(void *buf, long pos, long posto);
long PymBuf_Replace(void *o, long pos, long posto, PyObject *s);

PyObject *PymBuf_GetChar(void *buf, long pos, long posto);
PyObject *PymBuf_GetStyle(void *buf, long pos, long posto);
long PymBuf_SetStyle(void *buf, long pos, long posto, UINT idx);
long PymBuf_GetLineNo(void *buf, long pos);
long PymBuf_GetLineNoPos(void *buf, long lineno);
long PymBuf_GetTOL(void *buf, long pos);
long PymBuf_GetEOL(void *buf, long pos);
long PymBuf_GetLineFeed(void *buf, long pos);
long PymBuf_GetSize(void *buf);

long PymBuf_Find(void *o, long pos, long to, wchar_t c);
long PymBuf_Find_back(void *o, long pos, long to, wchar_t c);
long PymBuf_Find_i(void *o, long pos, long to, wchar_t c);
long PymBuf_Find_i_back(void *o, long pos, long to, wchar_t c);
PyObject *PymBuf_FindOneOf(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
PyObject *PymBuf_FindOneOf_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
long PymBuf_FindString(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
long PymBuf_FindString_i(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
long PymBuf_FindString_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
long PymBuf_FindString_i_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t);
long PymBuf_FindString_esc(void *o, long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc);
long PymBuf_FindString_i_esc(void *o, long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc);
long PymBuf_FindStyle(void *o, long pos, long to, UINT idx);
long PymBuf_FindStyle_back(void *o, long pos, long to, UINT idx);
PyObject *PymBuf_FindStyleOneOf(void *o, long pos, long to, long *f, long *t);
PyObject *PymBuf_FindStyleOneOf_back(void *o, long pos, long to, long *f, long *t);
PyObject *PymBuf_GetStyleRange(void *o, long pos);


PyObject *PymBuf_SplitRow(
    long pos, long posto, PyObject *rowType, long maxwidth, 
    HDC device, PyObject *buf, PymScreenConf *conf, int nStyles, PymTextStyle *styles);

int PymEditor_PaintRow(PyObject *dc, PyObject *row, int x, int y, int width, 
    PymScreenConf *conf, int nStyles, PymTextStyle *styles);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
#include "gappedbuf.h"

typedef std::vector<PymScreenChar> PymScreenChars;




struct PymCharInfo {
// | 15 14 13 12 11 10 9 | 8 7 6 5 4  3 | 2 1 0 |
// |         style       |                      |

	enum {MAX_STYLE=127};
	unsigned short m_flags;

	void init(wchar_t c, UINT style) {
		m_flags = 0;
		setStyleIdx(style);
	}
	void setStyleIdx(UINT n) {
		m_flags = (m_flags & 0xf7) | (n << 9);
	}
	
	UINT getStyleIdx() const {
		return m_flags >> 9;
	}
};

/*
struct PymCharStyle {
	PymStyleFont latinFont;
	PymStyleFont nonLatinFont;
	PymStyleColor color;
};
*/


template <class T, class BUDDY> 
class CombinedGappedBuf:public GappedBuffer<T> {
public:
	CombinedGappedBuf(GappedBuffer<BUDDY> &buddy):m_buddy(buddy) {
	}

	void insBuffer(long pos, long len) {
		m_buddy.expandBuf(pos, len);
		GappedBuffer<T>::insBuffer(pos, len);
	}

	void delBuffer(long from, long to) {
		m_buddy.del(from, to);
		GappedBuffer<T>::delBuffer(from, to);
	}
	
protected:	
	
	GappedBuffer<BUDDY> &m_buddy;
};


class PymBuffer {
public:
	PymBuffer():m_chars(m_infos) {
	}
	virtual ~PymBuffer() {
	}

	long begin() {
		return 0;
	}

	long end() const {
		return m_chars.end();
	}

	long size() const {
		return m_chars.end();
	}

	void get(long from, long to, wchar_t *buf) const {
		m_chars.get(from, to, buf);
	}

	wchar_t get(long from) const {
		return m_chars.get(from);
	}

	void ins(long pos, const wchar_t *from, const wchar_t *to, UINT styleIdx=-1);
	void del(long from, long to);
	void rep(long posfrom, long posto, const wchar_t *from, const wchar_t *to, UINT styleIdx=-1);

	void setStyleIdx(long from, long to, UINT idx);
	UINT getStyleIdx(long from) const {
		ASSERT(from < end());

		return m_infos.get(from).getStyleIdx();
	}

	void getStyleIdx(long from, long to, UINT *buf) const {
		ASSERT(from <= to);
		ASSERT(to <= end());

		for (long pos = from; pos < to; pos++) {
			const PymCharInfo &info = m_infos.get(from);
			*buf++ = info.getStyleIdx();
		}
	}

	enum CHAR_TYPE {
		CHAR_SINGLE=0, CHAR_WORDCHAR=1, CHAR_WS=2, CHAR_GRAPH=3, 
		CHAR_CTRL=4, CHAR_KANA=5, 
		CHAR_MB_BEGIN=10,
		CHAR_MB_KANA=11, CHAR_MB_HIRA=12, CHAR_MB_SYMBOL=13,
		CHAR_MB_FULLWIDTH=14, CHAR_MB=15, CHAR_MB_WS=16};
	
	inline CHAR_TYPE getCStyle(long pos) {
		ASSERT(pos < end());

		wchar_t c = get(pos);
		if (c < 256)
		{
			if (iscsym(c))
				return CHAR_WORDCHAR;
			if (isspace(c))
				return CHAR_WS;
			if (isgraph(c))
				return CHAR_GRAPH;
			if (iscntrl(c))
				return CHAR_CTRL;
			return CHAR_SINGLE;
		}
		else
		{
			if (0x3040 <= c && c <= 0x309f) {
				return CHAR_MB_HIRA;
			}
			else if (0x30a0 <= c && c <= 0x30ff) {
				return CHAR_MB_KANA;
			}
			else if (0xff61 <= c && c <= 0xff9f) {
				return CHAR_KANA;
			}
			else if (0x3000  == c) {
				return CHAR_MB_WS;
			}
			else if (0x3001  <= c && c <= 0x303f) {
				return CHAR_MB_SYMBOL;
			}
			else if (0xff00  <= c && c <= 0xffef) {
				return CHAR_MB_FULLWIDTH;
			}else {
				return CHAR_MB;
			}
		}

	/*
		hiragana
		3040-309f

		katakana
		30A0-30FF

		CJK Symbols and Punctuation
		3000-303f

		Katakana Phonetic Extensions
		31F0-31FF

		Enclosed CJK Letters and Months
		3200-32ff

		CJK Compatibility
		Range: 3300-33FF

		CJK Unified Ideographs Extension A
		Range: 3400-4DBF

		CJK Unified Ideographs
		Range: 4E00-F9FAF

		Private Use Area
		Range: E000-F8FF

		CJK Compatibility Ideographs
		Range: F900-FAFF

		CJK Compatibility Forms
		Range: FE30-FE4F

		Halfwidth and Fullwidth Forms
		Range: FF00-FFEF
	*/
	}

	long find(long pos, long to, wchar_t c);
	long find_back(long pos, long to, wchar_t c);
	long find_i(long pos, long to, wchar_t c);
	long find_i_back(long pos, long to, wchar_t c);
	long findOneOf(long pos, long to, const wchar_t *c, const wchar_t *t, UINT &ret);
	long findOneOf_back(long pos, long to, const wchar_t *c, const wchar_t *t, UINT &ret);
	long findString(long pos, long to, const wchar_t *c, const wchar_t *t);
	long findString_i(long pos, long to, const wchar_t *c, const wchar_t *t);
	long findString_back(long pos, long to, const wchar_t *c, const wchar_t *t);
	long findString_i_back(long pos, long to, const wchar_t *c, const wchar_t *t);
	long findString(long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc);
	long findString_i(long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc);
	long findStyle(long pos, long to, UINT idx);
	long findStyle_back(long pos, long to, UINT idx);
	long findStyleOneOf(long pos, long to, long *f, long *t, UINT &ret);
	long findStyleOneOf_back(long pos, long to, long *f, long *t, UINT &ret);
	void getStyleRange(long pos, long &f, long &t);

	
	bool isLineBreak(long pos) {
		ASSERT(pos <= end());
		if (pos==end() || get(pos) == '\n') {
			return true;
		}
		return false;
	}
	long getTopOfLine(long pos) {
		ASSERT(pos <= end());
		
		long ret = find_back(0, pos, '\n');
		if (ret == -1) {
			return 0;
		}
		else {
			return ret+1;
		}
/*
		long ret(pos);
		while (ret)
		{
			--ret;
			if (isLineBreak(ret))
				return ++ret;
		}
*/
		return ret;
	}

	long getEndOfLine(long pos) {
		ASSERT(pos <= end());

		long ret = find(pos, end(), '\n');
		if (ret == -1) {
			return end();
		}
		return ret+1;
	}
	
	long getLineFeed(long pos) {
		ASSERT(pos <= end());

		long ret = find(pos, end(), '\n');
		if (ret == -1) {
			return end();
		}
		return ret;
	}
	
	long getLineNo(long pos) {
		if (!m_lf.size()) {
			return 0;
		}
		if (m_lf.get(m_lf.size()-1) < pos) {
			return m_lf.size();
		}

		long start = 0;
		long end = m_lf.size()-1;

		while (start <= end) {
			long p = start + (end - start) / 2;
			long v = m_lf.get(p);
			
			if (v < pos) {
				start = p + 1;
			}
			else {
				if (!p || m_lf.get(p-1) < pos) {
					return p;
				}
				else {
					end = p - 1;
				}
			}
		}
			
		return m_lf.size();
	}

	long getLineNoPos(long lineno) {
		if (lineno >= m_lf.size()) {
			return end();
		}
		else {
			return m_lf.get(lineno);
		}
	}

public:
	GappedBuffer<PymCharInfo> m_infos;
	CombinedGappedBuf<wchar_t, PymCharInfo> m_chars;
	GappedBuffer<long> m_lf;
};





#endif



#endif