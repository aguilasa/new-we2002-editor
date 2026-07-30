// carattDlg.cpp : implementation file
//

#include "stdafx.h"
#include "ed.h"
#include "carattDlg.h"
#include "edDlg.h"
//#ifndef __MY__GLOBALS__H
//#include "myglobals.h"
//#endif 

char g_ruolo[8][3] = {"GK", "CB", "SB", "DH", "SH", "OH", "CF", "WG"};
char g_colore_pelle[4][2] = { "A", "B", "C", "D" };
char g_stile_capelli[][3] = { "A1", "A2", "A3",
						  "B1", "B2", "B3", "B4", "B5", "B6",
						  "C1", "C2", 
						  "D1", "D2", 
						  "E1", "E2",
						  "F1", "F2", "F3",
						  "G1",
						  "H1",
						  "I1", "I2", "I3",
						  "J1",
						  "K1",
						  "L1", "L2", "L3",
						  "M1",
						  "N1",
						  "O1",
						  "P1"
						};							 
char g_colore_capelli[8][2] = { "A", "B", "C", "D", "E", "F", "G", "H" };
char g_stile_barba[7][2] = { "A", "B", "C", "D", "E", "F", "G" };
char g_colore_barba[7][2] = { "A", "B", "C", "D", "E", "F", "G" }; 
char g_corporatura[8][2] = { "A", "B", "C", "D", "E", "F", "G", "H" };
char g_scarpe[8][2] = { "A", "B", "C", "D", "E", "F", "G", "H" };
char g_piede[3][11] = { "RIGHT", "LEFT", "BOTH" };
char g_fuori_ruolo[2][5] = { "NO", "YES" };


#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// carattDlg dialog


carattDlg::carattDlg(CWnd* pParent /*=NULL*/)
	: CDialog(carattDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(carattDlg)
	//}}AFX_DATA_INIT
}


void carattDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(carattDlg)
	DDX_Control(pDX, TXT_GNUMERO, txt_numero);
	DDX_Control(pDX, TXT_ETA, txt_eta);
	DDX_Control(pDX, TXT_ALTEZZA, txt_altz);
	DDX_Control(pDX, TXT_GVEL, txt_vel);
	DDX_Control(pDX, TXT_GTEST, txt_tes);
	DDX_Control(pDX, TXT_GTECN, txt_tec);
	DDX_Control(pDX, TXT_GRIFL, txt_rif);
	DDX_Control(pDX, TXT_GRES, txt_res);
	DDX_Control(pDX, TXT_GPZT, txt_pz_tiro);
	DDX_Control(pDX, TXT_GPRET, txt_pr_tiro);
	DDX_Control(pDX, TXT_GPASS, txt_pass);
	DDX_Control(pDX, TXT_GNOME, txt_nome);
	DDX_Control(pDX, TXT_GFZF, txt_frz);
	DDX_Control(pDX, TXT_GELE, txt_ele);
	DDX_Control(pDX, TXT_GEFF, txt_eff);
	DDX_Control(pDX, TXT_GDRIB, txt_dri);
	DDX_Control(pDX, TXT_GDIF, txt_dif);
	DDX_Control(pDX, TXT_GCOSTO, txt_costo);
	DDX_Control(pDX, TXT_GATT, txt_att);
	DDX_Control(pDX, TXT_GAGGR, txt_agg);
	DDX_Control(pDX, TXT_GACC, txt_acc);
	DDX_Control(pDX, CMB_GSCARPE, cmb_scarpe);
	DDX_Control(pDX, CMB_GRUOLO, cmb_ruolo);
	DDX_Control(pDX, CMB_GPIEDE, cmb_piede);
	DDX_Control(pDX, CMB_GPELLE, cmb_pelle);
	DDX_Control(pDX, CMB_GFRUOLO, cmb_fuori_ruolo);
	DDX_Control(pDX, CMB_GCORPO, cmb_corporatura);
	DDX_Control(pDX, CMB_GCAPSTILE, cmb_capelli_stile);
	DDX_Control(pDX, CMB_GCAPCOL, cmb_capelli_col);
	DDX_Control(pDX, CMB_GBARBASTILE, cmb_barba_stile);
	DDX_Control(pDX, CMB_GBARBACOL, cmb_barba_col);
	DDX_Control(pDX, CMD_READ_URL, cmd_import_url);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(carattDlg, CDialog)
	//{{AFX_MSG_MAP(carattDlg)
	ON_EN_KILLFOCUS(TXT_ALTEZZA, OnKillfocusAltezza)
	ON_EN_KILLFOCUS(TXT_ETA, OnKillfocusEta)
	ON_EN_KILLFOCUS(TXT_GACC, OnKillfocusGacc)
	ON_EN_KILLFOCUS(TXT_GAGGR, OnKillfocusGaggr)
	ON_EN_KILLFOCUS(TXT_GATT, OnKillfocusGatt)
	ON_EN_KILLFOCUS(TXT_GCOSTO, OnKillfocusGcosto)
	ON_EN_KILLFOCUS(TXT_GDIF, OnKillfocusGdif)
	ON_EN_KILLFOCUS(TXT_GDRIB, OnKillfocusGdrib)
	ON_EN_KILLFOCUS(TXT_GEFF, OnKillfocusGeff)
	ON_EN_KILLFOCUS(TXT_GELE, OnKillfocusGele)
	ON_EN_KILLFOCUS(TXT_GFZF, OnKillfocusGfzf)
	ON_EN_KILLFOCUS(TXT_GNOME, OnKillfocusGnome)
	ON_EN_KILLFOCUS(TXT_GPASS, OnKillfocusGpass)
	ON_EN_KILLFOCUS(TXT_GPRET, OnKillfocusGpret)
	ON_EN_KILLFOCUS(TXT_GPZT, OnKillfocusGpzt)
	ON_EN_KILLFOCUS(TXT_GRES, OnKillfocusGres)
	ON_EN_KILLFOCUS(TXT_GRIFL, OnKillfocusGrifl)
	ON_EN_KILLFOCUS(TXT_GTECN, OnKillfocusGtecn)
	ON_EN_KILLFOCUS(TXT_GTEST, OnKillfocusGtest)
	ON_EN_KILLFOCUS(TXT_GVEL, OnKillfocusGvel)
	ON_CBN_KILLFOCUS(CMB_GBARBACOL, OnKillfocusGbarbacol)
	ON_CBN_KILLFOCUS(CMB_GBARBASTILE, OnKillfocusGbarbastile)
	ON_CBN_KILLFOCUS(CMB_GCAPCOL, OnKillfocusGcapcol)
	ON_CBN_KILLFOCUS(CMB_GCAPSTILE, OnKillfocusGcapstile)
	ON_CBN_KILLFOCUS(CMB_GCORPO, OnKillfocusGcorpo)
	ON_CBN_KILLFOCUS(CMB_GFRUOLO, OnKillfocusGfruolo)
	ON_CBN_KILLFOCUS(CMB_GPELLE, OnKillfocusGpelle)
	ON_CBN_KILLFOCUS(CMB_GPIEDE, OnKillfocusGpiede)
	ON_CBN_KILLFOCUS(CMB_GRUOLO, OnKillfocusGruolo)
	ON_CBN_KILLFOCUS(CMB_GSCARPE, OnKillfocusGscarpe)
	ON_EN_KILLFOCUS(TXT_GNUMERO, OnKillfocusGnumero)
	ON_BN_CLICKED(CMD_READ_URL, OnClickReadSingleURL)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// carattDlg message handlers

void carattDlg::carica()
{
	int rad = 10;
	char strint[4];

	txt_nome.SetWindowText(auxgioc[id_giocatore].nome);
	_itoa(auxgioc[id_giocatore].costo, strint, rad);
	txt_costo.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].numero, strint, rad);
	txt_numero.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].altezza, strint, rad);
	txt_altz.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].eta, strint, rad);
	txt_eta.SetWindowText(strint);

	_itoa(auxgioc[id_giocatore].accel, strint, rad);
	txt_acc.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].aggress, strint, rad);
	txt_agg.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].attacco, strint, rad);
	txt_att.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].difesa, strint, rad);
	txt_dif.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].dribbling, strint, rad);
	txt_dri.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].salto, strint, rad);
	txt_ele.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].effetto, strint, rad);
	txt_eff.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].forza, strint, rad);
	txt_frz.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].passaggio, strint, rad);
	txt_pass.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].prec_tiro, strint, rad);
	txt_pr_tiro.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].pot_tiro, strint, rad);
	txt_pz_tiro.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].resistenza, strint, rad);
	txt_res.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].riflessi, strint, rad);
	txt_rif.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].tecnica, strint, rad);
	txt_tec.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].testa, strint, rad);
	txt_tes.SetWindowText(strint);
	_itoa(auxgioc[id_giocatore].velocita, strint, rad);
	txt_vel.SetWindowText(strint);
	// selezione combo
	cmb_ruolo.SetCurSel(auxgioc[id_giocatore].posizione);
	cmb_pelle.SetCurSel(auxgioc[id_giocatore].col_pelle);
	cmb_capelli_stile.SetCurSel(auxgioc[id_giocatore].stile_capelli);
	cmb_capelli_col.SetCurSel(auxgioc[id_giocatore].col_capelli);
	cmb_barba_stile.SetCurSel(auxgioc[id_giocatore].stile_barba);
	cmb_barba_col.SetCurSel(auxgioc[id_giocatore].col_barba);
	cmb_corporatura.SetCurSel(auxgioc[id_giocatore].corporatura);
	cmb_scarpe.SetCurSel(auxgioc[id_giocatore].scarpe);
	cmb_piede.SetCurSel(auxgioc[id_giocatore].piede);
	cmb_fuori_ruolo.SetCurSel(auxgioc[id_giocatore].fuori_ruolo);

}

