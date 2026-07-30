// tattDlg.cpp : implementation file
//

#include "stdafx.h"
#include "ed.h"
#include "tattDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

#define TBTW 38
#define TBTH 16
//tattiche
#define TTXMAX 48
#define TTXMIN 0
#define TTYMAX 112
#define TTYMIN 0
#define TTCORRX -8
#define TTCORRY 6

char nruoli[21][6]=
{
"GK","CB SX","CB CN","SW","LIB","CB DX","LB","RB",
"DH SX","DH CN","DH DX","LH","RH","OH SX","OH CN","OH DX",
"CF SX","CF CN","CF DX","LW","RW"
};

/////////////////////////////////////////////////////////////////////////////
// tattDlg dialog


tattDlg::tattDlg(CWnd* pParent /*=NULL*/)
	: CDialog(tattDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(tattDlg)
	//}}AFX_DATA_INIT
}


void tattDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(tattDlg)
	DDX_Control(pDX, TTXT_NOMETATTICA, txt_nome);
	DDX_Control(pDX, TCMB_NSQUADRE, cmb_seltatt);
	DDX_Control(pDX, TCAMPO_, frm_campo);
	DDX_Control(pDX, TTXT_TATY2, txt_taty2);
	DDX_Control(pDX, TTXT_TATY3, txt_taty3);
	DDX_Control(pDX, TTXT_TATY4, txt_taty4);
	DDX_Control(pDX, TTXT_TATY5, txt_taty5);
	DDX_Control(pDX, TTXT_TATY6, txt_taty6);
	DDX_Control(pDX, TTXT_TATY7, txt_taty7);
	DDX_Control(pDX, TTXT_TATY8, txt_taty8);
	DDX_Control(pDX, TTXT_TATY9, txt_taty9);
	DDX_Control(pDX, TTXT_TATY10, txt_taty10);
	DDX_Control(pDX, TTXT_TATY11, txt_taty11);
	DDX_Control(pDX, TTXT_TATX2, txt_tatx2);
	DDX_Control(pDX, TTXT_TATX3, txt_tatx3);
	DDX_Control(pDX, TTXT_TATX4, txt_tatx4);
	DDX_Control(pDX, TTXT_TATX5, txt_tatx5);
	DDX_Control(pDX, TTXT_TATX6, txt_tatx6);
	DDX_Control(pDX, TTXT_TATX7, txt_tatx7);
	DDX_Control(pDX, TTXT_TATX8, txt_tatx8);
	DDX_Control(pDX, TTXT_TATX9, txt_tatx9);
	DDX_Control(pDX, TTXT_TATX10, txt_tatx10);
	DDX_Control(pDX, TTXT_TATX11, txt_tatx11);
	DDX_Control(pDX, TCMD_VT1, cmd_vtat1);
	DDX_Control(pDX, TCMD_VT2, cmd_vtat2);
	DDX_Control(pDX, TCMD_VT3, cmd_vtat3);
	DDX_Control(pDX, TCMD_VT4, cmd_vtat4);
	DDX_Control(pDX, TCMD_VT5, cmd_vtat5);
	DDX_Control(pDX, TCMD_VT6, cmd_vtat6);
	DDX_Control(pDX, TCMD_VT7, cmd_vtat7);
	DDX_Control(pDX, TCMD_VT8, cmd_vtat8);
	DDX_Control(pDX, TCMD_VT9, cmd_vtat9);
	DDX_Control(pDX, TCMD_VT10, cmd_vtat10);
	DDX_Control(pDX, TCMB_TAT9, cmb_tat9);
	DDX_Control(pDX, TCMB_TAT8, cmb_tat8);
	DDX_Control(pDX, TCMB_TAT7, cmb_tat7);
	DDX_Control(pDX, TCMB_TAT6, cmb_tat6);
	DDX_Control(pDX, TCMB_TAT5, cmb_tat5);
	DDX_Control(pDX, TCMB_TAT4, cmb_tat4);
	DDX_Control(pDX, TCMB_TAT3, cmb_tat3);
	DDX_Control(pDX, TCMB_TAT2, cmb_tat2);
	DDX_Control(pDX, TCMB_TAT11, cmb_tat11);
	DDX_Control(pDX, TCMB_TAT10, cmb_tat10);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(tattDlg, CDialog)
	//{{AFX_MSG_MAP(tattDlg)
	ON_CBN_SELCHANGE(TCMB_NSQUADRE, OnChnageSelTatt)
	ON_CBN_SELCHANGE(TCMB_TAT2, OnSelchangeTat2)
	ON_CBN_SELCHANGE(TCMB_TAT3, OnSelchangeTat3)
	ON_CBN_SELCHANGE(TCMB_TAT4, OnSelchangeTat4)
	ON_CBN_SELCHANGE(TCMB_TAT5, OnSelchangeTat5)
	ON_CBN_SELCHANGE(TCMB_TAT6, OnSelchangeTat6)
	ON_CBN_SELCHANGE(TCMB_TAT7, OnSelchangeTat7)
	ON_CBN_SELCHANGE(TCMB_TAT8, OnSelchangeTat8)
	ON_CBN_SELCHANGE(TCMB_TAT9, OnSelchangeTat9)
	ON_CBN_SELCHANGE(TCMB_TAT10, OnSelchangeTat10)
	ON_CBN_SELCHANGE(TCMB_TAT11, OnSelchangeTat11)
	ON_EN_KILLFOCUS(TTXT_NOMETATTICA, OnKillfocusNometattica)
	ON_EN_CHANGE(TTXT_TATX2, OnChangeTatx2)
	ON_EN_CHANGE(TTXT_TATX3, OnChangeTatx3)
	ON_EN_CHANGE(TTXT_TATX4, OnChangeTatx4)
	ON_EN_CHANGE(TTXT_TATX5, OnChangeTatx5)
	ON_EN_CHANGE(TTXT_TATX6, OnChangeTatx6)
	ON_EN_CHANGE(TTXT_TATX7, OnChangeTatx7)
	ON_EN_CHANGE(TTXT_TATX8, OnChangeTatx8)
	ON_EN_CHANGE(TTXT_TATX9, OnChangeTatx9)
	ON_EN_CHANGE(TTXT_TATX10, OnChangeTatx10)
	ON_EN_CHANGE(TTXT_TATX11, OnChangeTatx11)
	ON_EN_CHANGE(TTXT_TATY2, OnChangeTaty2)
	ON_EN_CHANGE(TTXT_TATY3, OnChangeTaty3)
	ON_EN_CHANGE(TTXT_TATY4, OnChangeTaty4)
	ON_EN_CHANGE(TTXT_TATY5, OnChangeTaty5)
	ON_EN_CHANGE(TTXT_TATY6, OnChangeTaty6)
	ON_EN_CHANGE(TTXT_TATY7, OnChangeTaty7)
	ON_EN_CHANGE(TTXT_TATY8, OnChangeTaty8)
	ON_EN_CHANGE(TTXT_TATY9, OnChangeTaty9)
	ON_EN_CHANGE(TTXT_TATY10, OnChangeTaty10)
	ON_EN_CHANGE(TTXT_TATY11, OnChangeTaty11)
	ON_CBN_KILLFOCUS(TCMB_TAT2, OnKillfocusTat2)
	ON_CBN_KILLFOCUS(TCMB_TAT3, OnKillfocusTat3)
	ON_CBN_KILLFOCUS(TCMB_TAT4, OnKillfocusTat4)
	ON_CBN_KILLFOCUS(TCMB_TAT5, OnKillfocusTat5)
	ON_CBN_KILLFOCUS(TCMB_TAT6, OnKillfocusTat6)
	ON_CBN_KILLFOCUS(TCMB_TAT7, OnKillfocusTat7)
	ON_CBN_KILLFOCUS(TCMB_TAT8, OnKillfocusTat8)
	ON_CBN_KILLFOCUS(TCMB_TAT9, OnKillfocusTat9)
	ON_CBN_KILLFOCUS(TCMB_TAT10, OnKillfocusTat10)
	ON_CBN_KILLFOCUS(TCMB_TAT11, OnKillfocusTat11)
	ON_EN_KILLFOCUS(TTXT_TATX2, OnKillfocusTatx2)
	ON_EN_KILLFOCUS(TTXT_TATX3, OnKillfocusTatx3)
	ON_EN_KILLFOCUS(TTXT_TATX4, OnKillfocusTatx4)
	ON_EN_KILLFOCUS(TTXT_TATX5, OnKillfocusTatx5)
	ON_EN_KILLFOCUS(TTXT_TATX6, OnKillfocusTatx6)
	ON_EN_KILLFOCUS(TTXT_TATX7, OnKillfocusTatx7)
	ON_EN_KILLFOCUS(TTXT_TATX8, OnKillfocusTatx8)
	ON_EN_KILLFOCUS(TTXT_TATX9, OnKillfocusTatx9)
	ON_EN_KILLFOCUS(TTXT_TATX10, OnKillfocusTatx10)
	ON_EN_KILLFOCUS(TTXT_TATX11, OnKillfocusTatx11)
	ON_EN_KILLFOCUS(TTXT_TATY2, OnKillfocusTaty2)
	ON_EN_KILLFOCUS(TTXT_TATY3, OnKillfocusTaty3)
	ON_EN_KILLFOCUS(TTXT_TATY4, OnKillfocusTaty4)
	ON_EN_KILLFOCUS(TTXT_TATY5, OnKillfocusTaty5)
	ON_EN_KILLFOCUS(TTXT_TATY6, OnKillfocusTaty6)
	ON_EN_KILLFOCUS(TTXT_TATY7, OnKillfocusTaty7)
	ON_EN_KILLFOCUS(TTXT_TATY8, OnKillfocusTaty8)
	ON_EN_KILLFOCUS(TTXT_TATY9, OnKillfocusTaty9)
	ON_EN_KILLFOCUS(TTXT_TATY10, OnKillfocusTaty10)
	ON_EN_KILLFOCUS(TTXT_TATY11, OnKillfocusTaty11)
	ON_BN_CLICKED(CMD_IMP, OnImporta)
	ON_BN_CLICKED(CMD_EXP, OnEsporta)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// tattDlg message handlers

