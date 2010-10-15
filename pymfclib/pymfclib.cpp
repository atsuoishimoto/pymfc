// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

#include "stdafx.h"
#include "pymfclib.h"
#include "pymfcdefs.h"
#include "pymapp.h"
#include <initguid.h>
#include "pymfclib_i.c"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE

static char THIS_FILE[] = __FILE__;
#endif

class CpymfclibModule :
	public CAtlMfcModule
{
public:
	DECLARE_LIBID(LIBID_pymfclibLib);
	DECLARE_REGISTRY_APPID_RESOURCEID(IDR_PYMFCLIB, "{9BCD1061-A68D-43C0-9598-62DED1E5EFB1}");};

CpymfclibModule _AtlModule;



AFX_MODULE_STATE* PYMFC_AFX_DLLSTATE::state=NULL;
PyObject* PYMFC_AFX_DLLSTATE::ref_pymfclib = NULL;
CRITICAL_SECTION PYMFC_AFX_DLLSTATE::delWndCS;
std::vector<CWnd *> PYMFC_AFX_DLLSTATE::delWnds;

PyObject *PyMFCException::m_errobj = NULL;
PyObject *PyMFCWin32Exception::m_errobj = NULL;



/////////////////////////////////////////////////////////////////////////////
// CPymfclibApp

BEGIN_MESSAGE_MAP(CPymfclibApp, CWinApp)
	//{{AFX_MSG_MAP(CPymfclibApp)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

CPymfclibApp::CPymfclibApp()
{
}

CPymfclibApp::~CPymfclibApp() {
	// Detach idle proc. Python interpreter is already cleaned up by this timing,
	// so idle proc cannnot be decrefed.
	m_idleProc.detach();
	m_timerProcs.detach();
}

CPymfclibApp theApp;

void CPymfclibApp::setIdleProc(PyObject *proc) {
	m_idleProc = PyDTObject(proc, false);
}

void CPymfclibApp::setTimerProcs(PyObject *procs) {
	m_timerProcs = PyDTObject(procs, false);
}


int CPymfclibApp::Run() 
{
	int ret = CWinThread::Run();	// Don't call CWinApp::Run()
	{
		PyMFCEnterPython ep;
	}
	m_idleProc.free();
	m_timerProcs.free();
	return ret;
}

BOOL CPymfclibApp::PreTranslateMessage(MSG* pMsg) {


	if (pMsg->message == WM_TIMER && pMsg->hwnd == NULL) {
		if (m_timerProcs.get()) {
			PyMFCEnterPython ep;
	
			try {
				PyDTObject f(m_timerProcs.getItem(PyDTInt(pMsg->wParam)));
				if (f.get()) {
					f.call("");
				}
			}
			catch (PyDTException &err) {
				err.setError();
//				printf("Error at CPymfclibApp::PreTranslateMessage\n");
				PyErr_Print();
			}
		}
	}

	return CWinApp::PreTranslateMessage(pMsg);
}

DWORD lasttimer = 0;
DWORD lastmsg = 0;
BOOL FORCE_IDLE = FALSE;
BOOL IDLE_RESUME = FALSE;


BOOL CPymfclibApp::InitInstance()
{
	COleObjectFactory::RegisterAll();
	AfxEnableControlContainer();
	_AtlModule.RegisterServer();
	return CWinApp::InitInstance();
}

BOOL CPymfclibApp::IsIdleMessage(MSG* pMsg) {
	lastmsg  = pMsg->message;
/*
if (pMsg->message != 0x113) {
		printf("----> %x\n", pMsg->message);
	}
*/	
	if (pMsg->message == 0x400) {
		FORCE_IDLE = TRUE;
		IDLE_RESUME = TRUE;
	}
	if (FORCE_IDLE) {
		return TRUE;
	}
	if (pMsg->message == WM_TIMER) {
		return FALSE;
	}
/*
	if (pMsg->message == WM_TIMER) {
		if (GetTickCount() - lasttimer >= 5000) {
			lasttimer = GetTickCount();
			printf("ACTIVE\n");
			return TRUE;
		}
		return FALSE;
	}
*/
	return CWinApp::IsIdleMessage(pMsg);
}


BOOL CPymfclibApp::OnIdle(LONG lCount) 
{	
	FORCE_IDLE = FALSE;

	if (lCount == 0) {
		m_runningIdleProc = 0;
		IDLE_RESUME = TRUE;
	}

	BOOL ret = CWinApp::OnIdle(lCount);
	if (!ret) {
		PYMFC_AFX_DLLSTATE::DeleteSuspendedWnd();
	}
	if (ret) {
		return TRUE;
	}
	
	if (m_idleProc.get()) {
		PyMFCEnterPython ep;
		try {
			if (IDLE_RESUME) {
				m_idleProc.callMethod("resume", "");
				IDLE_RESUME = FALSE;
			}

			PyDTObject ret = m_idleProc.call("");
			if (ret.getInt() == 0) {
				return FALSE;
			}
			return TRUE;
		}
		catch (PyDTException &err) {
//			printf("Error at CPymfclibApp::OnIdle\n");
			err.setError();
			PyErr_Print();
			return FALSE;
		}
	}
	return FALSE;
}

