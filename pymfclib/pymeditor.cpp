// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pydt.h"
#include "pymfcdefs.h"
#include "pymeditor.h"
#include "pymutils.h"







void PymBuffer::ins(long pos, const wchar_t *from, const wchar_t *to, UINT styleIdx) {

//DUMPTIME("PymBuffer::ins:")

	ASSERT(from <= to);
	ASSERT(pos <= m_chars.end());

	if (from == to)
		return;

	m_chars.ins(pos, from, to);

	if (styleIdx == -1) {
		if (pos == 0) {
			styleIdx = 0;
		}
		else {
			getStyleIdx(pos-1, pos, &styleIdx);
		}
	}

	long ipos = pos;
	for (const wchar_t *c = from; c != to; c++, ipos++) {
		PymCharInfo &info = m_infos.get(ipos);
		info.init(*c, styleIdx);
	}

	long lno = getLineNo(pos);
	
	for (long p = 0; p < (to - from); p++) {
		if (from[p] == L'\n') {
			m_lf.insValue(lno, pos+p);
			lno += 1;
		}
	}

	long d = to-from;
	for (; lno < m_lf.size(); lno++) {
		m_lf.get(lno) += d;
	}

#if defined(_DEBUG) && 0
	for (long l = 0; l < m_lf.size(); l++) {
		assert(m_chars.get(m_lf.get(l)) == L'\n');
	}

	for (long pp = 0, n = 0; pp < m_chars.size(); pp++) {
		if (m_chars.get(pp) == L'\n') {
			assert(m_lf.get(n) == pp);
			n += 1;
		}
	}

	assert(m_lf.size() == n);
#endif

}	


void PymBuffer::del(long from, long to) {
	ASSERT(from <= to);
	ASSERT(to <= end());
	if (from == to)
		return;
	m_chars.del(from, to);

	
	long lno = getLineNo(from);
	while (lno < m_lf.size()) {
		long p = m_lf.get(lno);
		if (p >= to) {
			break;
		}
		m_lf.del(lno, lno + 1);
	}


	for (; lno < m_lf.size(); lno++) {
		m_lf.get(lno) -= (to-from);
	}

#if defined(_DEBUG) && 0
	for (long l = 0; l < m_lf.size(); l++) {
		assert(m_chars.get(m_lf.get(l)) == L'\n');
	}

	for (long pp = 0, n = 0; pp < m_chars.size(); pp++) {
		if (m_chars.get(pp) == L'\n') {
			assert(m_lf.get(n) == pp);
			n += 1;
		}
	}

	assert(m_lf.size() == n);
#endif

}	

void PymBuffer::rep(long posfrom, long posto, const wchar_t *from, const wchar_t *to, UINT styleIdx) {
	del(posfrom, posto);
	ins(posfrom, from, to, styleIdx);
}

void PymBuffer::setStyleIdx(long from, long to, UINT idx) {
	ASSERT(from <= to);
	ASSERT(to <= end());

	for (; from < to; from++) {
		m_infos.get(from).setStyleIdx(idx);
	}
}

long PymBuffer::find(long pos, long to, wchar_t c) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	return m_chars.find(pos, to, c);
}

long PymBuffer::find_back(long pos, long to, wchar_t c) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	return m_chars.find_back(pos, to, c);
}

long PymBuffer::find_i(long pos, long to, wchar_t c) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	wchar_t c1 = towupper(c);
	wchar_t c2 = towlower(c);
	
	return m_chars.findOr(pos, to, c1, c2);
}

long PymBuffer::find_i_back(long pos, long to, wchar_t c) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	wchar_t c1 = towupper(c);
	wchar_t c2 = towlower(c);
	
	return m_chars.findOr_back(pos, to, c1, c2);
}

long PymBuffer::findOneOf(long pos, long to, const wchar_t *c, const wchar_t *t, UINT &ret) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	return m_chars.findOneOf(pos, to, c, t, ret);
}

long PymBuffer::findOneOf_back(long pos, long to, const wchar_t *c, const wchar_t *t, UINT &ret) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	return m_chars.findOneOf_back(pos, to, c, t, ret);
}

// todo: Speed up!
long PymBuffer::findString(long pos, long to, const wchar_t *c, const wchar_t *t) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	while (pos < to) {
		long p = m_chars.find(pos, to, *c);
		if (p == -1) {
			break;
		}
		if (p + (t-c) > to) {
			break;
		}
		if (m_chars.isMatch(p, c, t)) {
			return p;
		}
		pos = p + 1;
	}
	return -1;
}

long PymBuffer::findString_back(long pos, long to, const wchar_t *c, const wchar_t *t) {
	ASSERT(pos <= to);
	ASSERT(to <= end());
	
	if (!to) {
		return -1;
	}
	long charto = to;
	while (pos <= to) {
		long p = m_chars.find_back(pos, to, *c);
		if (p == -1) {
			break;
		}
		if (p + (t-c) > charto) {
			to = p - 1;
			continue;
		}
		if (m_chars.isMatch(p, c, t)) {
			return p;
		}
		pos = p - 1;
	}
	return -1;
}