BOOL tattDlg::OnInitDialog() 
{
	int i;
	CDialog::OnInitDialog();
	for(i=1;i<21;i++)
	{
		cmb_tat2.AddString(nruoli[i]);
		cmb_tat3.AddString(nruoli[i]);
		cmb_tat4.AddString(nruoli[i]);
		cmb_tat5.AddString(nruoli[i]);
		cmb_tat6.AddString(nruoli[i]);
		cmb_tat7.AddString(nruoli[i]);
		cmb_tat8.AddString(nruoli[i]);
		cmb_tat9.AddString(nruoli[i]);
		cmb_tat10.AddString(nruoli[i]);
		cmb_tat11.AddString(nruoli[i]);
	}

	for(i=0;i<16;i++)
		cmb_seltatt.AddString(ttt[i].nome);
	txt_nome.SetLimitText(6);

	txt_taty2.SetLimitText(3);
	txt_taty3.SetLimitText(3);
	txt_taty4.SetLimitText(3);
	txt_taty5.SetLimitText(3);
	txt_taty6.SetLimitText(3);
	txt_taty7.SetLimitText(3);
	txt_taty8.SetLimitText(3);
	txt_taty9.SetLimitText(3);
	txt_taty10.SetLimitText(3);
	txt_taty11.SetLimitText(3);
	txt_tatx2.SetLimitText(2);
	txt_tatx3.SetLimitText(2);
	txt_tatx4.SetLimitText(2);
	txt_tatx5.SetLimitText(2);
	txt_tatx6.SetLimitText(2);
	txt_tatx7.SetLimitText(2);
	txt_tatx8.SetLimitText(2);
	txt_tatx9.SetLimitText(2);
	txt_tatx10.SetLimitText(2);
	txt_tatx11.SetLimitText(2);
	
	cmb_seltatt.SetCurSel(0);
	tattDlg::OnChnageSelTatt();
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void tattDlg::vtatt(CEdit *ttx, CEdit *tty, CButton *vt)
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	int aax, aay;
	float pasx, pasy;
	WINDOWPLACEMENT pl;
	ttx->GetWindowText(str);
	auxx = float(atoi(str)-TTXMIN);
	tty->GetWindowText(str);
	auxy = float(atoi(str)-TTYMIN);
	aax = TTXMAX-TTXMIN;
	aay = TTYMAX-TTYMIN;
	frm_campo.GetWindowPlacement(&pl);
	pasx = float(pl.rcNormalPosition.right-pl.rcNormalPosition.left)/aax;
	pasy = float(pl.rcNormalPosition.bottom-pl.rcNormalPosition.top)/aay;
	ax = pl.rcNormalPosition.left+int(pasx*auxx)-TBTW/2+TTCORRX;
	ay = pl.rcNormalPosition.top+int(pasy*auxy)-TBTH/2+TTCORRY;
	vt->MoveWindow(ax,ay,TBTW,TBTH,TRUE);
}

