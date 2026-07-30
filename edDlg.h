#include <string>
#include "giocatore.h"
using namespace std;
// edDlg.h : header file
//

#if !defined(AFX_EDDLG_H__C19753EA_8B46_11D6_9298_D487BCB91A01__INCLUDED_)
#define AFX_EDDLG_H__C19753EA_8B46_11D6_9298_D487BCB91A01__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CEdDlgAutoProxy;

/////////////////////////////////////////////////////////////////////////////
// CEdDlg dialog

class CEdDlg : public CDialog
{
	DECLARE_DYNAMIC(CEdDlg);
	friend class CEdDlgAutoProxy;

// Construction
public:
	void aggiornaNtatt();
	void nomiallstar();
	void sostituzione(int k);
	void caratteristiche(int id);
	void applica_tatt(int k);
	void muovitattica(float auxx,float auxy,int *rx,int *ry);
	void carica_dabin();
	void carica_url();
	BOOL aprifilebin(char *filtro);
	CEdDlg(CWnd* pParent = NULL);	// standard constructor
	virtual ~CEdDlg();

// Dialog Data
	//{{AFX_DATA(CEdDlg)
	enum { IDD = IDD_ED_DIALOG };
	CButton	cmd_nometat9;
	CButton	cmd_nometat8;
	CButton	cmd_nometat7;
	CButton	cmd_nometat6;
	CButton	cmd_nometat5;
	CButton	cmd_nometat4;
	CButton	cmd_nometat3;
	CButton	cmd_nometat2;
	CButton	cmd_nometat16;
	CButton	cmd_nometat15;
	CButton	cmd_nometat14;
	CButton	cmd_nometat13;
	CButton	cmd_nometat12;
	CButton	cmd_nometat11;
	CButton	cmd_nometat10;
	CButton	cmd_nometat1;
	CStatic	lbl_nome_squadk;
	CEdit	txt_nome_squadk;
	CEdit	txt_nome_squad_a3;
	CComboBox	cmb_kik_rig;
	CStatic	lbl_nome_add2;
	CStatic	lbl_nome_add1;
	CEdit	txt_nomi_addml2;
	CEdit	txt_nomi_addml1;
	CStatic	lbl_nomi_addml;
	CEdit	txt_taty11;
	CEdit	txt_tatx11;
	CEdit	txt_gioc9;
	CEdit	txt_gioc8;
	CEdit	txt_gioc7;
	CEdit	txt_gioc6;
	CEdit	txt_gioc5;
	CEdit	txt_gioc4;
	CEdit	txt_gioc3;
	CEdit	txt_gioc23;
	CEdit	txt_gioc22;
	CEdit	txt_gioc21;
	CEdit	txt_gioc20;
	CEdit	txt_gioc2;
	CEdit	txt_gioc19;
	CEdit	txt_gioc18;
	CEdit	txt_gioc17;
	CEdit	txt_gioc16;
	CEdit	txt_gioc15;
	CEdit	txt_gioc14;
	CEdit	txt_gioc13;
	CEdit	txt_gioc12;
	CEdit	txt_gioc11;
	CEdit	txt_gioc10;
	CEdit	txt_gioc1;
	//urls
	CEdit	txt_url_gioc1;
	CEdit	txt_url_gioc2;
	CEdit	txt_url_gioc3;
	CEdit	txt_url_gioc4;
	CEdit	txt_url_gioc5;
	CEdit	txt_url_gioc6;
	CEdit	txt_url_gioc7;
	CEdit	txt_url_gioc8;
	CEdit	txt_url_gioc9;
	CEdit	txt_url_gioc10;
	CEdit	txt_url_gioc11;
	CEdit	txt_url_gioc12;
	CEdit	txt_url_gioc13;
	CEdit	txt_url_gioc14;
	CEdit	txt_url_gioc15;
	CEdit	txt_url_gioc16;
	CEdit	txt_url_gioc17;
	CEdit	txt_url_gioc18;
	CEdit	txt_url_gioc19;
	CEdit	txt_url_gioc20;
	CEdit	txt_url_gioc21;
	CEdit	txt_url_gioc22;
	CEdit	txt_url_gioc23;
	//end urls
	CEdit	txt_num_gioc9;
	CEdit	txt_num_gioc8;
	CEdit	txt_num_gioc7;
	CEdit	txt_num_gioc6;
	CEdit	txt_num_gioc5;
	CEdit	txt_num_gioc4;
	CEdit	txt_num_gioc3;
	CEdit	txt_num_gioc23;
	CEdit	txt_num_gioc22;
	CEdit	txt_num_gioc21;
	CEdit	txt_num_gioc20;
	CEdit	txt_num_gioc2;
	CEdit	txt_num_gioc19;
	CEdit	txt_num_gioc18;
	CEdit	txt_num_gioc17;
	CEdit	txt_num_gioc16;
	CEdit	txt_num_gioc15;
	CEdit	txt_num_gioc14;
	CEdit	txt_num_gioc13;
	CEdit	txt_num_gioc12;
	CEdit	txt_num_gioc11;
	CEdit	txt_num_gioc10;
	CEdit	txt_num_gioc1;
	CEdit	txt_taty9;
	CEdit	txt_taty8;
	CEdit	txt_taty7;
	CEdit	txt_taty6;
	CEdit	txt_taty5;
	CEdit	txt_taty4;
	CEdit	txt_taty3;
	CEdit	txt_taty2;
	CEdit	txt_taty10;
	CEdit	txt_tatx9;
	CEdit	txt_tatx8;
	CEdit	txt_tatx7;
	CEdit	txt_tatx6;
	CEdit	txt_tatx5;
	CEdit	txt_tatx4;
	CEdit	txt_tatx3;
	CEdit	txt_tatx2;
	CEdit	txt_tatx10;
	CEdit	txt_nome_squad6;
	CEdit	txt_nome_squad5;
	CEdit	txt_nome_squad4;
	CEdit	txt_nome_squad3;
	CEdit	txt_nome_squad2;
	CEdit	txt_nome_squad1;
	CEdit	txt_nome_squad_m;
	CEdit	txt_nome_squad_a2;
	CEdit	txt_nome_squad_a1;
	CEdit	txt_bar_tec;
	CEdit	txt_bar_spe;
	CEdit	txt_bar_pow;
	CEdit	txt_bar_off;
	CEdit	txt_bar_def;
	CStatic	lab_nome_squad6;
	CStatic	lab_nome_squad5;
	CStatic	lab_nome_squad4;
	CStatic	lab_nome_squad3;
	CStatic	lab_nome_squad2;
	CStatic	lab_nome_squad1;
	CStatic	lab_nome_squad_m;
	CStatic	lab_nome_squad_a2;
	CStatic	lab_nome_squad_a1;
	CButton	cmd_visual_tat9;
	CButton	cmd_visual_tat8;
	CButton	cmd_visual_tat7;
	CButton	cmd_visual_tat6;
	CButton	cmd_visual_tat5;
	CButton	cmd_visual_tat4;
	CButton	cmd_visual_tat3;
	CButton	cmd_visual_tat2;
	CButton	cmd_visual_tat10;
	CButton	cmd_visual_tat1;
	CButton	cmb_sost9;
	CButton	cmb_sost8;
	CButton	cmb_sost7;
	CButton	cmb_sost6;
	CButton	cmb_sost5;
	CButton	cmb_sost4;
	CButton	cmb_sost3;
	CButton	cmb_sost23;
	CButton	cmb_sost22;
	CButton	cmb_sost21;
	CButton	cmb_sost20;
	CButton	cmb_sost2;
	CButton	cmb_sost19;
	CButton	cmb_sost18;
	CButton	cmb_sost17;
	CButton	cmb_sost16;
	CButton	cmb_sost15;
	CButton	cmb_sost14;
	CButton	cmb_sost13;
	CButton	cmb_sost12;
	CButton	cmb_sost11;
	CButton	cmb_sost10;
	CButton	cmb_sost1;
	CComboBox	cmb_tat7;
	CComboBox	cmb_tat9;
	CComboBox	cmb_tat8;
	CComboBox	cmb_tat6;
	CComboBox	cmb_tat5;
	CComboBox	cmb_tat4;
	CComboBox	cmb_tat3;
	CComboBox	cmb_tat2;
	CComboBox	cmb_tat10;
	CComboBox	cmb_tat11;
	CComboBox	cmb_squadra;
	CComboBox	cmb_kik_punl;
	CComboBox	cmb_kik_punc;
	CComboBox	cmb_kik_cap;
	CComboBox	cmb_kik_angsx;
	CComboBox	cmb_kik_angdx;
	CComboBox	cmb_band_stile;
	CButton	frm_tat_campo;
	//}}AFX_DATA
  // ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CEdDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	CEdDlgAutoProxy* m_pAutoProxy;
	HICON m_hIcon;

