// selezDlg.cpp : implementation file
//

#include "stdafx.h"
#include "ed.h"
#include "selezDlg.h"
#include "giocatore.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
int applk[120];

const int sstart_link[] = 
{
0, //irlanda
5, //scozia
9, //galles
10, //inghilterra
51, //portogallo
58, //spagna
100, //francia
168, //belgio
173, //olanda
210, //svizzera
211, //italia
275, //r.ceca
276, //germania
301, //danimarca
304, //norvegia
306, //svezia
311, //finlandia
312, //polonia
0,	 //slovacchia
313, //austria
0,	 //ungheria
0,	 //slovania
314, //croazia
318, //jugoslavia
321, //romania
0,	 //bulgaria
325, //grecia
333, //turchia
343, //ucraina
347, //russia
349, //marocco
0,	 //tunisia
350, //egitto
351, //nigeria
0,	 //camerun
0,	 //sudafrica
0,	 //senegal
352, //usa
0,	 //messico
0,	 //costa rica
353, //colombia
354, //brasile
0,	 //peru
0,	 //cile
390, //paraguay
391, //uruguay
394, //argentina
0,	 //ecuador
428, //giappone
0,	 //corea
0,	 //cina
0,	 //iran
0,	 //arabia
432, //australia
0,	 //euro all-star
0,	 //world all-star
0,	 //cl. ing
0,	 //cl. fra
0,	 //cl. ola
0,	 //cl. ita
0,	 //cl. ger
0,	 //cl. bra
0,	 //cl. arg
-1, 
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
-1,
434, //islanda
435, //uzbekistan
436, //georgia
438, //bielorussia
440, //bosnia
0,	 //macedonia
442, //lussemburgo
4,	 //n.irlanda
0,	 //giamaica
0,	 //uae
443, //algeria
444, //ghana
0,	 //guinea
451, //costa avorio
456, //congo
457, //togo
458, //burundi
0,	 //liberia
0,	 //zambia
459, //sierra leone
0,	 //canada
460, //trinidad
0,	 //honduras
0,	 //libano
0	 //zelanda
};

// codici ml
const int snc_naz_seq[] = 
{
0, //irlanda
102, // n.irlanda
1, //scozia
2, //galles
3, //inghilterra
4, //portogallo
5, //spagna
6, //francia
7, //belgio
8, //olanda
9, //svizzera
10, //italia
11, //r.ceca
12, //germania
13, //danimarca
14, //norvegia
15, //svezia
16, //finlandia
17, //polonia
19, //austria
22, //croazia
23, //jugoslavia
24, //romania
26, //grecia
27, //turchia
28, //ucraina
29, //russia
30, //marocco
32, //egitto
33, //nigeria
37, //usa
40, //colombia
41, //brasile
44, //paraguay
45, //uruguay
46, //argentina
48, //giappone
53, //australia
95, //islanda
96, //uzbekistan
97, //georgia
98, //bielorussia
99, //bosnia
101, //lussemburgo
105, //algeria
106, //ghana
108, //costa avorio
109, //congo
110, //togo
111, //burundi
114, //sierra leone
116 //trinidad
};

char snc_naz_qt[] = 
{
4, //irlanda
1, //n.irlanda
4, //scozia
1, //galles
41,//inghilterra
7, //portogallo
42, //spagna
68, //francia
5, //belgio
37, //olanda
1, //svizzera
64, //italia
1, //r.ceca
25, //germania
3, //danimarca
2, //norvegia
5, //svezia
1, //finlandia
1, //polonia
1, //austria
4, //croazia
3, //jugoslavia
4, //romania
8, //grecia
10, //turchia
4, //ucraina
2, //russia
1, //marocco
1, //egitto
1, //nigeria
1, //usa
1, //colombia
36, //brasile
1, //paraguay
3, //uruguay
34, //argentina
4, //giappone
2, //australia
1, //islanda
1, //uzbekistan
2, //georgia
2, //bielorussia
2, //bosnia
1, //lussemburgo
1, //algeria
7, //ghana
5, //costa avorio
1, //congo
1, //togo
1, //burundi
1, //sierra leone
2 //trinidad
}; //462

