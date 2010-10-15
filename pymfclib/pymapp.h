// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#ifndef PYMFCAPP_H
#define PYMFCAPP_H

#ifdef __cplusplus
extern "C" {
#else
#	pragma warning(disable:4101 4102)
#endif


PYMFC_API int App_Run();
PYMFC_API void App_Quit(int result);
PYMFC_API int App_SetIdleProc(PyObject *proc);
PYMFC_API int App_SetTimerProcs(PyObject *procs);
PYMFC_API int App_PumpMessage();




#ifdef __cplusplus
}
#endif



#endif