#if !defined(AFX_TATTDLG_H__DA982FE2_8BFA_11D6_9299_FB8FF6EB5F1B__INCLUDED_)
#define AFX_TATTDLG_H__DA982FE2_8BFA_11D6_9299_FB8FF6EB5F1B__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// tattDlg.h : header file
//

#include "tattica.h"
/////////////////////////////////////////////////////////////////////////////

class tattDlg : public CDialog
{
// Construction
public:
	void exitaty(CEdit *txt, int n);
	void exitatx(CEdit *txt, int n);
	void exitcmbtatt(CComboBox *cb, int n);
	void vtatt();
	tattica *ttt;
	tattDlg(CWnd* pParent = NULL);   // standard constructor
	void vtatt(CEdit *ttx, CEdit *tty, CButton *vt);
	void changecmbtatt(CComboBox *cb, CButton *bt);
// Dialog Data
	//{{AFX_DATA(tattDlg)
	enum { IDD = DLG_PTATTICHE };
	CEdit	txt_taty2;
	CEdit	txt_taty3;
	CEdit	txt_taty4;
	CEdit	txt_taty5;
	CEdit	txt_taty6;
	CEdit	txt_taty7;
	CEdit	txt_taty8;
	CEdit	txt_taty9;
	CEdit	txt_taty10;
	CEdit	txt_taty11;
	CEdit	txt_tatx2;
	CEdit	txt_tatx3;
	CEdit	txt_tatx4;
	CEdit	txt_tatx5;
	CEdit	txt_tatx6;
	CEdit	txt_tatx7;
	CEdit	txt_tatx8;
	CEdit	txt_tatx9;
	CEdit	txt_tatx10;
	CEdit	txt_tatx11;
	CEdit	txt_nome;
	CButton	cmd_vtat1;
	CButton	cmd_vtat2;
	CButton	cmd_vtat3;
	CButton	cmd_vtat4;
	CButton	cmd_vtat5;
	CButton	cmd_vtat6;
	CButton	cmd_vtat7;
	CButton	cmd_vtat8;
	CButton	cmd_vtat9;
	CButton	cmd_vtat10;
	CComboBox	cmb_tat2;
	CComboBox	cmb_tat3;
	CComboBox	cmb_tat4;
	CComboBox	cmb_tat5;
	CComboBox	cmb_tat6;
	CComboBox	cmb_tat7;
	CComboBox	cmb_tat8;
	CComboBox	cmb_tat9;
	CComboBox	cmb_tat10;
	CComboBox	cmb_tat11;
	CComboBox	cmb_seltatt;
	CButton	frm_campo;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(tattDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(tattDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnChnageSelTatt();
	afx_msg void OnSelchangeTat2();
	afx_msg void OnSelchangeTat3();
	afx_msg void OnSelchangeTat4();
	afx_msg void OnSelchangeTat5();
	afx_msg void OnSelchangeTat6();
	afx_msg void OnSelchangeTat7();
	afx_msg void OnSelchangeTat8();
	afx_msg void OnSelchangeTat9();
	afx_msg void OnSelchangeTat10();
	afx_msg void OnSelchangeTat11();
	afx_msg void OnKillfocusNometattica();
	afx_msg void OnChangeTatx2();
	afx_msg void OnChangeTatx3();
	afx_msg void OnChangeTatx4();
	afx_msg void OnChangeTatx5();
	afx_msg void OnChangeTatx6();
	afx_msg void OnChangeTatx7();
	afx_msg void OnChangeTatx8();
	afx_msg void OnChangeTatx9();
	afx_msg void OnChangeTatx10();
	afx_msg void OnChangeTatx11();
	afx_msg void OnChangeTaty2();
	afx_msg void OnChangeTaty3();
	afx_msg void OnChangeTaty4();
	afx_msg void OnChangeTaty5();
	afx_msg void OnChangeTaty6();
	afx_msg void OnChangeTaty7();
	afx_msg void OnChangeTaty8();
	afx_msg void OnChangeTaty9();
	afx_msg void OnChangeTaty10();
	afx_msg void OnChangeTaty11();
	afx_msg void OnKillfocusTat2();
	afx_msg void OnKillfocusTat3();
	afx_msg void OnKillfocusTat4();
	afx_msg void OnKillfocusTat5();
	afx_msg void OnKillfocusTat6();
	afx_msg void OnKillfocusTat7();
	afx_msg void OnKillfocusTat8();
	afx_msg void OnKillfocusTat9();
	afx_msg void OnKillfocusTat10();
	afx_msg void OnKillfocusTat11();
	afx_msg void OnKillfocusTatx2();
	afx_msg void OnKillfocusTatx3();
	afx_msg void OnKillfocusTatx4();
	afx_msg void OnKillfocusTatx5();
	afx_msg void OnKillfocusTatx6();
	afx_msg void OnKillfocusTatx7();
	afx_msg void OnKillfocusTatx8();
	afx_msg void OnKillfocusTatx9();
	afx_msg void OnKillfocusTatx10();
	afx_msg void OnKillfocusTatx11();
	afx_msg void OnKillfocusTaty2();
	afx_msg void OnKillfocusTaty3();
	afx_msg void OnKillfocusTaty4();
	afx_msg void OnKillfocusTaty5();
	afx_msg void OnKillfocusTaty6();
	afx_msg void OnKillfocusTaty7();
	afx_msg void OnKillfocusTaty8();
	afx_msg void OnKillfocusTaty9();
	afx_msg void OnKillfocusTaty10();
	afx_msg void OnKillfocusTaty11();
	afx_msg void OnImporta();
	afx_msg void OnEsporta();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_TATTDLG_H__DA982FE2_8BFA_11D6_9299_FB8FF6EB5F1B__INCLUDED_)