char snomi_squadre[120][20] =
{
"Irland",
"Scotland",
"Wales",
"England",
"Portugal",
"Spain",
"France",
"Belgium",
"Netherlands",
"Switzerland",
"Italy",
"Czech Rep.",
"Germany",
"Denmark",
"Norway",
"Sweden",
"Iceland",
"Poland",
"Slovakia",
"Austria",
"Hungary",
"Albania",
"Croatia",
"Serbia",
"Romania",
"Bosnia",
"Greece",
"Turkey",
"Ukraine",
"Russia",
"Morocco",
"Ivory Coast",
"Egypt",
"Nigeria",
"Cameroon",
"Algeria",
"Ghana",
"U.S.A.",
"Mexico",
"Venezuela",
"Colombia",
"Brazil",
"Peru",
"Chile",
"Paraguay",
"Uruguay",
"Argentina",
"Ecuador",
"Japan",
"South Korea",
"China",
"India",
"New Zealand",
"Australia",//54
"Euro All Stars",
"World All Stars",
"Clas. England",
"Clas. France",
"Clas. Netherlands",
"Clas. Italy",
"Clas. Germany",
"Clas. Brazil",
"Clas. Argentina",
"Manchester Utd",//64
"Arsenal",
"Chelsea",
"Liverpool",
"Manchester City",
"Tottenham",
"Atletico Madrid",
"Barcelona",
"Real Madrid",
"Valencia",
"Sevilla",
"Monaco",
"Porto",
"P.S.G.",
"Benfica",
"Ajax",
"CSKA Moscow",
"Zenit",
"Inter",
"Juventus",
"Milan",
"Lazio",
"Napoli",
"Fiorentina",
"Roma",
"B.Dortmund",
"B.Munchen",
"B.Leverkusen",
"Wolfsburg",
"Galatasaray",
"Shakhtar Donetsk",
"Basilea",
"Island", //95
"Uzbekistan",
"Georgia",
"Bielorus",
"Bosnia H.",
"Macedonia",
"Luxemburg",
"N.Irland",
"Jamaica",
"UAE",
"Algeria",
"Ghana",
"Guinea",
"Ivory Cost",
"Congo",
"Togo",
"Burundi",
"Liberia",
"Zambia",
"Sierra Leone",
"Canada",
"Trinidad-Tobago",
"Honduras",
"Libano",
"New Zeland"
};
#define NOML 

selezDlg::selezDlg(CWnd* pParent /*=NULL*/)
	: CDialog(selezDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(selezDlg)
	//}}AFX_DATA_INIT
}


void selezDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(selezDlg)
	DDX_Control(pDX, LBL_LK, lbl_nazion);
	DDX_Control(pDX, CMB_NAZIONALITA, cmb_nazion);
	DDX_Control(pDX, CHK_LK_NDEF, chk_ndef);
	DDX_Control(pDX, CHK_LK_DEF, chk_lkdef);
	DDX_Control(pDX, LBL_NAZML, lbl_nazml);
	DDX_Control(pDX, CHK_ML, chk_ml);
	DDX_Control(pDX, CHK_SC, chk_sc);
	DDX_Control(pDX, LIST_SQUADRE, lst_squadre);
	DDX_Control(pDX, LIST_GIOCATORI, lst_giocatori);
	//}}AFX_DATA_MAP
}


BEGIN_MESSAGE_MAP(selezDlg, CDialog)
	//{{AFX_MSG_MAP(selezDlg)
	ON_LBN_SELCHANGE(LIST_SQUADRE, OnSelchangeSquadre)
	ON_LBN_SELCHANGE(LIST_GIOCATORI, OnSelchangeGiocatori)
	ON_LBN_DBLCLK(LIST_GIOCATORI, OnDblclkGiocatori)
	ON_BN_CLICKED(CHK_ML, OnMl)
	ON_BN_CLICKED(CHK_SC, OnSc)
	ON_BN_CLICKED(CHK_LK_DEF, OnLkDef)
	ON_BN_CLICKED(CHK_LK_NDEF, OnLkNdef)
	ON_BN_CLICKED(IDC_BUTTON1, OnOOKK)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// selezDlg message handlers

