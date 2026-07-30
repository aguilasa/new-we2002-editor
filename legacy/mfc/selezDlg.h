#if !defined(AFX_SELEZDLG_H__9DFA2EC6_9713_11D6_9298_ED1FD355C71E__INCLUDED_)
#define AFX_SELEZDLG_H__9DFA2EC6_9713_11D6_9298_ED1FD355C71E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// selezDlg.h : header file
//
#include "giocatore.h"
#include "squadra_ml.h"
/////////////////////////////////////////////////////////////////////////////
// selezDlg dialog

class selezDlg : public CDialog
{
// Construction
public:
	void trovaLK(int id,unsigned char *lk);
	selezDlg(CWnd* pParent = NULL);   // standard constructor

	int id_giocatore;
	int pos;
	BOOL ml;
	giocatore *auxgioc;
	squadra_ml *auxml;
// Dialog Data
	//{{AFX_DATA(selezDlg)
	enum { IDD = DLG_SELECT_GIOC };
	CStatic	lbl_nazion;
	CComboBox	cmb_nazion;
	CButton	chk_ndef;
	CButton	chk_lkdef;
	CStatic	lbl_nazml;
	CButton	chk_ml;
	CButton	chk_sc;
	CListBox	lst_squadre;
	CListBox	lst_giocatori;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(selezDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(selezDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSelchangeSquadre();
	afx_msg void OnSelchangeGiocatori();
	afx_msg void OnDblclkGiocatori();
	afx_msg void OnMl();
	afx_msg void OnSc();
	afx_msg void OnLkDef();
	afx_msg void OnLkNdef();
	afx_msg void OnOOKK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_SELEZDLG_H__9DFA2EC6_9713_11D6_9298_ED1FD355C71E__INCLUDED_)
