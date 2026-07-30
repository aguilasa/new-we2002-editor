#if !defined(AFX_CARATTDLG_H__9DFA2EC1_9713_11D6_9298_ED1FD355C71E__INCLUDED_)
#define AFX_CARATTDLG_H__9DFA2EC1_9713_11D6_9298_ED1FD355C71E__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000
// carattDlg.h : header file
//
#include "giocatore.h"
/////////////////////////////////////////////////////////////////////////////
// carattDlg dialog

class carattDlg : public CDialog
{
// Construction
public:
	void exitCMB(CComboBox *cmb,int *q);
	void exitTXT(CEdit *txt,int *q);
	void carica();
	carattDlg(CWnd* pParent = NULL);   // standard constructor

	giocatore *auxgioc;
	fifa_player *auxfifapl;
	int id_giocatore;

// Dialog Data
	//{{AFX_DATA(carattDlg)
	enum { IDD = DLG_CARATT };
	CEdit	txt_numero;
	CEdit	txt_eta;
	CEdit	txt_altz;
	CEdit	txt_vel;
	CEdit	txt_tes;
	CEdit	txt_tec;
	CEdit	txt_rif;
	CEdit	txt_res;
	CEdit	txt_pz_tiro;
	CEdit	txt_pr_tiro;
	CEdit	txt_pass;
	CEdit	txt_nome;
	CEdit	txt_frz;
	CEdit	txt_ele;
	CEdit	txt_eff;
	CEdit	txt_dri;
	CEdit	txt_dif;
	CEdit	txt_costo;
	CEdit	txt_att;
	CEdit	txt_agg;
	CEdit	txt_acc;
	CComboBox	cmb_scarpe;
	CComboBox	cmb_ruolo;
	CComboBox	cmb_piede;
	CComboBox	cmb_pelle;
	CComboBox	cmb_fuori_ruolo;
	CComboBox	cmb_corporatura;
	CComboBox	cmb_capelli_stile;
	CComboBox	cmb_capelli_col;
	CComboBox	cmb_barba_stile;
	CComboBox	cmb_barba_col;
	CButton		cmd_import_url;
	//}}AFX_DATA


// Overrides
	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(carattDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:

	// Generated message map functions
	//{{AFX_MSG(carattDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnKillfocusAltezza();
	afx_msg void OnKillfocusEta();
	afx_msg void OnKillfocusGacc();
	afx_msg void OnKillfocusGaggr();
	afx_msg void OnKillfocusGatt();
	afx_msg void OnKillfocusGcosto();
	afx_msg void OnKillfocusGdif();
	afx_msg void OnKillfocusGdrib();
	afx_msg void OnKillfocusGeff();
	afx_msg void OnKillfocusGele();
	afx_msg void OnKillfocusGfzf();
	afx_msg void OnKillfocusGnome();
	afx_msg void OnKillfocusGpass();
	afx_msg void OnKillfocusGpret();
	afx_msg void OnKillfocusGpzt();
	afx_msg void OnKillfocusGres();
	afx_msg void OnKillfocusGrifl();
	afx_msg void OnKillfocusGtecn();
	afx_msg void OnKillfocusGtest();
	afx_msg void OnKillfocusGvel();
	afx_msg void OnKillfocusGbarbacol();
	afx_msg void OnKillfocusGbarbastile();
	afx_msg void OnKillfocusGcapcol();
	afx_msg void OnKillfocusGcapstile();
	afx_msg void OnKillfocusGcorpo();
	afx_msg void OnKillfocusGfruolo();
	afx_msg void OnKillfocusGpelle();
	afx_msg void OnKillfocusGpiede();
	afx_msg void OnKillfocusGruolo();
	afx_msg void OnKillfocusGscarpe();
	afx_msg void OnKillfocusGnumero();
	afx_msg void OnClickReadSingleURL();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_CARATTDLG_H__9DFA2EC1_9713_11D6_9298_ED1FD355C71E__INCLUDED_)