BOOL selezDlg::OnInitDialog() 
{
	CDialog::OnInitDialog();

	int i;
	char strint[4],auxch[50];
	for(i=0;i<54;i++)
	{
		_itoa(i+1, strint, 10);
		strcpy(auxch, "National ");
		strcat(auxch, strint);
		strcat(auxch, " - ");
		strcat(auxch, snomi_squadre[i]);
		lst_squadre.AddString(auxch);
	}
	for(i=0;i<9;i++)
	{
		_itoa(i+1, strint, 10);
		strcpy(auxch, "All-star ");
		strcat(auxch, strint);
		strcat(auxch, " - ");
		strcat(auxch, snomi_squadre[i+54]);
		lst_squadre.AddString(auxch);
	}
	lst_squadre.AddString("- ML (non contacted) ");
	//lst_squadre.SetCurSel(0);
	//selezDlg::OnSelchangeSquadre();
	//posizionarsi sul giocatore selezionato

	if(ml)
	{
		chk_ml.ShowWindow(1);
		chk_sc.ShowWindow(0);
		chk_ml.SetCheck(1);
	}
	return TRUE;  // return TRUE unless you set the focus to a control
	              // EXCEPTION: OCX Property Pages should return FALSE
}

void selezDlg::OnSelchangeSquadre() 
{
	char auxch[50], auxch2[50];
	string s;
	int f,t;

	int i,id;
	int n,p;
	id = lst_squadre.GetCurSel();
	lst_giocatori.ResetContent();

	for(i=0;i<(id==63?462:23);i++)
	{
		p=(id==63?i:(id*23)+462+i);
		strcpy(auxch, auxgioc[p].nome);
		if(strlen(auxgioc[p].url)>0)
		{
			s=auxgioc[p].url;
			f = s.find('-'); t = s.find('?');
			s.copy(auxch2, t-f-1, f+1);
			auxch2[t-f-1]='\0';
			strcat(auxch, " | ");
			strcat(auxch, auxch2);
		}
		else{auxch[10]='\0';}
		lst_giocatori.AddString(auxch);
	}

	selezDlg::OnMl();
}

void selezDlg::OnSelchangeGiocatori() {
	int i,conta,id;
	char aux[50],strint[4];

	if(lst_squadre.GetCurSel() == 63)
	{
		id = lst_giocatori.GetCurSel();
		i = conta = 0;
//		if(id>349)
//			id++;
		while(conta+snc_naz_qt[i]-1<id)
		{
			conta += snc_naz_qt[i];
			i++;
		}
		_itoa(id+1,strint,10);
		strcpy(aux,strint);
		strcat(aux,"° (nazionality ");
		_itoa(snc_naz_seq[i],strint,10);
		strcat(aux,strint);
		strcat(aux," - ");
		strcat(aux,snomi_squadre[snc_naz_seq[i]]);
		strcat(aux," )");
		lbl_nazml.SetWindowText(aux);

		//nazionalita disponibili
		cmb_nazion.ResetContent();
		conta = 0;
		for(i=0;i<120;i++)
		{
			if(sstart_link[i]<=id && id-sstart_link[i]<255 && sstart_link[i] != -1)
			{
				cmb_nazion.AddString(snomi_squadre[i]);
				applk[conta] = i;
				conta ++;
			}
		}
		cmb_nazion.SetCurSel(0);
	} else
		lbl_nazml.SetWindowText("");

}