long PymBuffer::findString_i(long pos, long to, const wchar_t *c, const wchar_t *t) {

	ASSERT(pos <= to);
	ASSERT(to <= end());

	wchar_t c1 = towupper(*c);
	wchar_t c2 = towlower(*c);
	
	std::vector<wchar_t> str;
	for (const wchar_t *f=c; f != t; f++) {
		str.push_back(towupper(*f));
	}
	long len = t-c;
	c = &str[0];

	while (pos <= to) {
		long p = m_chars.findOr(pos, to, c1, c2);
		if (p == -1) {
			break;
		}

		if (p + len > to) {
			break;
		}
		
		long i;
		for (i = 0; i < len; i++) {
			if (towupper(m_chars.get(p+i)) != c[i]) {
				break;
			}
		}
		if (i == len) {
			return p;
		}
		pos = p+1;
	}
	return -1;
}

long PymBuffer::findString_i_back(long pos, long to, const wchar_t *c, const wchar_t *t) {

	ASSERT(pos <= to);
	ASSERT(to <= end());

	wchar_t c1 = towupper(*c);
	wchar_t c2 = towlower(*c);
	
	std::vector<wchar_t> str;
	for (const wchar_t *f=c; f != t; f++) {
		str.push_back(towupper(*f));
	}
	
	int len = t-c;
	c = &str[0];
	long charto = to;

	while (pos <= to) {
		long p = m_chars.findOr_back(pos, to, c1, c2);
		if (p == -1) {
			break;
		}

		if (p + len > charto) {
			to = p - 1;
			continue;
		}
		long i;
		for (i = 0; i < len; i++) {
			if (towupper(m_chars.get(p+i)) != c[i]) {
				break;
			}
		}
		if (i == len) {
			return p;
		}
		to = p-1;
	}
	return -1;
}

long PymBuffer::findString(long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc) {
	wchar_t st[2];
	st[0] = *c;
	st[1] = esc;

	while (pos < to) {
		UINT isEsc;
		long p = m_chars.findOneOf(pos, to, st, st+2, isEsc);

		if (p == -1) {
			break;
		}
		
		if (isEsc) {
			pos = p + 2;
			continue;
		}

		if (p + (t-c) > to) {
			break;
		}

		if (m_chars.isMatch(p, c, t)) {
			return p;
		}
	}
	return -1;
}

long PymBuffer::findString_i(long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc) {
	wchar_t st[2];
	st[0] = *c;
	st[1] = esc;

	wchar_t c1 = towupper(*c);
	wchar_t c2 = towlower(*c);
	
	std::vector<wchar_t> str;
	for (const wchar_t *f=c; f != t; f++) {
		str.push_back(towupper(*f));
	}
	
	int len = t-c;
	c = &str[0];

	while (pos < to) {
		UINT isEsc;
		long p = m_chars.findOneOf(pos, to, st, st+2, isEsc);

		if (p == -1) {
			break;
		}
		
		if (isEsc) {
			pos = p + 2;
			continue;
		}

		if (p + len > to) {
			break;
		}
		long i;
		for (i = 0; i < len; i++) {
			if (towupper(m_chars.get(p+i)) != c[i]) {
				break;
			}
		}
		if (i == len) {
			return p;
		}
	}
	return -1;
}

long PymBuffer::findStyle(long pos, long to, UINT idx) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	for (long p = pos; p < to; p++) {
		UINT char_idx = m_infos.get(p).getStyleIdx();
		if (char_idx == idx) {
			return p;
		}
	}
	return -1;
}

long PymBuffer::findStyle_back(long pos, long to, UINT idx) {
	ASSERT(pos <= to);
	ASSERT(to <= end());

	for (long p = to-1; p <= pos; p--) {
		UINT char_idx = m_infos.get(p).getStyleIdx();
		if (char_idx == idx) {
			return p;
		}
	}
	return -1;
}

long PymBuffer::findStyleOneOf(long pos, long to, long *f, long *t, UINT &ret) {
	ASSERT(pos <= to);
	ASSERT(to <= end());


	for (long p = pos; p < to; p++) {
		UINT char_idx = m_infos.get(p).getStyleIdx();
		for (long *s = f; s != t; p++) {
			if ((UINT)*s == char_idx) {
				ret = s-f;
				return p;
			}
		}
	}
	
	return -1;
}

long PymBuffer::findStyleOneOf_back(long pos, long to, long *f, long *t, UINT &ret) {
	for (long p = to-1; p <= pos; p--) {
		UINT char_idx = m_infos.get(p).getStyleIdx();
		for (long *s = f; s != t; p++) {
			if ((UINT)*s == char_idx) {
				ret = s-f;
				return p;
			}
		}
	}
	return -1;
}


void PymBuffer::getStyleRange(long pos, long &f, long &t) {
	UINT cur_idx = m_infos.get(pos).getStyleIdx();

	f = t = pos;
	long p;
	for (p = pos-1; p >= 0; p--) {
		UINT pos_idx = m_infos.get(p).getStyleIdx();
		if (pos_idx != cur_idx) {
			break;
		}
		f = p;
	}

	for (p = pos+1; p < size(); p++) {
		UINT pos_idx = m_infos.get(p).getStyleIdx();
		if (pos_idx != cur_idx) {
			break;
		}
		t = p;
	}
}




















inline
static PymBuffer *getBuf(void *o) {
	if (!o) {
		throw PyDTExc_InvalidType("NULL PymBuffer");
	}
	
	PymBuffer *ret = dynamic_cast<PymBuffer*>((PymBuffer*)o);
	if (!ret) {
		throw PyDTExc_InvalidType("Invalid PymBuffer");
	}
	return ret;
}

void *PymBuf_New() {
	PyMFC_PROLOGUE(PymBuf_New);
	return (void *)new PymBuffer();
	PyMFC_EPILOGUE(0);
}

