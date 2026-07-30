// ed.h : main header file for the ED application
//

#if !defined(AFX_ED_H__C19753E8_8B46_11D6_9298_D487BCB91A01__INCLUDED_)
#define AFX_ED_H__C19753E8_8B46_11D6_9298_D487BCB91A01__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#ifndef __AFXWIN_H__
	#error include 'stdafx.h' before including this file for PCH
#endif

#include "resource.h"		// main symbols

/////////////////////////////////////////////////////////////////////////////
// CEdApp:
// See ed.cpp for the implementation of this class
//

class CEdApp : public CWinApp
{
public:
	CEdApp();

// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CEdApp)
	public:
	virtual BOOL InitInstance();
	//}}AFX_VIRTUAL

// Implementation

	//{{AFX_MSG(CEdApp)
		// NOTE - the ClassWizard will add and remove member functions here.
		//    DO NOT EDIT what you see in these blocks of generated code !
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};


/////////////////////////////////////////////////////////////////////////////

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_ED_H__C19753E8_8B46_11D6_9298_D487BCB91A01__INCLUDED_)