void tattDlg::changecmbtatt(CComboBox *cb, CButton *bt)
{
	CString auxstr;
	cb->GetWindowText(auxstr);
	bt->SetWindowText(auxstr);
}

void tattDlg::OnChnageSelTatt() 
{
	char strint[10];
	int id = cmb_seltatt.GetCurSel();
	txt_nome.SetWindowText(ttt[id].nome);	
	cmb_tat2.SetCurSel(ttt[id].ruoli[1]-2);
	cmb_tat3.SetCurSel(ttt[id].ruoli[2]-2);
	cmb_tat4.SetCurSel(ttt[id].ruoli[3]-2);
	cmb_tat5.SetCurSel(ttt[id].ruoli[4]-2);
	cmb_tat6.SetCurSel(ttt[id].ruoli[5]-2);
	cmb_tat7.SetCurSel(ttt[id].ruoli[6]-2);
	cmb_tat8.SetCurSel(ttt[id].ruoli[7]-2);
	cmb_tat9.SetCurSel(ttt[id].ruoli[8]-2);
	cmb_tat10.SetCurSel(ttt[id].ruoli[9]-2);
	cmb_tat11.SetCurSel(ttt[id].ruoli[10]-2);
		//tatx
	_itoa(int(ttt[id].x[0]), strint, 10);
	txt_tatx2.SetWindowText(strint);
	_itoa(int(ttt[id].x[1]), strint, 10);
	txt_tatx3.SetWindowText(strint);
	_itoa(int(ttt[id].x[2]), strint, 10);
	txt_tatx4.SetWindowText(strint);
	_itoa(int(ttt[id].x[3]), strint, 10);
	txt_tatx5.SetWindowText(strint);
	_itoa(int(ttt[id].x[4]), strint, 10);
	txt_tatx6.SetWindowText(strint);
	_itoa(int(ttt[id].x[5]), strint, 10);
	txt_tatx7.SetWindowText(strint);
	_itoa(int(ttt[id].x[6]), strint, 10);
	txt_tatx8.SetWindowText(strint);
	_itoa(int(ttt[id].x[7]), strint, 10);
	txt_tatx9.SetWindowText(strint);
	_itoa(int(ttt[id].x[8]), strint, 10);
	txt_tatx10.SetWindowText(strint);
	_itoa(int(ttt[id].x[9]), strint, 10);
	txt_tatx11.SetWindowText(strint);
		//taty
	_itoa(int(ttt[id].y[0]), strint, 10);
	txt_taty2.SetWindowText(strint);
	_itoa(int(ttt[id].y[1]), strint, 10);
	txt_taty3.SetWindowText(strint);
	_itoa(int(ttt[id].y[2]), strint, 10);
	txt_taty4.SetWindowText(strint);
	_itoa(int(ttt[id].y[3]), strint, 10);
	txt_taty5.SetWindowText(strint);
	_itoa(int(ttt[id].y[4]), strint, 10);
	txt_taty6.SetWindowText(strint);
	_itoa(int(ttt[id].y[5]), strint, 10);
	txt_taty7.SetWindowText(strint);
	_itoa(int(ttt[id].y[6]), strint, 10);
	txt_taty8.SetWindowText(strint);
	_itoa(int(ttt[id].y[7]), strint, 10);
	txt_taty9.SetWindowText(strint);
	_itoa(int(ttt[id].y[8]), strint, 10);
	txt_taty10.SetWindowText(strint);
	_itoa(int(ttt[id].y[9]), strint, 10);
	txt_taty11.SetWindowText(strint);

	tattDlg::OnSelchangeTat2();
	tattDlg::OnSelchangeTat3();
	tattDlg::OnSelchangeTat4();
	tattDlg::OnSelchangeTat5();
	tattDlg::OnSelchangeTat6();
	tattDlg::OnSelchangeTat7();
	tattDlg::OnSelchangeTat8();
	tattDlg::OnSelchangeTat9();
	tattDlg::OnSelchangeTat10();
	tattDlg::OnSelchangeTat11();
}

