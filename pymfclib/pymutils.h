// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMUTILS_H
#define PYMUTILS_H

#include <vector>

class UnicodeStr
{
public:
	UnicodeStr(const char *str, int len)
		:m_wstr(NULL), m_len(NULL)
	{
		if (!str)
			return;

		UINT l = MultiByteToWideChar(CP_ACP, 0, str, len, NULL, 0);
		m_wstr = new WCHAR[l+1];
		m_len = MultiByteToWideChar(CP_ACP, 0, str, len, m_wstr, l+1);
		m_wstr[m_len] = 0;
	}
	UnicodeStr(const char *str)
		:m_wstr(NULL), m_len(NULL)
	{
		if (!str)
			return;

		UINT l = MultiByteToWideChar(CP_ACP, 0, str, -1, NULL, 0);
		m_wstr = new WCHAR[l+1];
		m_len = MultiByteToWideChar(CP_ACP, 0, str, -1, m_wstr, l+1);
		m_wstr[m_len] = 0;
	}
	~UnicodeStr()
	{
		if (m_wstr) delete []m_wstr;
	}
	const WCHAR *get() {
		return m_wstr;
	}
	int size() {
		return m_len;
	}

	WCHAR *m_wstr;
	UINT m_len;
};


template <class T>
class HGlobalPtr {
public:
	HGlobalPtr(HGLOBAL hGlobal, bool release):m_hGlobal(hGlobal), m_release(release), m_ptr(0){
		assert(hGlobal);
	}
	~HGlobalPtr() {
		if (m_ptr) {
			GlobalUnlock(m_hGlobal);
		}
		if (m_release) {
			GlobalFree(m_hGlobal);
		}
	}
	T *operator ->() {
		return get();
	}

	T *get() {
		if (!m_ptr) {
			m_ptr = (T *)GlobalLock(m_hGlobal);
		}
		return m_ptr;
	}

	size_t getSize() {
		return GlobalSize(m_hGlobal);
	}

	HGLOBAL m_hGlobal;
	bool m_release;
	T *m_ptr;
};

template <class T>
class PyMFCAutoVector: public std::vector<T> {
public:
	~PyMFCAutoVector() {
		for (iterator iter=begin(); iter != end(); ++iter) {
			delete *iter;
		}
	}
};


class PyMFCPtr:public PyDTObject {
public:
	PyMFCPtr(void *p);
	static void* asPtr(PyObject *);
	static bool isPtr(PyObject *);
};

class PyMFCHandle:public PyDTObject {
public:
	PyMFCHandle(void *p);
	static void* asHandle(PyObject *);
	static bool isHandle(PyObject *);
};


#endif