BOOL carattDlg::OnInitDialog() 
{

	CDialog::OnInitDialog();

	int i;
	for(i=0;i<8;i++)
		cmb_ruolo.AddString(g_ruolo[i]);
	for(i=0;i<4;i++)
		cmb_pelle.AddString(g_colore_pelle[i]);
	for(i=0;i<32;i++)
		cmb_capelli_stile.AddString(g_stile_capelli[i]);
	for(i=0;i<8;i++)
		cmb_capelli_col.AddString(g_colore_capelli[i]);
	for(i=0;i<7;i++)
		cmb_barba_stile.AddString(g_stile_barba[i]);
	for(i=0;i<7;i++)
		cmb_barba_col.AddString(g_colore_barba[i]);
	for(i=0;i<8;i++)
		cmb_corporatura.AddString(g_corporatura[i]);
	for(i=0;i<8;i++)
		cmb_scarpe.AddString(g_scarpe[i]);
	for(i=0;i<3;i++)
		cmb_piede.AddString(g_piede[i]);
	for(i=0;i<2;i++)
		cmb_fuori_ruolo.AddString(g_fuori_ruolo[i]);

	txt_altz.SetLimitText(3);
	txt_eta.SetLimitText(2);
	txt_nome.SetLimitText(10);
	txt_acc.SetLimitText(2);
	txt_agg.SetLimitText(2);
	txt_att.SetLimitText(2);
	txt_costo.SetLimitText(2);
	txt_dif.SetLimitText(2);
	txt_dri.SetLimitText(2);
	txt_eff.SetLimitText(2);
	txt_frz.SetLimitText(2);
	txt_pass.SetLimitText(2);
	txt_pr_tiro.SetLimitText(2);
	txt_pz_tiro.SetLimitText(2);
	txt_res.SetLimitText(2);
	txt_rif.SetLimitText(2);
	txt_tec.SetLimitText(2);
	txt_tes.SetLimitText(2);
	txt_vel.SetLimitText(2);

	carica();
	return TRUE;
}

void carattDlg::OnKillfocusAltezza() 
{
	CString str;
	int i;
	txt_altz.GetWindowText(str);
	i = atoi(str);
	if(i<155)
	{
		i = 155;
		txt_altz.SetWindowText("155");
	}
	if(i>210)
	{
		i = 210;
		txt_altz.SetWindowText("210");
	}
	auxgioc[id_giocatore].altezza = i;
}

void carattDlg::OnKillfocusEta() 
{
	CString str;
	int i;
	txt_eta.GetWindowText(str);
	i = atoi(str);
	if(i<15)
	{
		i = 15;
		txt_eta.SetWindowText("15");
	}
	if(i>46)
	{
		i = 46;
		txt_eta.SetWindowText("46");
	}
	auxgioc[id_giocatore].eta = i;
}

void carattDlg::OnKillfocusGcosto() 
{
	CString str;
	int i;
	txt_costo.GetWindowText(str);
	i = atoi(str);
	auxgioc[id_giocatore].costo = i;
}

void carattDlg::OnKillfocusGnome() 
{
	CString str;
	txt_nome.GetWindowText(str);
	strcpy(auxgioc[id_giocatore].nome,str);
}

void carattDlg::OnKillfocusGacc() 
{
	exitTXT(&txt_acc,&auxgioc[id_giocatore].accel);
}

void carattDlg::OnKillfocusGaggr() 
{
	exitTXT(&txt_agg,&auxgioc[id_giocatore].aggress);
}

void carattDlg::OnKillfocusGatt() 
{
	exitTXT(&txt_att,&auxgioc[id_giocatore].attacco);
}

void carattDlg::OnKillfocusGdif() 
{
	exitTXT(&txt_dif,&auxgioc[id_giocatore].difesa);
}

void carattDlg::OnKillfocusGdrib() 
{
	exitTXT(&txt_dri,&auxgioc[id_giocatore].dribbling);
}

void carattDlg::OnKillfocusGeff() 
{
	exitTXT(&txt_eff,&auxgioc[id_giocatore].effetto);
}