void tattDlg::OnSelchangeTat2() 
{
	changecmbtatt(&cmb_tat2, &cmd_vtat1);
}

void tattDlg::OnSelchangeTat3() 
{
	changecmbtatt(&cmb_tat3, &cmd_vtat2);
}

void tattDlg::OnSelchangeTat4() 
{
	changecmbtatt(&cmb_tat4, &cmd_vtat3);
}

void tattDlg::OnSelchangeTat5() 
{
	changecmbtatt(&cmb_tat5, &cmd_vtat4);
}

void tattDlg::OnSelchangeTat6() 
{
	changecmbtatt(&cmb_tat6, &cmd_vtat5);
}

void tattDlg::OnSelchangeTat7() 
{
	changecmbtatt(&cmb_tat7, &cmd_vtat6);
}

void tattDlg::OnSelchangeTat8() 
{
	changecmbtatt(&cmb_tat8, &cmd_vtat7);
}

void tattDlg::OnSelchangeTat9() 
{
	changecmbtatt(&cmb_tat9, &cmd_vtat8);
}

void tattDlg::OnSelchangeTat10() 
{
	changecmbtatt(&cmb_tat10, &cmd_vtat9);
}

void tattDlg::OnSelchangeTat11() 
{
	changecmbtatt(&cmb_tat11, &cmd_vtat10);
}

