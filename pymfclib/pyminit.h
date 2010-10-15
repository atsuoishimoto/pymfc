#ifndef PYMFCINIT_H_DEF
#define PYMFCINIT_H_DEF

#ifdef __cplusplus
extern "C" {
#endif

#include "pymfcdefs.h"

PYMFC_API int pymInit(PyObject *);
PYMFC_API int pymInitModules();
PYMFC_API PyObject *pymInitPyMFCException();
PYMFC_API PyObject *pymInitPyMFCWin32Exception();
PYMFC_API PyObject *pymInitWndMsgType();
PYMFC_API PyObject *pymInitKeyDict();
PYMFC_API PyObject *pymInitMessageDict();

//void init_shlobj(PyObject *module);
//void init_oleobjs(PyObject *module);
//void init_commodule(PyObject *module);
//void init_pymfclib_gdi(void);
//void init_pymfclib_system(void);


#ifdef __cplusplus
}
#endif

#endif
