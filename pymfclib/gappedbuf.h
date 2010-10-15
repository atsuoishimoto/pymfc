// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef GAPPEDBUFFER_H
#define GAPPEDBUFFER_H

#pragma inline_depth(32)


#include <vector>
#include <new>

template <class T>
class GappedBuffer {
public:
	GappedBuffer() {
		m_buf = NULL;
		m_bufSize = 0;
		m_elemCount = 0;
		m_gapPos = 0;
		m_gapSize = 0;
	}

	~GappedBuffer() {
		if (m_buf)
			free(m_buf);
	}

	void ins(long pos, const T *from, const T *to) {
		ASSERT(pos <= end());

		size_t len = to - from;
		if (!len)
			return;

		insBuffer(pos, len);
		memcpy(&m_buf[pos], from, len * sizeof(T));
	}

	void insValue(long pos, const T &n) {
		ASSERT(pos <= end());
		insBuffer(pos, 1);
		m_buf[pos] = n;
	}

	void expandBuf(long pos, long size) {
		ASSERT(pos <= end());
		insBuffer(pos, size);
	}


	void del(long from, long to) {
		delBuffer(from, to);
	}
	
	void set(long from, long to, const T& n) {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		
		long i;
		long stop = min(to, m_gapPos);
		for (i = from; i < stop; i++) {
			m_buf[i] = n;
		}
		
		if (i == to) {
			return;
		}
		long start = max(from, m_gapPos);
		for (i = start; i < to; i++) {
			m_buf[i] = n;
		}
	}

	T &get(long pos) {
		ASSERT(pos < end());
		return *(m_buf + pos + (pos < m_gapPos ? 0:m_gapSize));
	}

	const T &get(long pos) const {
		ASSERT(pos < end());
		return *(m_buf + pos + (pos < m_gapPos ? 0:m_gapSize));
	}

	T &last() const {
		ASSERT(size());
		return get(size()-1);
	}

	void get(long from, long to, T *retFrom) const {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		
		if (m_gapPos < from) {
			memcpy(retFrom, &m_buf[from+m_gapSize], (to-from)*sizeof(T));
		}
		else if (to <= m_gapPos) {
			memcpy(retFrom, &m_buf[from], (to-from)*sizeof(T));
		}
		else {
			long former = m_gapPos - from;
			memcpy(retFrom, &m_buf[from], former*sizeof(T));
			memcpy(&retFrom[former], &m_buf[m_gapPos+m_gapSize], (to-from-former)*sizeof(T));
		}
	}

	void get(long from, long to, std::vector<T> &ret) const {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		
		ret.clear();
		ret.resize(to - from);

		// todo:speedup
		T *pos = &(*ret.begin());
		get(from, to, pos);	
	}

	long begin() const {
		return 0;
	}

	long end() const {
		return m_elemCount;
	}

	long size() const {
		return m_elemCount;
	}

	long find(long from, long to, const T &c) {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		
		long i;
		long stop = min(to, m_gapPos);
		for (i = from; i < stop; i++) {
			if (c == m_buf[i]) {
				return i;
			}
		}
		
		if (i == to) {
			return -1;
		}
		long start = max(from, m_gapPos);
		for (i = start; i < to; i++) {
			if (c == m_buf[m_gapSize + i]) {
				return i;
			}
		}
		return -1;
	}

	long find_back(long from, long to, const T &c) {
		if (!to) {
			return -1;
		}

		ASSERT(from < to);
		ASSERT(to <= m_elemCount);

		long i;

		long end = max(from, m_gapPos);
		for (i = to-1; i >= end; i--) {
			if (c == m_buf[m_gapSize + i]) {
				return i;
			}
		}
		
		long start = min(to, m_gapPos)-1;
		for (i = start; i >= from; i--) {
			if (c == m_buf[i]) {
				return i;
			}
		}
		return -1;
	}

	long findOr(long from, long to, const T &c1, const T &c2) {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		
		long i;
		long stop = min(to, m_gapPos);
		for (i = from; i < stop; i++) {
			if (c1 == m_buf[i] || c2 == m_buf[i]) {
				return i;
			}
		}
		
		if (i == to) {
			return -1;
		}
		long start = max(from, m_gapPos);
		for (i = start; i < to; i++) {
			if (c1 == m_buf[m_gapSize + i] || c2 == m_buf[m_gapSize + i]) {
				return i;
			}
		}
		return -1;
	}

	long findOr_back(long from, long to, const T &c1, const T &c2) {
		if (!to) {
			return -1;
		}

		ASSERT(from < to);
		ASSERT(to <= m_elemCount);

		long i;

		long end = max(from, m_gapPos);
		for (i = to-1; i >= end; i--) {
			if (c1 == m_buf[m_gapSize + i] || c2 == m_buf[m_gapSize + i]) {
				return i;
			}
		}
		
		long start = min(to, m_gapPos)-1;
		for (i = start; i >= from; i--) {
			if (c1 == m_buf[i] || c2 == m_buf[i]) {
				return i;
			}
		}
		return -1;
	}