void tattDlg::OnKillfocusNometattica() 
{
	int id = cmb_seltatt.GetCurSel();
	CString aux;
	txt_nome.GetWindowText(aux);
	strcpy(ttt[id].nome,aux);
	cmb_seltatt.ResetContent();
	for(int i=0;i<16;i++)
		cmb_seltatt.AddString(ttt[i].nome);
	cmb_seltatt.SetCurSel(id);

}

void tattDlg::OnChangeTatx2() 
{
	vtatt(&txt_tatx2, &txt_taty2, &cmd_vtat1);
}

void tattDlg::OnChangeTatx3() 
{
	vtatt(&txt_tatx3, &txt_taty3, &cmd_vtat2);
}

void tattDlg::OnChangeTatx4() 
{
	vtatt(&txt_tatx4, &txt_taty4, &cmd_vtat3);
}

void tattDlg::OnChangeTatx5() 
{
	vtatt(&txt_tatx5, &txt_taty5, &cmd_vtat4);
}

void tattDlg::OnChangeTatx6() 
{
	vtatt(&txt_tatx6, &txt_taty6, &cmd_vtat5);
}

void tattDlg::OnChangeTatx7() 
{
	vtatt(&txt_tatx7, &txt_taty7, &cmd_vtat6);
}

void tattDlg::OnChangeTatx8() 
{
	vtatt(&txt_tatx8, &txt_taty8, &cmd_vtat7);
}

void tattDlg::OnChangeTatx9() 
{
	vtatt(&txt_tatx9, &txt_taty9, &cmd_vtat8);
}