void selezDlg::OnDblclkGiocatori() 
{
	giocatore gapp;
	int id,sq;
	id = lst_giocatori.GetCurSel();
	sq = lst_squadre.GetCurSel();
	//bisogna levare quello non codificato!
	if(sq != 63)
		id = sq*23+id+462;
	//nazionali, scambia valori
	if(!ml || chk_ml.GetCheck() == 0)
	{
		if(chk_sc.GetCheck() == 1)
		{
			//appoggia giocatore da sostituire
			gapp.accel = auxgioc[id].accel;
			gapp.aggress = auxgioc[id].aggress;
			gapp.altezza = auxgioc[id].altezza;
			gapp.attacco = auxgioc[id].attacco;
			gapp.col_barba = auxgioc[id].col_barba;
			gapp.col_capelli = auxgioc[id].col_capelli;
			gapp.col_pelle = auxgioc[id].col_pelle;
			gapp.corporatura = auxgioc[id].corporatura;
			gapp.costo = auxgioc[id].costo;
			gapp.difesa = auxgioc[id].difesa;
			gapp.dribbling = auxgioc[id].dribbling;
			gapp.effetto = auxgioc[id].effetto;
			gapp.eta = auxgioc[id].eta;
			gapp.forza = auxgioc[id].forza;
			gapp.fuori_ruolo = auxgioc[id].fuori_ruolo;
			strcpy(gapp.nome,auxgioc[id].nome);
			gapp.numero = auxgioc[id].numero;
			gapp.passaggio = auxgioc[id].passaggio;
			gapp.piede = auxgioc[id].piede;
			gapp.posizione = auxgioc[id].posizione;
			gapp.pot_tiro = auxgioc[id].pot_tiro;
			gapp.prec_tiro = auxgioc[id].prec_tiro;
			gapp.resistenza = auxgioc[id].resistenza;
			gapp.riflessi = auxgioc[id].riflessi;
			gapp.salto = auxgioc[id].salto;
			gapp.scarpe = auxgioc[id].scarpe;
			gapp.stile_barba = auxgioc[id].stile_barba;
			gapp.stile_capelli = auxgioc[id].stile_capelli;
			gapp.tecnica = auxgioc[id].tecnica;
			gapp.testa = auxgioc[id].testa;
			strcpy(gapp.url,auxgioc[id].url);
			gapp.velocita = auxgioc[id].velocita;
			//copia giocatore sostituto
			auxgioc[id].accel = auxgioc[id_giocatore].accel;
			auxgioc[id].aggress = auxgioc[id_giocatore].aggress;
			auxgioc[id].altezza = auxgioc[id_giocatore].altezza;
			auxgioc[id].attacco = auxgioc[id_giocatore].attacco;
			auxgioc[id].col_barba = auxgioc[id_giocatore].col_barba;
			auxgioc[id].col_capelli = auxgioc[id_giocatore].col_capelli;
			auxgioc[id].col_pelle = auxgioc[id_giocatore].col_pelle;
			auxgioc[id].corporatura = auxgioc[id_giocatore].corporatura;
			auxgioc[id].costo = auxgioc[id_giocatore].costo;
			auxgioc[id].difesa = auxgioc[id_giocatore].difesa;
			auxgioc[id].dribbling = auxgioc[id_giocatore].dribbling;
			auxgioc[id].effetto = auxgioc[id_giocatore].effetto;
			auxgioc[id].eta = auxgioc[id_giocatore].eta;
			auxgioc[id].forza = auxgioc[id_giocatore].forza;
			auxgioc[id].fuori_ruolo = auxgioc[id_giocatore].fuori_ruolo;
			strcpy(auxgioc[id].nome,auxgioc[id_giocatore].nome);
			auxgioc[id].numero = auxgioc[id_giocatore].numero;
			auxgioc[id].passaggio = auxgioc[id_giocatore].passaggio;
			auxgioc[id].piede = auxgioc[id_giocatore].piede;
			auxgioc[id].posizione = auxgioc[id_giocatore].posizione;
			auxgioc[id].pot_tiro = auxgioc[id_giocatore].pot_tiro;
			auxgioc[id].prec_tiro = auxgioc[id_giocatore].prec_tiro;
			auxgioc[id].resistenza = auxgioc[id_giocatore].resistenza;
			auxgioc[id].riflessi = auxgioc[id_giocatore].riflessi;
			auxgioc[id].salto = auxgioc[id_giocatore].salto;
			auxgioc[id].scarpe = auxgioc[id_giocatore].scarpe;
			auxgioc[id].stile_barba = auxgioc[id_giocatore].stile_barba;
			auxgioc[id].stile_capelli = auxgioc[id_giocatore].stile_capelli;
			auxgioc[id].tecnica = auxgioc[id_giocatore].tecnica;
			auxgioc[id].testa = auxgioc[id_giocatore].testa;
			strcpy(auxgioc[id].url,auxgioc[id_giocatore].url);
			auxgioc[id].velocita = auxgioc[id_giocatore].velocita;
			//ripassa 
			auxgioc[id_giocatore].accel = gapp.accel;
			auxgioc[id_giocatore].aggress = gapp.aggress;
			auxgioc[id_giocatore].altezza = gapp.altezza;
			auxgioc[id_giocatore].attacco = gapp.attacco;
			auxgioc[id_giocatore].col_barba = gapp.col_barba;
			auxgioc[id_giocatore].col_capelli = gapp.col_capelli;
			auxgioc[id_giocatore].col_pelle = gapp.col_pelle;
			auxgioc[id_giocatore].corporatura = gapp.corporatura;
			auxgioc[id_giocatore].costo = gapp.costo;
			auxgioc[id_giocatore].difesa = gapp.difesa;
			auxgioc[id_giocatore].dribbling = gapp.dribbling;
			auxgioc[id_giocatore].effetto = gapp.effetto;
			auxgioc[id_giocatore].eta = gapp.eta;
			auxgioc[id_giocatore].forza = gapp.forza;
			auxgioc[id_giocatore].fuori_ruolo = gapp.fuori_ruolo;
			strcpy(auxgioc[id_giocatore].nome,gapp.nome);
			auxgioc[id_giocatore].numero = gapp.numero;
			auxgioc[id_giocatore].passaggio = gapp.passaggio;
			auxgioc[id_giocatore].piede = gapp.piede;
			auxgioc[id_giocatore].posizione = gapp.posizione;
			auxgioc[id_giocatore].pot_tiro = gapp.pot_tiro;
			auxgioc[id_giocatore].prec_tiro = gapp.prec_tiro;
			auxgioc[id_giocatore].resistenza = gapp.resistenza;
			auxgioc[id_giocatore].riflessi = gapp.riflessi;
			auxgioc[id_giocatore].salto = gapp.salto;
			auxgioc[id_giocatore].scarpe = gapp.scarpe;
			auxgioc[id_giocatore].stile_barba = gapp.stile_barba;
			auxgioc[id_giocatore].stile_capelli = gapp.stile_capelli;
			auxgioc[id_giocatore].tecnica = gapp.tecnica;
			auxgioc[id_giocatore].testa = gapp.testa;
			strcpy(auxgioc[id_giocatore].url,gapp.url);
			auxgioc[id_giocatore].velocita = gapp.velocita;
		} else
		{
			auxgioc[id_giocatore].accel = auxgioc[id].accel;
			auxgioc[id_giocatore].aggress = auxgioc[id].aggress;
			auxgioc[id_giocatore].altezza = auxgioc[id].altezza;
			auxgioc[id_giocatore].attacco = auxgioc[id].attacco;
			auxgioc[id_giocatore].col_barba = auxgioc[id].col_barba;
			auxgioc[id_giocatore].col_capelli = auxgioc[id].col_capelli;
			auxgioc[id_giocatore].col_pelle = auxgioc[id].col_pelle;
			auxgioc[id_giocatore].corporatura = auxgioc[id].corporatura;
			auxgioc[id_giocatore].costo = auxgioc[id].costo;
			auxgioc[id_giocatore].difesa = auxgioc[id].difesa;
			auxgioc[id_giocatore].dribbling = auxgioc[id].dribbling;
			auxgioc[id_giocatore].effetto = auxgioc[id].effetto;
			auxgioc[id_giocatore].eta = auxgioc[id].eta;
			auxgioc[id_giocatore].forza = auxgioc[id].forza;
			auxgioc[id_giocatore].fuori_ruolo = auxgioc[id].fuori_ruolo;
			strcpy(auxgioc[id_giocatore].nome,auxgioc[id].nome);
			auxgioc[id_giocatore].numero = auxgioc[id].numero;
			auxgioc[id_giocatore].passaggio = auxgioc[id].passaggio;
			auxgioc[id_giocatore].piede = auxgioc[id].piede;
			auxgioc[id_giocatore].posizione = auxgioc[id].posizione;
			auxgioc[id_giocatore].pot_tiro = auxgioc[id].pot_tiro;
			auxgioc[id_giocatore].prec_tiro = auxgioc[id].prec_tiro;
			auxgioc[id_giocatore].resistenza = auxgioc[id].resistenza;
			auxgioc[id_giocatore].riflessi = auxgioc[id].riflessi;
			auxgioc[id_giocatore].salto = auxgioc[id].salto;
			auxgioc[id_giocatore].scarpe = auxgioc[id].scarpe;
			auxgioc[id_giocatore].stile_barba = auxgioc[id].stile_barba;
			auxgioc[id_giocatore].stile_capelli = auxgioc[id].stile_capelli;
			auxgioc[id_giocatore].tecnica = auxgioc[id].tecnica;
			auxgioc[id_giocatore].testa = auxgioc[id].testa;
			strcpy(auxgioc[id_giocatore].url,auxgioc[id].url);
			auxgioc[id_giocatore].velocita = auxgioc[id].velocita;
		}
	// cambia link ml
	} else
	{
		trovaLK(id,&auxml[0].link[pos]);
	}
	selezDlg::OnOK();
}