long PymBuf_Free(void *o) {
	PyMFC_PROLOGUE(PymBuf_Free);

	delete getBuf(o);
	return TRUE;

	PyMFC_EPILOGUE(0);
}

long PymBuf_Insert(void *o, long pos, PyObject *s) {
	PyMFC_PROLOGUE(PymBuf_Insert);
	
	PymBuffer *buf = getBuf(o);
	PyDTUnicode str(s, false);
	size_t size = str.size();
	const wchar_t *f = str.asUnicode();
	const wchar_t *t = f + size;
	buf->ins(pos, f, t);
	
	return TRUE;

	PyMFC_EPILOGUE(0);
}

long PymBuf_Dele(void *o, long pos, long posto) {
	PyMFC_PROLOGUE(PymBuf_Dele);
	
	PymBuffer *buf = getBuf(o);
	buf->del(pos, posto);
	
	return TRUE;

	PyMFC_EPILOGUE(0);
}

long PymBuf_Replace(void *o, long pos, long posto, PyObject *s) {
	PyMFC_PROLOGUE(PymBuf_Replace);
	
	PymBuffer *buf = getBuf(o);
	PyDTUnicode str(s, false);
	size_t size = str.size();
	const wchar_t *f = str.asUnicode();
	const wchar_t *t = f + size;
	
	buf->rep(pos, posto, f, t);
	
	return TRUE;

	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_GetChar(void *o, long pos, long posto) {
	PyMFC_PROLOGUE(PymBuf_GetChar);
	
	PymBuffer *buf = getBuf(o);

	if (pos < 0)
		pos = 0;
	else if (pos > buf->end())
		pos = buf->end();
	if (posto < 0)
		posto = 0;
	if (posto < pos)
		posto = pos;
	else if (posto > buf->end())
		posto = buf->end();

	if (posto <= pos) {
		return PyDTUnicode(L"").detach();
	}

	if (posto - pos == 1) {
		wchar_t c = buf->get(pos);
		return PyDTUnicode(&c, 1).detach();
	}
	else {
		std::vector<wchar_t> s;
		s.resize(posto - pos);

		buf->get(pos, posto, &s[0]);
		return PyDTUnicode(&s[0], posto - pos).detach();
	}
	

	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_GetStyle(void *o, long pos, long posto) {
	PyMFC_PROLOGUE(PymBuf_GetStyle);
	
	PymBuffer *buf = getBuf(o);
	if (posto <= pos) {
		return PyDTList(0).detach();
	}

	std::vector<UINT> s;
	s.resize(posto - pos);
	buf->getStyleIdx(pos, posto, &s[0]);
	
	PyDTList ret(posto - pos);
	for (long i = pos; i < posto; i++) {
		ret.setItem(i - pos, PyDTInt(s[i - pos]));
	}

	return ret.detach();

	PyMFC_EPILOGUE(0);
}

long PymBuf_SetStyle(void *o, long pos, long posto, UINT idx) {
	PyMFC_PROLOGUE(PymBuf_SetStyle);
	
	PymBuffer *buf = getBuf(o);

	if (pos == posto) {
		return TRUE;
	}

	if (posto < pos) {
		throw PyDTExc_InvalidValue("Invalid pos/posto");
	}
	if (idx > PymCharInfo::MAX_STYLE) {
		throw PyDTExc_InvalidValue("Invalid style idx");
	}

	buf->setStyleIdx(pos, posto, idx);
	return TRUE;

	PyMFC_EPILOGUE(0);
}

long PymBuf_GetLineNo(void *o, long pos) {
	PyMFC_PROLOGUE(PymBuf_GetLineNo);
	
	PymBuffer *buf = getBuf(o);
	return buf->getLineNo(pos);

	PyMFC_EPILOGUE(0);
}

long PymBuf_GetLineNoPos(void *o, long lineno) {
	PyMFC_PROLOGUE(PymBuf_GetLineNoPos);
	
	PymBuffer *buf = getBuf(o);
	return buf->getLineNoPos(lineno);

	PyMFC_EPILOGUE(0);
}

long PymBuf_GetTOL(void *o, long pos) {
	PyMFC_PROLOGUE(PymBuf_GetTOL);
	
	PymBuffer *buf = getBuf(o);
	return buf->getTopOfLine(pos);

	PyMFC_EPILOGUE(0);
}

long PymBuf_GetEOL(void *o, long pos) {
	PyMFC_PROLOGUE(PymBuf_GetEOL);
	
	PymBuffer *buf = getBuf(o);
	return buf->getEndOfLine(pos);

	PyMFC_EPILOGUE(0);
}


long PymBuf_GetLineFeed(void *o, long pos) {
	PyMFC_PROLOGUE(PymBuf_GetLineFeed);
	
	PymBuffer *buf = getBuf(o);
	return buf->getLineFeed(pos);

	PyMFC_EPILOGUE(0);
}


long PymBuf_GetSize(void *o) {
	PyMFC_PROLOGUE(PymBuf_GetSize);
	
	PymBuffer *buf = getBuf(o);
	return buf->size();

	PyMFC_EPILOGUE(0);
}


long PymBuf_Find(void *o, long pos, long to, wchar_t c) {
	PyMFC_PROLOGUE(PymBuf_Find);
	return getBuf(o)->find(pos, to, c);
	PyMFC_EPILOGUE(0);
}

long PymBuf_Find_back(void *o, long pos, long to, wchar_t c) {
	PyMFC_PROLOGUE(PymBuf_Find_back);
	return getBuf(o)->find_back(pos, to, c);
	PyMFC_EPILOGUE(0);
}

long PymBuf_Find_i(void *o, long pos, long to, wchar_t c) {
	PyMFC_PROLOGUE(PymBuf_Find_i);
	return getBuf(o)->find_i(pos, to, c);
	PyMFC_EPILOGUE(0);
}

long PymBuf_Find_i_back(void *o, long pos, long to, wchar_t c) {
	PyMFC_PROLOGUE(PymBuf_Find_i_back);
	return getBuf(o)->find_i_back(pos, to, c);
	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_FindOneOf(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindOneOf);
	UINT idx;
	long ret = getBuf(o)->findOneOf(pos, to, c, t, idx);
	if (ret == -1) {
		PyMFC_RETNONE();
	}
	PyDTTuple tp(2);
	tp.setItem(0, ret);
	tp.setItem(1, idx);
	return tp.detach();

	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_FindOneOf_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindOneOf_back);
	UINT idx;
	long ret = getBuf(o)->findOneOf_back(pos, to, c, t, idx);
	if (ret == -1) {
		PyMFC_RETNONE();
	}
	PyDTTuple tp(2);
	tp.setItem(0, ret);
	tp.setItem(1, idx);
	return tp.detach();

	PyMFC_EPILOGUE(0);
}


long PymBuf_FindString(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindString);
	return getBuf(o)->findString(pos, to, c, t);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindString_i(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindString_i);
	return getBuf(o)->findString_i(pos, to, c, t);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindString_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindString_back);
	return getBuf(o)->findString_back(pos, to, c, t);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindString_i_back(void *o, long pos, long to, const wchar_t *c, const wchar_t *t) {
	PyMFC_PROLOGUE(PymBuf_FindString_i_back);
	return getBuf(o)->findString_i_back(pos, to, c, t);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindString_esc(void *o, long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc) {
	PyMFC_PROLOGUE(PymBuf_FindString_esc);
	return getBuf(o)->findString(pos, to, c, t, esc);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindString_i_esc(void *o, long pos, long to, const wchar_t *c, const wchar_t *t, wchar_t esc) {
	PyMFC_PROLOGUE(PymBuf_FindString_i_esc);
	return getBuf(o)->findString_i(pos, to, c, t, esc);
	PyMFC_EPILOGUE(0);
}

long PymBuf_FindStyle(void *o, long pos, long to, UINT idx) {
	PyMFC_PROLOGUE(PymBuf_FindStyle);
	return getBuf(o)->findStyle(pos, to, idx);
	PyMFC_EPILOGUE(0);
}
long PymBuf_FindStyle_back(void *o, long pos, long to, UINT idx) {
	PyMFC_PROLOGUE(PymBuf_FindStyle_back);
	return getBuf(o)->findStyle_back(pos, to, idx);
	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_FindStyleOneOf(void *o, long pos, long to, long *f, long *t) {
	PyMFC_PROLOGUE(PymBuf_FindStyleOneOf);

	UINT idx;
	long ret = getBuf(o)->findStyleOneOf(pos, to, f, t, idx);
	if (ret == -1) {
		PyMFC_RETNONE();
	}
	PyDTTuple tp(2);
	tp.setItem(0, ret);
	tp.setItem(1, idx);
	return tp.detach();
	
	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_FindStyleOneOf_back(void *o, long pos, long to, long *f, long *t) {
	PyMFC_PROLOGUE(PymBuf_FindStyleOneOf_back);

	UINT idx;
	long ret = getBuf(o)->findStyleOneOf_back(pos, to, f, t, idx);
	if (ret == -1) {
		PyMFC_RETNONE();
	}
	PyDTTuple tp(2);
	tp.setItem(0, ret);
	tp.setItem(1, idx);
	return tp.detach();
	
	PyMFC_EPILOGUE(0);
}

PyObject *PymBuf_GetStyleRange(void *o, long pos) {
	PyMFC_PROLOGUE(PymBuf_findStyleRange);

	long f, t;
	getBuf(o)->getStyleRange(pos, f, t);
	PyDTTuple tp(2);
	tp.setItem(0, f);
	tp.setItem(1, t);
	return tp.detach();
	
	PyMFC_EPILOGUE(0);
}

static
void buildScreenChars(PymBuffer &buf, long pos, long posto, 
		HDC hDC, const PymScreenConf &conf, int nStyles, const PymTextStyle *styles, 
		PymScreenChars &ret) {

	ASSERT(pos <= posto);
	ASSERT(posto <= buf.end());
	
	enum {UCS_HANKANA_BEGIN=0xff61, UCS_HANKANA_END=0xff9f};

	CDC *cdc = CDC::FromHandle(hDC);

	ret.resize(posto-pos);

	const PymStyleFont *curfont = &styles[0].latinFont;
	if (!curfont) {
		throw PyDTException(PyExc_ValueError, "Font object is not specified.");
	}
	
	HFONT orgFont = (HFONT)cdc->SelectObject((HFONT)curfont->hFont);
	
	UINT col = 0;
	BOOL italic = styles[0].latinFont.lf.lfItalic;
//todo: Tune up. Stop calling GetTextExtentPoint32W for each character
	
	for (long p = pos; p != posto; p++) {
		PymScreenChar &c = ret[p-pos];
		c.c = buf.get(p);
		c.style = buf.getStyleIdx(p);
		if (c.style >= nStyles) {
			c.style = 0;
		}
		c.latin = c.c < 256; // todo: 

		const PymStyleFont *nextfont = c.latin ? 
			&styles[c.style].latinFont : &styles[c.style].noLatinFont;
		
		if (curfont->hFont != nextfont->hFont) {
			curfont = nextfont;
			if (!curfont) {
				throw PyDTException(PyExc_ValueError, "Font object is not specified");
			}
			cdc->SelectObject((HFONT)curfont->hFont);

			if (italic) {
				// make gap at end of italic string for overhang.
				if (p-pos) {
					PymScreenChar &prev = ret[p-pos-1];
					prev.width += (short)nextfont->tm.tmAscent/10+1;
					//todo: How can I get correct gap size?
				}
			}
			italic = curfont->lf.lfItalic;
		}
		if (c.c == '\t') {
			int len = conf.tab - col % conf.tab;
			c.col = len;
		}
		else if (c.c < 0x100 || (UCS_HANKANA_BEGIN <= c.c && c.c <= UCS_HANKANA_END)) {
// todo:http://www.unicode.org/unicode/reports/tr11/ ?????
			c.col = 1;
		}
		else {
			c.col = 2;
		}

		SIZE size;
		if (c.c == '\n') {
			size.cx = curfont->spcWidth;
			size.cx = 6;
			size.cy = curfont->tm.tmHeight + curfont->tm.tmExternalLeading;
		}
		else if (c.c == '\t') {
			size.cx = curfont->spcWidth * c.col;
			size.cy = curfont->tm.tmHeight + curfont->tm.tmExternalLeading;
		}
		else {
			BOOL ret = GetTextExtentPoint32W(cdc->m_hDC, &c.c, 1, &size);
			ASSERT(ret);
		}

		c.width = (short)size.cx;
		if (c.width < 0) {
			c.width = 1;
		}
		c.height= (short)size.cy;
		if (c.height < 0) {
			c.height = 1;
		}
		c.selected = FALSE;

		col += c.col;
	}


	cdc->SelectObject(orgFont);
}



class RowSplitter {
public:
	void getLines(PyDTObject &bufobj, PymBuffer &buf, const PymScreenConf &conf, 
		int nStyle, PymTextStyle *styles, PymScreenChars &chars,
		int maxwidth,
		long pos, PyDTObject &rowtype, PyDTList &ret) {

		long lineno = buf.getLineNo(pos);
		size_t linetop=0, lineend;
		int indent_width = 0;
		int indent_col = 0;
		const wchar_t *nowrapchars_top = conf.nowrapchars_top;
		const wchar_t *nowrapchars_end= conf.nowrapchars_end;
		const wchar_t *nowrapheaders = conf.nowrapheaders;
		const wchar_t *itemize = conf.itemize;

		bool first_row = true;
		do {
			if (!conf.wrap) {
				// No wrap
				splitCol(linetop, chars, LONG_MAX, lineend);
			}
			else if (first_row && chars.size() && (wcschr(nowrapheaders, chars[0].c) != NULL)) {
				// No wrap
				splitCol(linetop, chars, LONG_MAX, lineend);
			}
			else if (conf.wrap && (conf.maxcol==0)){
				// Wrap by screen width.
				splitWidth(linetop, chars, maxwidth - indent_width, lineend);
			}
			else {
				// fixed column
				splitCol(linetop, chars, conf.maxcol - indent_col, lineend);
			}

			if (conf.wrap && conf.wordwrap) {
				adjustWrapPos(linetop, chars, lineend, nowrapchars_top, nowrapchars_end, conf.indentwrap && first_row, conf.forcewrap, itemize);
			}
			
			// todo: move to win32
			PymScreenChars::iterator iter;

			// minimum height	
			int height = styles[0].latinFont.tm.tmHeight + 
					styles[0].latinFont.tm.tmExternalLeading;
			// minimum ascent
			int ascent = styles[0].latinFont.tm.tmAscent;

			for (iter=chars.begin()+linetop; iter != chars.begin()+lineend; iter++) {
				// get max height
				height = max(height, iter->height);

				// get max ascent
				PymTextStyle &cstyle = styles[iter->style];
				TEXTMETRIC &tm = iter->latin ? cstyle.latinFont.tm : cstyle.noLatinFont.tm;
				
				ascent = max(ascent, tm.tmAscent);
			}
			height += conf.linegap;			
			

			PyDTObject row(rowtype.call("O", bufobj.get()));
			PymScreenRow *p_row = (PymScreenRow *)PyMFCPtr::asPtr(row.callMethod("getBuffer", "").get());

			p_row->top = pos+linetop;
			p_row->end = pos+lineend;
			p_row->lineNo = lineno;
			p_row->height = height;
			p_row->ascent = ascent;
			p_row->indent = indent_width;
			p_row->indentCol = indent_col;

			int len = lineend - linetop;
			p_row->chars = (PymScreenChar*)malloc(
					sizeof(PymScreenChar) * (len+1)); // never 0
			if (!p_row->chars) {
				throw std::bad_alloc();
			}
			if (len) {
				memcpy(p_row->chars, &(chars[linetop]), 
					sizeof(PymScreenChar) * len);
			}
			ret.append(row);

			if (conf.indentwrap && first_row) {
				for (iter=chars.begin()+linetop; iter != chars.begin()+lineend; iter++) {
					wchar_t c = iter->c;
					if (c == ' ' || c == '\t' || wcschr(itemize, c)) {
						indent_width += iter->width;
						indent_col += iter->col;
					}
					else {
						break;
					}
				}
			}
			
			first_row = false;
			linetop = lineend;
		} while (linetop < chars.size());

//		ASSERT(ret.size());
	}

	void splitCol(size_t pos, PymScreenChars &chars, size_t maxcol, size_t &lineend) {
		size_t curcol = 0;
		for (;pos < chars.size(); pos++) {
			PymScreenChar &c = chars[pos];
			if (((curcol + c.col) > maxcol) && (curcol > 0)) {
				lineend = pos;
				return;
			}
			curcol += c.col;
		}
		lineend = pos;
	}

	void splitWidth(size_t pos, PymScreenChars &chars, size_t maxwidth, size_t &lineend) {
		
		maxwidth -= 3; // margin at right border. todo: screenconf
		
		size_t width = 0;
		for (;pos < chars.size(); pos++) {
			PymScreenChar &c = chars[pos];
			if (((width + c.width) > maxwidth) && (width > 0)) {
				lineend = pos;
				return;
			}
			width += c.width;
		}
		lineend = pos;
	}

	void adjustWrapPos(size_t top, PymScreenChars &chars, size_t &lineend, 
		    const wchar_t *nowrapchars_top, const wchar_t *nowrapchars_end, bool indent_firstrow, int forcewrap, const wchar_t *itemize) {

		if (lineend == chars.size()) {
			// end of line, not wrap.
			return;
		}
		
		size_t endpos;
		if (forcewrap) {
			endpos = lineend-1;
		}
		else {
			endpos = chars.size()-1;
		}
		size_t wrappos = top;
		bool notws = false;
		for (size_t pos = top; pos < endpos; pos++) {
			if (wrappos != top && pos >= lineend) {
				break;
			}

			PymScreenChar &c = chars[pos];
			PymScreenChar &nexttop = chars[pos+1];
			
			notws = notws || c.c >= 256 || !isspace(c.c) || wcschr(itemize, c.c);

			if (c.c < 0x7f && !isspace(c.c)) {
				continue;
//				if (nexttop.c < 0x7f && !isspace(nexttop.c)) {
//					continue;
//				}
			}

			if (nexttop.c != '\n') {
				if (wcschr(nowrapchars_top, nexttop.c) != NULL) {
					continue;
				}

				if (wcschr(nowrapchars_end, c.c) != NULL) {
					continue;
				}
			}

			if (!indent_firstrow || notws) {
				// if indent-wrap was specified, the first row of line 
				// should not wrap untill non-space chars were found.
				wrappos = pos+1;
			}
			if (wrappos >= lineend) {
				break;
			}
		}

		if (wrappos != top) {
			// wrap position found.
			lineend = wrappos;
			return;
		}
		else if (!forcewrap){
			lineend = chars.size();
		}
	}
};



PyObject *PymBuf_SplitRow(long pos, long posto, PyObject *rowType, long maxwidth, 
	HDC device, PyObject *buf, PymScreenConf *conf, int nStyles, PymTextStyle *styles) {
	
	PyMFC_PROLOGUE(PymBuf_SplitRow)

	timeBeginPeriod(1);
	DWORD ttt = GetTickCount();

	PyDTObject bufobj(buf, false);
	PymBuffer *b = (PymBuffer*)PyMFCPtr::asPtr(bufobj.callMethod("getBuffer", "").get());


	PymScreenChars chars;
	buildScreenChars(*b, pos, posto, device, *(PymScreenConf*)conf, 
		nStyles, (PymTextStyle *)styles, chars);

	PyDTList ret(0);
	RowSplitter rs;
	rs.getLines(bufobj, *b, *(PymScreenConf*)conf, nStyles, styles, 
		chars, maxwidth, pos, PyDTObject(rowType, false), ret);


//	printf("%d-%d\n", GetTickCount()-ttt, ret.getSize());
	return ret.detach();

	PyMFC_EPILOGUE(NULL);
}



class Win32ScreenRowPaint {
//private:
public:
//	long m_size;
//	int m_width, m_height;
//	BOOL m_lastRow;

//	Win32ScreenRowPaint(PymScreenChar *chars, long size, int width, int height, BOOL lastrow)
//		:m_chars(chars), m_size(size), m_width(width), m_height(height), m_lastRow(lastrow){}


	void draw(CDC &dc, int width, int rowHeight, int indent, int ascent, int xorg, int yorg, 
		PymScreenChar *chars, long size, PymTextStyle *styles, BOOL lastrow,
		bool showTab, bool showLf, bool showFullSpc) {

#define KAA_FULL_SPACE 0x3000

//		ASSERT(styles.size());
		
		dc.SetTextAlign(TA_UPDATECP);

		// fill row indent rect
		if (xorg + indent > 0) {
			CRect rcFill(0, yorg, indent-xorg, yorg+rowHeight);
			dc.FillSolidRect(&rcFill, styles[0].color.text.back);
		}

		xorg += indent;
		// skip off-screen chars
		PymScreenChar *c;
		for (c = chars; c < chars + size; c++) {
			if (xorg + c->width >= 0) {
				break;
			}
			xorg += c->width;
		}
		dc.MoveTo(xorg, yorg);

		UINT styleIdx = -1;
		PymTextStyle *style=NULL;
		BOOL selected = FALSE;
		BOOL latin = true;
		PymScreenChar *styleTop = c;

		for (; c != chars + size; c++) {
			if (c->c == '\t') {
				if (c != styleTop) {
					CPoint loc(dc.GetCurrentPosition().x, yorg);
					drawString(dc, loc, rowHeight, ascent, styleTop, c, *style);
				}
				CPoint loc(dc.GetCurrentPosition().x, 0);
				drawTab(dc, loc, rowHeight, ascent, c, styles[c->style], showTab);
				styleTop = c+1;
				continue;
			}
			if (c->c == KAA_FULL_SPACE) {
				if (c!= styleTop) {
					CPoint loc(dc.GetCurrentPosition().x, yorg);
					drawString(dc, loc, rowHeight, ascent, styleTop, c, *style);
				}
				CPoint loc(dc.GetCurrentPosition().x, 0);
				drawFullSpace(dc, loc, rowHeight, ascent, c, styles[c->style], showFullSpc);
				styleTop = c+1;
				continue;
			}
			if (styleIdx != c->style 
				|| selected != c->selected
				|| latin != c->latin
				|| c->c == '\n') {

				if (c != styleTop) {
					CPoint loc(dc.GetCurrentPosition().x, yorg);
					drawString(dc, loc, rowHeight, ascent, styleTop, c, *style);
					styleTop = c;
				}
				selected = c->selected;
				styleIdx = c->style;
				style = &styles[styleIdx];
				latin = c->latin;
			}
			if (c->c == '\n') {
				break;
			}
		}

		if (!style) {
			if (size) {
				style = &styles[chars[size-1].style];
			}
			else {
				style = &styles[0];
			}
		}

		if (styleTop != chars + size) {
			CPoint loc(dc.GetCurrentPosition().x, yorg);
			drawString(dc, loc, rowHeight, ascent, styleTop, chars+size, *style);
		}

		CPoint pos(dc.GetCurrentPosition());
		CRect rcFill(pos.x, yorg, width, yorg+rowHeight);

		if (rcFill.left < rcFill.right) {
			if (!lastrow) {
				dc.FillSolidRect(&rcFill, style->color.text.back);
			}
			else {
				dc.FillSolidRect(&rcFill, styles[0].color.text.back);
			}
		}

		if (c < chars+size) {
			wchar_t lc = c->c;
			if (lc == '\n') {
				CPoint loc(dc.GetCurrentPosition().x, yorg);
				if (showLf) {
					drawLf(dc, loc, rowHeight, ascent, c, *style);
				}
			}
		}
	}

	void drawString(CDC &dc, const CPoint &loc, int rowHeight, int ascent, PymScreenChar *pos, PymScreenChar *posTo, PymTextStyle &style) {
		if (!pos->selected) {
			dc.SetTextColor(style.color.text.fore);
			dc.SetBkColor(style.color.text.back);
		}
		else {
			dc.SetTextColor(style.color.text_sel.fore);
			dc.SetBkColor(style.color.text_sel.back);
		}
		if (pos->latin) {
			dc.SelectObject((HFONT)style.latinFont.hFont);
		}
		else {
			dc.SelectObject((HFONT)style.noLatinFont.hFont);
		}

		std::vector<wchar_t> s;
		int width = 0;
		for (PymScreenChar *ctop=pos; ctop < posTo; ctop++) {
			if (ctop->c == '\n') {
				break;
			}
			s.push_back(ctop->c);
			width += ctop->width;
		}

		TEXTMETRIC *tm = pos->latin ? &style.latinFont.tm : &style.noLatinFont.tm;
//		printf("%d %d %d\n", tm->tmHeight, tm->tmDescent, tm->tmExternalLeading);
		dc.MoveTo(loc.x, loc.y + ascent - tm->tmAscent - tm->tmExternalLeading);

//		dc.MoveTo(loc.x, loc.y + rowHeight - tm->tmHeight);
//	TextOutW(dc, 0, 0, &s[0], s.size());

		CRect rc(loc.x, loc.y, loc.x+width, loc.y + rowHeight);
		dc.SetBkMode(TRANSPARENT);
		ExtTextOutW(dc, 0, 0, ETO_OPAQUE, rc, &s[0], s.size(), NULL);
		dc.SetBkMode(OPAQUE);
	//	TextOutW(dc, 0, 0, &s[0], s.size());
		dc.MoveTo(loc.x+width, loc.y);
	}


	void drawLf(CDC &dc, const CPoint &loc, int rowHeight, int ascent, PymScreenChar *pos, PymTextStyle &style) {

		PymStyleFont *kf = pos->latin ? &style.latinFont : &style.noLatinFont; 
		TEXTMETRIC &tm = kf->tm;

		UINT h = int(tm.tmAscent * 45.0 / 100 + 1);
		UINT w = 6;

		CPen pen;

		CRect bk(loc.x, loc.y, loc.x + w, loc.y + rowHeight);

		if (!pos->selected) {
			pen.CreatePen(PS_SOLID, 1, style.color.lf.fore);
			dc.FillSolidRect(bk, style.color.lf.back);
		}
		else {
			pen.CreatePen(PS_SOLID, 1, style.color.lf_sel.fore);
			dc.FillSolidRect(bk, style.color.lf_sel.back);
		}

		int top = loc.y + ascent - tm.tmAscent;
		CRect rc(loc.x, top+h, loc.x + w, loc.y + ascent);
//		CRect rc(loc.x, loc.y + rowHeight - tm.tmDescent - h - 1, loc.x + w, loc.y + rowHeight - tm.tmDescent - 1);


//		dc.MoveTo(loc.x, loc.y + ascent - tm->tmAscent - tm->tmExternalLeading);

		dc.SelectObject(&pen);

		dc.MoveTo(rc.left+3, rc.top);
		dc.LineTo(rc.left+3, rc.bottom);

		dc.MoveTo(rc.left+1, rc.bottom-2);
		dc.LineTo(rc.left+3, rc.bottom);

		dc.MoveTo(rc.left+3, rc.bottom);
		dc.LineTo(rc.left+6, rc.bottom-3);

		dc.MoveTo(rc.right, loc.y);
	}

	void drawTab(CDC &dc, const CPoint &loc, int rowHeight, int ascent, PymScreenChar *pos, PymTextStyle &style, bool show) {
		
		PymStyleFont *kf = pos->latin ? &style.latinFont : &style.noLatinFont; 
		TEXTMETRIC &tm = kf->tm;

		UINT spcWidth = kf->spcWidth;

		UINT h = spcWidth;
		if (h % 2 == 0) {
			h--;
		}


		CPen pen;
		CRect bk(loc.x, loc.y, loc.x + pos->width, loc.y + rowHeight);
		if (!pos->selected) {
			pen.CreatePen(PS_SOLID, 1, style.color.tab.fore);
			dc.FillSolidRect(bk, style.color.tab.back);
		}
		else {
			pen.CreatePen(PS_SOLID, 1, style.color.tab_sel.fore);
			dc.FillSolidRect(bk, style.color.tab_sel.back);
		}

		dc.SelectObject(&pen);

		int top = loc.y + ascent - tm.tmAscent;
		CRect rc(loc.x, 
				loc.y + ascent - 1 - spcWidth, 
				loc.x + spcWidth, 
				loc.y + ascent - 1);

//		CRect rc(loc.x, 
//				loc.y + rowHeight - tm.tmDescent - spcWidth - 1, 
//				loc.x + spcWidth, 
//				loc.y + rowHeight - tm.tmDescent - 1);

		if (show) {
			dc.MoveTo(rc.left+1, rc.top);
			dc.LineTo(rc.left+1+h/2, rc.top + h / 2);
			dc.LineTo(rc.left, rc.top + h);
		}
		dc.MoveTo(loc.x + pos->width, loc.y);
	}

	void drawFullSpace(CDC &dc, const CPoint &loc, int rowHeight, int ascent, PymScreenChar *pos, PymTextStyle &style, bool show) {

		PymStyleFont *kf = pos->latin ? &style.latinFont : &style.noLatinFont; 
		TEXTMETRIC &tm = kf->tm;

		UINT spcWidth = pos->width;
		UINT margin = (int)(spcWidth * 2.5 / 10);

		CPen pen;
		CRect bk(loc.x, loc.y, loc.x + pos->width, loc.y + rowHeight);

		if (!pos->selected) {
			pen.CreatePen(PS_SOLID, 1, style.color.fullspc.fore);
			dc.FillSolidRect(bk, style.color.fullspc.back);
		}
		else {
			pen.CreatePen(PS_SOLID, 1, style.color.fullspc_sel.fore);
			dc.FillSolidRect(bk, style.color.fullspc_sel.back);
		}

		dc.SelectObject(&pen);

		CRect rc(loc.x + margin,
				loc.y + ascent - (spcWidth - margin*2),
				loc.x + spcWidth-margin, 
				loc.y + ascent);

//		CRect rc(loc.x + margin,
//				loc.y + rowHeight - spcWidth + margin,
//				loc.x + spcWidth-margin, 
//				loc.y + rowHeight - margin);

		if (show) {
			dc.MoveTo(rc.left, rc.top);
			dc.LineTo(rc.right-1, rc.top);
			dc.LineTo(rc.right-1, rc.bottom);
			dc.LineTo(rc.left, rc.bottom);
			dc.LineTo(rc.left, rc.top);
		}
		dc.MoveTo(loc.x + spcWidth, loc.y);
	}

};



int PymEditor_PaintRow(PyObject *rowobj, PyObject *dc, int xorg, int yorg, int width, 
					   PymScreenConf *conf, int nStyles, PymTextStyle *styles) {

//int Win32PaintScreenRow(PyObject *screen, PyObject *rowobj, PyObject *device, int xorg, int yorg, int width) {

	PyMFC_PROLOGUE(Win32PaintScreenRow)


	// strange. This makes WM_SIZE run faster on my w2k box.
	// May be I can tune up RecalcLayout() or somewhere else...
	GdiSetBatchLimit(1);

	
	PyDTObject row(rowobj, false);
	HDC hdc = (HDC)PyMFCHandle::asHandle(PyDTObject(dc, false).callMethod("getHandle", "").get());

	int rowHeight = row.getAttr("height").getInt();
	int indent = row.getAttr("indent").getInt();
	int ascent = row.getAttr("ascent").getInt() + conf->linegap;

	
	PymScreenRow *c_row= (PymScreenRow*)PyMFCPtr::asPtr(row.callMethod("getBuffer", "").get());
	long size = c_row->end - c_row->top;

	BOOL lastrow = row.callMethod("isLastRow", "").getInt();
	//	CDC &dc, int width, int rowHeight, int xorg, int yorg, PymScreenChar *chars, long size, PymTextStyle *styles, BOOL lastrow

	
	bool showTab = conf->showtab != 0;
	bool showLf = conf->showlf != 0;
	bool showFullSpc = conf->showfullspc != 0;

	CDC dc;
	dc.Attach((HDC)hdc);
	try {
		Win32ScreenRowPaint p;
		p.draw(dc, width, rowHeight, indent, ascent, xorg, yorg, c_row->chars, 
			size, styles, lastrow, showTab, showLf, showFullSpc);
	}
	catch(...) {
		dc.Detach();
		throw;
	}

	dc.Detach();
	return TRUE;

	PyMFC_EPILOGUE(0);
}