void tattDlg::OnChangeTatx10() 
{
	vtatt(&txt_tatx10, &txt_taty10, &cmd_vtat9);
}

void tattDlg::OnChangeTatx11() 
{
	vtatt(&txt_tatx11, &txt_taty11, &cmd_vtat10);
}

void tattDlg::OnChangeTaty2() 
{
	vtatt(&txt_tatx2, &txt_taty2, &cmd_vtat1);
}

void tattDlg::OnChangeTaty3() 
{
	vtatt(&txt_tatx3, &txt_taty3, &cmd_vtat2);
}

void tattDlg::OnChangeTaty4() 
{
	vtatt(&txt_tatx4, &txt_taty4, &cmd_vtat3);
}

void tattDlg::OnChangeTaty5() 
{
	vtatt(&txt_tatx5, &txt_taty5, &cmd_vtat4);
}

void tattDlg::OnChangeTaty6() 
{
	vtatt(&txt_tatx6, &txt_taty6, &cmd_vtat5);
}

void tattDlg::OnChangeTaty7() 
{
	vtatt(&txt_tatx7, &txt_taty7, &cmd_vtat6);
}

void tattDlg::OnChangeTaty8() 
{
	vtatt(&txt_tatx8, &txt_taty8, &cmd_vtat7);
}

void tattDlg::OnChangeTaty9() 
{
	vtatt(&txt_tatx9, &txt_taty9, &cmd_vtat8);
}

void tattDlg::OnChangeTaty10() 
{
	vtatt(&txt_tatx10, &txt_taty10, &cmd_vtat9);
}

void tattDlg::OnChangeTaty11() 
{
	vtatt(&txt_tatx11, &txt_taty11, &cmd_vtat10);
}

void tattDlg::exitcmbtatt(CComboBox *cb, int n)
{
	ttt[cmb_seltatt.GetCurSel()].ruoli[n] = cb->GetCurSel()+2;
}

void tattDlg::exitatx(CEdit *txt, int n)
{
	CString str;
	char str1[6];
	int i;
	txt->GetWindowText(str);
	i = atoi(str);
	if(i<TTXMIN)
	{
		_itoa(TTXMIN,str1,10);
		i = TTXMIN;
		txt->SetWindowText(str1);
	}
	if(i>TTXMAX)
	{
		_itoa(TTXMAX,str1,10);
		i = TTXMAX;
		txt->SetWindowText(str1);
	}
	ttt[cmb_seltatt.GetCurSel()].x[n] = i;
}

void tattDlg::exitaty(CEdit *txt, int n)
{
	CString str;
	char str1[6];
	int i;
	txt->GetWindowText(str);
	i = atoi(str);
	if(i<TTYMIN)
	{
		_itoa(TTYMIN,str1,10);
		i = TTYMIN;
		txt->SetWindowText(str1);
	}
	if(i>TTYMAX)
	{
		_itoa(TTYMAX,str1,10);
		i = TTYMAX;
		txt->SetWindowText(str1);
	}
	ttt[cmb_seltatt.GetCurSel()].y[n] = i;
}

void tattDlg::OnKillfocusTat2() 
{
	exitcmbtatt(&cmb_tat2, 1);
}

void tattDlg::OnKillfocusTat3() 
{
	exitcmbtatt(&cmb_tat3, 2);
}

void tattDlg::OnKillfocusTat4() 
{
	exitcmbtatt(&cmb_tat4, 3);
}

void tattDlg::OnKillfocusTat5() 
{
	exitcmbtatt(&cmb_tat5, 4);
}

void tattDlg::OnKillfocusTat6() 
{
	exitcmbtatt(&cmb_tat6, 5);
}

void tattDlg::OnKillfocusTat7() 
{
	exitcmbtatt(&cmb_tat7, 6);
}

void tattDlg::OnKillfocusTat8() 
{
	exitcmbtatt(&cmb_tat8, 7);
}

void tattDlg::OnKillfocusTat9() 
{
	exitcmbtatt(&cmb_tat9, 8);
}

void tattDlg::OnKillfocusTat10() 
{
	exitcmbtatt(&cmb_tat10, 9);
}