void carattDlg::OnKillfocusGele() 
{
	exitTXT(&txt_ele,&auxgioc[id_giocatore].salto);
}

void carattDlg::OnKillfocusGfzf() 
{
	exitTXT(&txt_frz,&auxgioc[id_giocatore].forza);
}

void carattDlg::OnKillfocusGpass() 
{
	exitTXT(&txt_pass,&auxgioc[id_giocatore].passaggio);
}

void carattDlg::OnKillfocusGpret() 
{
	exitTXT(&txt_pr_tiro,&auxgioc[id_giocatore].prec_tiro);
}

void carattDlg::OnKillfocusGpzt() 
{
	exitTXT(&txt_pz_tiro,&auxgioc[id_giocatore].pot_tiro);
}

void carattDlg::OnKillfocusGres() 
{
	exitTXT(&txt_res,&auxgioc[id_giocatore].resistenza);
}

void carattDlg::OnKillfocusGrifl() 
{
	exitTXT(&txt_rif,&auxgioc[id_giocatore].riflessi);
}

void carattDlg::OnKillfocusGtecn() 
{
	exitTXT(&txt_tec,&auxgioc[id_giocatore].tecnica);
}

void carattDlg::OnKillfocusGtest() 
{
	exitTXT(&txt_tes,&auxgioc[id_giocatore].testa);
}

void carattDlg::OnKillfocusGvel() 
{
	exitTXT(&txt_vel,&auxgioc[id_giocatore].velocita);
}

void carattDlg::OnKillfocusGnumero() 
{
	CString str;
	int i;
	txt_numero.GetWindowText(str);
	i = atoi(str);
	if(i<1)
	{
		i = 1;
		txt_numero.SetWindowText("1");
	}
	if(i>32)
	{
		i = 32;
		txt_numero.SetWindowText("32");
	}
	auxgioc[id_giocatore].numero = i;
}

void carattDlg::exitTXT(CEdit *txt,int *q)
{
	CString str;
	int i;
	txt->GetWindowText(str);
	i = atoi(str);
	if(i<12)
	{
		i = 12;
		txt->SetWindowText("12");
	}
	if(i>19)
	{
		i = 19;
		txt->SetWindowText("19");
	}
	*q = i;
}

void carattDlg::OnKillfocusGbarbacol() 
{
	exitCMB(&cmb_barba_col,&auxgioc[id_giocatore].col_barba);
}

void carattDlg::OnKillfocusGbarbastile() 
{
	exitCMB(&cmb_barba_stile,&auxgioc[id_giocatore].stile_barba);
}

void carattDlg::OnKillfocusGcapcol() 
{
	exitCMB(&cmb_capelli_col,&auxgioc[id_giocatore].col_capelli);
}

void carattDlg::OnKillfocusGcapstile() 
{
	exitCMB(&cmb_capelli_stile,&auxgioc[id_giocatore].stile_capelli);
}

void carattDlg::OnKillfocusGcorpo() 
{
	exitCMB(&cmb_corporatura,&auxgioc[id_giocatore].corporatura);
}

void carattDlg::OnKillfocusGfruolo() 
{
	exitCMB(&cmb_fuori_ruolo,&auxgioc[id_giocatore].fuori_ruolo);
}

void carattDlg::OnKillfocusGpelle() 
{
	exitCMB(&cmb_pelle,&auxgioc[id_giocatore].col_pelle);
}

void carattDlg::OnKillfocusGpiede() 
{
	exitCMB(&cmb_piede,&auxgioc[id_giocatore].piede);
}

void carattDlg::OnKillfocusGruolo() 
{
	exitCMB(&cmb_ruolo,&auxgioc[id_giocatore].posizione);
}

void carattDlg::OnKillfocusGscarpe() 
{
	exitCMB(&cmb_scarpe,&auxgioc[id_giocatore].scarpe);
}

void carattDlg::OnClickReadSingleURL()
{
	int res = 0;
	string link(auxgioc[id_giocatore].url);
	if (link.length() > 0 && link != "dummy")
	{
		res = auxfifapl[id_giocatore].UpdatePlayerFromURL(link);
	}
	else
	{
		if(link == "dummy")
		{
			auxfifapl[id_giocatore].SetPlayerToDummy();
			res = 1;
		}
	}
	if(res == 1) 
	{
		auxgioc[id_giocatore].editFromFIFA(auxfifapl[id_giocatore],1,1,1);
		setPlayerNo(id_giocatore, auxfifapl[id_giocatore].number[0], auxfifapl[id_giocatore].number[1]);
		carica();
		AfxMessageBox("Done.");
	}
}

void carattDlg::exitCMB(CComboBox *cmb, int *q)
{
	int i;
	i = cmb->GetCurSel();
	*q = i;
}

