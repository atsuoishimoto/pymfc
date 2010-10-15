/* 
pydt - Simple wrappers for Python Data Types 
Copyright (c) 2004, Atsuo Ishimoto

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software
"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to
whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/



#ifndef PYDT_H
#define PYDT_H

// PyDTXXXX: Simple wrappers for Python Data Types
#include <string>
#include <vector>

#ifdef HAVE_USABLE_WCHAR_T

#endif

#ifndef ASSERT
#define ASSERT assert
#endif

/* generic  */
class PyDTException {
public:
	PyDTException(PyObject *excp, const char *s=""):m_err(s),m_exc(excp) {
	}
	virtual ~PyDTException() {}

	virtual void setError() {
		PyErr_SetString(m_exc, m_err.c_str());
	}
	std::string m_err;
	PyObject *m_exc;
};

/* raises PyExc_TypeError */
class PyDTExc_InvalidType:public PyDTException {
public:
	PyDTExc_InvalidType(const char *expected=""):PyDTException(PyExc_TypeError, expected) {
	}

	void setError() {
		if (m_err.size()) {
			std::string s = std::string("PyDT: invalid type object - " + m_err + "  expected");
			PyErr_SetString(m_exc, s.c_str());
		}
		else {
			PyErr_SetString(m_exc, "PyDT: invalid type object.");
		}
	}
};

/* raises PyExc_ValueError */
class PyDTExc_InvalidValue:public PyDTException {
public:
	PyDTExc_InvalidValue(const char *s=""):PyDTException(PyExc_ValueError, s) {
	}
};

/* raises PyExc_RuntimeError */
class PyDTExc_RuntimeError:public PyDTException {
public:
	PyDTExc_RuntimeError(const char *s=""):PyDTException(PyExc_RuntimeError, s) {
	}
};


/* PyDTExc_PythonError doesn't overwrite current exception.
Used to preserve detected exception */

class PyDTExc_PythonError:public PyDTException {
public:
	PyDTExc_PythonError():PyDTException(NULL, "") {
	}
	void setError() {
	}
};

#ifdef WIN32

class PyDTExc_Win32Err:public PyDTException
{
public:
	PyDTExc_Win32Err(LPCSTR file=NULL, DWORD line=0, PyObject *exc=NULL)
			:PyDTException(exc, ""), m_filename(file), m_line(line)
	{
		DWORD err = GetLastError();		// Last error code has set to 0.
		SetText(err);
		SetLastError(err);				// Restore error code.
	}

	PyDTExc_Win32Err(DWORD err, LPCSTR file=NULL, DWORD line=0, PyObject *exc=NULL)
		:PyDTException(exc, ""), m_errcode(0), m_filename(file), m_line(line)
	{
		SetText(err);
	}
	
	PyDTExc_Win32Err(const PyDTExc_Win32Err &r)
		:PyDTException(r.m_exc, ""), m_errcode(0), m_filename(r.m_filename), m_line(r.m_line)
	{
		SetText(r.m_errcode);
	}

	virtual ~PyDTExc_Win32Err()
	{
	}

	PyDTExc_Win32Err &operator =(const PyDTExc_Win32Err &r)
	{
		m_filename = r.m_filename; m_line = m_line;
		SetText(r.m_errcode);
		return *this;
	}

	void setError() {
		if (!m_exc) {
			m_exc = PyExc_RuntimeError;
		}
		PyDTException::setError();
	}

	LPCSTR GetText() const {return m_err.c_str();}
	DWORD  GetErr() const {return m_errcode;}
	
private:
	void SetText(DWORD err) {
		m_errcode = err;

		TCHAR *buf;
		DWORD ret = FormatMessage(
			FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
			NULL, err, LANG_NEUTRAL,
			(LPTSTR)&buf,
			0,
			NULL);
		if (ret)
		{
//			for (int i = 0; buf[i]; i++)
//				if (buf[i] == '\n' || buf[i] == '\r' )
//					buf[i] = 0;
			
#ifndef UNICODE
			m_err = buf;
#else
			UINT l = WideCharToMultiByte(CP_ACP, 0, buf, ret+1, NULL, 0, NULL, NULL);
			char *t = new char[l+1];
			WideCharToMultiByte(CP_ACP, 0, buf, ret+1, t, l+1, NULL, NULL);
			m_err = t;
			delete []t;
#endif
			LocalFree(buf);
		}
		else
		{
			buf = NULL;
		}
	}

	DWORD m_errcode;
	LPCSTR m_filename;
	DWORD m_line;
};

#endif // WIN32

class PyDTString;

class PyDTObject {
public:	

	PyDTObject():m_obj(NULL), m_own(false) {}
	PyDTObject(PyObject *obj, bool own):m_obj(obj), m_own(own){
	}
	PyDTObject(const PyDTObject&r):m_obj(r.m_obj), m_own(false) {
		incRef(true);
	}

	PyDTObject &operator = (const PyDTObject &r) {
		free();
		m_obj = r.m_obj;
		incRef(true);
		check();
		return *this;
	}

	virtual ~PyDTObject(){
		free();
	}

	void incRef(bool setown=false) {
		if (m_obj)
			Py_INCREF(m_obj);
		if (setown) {
			m_own = true;
		}
	}
	
	void decRef(bool resetown=false) {
		if (resetown) {
			m_own = false;
		}
		if (m_obj)
			Py_DECREF(m_obj);
	}
	
	int getRefCount() const {
		checkNull();
		return m_obj->ob_refcnt;
	}
	bool isInt() const {
		return m_obj != NULL && PyInt_CheckExact(m_obj);
	}

	bool isLong() const {
		return m_obj != NULL && PyLong_CheckExact(m_obj);
	}

	bool isFloat() const {
		return m_obj != NULL && PyFloat_CheckExact(m_obj);
	}

	bool isBool() const {
		return m_obj != NULL && PyBool_Check(m_obj);
	}

	bool isString() const {
		return m_obj != NULL && PyString_CheckExact(m_obj);
	}
	
	bool isUnicode() const {
		return m_obj != NULL && PyUnicode_CheckExact(m_obj);
	}
	
	bool isTuple() const {
		return m_obj != NULL && PyTuple_CheckExact(m_obj);
	}

	bool isList() const {
		return m_obj != NULL && PyList_CheckExact(m_obj);
	}
	
	bool isDict() const {
#ifndef PyDict_CheckExact
#	define PyDict_CheckExact(op) ((op)->ob_type == &PyDict_Type)
#endif
		return m_obj != NULL && PyDict_CheckExact(m_obj);

	}
	
	
	PyObject *get() const {
		PyObject *ret = m_obj;
		return ret;
	}

	PyObject *detach() {
		PyObject *ret = m_obj;
		m_obj = NULL;
		m_own = false;
		return ret;
	}

	void set(PyObject *obj, bool own) {
		free();
		m_obj = obj;
		m_own = own;
		check();
	}

	void free() {
		PyObject *obj = m_obj;
		m_obj = NULL;
		if (m_own && obj) {
			m_own = false;
			Py_DECREF(obj);
		}
	}
	
	PyObject **getBuf() {
		free();
		return &m_obj;
	}

	bool isTrue() const {
		if (m_obj) {
			int ret = PyObject_IsTrue(m_obj);
			if (ret == 1) {
				return true;
			}
			else if (ret == -1) {
				throw PyDTExc_PythonError();
			}
		}
		return false;
	}

	bool isNone() const {
		return m_obj == Py_None;
	}
	
	bool isNull() const {
		return !m_obj;
	}

	bool isInstance(const PyTypeObject &type) const {
		checkNull();
		return PyObject_IsInstance(m_obj, (PyObject *)&type) == 1;
	}