	long findOneOf(long from, long to, const T *c, const T *t, UINT &ret) {
		if (!to) {
			return -1;
		}

		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		ASSERT(c);
		ASSERT(t-c);
		
		long num = t-c;
		long i;
		long stop = min(to, m_gapPos);
		for (i = from; i < stop; i++) {
			T &v = m_buf[i];
			for (long j=0; j < num; j++) {
				if (v == c[j]) {
					ret = j;
					return i;
				}
			}
		}
		
		if (i == to) {
			return -1;
		}
		long start = max(from, m_gapPos);
		for (i = start; i < to; i++) {
			T &v = m_buf[m_gapSize + i];
			for (long j=0; j < num; j++) {
				if (v == c[j]) {
					ret = j;
					return i;
				}
			}
		}
		return -1;
	}

	long findOneOf_back(long from, long to, const T *c, const T *t, UINT &ret) {
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);
		ASSERT(c);
		ASSERT(t-c);
		
		if (!to) {
			return -1;
		}
		
		long num = t-c;
		long i;

		long end = max(from, m_gapPos);
		for (i = to-1; i >= end; i--) {
			T &v = m_buf[i+m_gapSize];
			for (long j=0; j < num; j++) {
				if (v == c[j]) {
					ret = j;
					return i;
				}
			}
		}
		
		long start = min(to, m_gapPos)-1;
		for (i = start; i >= from; i--) {
			T &v = m_buf[i];
			for (long j=0; j < num; j++) {
				if (v == c[j]) {
					ret = j;
					return i;
				}
			}
		}
		return -1;
	}
	
	bool isMatch(long from, const T *c, const T *t) {
		// todo: speedup
		ASSERT(from <= m_elemCount);
		ASSERT(c);
		ASSERT(t-c);

		if (from + (t-c) > size()) {
			return false;
		}
		
		for (long i = 0; i < t-c; i++) {
			if (get(from+i) != c[i]) {
				return false;
			}
		}
		return true;
	}

protected:

	void setBufSize(long size) {
		if (size  <= m_bufSize) 
			return;

		T *n = (T *)realloc(m_buf, size * sizeof(T));
		if (!n) {
			throw std::bad_alloc();
		}
		m_buf = n;
		m_bufSize = size;
	}

	void shrinkGap() {
		long GAPSIZE = 256*16;
		if (m_elemCount + GAPSIZE > m_bufSize) {
			return;
		}

		memmove(&m_buf[m_gapPos+GAPSIZE], 
				&m_buf[m_gapPos+m_gapSize], 
				(m_elemCount - m_gapPos) * sizeof(T));

		m_gapSize = GAPSIZE;
		long size = m_elemCount + GAPSIZE;

		T * n = (T *)realloc(m_buf, size * sizeof(T));
		if (!n) {
			throw std::bad_alloc();
		}
		m_buf = n;
		m_bufSize = size;
	}

	void moveGap(long pos) {
		ASSERT(pos <= end());
		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);

		if (pos == m_gapPos)
			return;

		if (m_gapSize)
		{
			if (pos < m_gapPos)
				memmove(&m_buf[pos+m_gapSize], &m_buf[pos], (m_gapPos - pos) * sizeof(T));
			else
				memmove(&m_buf[m_gapPos], &m_buf[m_gapPos + m_gapSize], (pos - m_gapPos) * sizeof(T));
		}
		m_gapPos = pos;
	}

	void expandGap(long size)
	{
		ASSERT(size);
		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);

		if (size <= m_gapSize)
			return;

		setBufSize(m_elemCount + size);
		if (m_gapPos < m_elemCount) {
			memmove(
				&m_buf[m_gapPos + size], 
				&m_buf[m_gapPos + m_gapSize], 
				(m_elemCount - m_gapPos) * sizeof(T));
		}

		m_gapSize = size;

#ifdef _DEBUG
		memset(&m_buf[m_gapPos], '$', m_gapSize * sizeof(T));
#endif

		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);
	}

	virtual void insBuffer(long pos, long len) {
		ASSERT(len);
		ASSERT(pos <= end());

		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);

		moveGap(pos);

		if (m_gapSize <= len)
			expandGap(max(512, len*2));	//todo:optimize

		ASSERT(m_gapPos <= end());

#ifdef _DEBUG
		memset(&m_buf[m_gapPos], '#', m_gapSize * sizeof(T));
#endif
		m_elemCount += len;
		m_gapPos += len;
		m_gapSize -= len;

		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);
	}

	virtual void delBuffer(long from, long to) {

		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);
		ASSERT(from <= to);
		ASSERT(to <= m_elemCount);

		long n = to - from;
		if (!n)
			return;

		moveGap(from);
		m_gapSize += n;
		m_elemCount -= n;

		if ((m_gapSize > m_elemCount*3) && (m_gapSize > 256*16))
//		if (m_gapSize > 256*4)
//		if (m_gapSize > 256*16)
//		if (m_gapSize > 256*64)
//		if (m_gapSize > 256*256)
		{
			shrinkGap();
		}
		
		
		ASSERT(m_gapPos <= end());
		ASSERT(m_elemCount + m_gapSize <= m_bufSize);
	}

protected:
	T *m_buf;
	
	long m_bufSize;
	long m_elemCount;
	long m_gapPos;
	long m_gapSize;

};





#endif