	BOOL CanExit();

	// Generated message map functions
	//{{AFX_MSG(CEdDlg)
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg void OnClose();
	virtual void OnOK();
	virtual void OnCancel();
	afx_msg void OnCancelMode();
	afx_msg void OnSelezioneSquadraV();
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
	afx_msg void OnChangeURL1();
	afx_msg void OnChangeURL2();
	afx_msg void OnChangeURL3();
	afx_msg void OnChangeURL4();
	afx_msg void OnChangeURL5();
	afx_msg void OnChangeURL6();
	afx_msg void OnChangeURL7();
	afx_msg void OnChangeURL8();
	afx_msg void OnChangeURL9();
	afx_msg void OnChangeURL10();
	afx_msg void OnChangeURL11();
	afx_msg void OnChangeURL12();
	afx_msg void OnChangeURL13();
	afx_msg void OnChangeURL14();
	afx_msg void OnChangeURL15();
	afx_msg void OnChangeURL16();
	afx_msg void OnChangeURL17();
	afx_msg void OnChangeURL18();
	afx_msg void OnChangeURL19();
	afx_msg void OnChangeURL20();
	afx_msg void OnChangeURL21();
	afx_msg void OnChangeURL22();
	afx_msg void OnChangeURL23();
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
	afx_msg void OnKillfocusTaty10();
	afx_msg void OnKillfocusTaty11();
	afx_msg void OnKillfocusTaty2();
	afx_msg void OnKillfocusTaty3();
	afx_msg void OnKillfocusTaty4();
	afx_msg void OnKillfocusTaty5();
	afx_msg void OnKillfocusTaty6();
	afx_msg void OnKillfocusTaty7();
	afx_msg void OnKillfocusTaty8();
	afx_msg void OnKillfocusTaty9();
	afx_msg void On451a();
	afx_msg void On451b();
	afx_msg void On442a();
	afx_msg void On442b();
	afx_msg void On433a();
	afx_msg void On433b();
	afx_msg void On361a();
	afx_msg void On361b();
	afx_msg void On352a();
	afx_msg void On352b();
	afx_msg void On343a();
	afx_msg void On343b();
	afx_msg void On541a();
	afx_msg void On541b();
	afx_msg void On532a();
	afx_msg void On532b();
	afx_msg void OnCopiaNomisquadra();
	afx_msg void OnWriteCD();
	afx_msg void OnImportSoFIFAWeb();
	afx_msg void OnImportSoFIFATxt();
	afx_msg void OnEditAllFromFIFA();
	afx_msg void OnEditOptForm();
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
	afx_msg void OnKillfocusNsquad1();
	afx_msg void OnKillfocusNsquad2();
	afx_msg void OnKillfocusNsquad3();
	afx_msg void OnKillfocusNsquad4();
	afx_msg void OnKillfocusNsquad5();
	afx_msg void OnKillfocusNsquad6();
	afx_msg void OnKillfocusNsquadM();
	afx_msg void OnKillfocusNsquadA1();
	afx_msg void OnKillfocusNsquadA2();
	afx_msg void OnKillfocusNomiml1();
	afx_msg void OnKillfocusNomiml2();
	afx_msg void OnKillfocusBarOff();
	afx_msg void OnKillfocusBarDef();
	afx_msg void OnKillfocusBarPow();
	afx_msg void OnKillfocusBarSpe();
	afx_msg void OnKillfocusBarTec();
	afx_msg void OnKillfocusKikPunl();
	afx_msg void OnKillfocusKikPunc();
	afx_msg void OnKillfocusKikCap();
	afx_msg void OnKillfocusKikAngsx();
	afx_msg void OnKillfocusKikAngdx();
	afx_msg void OnKillfocusKikRig();
	afx_msg void OnKillfocusNsquadA3();
	afx_msg void OnKillfocusNum1();
	afx_msg void OnKillfocusNum2();
	afx_msg void OnKillfocusNum3();
	afx_msg void OnKillfocusNum4();
	afx_msg void OnKillfocusNum5();
	afx_msg void OnKillfocusNum6();
	afx_msg void OnKillfocusNum7();
	afx_msg void OnKillfocusNum8();
	afx_msg void OnKillfocusNum9();
	afx_msg void OnKillfocusNum10();
	afx_msg void OnKillfocusNum11();
	afx_msg void OnKillfocusNum12();
	afx_msg void OnKillfocusNum13();
	afx_msg void OnKillfocusNum14();
	afx_msg void OnKillfocusNum15();
	afx_msg void OnKillfocusNum16();
	afx_msg void OnKillfocusNum17();
	afx_msg void OnKillfocusNum18();
	afx_msg void OnKillfocusNum19();
	afx_msg void OnKillfocusNum20();
	afx_msg void OnKillfocusNum21();
	afx_msg void OnKillfocusNum22();
	afx_msg void OnKillfocusNum23();
	afx_msg void OnCarat1();
	afx_msg void OnCarat2();
	afx_msg void OnCarat3();
	afx_msg void OnCarat4();
	afx_msg void OnCarat5();
	afx_msg void OnCarat6();
	afx_msg void OnCarat7();
	afx_msg void OnCarat8();
	afx_msg void OnCarat9();
	afx_msg void OnCarat10();
	afx_msg void OnCarat11();
	afx_msg void OnCarat12();
	afx_msg void OnCarat13();
	afx_msg void OnCarat14();
	afx_msg void OnCarat15();
	afx_msg void OnCarat16();
	afx_msg void OnCarat17();
	afx_msg void OnCarat18();
	afx_msg void OnCarat19();
	afx_msg void OnCarat20();
	afx_msg void OnCarat21();
	afx_msg void OnCarat22();
	afx_msg void OnCarat23();
	afx_msg void OnSost1();
	afx_msg void OnSost2();
	afx_msg void OnSost3();
	afx_msg void OnSost4();
	afx_msg void OnSost5();
	afx_msg void OnSost6();
	afx_msg void OnSost7();
	afx_msg void OnSost8();
	afx_msg void OnSost9();
	afx_msg void OnSost10();
	afx_msg void OnSost11();
	afx_msg void OnSost12();
	afx_msg void OnSost13();
	afx_msg void OnSost14();
	afx_msg void OnSost15();
	afx_msg void OnSost16();
	afx_msg void OnSost17();
	afx_msg void OnSost18();
	afx_msg void OnSost19();
	afx_msg void OnSost20();
	afx_msg void OnSost21();
	afx_msg void OnSost22();
	afx_msg void OnSost23();
	afx_msg void OnEsporta();
	afx_msg void OnImporta();
	afx_msg void OnKillfocusNsquadk();
	afx_msg void OnButtgraf();
	afx_msg void OnNumeriDefault();
	afx_msg void OnReload();
	afx_msg void OnCalcolaCostiML();
	afx_msg void OnOrdinaPanchina();
	afx_msg void OnImportaTot();
	afx_msg void OnEsportaTot();
	afx_msg void OnTattPredef();
	afx_msg void carica_SOFIFAFields();
	afx_msg void carica_SOFIFAConversionRules();
	afx_msg void OnEditAllPlayersLook();
	afx_msg void OnEditAllBars();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

int getWEPositionFromFifaPosition(string fpos);
int getValue(string attr, fifa_player fpl);
int CalcolaCostoGiocatore(int i);
int trovaIDml(unsigned char *lk);
void setPlayerNo(int pl, int natNo, int clubNo);

//{{AFX_INSERT_LOCATION}}
// Microsoft Visual C++ will insert additional declarations immediately before the previous line.

#endif // !defined(AFX_EDDLG_H__C19753EA_8B46_11D6_9298_D487BCB91A01__INCLUDED_)