	bool isInstance(const PyTypeObject *type) const {
		checkNull();
		return PyObject_IsInstance(m_obj, (PyObject *)type) == 1;
	}

	bool isInstance(const PyDTObject &type) const {
		checkNull();
		return PyObject_IsInstance(m_obj, type.get()) == 1;
	}

	bool isInstance(const PyObject *type) const {
		checkNull();
		return PyObject_IsInstance(m_obj, (PyObject *)type) == 1;
	}


	PyDTObject call(char *format, ...) const {
		va_list va;
		PyObject *args, *retval;

		checkNull();

		if (format && *format) {
			va_start(va, format);
			args = Py_VaBuildValue(format, va);
			va_end(va);
		}
		else
			args = PyTuple_New(0);

		if (args == NULL)
			throw PyDTExc_PythonError();

		if (!PyTuple_Check(args)) {
			PyObject *a;

			a = PyTuple_New(1);
			if (a == NULL) {
				Py_DECREF(args);
				throw PyDTExc_PythonError();	
			}
			if (PyTuple_SetItem(a, 0, args) < 0) {
				Py_DECREF(args);
				Py_DECREF(a);
				throw PyDTExc_PythonError();
			}
			args = a;
		}
		retval = PyObject_CallObject(m_obj, args);

		Py_DECREF(args);

		if (!retval) {
			throw PyDTExc_PythonError();
		}
		else {
			return PyDTObject(retval, true);
		}
	}

	PyDTObject callMethod(char *name, char *format, ...) const {
		va_list va;
		PyObject *args, *func = 0, *retval;
		va_start(va, format);

		checkNull();

		if (m_obj == NULL || name == NULL) {
			va_end(va);
			null_error();
			throw PyDTExc_PythonError();
		}

		func = PyObject_GetAttrString(m_obj, name);
		if (func == NULL) {
			va_end(va);
			throw PyDTException(PyExc_AttributeError, name);
		}

		if (!PyCallable_Check(func)) {
			va_end(va);
			throw PyDTException(PyExc_TypeError, "call of non-callable attribute");
		}

		if (format && *format)
			args = Py_VaBuildValue(format, va);
		else
			args = PyTuple_New(0);

		va_end(va);

		if (!args)
			return PyDTObject();

		if (!PyTuple_Check(args)) {
			PyObject *a;

			a = PyTuple_New(1);
			if (a == NULL) {
				Py_DECREF(args);
				throw PyDTExc_PythonError();
			}

			if (PyTuple_SetItem(a, 0, args) < 0) {
				Py_DECREF(args);
				Py_DECREF(a);
				throw PyDTExc_PythonError();
			}
			args = a;
		}

		retval = PyObject_CallObject(func, args);
		Py_DECREF(args);
		Py_DECREF(func);

		if (!retval) {
			throw PyDTExc_PythonError();
		}
		else {
			return PyDTObject(retval, true);
		}
	};

	void setAttr(const char *name, const PyDTObject &obj) {
		checkNull();
		if (-1 == PyObject_SetAttrString(m_obj, (char *)name, obj.get())) {
			throw PyDTExc_PythonError();
		}
	}

	void setAttr(const PyDTObject &name, const PyDTObject &obj) {
		checkNull();
		if (-1 == PyObject_SetAttr(m_obj, name.get(), obj.get())) {
			throw PyDTExc_PythonError();
		}
	}

	void setAttr(const char *name, long value) {
		checkNull();
		PyObject *v = PyInt_FromLong(value);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		if (-1 == PyObject_SetAttrString(m_obj, (char *)name, v)) {
			Py_DECREF(v);
			throw PyDTExc_PythonError();
		}
		Py_DECREF(v);
	}

	bool hasAttr(const char *name) const {
		checkNull();
		return PyObject_HasAttrString(m_obj, (char *)name) == 1;
	}

	bool getAttr(const char *name, PyDTObject &ret) const {
		checkNull();
		PyObject *o=PyObject_GetAttrString(m_obj, (char *)name);
		if (o) {
			ret.set(o, true);
			return true;
		}
		else {
			return false;
		}
	}

	bool getAttr(const PyDTObject &name, PyDTObject &ret) const {
		checkNull();
		PyObject *o=PyObject_GetAttr(m_obj, name.get());
		if (o) {
			ret.set(o, true);
			return true;
		}
		else {
			return false;
		}
	}

	PyDTObject getAttr(const char *name) const {
		checkNull();
		PyObject *o=PyObject_GetAttrString(m_obj, (char *)name);
		if (o) {
			return PyDTObject(o, true);
		}
		else {
			throw PyDTException(PyExc_AttributeError, name);
		}
	}

	PyDTObject getAttr(const PyDTObject &name) const {
		checkNull();
		PyObject *o=PyObject_GetAttr(m_obj, name.get());
		if (o) {
			return PyDTObject(o, true);
		}
		else {
			PyErr_SetObject(PyExc_AttributeError, name.get());
			throw PyDTExc_PythonError();
		}
	}

	long getInt(long ifNone=0) const {
		if (!m_obj || isNone()) {
			return ifNone;
		}
		else if (isInt()) {
			long ret = PyInt_AS_LONG(m_obj);
			if (PyErr_Occurred()) {
				throw PyDTExc_PythonError();
			}
			return ret;
		}
		else {
			long ret = PyInt_AsLong(toInt().get());
			if (PyErr_Occurred()) {
				throw PyDTExc_PythonError();
			}
			return ret;
		}
	}
	
	unsigned long getULong(unsigned long ifNone=0) const {
		if (!m_obj || isNone()) {
			return ifNone;
		}
		else if (isInt()) {
			unsigned long ret = PyInt_AS_LONG(m_obj);
			if (PyErr_Occurred()) {
				throw PyDTExc_PythonError();
			}
			return ret;
		}
		else if (isLong()) {
			unsigned long ret =  PyLong_AsUnsignedLongMask(m_obj);
			if (PyErr_Occurred()) {
				throw PyDTExc_PythonError();
			}
			return ret;
		}
		else {
			unsigned long ret = PyLong_AsUnsignedLongMask(toInt().get());
			if (PyErr_Occurred()) {
				throw PyDTExc_PythonError();
			}
			return ret;
		}
	}
	

	PyDTObject toInt() const {
		if (m_obj) {
			PyObject *ret = PyNumber_Int(m_obj);
			if (!ret) {
				throw PyDTExc_PythonError();
			}
			return PyDTObject(ret, true);
		}
		else {
			throw PyDTExc_InvalidType();
		}
	}
	
	void *asVoidPtr(void *ifNone=0) const {
		if (!m_obj || isNone()) {
			return ifNone;
		}
		return PyLong_AsVoidPtr(m_obj);
	}

	inline PyDTString repr() const;

	void print(FILE *fp=NULL, bool raw=false) const {
		if (!fp) {
			fp = stdout;
		}
		int flags = 0;
		if (raw) {
			flags |= Py_PRINT_RAW;
		}

		if (-1 == PyObject_Print(m_obj, fp, flags)) {
			throw PyDTExc_PythonError();
		}
	}

	PyDTObject add(const PyDTObject &obj) const {
		PyObject *ret = PyNumber_Add(m_obj, obj.get());
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		return PyDTObject(ret, true);
	}
	
	static PyDTObject fromVoidPtr(void *p) {
		PyObject *ret = PyLong_FromVoidPtr(p);
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		return PyDTObject(ret, true);
	}

	void check() const {
		if (m_obj)
			checkType();
	}

	void checkNull() const {
		if (!m_obj) {
			throw PyDTExc_InvalidValue("Null Python object");
		}
	}

public:
//protected:
	PyObject *m_obj;
	bool m_own;

	virtual void checkType() const {
	}

protected:


