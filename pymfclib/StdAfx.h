// Copyright (c) 2001- Atsuo Ishimoto
// See LICENSE for details.

// stdafx.h : �W���̃V�X�e�� �C���N���[�h �t�@�C���A
//            �܂��͎Q�Ɖ񐔂������A�����܂�ύX����Ȃ�
//            �v���W�F�N�g��p�̃C���N���[�h �t�@�C�����L�q���܂��B
//

#if !defined(AFX_STDAFX_H__6784D2C0_56FA_4042_B84B_986299C23A43__INCLUDED_)
#define _ATL_APARTMENT_THREADED 
#define AFX_STDAFX_H__6784D2C0_56FA_4042_B84B_986299C23A43__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

//#define VC_EXTRALEAN		// Windows �w�b�_�[����w�ǎg�p����Ȃ��X�^�b�t�����O���܂��B

#include <afxwin.h>         // MFC �̃R�A����ѕW���R���|�[�l���g
#include <afxext.h>         // MFC �̊g������

#ifndef _AFX_NO_OLE_SUPPORT
#include <afxole.h>         // MFC �� OLE �N���X
#include <afxodlgs.h>       // MFC �� OLE �_�C�A���O �N���X
#include <afxdisp.h>        // MFC �̃I�[�g���[�V���� �N���X
#endif // _AFX_NO_OLE_SUPPORT


#ifndef _AFX_NO_DB_SUPPORT
#include <afxdb.h>			// MFC ODBC �f�[�^�x�[�X �N���X
#endif // _AFX_NO_DB_SUPPORT

#ifndef _AFX_NO_DAO_SUPPORT
#include <afxdao.h>			// MFC DAO �f�[�^�x�[�X �N���X
#endif // _AFX_NO_DAO_SUPPORT

#include <afxdtctl.h>		// MFC �� Internet Explorer 4 �R���� �R���g���[�� �T�|�[�g
#ifndef _AFX_NO_AFXCMN_SUPPORT
#include <afxcmn.h>			// MFC �� Windows �R���� �R���g���[�� �T�|�[�g
#endif // _AFX_NO_AFXCMN_SUPPORT

#include <imm.h>
#include <mmsystem.h>
#include <comdef.h>
#include <commdlg.h>
#include <WinInet.h>
#include <commctrl.h> 
#include <exdispid.h>
#include <python.h>
#include <structmember.h>

#include <afxctl.h>

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ �͑O�s�̒��O�ɒǉ��̐錾��}�����܂��B




#include <atlbase.h>
#include <atlcom.h>
#include <atlctl.h>
#include <atlcoll.h>
#endif // !defined(AFX_STDAFX_H__6784D2C0_56FA_4042_B84B_986299C23A43__INCLUDED_)