void tattDlg::OnKillfocusTat11() 
{
	exitcmbtatt(&cmb_tat11, 10);
}

void tattDlg::OnKillfocusTatx2() 
{
	exitatx(&txt_tatx2, 0);
}

void tattDlg::OnKillfocusTatx3() 
{
	exitatx(&txt_tatx3, 1);
}

void tattDlg::OnKillfocusTatx4() 
{
	exitatx(&txt_tatx4, 2);
}

void tattDlg::OnKillfocusTatx5() 
{
	exitatx(&txt_tatx5, 3);
}

void tattDlg::OnKillfocusTatx6() 
{
	exitatx(&txt_tatx6, 4);
}

void tattDlg::OnKillfocusTatx7() 
{
	exitatx(&txt_tatx7, 5);
}

void tattDlg::OnKillfocusTatx8() 
{
	exitatx(&txt_tatx8, 6);
}

void tattDlg::OnKillfocusTatx9() 
{
	exitatx(&txt_tatx9, 7);
}

void tattDlg::OnKillfocusTatx10() 
{
	exitatx(&txt_tatx10, 8);
}

void tattDlg::OnKillfocusTatx11() 
{
	exitatx(&txt_tatx11, 9);
}

void tattDlg::OnKillfocusTaty2() 
{
	exitaty(&txt_taty2, 0);
}

void tattDlg::OnKillfocusTaty3() 
{
	exitaty(&txt_taty3, 1);
}

void tattDlg::OnKillfocusTaty4() 
{
	exitaty(&txt_taty4, 2);
}

void tattDlg::OnKillfocusTaty5() 
{
	exitaty(&txt_taty5, 3);
}

void tattDlg::OnKillfocusTaty6() 
{
	exitaty(&txt_taty6, 4);
}

void tattDlg::OnKillfocusTaty7() 
{
	exitaty(&txt_taty7, 5);
}

void tattDlg::OnKillfocusTaty8() 
{
	exitaty(&txt_taty8, 6);
}

void tattDlg::OnKillfocusTaty9() 
{
	exitaty(&txt_taty9, 7);
}

void tattDlg::OnKillfocusTaty10() 
{
	exitaty(&txt_taty10, 8);
}

void tattDlg::OnKillfocusTaty11() 
{
	exitaty(&txt_taty11, 9);
}

void tattDlg::OnImporta() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "tactic file MANIA 2002 (*.t2002)|*.t2002|";
	char aux[10];
	CString nome_file,fil_path_programma;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

 	CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "TACTIC FILE TO IMPORT";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	CFile fil_ctrl(nome_file, CFile::modeRead | CFile::typeBinary );
	fil_ctrl.Seek(0,CFile::begin);
	fil_ctrl.Read(aux,8);
	aux[8] = NULL;
	if(strcmp(aux,"f.m.tatt") != 0 || fil_ctrl.GetLength() != 52)
	{
		AfxMessageBox("Not right file !");
		return;
	}
	fil_ctrl.Read(&ttt[cmb_seltatt.GetCurSel()],sizeof(tattica));
	fil_ctrl.Close();
	OnChnageSelTatt();
	OnKillfocusNometattica();
	AfxMessageBox("Tactic imported !");
}	

void tattDlg::OnEsporta() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "tactic file MANIA 2002 (*.t2002)|*.t2002|";
	CString nome_file,fil_path_programma;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

	CFileDialog dlg(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "TACTIC FILE TO EXPORT";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	if(nome_file.Right(6) != ".t2002")
		nome_file += ".t2002";
	CFile fil_ctrl(nome_file, CFile::modeReadWrite | CFile::typeBinary | CFile::modeCreate);
	fil_ctrl.Seek(0,CFile::begin);
	// salvataggio sul nuovo file
	fil_ctrl.Write("f.m.tatt",8);
	fil_ctrl.Write(&ttt[cmb_seltatt.GetCurSel()],sizeof(tattica));
	fil_ctrl.Close();
	AfxMessageBox("Tactic exported !");
}