void selezDlg::trovaLK(int id,unsigned char *lk)
{
	int i,conta;
	//nazionale
	if(id>461)
	{
		//cod naz
		lk[0] = int((id-462)/23);
		//pos naz
		lk[1] = (id-462)%23;
	}
	//non contact
	else
	{
		if(chk_lkdef.GetCheck() == 1)
		{
			i = conta = 0;
			while(conta+snc_naz_qt[i]<=id)
			{
				conta += snc_naz_qt[i];
				i++;
			}
			lk[0] = snc_naz_seq[i];
			lk[1] = id-conta+23;
		} else
		{
			i = cmb_nazion.GetCurSel();
			lk[0] = applk[i];
			lk[1] = lst_giocatori.GetCurSel()-sstart_link[applk[i]]+23;
		}
	}
}

void selezDlg::OnMl() 
{
	if(chk_ml.GetCheck() == 1)
	{
		chk_ml.SetWindowText("link");
		chk_sc.ShowWindow(0);
		if(lst_squadre.GetCurSel() == 63)
		{
			lbl_nazml.ShowWindow(1);
			chk_lkdef.ShowWindow(1);
			chk_ndef.ShowWindow(1);
			cmb_nazion.ShowWindow(1);
			chk_lkdef.SetCheck(1);
		}
	} else
	{
		chk_ml.SetWindowText("skill");
		chk_sc.ShowWindow(1);
		lbl_nazml.ShowWindow(0);
		chk_lkdef.ShowWindow(0);
		chk_ndef.ShowWindow(0);
		cmb_nazion.ShowWindow(0);
	}
	if(lst_squadre.GetCurSel() != 63)
	{
		lbl_nazml.ShowWindow(0);
		chk_lkdef.ShowWindow(0);
		chk_ndef.ShowWindow(0);
		cmb_nazion.ShowWindow(0);
		chk_lkdef.SetCheck(0);
	}
}

void selezDlg::OnSc() 
{
	if(chk_sc.GetCheck() == 1)
		chk_sc.SetWindowText("complete substitution");
	else
		chk_sc.SetWindowText("incomplete substitution");
}

void selezDlg::OnLkDef() 
{
	int i = chk_lkdef.GetCheck();
	chk_ndef.SetCheck(!i);
}

void selezDlg::OnLkNdef() 
{
	int i = chk_ndef.GetCheck();
	chk_lkdef.SetCheck(!i);
}

void selezDlg::OnOOKK() 
{
	selezDlg::OnDblclkGiocatori();
}
