

/* this ALWAYS GENERATED file contains the definitions for the interfaces */


 /* File created by MIDL compiler version 7.00.0500 */
/* at Wed Nov 17 18:22:29 2010
 */
/* Compiler settings for .\pymfclib.idl:
    Oicf, W1, Zp8, env=Win32 (32b run)
    protocol : dce , ms_ext, c_ext, robust
    error checks: allocation ref bounds_check enum stub_data 
    VC __declspec() decoration level: 
         __declspec(uuid()), __declspec(selectany), __declspec(novtable)
         DECLSPEC_UUID(), MIDL_INTERFACE()
*/
//@@MIDL_FILE_HEADING(  )

#pragma warning( disable: 4049 )  /* more than 64k source lines */


/* verify that the <rpcndr.h> version is high enough to compile this file*/
#ifndef __REQUIRED_RPCNDR_H_VERSION__
#define __REQUIRED_RPCNDR_H_VERSION__ 475
#endif

#include "rpc.h"
#include "rpcndr.h"

#ifndef __RPCNDR_H_VERSION__
#error this stub requires an updated version of <rpcndr.h>
#endif // __RPCNDR_H_VERSION__

#ifndef COM_NO_WINDOWS_H
#include "windows.h"
#include "ole2.h"
#endif /*COM_NO_WINDOWS_H*/

#ifndef __pymfclib_i_h__
#define __pymfclib_i_h__

#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

/* Forward Declarations */ 

#ifndef __IPyMFC_CustomProtocol_FWD_DEFINED__
#define __IPyMFC_CustomProtocol_FWD_DEFINED__
typedef interface IPyMFC_CustomProtocol IPyMFC_CustomProtocol;
#endif 	/* __IPyMFC_CustomProtocol_FWD_DEFINED__ */


#ifndef __PyMFC_CustomProtocol_FWD_DEFINED__
#define __PyMFC_CustomProtocol_FWD_DEFINED__

#ifdef __cplusplus
typedef class PyMFC_CustomProtocol PyMFC_CustomProtocol;
#else
typedef struct PyMFC_CustomProtocol PyMFC_CustomProtocol;
#endif /* __cplusplus */

#endif 	/* __PyMFC_CustomProtocol_FWD_DEFINED__ */


/* header files for imported files */
#include "oaidl.h"
#include "ocidl.h"

#ifdef __cplusplus
extern "C"{
#endif 


#ifndef __IPyMFC_CustomProtocol_INTERFACE_DEFINED__
#define __IPyMFC_CustomProtocol_INTERFACE_DEFINED__

/* interface IPyMFC_CustomProtocol */
/* [unique][helpstring][uuid][object] */ 


EXTERN_C const IID IID_IPyMFC_CustomProtocol;

#if defined(__cplusplus) && !defined(CINTERFACE)
    
    MIDL_INTERFACE("2B4CE3D9-C71E-49A2-83B5-13900F624327")
    IPyMFC_CustomProtocol : public IUnknown
    {
    public:
    };
    
#else 	/* C style interface */

    typedef struct IPyMFC_CustomProtocolVtbl
    {
        BEGIN_INTERFACE
        
        HRESULT ( STDMETHODCALLTYPE *QueryInterface )( 
            IPyMFC_CustomProtocol * This,
            /* [in] */ REFIID riid,
            /* [iid_is][out] */ 
            __RPC__deref_out  void **ppvObject);
        
        ULONG ( STDMETHODCALLTYPE *AddRef )( 
            IPyMFC_CustomProtocol * This);
        
        ULONG ( STDMETHODCALLTYPE *Release )( 
            IPyMFC_CustomProtocol * This);
        
        END_INTERFACE
    } IPyMFC_CustomProtocolVtbl;

    interface IPyMFC_CustomProtocol
    {
        CONST_VTBL struct IPyMFC_CustomProtocolVtbl *lpVtbl;
    };

    

#ifdef COBJMACROS


#define IPyMFC_CustomProtocol_QueryInterface(This,riid,ppvObject)	\
    ( (This)->lpVtbl -> QueryInterface(This,riid,ppvObject) ) 

#define IPyMFC_CustomProtocol_AddRef(This)	\
    ( (This)->lpVtbl -> AddRef(This) ) 

#define IPyMFC_CustomProtocol_Release(This)	\
    ( (This)->lpVtbl -> Release(This) ) 


#endif /* COBJMACROS */


#endif 	/* C style interface */




#endif 	/* __IPyMFC_CustomProtocol_INTERFACE_DEFINED__ */



#ifndef __pymfclibLib_LIBRARY_DEFINED__
#define __pymfclibLib_LIBRARY_DEFINED__

/* library pymfclibLib */
/* [helpstring][version][uuid] */ 


EXTERN_C const IID LIBID_pymfclibLib;

EXTERN_C const CLSID CLSID_PyMFC_CustomProtocol;

#ifdef __cplusplus

class DECLSPEC_UUID("3B507234-6A52-4FAC-8664-3C3D76C1C13E")
PyMFC_CustomProtocol;
#endif
#endif /* __pymfclibLib_LIBRARY_DEFINED__ */

/* Additional Prototypes for ALL interfaces */

/* end of Additional Prototypes */

#ifdef __cplusplus
}
#endif

#endif