	PyObject *null_error(void) const 
	{
		if (!PyErr_Occurred())
			PyErr_SetString(PyExc_SystemError,
					"null argument to internal routine");
		return NULL;
	}

	PyObject *
	type_error(const char *msg) const
	{
		PyErr_SetString(PyExc_TypeError, msg);
		return NULL;
	}
};


class PyDTString:public PyDTObject {
public:
	static PyDTString fromBuf(const char *buf, int len) {
		ASSERT(buf);
		return PyDTString(buf, len);
	}

	PyDTString():PyDTObject() {
	}
	
	PyDTString(PyObject *obj, bool own) :PyDTObject(obj, own){
		check();
	}

	PyDTString(const PyDTObject&r):PyDTObject(r){
		check();
	}

	PyDTString(const char *s, int len) {
		ASSERT(s);
		PyObject *v = PyString_FromStringAndSize(s, len);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTString(const char *start, const char *end) {
		ASSERT(start); 
		ASSERT(end);
		ASSERT(start <= end);

		PyObject *v = PyString_FromStringAndSize(start, end-start);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTString(const char *s) {
		ASSERT(s);
		PyObject *v = PyString_FromString(s);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTString(const char &c) {
		PyObject *v = PyString_FromStringAndSize(&c, 1);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTString(const std::string &s) {
		PyObject *v = PyString_FromStringAndSize(s.c_str(), s.size());
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	const char * asString() const {
		checkNull();
		const char *ret = PyString_AS_STRING(m_obj);
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}
	
	const char * asStringAndSize(int &len) const {
		checkNull();
		char *s=NULL;
		if (-1 == PyString_AsStringAndSize(m_obj, &s, &len)) {
			throw PyDTExc_PythonError();
		}
		return s;
	}
	
	int getSize() const {
		checkNull();
		return PyString_GET_SIZE(m_obj);
	}

	int size() const {
		checkNull();
		return PyString_GET_SIZE(m_obj);
	}

protected:	
	void checkType() const {
		if (!PyString_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("str");
		}
	}
};


class PyDTUnicode:public PyDTObject {
public:
	static PyDTUnicode fromUTF8(const char *buf, int len) {
		ASSERT(buf);
		return PyDTUnicode(PyUnicode_DecodeUTF8(buf, len, "strict"), true);
	}

	PyDTUnicode():PyDTObject() {
	}
	
	PyDTUnicode(PyObject *obj, bool own) :PyDTObject(obj, own){
		check();
	}
	PyDTUnicode(const PyDTObject&r):PyDTObject(r){
		check();
	}
	
	PyDTUnicode(const Py_UNICODE *s, int len) {
		ASSERT(s);
		PyObject *v = PyUnicode_FromUnicode(s, len);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTUnicode(const wchar_t *s) {
		ASSERT(s);
		PyObject *v = PyUnicode_FromWideChar(s, wcslen(s));
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTUnicode(const Py_UNICODE &c) {
		PyObject *v = PyUnicode_FromUnicode(&c, 1);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTUnicode(const _bstr_t &s) {
		PyObject *v = PyUnicode_FromUnicode(s, s.length());
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

/*
	PyDTUnicode(const std::wstring &s) {
		PyObject *v = PyUnicode_FromUnicode(s.c_str(), s.size());
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
*/
	const Py_UNICODE *asUnicode() const {
		checkNull();
		const Py_UNICODE *ret = PyUnicode_AS_UNICODE(m_obj);
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}
	
	const Py_UNICODE * asUnicodeAndSize(int &len) const {
		checkNull();
		Py_UNICODE *s=PyUnicode_AS_UNICODE(m_obj);
		len = PyUnicode_GET_SIZE(m_obj);
		return s;
	}

	PyDTString asUTF8() const {
		checkNull();
		PyObject *ret = PyUnicode_AsUTF8String(m_obj);
		if (!ret) {
			throw PyDTExc_PythonError();
		}
		return PyDTString(ret, true);
	}

	static PyDTUnicode fromBuf(const Py_UNICODE *buf, int len) {
		return PyDTUnicode(buf, len);
	}

	int size() const {
		checkNull();
		return PyUnicode_GET_SIZE(m_obj);
	}
protected:
	void checkType() const {
		if (!PyUnicode_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("unicode");
		}
	}
};


class PyDTInt:public PyDTObject {
public:
	PyDTInt():PyDTObject() {
	}

	PyDTInt(const PyDTObject&r):PyDTObject(r) {
		check();
	}

	PyDTInt(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	PyDTInt(long n) {
		PyObject *v = PyInt_FromLong(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTInt(const char *s, int base) {
		PyObject *v = PyInt_FromString((char*)s, NULL, base);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTInt(const char *s, const char *&end, int base) {
		PyObject *v = PyInt_FromString((char*)s, (char **)&end, base);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	long asLong() const {
		checkNull();
		long ret = PyInt_AS_LONG(m_obj);
		return ret;
	}

protected:	
	void checkType() const {
		if (!PyInt_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("int");
		}
	}
};


class PyDTLong :public PyDTObject {
public:
	PyDTLong():PyDTObject() {
	}

	PyDTLong(const PyDTObject&r):PyDTObject(r) {
		check();
	}

	PyDTLong(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	PyDTLong(long n) {
		PyObject *v = PyLong_FromLong(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTLong(unsigned long n) {
		PyObject *v = PyLong_FromUnsignedLong(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTLong(PY_LONG_LONG n) {
		PyObject *v = PyLong_FromLongLong(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTLong(unsigned PY_LONG_LONG n) {
		PyObject *v = PyLong_FromUnsignedLongLong(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTLong(double n) {
		PyObject *v = PyLong_FromDouble(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTLong(const char *s, int base) {
		PyObject *v = PyLong_FromString((char*)s, NULL, base);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTLong(const char *s, const char *&end, int base) {
		PyObject *v = PyLong_FromString((char*)s, (char **)&end, base);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	long asLong() const {
		checkNull();
		long ret = PyLong_AsLong(m_obj);
		if (PyErr_Occurred()) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}

	unsigned long asUnsignedLong() const {
		checkNull();
		long ret = PyLong_AsUnsignedLong(m_obj);
		if (PyErr_Occurred()) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}

	PY_LONG_LONG asLongLong() const {
		checkNull();
		PY_LONG_LONG ret = PyLong_AsLongLong(m_obj);
		if (PyErr_Occurred()) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}

	unsigned PY_LONG_LONG asUnsignedLongLong() const {
		checkNull();
		PY_LONG_LONG ret = PyLong_AsUnsignedLongLong(m_obj);
		if (PyErr_Occurred()) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}
protected:	
	void checkType() const {
		if (!PyLong_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("long");
		}
	}
};


class PyDTFloat:public PyDTObject {
public:
	PyDTFloat():PyDTObject() {
	}

	PyDTFloat(const PyDTObject&r):PyDTObject(r) {
		check();
	}

	PyDTFloat(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	PyDTFloat(double n) {
		PyObject *v = PyFloat_FromDouble(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	PyDTFloat(const char *s, const char *end) {
		PyDTString pstr(s, end);
		PyObject *v = PyFloat_FromString(pstr.get(), NULL);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	long asLong() const {
		checkNull();
		long ret = PyInt_AS_LONG(m_obj);
		return ret;
	}
protected:	
	void checkType() const {
		if (!PyFloat_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("int");
		}
	}
};



class PyDTSequence:public PyDTObject {
public:
	PyDTSequence():PyDTObject() {
	}
	
	PyDTSequence(PyObject *obj, bool own) :PyDTObject(obj, own){
		check();
	}
	
	PyDTSequence(const PyDTObject&r):PyDTObject(r){
		check();
	}

	virtual int getSize() const {
		checkNull();
		int ret = PySequence_Size(m_obj);
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
		return ret;
	}

	virtual void getItem(int n, PyDTObject &ret) const {
		checkNull();
		PyObject *v = PySequence_GetItem(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		ret.set(v, true);
	}
	
	virtual PyDTObject getItem(int n) const {
		checkNull();
		ASSERT(n < getSize());

		PyObject *v = PySequence_GetItem(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		return PyDTObject(v, true);
	}
	
protected:
	void checkType() const {
		if (!PySequence_Check(m_obj)) {
			throw PyDTExc_InvalidType("sequence");
		}
	}
};


class PyDTTuple:public PyDTSequence {
public:
	PyDTTuple():PyDTSequence() {
	}

	PyDTTuple(PyObject *obj, bool own) :PyDTSequence(obj, own) {
	}
	
	PyDTTuple(const PyDTObject&r):PyDTSequence(r){
		check();
	}

	PyDTTuple(int n):PyDTSequence(NULL, false) {
		PyObject *v = PyTuple_New(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	int getSize() const {
		checkNull();
		int ret = PyTuple_GET_SIZE(m_obj);
		return ret;
	}

	void getItem(int n, PyDTObject &ret) const {
		getTupleItem(n, ret);
	}

	virtual PyDTObject getItem(int n) const {
		checkNull();
		ASSERT(n < getSize());

		PyObject *v = PyTuple_GET_ITEM(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		Py_INCREF(v);
		return PyDTObject(v, true);
//		PyDTObject ret(v, true);
//		ret.incRef();
//		return ret;
	}

	void getTupleItem(int n, PyDTObject &ret) const {
		checkNull();
		PyObject *v = PyTuple_GET_ITEM(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		ret.set(v, true);
		ret.incRef();
	}

	void setItem(int n, const PyDTObject &obj) {
		checkNull();
		PyDTObject item(obj);
		item.incRef();   // PyTuple_SetItem steals object ref.
		if (PyTuple_SetItem(m_obj, n, item.get())) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(int n, int v) {
		checkNull();
		if (PyTuple_SetItem(m_obj, n, PyDTInt(v).detach())) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(int n, const char *s) {
		checkNull();
		if (PyTuple_SetItem(m_obj, n, PyDTString(s).detach())) {
			throw PyDTExc_PythonError();
		}
	}
	void setItem(int n, const wchar_t *s) {
		checkNull();
		if (PyTuple_SetItem(m_obj, n, PyDTUnicode(s).detach())) {
			throw PyDTExc_PythonError();
		}
	}
protected:
	void checkType() const {
		if (!PyTuple_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("tuple");
		}
	}
};


class PyDTList:public PyDTSequence {
public:
	PyDTList():PyDTSequence() {
	}
	
	PyDTList(PyObject *obj, bool own) :PyDTSequence(obj, own){
	}

	PyDTList(const PyDTObject&r):PyDTSequence(r){
		check();
	}

	PyDTList(int n):PyDTSequence(NULL, false) {
		PyObject *v = PyList_New(n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}
	
	int getSize() const {
		checkNull();
		int ret = PyList_GET_SIZE(m_obj);
		return ret;
	}

	void getItem(int n, PyDTObject &ret) const {
		checkNull();
		PyObject *v = PyList_GET_ITEM(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		ret.set(v, true);
		ret.incRef();
	}

	void getListItem(int n, PyDTObject &ret) const {
		checkNull();
		PyObject *v = PyList_GET_ITEM(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		ret.set(v, true);
		ret.incRef();
	}

	virtual PyDTObject getItem(int n) const {
		checkNull();
		ASSERT(n < getSize());

		PyObject *v = PyList_GET_ITEM(m_obj, n);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		Py_INCREF(v);
		return PyDTObject(v, true);
	}

	void setItem(int n, const PyDTObject &obj) {
		checkNull();
		ASSERT(n < getSize());

		PyDTObject item(obj);
		item.incRef();
		if (PyList_SetItem(m_obj, n, item.get())) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(int n, int v) {
		checkNull();
		if (PyList_SetItem(m_obj, n, PyDTInt(v).detach())) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(int n, const char *s) {
		checkNull();
		if (PyList_SetItem(m_obj, n, PyDTString(s).detach())) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(int n, const wchar_t *s) {
		checkNull();
		if (PyList_SetItem(m_obj, n, PyDTUnicode(s).detach())) {
			throw PyDTExc_PythonError();
		}
	}

	PyDTObject getSlice(int f, int t) const {
		checkNull();
		PyObject *v = PyList_GetSlice(m_obj, f, t);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		return PyDTList(v, true);
	}
	
	PyDTObject getSlice() const {
		checkNull();
		PyObject *v = PyList_GetSlice(m_obj, 0, getSize());
		if (!v) {
			throw PyDTExc_PythonError();
		}
		return PyDTList(v, true);
	}
	
	void insert(int n, PyDTObject &obj) {
		checkNull();
		// don't steal
		int ret = PyList_Insert(m_obj, n, obj.get());
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
	}

	void insert(int n, const char *s) {
		checkNull();
		PyDTString str(s);
		insert(n, str);
	}

	void insert(int n, const wchar_t *s) {
		checkNull();
		PyDTUnicode str(s);
		insert(n, str);
	}

	void append(PyDTObject &obj) {
		checkNull();
		// don't steal
		int ret = PyList_Append(m_obj, obj.get());
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
	}

	void append(const char *s) {
		checkNull();
		PyDTString str(s);
		append(str);
	}

	void append(const wchar_t *s) {
		checkNull();
		PyDTUnicode str(s);
		append(str);
	}

	void sort() {
		checkNull();
		if (-1 == PyList_Sort(m_obj)) {
			throw PyDTExc_PythonError();
		}
	}

	PyDTTuple asTuple() const {
		checkNull();
		return PyDTTuple(PyList_AsTuple(m_obj), true);
	}
protected:
	void checkType() const {
		if (!PyList_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("list");
		}
	}
};

class PyDTDict:public PyDTObject {
public:
	PyDTDict():PyDTObject() {
	}

	PyDTDict(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	PyDTDict(const PyDTObject &r):PyDTObject(r){
		check();
	}

	PyDTObject &newObj() {
		free();
		PyObject *v = PyDict_New();
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
		return *this;
	}

	void setItem(const PyDTObject &key, const PyDTObject &value) {
		checkNull();
		// don't steal
		int ret = PyDict_SetItem(m_obj, key.get(), value.get());
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(const char *s, const PyDTObject &value) {
		checkNull();
		// don't steal
		int ret = PyDict_SetItemString(m_obj, (char *)s, value.get());
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
	}

	void setItem(const char *s, PyObject *value, bool steal) {
		checkNull();
		// don't steal
		int ret = PyDict_SetItemString(m_obj, (char *)s, value);
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
		if (steal) {
			Py_DECREF(value);
		}
	}

	void setItem(const char *s, int value) {
		checkNull();
		PyDTInt v(value);
		setItem(s, v);
	}

	void setItem(const char *s, unsigned int value) {
		checkNull();
		PyDTInt v(value);
		setItem(s, v);
	}

	void setItem(const char *s, long value) {
		checkNull();
		PyDTInt v(value);
		setItem(s, v);
	}

	void setItem(const char *s, unsigned long value) {
		checkNull();
		PyDTInt v(value);
		setItem(s, v);
	}

	void setItem(const char *s, const char *value) {
		checkNull();
		PyDTString v(value);
		setItem(s, v);
	}

	void setItem(const char *s, const char *value, int len) {
		checkNull();
		PyDTString v(value, len);
		setItem(s, v);
	}

	void setItem(const char *s, const wchar_t *value) {
		checkNull();
		PyDTUnicode v(value);
		setItem(s, v);
	}


	void delItem(const PyDTObject &key) {
		checkNull();
		int ret = PyDict_DelItem(m_obj, key.get());
		if (ret == -1) {
			throw PyDTExc_PythonError();
		}
	}

	bool getItem(const PyDTObject &key, PyDTObject &ret) const {
		checkNull();
		PyObject *o = PyDict_GetItem(m_obj, key.get());
		if (o) {
			ret.set(o, true);
			ret.incRef();
			return true;
		}
		else {
			return false;
		}
	}

	bool getItem(const char *key, PyDTObject &ret) const {
		checkNull();
		PyObject *o = PyDict_GetItemString(m_obj, (char *)key);
		if (o) {
			ret.set(o, true);
			ret.incRef();
			return true;
		}
		else {
			return false;
		}
	}

	PyDTObject getItem(const PyDTObject &key) const {
		checkNull();
		PyObject *o = PyDict_GetItem(m_obj, key.get());
		if (o) {
			Py_INCREF(o);
			return PyDTObject(o, true);
		}
		else {
			return PyDTObject();
		}
	}

	PyDTObject getItem(const char *key) const {
		checkNull();
		PyObject *o = PyDict_GetItemString(m_obj, (char *)key);
		if (o) {
			Py_INCREF(o);
			return PyDTObject(o, true);
		}
		else {
			return PyDTObject();
		}
	}
	
	bool hasKey(const PyDTObject &key) {
		checkNull();
		int ret = PyDict_Contains(m_obj, key.get());
		switch (ret) {
			case 1:
				return true;
			case 0:
				return false;
			default:
				throw PyDTExc_PythonError();
		}
	}

	bool hasKey(const char *key) {
		checkNull();
		return hasKey(PyDTString(key));
	}

	bool next(int &pos, PyDTObject &key, PyDTObject &value) {
		checkNull();
		PyDTObject k, v;
		
		int ret = PyDict_Next(m_obj, &pos, k.getBuf(), v.getBuf());
		if (ret) {
			key = k; value = v;
			return true;
		}
		return false;
	}

	int getSize() const {
		checkNull();
		return PyDict_Size(m_obj);
	}

	PyDTList items() {
		checkNull();
		return PyDTList(PyDict_Items(m_obj), true);
	}

	void merge(PyDTDict &dict) {
		checkNull();
		ASSERT(dict.get());

		if (PyDict_Update(m_obj, dict.get()) < 0) {
			throw PyDTExc_PythonError();
		}
	}
protected:
	void checkType() const {
		if (!PyDict_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("dict");
		}
	}
};


class PyDTModule:public PyDTObject {
public:
	static PyDTModule create(const char *name, const char *filename) {
		PyObject *m = PyModule_New((char*)name);
		if (!m) {
			throw PyDTExc_PythonError();
		}
		PyDTModule ret(m, true);
		return ret;
	}

	PyDTModule(const PyDTObject&r):PyDTObject(r){
		check();
	}

	PyDTModule(const char *name) {
		ASSERT(name);
		PyObject *v = PyImport_ImportModule((char *)name);
		if (!v) {
			throw PyDTExc_PythonError();
		}
		set(v, true);
	}

	PyDTModule(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	void add(const char *name, int value) {
		checkNull();
		if (-1 == PyModule_AddIntConstant(m_obj, (char *)name, value)) {
			throw PyDTExc_PythonError();
		}
	}

	void add(const char *name, const char *value) {
		checkNull();
		if (-1 == PyModule_AddStringConstant(m_obj, (char *)name, (char *)value)) {
			throw PyDTExc_PythonError();
		}
	}

	void add(const char *name, PyDTObject &value) {
		checkNull();
		value.incRef();	// PyModule_AddObject steals refcount
		if (-1 == PyModule_AddObject(m_obj, (char *)name, value.get())) {
			throw PyDTExc_PythonError();
		}
	}
	
	void add(const char *name, PyTypeObject &type) {
		checkNull();
		if (-1 == PyModule_AddObject(m_obj, (char *)name, (PyObject *)&type)) {
			throw PyDTExc_PythonError();
		}
	}
	
	void getDict(PyDTObject &ret) {
		checkNull();
		ret.set(PyModule_GetDict(m_obj), false);
	}

protected:	
	void checkType() const {
		if (!PyModule_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("module");
		}
	}

};

class PyDTInstance:public PyDTObject {
public:
	PyDTInstance(PyObject *obj, bool own) :PyDTObject(obj, own) {
		check();
	}

	PyDTInstance(const PyDTObject&r):PyDTObject(r){
		check();
	}
protected:
	void checkType() const {
		if (!PyInstance_Check(m_obj)) {
			throw PyDTExc_InvalidType("instance");
		}
	}
};

class PyDTNone:public PyDTObject {
public:
	PyDTNone():PyDTObject(Py_None, true){
		incRef();
	}
};

class PyDTBool:public PyDTObject {
protected:
	PyDTBool(PyObject *obj, bool own):PyDTObject(obj, own) {
	}
	void checkType() const {
		if (!isBool()) {
			throw PyDTExc_InvalidType("dict");
		}
	}
};

class PyDTTrue:public PyDTBool{
public:
	PyDTTrue():PyDTBool(Py_True, true){
		incRef();
	}
};

class PyDTFalse:public PyDTBool {
public:
	PyDTFalse():PyDTBool(Py_False, true){
		incRef();
	}
};

class PyDTType:public PyDTObject {
public:
	PyDTType(PyTypeObject *type)
		:PyDTObject((PyObject *)type, false) {
	}
	PyDTType(PyObject *type)
		:PyDTObject(type, false) {
	}

protected:
	void checkType() const {
		if (!PyType_CheckExact(m_obj)) {
			throw PyDTExc_InvalidType("int");
		}
	}
};


inline PyDTString PyDTObject::repr() const {
	checkNull();
	PyObject *ret = PyObject_Repr(m_obj);
	if (!ret) {
		throw PyDTExc_PythonError();
	}
	return PyDTString(ret, true);
}



inline
PyDTTuple pydtMakeTuple(PyDTObject &v1) {
	PyDTTuple ret(1);
	ret.setItem(0, v1);
	return ret;
}

inline
PyDTTuple pydtMakeTuple(PyDTObject &v1, PyDTObject &v2) {
	PyDTTuple ret(2);
	ret.setItem(0, v1);
	ret.setItem(1, v2);
	return ret;
}

inline
PyDTTuple pydtMakeTuple(long v1, long v2) {
	PyDTTuple ret(2);
	ret.setItem(0, PyDTInt(v1));
	ret.setItem(1, PyDTInt(v2));
	return ret;
}

inline
PyDTTuple pydtMakeTuple(long v1, long v2, long v3) {
	PyDTTuple ret(3);
	ret.setItem(0, PyDTInt(v1));
	ret.setItem(1, PyDTInt(v2));
	ret.setItem(2, PyDTInt(v3));
	return ret;
}

inline
PyDTTuple pydtMakeTuple(long v1, long v2, long v3, long v4) {
	PyDTTuple ret(4);
	ret.setItem(0, PyDTInt(v1));
	ret.setItem(1, PyDTInt(v2));
	ret.setItem(2, PyDTInt(v3));
	ret.setItem(3, PyDTInt(v4));
	return ret;
}

inline
PyDTTuple pydtMakeTuple(const char *v1, const char *v2) {
	PyDTTuple ret(2);
	ret.setItem(0, PyDTString(v1));
	ret.setItem(1, PyDTString(v2));
	return ret;
}

inline
PyDTTuple pydtMakeTuple(const char *v1, const char *v2, const char *v3) {
	PyDTTuple ret(3);
	ret.setItem(0, PyDTString(v1));
	ret.setItem(1, PyDTString(v2));
	ret.setItem(2, PyDTString(v3));
	return ret;
}

inline
PyDTTuple pydtMakeTuple(const char *v1, const char *v2, const char *v3, const char *v4) {
	PyDTTuple ret(4);
	ret.setItem(0, PyDTString(v1));
	ret.setItem(1, PyDTString(v2));
	ret.setItem(2, PyDTString(v3));
	ret.setItem(3, PyDTString(v4));
	return ret;
}


template <class T>
class PyDTExtDef {
public:
	typedef typename T::TypeInstance TTYPEINSTANCE;
	PyDTExtDef() {
		memset(&m_typeObj, 0, sizeof(m_typeObj));
		memset(&m_seqMethods, 0, sizeof(m_seqMethods));
		memset(&m_numMethods, 0, sizeof(m_numMethods));
	}
	
	PyTypeObject &getTypeObj() {
		return m_typeObj;
	}
	
	PyDTObject getDTTypeObj() {
		return PyDTObject((PyObject *)&m_typeObj, false);
	}

	TTYPEINSTANCE *newObject() {
		TTYPEINSTANCE *ret;
		if (m_typeObj.tp_flags & Py_TPFLAGS_HAVE_GC) {
			ret = PyObject_GC_New(TTYPEINSTANCE, &getTypeObj());
		}
		else {
			ret = PyObject_New(TTYPEINSTANCE, &getTypeObj());
		}
		return ret;
	}

	void initType(const char *name) {
		m_typeObj = STDTYPETYPE;
		m_typeObj.tp_name = (char *)name;

		m_typeObj.tp_base = T::getBaseType();

		T::initMethods(*this);
		initSlots(name);
		PyType_Ready(&m_typeObj);
	}

	void initSlots(const char *name) {
		
		if (m_methods.size()) {
			PyMethodDef m;
			memset(&m, 0, sizeof(m));
			m_methods.push_back(m);
			m_typeObj.tp_methods = &(*m_methods.begin());
		}
		
		if (m_members.size()) {
			PyMemberDef m;
			memset(&m, 0, sizeof(m));
			m_members.push_back(m);
			m_typeObj.tp_members = &(*m_members.begin());
		}
		
		if (m_getset.size()) {
			PyGetSetDef gs = {NULL, NULL, NULL, NULL};
			memset(&gs, 0, sizeof(gs));
			m_getset.push_back(gs);
			m_typeObj.tp_getset= &(*m_getset.begin());
		}
	}
	
	static int defInitProc(TTYPEINSTANCE *obj, PyObject *args, PyObject *kwds) {
		return T::onInitObj(obj, args, kwds);
	}

	static void defDealloc(TTYPEINSTANCE *obj) {
		T::onDeallocObj(obj);
		obj->ob_type->tp_free((PyObject *)obj);
	}

	static void defGCDealloc(TTYPEINSTANCE *obj) {
		PyObject_GC_UnTrack((PyObject *) obj);
		T::onDeallocObj(obj);
		obj->ob_type->tp_free((PyObject *)obj);
	}

	void setDictOffset(int offset) {
		m_typeObj.tp_dictoffset = offset;
	}

	// GC support
	typedef int (*VISITPROC)(PyObject *object, void *arg);
	typedef int (*TRAVERSEPROC)(TTYPEINSTANCE *self, visitproc visit, void *arg);
	typedef int (*INQUIRYPROC)(TTYPEINSTANCE *self);

	void setGC(TRAVERSEPROC traverse, INQUIRYPROC inquiryproc) {
		m_typeObj.tp_traverse = (traverseproc)traverse;
		m_typeObj.tp_clear = (inquiry)inquiryproc;
		m_typeObj.tp_dealloc = (destructor)defGCDealloc;
		m_typeObj.tp_free = _PyObject_GC_Del;

		m_typeObj.tp_flags |=  Py_TPFLAGS_HAVE_GC;
	}

	// methods
	typedef PyObject *(*NOARGMETHOD)(TTYPEINSTANCE *);
	typedef PyObject *(*VARARGMETHOD)(TTYPEINSTANCE *, PyObject *);
	typedef PyObject *(*KWDARGMETHOD)(TTYPEINSTANCE *, PyObject *, PyObject *);

	void addMethod(const char *name, NOARGMETHOD func, const char *doc=NULL) {
		addmethod(name, func, doc, METH_NOARGS);
	}

	void addArgMethod(const char *name, VARARGMETHOD func, const char *doc=NULL) {
		addmethod(name, func, doc, METH_VARARGS);
	}

	void addKwdArgMethod(const char *name, KWDARGMETHOD func, const char *doc=NULL) {
		addmethod(name, func, doc, METH_VARARGS|METH_KEYWORDS);
	}

	void addObjArgMethod(const char *name, VARARGMETHOD func, const char *doc=NULL) {
		addmethod(name, func, doc, METH_O);
	}

	// Sequence methods
	typedef int (*SEQ_LENGTH)(TTYPEINSTANCE *);
	typedef PyObject * (*SEQ_CONCAT)(TTYPEINSTANCE *, PyObject *);
	typedef PyObject *(*SEQ_REPEAT)(TTYPEINSTANCE *, int);
	typedef PyObject *(*SEQ_ITEM)(TTYPEINSTANCE *, int);
	typedef PyObject *(*SEQ_SLICE)(TTYPEINSTANCE *, int, int);
	typedef int(*SEQ_ASS_ITEM)(TTYPEINSTANCE *, int, PyObject *);
	typedef int(*SEQ_ASS_SLICE)(TTYPEINSTANCE *, int, int, PyObject *);
	typedef int(*SEQ_CONTAINS)(TTYPEINSTANCE *, PyObject *, PyObject *);
	typedef int(*SEQ_INPLACE_CONCAT)(TTYPEINSTANCE *, PyObject *);
	typedef PyObject *(*SEQ_INPLACE_REPEAT)(TTYPEINSTANCE *, int);

	void setSeqMethods(SEQ_LENGTH length, SEQ_CONCAT concat, SEQ_REPEAT repeat, 
		SEQ_ITEM item, SEQ_SLICE slice, SEQ_ASS_ITEM ass_item, 
		SEQ_ASS_SLICE ass_slice, SEQ_CONTAINS contains, 
		SEQ_INPLACE_CONCAT inplace_concat, SEQ_INPLACE_REPEAT inplace_repeat) {

		m_seqMethods.sq_length = (inquiry)length;
		m_seqMethods.sq_concat = (binaryfunc)concat;
		m_seqMethods.sq_repeat = (intargfunc)repeat;
		m_seqMethods.sq_item = (intargfunc)item;
		m_seqMethods.sq_slice = (intintargfunc)slice;
		m_seqMethods.sq_ass_item = (intobjargproc)ass_item;
		m_seqMethods.sq_ass_slice = (intintobjargproc)ass_slice;
		m_seqMethods.sq_contains = (objobjproc)contains;
		m_seqMethods.sq_inplace_concat = (binaryfunc)inplace_concat;
		m_seqMethods.sq_inplace_repeat = (intargfunc)inplace_repeat;
		
		m_typeObj.tp_as_sequence = &m_seqMethods;
	}

	// Number methods
	typedef PyObject * (*UNARY_FUNC)(TTYPEINSTANCE *);
	typedef PyObject * (*BINARY_FUNC)(TTYPEINSTANCE *, PyObject *);
	typedef PyObject * (*TERNARY_FUNC)(PyObject *, PyObject *, PyObject *);
	typedef int (*INQUIRY_FUNC)(TTYPEINSTANCE *);
	typedef int (*COERCION_FUNC)(PyObject **, PyObject **);

	void setNumberMethods(
		BINARY_FUNC nb_add=NULL,
		BINARY_FUNC nb_subtract=NULL,
		BINARY_FUNC nb_multiply=NULL,
		BINARY_FUNC nb_divide=NULL,
		BINARY_FUNC nb_remainder=NULL,
		BINARY_FUNC nb_divmod=NULL,
		TERNARY_FUNC nb_power=NULL,
		UNARY_FUNC nb_negative=NULL,
		UNARY_FUNC nb_positive=NULL,
		UNARY_FUNC nb_absolute=NULL,
		INQUIRY_FUNC nb_nonzero=NULL,
		UNARY_FUNC nb_invert=NULL,
		BINARY_FUNC nb_lshift=NULL,
		BINARY_FUNC nb_rshift=NULL,
		BINARY_FUNC nb_and=NULL,
		BINARY_FUNC nb_xor=NULL,
		BINARY_FUNC nb_or=NULL,
		COERCION_FUNC nb_coerce=NULL,
		UNARY_FUNC nb_int=NULL,
		UNARY_FUNC nb_long=NULL,
		UNARY_FUNC nb_float=NULL,
		UNARY_FUNC nb_oct=NULL,
		UNARY_FUNC nb_hex=NULL,
		BINARY_FUNC nb_inplace_add=NULL,
		BINARY_FUNC nb_inplace_subtract=NULL,
		BINARY_FUNC nb_inplace_multiply=NULL,
		BINARY_FUNC nb_inplace_divide=NULL,
		BINARY_FUNC nb_inplace_remainder=NULL,
		TERNARY_FUNC nb_inplace_power=NULL,
		BINARY_FUNC nb_inplace_lshift=NULL,
		BINARY_FUNC nb_inplace_rshift=NULL,
		BINARY_FUNC nb_inplace_and=NULL,
		BINARY_FUNC nb_inplace_xor=NULL,
		BINARY_FUNC nb_inplace_or=NULL,
		BINARY_FUNC nb_floor_divide=NULL,
		BINARY_FUNC nb_true_divide=NULL,
		BINARY_FUNC nb_inplace_floor_divide=NULL,
		BINARY_FUNC nb_inplace_true_divide=NULL ) {

		m_numMethods.nb_add = (binaryfunc)nb_add;
		m_numMethods.nb_subtract = (binaryfunc)nb_subtract;
		m_numMethods.nb_multiply = (binaryfunc)nb_multiply;
		m_numMethods.nb_divide = (binaryfunc)nb_divide;
		m_numMethods.nb_remainder = (binaryfunc)nb_remainder;
		m_numMethods.nb_divmod = (binaryfunc)nb_divmod;
		m_numMethods.nb_power = (ternaryfunc)nb_power;
		m_numMethods.nb_negative = (unaryfunc)nb_negative;
		m_numMethods.nb_positive = (unaryfunc)nb_positive;
		m_numMethods.nb_absolute = (unaryfunc)nb_absolute;
		m_numMethods.nb_nonzero = (inquiry)nb_nonzero;
		m_numMethods.nb_invert = (unaryfunc)nb_invert;
		m_numMethods.nb_lshift = (binaryfunc)nb_lshift;
		m_numMethods.nb_rshift = (binaryfunc)nb_rshift;
		m_numMethods.nb_and = (binaryfunc)nb_and;
		m_numMethods.nb_xor = (binaryfunc)nb_xor;
		m_numMethods.nb_or = (binaryfunc)nb_or;
		m_numMethods.nb_coerce = (coercion)nb_coerce;
		m_numMethods.nb_int = (unaryfunc)nb_int;
		m_numMethods.nb_long = (unaryfunc)nb_long;
		m_numMethods.nb_float = (unaryfunc)nb_float;
		m_numMethods.nb_oct = (unaryfunc)nb_oct;
		m_numMethods.nb_hex = (unaryfunc)nb_hex;
		m_numMethods.nb_inplace_add = (binaryfunc)nb_inplace_add;
		m_numMethods.nb_inplace_subtract = (binaryfunc)nb_inplace_subtract;
		m_numMethods.nb_inplace_multiply = (binaryfunc)nb_inplace_multiply;
		m_numMethods.nb_inplace_divide = (binaryfunc)nb_inplace_divide;
		m_numMethods.nb_inplace_remainder = (binaryfunc)nb_inplace_remainder;
		m_numMethods.nb_inplace_power = (ternaryfunc)nb_inplace_power;
		m_numMethods.nb_inplace_lshift = (binaryfunc)nb_inplace_lshift;
		m_numMethods.nb_inplace_rshift = (binaryfunc)nb_inplace_rshift;
		m_numMethods.nb_inplace_and = (binaryfunc)nb_inplace_and;
		m_numMethods.nb_inplace_xor = (binaryfunc)nb_inplace_xor;
		m_numMethods.nb_inplace_or = (binaryfunc)nb_inplace_or;
		m_numMethods.nb_floor_divide = (binaryfunc)nb_floor_divide;
		m_numMethods.nb_true_divide = (binaryfunc)nb_true_divide;
		m_numMethods.nb_inplace_floor_divide = (binaryfunc)nb_inplace_floor_divide;
		m_numMethods.nb_inplace_true_divide = (binaryfunc)nb_inplace_true_divide;
		
		m_typeObj.tp_as_number = &m_numMethods;
	}


	
	// Property methods
	typedef PyObject *(*GETTER_FUNC)(TTYPEINSTANCE *, void *);
	typedef int (*SETTER_FUNC)(TTYPEINSTANCE *, PyObject *, void *);

	void addGetSet(const char *name, GETTER_FUNC g, SETTER_FUNC s, const char *doc=NULL, void *closure=NULL) {
		PyGetSetDef gs;
		gs.name = (char *)name; 
		gs.get = (getter)g;
		gs.set = (setter)s;
		gs.doc = (char *)doc;
		gs.closure = closure;
	
		m_getset.push_back(gs);
	}

	// Type members
	void addIntMember(const char *name, int offset, bool ro=false, const char *doc=NULL) {
		addmember(name, T_INT, offset, doc, ro);
	}

	void addObjMember(const char *name, int offset, bool ro=false, const char *doc=NULL) {
		addmember(name, T_OBJECT, offset, doc, ro);
	}


protected:	
	PyTypeObject				m_typeObj;
	PySequenceMethods			m_seqMethods;
	PyNumberMethods				m_numMethods;
	std::vector<PyMethodDef>	m_methods;
	std::vector<PyGetSetDef>	m_getset;
	std::vector<PyMemberDef>	m_members;

	static PyTypeObject STDTYPETYPE;
private:
	void addmethod(const char *name, void *func, const char *doc, int flag) {
		PyMethodDef m;
		m.ml_name  = (char *)name;
		m.ml_meth  = (PyCFunction)func;
		m.ml_flags = flag;
		m.ml_doc   = (char *)doc;
		m_methods.push_back(m);
	}

	void addmember(const char *name, int type, int offset, const char *doc, bool ro) {
		PyMemberDef m;
		m.name = (char *)name;
		m.type = type;
		m.offset = offset;
		m.flags = ro ? RO:0;
		m.doc = (char *)doc;
		
		m_members.push_back(m);
	}
};

 
template <class T> PyTypeObject	PyDTExtDef<T>::STDTYPETYPE = {
	PyObject_HEAD_INIT(&PyType_Type)
	0,
	"",
	sizeof(TTYPEINSTANCE),
	0,
	(destructor)defDealloc, 	/* tp_dealloc */
	0,					/* tp_print */
	0,					/* tp_getattr */
	0,					/* tp_setattr */
	0,					/* tp_compare */
	0,					/* tp_repr */
	0,					/* tp_as_number */
	0,					/* tp_as_sequence */
	0,					/* tp_as_mapping */
	0,					/* tp_hash */
	0,					/* tp_call */
	0,					/* tp_str */
	PyObject_GenericGetAttr, /* tp_getattro */
	PyObject_GenericSetAttr, /* tp_setattro */
	0,					/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,	/* tp_flags */
	0,					/* tp_doc */
	0,					/* tp_traverse */
	0,					/* tp_clear */
	0,					/* tp_richcompare */
	0,					/* tp_weaklistoffset */
	0,					/* tp_iter */
	0,					/* tp_iternext */
	0,					/* tp_methods */
	0,					/* tp_members */
	0,					/* tp_getset */
	0,					/* tp_base */
	0,					/* tp_dict */
	0,					/* tp_descr_get */
	0,					/* tp_descr_set */
	0,					/* tp_dictoffset */
	(initproc)defInitProc,	/* tp_init */
	PyType_GenericAlloc,	/* tp_alloc */
	PyType_GenericNew,		/* tp_new */
	_PyObject_Del,			/* tp_free */
};


template <class T>
void PyDTRegType(PyDTModule &mod, const char *tp_name, const char *name, T &def) {
//	static T def;
	assert(def.getTypeObj().tp_name == NULL);  // def cannot initialized twice
	def.initType(tp_name);
	mod.add(name, def.getTypeObj());
}

template <class T>
class PyDTEnumType {
public:
	typedef PyDTExtDef<T> EXTDEF;
	struct TypeInstance {
		PyObject_HEAD
	};

	static void addConstDef(EXTDEF &def, const char *name, int value, const char *doc=NULL) {
		def.addGetSet(name, &getConst, NULL, doc, (void *)value);
	}

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		T::initConsts(def);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		return 0;
	}

	static void onDeallocObj(TypeInstance *obj) {
	}

	static PyObject *getConst(TypeInstance *obj, void *value) {
		return PyDTInt((int)value).detach();
	}
};


template <class T, unsigned int INITVALUE=0>
class PyDTFlagType {

/* SAMPLE
class PyMFCDropEffect:public PyDTFlagType<PyMFCDropEffect, DROPEFFECT_NONE> {
public:
	static void initFlags(EXTDEF &def) {
		addValueDef(def, "none", DROPEFFECT_NONE);
		addFlagDef(def, "copy", DROPEFFECT_COPY);
		addFlagDef(def, "move", DROPEFFECT_MOVE);
		addFlagDef(def, "link", DROPEFFECT_LINK);
		addFlagDef(def, "scroll", DROPEFFECT_SCROLL);
	}
	static EXTDEF def_dropeffect;
};

PyMFCDropEffect::EXTDEF PyMFCDropEffect::def_dropeffect;
*/

public:
	typedef PyDTExtDef<T> EXTDEF;
	struct TypeInstance {
		PyObject_HEAD
		unsigned int value;
	};

	static void addFlagDef(EXTDEF &def, const char *name, unsigned int mask, const char *doc=NULL) {
		def.addGetSet(name, &getFlag, &setFlag, doc, (void *)mask);
	}

	static void addValueDef(EXTDEF &def, const char *name, unsigned int mask, const char *doc=NULL) {
		def.addGetSet(name, &getValue, &setValue, doc, (void *)mask);
	}

	static PyTypeObject *getBaseType() {
		return NULL;
	}

	static void initMethods(EXTDEF &def) {
		def.addIntMember("value", offsetof(TypeInstance, value));
		def.setNumberMethods(
			NULL, // nb_add,
			NULL, // nb_subtract,
			NULL, // nb_multiply,
			NULL, // nb_divide,
			NULL, // nb_remainder,
			NULL, // nb_divmod,
			NULL, // nb_power,
			NULL, // nb_negative,
			NULL, // nb_positive,
			NULL, // nb_absolute,
			nonzero, // nb_nonzero,
			NULL, // nb_invert,
			NULL, // nb_lshift,
			NULL, // nb_rshift,
			NULL, // nb_and,
			NULL, // nb_xor,
			NULL, // nb_or,
			NULL, // nb_coerce,
			to_int, // nb_int,
			NULL, // nb_long,
			NULL, // nb_float,
			NULL, // nb_oct,
			NULL, // nb_hex,
			NULL, // nb_inplace_add,
			NULL, // nb_inplace_subtract,
			NULL, // nb_inplace_multiply,
			NULL, // nb_inplace_divide,
			NULL, // nb_inplace_remainder,
			NULL, // nb_inplace_power,
			NULL, // nb_inplace_lshift,
			NULL, // nb_inplace_rshift,
			NULL, // nb_inplace_and,
			NULL, // nb_inplace_xor,
			NULL, // nb_inplace_or,
			NULL, // nb_floor_divide,
			NULL, // nb_true_divide,
			NULL, // nb_inplace_floor_divide,
			NULL  // nb_inplace_true_divide 
		);
		
		
		T::initFlags(def);
	}

	static int onInitObj(TypeInstance *obj, PyObject *args, PyObject *kwds) {
		try {
			obj->value = INITVALUE;

			if (args) {
				PyDTTuple arg(args, false);
				int argsize = arg.getSize();
				if (argsize == 1) {
					PyDTObject r(arg.getItem(0));

					if (r.isInstance(PyObject_Type((PyObject*)obj))) {
						PyDTInt value(r.getAttr("value"));
						obj->value = value.asLong();
					}
					else {
						PyDTObject s((PyObject *)obj, false);
						PyDTObject f;
						if (s.getAttr("fromObj", f)) {
							f.call("O", r.get());
						}
						else {
							PyErr_SetString(PyExc_TypeError, "Positional parameters aren't allowed");
							return -1;
						}
					}
				}
				else if (argsize) {
					PyErr_SetString(PyExc_TypeError, "Positional parameters aren't allowed");
					return -1;
				}
			}

			if (kwds) {
				PyDTObject s((PyObject *)obj, false);

				PyDTList items(PyDTDict(kwds, false).items());
				for (int i = 0; i < items.getSize(); i++) {
					PyDTTuple tp(items.getItem(i));

					PyDTString name(tp.getItem(0));
					PyDTObject val(tp.getItem(1));

					s.setAttr(name, val);
				}
			}
			return 0;
		}
		catch (PyDTException &err) {
			err.setError();
			return -1;
		}
		return -1;	// never reach here.
	}

	static void onDeallocObj(TypeInstance *obj) {
	}

	static int setFlag(TypeInstance *obj, PyObject *v, void *value) {
		try {
			int mask = (int)value;
			if (v) {
				if (PyDTObject(v, false).getInt()) {
					obj->value |= mask;
				}
				else {
					obj->value &= ~mask;
				}
			}
			else {
				obj->value &= ~mask;
			}
			return 0;
		}
		catch (PyDTException &err) {
			err.setError();
			return -1;
		}
		return -1;	// never reach here.
	}

	static PyObject *getValue(TypeInstance *obj, void *value) {
		return PyDTInt(obj->value == (unsigned int)value ? 1:0).detach();
	}

	static int setValue(TypeInstance *obj, PyObject *v, void *value) {
		try {
			if (v) {
				if (PyDTObject(v, false).getInt()) {
					obj->value = (int)value;
				}
			}
			return 0;
		}
		catch (PyDTException &err) {
			err.setError();
			return -1;
		}
		return -1;	// never reach here.
	}

	static PyObject *getFlag(TypeInstance *obj, void *value) {
		return PyDTInt(obj->value & (int)value ? 1:0).detach();
	}

	static PyObject *to_int(TypeInstance *obj) {
		return PyDTInt(obj->value).detach();
	}
	
	static int nonzero(TypeInstance *obj) {
		return obj->value != 0;
	}
};


#endif