BOOL CPymfclibApp::OnKickIdle(LONG lCount) {
	return OnIdle(lCount);
}

int CPymfclibApp::ExitInstance() 
{
	PYMFC_AFX_DLLSTATE::DeleteSuspendedWnd();
	return CWinApp::ExitInstance();
}

int App_Run() {
	PyMFC_PROLOGUE(App_Run);
	
	int ret;
	{
		PyMFCLeavePython lp;
		ret = theApp.Run();
	}
	return ret;

	PyMFC_EPILOGUE(-1);
}

void App_Quit(int result) {
	PyMFC_PROLOGUE(App_Quit)
	PostQuitMessage(result);
	PyMFC_VOID_EPILOGUE()
}


int App_SetIdleProc(PyObject *proc) {
	PyMFC_PROLOGUE(App_SetIdleProc);
	
	theApp.setIdleProc(proc);
	return TRUE;
	
	PyMFC_EPILOGUE(0);
}

int App_SetTimerProcs(PyObject *procs) {
	PyMFC_PROLOGUE(App_SetTimerProc);
	
	theApp.setTimerProcs(procs);
	return TRUE;
	
	PyMFC_EPILOGUE(0);
}

int App_PumpMessage() {
	PyMFC_PROLOGUE(App_PumpMessage);
	return theApp.PumpMessage();
	PyMFC_EPILOGUE(0);
}

// DllCanUnloadNow - Allows COM to unload DLL
#if !defined(_WIN32_WCE) && !defined(_AMD64_) && !defined(_IA64_)
#pragma comment(linker, "/EXPORT:DllCanUnloadNow=_DllCanUnloadNow@0,PRIVATE")
#pragma comment(linker, "/EXPORT:DllGetClassObject=_DllGetClassObject@12,PRIVATE")
#pragma comment(linker, "/EXPORT:DllRegisterServer=_DllRegisterServer@0,PRIVATE")
#pragma comment(linker, "/EXPORT:DllUnregisterServer=_DllUnregisterServer@0,PRIVATE")
#else
#if defined(_X86_) || defined(_SHX_)
#pragma comment(linker, "/EXPORT:DllCanUnloadNow=_DllCanUnloadNow,PRIVATE")
#pragma comment(linker, "/EXPORT:DllGetClassObject=_DllGetClassObject,PRIVATE")
#pragma comment(linker, "/EXPORT:DllRegisterServer=_DllRegisterServer,PRIVATE")
#pragma comment(linker, "/EXPORT:DllUnregisterServer=_DllUnregisterServer,PRIVATE")
#else
#pragma comment(linker, "/EXPORT:DllCanUnloadNow,PRIVATE")
#pragma comment(linker, "/EXPORT:DllGetClassObject,PRIVATE")
#pragma comment(linker, "/EXPORT:DllRegisterServer,PRIVATE")
#pragma comment(linker, "/EXPORT:DllUnregisterServer,PRIVATE")
#endif // (_X86_)||(_SHX_)
#endif // !_WIN32_WCE && !_AMD64_ && !_IA64_ 

STDAPI DllCanUnloadNow(void)
{
	AFX_MANAGE_STATE(AfxGetStaticModuleState());
	if (_AtlModule.GetLockCount() > 0)
		return S_FALSE;
	return S_OK;
}

// DllGetClassObject - Returns class factory
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID* ppv)
{
	AFX_MANAGE_STATE(AfxGetStaticModuleState());
	if (S_OK == _AtlModule.GetClassObject(rclsid, riid, ppv))
		return S_OK;
	return AfxDllGetClassObject(rclsid, riid, ppv);
}

// DllRegisterServer - Adds entries to the system registry
STDAPI DllRegisterServer(void)
{
	AFX_MANAGE_STATE(AfxGetStaticModuleState());
	_AtlModule.UpdateRegistryAppId(TRUE);
	HRESULT hRes2 = _AtlModule.RegisterServer(TRUE);
	if (hRes2 != S_OK)
		return hRes2;
	if (!COleObjectFactory::UpdateRegistryAll(TRUE))
		return ResultFromScode(SELFREG_E_CLASS);
	return S_OK;
}

// DllUnregisterServer - Removes entries from the system registry
STDAPI DllUnregisterServer(void)
{
	AFX_MANAGE_STATE(AfxGetStaticModuleState());
	_AtlModule.UpdateRegistryAppId(FALSE);
	HRESULT hRes2 = _AtlModule.UnregisterServer(TRUE);
	if (hRes2 != S_OK)
		return hRes2;
	if (!COleObjectFactory::UpdateRegistryAll(FALSE))
		return ResultFromScode(SELFREG_E_CLASS);
	return S_OK;
}
