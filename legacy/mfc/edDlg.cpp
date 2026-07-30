#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <list>
#include "ed.h"
#include "edDlg.h"
#include "giocatore.h"
#include "squadra.h"
#include "graf.h"
#include "tattica.h"
#include "tattDlg.h"
#include "carattDlg.h"
#include "selezDlg.h"
#include "editOptForm.h"
#include "squadra_ml.h"
#include "myiotxt.h"
using namespace std;

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

#define GIOCATORI_NC 462
#define GIOCATORI_NAZALL 1449
#define GIOCATORI_TOT 1911

unsigned char link_euroas[46];
unsigned char link_worldas[46];

map<string,vector<string>> fifaVerGroupsMap;
map<string,map<string,vector<string>>> fifaVerGroupFieldMap;
map<string,int> fifaVerNumFields;
map<string,map<string,map<string,int>>> fifaVerGroupFieldIndexMap;
map<string,int> WEToIntPositionMap;
map<string,int> fifaToWEPositionMap;

struct fieldConversionSubFunction 
{
	//aggregation
	int aggregationFunctionType;
	int nAggrFields;
	int fieldIndexes[3];
	float fieldWeights[3];
	//discrete
	int discreteField;
	map<string,float> discreteFieldValuesMap;
	float discreteFieldWeight;
	//value FIFA to WE conversion
	float weIntervalUpperBound[7];

	int getValue(fifa_player fpl)
	{
		int k;
		float resVal;

		//aggregation part
		switch(aggregationFunctionType)
		{
			float wsum;
			case 0:
				//average
				resVal = 0;
				wsum = 0;
				for(k=0;k<nAggrFields;k++)
				{
					resVal = resVal + fpl.attributeValues[fieldIndexes[k]] * fieldWeights[k];
					wsum = wsum + fieldWeights[k];
				}
				resVal = resVal / wsum;
				break;
			case 1:
				//max
				resVal = 0;
				for(k=0;k<nAggrFields;k++)
				{
					if(resVal < fpl.attributeValues[fieldIndexes[k]]){resVal = fpl.attributeValues[fieldIndexes[k]];}
				}
				break;
			case -1:
				//min
				resVal = 100;
				for(k=0;k<nAggrFields;k++)
				{
					if(resVal > fpl.attributeValues[fieldIndexes[k]]){resVal = fpl.attributeValues[fieldIndexes[k]];}
				}
				break;
		}

		//discrete part
		if(discreteField > 0)
		{
			string att;
			switch(discreteField)
			{
				case 1:
					//offensive work rate
					att = fpl.offWeight;
					break;
				case 2:
					//defensive work rate
					att = fpl.defWeight;
					break;
				case 3:
					//skill moves
					att = to_string((_ULonglong)fpl.skillMoves);
					break;
			}
			resVal = resVal + discreteFieldValuesMap[att] * discreteFieldWeight;
		}

			 if(resVal <= weIntervalUpperBound[0]){return 12;}
		else if(resVal <= weIntervalUpperBound[1]){return 13;}
		else if(resVal <= weIntervalUpperBound[2]){return 14;}
		else if(resVal <= weIntervalUpperBound[3]){return 15;}
		else if(resVal <= weIntervalUpperBound[4]){return 16;}
		else if(resVal <= weIntervalUpperBound[5]){return 17;}
		else if(resVal <= weIntervalUpperBound[6]){return 18;}
		else									 {return 19;}
	}
};

struct fieldConversionFunction
{
	map<int, fieldConversionSubFunction> subFunctionsMap;
	int getValue(fifa_player fpl)
	{
		string sTemp = fpl.positions;
		if(sTemp.find(',')!=string::npos){sTemp = sTemp.substr(0,sTemp.find(','));}
		int WEposition = fifaToWEPositionMap[sTemp];
		return subFunctionsMap[WEposition].getValue(fpl);
	}
};

map<string, fieldConversionFunction> fieldConversionFunctionMap;

giocatore gioc[GIOCATORI_TOT];//prima i nc, poi i naz
fifa_player gioc_fifa[GIOCATORI_TOT];//prima i nc, poi i naz
squadra squad_nazall[63];
squadra_ml squad_ml[32];
squadra_ml squad_defml;
tattica tattpred[16];

carattDlg dlg_car;
selezDlg dlg_sel;
tattDlg dlg_tatt;
graf dlg_graf;
editOptForm dlg_edopt;

#define BTW 38
#define BTH 16
//tattiche
#define TXMAX 48
#define TXMIN 0
#define TYMAX 112
#define TYMIN 0
#define TCORRX -8
#define TCORRY 6

// trovare il posto giusto per questa roba!!

/******* globali *********/

CString fil_nomeCD; // nome del file immagine
CString fil_path_programma; //path del programma

#define SQUADRE_NAZ 54
#define SQUADRE_ALLS 9
#define SQUADRE_ML 32

const int start_link[] = 
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
0,	 //slovenia
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
-1, // le 32 ml
-1, // che non si possono chiaramente linkare
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
int nc_naz_seq[] = 
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

char nc_naz_qt[] = 
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

char nomi_squadre[120][20] =
{
"Ireland",
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
"Manchester U.",//64
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
"CSKA Moskva",
"Zenit",
"Inter",
"Juventus",
"Milan",
"Lazio",
"Napoli",
"Fiorentina",
"Roma",
"B. Dortmund",
"B. Munchen",
"B. Leverkusen",
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

// offsets nomi squadre
#define OFS_NOMI_SQ1 1012640
#define OFS_NOMI_SQ1_F 1013431
#define OFS_NOMI_SQ1A 1013736

#define OFS_NOMI_SQ2 1881968
#define OFS_NOMI_SQ3 2003996
#define OFS_NOMI_SQ4 2830160
#define OFS_NOMI_SQ5 4822908
#define OFS_NOMI_SQ5A 4823976
#define OFS_NOMI_SQ6 5651448
#define OFS_NOMI_SQ6A 5651880 
#define OFS_NOMI_SQ6B 5652364 

#define OFS_NOMI_SQK 2002316
#define OFS_NOMI_SQK1 2003928

#define OFS_NOMI_SQ_M 4598596
#define OFS_NOMI_SQ_AB1 2004996
#define OFS_NOMI_SQ_AB2 5651068
#define OFS_NOMI_SQ_AB3 4234484


#define OFS_NOMI_PML1 2028267
#define OFS_NOMI_PML2 2476048
#define OFS_NOMI_PML2A 2476680

// barre della forza
#define OFS_BAR 2328184
#define OFS_BAR1 2328504

// calciatori-capitano
#define OFS_KICKER 2329056

// nomi giocatori
#define OFS_NOMI_G 387792
#define OFS_NOMI_G2 390456
#define OFS_NOMI_G3 392808
#define OFS_NOMI_G4 395160
#define OFS_NOMI_G5 397512
#define OFS_NOMI_G6 399864
#define OFS_NOMI_G7 402216
#define OFS_NOMI_G8 404568

#define OFS_NOMI_GML 2006288
#define OFS_NOMI_GML2 2008632
#define OFS_NOMI_GML3 2010984

//caratteristiche
#define OFS_CARAT_G 2179492
#define OFS_CARAT_G1 2180328
#define OFS_CARAT_G2 2182680 //2352
#define OFS_CARAT_G3 2185032
#define OFS_CARAT_G4 2187384
#define OFS_CARAT_G5 2189736
#define OFS_CARAT_G6 2192088
#define OFS_CARAT_G7 2194440
#define OFS_CARAT_G8 2196792
#define OFS_CARAT_G9 2199144

#define OFS_CARAT_GML 2204112
#define OFS_CARAT_GML1 2206200
#define OFS_CARAT_GML2 2208552

// bandiere
#define OFS_BANDIERE_FORMA1 1929004
#define OFS_BANDIERE_FORMA2 2005412
#define OFS_BANDIERE_FORMA3 2328060
#define OFS_BANDIERE_FORMA4 4904664
#define OFS_BANDIERE_FORMA5 5711640
#define OFS_BANDIERE_COLORE 12549518
#define OFS_BANDIERE_COLORE1 12550296
#define OFS_BANDIERE_COLORE2 12552648
#define OFS_BANDIERE_COLORE_SEN 12545758

// costi giocatori per ml
#define OFS_COSTI_NAZ 3067404
#define OFS_COSTI_NC 3069512

// numeri ml
#define OFS_NUMERI_ML 2014504

// numeri nazionali
#define OFS_NUMERI_NAZ 404716

// tattiche
#define OFS_TATTICHE 2303700
#define OFS_TATTICHEA 2304984

// link ml
#define OFS_LINK_ML 2012680
#define OFS_LINK_ML1 2012728
#define OFS_LINK_ML2 2013336

// anteprima maglie
#define OFS_ANT_MAGLIE 2667256
#define OFS_ANT_MAGLIE1 2669544
#define OFS_ANT_MAGLIE2 2671896
#define OFS_ANT_MAGLIE3 2674248

// vettori lunghezza nomi 
// in ordine giusto naz-alls-ml
//compresi ultimo byte null di stacco

char lun_nomi1[95] = 
{
8,12,8,8,12,8,8,8,12,12,8,8,8,8,8,8,8,8,12,8,8,12,8,12,8,12,8,8,8,8,
8,8,8,8,12,16,8,12,8,12,12,8,8,8,12,8,12,8,8,8,8,8,16,12,
16,16,16,16,20,16,16,16,20,
8,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
};

char lun_nomi2[95] = 
{
8,12,8,12,12,8,8,8,8,8,8,8,8,8,8,12,12,12,8,8,8,8,8,12,8,12,8,
8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,8,4,12,8,12,8,8,8,8,8,12,12,
16,16,16,12,16,12,12,16,16,
8,8,8,12,8,8,16,8,8,12,12,12,12,12,8,12,
12,8,8,8,12,8,8,8,12,12,8,8,12,16,8,12
};

char lun_nomi3[95]=
{
8,12,8,8,12,8,8,8,12,12,8,8,8,8,8,8,8,8,12,8,8,12,8,12,8,12,
8,8,8,8,8,8,8,8,12,16,8,12,8,12,12,8,8,8,12,8,12,8,8,8,8,8,16,12,
16,16,16,16,20,16,16,16,20,
8,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
};

char lun_nomi4[95]=
{
8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,
8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,4,4,4,8,8,8,8,8,16,12,12,
12,12,12,16,8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,8,12,8,4,8,8,8,8,
8,8,12,8,4,8,12,8,8
};

char lun_nomi5[95]=
{
8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,4,
8,4,8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,12,8,
12,16,12,12,12,12,12,12,12,
8,8,8,8,8,8,12,8,8,8,8,12,12,8,8,8,
12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
};

char lun_nomi6[95]=
{
8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,
4,8,4,8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,
12,8,12,16,16,12,12,12,12,16,16,8,8,8,8,8,8,12,8,8,8,8,12,12,8,8,
8,12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
};

char lun_nomi_min[95]=
{
8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,4,8,4,8,
8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,12,8,12,16,
16,12,12,12,12,16,16,8,8,8,8,8,8,12,8,8,8,8,12,12,8,
8,8,12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
};

char lun_nomi_add1[32]=
{
8,8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,
12,8,4,8,8,8,8,8,8,12,8,4,8,12,8,9
};

char lun_nomi_add2[32]=
{
7,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
};


char lun_nomik[95] = 
{
8,8,6,8,6,6,6,6,6,6,6,6,6,6,6,8,8,6,6,8,6,6,6,8,6,6,6,6,6,6,
6,6,6,8,6,6,6,6,6,6,6,6,6,6,6,6,8,6,6,6,6,6,8,8,
12,12,14,12,12,12,10,12,14,
6,6,6,8,8,6,10,8,6,8,8,8,8,8,6,8,
10,6,6,6,8,6,6,6,8,10,6,6,8,10,6,6
};

#define N_RUOLI 21

char ruoli[N_RUOLI][6]=
{
"GK","CB SX","CB CN","SW","LIB","CB DX","LB","RB",
"DH SX","DH CN","DH DX","LH","RH","OH SX","OH CN","OH DX",
"CF SX","CF CN","CF DX","LW","RW"
};

/*************************/

void asciitokanji(unsigned char *as,unsigned char *kj,int l)
{
	int i;
	for(i=0;i<l-1;i++)
	{
		//lettere maiuscole
		if(as[i]>64 && as[i]<91)
		{
			kj[i*2] = (char)130;
			kj[(i*2)+1] = as[i]+31;//31 = 96-65, 96=0x(82)60 A in kanji, 65 = A in ascii
		//lettere minuscole
		} else if(as[i]>96 && as[i]<123)
		{
			kj[i*2] = (char)130;
			kj[(i*2)+1] = as[i]+(char)32;//32 = 129-97, 129=0x(82)81 a in kanji, 97 = a in ascii
		//numeri
		} else if(as[i]>47 && as[i]<58)
		{
			kj[i*2] = (char)130;
			kj[(i*2)+1] = as[i]+(char)31;//32 = 129-97, 129=0x(82)81 a in kanji, 97 = a in ascii
		//punto
		} else if(as[i] == 46)
		{
			kj[i*2] = (char)129;
			kj[(i*2)+1] = (char)66;
		//null
		} else if(as[i] == 0)
		{
			kj[i*2] = NULL;
			kj[(i*2)+1] = NULL;
		//default spazio
		} else
		{
			kj[i*2] = (char)130;
			kj[(i*2)+1] = (char)128;
		}
	}
	kj[i*2] = NULL;
	kj[(i*2)+1] = NULL;
}

void kanjitoascii(unsigned char *kj,unsigned char *as,int l)
{
	int i;
	char aux[40];
	for(i=0;i<(l-1)*2;i+=2) 
	{
		//lettere maiuscole
		if(kj[i] == 130 && kj[i+1]>95 && kj[i+1]<122)
		{
			aux[i] = kj[i+1]-(char)31;
		//lettere minuscole
		} else if(kj[i] == 130 && kj[i+1]>128 && kj[i+1]<155)
		{
			aux[i] = kj[i+1]-(char)32;
		//numeri
		} else if(kj[i] == 130 && kj[i+1]>78 && kj[i+1]<89)
		{
			aux[i] = kj[i+1]-(char)31;
		//punto
		} else if(kj[i] == 129 && kj[i+1] == 66)
		{
			aux[i] = (char)46;
		//null
		} else if(kj[i] == 0 && kj[i+1] == 0)
		{
			aux[i] = NULL;
		//default spazio
		} else
		{
			aux[i] = (char)32;
		}
	}
	for(i=0;i<l-1;i++) 
		as[i] = aux[i*2];

	as[i] = NULL;
}

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	virtual void OnOK();
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CEdDlg dialog

IMPLEMENT_DYNAMIC(CEdDlg, CDialog);

CEdDlg::CEdDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CEdDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CEdDlg)
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
	m_pAutoProxy = NULL;
}

CEdDlg::~CEdDlg()
{
	// If there is an automation proxy for this dialog, set
	//  its back pointer to this dialog to NULL, so it knows
	//  the dialog has been deleted.
//	if (m_pAutoProxy != NULL)
//		m_pAutoProxy->m_pDialog = NULL;
}

void CEdDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CEdDlg)		
	DDX_Control(pDX, CMD_TACT9, cmd_nometat9);
	DDX_Control(pDX, CMD_TACT8, cmd_nometat8);
	DDX_Control(pDX, CMD_TACT7, cmd_nometat7);
	DDX_Control(pDX, CMD_TACT6, cmd_nometat6);
	DDX_Control(pDX, CMD_TACT5, cmd_nometat5);
	DDX_Control(pDX, CMD_TACT4, cmd_nometat4);
	DDX_Control(pDX, CMD_TACT3, cmd_nometat3);
	DDX_Control(pDX, CMD_TACT2, cmd_nometat2);
	DDX_Control(pDX, CMD_TACT16, cmd_nometat16);
	DDX_Control(pDX, CMD_TACT15, cmd_nometat15);
	DDX_Control(pDX, CMD_TACT14, cmd_nometat14);
	DDX_Control(pDX, CMD_TACT13, cmd_nometat13);
	DDX_Control(pDX, CMD_TACT12, cmd_nometat12);
	DDX_Control(pDX, CMD_TACT11, cmd_nometat11);
	DDX_Control(pDX, CMD_TACT10, cmd_nometat10);
	DDX_Control(pDX, CMD_TACT1, cmd_nometat1);
	DDX_Control(pDX, LAB_NSQUADK, lbl_nome_squadk);
	DDX_Control(pDX, TXT_NSQUADK, txt_nome_squadk);
	DDX_Control(pDX, TXT_NSQUAD_A3, txt_nome_squad_a3);
	DDX_Control(pDX, CMB_KIK_RIG, cmb_kik_rig);
	DDX_Control(pDX, LBL_NOMEMLADD2, lbl_nome_add2);
	DDX_Control(pDX, LBL_NOMEMLADD1, lbl_nome_add1);
	DDX_Control(pDX, TXT_NOMIML2, txt_nomi_addml2);
	DDX_Control(pDX, TXT_NOMIML1, txt_nomi_addml1);
	DDX_Control(pDX, LAB_ML_NOMEADD, lbl_nomi_addml);
	DDX_Control(pDX, TXT_TATY11, txt_taty11);
	DDX_Control(pDX, TXT_TATX11, txt_tatx11);
	DDX_Control(pDX, TXT_GIOC9, txt_gioc9);
	DDX_Control(pDX, TXT_GIOC8, txt_gioc8);
	DDX_Control(pDX, TXT_GIOC7, txt_gioc7);
	DDX_Control(pDX, TXT_GIOC6, txt_gioc6);
	DDX_Control(pDX, TXT_GIOC5, txt_gioc5);
	DDX_Control(pDX, TXT_GIOC4, txt_gioc4);
	DDX_Control(pDX, TXT_GIOC3, txt_gioc3);
	DDX_Control(pDX, TXT_GIOC23, txt_gioc23);
	DDX_Control(pDX, TXT_GIOC22, txt_gioc22);
	DDX_Control(pDX, TXT_GIOC21, txt_gioc21);
	DDX_Control(pDX, TXT_GIOC20, txt_gioc20);
	DDX_Control(pDX, TXT_GIOC2, txt_gioc2);
	DDX_Control(pDX, TXT_GIOC19, txt_gioc19);
	DDX_Control(pDX, TXT_GIOC18, txt_gioc18);
	DDX_Control(pDX, TXT_GIOC17, txt_gioc17);
	DDX_Control(pDX, TXT_GIOC16, txt_gioc16);
	DDX_Control(pDX, TXT_GIOC15, txt_gioc15);
	DDX_Control(pDX, TXT_GIOC14, txt_gioc14);
	DDX_Control(pDX, TXT_GIOC13, txt_gioc13);
	DDX_Control(pDX, TXT_GIOC12, txt_gioc12);
	DDX_Control(pDX, TXT_GIOC11, txt_gioc11);
	DDX_Control(pDX, TXT_GIOC10, txt_gioc10);
	DDX_Control(pDX, TXT_GIOC1, txt_gioc1);
	//urls
	DDX_Control(pDX, TXT_URL1, txt_url_gioc1);
	DDX_Control(pDX, TXT_URL2, txt_url_gioc2);
	DDX_Control(pDX, TXT_URL3, txt_url_gioc3);
	DDX_Control(pDX, TXT_URL4, txt_url_gioc4);
	DDX_Control(pDX, TXT_URL5, txt_url_gioc5);
	DDX_Control(pDX, TXT_URL6, txt_url_gioc6);
	DDX_Control(pDX, TXT_URL7, txt_url_gioc7);
	DDX_Control(pDX, TXT_URL8, txt_url_gioc8);
	DDX_Control(pDX, TXT_URL9, txt_url_gioc9);
	DDX_Control(pDX, TXT_URL10, txt_url_gioc10);
	DDX_Control(pDX, TXT_URL11, txt_url_gioc11);
	DDX_Control(pDX, TXT_URL12, txt_url_gioc12);
	DDX_Control(pDX, TXT_URL13, txt_url_gioc13);
	DDX_Control(pDX, TXT_URL14, txt_url_gioc14);
	DDX_Control(pDX, TXT_URL15, txt_url_gioc15);
	DDX_Control(pDX, TXT_URL16, txt_url_gioc16);
	DDX_Control(pDX, TXT_URL17, txt_url_gioc17);
	DDX_Control(pDX, TXT_URL18, txt_url_gioc18);
	DDX_Control(pDX, TXT_URL19, txt_url_gioc19);
	DDX_Control(pDX, TXT_URL20, txt_url_gioc20);
	DDX_Control(pDX, TXT_URL21, txt_url_gioc21);
	DDX_Control(pDX, TXT_URL22, txt_url_gioc22);
	DDX_Control(pDX, TXT_URL23, txt_url_gioc23);
	//-
	DDX_Control(pDX, TXT_NUM9, txt_num_gioc9);
	DDX_Control(pDX, TXT_NUM8, txt_num_gioc8);
	DDX_Control(pDX, TXT_NUM7, txt_num_gioc7);
	DDX_Control(pDX, TXT_NUM6, txt_num_gioc6);
	DDX_Control(pDX, TXT_NUM5, txt_num_gioc5);
	DDX_Control(pDX, TXT_NUM4, txt_num_gioc4);
	DDX_Control(pDX, TXT_NUM3, txt_num_gioc3);
	DDX_Control(pDX, TXT_NUM23, txt_num_gioc23);
	DDX_Control(pDX, TXT_NUM22, txt_num_gioc22);
	DDX_Control(pDX, TXT_NUM21, txt_num_gioc21);
	DDX_Control(pDX, TXT_NUM20, txt_num_gioc20);
	DDX_Control(pDX, TXT_NUM2, txt_num_gioc2);
	DDX_Control(pDX, TXT_NUM19, txt_num_gioc19);
	DDX_Control(pDX, TXT_NUM18, txt_num_gioc18);
	DDX_Control(pDX, TXT_NUM17, txt_num_gioc17);
	DDX_Control(pDX, TXT_NUM16, txt_num_gioc16);
	DDX_Control(pDX, TXT_NUM15, txt_num_gioc15);
	DDX_Control(pDX, TXT_NUM14, txt_num_gioc14);
	DDX_Control(pDX, TXT_NUM13, txt_num_gioc13);
	DDX_Control(pDX, TXT_NUM12, txt_num_gioc12);
	DDX_Control(pDX, TXT_NUM11, txt_num_gioc11);
	DDX_Control(pDX, TXT_NUM10, txt_num_gioc10);
	DDX_Control(pDX, TXT_NUM1, txt_num_gioc1);
	DDX_Control(pDX, TXT_TATY9, txt_taty9);
	DDX_Control(pDX, TXT_TATY8, txt_taty8);
	DDX_Control(pDX, TXT_TATY7, txt_taty7);
	DDX_Control(pDX, TXT_TATY6, txt_taty6);
	DDX_Control(pDX, TXT_TATY5, txt_taty5);
	DDX_Control(pDX, TXT_TATY4, txt_taty4);
	DDX_Control(pDX, TXT_TATY3, txt_taty3);
	DDX_Control(pDX, TXT_TATY2, txt_taty2);
	DDX_Control(pDX, TXT_TATY10, txt_taty10);
	DDX_Control(pDX, TXT_TATX9, txt_tatx9);
	DDX_Control(pDX, TXT_TATX8, txt_tatx8);
	DDX_Control(pDX, TXT_TATX7, txt_tatx7);
	DDX_Control(pDX, TXT_TATX6, txt_tatx6);
	DDX_Control(pDX, TXT_TATX5, txt_tatx5);
	DDX_Control(pDX, TXT_TATX4, txt_tatx4);
	DDX_Control(pDX, TXT_TATX3, txt_tatx3);
	DDX_Control(pDX, TXT_TATX2, txt_tatx2);
	DDX_Control(pDX, TXT_TATX10, txt_tatx10);
	DDX_Control(pDX, TXT_NSQUAD6, txt_nome_squad6);
	DDX_Control(pDX, TXT_NSQUAD5, txt_nome_squad5);
	DDX_Control(pDX, TXT_NSQUAD4, txt_nome_squad4);
	DDX_Control(pDX, TXT_NSQUAD3, txt_nome_squad3);
	DDX_Control(pDX, TXT_NSQUAD2, txt_nome_squad2);
	DDX_Control(pDX, TXT_NSQUAD1, txt_nome_squad1);
	DDX_Control(pDX, TXT_NSQUAD_M, txt_nome_squad_m);
	DDX_Control(pDX, TXT_NSQUAD_A2, txt_nome_squad_a2);
	DDX_Control(pDX, TXT_NSQUAD_A1, txt_nome_squad_a1);
	DDX_Control(pDX, TXT_BAR_TEC, txt_bar_tec);
	DDX_Control(pDX, TXT_BAR_SPE, txt_bar_spe);
	DDX_Control(pDX, TXT_BAR_POW, txt_bar_pow);
	DDX_Control(pDX, TXT_BAR_OFF, txt_bar_off);
	DDX_Control(pDX, TXT_BAR_DEF, txt_bar_def);
	DDX_Control(pDX, LAB_NSQUAD6, lab_nome_squad6);
	DDX_Control(pDX, LAB_NSQUAD5, lab_nome_squad5);
	DDX_Control(pDX, LAB_NSQUAD4, lab_nome_squad4);
	DDX_Control(pDX, LAB_NSQUAD3, lab_nome_squad3);
	DDX_Control(pDX, LAB_NSQUAD2, lab_nome_squad2);
	DDX_Control(pDX, LAB_NSQUAD1, lab_nome_squad1);
	DDX_Control(pDX, LAB_NSQUAD_M, lab_nome_squad_m);
	DDX_Control(pDX, LAB_NSQUAD_A2, lab_nome_squad_a2);
	DDX_Control(pDX, LAB_NSQUAD_A1, lab_nome_squad_a1);
	DDX_Control(pDX, CMD_VT9, cmd_visual_tat9);
	DDX_Control(pDX, CMD_VT8, cmd_visual_tat8);
	DDX_Control(pDX, CMD_VT7, cmd_visual_tat7);
	DDX_Control(pDX, CMD_VT6, cmd_visual_tat6);
	DDX_Control(pDX, CMD_VT5, cmd_visual_tat5);
	DDX_Control(pDX, CMD_VT4, cmd_visual_tat4);
	DDX_Control(pDX, CMD_VT3, cmd_visual_tat3);
	DDX_Control(pDX, CMD_VT2, cmd_visual_tat2);
	DDX_Control(pDX, CMD_VT10, cmd_visual_tat10);
	DDX_Control(pDX, CMD_VT1, cmd_visual_tat1);
	DDX_Control(pDX, CMD_SOST9, cmb_sost9);
	DDX_Control(pDX, CMD_SOST8, cmb_sost8);
	DDX_Control(pDX, CMD_SOST7, cmb_sost7);
	DDX_Control(pDX, CMD_SOST6, cmb_sost6);
	DDX_Control(pDX, CMD_SOST5, cmb_sost5);
	DDX_Control(pDX, CMD_SOST4, cmb_sost4);
	DDX_Control(pDX, CMD_SOST3, cmb_sost3);
	DDX_Control(pDX, CMD_SOST23, cmb_sost23);
	DDX_Control(pDX, CMD_SOST22, cmb_sost22);
	DDX_Control(pDX, CMD_SOST21, cmb_sost21);
	DDX_Control(pDX, CMD_SOST20, cmb_sost20);
	DDX_Control(pDX, CMD_SOST2, cmb_sost2);
	DDX_Control(pDX, CMD_SOST19, cmb_sost19);
	DDX_Control(pDX, CMD_SOST18, cmb_sost18);
	DDX_Control(pDX, CMD_SOST17, cmb_sost17);
	DDX_Control(pDX, CMD_SOST16, cmb_sost16);
	DDX_Control(pDX, CMD_SOST15, cmb_sost15);
	DDX_Control(pDX, CMD_SOST14, cmb_sost14);
	DDX_Control(pDX, CMD_SOST13, cmb_sost13);
	DDX_Control(pDX, CMD_SOST12, cmb_sost12);
	DDX_Control(pDX, CMD_SOST11, cmb_sost11);
	DDX_Control(pDX, CMD_SOST10, cmb_sost10);
	DDX_Control(pDX, CMD_SOST1, cmb_sost1);
	DDX_Control(pDX, CMB_TAT7, cmb_tat7);
	DDX_Control(pDX, CMB_TAT9, cmb_tat9);
	DDX_Control(pDX, CMB_TAT8, cmb_tat8);
	DDX_Control(pDX, CMB_TAT6, cmb_tat6);
	DDX_Control(pDX, CMB_TAT5, cmb_tat5);
	DDX_Control(pDX, CMB_TAT4, cmb_tat4);
	DDX_Control(pDX, CMB_TAT3, cmb_tat3);
	DDX_Control(pDX, CMB_TAT2, cmb_tat2);
	DDX_Control(pDX, CMB_TAT10, cmb_tat10);
	DDX_Control(pDX, CMB_TAT11, cmb_tat11);
	DDX_Control(pDX, CMB_NSQUADRE, cmb_squadra);
	DDX_Control(pDX, CMB_KIK_PUNL, cmb_kik_punl);
	DDX_Control(pDX, CMB_KIK_PUNC, cmb_kik_punc);
	DDX_Control(pDX, CMB_KIK_CAP, cmb_kik_cap);
	DDX_Control(pDX, CMB_KIK_ANGSX, cmb_kik_angsx);
	DDX_Control(pDX, CMB_KIK_ANGDX, cmb_kik_angdx);
	DDX_Control(pDX, CAMPO_, frm_tat_campo);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CEdDlg, CDialog)
	//{{AFX_MSG_MAP(CEdDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_WM_CLOSE()
	ON_WM_CANCELMODE()
	ON_CBN_SELCHANGE(CMB_NSQUADRE, OnSelezioneSquadraV)
	ON_CBN_SELCHANGE(CMB_TAT2, OnSelchangeTat2)
	ON_CBN_SELCHANGE(CMB_TAT3, OnSelchangeTat3)
	ON_CBN_SELCHANGE(CMB_TAT4, OnSelchangeTat4)
	ON_CBN_SELCHANGE(CMB_TAT5, OnSelchangeTat5)
	ON_CBN_SELCHANGE(CMB_TAT6, OnSelchangeTat6)
	ON_CBN_SELCHANGE(CMB_TAT7, OnSelchangeTat7)
	ON_CBN_SELCHANGE(CMB_TAT8, OnSelchangeTat8)
	ON_CBN_SELCHANGE(CMB_TAT9, OnSelchangeTat9)
	ON_CBN_SELCHANGE(CMB_TAT10, OnSelchangeTat10)
	ON_CBN_SELCHANGE(CMB_TAT11, OnSelchangeTat11)
	ON_EN_CHANGE(TXT_TATX2, OnChangeTatx2)
	ON_EN_CHANGE(TXT_TATX3, OnChangeTatx3)
	ON_EN_CHANGE(TXT_TATX4, OnChangeTatx4)
	ON_EN_CHANGE(TXT_TATX5, OnChangeTatx5)
	ON_EN_CHANGE(TXT_TATX6, OnChangeTatx6)
	ON_EN_CHANGE(TXT_TATX7, OnChangeTatx7)
	ON_EN_CHANGE(TXT_TATX8, OnChangeTatx8)
	ON_EN_CHANGE(TXT_TATX9, OnChangeTatx9)
	ON_EN_CHANGE(TXT_TATX10, OnChangeTatx10)
	ON_EN_CHANGE(TXT_TATX11, OnChangeTatx11)
	ON_EN_CHANGE(TXT_TATY2, OnChangeTaty2)
	ON_EN_CHANGE(TXT_TATY3, OnChangeTaty3)
	ON_EN_CHANGE(TXT_TATY4, OnChangeTaty4)
	ON_EN_CHANGE(TXT_TATY5, OnChangeTaty5)
	ON_EN_CHANGE(TXT_TATY6, OnChangeTaty6)
	ON_EN_CHANGE(TXT_TATY7, OnChangeTaty7)
	ON_EN_CHANGE(TXT_TATY8, OnChangeTaty8)
	ON_EN_CHANGE(TXT_TATY9, OnChangeTaty9)
	ON_EN_CHANGE(TXT_TATY10, OnChangeTaty10)
	ON_EN_CHANGE(TXT_TATY11, OnChangeTaty11)
	ON_EN_CHANGE(TXT_URL1, OnChangeURL1)
	ON_EN_CHANGE(TXT_URL2, OnChangeURL2)
	ON_EN_CHANGE(TXT_URL3, OnChangeURL3)
	ON_EN_CHANGE(TXT_URL4, OnChangeURL4)
	ON_EN_CHANGE(TXT_URL5, OnChangeURL5)
	ON_EN_CHANGE(TXT_URL6, OnChangeURL6)
	ON_EN_CHANGE(TXT_URL7, OnChangeURL7)
	ON_EN_CHANGE(TXT_URL8, OnChangeURL8)
	ON_EN_CHANGE(TXT_URL9, OnChangeURL9)
	ON_EN_CHANGE(TXT_URL10, OnChangeURL10)
	ON_EN_CHANGE(TXT_URL11, OnChangeURL11)
	ON_EN_CHANGE(TXT_URL12, OnChangeURL12)
	ON_EN_CHANGE(TXT_URL13, OnChangeURL13)
	ON_EN_CHANGE(TXT_URL14, OnChangeURL14)
	ON_EN_CHANGE(TXT_URL15, OnChangeURL15)
	ON_EN_CHANGE(TXT_URL16, OnChangeURL16)
	ON_EN_CHANGE(TXT_URL17, OnChangeURL17)
	ON_EN_CHANGE(TXT_URL18, OnChangeURL18)
	ON_EN_CHANGE(TXT_URL19, OnChangeURL19)
	ON_EN_CHANGE(TXT_URL20, OnChangeURL20)
	ON_EN_CHANGE(TXT_URL21, OnChangeURL21)
	ON_EN_CHANGE(TXT_URL22, OnChangeURL22)
	ON_EN_CHANGE(TXT_URL23, OnChangeURL23)
	ON_EN_KILLFOCUS(TXT_TATX2, OnKillfocusTatx2)
	ON_EN_KILLFOCUS(TXT_TATX3, OnKillfocusTatx3)
	ON_EN_KILLFOCUS(TXT_TATX4, OnKillfocusTatx4)
	ON_EN_KILLFOCUS(TXT_TATX5, OnKillfocusTatx5)
	ON_EN_KILLFOCUS(TXT_TATX6, OnKillfocusTatx6)
	ON_EN_KILLFOCUS(TXT_TATX7, OnKillfocusTatx7)
	ON_EN_KILLFOCUS(TXT_TATX8, OnKillfocusTatx8)
	ON_EN_KILLFOCUS(TXT_TATX9, OnKillfocusTatx9)
	ON_EN_KILLFOCUS(TXT_TATX10, OnKillfocusTatx10)
	ON_EN_KILLFOCUS(TXT_TATX11, OnKillfocusTatx11)
	ON_EN_KILLFOCUS(TXT_TATY10, OnKillfocusTaty10)
	ON_EN_KILLFOCUS(TXT_TATY11, OnKillfocusTaty11)
	ON_EN_KILLFOCUS(TXT_TATY2, OnKillfocusTaty2)
	ON_EN_KILLFOCUS(TXT_TATY3, OnKillfocusTaty3)
	ON_EN_KILLFOCUS(TXT_TATY4, OnKillfocusTaty4)
	ON_EN_KILLFOCUS(TXT_TATY5, OnKillfocusTaty5)
	ON_EN_KILLFOCUS(TXT_TATY6, OnKillfocusTaty6)
	ON_EN_KILLFOCUS(TXT_TATY7, OnKillfocusTaty7)
	ON_EN_KILLFOCUS(TXT_TATY8, OnKillfocusTaty8)
	ON_EN_KILLFOCUS(TXT_TATY9, OnKillfocusTaty9)
	ON_BN_CLICKED(CMD_TACT1, On451a)
	ON_BN_CLICKED(CMD_TACT2, On451b)
	ON_BN_CLICKED(CMD_TACT3, On442a)
	ON_BN_CLICKED(CMD_TACT4, On442b)
	ON_BN_CLICKED(CMD_TACT5, On433a)
	ON_BN_CLICKED(CMD_TACT6, On433b)
	ON_BN_CLICKED(CMD_TACT7, On361a)
	ON_BN_CLICKED(CMD_TACT8, On361b)
	ON_BN_CLICKED(CMD_TACT9, On352a)
	ON_BN_CLICKED(CMD_TACT10, On352b)
	ON_BN_CLICKED(CMD_TACT11, On343a)
	ON_BN_CLICKED(CMD_TACT12, On343b)
	ON_BN_CLICKED(CMD_TACT13, On541a)
	ON_BN_CLICKED(CMD_TACT14, On541b)
	ON_BN_CLICKED(CMD_TACT15, On532a)
	ON_BN_CLICKED(CMD_TACT16, On532b)
	ON_BN_CLICKED(CMD_COPIA_NOMISQUADRA, OnCopiaNomisquadra)
	ON_BN_CLICKED(CMB_WRITE, OnWriteCD)
	ON_BN_CLICKED(CMB_IMPFIFAWEB, OnImportSoFIFAWeb)
	ON_BN_CLICKED(CMB_IMPFIFATXT, OnImportSoFIFATxt)
	ON_BN_CLICKED(CMB_EDITALLTXT, OnEditAllFromFIFA)
	ON_BN_CLICKED(CMB_SHOWEDITOPT, OnEditOptForm)
	ON_BN_CLICKED(CMB_EDITALLLOOK, OnEditAllPlayersLook)
	ON_BN_CLICKED(CMB_EDITALLBARS, OnEditAllBars)
	ON_CBN_KILLFOCUS(CMB_TAT2, OnKillfocusTat2)
	ON_CBN_KILLFOCUS(CMB_TAT3, OnKillfocusTat3)
	ON_CBN_KILLFOCUS(CMB_TAT4, OnKillfocusTat4)
	ON_CBN_KILLFOCUS(CMB_TAT5, OnKillfocusTat5)
	ON_CBN_KILLFOCUS(CMB_TAT6, OnKillfocusTat6)
	ON_CBN_KILLFOCUS(CMB_TAT7, OnKillfocusTat7)
	ON_CBN_KILLFOCUS(CMB_TAT8, OnKillfocusTat8)
	ON_CBN_KILLFOCUS(CMB_TAT9, OnKillfocusTat9)
	ON_CBN_KILLFOCUS(CMB_TAT10, OnKillfocusTat10)
	ON_CBN_KILLFOCUS(CMB_TAT11, OnKillfocusTat11)
	ON_EN_KILLFOCUS(TXT_NSQUAD1, OnKillfocusNsquad1)
	ON_EN_KILLFOCUS(TXT_NSQUAD2, OnKillfocusNsquad2)
	ON_EN_KILLFOCUS(TXT_NSQUAD3, OnKillfocusNsquad3)
	ON_EN_KILLFOCUS(TXT_NSQUAD4, OnKillfocusNsquad4)
	ON_EN_KILLFOCUS(TXT_NSQUAD5, OnKillfocusNsquad5)
	ON_EN_KILLFOCUS(TXT_NSQUAD6, OnKillfocusNsquad6)
	ON_EN_KILLFOCUS(TXT_NSQUAD_M, OnKillfocusNsquadM)
	ON_EN_KILLFOCUS(TXT_NSQUAD_A1, OnKillfocusNsquadA1)
	ON_EN_KILLFOCUS(TXT_NSQUAD_A2, OnKillfocusNsquadA2)
	ON_EN_KILLFOCUS(TXT_NOMIML1, OnKillfocusNomiml1)
	ON_EN_KILLFOCUS(TXT_NOMIML2, OnKillfocusNomiml2)
	ON_EN_KILLFOCUS(TXT_BAR_OFF, OnKillfocusBarOff)
	ON_EN_KILLFOCUS(TXT_BAR_DEF, OnKillfocusBarDef)
	ON_EN_KILLFOCUS(TXT_BAR_POW, OnKillfocusBarPow)
	ON_EN_KILLFOCUS(TXT_BAR_SPE, OnKillfocusBarSpe)
	ON_EN_KILLFOCUS(TXT_BAR_TEC, OnKillfocusBarTec)
	ON_CBN_KILLFOCUS(CMB_KIK_PUNL, OnKillfocusKikPunl)
	ON_CBN_KILLFOCUS(CMB_KIK_PUNC, OnKillfocusKikPunc)
	ON_CBN_KILLFOCUS(CMB_KIK_CAP, OnKillfocusKikCap)
	ON_CBN_KILLFOCUS(CMB_KIK_ANGSX, OnKillfocusKikAngsx)
	ON_CBN_KILLFOCUS(CMB_KIK_ANGDX, OnKillfocusKikAngdx)
	ON_CBN_KILLFOCUS(CMB_KIK_RIG, OnKillfocusKikRig)
	ON_EN_KILLFOCUS(TXT_NSQUAD_A3, OnKillfocusNsquadA3)
	ON_EN_KILLFOCUS(TXT_NUM1, OnKillfocusNum1)
	ON_EN_KILLFOCUS(TXT_NUM2, OnKillfocusNum2)
	ON_EN_KILLFOCUS(TXT_NUM3, OnKillfocusNum3)
	ON_EN_KILLFOCUS(TXT_NUM4, OnKillfocusNum4)
	ON_EN_KILLFOCUS(TXT_NUM5, OnKillfocusNum5)
	ON_EN_KILLFOCUS(TXT_NUM6, OnKillfocusNum6)
	ON_EN_KILLFOCUS(TXT_NUM7, OnKillfocusNum7)
	ON_EN_KILLFOCUS(TXT_NUM8, OnKillfocusNum8)
	ON_EN_KILLFOCUS(TXT_NUM9, OnKillfocusNum9)
	ON_EN_KILLFOCUS(TXT_NUM10, OnKillfocusNum10)
	ON_EN_KILLFOCUS(TXT_NUM11, OnKillfocusNum11)
	ON_EN_KILLFOCUS(TXT_NUM12, OnKillfocusNum12)
	ON_EN_KILLFOCUS(TXT_NUM13, OnKillfocusNum13)
	ON_EN_KILLFOCUS(TXT_NUM14, OnKillfocusNum14)
	ON_EN_KILLFOCUS(TXT_NUM15, OnKillfocusNum15)
	ON_EN_KILLFOCUS(TXT_NUM16, OnKillfocusNum16)
	ON_EN_KILLFOCUS(TXT_NUM17, OnKillfocusNum17)
	ON_EN_KILLFOCUS(TXT_NUM18, OnKillfocusNum18)
	ON_EN_KILLFOCUS(TXT_NUM19, OnKillfocusNum19)
	ON_EN_KILLFOCUS(TXT_NUM20, OnKillfocusNum20)
	ON_EN_KILLFOCUS(TXT_NUM21, OnKillfocusNum21)
	ON_EN_KILLFOCUS(TXT_NUM22, OnKillfocusNum22)
	ON_EN_KILLFOCUS(TXT_NUM23, OnKillfocusNum23)
	ON_BN_CLICKED(CMD_CARAT1, OnCarat1)
	ON_BN_CLICKED(CMD_CARAT2, OnCarat2)
	ON_BN_CLICKED(CMD_CARAT3, OnCarat3)
	ON_BN_CLICKED(CMD_CARAT4, OnCarat4)
	ON_BN_CLICKED(CMD_CARAT5, OnCarat5)
	ON_BN_CLICKED(CMD_CARAT6, OnCarat6)
	ON_BN_CLICKED(CMD_CARAT7, OnCarat7)
	ON_BN_CLICKED(CMD_CARAT8, OnCarat8)
	ON_BN_CLICKED(CMD_CARAT9, OnCarat9)
	ON_BN_CLICKED(CMD_CARAT10, OnCarat10)
	ON_BN_CLICKED(CMD_CARAT11, OnCarat11)
	ON_BN_CLICKED(CMD_CARAT12, OnCarat12)
	ON_BN_CLICKED(CMD_CARAT13, OnCarat13)
	ON_BN_CLICKED(CMD_CARAT14, OnCarat14)
	ON_BN_CLICKED(CMD_CARAT15, OnCarat15)
	ON_BN_CLICKED(CMD_CARAT16, OnCarat16)
	ON_BN_CLICKED(CMD_CARAT17, OnCarat17)
	ON_BN_CLICKED(CMD_CARAT18, OnCarat18)
	ON_BN_CLICKED(CMD_CARAT19, OnCarat19)
	ON_BN_CLICKED(CMD_CARAT20, OnCarat20)
	ON_BN_CLICKED(CMD_CARAT21, OnCarat21)
	ON_BN_CLICKED(CMD_CARAT22, OnCarat22)
	ON_BN_CLICKED(CMD_CARAT23, OnCarat23)
	ON_BN_CLICKED(CMD_SOST1, OnSost1)
	ON_BN_CLICKED(CMD_SOST2, OnSost2)
	ON_BN_CLICKED(CMD_SOST3, OnSost3)
	ON_BN_CLICKED(CMD_SOST4, OnSost4)
	ON_BN_CLICKED(CMD_SOST5, OnSost5)
	ON_BN_CLICKED(CMD_SOST6, OnSost6)
	ON_BN_CLICKED(CMD_SOST7, OnSost7)
	ON_BN_CLICKED(CMD_SOST8, OnSost8)
	ON_BN_CLICKED(CMD_SOST9, OnSost9)
	ON_BN_CLICKED(CMD_SOST10, OnSost10)
	ON_BN_CLICKED(CMD_SOST11, OnSost11)
	ON_BN_CLICKED(CMD_SOST12, OnSost12)
	ON_BN_CLICKED(CMD_SOST13, OnSost13)
	ON_BN_CLICKED(CMD_SOST14, OnSost14)
	ON_BN_CLICKED(CMD_SOST15, OnSost15)
	ON_BN_CLICKED(CMD_SOST16, OnSost16)
	ON_BN_CLICKED(CMD_SOST17, OnSost17)
	ON_BN_CLICKED(CMD_SOST18, OnSost18)
	ON_BN_CLICKED(CMD_SOST19, OnSost19)
	ON_BN_CLICKED(CMD_SOST20, OnSost20)
	ON_BN_CLICKED(CMD_SOST21, OnSost21)
	ON_BN_CLICKED(CMD_SOST22, OnSost22)
	ON_BN_CLICKED(CMD_SOST23, OnSost23)
	ON_BN_CLICKED(IDC_BUTTON2, OnEsporta)
	ON_BN_CLICKED(IDC_BUTTON1, OnImporta)
	ON_EN_KILLFOCUS(TXT_NSQUADK, OnKillfocusNsquadk)
	ON_BN_CLICKED(IDC_BUTTGRAF, OnButtgraf)
	ON_BN_CLICKED(CMD_NUMDEF, OnNumeriDefault)
	ON_BN_CLICKED(CMB_RELOAD, OnReload)
	ON_BN_CLICKED(CMD_CALCCOSTI, OnCalcolaCostiML)
	ON_BN_CLICKED(CMD_CALCFORZA2, OnOrdinaPanchina)
	ON_BN_CLICKED(CMD_IMP_TOT, OnImportaTot)
	ON_BN_CLICKED(CMD_ESP_TOT, OnEsportaTot)
	ON_BN_CLICKED(CMD_TATT_PREDEF, OnTattPredef)
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CEdDlg message handlers

BOOL CEdDlg::OnInitDialog()
{
	int i;
	char auxch[40];
	char strint[3];

	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// --------------------------
	/**/
	
	if(! aprifilebin("WE2002 CD Image (we2002.bin)|we2002.bin|Binary file (*.bin)|*.bin|All file (*.*)|*.*||"))
	{
		return FALSE;
	}
//	fil_nomeCD = "C:\\Documenti\\iss\\we2002.bin";
	carica_dabin();
	carica_url();
	carica_SOFIFAFields();
	carica_SOFIFAConversionRules();

	cmb_squadra.AddString("---");
	for(i=0;i<SQUADRE_NAZ;i++)
	{
		_itoa(i+1, strint, 10);
		strcpy(auxch, "Nation ");
		strcat(auxch, strint);
		strcat(auxch, " - ");
		strcat(auxch, nomi_squadre[i]);
		cmb_squadra.AddString(auxch);
	}
	for(i=0;i<SQUADRE_ALLS;i++)
	{
		_itoa(i+1, strint, 10);
		strcpy(auxch, "All-star ");
		strcat(auxch, strint);
		strcat(auxch, " - ");
		strcat(auxch, nomi_squadre[i+54]);
		cmb_squadra.AddString(auxch);
	}
	for(i=0;i<SQUADRE_ML;i++)
	{
		_itoa(i+1, strint, 10);
		strcpy(auxch, "Master League ");
		strcat(auxch, strint);
		strcat(auxch, " - ");
		strcat(auxch, nomi_squadre[i+63]);
		cmb_squadra.AddString(auxch);
	}
	cmb_squadra.AddString("Master League (default)");
	cmb_squadra.SetCurSel(0);
	
	txt_gioc1.LimitText(10);
	txt_gioc2.LimitText(10);
	txt_gioc3.LimitText(10);
	txt_gioc4.LimitText(10);
	txt_gioc5.LimitText(10);
	txt_gioc6.LimitText(10);
	txt_gioc7.LimitText(10);
	txt_gioc8.LimitText(10);
	txt_gioc9.LimitText(10);
	txt_gioc10.LimitText(10);
	txt_gioc11.LimitText(10);
	txt_gioc12.LimitText(10);
	txt_gioc13.LimitText(10);
	txt_gioc14.LimitText(10);
	txt_gioc15.LimitText(10);
	txt_gioc16.LimitText(10);
	txt_gioc17.LimitText(10);
	txt_gioc18.LimitText(10);
	txt_gioc19.LimitText(10);
	txt_gioc20.LimitText(10);
	txt_gioc21.LimitText(10);
	txt_gioc22.LimitText(10);
	txt_gioc23.LimitText(10);

	txt_nome_squad_a1.LimitText(3);
	txt_nome_squad_a2.LimitText(3);
	txt_nome_squad_a3.LimitText(3);
	
	txt_bar_def.LimitText(1);
	txt_bar_off.LimitText(1);
	txt_bar_pow.LimitText(1);
	txt_bar_spe.LimitText(1);
	txt_bar_tec.LimitText(1);

	txt_num_gioc1.LimitText(2);
	txt_num_gioc2.LimitText(2);
	txt_num_gioc3.LimitText(2);
	txt_num_gioc4.LimitText(2);
	txt_num_gioc5.LimitText(2);
	txt_num_gioc6.LimitText(2);
	txt_num_gioc7.LimitText(2);
	txt_num_gioc8.LimitText(2);
	txt_num_gioc9.LimitText(2);
	txt_num_gioc10.LimitText(2);
	txt_num_gioc11.LimitText(2);
	txt_num_gioc12.LimitText(2);
	txt_num_gioc13.LimitText(2);
	txt_num_gioc14.LimitText(2);
	txt_num_gioc15.LimitText(2);
	txt_num_gioc16.LimitText(2);
	txt_num_gioc17.LimitText(2);
	txt_num_gioc18.LimitText(2);
	txt_num_gioc19.LimitText(2);
	txt_num_gioc20.LimitText(2);
	txt_num_gioc21.LimitText(2);
	txt_num_gioc22.LimitText(2);
	txt_num_gioc23.LimitText(2);

	txt_tatx2.LimitText(2);
	txt_tatx3.LimitText(2);
	txt_tatx4.LimitText(2);
	txt_tatx5.LimitText(2);
	txt_tatx6.LimitText(2);
	txt_tatx7.LimitText(2);
	txt_tatx8.LimitText(2);
	txt_tatx9.LimitText(2);
	txt_tatx10.LimitText(2);
	txt_tatx11.LimitText(2);

	txt_taty2.LimitText(3);
	txt_taty3.LimitText(3);
	txt_taty4.LimitText(3);
	txt_taty5.LimitText(3);
	txt_taty6.LimitText(3);
	txt_taty7.LimitText(3);
	txt_taty8.LimitText(3);
	txt_taty9.LimitText(3);
	txt_taty10.LimitText(3);
	txt_taty11.LimitText(3);

	// ruoli x tattiche
	for(i=1;i<N_RUOLI;i++)
	{
		cmb_tat2.AddString(ruoli[i]);
		cmb_tat3.AddString(ruoli[i]);
		cmb_tat4.AddString(ruoli[i]);
		cmb_tat5.AddString(ruoli[i]);
		cmb_tat6.AddString(ruoli[i]);
		cmb_tat7.AddString(ruoli[i]);
		cmb_tat8.AddString(ruoli[i]);
		cmb_tat9.AddString(ruoli[i]);
		cmb_tat10.AddString(ruoli[i]);
		cmb_tat11.AddString(ruoli[i]);
 	}
	aggiornaNtatt();

	dlg_edopt.edit_names=1;
	dlg_edopt.edit_age_height_weight_foot=1;
	dlg_edopt.edit_characteristics=1;
	dlg_edopt.edit_shirt_numbers=1;

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CEdDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CEdDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

HCURSOR CEdDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CEdDlg::OnClose() 
{
	if (CanExit())
		CDialog::OnClose();
}

void CEdDlg::OnOK() 
{
	if (CanExit())
		CDialog::OnOK();
}

void CEdDlg::OnCancel() 
{
	if (CanExit())
		CDialog::OnCancel();
}

BOOL CEdDlg::CanExit()
{
	return TRUE;
}

void CAboutDlg::OnOK() 
{
	CDialog::OnOK();
}

void CEdDlg::OnCancelMode() 
{
	CDialog::OnCancelMode();
	
	// TODO: Add your message handler code here
	
}

BOOL CEdDlg::aprifilebin(char *filtro)
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

 	CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "IMAGE CD SELECTION";
	if( IDOK == dlg.DoModal() )
		fil_nomeCD = dlg.m_ofn.lpstrFile;
	else
	{
		AfxMessageBox("Impossible editing without CD image !");
		return FALSE;
	}
	CFile fil_ctrl(fil_nomeCD, CFile::modeRead | CFile::typeBinary);
	if(fil_ctrl.GetLength() != 474431328)
	{
		AfxMessageBox("Not WE2002 CD image (474.431.328 bytes)! Suggest to close the program !");
//		return FALSE;
	}
	
	fil_ctrl.Close();
	return TRUE;

}

void CEdDlg::carica_url()
{
	int i;

	CString fil_nomeURL;
	fil_nomeURL = fil_nomeCD;
	fil_nomeURL.Replace( ".bin", "_url.txt" );

	string line;
	ifstream fil_url;
	fil_url.open (fil_nomeURL);
	if (fil_url.is_open())
	{
		for(i=0;i<GIOCATORI_TOT;i++)
		{
			getline (fil_url,line); 
			strcpy(gioc[i].url, line.c_str());
		}		
		fil_url.close();
	}
	else
	{
		for(i=0;i<GIOCATORI_TOT;i++)
		{
			strcpy(gioc[i].url, "");
		}
	}
}

void CEdDlg::carica_dabin()
{
	int i,j;
	unsigned short auxcol[16];
	char auxstr[50], auxstr1[50], auxnome[11];
	CFile fil_ctrl;
	if(fil_ctrl.Open(fil_nomeCD, CFile::modeRead | CFile::typeBinary) == 0)
	{
		AfxMessageBox("Error ! Impossible to open CD image !");
		return;
	}

// squadre
	//caricare i nomi 
		// lotto kanji - ml
	fil_ctrl.Seek(OFS_NOMI_SQK, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(&squad_ml[31-i].nomekanji,lun_nomik[94-i]*2);
		kanjitoascii((unsigned char*)squad_ml[31-i].nomekanji, (unsigned char*)squad_ml[31-i].nomek, lun_nomik[94-i]);
	}
	for(i = 0;i < 63;i ++)
	{
		if(i == 58)
		{
			fil_ctrl.Read(&squad_nazall[62-i].nomekanji,4);
			fil_ctrl.Seek(OFS_NOMI_SQK1, CFile::begin);
			fil_ctrl.Read(auxstr,8);
			for(j = 0;j < 8;j++)
				squad_nazall[62-i].nomekanji[4+j] = auxstr[j];
		} else
			fil_ctrl.Read(&squad_nazall[62-i].nomekanji,lun_nomik[62-i]*2);
		kanjitoascii((unsigned char*)squad_nazall[62-i].nomekanji, (unsigned char*)squad_nazall[62-i].nomek, lun_nomik[62-i]);
	}

		//1° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi1[94-i]);
		strcpy(squad_ml[31-i].nomi[0],auxstr);
	}
		//1° lotto - naz/alls - salto - jugoslavia (24°)
	for(i = 0;i < 63;i ++)
	{
		if(i == 40)
			fil_ctrl.Seek(OFS_NOMI_SQ1A, CFile::begin);
		fil_ctrl.Read(auxstr,lun_nomi1[62-i]);
		strcpy(squad_nazall[62-i].nomi[0],auxstr);
	}
		//2° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi2[94-i]);
		strcpy(squad_ml[31-i].nomi[1],auxstr);
	}
		//2° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi2[62-i]);
		strcpy(squad_nazall[62-i].nomi[1],auxstr);
	}
		//3° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ3, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi3[94-i]);
		strcpy(squad_ml[31-i].nomi[2],auxstr);
	}
		//3° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi3[62-i]);
		strcpy(squad_nazall[62-i].nomi[2],auxstr);
	}

		//4° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ4, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi4[94-i]);
		strcpy(squad_ml[31-i].nomi[3],auxstr);
	}
		//4° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi4[62-i]);
		strcpy(squad_nazall[62-i].nomi[3],auxstr);
	}
		//5° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ5, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi5[94-i]);
		strcpy(squad_ml[31-i].nomi[4],auxstr);
	}
		//5° lotto - naz/alls - salto - francia (7°)
	for(i = 0;i < 63;i ++)
	{
		if(i == 57)
		{
			fil_ctrl.Read(auxstr1, 4);
			auxstr1[4] = NULL;
			strcpy(auxstr, auxstr1);
			fil_ctrl.Seek(OFS_NOMI_SQ5A, CFile::begin);
			fil_ctrl.Read(auxstr1, 4);
			strcat(auxstr, auxstr1);
		} else
			fil_ctrl.Read(auxstr,lun_nomi5[62-i]);
		strcpy(squad_nazall[62-i].nomi[4],auxstr);
	}
		//6° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ6, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		if(i == 15)
			fil_ctrl.Seek(OFS_NOMI_SQ6A, CFile::begin);
		fil_ctrl.Read(auxstr,lun_nomi6[94-i]);
		strcpy(squad_ml[31-i].nomi[5],auxstr);
	}
		//6° lotto - naz/alls 
	fil_ctrl.Seek(OFS_NOMI_SQ6B, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi6[62-i]);
		strcpy(squad_nazall[62-i].nomi[5],auxstr);
	}
		//minuscolo - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_M, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi_min[94-i]);
		strcpy(squad_ml[31-i].nome_m,auxstr);
	}
		//minuscolo - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi_min[62-i]);
		strcpy(squad_nazall[62-i].nome_m,auxstr);
	}
		//abbrev.1 - ml
	auxstr1[4] = NULL;
	fil_ctrl.Seek(OFS_NOMI_SQ_AB1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_ml[31-i].nomi_a[0],auxstr1);
	}
		//abbrev.1 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_nazall[62-i].nomi_a[0],auxstr1);
	}
		//abbrev.2 - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_AB2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_ml[31-i].nomi_a[1],auxstr1);
	}
		//abbrev.2 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_nazall[62-i].nomi_a[1],auxstr1);
	}
		//abbrev.3 - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_AB3, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_ml[31-i].nomi_a[2],auxstr1);
	}
		//abbrev.3 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr1,4);
		strcpy(squad_nazall[62-i].nomi_a[2],auxstr1);
	}
		// nomi aggiuntivi ml - 1° lotto
	fil_ctrl.Seek(OFS_NOMI_PML1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,lun_nomi_add1[31-i]);
		strcpy(squad_ml[31-i].nomi[6],auxstr);
	}
		// nomi aggiuntivi ml - 2° lotto
	fil_ctrl.Seek(OFS_NOMI_PML2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		if(i == 30)
		{
			fil_ctrl.Read(auxstr1, 4);
			auxstr1[4] = NULL;
			strcpy(auxstr, auxstr1);
			fil_ctrl.Seek(OFS_NOMI_PML2A, CFile::begin);
			fil_ctrl.Read(auxstr1, 4);
			strcat(auxstr, auxstr1);
		} else
			fil_ctrl.Read(auxstr,lun_nomi_add2[31-i]);
		strcpy(squad_ml[31-i].nomi[7],auxstr);
	}
	for(i=0;i<10;i++)
		auxstr[i] = NULL;
	//caricare bar forza
		//nazionali-allstar
	fil_ctrl.Seek(OFS_BAR, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,1);
		squad_nazall[i].bar_attacco = auxstr[0];
		if(i == 3)
			fil_ctrl.Seek(OFS_BAR1, CFile::begin);
		fil_ctrl.Read(auxstr,4);
		squad_nazall[i].bar_difesa = auxstr[0];
		squad_nazall[i].bar_potenza = auxstr[1];
		squad_nazall[i].bar_velocita = auxstr[2];
		squad_nazall[i].bar_tecnica = auxstr[3];
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,5);
		squad_ml[i].bar_attacco = auxstr[0];
		squad_ml[i].bar_difesa = auxstr[1];
		squad_ml[i].bar_potenza = auxstr[2];
		squad_ml[i].bar_velocita = auxstr[3];
		squad_ml[i].bar_tecnica = auxstr[4];
	}

	//caricare kik
		//nazionali-allstar
	fil_ctrl.Seek(OFS_KICKER, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(auxstr,6);
		squad_nazall[i].kik_punl = auxstr[0];
		squad_nazall[i].kik_punc = auxstr[1];
		squad_nazall[i].kik_angdx = auxstr[2];
		squad_nazall[i].kik_angsx = auxstr[3];
		squad_nazall[i].kik_rigori = auxstr[4];
		squad_nazall[i].kik_cap = auxstr[5];
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,6);
		squad_ml[i].kik_punl = auxstr[1];
		squad_ml[i].kik_punc = auxstr[0];
		squad_ml[i].kik_angdx = auxstr[3];
		squad_ml[i].kik_angsx = auxstr[2];
		squad_ml[i].kik_rigori = auxstr[4];
		squad_ml[i].kik_cap = auxstr[5];
	}
		//default ml
	fil_ctrl.Read(auxstr,2);
	fil_ctrl.Read(auxstr,6);
	squad_defml.kik_punl = auxstr[1];
	squad_defml.kik_punc = auxstr[0];
	squad_defml.kik_angdx = auxstr[3];
	squad_defml.kik_angsx = auxstr[2];
	squad_defml.kik_rigori = auxstr[4];
	squad_defml.kik_cap = auxstr[5];

	//caricare tattiche 
		//nazionali-allstar
	auxstr[30] = NULL;
	fil_ctrl.Seek(OFS_TATTICHE, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		if(i == 32)
		{
			fil_ctrl.Read(auxstr1,20);
			for(j=0;j<20;j++)
				auxstr[j] = auxstr1[j];
			fil_ctrl.Seek(OFS_TATTICHEA, CFile::begin);
			fil_ctrl.Read(auxstr1, 10);
			for(j=0;j<10;j++)
				auxstr[j+20] = auxstr1[j];
			auxstr[30] = NULL;
		} else
			fil_ctrl.Read(auxstr,30);

		strcpy(squad_nazall[i].str_tattica, auxstr);
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Read(auxstr,30);
		strcpy(squad_ml[i].str_tattica, auxstr);
	}
		//default ml
	fil_ctrl.Read(auxstr,2);
	fil_ctrl.Read(auxstr,30);
	auxstr[30] = NULL;
	strcpy(squad_defml.str_tattica, auxstr);
	//caricare stringa numeri
		//per squadre ml
	fil_ctrl.Seek(OFS_NUMERI_ML, CFile::begin);
	fil_ctrl.Read(squad_defml.str_numeri,23);
	fil_ctrl.Read(auxstr,1);
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Read(&squad_ml[i].str_numeri,23);
		//per squadre naz/all
	fil_ctrl.Seek(OFS_NUMERI_NAZ, CFile::begin);
	for(i = 0;i < 64;i ++)
		fil_ctrl.Read(&squad_nazall[i].stc_numeri,16);


	//caricare bandiera
		//forma, la 1° (sono tutte ok e uguali)
		//naz/all
	fil_ctrl.Seek(OFS_BANDIERE_FORMA1, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Read(&squad_nazall[i].stile_bandiera,1);
	}
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Read(&squad_ml[i].stile_bandiera,1);
		//colori  
		//naz/all 
	fil_ctrl.Seek(OFS_BANDIERE_COLORE, CFile::begin);
	for(i = 0;i < 56;i ++)
	{
		switch(i)
		{
			case 13:
				fil_ctrl.Read(&squad_nazall[i].col_bandiera,26);
				fil_ctrl.Seek(OFS_BANDIERE_COLORE1, CFile::begin);
				fil_ctrl.Read(auxcol,6);
				for(j=0;j<3;j++)
					squad_nazall[i].col_bandiera[j+13] = auxcol[j];
				break;
			// le nuove nazionali non sono li...
			case 36:
			case 39:
			case 47:
				break;
			// ci sono nel mezzo le vecchie nazionali nord irlanda, giamaica, uae
			case 1:
			case 40:
			case 52:
				fil_ctrl.Seek(32,CFile::current);
			default :
				fil_ctrl.Read(&squad_nazall[i].col_bandiera,32);
				break;
		}
	}

	fil_ctrl.Seek(64,CFile::current);
	for(i = 0;i < 5;i ++)
		fil_ctrl.Read(&squad_ml[i].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[10].col_bandiera,32);
	for(i = 0;i < 3;i ++)
		fil_ctrl.Read(&squad_ml[i+7].col_bandiera,32);
	for(i = 0;i < 2;i ++)
		fil_ctrl.Read(&squad_ml[i+11].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[15].col_bandiera,32);
	for(i = 0;i < 4;i ++)
		fil_ctrl.Read(&squad_ml[i+18].col_bandiera,32);
	fil_ctrl.Seek(32,CFile::current);
	fil_ctrl.Read(&squad_ml[14].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[24].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[25].col_bandiera,32);
	//bayern monaco
	fil_ctrl.Read(&squad_ml[26].col_bandiera,26);
	fil_ctrl.Seek(OFS_BANDIERE_COLORE2, CFile::begin);
	fil_ctrl.Read(auxcol,6);
	for(j=0;j<3;j++)
		squad_ml[26].col_bandiera[j+13] = auxcol[j];
	fil_ctrl.Read(&squad_ml[27].col_bandiera,32);
	for(i = 0;i < 2;i ++)
		fil_ctrl.Read(&squad_ml[i+16].col_bandiera,32);
	fil_ctrl.Seek(64,CFile::current);
	fil_ctrl.Read(&squad_ml[13].col_bandiera,32);
	fil_ctrl.Seek(288,CFile::current);
	fil_ctrl.Read(&squad_nazall[39].col_bandiera,32);
	fil_ctrl.Seek(64,CFile::current);
	fil_ctrl.Read(&squad_nazall[47].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[6].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[23].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[28].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[29].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[30].col_bandiera,32);
	fil_ctrl.Read(&squad_ml[31].col_bandiera,32);
	//senegal
	fil_ctrl.Seek(OFS_BANDIERE_COLORE_SEN,CFile::begin);
	fil_ctrl.Read(&squad_nazall[36].col_bandiera,32);

	//anteprima maglia !!!!!!!!!!!!!!!!
	fil_ctrl.Seek(OFS_ANT_MAGLIE,CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		switch(i)
		{	
			case 30 :
				fil_ctrl.Read(&squad_nazall[i].maglia1,32);
				fil_ctrl.Read(&squad_nazall[i].maglia2,32);
				fil_ctrl.Seek(OFS_ANT_MAGLIE1,CFile::begin);
				break;
			default :
				fil_ctrl.Read(&squad_nazall[i].maglia1,32);
				fil_ctrl.Read(&squad_nazall[i].maglia2,32);
				break;
		}
	}
	//ml
	fil_ctrl.Seek(OFS_ANT_MAGLIE2,CFile::begin);
	for(i = 0;i < SQUADRE_ML;i ++)
	{
		fil_ctrl.Read(&squad_ml[i].maglia1,32);
		fil_ctrl.Read(&squad_ml[i].maglia2,32);
	}
	
// giocatori
	//caricare nomi
		//giocatori nazionali-alls
	fil_ctrl.Seek(OFS_NOMI_G, CFile::begin);
	fil_ctrl.Read(auxstr, 8);
	auxstr[8] = NULL;
	strcpy(auxnome,auxstr);
	fil_ctrl.Seek(OFS_NOMI_G+312, CFile::begin);
	fil_ctrl.Read(auxstr, 2);
	auxstr[2] = NULL;
	strcat(auxnome,auxstr);
	strcpy(gioc[GIOCATORI_NC].nome,auxnome);
	for(i=1+GIOCATORI_NC;i<GIOCATORI_TOT;i++)
	{
		switch(i)
		{
			case 205+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 6);
				auxstr[6] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G2, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				auxstr[4] = NULL;
				strcat(auxnome,auxstr);
				break;
			case 410+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 4);
				auxstr[4] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G3, CFile::begin);
				fil_ctrl.Read(auxstr, 6);
				auxstr[6] = NULL;
				strcat(auxnome,auxstr);
				break;
			case 615+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 2);
				auxstr[2] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G4, CFile::begin);
				fil_ctrl.Read(auxstr, 8);
				auxstr[8] = NULL;
				strcat(auxnome,auxstr);
				break;
			case 820+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_NOMI_G5, CFile::begin);
				fil_ctrl.Read(auxnome, 10);
				break;
			case 1024+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 8);
				auxstr[8] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G6, CFile::begin);
				fil_ctrl.Read(auxstr, 2);
				auxstr[2] = NULL;
				strcat(auxnome,auxstr);
				break;
			case 1229+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 6);
				auxstr[6] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G7, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				auxstr[4] = NULL;
				strcat(auxnome,auxstr);
				break;
			case 1434+GIOCATORI_NC :
				fil_ctrl.Read(auxstr, 4);
				auxstr[4] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_G8, CFile::begin);
				fil_ctrl.Read(auxstr, 6);
				auxstr[6] = NULL;
				strcat(auxnome,auxstr);
				break;
			default :
				fil_ctrl.Read(auxnome, 10);
				break;
		}
		auxnome[10] = NULL;
		strcpy(gioc[i].nome,auxnome);
	}
		//giocatori non contact ml
	fil_ctrl.Seek(OFS_NOMI_GML, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		switch(i)
		{
			case 203 :
				fil_ctrl.Read(auxnome, 10);
				fil_ctrl.Seek(OFS_NOMI_GML2, CFile::begin);
				break;
			case 408 :
				fil_ctrl.Read(auxstr, 8);
				auxstr[8] = NULL;
				strcpy(auxnome,auxstr);
				fil_ctrl.Seek(OFS_NOMI_GML3, CFile::begin);
				fil_ctrl.Read(auxstr, 2);
				auxstr[2] = NULL;
				strcat(auxnome,auxstr);
				break;
			default :
				fil_ctrl.Read(auxnome, 10);
				break;
		}
		auxnome[10] = NULL;
		strcpy(gioc[i].nome, auxnome);
	}

	//caricare caratteristiche
		//naz-all
	fil_ctrl.Seek(OFS_CARAT_G, CFile::begin);
	for(i=GIOCATORI_NC;i<GIOCATORI_TOT;i++)
	{
		switch(i)
		{
			case 44+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 4);
				fil_ctrl.Seek(OFS_CARAT_G1, CFile::begin);
				fil_ctrl.Read(auxstr, 8);
				for(j=0;j<8;j++)
					auxstr1[j+4] = auxstr[j];
				break;
			case 215+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G2, CFile::begin);
				fil_ctrl.Read(auxstr1, 12);
				break;
			case 385+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 8);
				fil_ctrl.Seek(OFS_CARAT_G3, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				for(j=0;j<4;j++)
					auxstr1[j+8] = auxstr[j];
				break;
			case 556+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 4);
				fil_ctrl.Seek(OFS_CARAT_G4, CFile::begin);
				fil_ctrl.Read(auxstr, 8);
				for(j=0;j<8;j++)
					auxstr1[j+4] = auxstr[j];
				break;
			case 727+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G5, CFile::begin);
				fil_ctrl.Read(auxstr1, 12);
				break;
			case 897+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 8);
				fil_ctrl.Seek(OFS_CARAT_G6, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				for(j=0;j<4;j++)
					auxstr1[j+8] = auxstr[j];
				break;
			case 1068+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 4);
				fil_ctrl.Seek(OFS_CARAT_G7, CFile::begin);
				fil_ctrl.Read(auxstr, 8);
				for(j=0;j<8;j++)
					auxstr1[j+4] = auxstr[j];
				break;
			case 1239+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G8, CFile::begin);
				fil_ctrl.Read(auxstr1, 12);
				break;
			case 1409+GIOCATORI_NC :
				fil_ctrl.Read(auxstr1, 8);
				fil_ctrl.Seek(OFS_CARAT_G9, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				for(j=0;j<4;j++)
					auxstr1[j+8] = auxstr[j];
				break;
			default :
				fil_ctrl.Read(auxstr1, 12);
				break;
		}
		for(j=0;j<12;j++)
			gioc[i].str_carat[j] = auxstr1[j];
		gioc[i].codifica_carat();
	}
		//giocatori non contact ml
	fil_ctrl.Seek(OFS_CARAT_GML, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		switch(i)
		{
			case 148 :
				fil_ctrl.Read(auxstr1, 8);
				fil_ctrl.Seek(OFS_CARAT_GML1, CFile::begin);
				fil_ctrl.Read(auxstr, 4);
				for(j=0;j<4;j++)
					auxstr1[j+8] = auxstr[j];
				break;
			case 319 :
				fil_ctrl.Read(auxstr1, 4);
				fil_ctrl.Seek(OFS_CARAT_GML2, CFile::begin);
				fil_ctrl.Read(auxstr, 8);
				for(j=0;j<8;j++)
					auxstr1[j+4] = auxstr[j];
				break;
			default :
				fil_ctrl.Read(auxstr1, 12);
				break;
		}
		for(j=0;j<12;j++)
			gioc[i].str_carat[j] = auxstr1[j];
		gioc[i].codifica_carat();
	}

	//assegnare link ml
		//default
	fil_ctrl.Seek(OFS_LINK_ML, CFile::begin);
	fil_ctrl.Read(auxstr, 46);
	for(j=0;j<46;j++)
		squad_defml.link[j] = auxstr[j];
		// tutte ml
	fil_ctrl.Seek(OFS_LINK_ML1, CFile::begin);
	for(i=0;i<SQUADRE_ML;i++)
	{
		if(i == 6)
		{
			fil_ctrl.Read(auxstr, 28);
			for(j=0;j<28;j++)
				squad_ml[i].link[j] = auxstr[j];
			fil_ctrl.Seek(OFS_LINK_ML2, CFile::begin);
			fil_ctrl.Read(auxstr, 18);
			for(j=0;j<18;j++)
				squad_ml[i].link[j+28] = auxstr[j];
		} else
		{
			fil_ctrl.Read(auxstr, 46);
			for(j=0;j<46;j++)
				squad_ml[i].link[j] = auxstr[j];
		}
	}

	//caricare costi ml
	fil_ctrl.Seek(OFS_COSTI_NAZ, CFile::begin);
	for(i=GIOCATORI_NC;i<GIOCATORI_TOT;i++)
	{
		if(i == 1704)
		{
			fil_ctrl.Seek(2,CFile::current);
			i = 1750;
		}
		fil_ctrl.Read(&gioc[i].costo, 1);
	}
	fil_ctrl.Seek(OFS_COSTI_NC, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		fil_ctrl.Read(auxstr1, 1);
		gioc[i].costo = auxstr1[0];
	}

	// link nomi all-star
	fil_ctrl.Seek(2328964, CFile::begin);
	fil_ctrl.Read(link_euroas, 46);
	fil_ctrl.Seek(2329010, CFile::begin);
	fil_ctrl.Read(link_worldas, 46);
	nomiallstar();

	//tattiche predefinite
	fil_ctrl.Seek(4822152, CFile::begin);
	for(i=0;i<16;i++)
	{
		fil_ctrl.Read(tattpred[15-i].nome, 6);
		tattpred[15-i].nome[6] = NULL;
		fil_ctrl.Read(auxstr, 2);
	}
	fil_ctrl.Seek(374188, CFile::begin);
	for(i=0;i<16;i++)
		fil_ctrl.Read(tattpred[i].ruoli, 11);
	fil_ctrl.Seek(374780, CFile::begin);
	for(i=0;i<16;i++)
	{
		fil_ctrl.Read(tattpred[i].x, 10);
		fil_ctrl.Read(tattpred[i].y, 10);
	}


	fil_ctrl.Close();
}

int getWEPositionFromFifaPosition(string fpos)
{
	return fifaToWEPositionMap[fpos];
}

int getValue(string attr, fifa_player fpl)
{
	return fieldConversionFunctionMap[attr].getValue(fpl);
}

void CEdDlg::OnSelezioneSquadraV() 
{
//////////////////////////////////////////////////
// accidenti a non poter usare i vettori!!!!	//
//////////////////////////////////////////////////
	int id,i,lk,k;
	char strint[7];
	char auxstr[10];

	id = cmb_squadra.GetCurSel();

	cmb_kik_angdx.ResetContent();
	cmb_kik_angsx.ResetContent();
	cmb_kik_cap.ResetContent();
	cmb_kik_punc.ResetContent();
	cmb_kik_punl.ResetContent();
	cmb_kik_rig.ResetContent();
	if(id>0)
	{
		//nomi
		txt_nome_squad1.EnableWindow(TRUE);
		txt_nome_squad2.EnableWindow(TRUE);
		txt_nome_squad3.EnableWindow(TRUE);
		txt_nome_squad4.EnableWindow(TRUE);
		txt_nome_squad5.EnableWindow(TRUE);
		txt_nome_squad6.EnableWindow(TRUE);
		txt_nome_squadk.EnableWindow(TRUE);
		txt_nome_squad_a1.EnableWindow(TRUE);
		txt_nome_squad_a2.EnableWindow(TRUE);
		txt_nome_squad_a3.EnableWindow(TRUE);
		txt_nome_squad_m.EnableWindow(TRUE);
		txt_nomi_addml1.ShowWindow(0);
		txt_nomi_addml2.ShowWindow(0);
		lbl_nomi_addml.ShowWindow(0);
		lbl_nome_add1.ShowWindow(0);
		lbl_nome_add2.ShowWindow(0);
		//bar
		txt_bar_off.EnableWindow(TRUE);
		txt_bar_def.EnableWindow(TRUE);
		txt_bar_pow.EnableWindow(TRUE);
		txt_bar_spe.EnableWindow(TRUE);
		txt_bar_tec.EnableWindow(TRUE);
		//nomi
		_itoa(lun_nomik[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lbl_nome_squadk.SetWindowText(auxstr);
		txt_nome_squadk.LimitText(lun_nomik[id-1]-1);

		_itoa(lun_nomi1[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad1.SetWindowText(auxstr);
		txt_nome_squad1.LimitText(lun_nomi1[id-1]-1);

		_itoa(lun_nomi2[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad2.SetWindowText(auxstr);
		txt_nome_squad2.LimitText(lun_nomi2[id-1]-1);
		
		_itoa(lun_nomi3[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad3.SetWindowText(auxstr);
		txt_nome_squad3.LimitText(lun_nomi3[id-1]-1);
		
		_itoa(lun_nomi4[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad4.SetWindowText(auxstr);
		txt_nome_squad4.LimitText(lun_nomi4[id-1]-1);
		
		_itoa(lun_nomi5[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad5.SetWindowText(auxstr);
		txt_nome_squad5.LimitText(lun_nomi5[id-1]-1);
		
		_itoa(lun_nomi6[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad6.SetWindowText(auxstr);
		txt_nome_squad6.LimitText(lun_nomi6[id-1]-1);
		
		_itoa(lun_nomi_min[id-1]-1, strint, 10);
		strcpy(auxstr, "(");
		strcat(auxstr, strint);
		strcat(auxstr, ")");
		lab_nome_squad_m.SetWindowText(auxstr);
		txt_nome_squad_m.LimitText(lun_nomi_min[id-1]-1);

		txt_url_gioc1.EnableWindow(TRUE);
		txt_url_gioc2.EnableWindow(TRUE);
		txt_url_gioc3.EnableWindow(TRUE);
		txt_url_gioc4.EnableWindow(TRUE);
		txt_url_gioc5.EnableWindow(TRUE);
		txt_url_gioc6.EnableWindow(TRUE);
		txt_url_gioc7.EnableWindow(TRUE);
		txt_url_gioc8.EnableWindow(TRUE);
		txt_url_gioc9.EnableWindow(TRUE);
		txt_url_gioc10.EnableWindow(TRUE);
		txt_url_gioc11.EnableWindow(TRUE);
		txt_url_gioc12.EnableWindow(TRUE);
		txt_url_gioc13.EnableWindow(TRUE);
		txt_url_gioc14.EnableWindow(TRUE);
		txt_url_gioc15.EnableWindow(TRUE);
		txt_url_gioc16.EnableWindow(TRUE);
		txt_url_gioc17.EnableWindow(TRUE);
		txt_url_gioc18.EnableWindow(TRUE);
		txt_url_gioc19.EnableWindow(TRUE);
		txt_url_gioc20.EnableWindow(TRUE);
		txt_url_gioc21.EnableWindow(TRUE);
		txt_url_gioc22.EnableWindow(TRUE);
		txt_url_gioc23.EnableWindow(TRUE);

		//naz+all
		if(id<64)
		{
			//nomi
			txt_nome_squadk.SetWindowText(squad_nazall[id-1].nomek);
			txt_nome_squad1.SetWindowText(squad_nazall[id-1].nomi[0]);
			txt_nome_squad2.SetWindowText(squad_nazall[id-1].nomi[1]);
			txt_nome_squad3.SetWindowText(squad_nazall[id-1].nomi[2]);
			txt_nome_squad4.SetWindowText(squad_nazall[id-1].nomi[3]);
			txt_nome_squad5.SetWindowText(squad_nazall[id-1].nomi[4]);
			txt_nome_squad6.SetWindowText(squad_nazall[id-1].nomi[5]);
			txt_nome_squad_a1.SetWindowText(squad_nazall[id-1].nomi_a[0]);
			txt_nome_squad_a2.SetWindowText(squad_nazall[id-1].nomi_a[1]);
			txt_nome_squad_a3.SetWindowText(squad_nazall[id-1].nomi_a[2]);
			txt_nome_squad_m.SetWindowText(squad_nazall[id-1].nome_m);
			//bar
			_itoa(int(squad_nazall[id-1].bar_attacco), strint, 10);
			txt_bar_off.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].bar_difesa), strint, 10);
			txt_bar_def.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].bar_potenza), strint, 10);
			txt_bar_pow.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].bar_velocita), strint, 10);
			txt_bar_spe.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].bar_tecnica), strint, 10);
			txt_bar_tec.SetWindowText(strint);
			//kik

			//tatt //accidenta a non poter usare i vettori!!!
				//ruoli
			cmb_tat2.SetCurSel(squad_nazall[id-1].str_tattica[0]-2);
			cmb_tat3.SetCurSel(squad_nazall[id-1].str_tattica[1]-2);
			cmb_tat4.SetCurSel(squad_nazall[id-1].str_tattica[2]-2);
			cmb_tat5.SetCurSel(squad_nazall[id-1].str_tattica[3]-2);
			cmb_tat6.SetCurSel(squad_nazall[id-1].str_tattica[4]-2);
			cmb_tat7.SetCurSel(squad_nazall[id-1].str_tattica[5]-2);
			cmb_tat8.SetCurSel(squad_nazall[id-1].str_tattica[6]-2);
			cmb_tat9.SetCurSel(squad_nazall[id-1].str_tattica[7]-2);
			cmb_tat10.SetCurSel(squad_nazall[id-1].str_tattica[8]-2);
			cmb_tat11.SetCurSel(squad_nazall[id-1].str_tattica[9]-2);
				//tatx
			_itoa(int(squad_nazall[id-1].str_tattica[10]), strint, 10);
			txt_tatx2.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[11]), strint, 10);
			txt_tatx3.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[12]), strint, 10);
			txt_tatx4.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[13]), strint, 10);
			txt_tatx5.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[14]), strint, 10);
			txt_tatx6.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[15]), strint, 10);
			txt_tatx7.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[16]), strint, 10);
			txt_tatx8.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[17]), strint, 10);
			txt_tatx9.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[18]), strint, 10);
			txt_tatx10.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[19]), strint, 10);
			txt_tatx11.SetWindowText(strint);
				//taty
			_itoa(int(squad_nazall[id-1].str_tattica[20]), strint, 10);
			txt_taty2.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[21]), strint, 10);
			txt_taty3.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[22]), strint, 10);
			txt_taty4.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[23]), strint, 10);
			txt_taty5.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[24]), strint, 10);
			txt_taty6.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[25]), strint, 10);
			txt_taty7.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[26]), strint, 10);
			txt_taty8.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[27]), strint, 10);
			txt_taty9.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[28]), strint, 10);
			txt_taty10.SetWindowText(strint);
			_itoa(int(squad_nazall[id-1].str_tattica[29]), strint, 10);
			txt_taty11.SetWindowText(strint);
			// giocatori
			k=-1;
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc1.SetWindowText(gioc[lk].nome);txt_url_gioc1.SetWindowText(gioc[lk].url);txt_url_gioc1.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc2.SetWindowText(gioc[lk].nome);txt_url_gioc2.SetWindowText(gioc[lk].url);txt_url_gioc2.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc3.SetWindowText(gioc[lk].nome);txt_url_gioc3.SetWindowText(gioc[lk].url);txt_url_gioc3.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc4.SetWindowText(gioc[lk].nome);txt_url_gioc4.SetWindowText(gioc[lk].url);txt_url_gioc4.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc5.SetWindowText(gioc[lk].nome);txt_url_gioc5.SetWindowText(gioc[lk].url);txt_url_gioc5.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc6.SetWindowText(gioc[lk].nome);txt_url_gioc6.SetWindowText(gioc[lk].url);txt_url_gioc6.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc7.SetWindowText(gioc[lk].nome);txt_url_gioc7.SetWindowText(gioc[lk].url);txt_url_gioc7.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc8.SetWindowText(gioc[lk].nome);txt_url_gioc8.SetWindowText(gioc[lk].url);txt_url_gioc8.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc9.SetWindowText(gioc[lk].nome);txt_url_gioc9.SetWindowText(gioc[lk].url);txt_url_gioc9.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc10.SetWindowText(gioc[lk].nome);txt_url_gioc10.SetWindowText(gioc[lk].url);txt_url_gioc10.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc11.SetWindowText(gioc[lk].nome);txt_url_gioc11.SetWindowText(gioc[lk].url);txt_url_gioc11.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc12.SetWindowText(gioc[lk].nome);txt_url_gioc12.SetWindowText(gioc[lk].url);txt_url_gioc12.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc13.SetWindowText(gioc[lk].nome);txt_url_gioc13.SetWindowText(gioc[lk].url);txt_url_gioc13.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc14.SetWindowText(gioc[lk].nome);txt_url_gioc14.SetWindowText(gioc[lk].url);txt_url_gioc14.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc15.SetWindowText(gioc[lk].nome);txt_url_gioc15.SetWindowText(gioc[lk].url);txt_url_gioc15.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc16.SetWindowText(gioc[lk].nome);txt_url_gioc16.SetWindowText(gioc[lk].url);txt_url_gioc16.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc17.SetWindowText(gioc[lk].nome);txt_url_gioc17.SetWindowText(gioc[lk].url);txt_url_gioc17.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc18.SetWindowText(gioc[lk].nome);txt_url_gioc18.SetWindowText(gioc[lk].url);txt_url_gioc18.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc19.SetWindowText(gioc[lk].nome);txt_url_gioc19.SetWindowText(gioc[lk].url);txt_url_gioc19.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc20.SetWindowText(gioc[lk].nome);txt_url_gioc20.SetWindowText(gioc[lk].url);txt_url_gioc20.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc21.SetWindowText(gioc[lk].nome);txt_url_gioc21.SetWindowText(gioc[lk].url);txt_url_gioc21.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc22.SetWindowText(gioc[lk].nome);txt_url_gioc22.SetWindowText(gioc[lk].url);txt_url_gioc22.EnableWindow(id!=55 && id!=56);
			k++; lk = (id!=55 && id!=56) ? ((id-1)*23)+k+GIOCATORI_NC : (id==55) ? trovaIDml(&link_euroas[k*2]) : trovaIDml(&link_worldas[k*2]);
			txt_gioc23.SetWindowText(gioc[lk].nome);txt_url_gioc23.SetWindowText(gioc[lk].url);txt_url_gioc23.EnableWindow(id!=55 && id!=56);
			// combo dei kik
			for(i=0;i<11;i++)
			{
				cmb_kik_angdx.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
				cmb_kik_angsx.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
				cmb_kik_cap.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
				cmb_kik_punc.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
				cmb_kik_punl.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
				cmb_kik_rig.AddString(gioc[((id-1)*23)+i+GIOCATORI_NC].nome);
			}
			//selezione kik
			cmb_kik_angdx.SetCurSel(squad_nazall[id-1].kik_angdx);
			cmb_kik_angsx.SetCurSel(squad_nazall[id-1].kik_angsx);
			cmb_kik_cap.SetCurSel(squad_nazall[id-1].kik_cap);
			cmb_kik_punc.SetCurSel(squad_nazall[id-1].kik_punc);
			cmb_kik_punl.SetCurSel(squad_nazall[id-1].kik_punl);
			cmb_kik_rig.SetCurSel(squad_nazall[id-1].kik_rigori);
			//numeri 
			_itoa(squad_nazall[id-1].stc_numeri.order_1+1, strint, 10);
			txt_num_gioc1.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_2+1, strint, 10);
			txt_num_gioc2.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_3+1, strint, 10);
			txt_num_gioc3.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_4+1, strint, 10);
			txt_num_gioc4.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_5+1, strint, 10);
			txt_num_gioc5.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_6+1, strint, 10);
			txt_num_gioc6.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_7+1, strint, 10);
			txt_num_gioc7.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_8+1, strint, 10);
			txt_num_gioc8.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_9+1, strint, 10);
			txt_num_gioc9.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_10+1, strint, 10);
			txt_num_gioc10.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_11+1, strint, 10);
			txt_num_gioc11.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_12+1, strint, 10);
			txt_num_gioc12.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_13+1, strint, 10);
			txt_num_gioc13.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_14+1, strint, 10);
			txt_num_gioc14.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_15+1, strint, 10);
			txt_num_gioc15.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_16+1, strint, 10);
			txt_num_gioc16.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_17+1, strint, 10);
			txt_num_gioc17.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_18+1, strint, 10);
			txt_num_gioc18.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_19+1, strint, 10);
			txt_num_gioc19.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_20+1, strint, 10);
			txt_num_gioc20.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_21+1, strint, 10);
			txt_num_gioc21.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_22+1, strint, 10);
			txt_num_gioc22.SetWindowText(strint);
			_itoa(squad_nazall[id-1].stc_numeri.order_23+1, strint, 10);
			txt_num_gioc23.SetWindowText(strint);
		// ml
		} else if(id>63 && id<96)
		{
			//nomi
			txt_nomi_addml1.ShowWindow(1);
			txt_nomi_addml2.ShowWindow(1);
			lbl_nomi_addml.ShowWindow(1);
			lbl_nome_add1.ShowWindow(1);
			lbl_nome_add2.ShowWindow(1);
			txt_nome_squadk.SetWindowText(squad_ml[id-64].nomek);
			txt_nome_squad1.SetWindowText(squad_ml[id-64].nomi[0]);
			txt_nome_squad2.SetWindowText(squad_ml[id-64].nomi[1]);
			txt_nome_squad3.SetWindowText(squad_ml[id-64].nomi[2]);
			txt_nome_squad4.SetWindowText(squad_ml[id-64].nomi[3]);
			txt_nome_squad5.SetWindowText(squad_ml[id-64].nomi[4]);
			txt_nome_squad6.SetWindowText(squad_ml[id-64].nomi[5]);
			txt_nome_squad_a1.SetWindowText(squad_ml[id-64].nomi_a[0]);
			txt_nome_squad_a2.SetWindowText(squad_ml[id-64].nomi_a[1]);
			txt_nome_squad_a3.SetWindowText(squad_ml[id-64].nomi_a[2]);
			txt_nome_squad_m.SetWindowText(squad_ml[id-64].nome_m);
			txt_nomi_addml1.SetWindowText(squad_ml[id-64].nomi[6]);
			txt_nomi_addml2.SetWindowText(squad_ml[id-64].nomi[7]);
			_itoa(lun_nomi_add1[id-64]-1, strint, 10);
			strcpy(auxstr, "(");
			strcat(auxstr, strint);
			strcat(auxstr, ")");
			lbl_nome_add1.SetWindowText(auxstr);
			txt_nomi_addml1.LimitText(lun_nomi_add1[id-64]-1);
			_itoa(lun_nomi_add2[id-64]-1, strint, 10);
			strcpy(auxstr, "(");
			strcat(auxstr, strint);
			strcat(auxstr, ")");
			lbl_nome_add2.SetWindowText(auxstr);
			txt_nomi_addml2.LimitText(lun_nomi_add2[id-64]-1);
			//bar
			_itoa(int(squad_ml[id-64].bar_attacco), strint, 10);
			txt_bar_off.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].bar_difesa), strint, 10);
			txt_bar_def.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].bar_potenza), strint, 10);
			txt_bar_pow.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].bar_velocita), strint, 10);
			txt_bar_spe.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].bar_tecnica), strint, 10);
			txt_bar_tec.SetWindowText(strint);
			//tatt 
				//ruoli
			cmb_tat2.SetCurSel(squad_ml[id-64].str_tattica[0]-2);
			cmb_tat3.SetCurSel(squad_ml[id-64].str_tattica[1]-2);
			cmb_tat4.SetCurSel(squad_ml[id-64].str_tattica[2]-2);
			cmb_tat5.SetCurSel(squad_ml[id-64].str_tattica[3]-2);
			cmb_tat6.SetCurSel(squad_ml[id-64].str_tattica[4]-2);
			cmb_tat7.SetCurSel(squad_ml[id-64].str_tattica[5]-2);
			cmb_tat8.SetCurSel(squad_ml[id-64].str_tattica[6]-2);
			cmb_tat9.SetCurSel(squad_ml[id-64].str_tattica[7]-2);
			cmb_tat10.SetCurSel(squad_ml[id-64].str_tattica[8]-2);
			cmb_tat11.SetCurSel(squad_ml[id-64].str_tattica[9]-2);
				//tatx
			_itoa(int(squad_ml[id-64].str_tattica[10]), strint, 10);
			txt_tatx2.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[11]), strint, 10);
			txt_tatx3.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[12]), strint, 10);
			txt_tatx4.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[13]), strint, 10);
			txt_tatx5.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[14]), strint, 10);
			txt_tatx6.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[15]), strint, 10);
			txt_tatx7.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[16]), strint, 10);
			txt_tatx8.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[17]), strint, 10);
			txt_tatx9.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[18]), strint, 10);
			txt_tatx10.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[19]), strint, 10);
			txt_tatx11.SetWindowText(strint);
				//taty
			_itoa(int(squad_ml[id-64].str_tattica[20]), strint, 10);
			txt_taty2.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[21]), strint, 10);
			txt_taty3.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[22]), strint, 10);
			txt_taty4.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[23]), strint, 10);
			txt_taty5.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[24]), strint, 10);
			txt_taty6.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[25]), strint, 10);
			txt_taty7.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[26]), strint, 10);
			txt_taty8.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[27]), strint, 10);
			txt_taty9.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[28]), strint, 10);
			txt_taty10.SetWindowText(strint);
			_itoa(int(squad_ml[id-64].str_tattica[29]), strint, 10);
			txt_taty11.SetWindowText(strint);
			// giocatori - da link + kik
			lk = trovaIDml(&squad_ml[id-64].link[0]);
			txt_gioc1.SetWindowText(gioc[lk].nome);txt_url_gioc1.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[2]);
			txt_gioc2.SetWindowText(gioc[lk].nome);txt_url_gioc2.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[4]);
			txt_gioc3.SetWindowText(gioc[lk].nome);txt_url_gioc3.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[6]);
			txt_gioc4.SetWindowText(gioc[lk].nome);txt_url_gioc4.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[8]);
			txt_gioc5.SetWindowText(gioc[lk].nome);txt_url_gioc5.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[10]);
			txt_gioc6.SetWindowText(gioc[lk].nome);txt_url_gioc6.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[12]);
			txt_gioc7.SetWindowText(gioc[lk].nome);txt_url_gioc7.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[14]);
			txt_gioc8.SetWindowText(gioc[lk].nome);txt_url_gioc8.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[16]);
			txt_gioc9.SetWindowText(gioc[lk].nome);txt_url_gioc9.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[18]);
			txt_gioc10.SetWindowText(gioc[lk].nome);txt_url_gioc10.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[20]);
			txt_gioc11.SetWindowText(gioc[lk].nome);txt_url_gioc11.SetWindowText(gioc[lk].url);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_ml[id-64].link[22]);
			txt_gioc12.SetWindowText(gioc[lk].nome);txt_url_gioc12.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[24]);
			txt_gioc13.SetWindowText(gioc[lk].nome);txt_url_gioc13.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[26]);
			txt_gioc14.SetWindowText(gioc[lk].nome);txt_url_gioc14.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[28]);
			txt_gioc15.SetWindowText(gioc[lk].nome);txt_url_gioc15.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[30]);
			txt_gioc16.SetWindowText(gioc[lk].nome);txt_url_gioc16.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[32]);
			txt_gioc17.SetWindowText(gioc[lk].nome);txt_url_gioc17.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[34]);
			txt_gioc18.SetWindowText(gioc[lk].nome);txt_url_gioc18.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[36]);
			txt_gioc19.SetWindowText(gioc[lk].nome);txt_url_gioc19.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[38]);
			txt_gioc20.SetWindowText(gioc[lk].nome);txt_url_gioc20.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[40]);
			txt_gioc21.SetWindowText(gioc[lk].nome);txt_url_gioc21.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[42]);
			txt_gioc22.SetWindowText(gioc[lk].nome);txt_url_gioc22.SetWindowText(gioc[lk].url);
			lk = trovaIDml(&squad_ml[id-64].link[44]);
			txt_gioc23.SetWindowText(gioc[lk].nome);txt_url_gioc23.SetWindowText(gioc[lk].url);

			//selezione kik
			cmb_kik_angdx.SetCurSel(squad_ml[id-64].kik_angdx);
			cmb_kik_angsx.SetCurSel(squad_ml[id-64].kik_angsx);
			cmb_kik_cap.SetCurSel(squad_ml[id-64].kik_cap);
			cmb_kik_punc.SetCurSel(squad_ml[id-64].kik_punc);
			cmb_kik_punl.SetCurSel(squad_ml[id-64].kik_punl);
			cmb_kik_rig.SetCurSel(squad_ml[id-64].kik_rigori);
			//numeri
			_itoa(squad_ml[id-64].str_numeri[0]+1, strint, 10);
			txt_num_gioc1.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[1]+1, strint, 10);
			txt_num_gioc2.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[2]+1, strint, 10);
			txt_num_gioc3.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[3]+1, strint, 10);
			txt_num_gioc4.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[4]+1, strint, 10);
			txt_num_gioc5.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[5]+1, strint, 10);
			txt_num_gioc6.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[6]+1, strint, 10);
			txt_num_gioc7.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[7]+1, strint, 10);
			txt_num_gioc8.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[8]+1, strint, 10);
			txt_num_gioc9.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[9]+1, strint, 10);
			txt_num_gioc10.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[10]+1, strint, 10);
			txt_num_gioc11.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[11]+1, strint, 10);
			txt_num_gioc12.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[12]+1, strint, 10);
			txt_num_gioc13.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[13]+1, strint, 10);
			txt_num_gioc14.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[14]+1, strint, 10);
			txt_num_gioc15.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[15]+1, strint, 10);
			txt_num_gioc16.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[16]+1, strint, 10);
			txt_num_gioc17.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[17]+1, strint, 10);
			txt_num_gioc18.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[18]+1, strint, 10);
			txt_num_gioc19.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[19]+1, strint, 10);
			txt_num_gioc20.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[20]+1, strint, 10);
			txt_num_gioc21.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[21]+1, strint, 10);
			txt_num_gioc22.SetWindowText(strint);
			_itoa(squad_ml[id-64].str_numeri[22]+1, strint, 10);
			txt_num_gioc23.SetWindowText(strint);

			txt_num_gioc1.EnableWindow(TRUE);
			txt_num_gioc2.EnableWindow(TRUE);
			txt_num_gioc3.EnableWindow(TRUE);
			txt_num_gioc4.EnableWindow(TRUE);
			txt_num_gioc5.EnableWindow(TRUE);
			txt_num_gioc6.EnableWindow(TRUE);
			txt_num_gioc7.EnableWindow(TRUE);
			txt_num_gioc8.EnableWindow(TRUE);
			txt_num_gioc9.EnableWindow(TRUE);
			txt_num_gioc10.EnableWindow(TRUE);
			txt_num_gioc11.EnableWindow(TRUE);
			txt_num_gioc12.EnableWindow(TRUE);
			txt_num_gioc13.EnableWindow(TRUE);
			txt_num_gioc14.EnableWindow(TRUE);
			txt_num_gioc15.EnableWindow(TRUE);
			txt_num_gioc16.EnableWindow(TRUE);
			txt_num_gioc17.EnableWindow(TRUE);
			txt_num_gioc18.EnableWindow(TRUE);
			txt_num_gioc19.EnableWindow(TRUE);
			txt_num_gioc20.EnableWindow(TRUE);
			txt_num_gioc21.EnableWindow(TRUE);
			txt_num_gioc22.EnableWindow(TRUE);
			txt_num_gioc23.EnableWindow(TRUE);
		
		} else if(id==96)
		// default ml
		{
			//nomi - non presenti
			txt_nome_squadk.SetWindowText("---");
			txt_nome_squad1.SetWindowText("---");
			txt_nome_squad2.SetWindowText("---");
			txt_nome_squad3.SetWindowText("---");
			txt_nome_squad4.SetWindowText("---");
			txt_nome_squad5.SetWindowText("---");
			txt_nome_squad6.SetWindowText("---");
			txt_nome_squad_a1.SetWindowText("---");
			txt_nome_squad_a2.SetWindowText("---");
			txt_nome_squad_a3.SetWindowText("---");
			txt_nome_squad_m.SetWindowText("---");
			txt_nome_squadk.EnableWindow(FALSE);
			txt_nome_squad1.EnableWindow(FALSE);
			txt_nome_squad2.EnableWindow(FALSE);
			txt_nome_squad3.EnableWindow(FALSE);
			txt_nome_squad4.EnableWindow(FALSE);
			txt_nome_squad5.EnableWindow(FALSE);
			txt_nome_squad6.EnableWindow(FALSE);
			txt_nome_squad_a1.EnableWindow(FALSE);
			txt_nome_squad_a2.EnableWindow(FALSE);
			txt_nome_squad_a3.EnableWindow(FALSE);
			txt_nome_squad_m.EnableWindow(FALSE);
			lbl_nome_squadk.SetWindowText("");
			lab_nome_squad1.SetWindowText("");
			lab_nome_squad2.SetWindowText("");
			lab_nome_squad3.SetWindowText("");
			lab_nome_squad4.SetWindowText("");
			lab_nome_squad5.SetWindowText("");
			lab_nome_squad6.SetWindowText("");
			lab_nome_squad_m.SetWindowText("");
			//bar
			txt_bar_off.SetWindowText("-");
			txt_bar_def.SetWindowText("-");
			txt_bar_pow.SetWindowText("-");
			txt_bar_spe.SetWindowText("-");
			txt_bar_tec.SetWindowText("-");
			txt_bar_off.EnableWindow(FALSE);
			txt_bar_def.EnableWindow(FALSE);
			txt_bar_pow.EnableWindow(FALSE);
			txt_bar_spe.EnableWindow(FALSE);
			txt_bar_tec.EnableWindow(FALSE);
			//tatt
				//ruoli
			cmb_tat2.SetCurSel(squad_defml.str_tattica[0]-2);
			cmb_tat3.SetCurSel(squad_defml.str_tattica[1]-2);
			cmb_tat4.SetCurSel(squad_defml.str_tattica[2]-2);
			cmb_tat5.SetCurSel(squad_defml.str_tattica[3]-2);
			cmb_tat6.SetCurSel(squad_defml.str_tattica[4]-2);
			cmb_tat7.SetCurSel(squad_defml.str_tattica[5]-2);
			cmb_tat8.SetCurSel(squad_defml.str_tattica[6]-2);
			cmb_tat9.SetCurSel(squad_defml.str_tattica[7]-2);
			cmb_tat10.SetCurSel(squad_defml.str_tattica[8]-2);
			cmb_tat11.SetCurSel(squad_defml.str_tattica[9]-2);
				//tatx
			_itoa(int(squad_defml.str_tattica[10]), strint, 10);
			txt_tatx2.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[11]), strint, 10);
			txt_tatx3.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[12]), strint, 10);
			txt_tatx4.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[13]), strint, 10);
			txt_tatx5.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[14]), strint, 10);
			txt_tatx6.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[15]), strint, 10);
			txt_tatx7.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[16]), strint, 10);
			txt_tatx8.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[17]), strint, 10);
			txt_tatx9.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[18]), strint, 10);
			txt_tatx10.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[19]), strint, 10);
			txt_tatx11.SetWindowText(strint);
				//taty
			_itoa(int(squad_defml.str_tattica[20]), strint, 10);
			txt_taty2.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[21]), strint, 10);
			txt_taty3.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[22]), strint, 10);
			txt_taty4.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[23]), strint, 10);
			txt_taty5.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[24]), strint, 10);
			txt_taty6.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[25]), strint, 10);
			txt_taty7.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[26]), strint, 10);
			txt_taty8.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[27]), strint, 10);
			txt_taty9.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[28]), strint, 10);
			txt_taty10.SetWindowText(strint);
			_itoa(int(squad_defml.str_tattica[29]), strint, 10);
			txt_taty11.SetWindowText(strint);
			//giocatori
			// giocatori - da link + kik
			lk = trovaIDml(&squad_defml.link[0]);
			txt_gioc1.SetWindowText(gioc[lk].nome);txt_url_gioc1.SetWindowText("");txt_url_gioc1.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[2]);
			txt_gioc2.SetWindowText(gioc[lk].nome);txt_url_gioc2.SetWindowText("");txt_url_gioc2.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[4]);
			txt_gioc3.SetWindowText(gioc[lk].nome);txt_url_gioc3.SetWindowText("");txt_url_gioc3.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[6]);
			txt_gioc4.SetWindowText(gioc[lk].nome);txt_url_gioc4.SetWindowText("");txt_url_gioc4.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[8]);
			txt_gioc5.SetWindowText(gioc[lk].nome);txt_url_gioc5.SetWindowText("");txt_url_gioc5.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[10]);
			txt_gioc6.SetWindowText(gioc[lk].nome);txt_url_gioc6.SetWindowText("");txt_url_gioc6.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[12]);
			txt_gioc7.SetWindowText(gioc[lk].nome);txt_url_gioc7.SetWindowText("");txt_url_gioc7.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[14]);
			txt_gioc8.SetWindowText(gioc[lk].nome);txt_url_gioc8.SetWindowText("");txt_url_gioc8.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[16]);
			txt_gioc9.SetWindowText(gioc[lk].nome);txt_url_gioc9.SetWindowText("");txt_url_gioc9.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[18]);
			txt_gioc10.SetWindowText(gioc[lk].nome);txt_url_gioc10.SetWindowText("");txt_url_gioc10.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			lk = trovaIDml(&squad_defml.link[20]);
			txt_gioc11.SetWindowText(gioc[lk].nome);txt_url_gioc11.SetWindowText("");txt_url_gioc11.EnableWindow(FALSE);
			cmb_kik_angdx.AddString(gioc[lk].nome);
			cmb_kik_angsx.AddString(gioc[lk].nome);
			cmb_kik_cap.AddString(gioc[lk].nome);
			cmb_kik_punc.AddString(gioc[lk].nome);
			cmb_kik_punl.AddString(gioc[lk].nome);
			cmb_kik_rig.AddString(gioc[lk].nome);

			txt_gioc12.SetWindowText(gioc[trovaIDml(&squad_defml.link[22])].nome);txt_url_gioc12.SetWindowText("");txt_url_gioc12.EnableWindow(FALSE);
			txt_gioc13.SetWindowText(gioc[trovaIDml(&squad_defml.link[24])].nome);txt_url_gioc13.SetWindowText("");txt_url_gioc13.EnableWindow(FALSE);
			txt_gioc14.SetWindowText(gioc[trovaIDml(&squad_defml.link[26])].nome);txt_url_gioc14.SetWindowText("");txt_url_gioc14.EnableWindow(FALSE);
			txt_gioc15.SetWindowText(gioc[trovaIDml(&squad_defml.link[28])].nome);txt_url_gioc15.SetWindowText("");txt_url_gioc15.EnableWindow(FALSE);
			txt_gioc16.SetWindowText(gioc[trovaIDml(&squad_defml.link[30])].nome);txt_url_gioc16.SetWindowText("");txt_url_gioc16.EnableWindow(FALSE);
			txt_gioc17.SetWindowText(gioc[trovaIDml(&squad_defml.link[32])].nome);txt_url_gioc17.SetWindowText("");txt_url_gioc17.EnableWindow(FALSE);
			txt_gioc18.SetWindowText(gioc[trovaIDml(&squad_defml.link[34])].nome);txt_url_gioc18.SetWindowText("");txt_url_gioc18.EnableWindow(FALSE);
			txt_gioc19.SetWindowText(gioc[trovaIDml(&squad_defml.link[36])].nome);txt_url_gioc19.SetWindowText("");txt_url_gioc19.EnableWindow(FALSE);
			txt_gioc20.SetWindowText(gioc[trovaIDml(&squad_defml.link[38])].nome);txt_url_gioc20.SetWindowText("");txt_url_gioc20.EnableWindow(FALSE);
			txt_gioc21.SetWindowText(gioc[trovaIDml(&squad_defml.link[40])].nome);txt_url_gioc21.SetWindowText("");txt_url_gioc21.EnableWindow(FALSE);
			txt_gioc22.SetWindowText(gioc[trovaIDml(&squad_defml.link[42])].nome);txt_url_gioc22.SetWindowText("");txt_url_gioc22.EnableWindow(FALSE);
			txt_gioc23.SetWindowText(gioc[trovaIDml(&squad_defml.link[44])].nome);txt_url_gioc23.SetWindowText("");txt_url_gioc23.EnableWindow(FALSE);

			//selezione kik
			cmb_kik_angdx.SetCurSel(squad_defml.kik_angdx);
			cmb_kik_angsx.SetCurSel(squad_defml.kik_angsx);
			cmb_kik_cap.SetCurSel(squad_defml.kik_cap);
			cmb_kik_punc.SetCurSel(squad_defml.kik_punc);
			cmb_kik_punl.SetCurSel(squad_defml.kik_punl);
			cmb_kik_rig.SetCurSel(squad_defml.kik_rigori);

			//numeri 
			_itoa(squad_defml.str_numeri[0]+1, strint, 10);
			txt_num_gioc1.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[1]+1, strint, 10);
			txt_num_gioc2.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[2]+1, strint, 10);
			txt_num_gioc3.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[3]+1, strint, 10);
			txt_num_gioc4.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[4]+1, strint, 10);
			txt_num_gioc5.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[5]+1, strint, 10);
			txt_num_gioc6.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[6]+1, strint, 10);
			txt_num_gioc7.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[7]+1, strint, 10);
			txt_num_gioc8.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[8]+1, strint, 10);
			txt_num_gioc9.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[9]+1, strint, 10);
			txt_num_gioc10.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[10]+1, strint, 10);
			txt_num_gioc11.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[11]+1, strint, 10);
			txt_num_gioc12.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[12]+1, strint, 10);
			txt_num_gioc13.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[13]+1, strint, 10);
			txt_num_gioc14.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[14]+1, strint, 10);
			txt_num_gioc15.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[15]+1, strint, 10);
			txt_num_gioc16.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[16]+1, strint, 10);
			txt_num_gioc17.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[17]+1, strint, 10);
			txt_num_gioc18.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[18]+1, strint, 10);
			txt_num_gioc19.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[19]+1, strint, 10);
			txt_num_gioc20.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[20]+1, strint, 10);
			txt_num_gioc21.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[21]+1, strint, 10);
			txt_num_gioc22.SetWindowText(strint);
			_itoa(squad_defml.str_numeri[22]+1, strint, 10);
			txt_num_gioc23.SetWindowText(strint);
/*		//numeri 
		txt_num_gioc1.EnableWindow(TRUE);
		txt_num_gioc2.EnableWindow(TRUE);
		txt_num_gioc3.EnableWindow(TRUE);
		txt_num_gioc4.EnableWindow(TRUE);
		txt_num_gioc5.EnableWindow(TRUE);
		txt_num_gioc6.EnableWindow(TRUE);
		txt_num_gioc7.EnableWindow(TRUE);
		txt_num_gioc8.EnableWindow(TRUE);
		txt_num_gioc9.EnableWindow(TRUE);
		txt_num_gioc10.EnableWindow(TRUE);
		txt_num_gioc11.EnableWindow(TRUE);
		txt_num_gioc12.EnableWindow(TRUE);
		txt_num_gioc13.EnableWindow(TRUE);
		txt_num_gioc14.EnableWindow(TRUE);
		txt_num_gioc15.EnableWindow(TRUE);
		txt_num_gioc16.EnableWindow(TRUE);
		txt_num_gioc17.EnableWindow(TRUE);
		txt_num_gioc18.EnableWindow(TRUE);
		txt_num_gioc19.EnableWindow(TRUE);
		txt_num_gioc20.EnableWindow(TRUE);
		txt_num_gioc21.EnableWindow(TRUE);
		txt_num_gioc22.EnableWindow(TRUE);
		txt_num_gioc23.EnableWindow(TRUE);
*/		}
	} else
	{
		//ripulitura
		txt_num_gioc1.SetWindowText("");
		txt_num_gioc2.SetWindowText("");
		txt_num_gioc3.SetWindowText("");
		txt_num_gioc4.SetWindowText("");
		txt_num_gioc5.SetWindowText("");
		txt_num_gioc6.SetWindowText("");
		txt_num_gioc7.SetWindowText("");
		txt_num_gioc8.SetWindowText("");
		txt_num_gioc9.SetWindowText("");
		txt_num_gioc10.SetWindowText("");
		txt_num_gioc11.SetWindowText("");
		txt_num_gioc12.SetWindowText("");
		txt_num_gioc13.SetWindowText("");
		txt_num_gioc14.SetWindowText("");
		txt_num_gioc15.SetWindowText("");
		txt_num_gioc16.SetWindowText("");
		txt_num_gioc17.SetWindowText("");
		txt_num_gioc18.SetWindowText("");
		txt_num_gioc19.SetWindowText("");
		txt_num_gioc20.SetWindowText("");
		txt_num_gioc21.SetWindowText("");
		txt_num_gioc22.SetWindowText("");
		txt_num_gioc23.SetWindowText("");

		lbl_nome_squadk.SetWindowText("");
		lab_nome_squad1.SetWindowText("");
		lab_nome_squad2.SetWindowText("");
		lab_nome_squad3.SetWindowText("");
		lab_nome_squad4.SetWindowText("");
		lab_nome_squad5.SetWindowText("");
		lab_nome_squad6.SetWindowText("");
		lab_nome_squad_m.SetWindowText("");
		txt_nome_squadk.SetWindowText("");
		txt_nome_squad1.SetWindowText("");
		txt_nome_squad2.SetWindowText("");
		txt_nome_squad3.SetWindowText("");
		txt_nome_squad4.SetWindowText("");
		txt_nome_squad5.SetWindowText("");
		txt_nome_squad6.SetWindowText("");
		txt_nome_squad_a1.SetWindowText("");
		txt_nome_squad_a2.SetWindowText("");
		txt_nome_squad_a3.SetWindowText("");
		txt_nome_squad_m.SetWindowText("");
		txt_bar_def.SetWindowText("");
		txt_bar_off.SetWindowText("");
		txt_bar_pow.SetWindowText("");
		txt_bar_spe.SetWindowText("");
		txt_bar_tec.SetWindowText("");
		txt_gioc1.SetWindowText("");txt_url_gioc1.SetWindowText("");
		txt_gioc2.SetWindowText("");txt_url_gioc2.SetWindowText("");
		txt_gioc3.SetWindowText("");txt_url_gioc3.SetWindowText("");
		txt_gioc4.SetWindowText("");txt_url_gioc4.SetWindowText("");
		txt_gioc5.SetWindowText("");txt_url_gioc5.SetWindowText("");
		txt_gioc6.SetWindowText("");txt_url_gioc6.SetWindowText("");
		txt_gioc7.SetWindowText("");txt_url_gioc7.SetWindowText("");
		txt_gioc8.SetWindowText("");txt_url_gioc8.SetWindowText("");
		txt_gioc9.SetWindowText("");txt_url_gioc9.SetWindowText("");
		txt_gioc10.SetWindowText("");txt_url_gioc10.SetWindowText("");
		txt_gioc11.SetWindowText("");txt_url_gioc11.SetWindowText("");
		txt_gioc12.SetWindowText("");txt_url_gioc12.SetWindowText("");
		txt_gioc13.SetWindowText("");txt_url_gioc13.SetWindowText("");
		txt_gioc14.SetWindowText("");txt_url_gioc14.SetWindowText("");
		txt_gioc15.SetWindowText("");txt_url_gioc15.SetWindowText("");
		txt_gioc16.SetWindowText("");txt_url_gioc16.SetWindowText("");
		txt_gioc17.SetWindowText("");txt_url_gioc17.SetWindowText("");
		txt_gioc18.SetWindowText("");txt_url_gioc18.SetWindowText("");
		txt_gioc19.SetWindowText("");txt_url_gioc19.SetWindowText("");
		txt_gioc20.SetWindowText("");txt_url_gioc20.SetWindowText("");
		txt_gioc21.SetWindowText("");txt_url_gioc21.SetWindowText("");
		txt_gioc22.SetWindowText("");txt_url_gioc22.SetWindowText("");
		txt_gioc23.SetWindowText("");txt_url_gioc23.SetWindowText("");
		cmb_tat2.SetCurSel(-1);
		cmb_tat3.SetCurSel(-1);
		cmb_tat4.SetCurSel(-1);
		cmb_tat5.SetCurSel(-1);
		cmb_tat6.SetCurSel(-1);
		cmb_tat7.SetCurSel(-1);
		cmb_tat8.SetCurSel(-1);
		cmb_tat9.SetCurSel(-1);
		cmb_tat10.SetCurSel(-1);
		cmb_tat11.SetCurSel(-1);
		txt_tatx2.SetWindowText("");
		txt_tatx3.SetWindowText("");
		txt_tatx4.SetWindowText("");
		txt_tatx5.SetWindowText("");
		txt_tatx6.SetWindowText("");
		txt_tatx7.SetWindowText("");
		txt_tatx8.SetWindowText("");
		txt_tatx9.SetWindowText("");
		txt_tatx10.SetWindowText("");
		txt_tatx11.SetWindowText("");
		txt_taty2.SetWindowText("");
		txt_taty3.SetWindowText("");
		txt_taty4.SetWindowText("");
		txt_taty5.SetWindowText("");
		txt_taty6.SetWindowText("");
		txt_taty7.SetWindowText("");
		txt_taty8.SetWindowText("");
		txt_taty9.SetWindowText("");
		txt_taty10.SetWindowText("");
		txt_taty11.SetWindowText("");
	}

	CEdDlg::OnSelchangeTat2();
	CEdDlg::OnSelchangeTat3();
	CEdDlg::OnSelchangeTat4();
	CEdDlg::OnSelchangeTat5();
	CEdDlg::OnSelchangeTat6();
	CEdDlg::OnSelchangeTat7();
	CEdDlg::OnSelchangeTat8();
	CEdDlg::OnSelchangeTat9();
	CEdDlg::OnSelchangeTat10();
	CEdDlg::OnSelchangeTat11();
	CEdDlg::OnChangeTatx2();
}

void CEdDlg::OnSelchangeTat2() 
{
	CString auxstr;
	cmb_tat2.GetWindowText(auxstr);
	cmd_visual_tat1.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat3() 
{
	CString auxstr;
	cmb_tat3.GetWindowText(auxstr);
	cmd_visual_tat2.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat4() 
{
	CString auxstr;
	cmb_tat4.GetWindowText(auxstr);
	cmd_visual_tat3.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat5() 
{
	CString auxstr;
	cmb_tat5.GetWindowText(auxstr);
	cmd_visual_tat4.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat6() 
{
	CString auxstr;
	cmb_tat6.GetWindowText(auxstr);
	cmd_visual_tat5.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat7() 
{
	CString auxstr;
	cmb_tat7.GetWindowText(auxstr);
	cmd_visual_tat6.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat8() 
{
	CString auxstr;
	cmb_tat8.GetWindowText(auxstr);
	cmd_visual_tat7.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat9() 
{
	CString auxstr;
	cmb_tat9.GetWindowText(auxstr);
	cmd_visual_tat8.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat10() 
{
	CString auxstr;
	cmb_tat10.GetWindowText(auxstr);
	cmd_visual_tat9.SetWindowText(auxstr);
}

void CEdDlg::OnSelchangeTat11() 
{
	CString auxstr;
	cmb_tat11.GetWindowText(auxstr);
	cmd_visual_tat10.SetWindowText(auxstr);
}

int trovaIDml(unsigned char *lk)
{
	unsigned int nz, g, r;
	nz = int(lk[0]);
	g = int(lk[1]);
	if(g>22)
	{
		r = g+start_link[nz]-23;
		gioc[r].nome;
	} else
	{
		r = (nz*23)+g+GIOCATORI_NC;
	}
	return r;
}

void CEdDlg::OnChangeTatx2() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx2.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty2.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat1.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx3() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx3.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty3.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat2.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx4() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx4.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty4.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat3.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx5() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx5.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty5.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat4.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx6() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx6.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty6.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat5.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx7() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx7.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty7.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat6.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx8() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx8.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty8.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat7.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx9() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx9.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty9.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat8.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx10() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx10.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty10.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat9.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::OnChangeTatx11() 
{
	CString str;
	float auxx,auxy;
	int ax,ay;
	txt_tatx11.GetWindowText(str);
	auxx = float(atoi(str)-TXMIN);
	txt_taty11.GetWindowText(str);
	auxy = float(atoi(str)-TYMIN);
	muovitattica(auxx,auxy,&ax,&ay);
	cmd_visual_tat10.MoveWindow(ax,ay,BTW,BTH,TRUE);
}

void CEdDlg::muovitattica(float auxx,float auxy,int *rx,int *ry)
{
	int ax, ay;
	float pasx, pasy;
	WINDOWPLACEMENT pl;
	ax = TXMAX-TXMIN;
	ay = TYMAX-TYMIN;
	frm_tat_campo.GetWindowPlacement(&pl);

	pasx = float(pl.rcNormalPosition.right-pl.rcNormalPosition.left)/ax;
	pasy = float(pl.rcNormalPosition.bottom-pl.rcNormalPosition.top)/ay;
	*rx = pl.rcNormalPosition.left+int(pasx*auxx)-BTW/2+TCORRX;
	*ry = pl.rcNormalPosition.top+int(pasy*auxy)-BTH/2+TCORRY;
}

void CEdDlg::OnChangeTaty2() 
{
	CEdDlg::OnChangeTatx2();
}

void CEdDlg::OnChangeTaty3() 
{
	CEdDlg::OnChangeTatx3();
}

void CEdDlg::OnChangeTaty4() 
{
	CEdDlg::OnChangeTatx4();
}

void CEdDlg::OnChangeTaty5() 
{
	CEdDlg::OnChangeTatx5();
}

void CEdDlg::OnChangeTaty6() 
{
	CEdDlg::OnChangeTatx6();
}

void CEdDlg::OnChangeTaty7() 
{
	CEdDlg::OnChangeTatx7();
}

void CEdDlg::OnChangeTaty8() 
{
	CEdDlg::OnChangeTatx8();
}

void CEdDlg::OnChangeTaty9() 
{
	CEdDlg::OnChangeTatx9();
}

void CEdDlg::OnChangeTaty10() 
{
	CEdDlg::OnChangeTatx10();
}

void CEdDlg::OnChangeTaty11() 
{
	CEdDlg::OnChangeTatx11();
}

void CEdDlg::OnChangeURL1() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc1.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[0]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL2() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc2.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+1+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[2]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL3() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc3.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+2+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[4]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL4() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc4.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+3+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[6]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL5() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc5.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+4+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[8]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL6() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc6.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+5+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[10]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL7() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc7.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+6+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[12]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL8() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc8.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+7+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[14]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL9() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc9.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+8+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[16]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL10() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc10.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+9+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[18]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL11() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc11.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+10+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[20]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL12() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc12.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+11+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[22]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL13() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc13.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+12+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[24]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL14() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc14.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+13+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[26]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL15() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc15.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+14+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[28]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL16() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc16.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+15+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[30]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL17() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc17.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+16+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[32]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL18() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc18.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+17+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[34]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL19() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc19.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+18+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[36]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL20() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc20.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+19+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[38]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL21() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc21.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+20+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[40]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL22() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc22.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+21+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[42]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnChangeURL23() 
{
	int id, lk;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id < 96)
	{
		CString str;
		txt_url_gioc23.GetWindowText(str);
		lk = (id<64) ? ((id-1)*23)+22+GIOCATORI_NC : trovaIDml(&squad_ml[id-64].link[44]);
		strcpy(gioc[lk].url, CT2A(str));
	}
}

void CEdDlg::OnKillfocusTatx2() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx2.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx2.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx2.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[10] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[10] = i;
	if(id == 96)
		squad_defml.str_tattica[10] = i;
}

void CEdDlg::OnKillfocusTatx3() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx3.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx3.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx3.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[11] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[11] = i;
	if(id == 96)
		squad_defml.str_tattica[11] = i;
}

void CEdDlg::OnKillfocusTatx4() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx4.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx4.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx4.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[12] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[12] = i;
	if(id == 96)
		squad_defml.str_tattica[12] = i;
}

void CEdDlg::OnKillfocusTatx5() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx5.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx5.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx5.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[13] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[13] = i;
	if(id == 96)
		squad_defml.str_tattica[13] = i;
}

void CEdDlg::OnKillfocusTatx6() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx6.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx6.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx6.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[14] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[14] = i;
	if(id == 96)
		squad_defml.str_tattica[14] = i;
}

void CEdDlg::OnKillfocusTatx7() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx7.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx7.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx7.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[15] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[15] = i;
	if(id == 96)
		squad_defml.str_tattica[15] = i;
}

void CEdDlg::OnKillfocusTatx8() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx8.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx8.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx8.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[16] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[16] = i;
	if(id == 96)
		squad_defml.str_tattica[16] = i;
}

void CEdDlg::OnKillfocusTatx9() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx9.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx9.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx9.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[17] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[17] = i;
	if(id == 96)
		squad_defml.str_tattica[17] = i;
}

void CEdDlg::OnKillfocusTatx10() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx10.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx10.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx10.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[18] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[18] = i;
	if(id == 96)
		squad_defml.str_tattica[18] = i;
}

void CEdDlg::OnKillfocusTatx11() 
{
	CString str;
	char str1[6];
	int i;
	txt_tatx11.GetWindowText(str);
	i = atoi(str);
	if(i<TXMIN)
	{
		_itoa(TXMIN,str1,10);
		i = TXMIN;
		txt_tatx11.SetWindowText(str1);
	}
	if(i>TXMAX)
	{
		_itoa(TXMAX,str1,10);
		i = TXMAX;
		txt_tatx11.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[19] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[19] = i;
	if(id == 96)
		squad_defml.str_tattica[19] = i;
}

void CEdDlg::OnKillfocusTaty2() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty2.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty2.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty2.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[20] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[20] = i;
	if(id == 96)
		squad_defml.str_tattica[20] = i;
}

void CEdDlg::OnKillfocusTaty3() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty3.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty3.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty3.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[21] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[21] = i;
	if(id == 96)
		squad_defml.str_tattica[21] = i;
}

void CEdDlg::OnKillfocusTaty4() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty4.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty4.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty4.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[22] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[22] = i;
	if(id == 96)
		squad_defml.str_tattica[22] = i;
}

void CEdDlg::OnKillfocusTaty5() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty5.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty5.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty5.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[23] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[23] = i;
	if(id == 96)
		squad_defml.str_tattica[23] = i;
}

void CEdDlg::OnKillfocusTaty6() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty6.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty6.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty6.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[24] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[24] = i;
	if(id == 96)
		squad_defml.str_tattica[24] = i;
}

void CEdDlg::OnKillfocusTaty7() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty7.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty7.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty7.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[25] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[25] = i;
	if(id == 96)
		squad_defml.str_tattica[25] = i;
}

void CEdDlg::OnKillfocusTaty8() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty8.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty8.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty8.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[26] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[26] = i;
	if(id == 96)
		squad_defml.str_tattica[26] = i;
}

void CEdDlg::OnKillfocusTaty9() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty9.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty9.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty9.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[27] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[27] = i;
	if(id == 96)
		squad_defml.str_tattica[27] = i;
}

void CEdDlg::OnKillfocusTaty10() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty10.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty10.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty10.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[28] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[28] = i;
	if(id == 96)
		squad_defml.str_tattica[28] = i;
}

void CEdDlg::OnKillfocusTaty11() 
{
	CString str;
	char str1[6];
	int i;
	txt_taty11.GetWindowText(str);
	i = atoi(str);
	if(i<TYMIN)
	{
		_itoa(TYMIN,str1,10);
		i = TYMIN;
		txt_taty11.SetWindowText(str1);
	}
	if(i>TYMAX)
	{
		_itoa(TYMAX,str1,10);
		i = TYMAX;
		txt_taty11.SetWindowText(str1);
	}
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[29] = i;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[29] = i;
	if(id == 96)
		squad_defml.str_tattica[29] = i;
}

void CEdDlg::applica_tatt(int k)
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	if(id>0)
	{
		if(id<64)
		{
//			for(i=0;i<30;i++)
//				squad_nazall[id-1].str_tattica[i] = tt[i];
			for(i=0;i<10;i++)
			{
				squad_nazall[id-1].str_tattica[i] = tattpred[k].ruoli[i+1];
				squad_nazall[id-1].str_tattica[i+10] = tattpred[k].x[i];
				squad_nazall[id-1].str_tattica[i+20] = tattpred[k].y[i];
			}
		}
		if(id>63 && id<96)
		{
//			for(i=0;i<30;i++)
//				squad_ml[id-64].str_tattica[i] = tt[i];
			for(i=0;i<10;i++)
			{
				squad_ml[id-64].str_tattica[i] = tattpred[k].ruoli[i+1];
				squad_ml[id-64].str_tattica[i+10] = tattpred[k].x[i];
				squad_ml[id-64].str_tattica[i+20] = tattpred[k].y[i];
			}
		}
		if(id == 96)
		{
//			for(i=0;i<30;i++)
//				squad_defml.str_tattica[i] = tt[i];
			for(i=0;i<10;i++)
			{
				squad_defml.str_tattica[i] = tattpred[k].ruoli[i+1];
				squad_defml.str_tattica[i+10] = tattpred[k].x[i];
				squad_defml.str_tattica[i+20] = tattpred[k].y[i];
			}
		}
		CEdDlg::OnSelezioneSquadraV();
	}
}

void CEdDlg::On451a() 
{
	applica_tatt(0);
}

void CEdDlg::On451b() 
{
	applica_tatt(1);
}

void CEdDlg::On442a() 
{
	applica_tatt(2);
}

void CEdDlg::On442b() 
{
	applica_tatt(3);
}

void CEdDlg::On433a() 
{
	applica_tatt(4);
}

void CEdDlg::On433b() 
{
	applica_tatt(5);
}

void CEdDlg::On361a() 
{
	applica_tatt(6);
}

void CEdDlg::On361b() 
{
	applica_tatt(7);
}

void CEdDlg::On352a() 
{
	applica_tatt(8);
}

void CEdDlg::On352b() 
{
	applica_tatt(9);
}

void CEdDlg::On343a() 
{
	applica_tatt(10);
}

void CEdDlg::On343b() 
{
	applica_tatt(11);
}

void CEdDlg::On541a() 
{
	applica_tatt(12);
}

void CEdDlg::On541b() 
{
	applica_tatt(13);
}

void CEdDlg::On532a() 
{
	applica_tatt(14);
}

void CEdDlg::On532b() 
{
	applica_tatt(15);
}

void CEdDlg::OnCopiaNomisquadra() 
{
	CString aux,aux1,aux2,aux3;
	int id;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id<64)
	{
		txt_nome_squad1.GetWindowText(aux);
		strcpy(squad_nazall[id-1].nomi[0],aux);

		aux1 = aux.Left(lun_nomi2[id-1]-1);
		strcpy(squad_nazall[id-1].nomi[1],aux1);
		txt_nome_squad2.SetWindowText(aux1);
		
		aux1 = aux.Left(lun_nomi3[id-1]-1);
		strcpy(squad_nazall[id-1].nomi[2],aux1);
		txt_nome_squad3.SetWindowText(aux1);
		
		aux1 = aux.Left(lun_nomi4[id-1]-1);
		strcpy(squad_nazall[id-1].nomi[3],aux1);
		txt_nome_squad4.SetWindowText(aux1);

		aux1 = aux.Left(lun_nomi5[id-1]-1);
		strcpy(squad_nazall[id-1].nomi[4],aux1);
		txt_nome_squad5.SetWindowText(aux1);

		aux1 = aux.Left(lun_nomi6[id-1]-1);
		strcpy(squad_nazall[id-1].nomi[5],aux1);
		txt_nome_squad6.SetWindowText(aux1);
		
		aux1 = aux.Left(3);
		strcpy(squad_nazall[id-1].nomi_a[0],aux1);
		strcpy(squad_nazall[id-1].nomi_a[1],aux1);
		strcpy(squad_nazall[id-1].nomi_a[2],aux1);
		txt_nome_squad_a1.SetWindowText(aux1);
		txt_nome_squad_a2.SetWindowText(aux1);
		txt_nome_squad_a3.SetWindowText(aux1);
		
		aux1 = aux.Right(aux.GetLength()-1);
		aux1.MakeLower();
		aux1 = aux1.Left(lun_nomi_min[id-1]-2);
		aux2 = aux.Left(1);
		aux2 += aux1;
		strcpy(squad_nazall[id-1].nome_m,aux2);
		txt_nome_squad_m.SetWindowText(aux2);

		aux1 = aux.Right(aux.GetLength()-1);
		aux1.MakeLower();
		aux1 = aux1.Left(lun_nomik[id-1]-2);
		aux2 = aux.Left(1);
		aux2 += aux1;
		strcpy(squad_nazall[id-1].nomek,aux2);
		txt_nome_squadk.SetWindowText(aux2);
	}		// ml
	if(id>63 && id<96)
	{
		txt_nome_squad1.GetWindowText(aux);
		strcpy(squad_ml[id-64].nomi[0],aux);

		aux1 = aux.Left(lun_nomi2[id-1]-1);
		strcpy(squad_ml[id-64].nomi[1],aux1);
		txt_nome_squad2.SetWindowText(aux1);
		
		aux1 = aux.Left(lun_nomi3[id-1]-1);
		strcpy(squad_ml[id-64].nomi[2],aux1);
		txt_nome_squad3.SetWindowText(aux1);
		
		aux1 = aux.Left(lun_nomi4[id-1]-1);
		strcpy(squad_ml[id-64].nomi[3],aux1);
		txt_nome_squad4.SetWindowText(aux1);

		aux1 = aux.Left(lun_nomi5[id-1]-1);
		strcpy(squad_ml[id-64].nomi[4],aux1);
		txt_nome_squad5.SetWindowText(aux1);

		aux1 = aux.Left(lun_nomi6[id-1]-1);
		strcpy(squad_ml[id-64].nomi[5],aux1);
		txt_nome_squad6.SetWindowText(aux1);
		
		aux1 = aux.Left(3);
		strcpy(squad_ml[id-64].nomi_a[0],aux1);
		strcpy(squad_ml[id-64].nomi_a[1],aux1);
		strcpy(squad_ml[id-64].nomi_a[2],aux1);
		txt_nome_squad_a1.SetWindowText(aux1);
		txt_nome_squad_a2.SetWindowText(aux1);
		txt_nome_squad_a3.SetWindowText(aux1);
		
		aux1 = aux.Right(aux.GetLength()-1);
		aux1.MakeLower();
		aux1 = aux1.Left(lun_nomi_min[id-1]-2);
		aux2 = aux.Left(1);
		aux2 += aux1;
		strcpy(squad_ml[id-64].nome_m,aux2);
		txt_nome_squad_m.SetWindowText(aux2);

		aux1 = aux.Right(aux.GetLength()-1);
		aux1.MakeLower();
		aux1 = aux1.Left(lun_nomik[id-64]-2);
		aux2 = aux.Left(1);
		aux2 += aux1;
		strcpy(squad_ml[id-64].nomek,aux2);
		txt_nome_squadk.SetWindowText(aux2);

		aux1 = aux.Left(lun_nomi_add1[id-64]-1);
		strcpy(squad_ml[id-64].nomi[6],aux1);
		txt_nomi_addml1.SetWindowText(aux1);

		aux1 = aux.Left(lun_nomi_add2[id-64]-1);
		strcpy(squad_ml[id-64].nomi[7],aux1);
		txt_nomi_addml2.SetWindowText(aux1);
	}
}

void CEdDlg::carica_SOFIFAFields()
{
	//load all fifa attribute custom settings
	fifaVerNumFields.clear();
	fifaVerGroupFieldIndexMap.clear();
	fifaVerGroupsMap.clear();
	fifaVerGroupFieldMap.clear();
	CString fil_nomeFIFAattributes = "SOFIFA attributes.txt";
	string line, fifa_version, group, attribute;
	ifstream fil_dbfields;
	fil_dbfields.open (fil_nomeFIFAattributes);
	if (fil_dbfields.is_open())
	{
		getline (fil_dbfields,line); //VERSION;GROUP;ATTRIBUTE
		do
		{
			getline (fil_dbfields,line);
			if(line!="")
			{
				vector<string> fields = split(line, ';');
				fifa_version = fields[0];
				group = fields[1];
				attribute = fields[2];

				if(fifaVerGroupFieldMap[fifa_version].count( group ) == 0)
				{
					if(fifaVerGroupsMap.count(fifa_version)==0)
					{
						fifaVerNumFields[fifa_version]=0;

						vector<string> newList;
						fifaVerGroupsMap.insert(pair<string, vector<string> >(fifa_version, newList));
					}
					fifaVerGroupsMap[fifa_version].push_back(group);

					vector<string> newList;
					fifaVerGroupFieldMap[fifa_version].insert(pair<string, vector<string> >(group, newList));
				}

				fifaVerGroupFieldMap[fifa_version][group].push_back(attribute);

				//store the position in the custom field vector
				fifaVerGroupFieldIndexMap[fifa_version][group][attribute]=fifaVerNumFields[fifa_version];
				fifaVerNumFields[fifa_version]++;

			}

		}while(line != "");
		fil_dbfields.close();
	}
	else
	{
		AfxMessageBox("Error ! Impossible to read SOFIFA attributes !");
		return;
	}
	//end read custom fields
}

void CEdDlg::OnImportSoFIFAWeb()
{
	
	ofstream myfile;
	myfile.open ("debugread.txt", ios::trunc);
	myfile << "PLAYER;OPERATION;RESULT" << endl;

	int i;
	//read online SOFIFA db
	for(i=0;i<GIOCATORI_TOT;i++)
	{
		myfile << to_string((_ULonglong)i) << ";";
		if (strlen(gioc[i].url) > 0)
		{
			string link(gioc[i].url);
			myfile << "IN from " << link << ";";
			gioc_fifa[i].UpdatePlayerFromURL(link);
		}
		else
		{
			string tmpStr(gioc[i].url);
			if(tmpStr == "dummy")
			{
				myfile << "DUMMY" << ";";
				gioc_fifa[i].SetPlayerToDummy();
			}
			else
			{
				myfile << "DONOTHING" << ";";
			}
		}
		myfile << "OK" << endl;
	}
	myfile.close();

	AfxMessageBox("Done. Results will now be written into text file.");

	//write SOFIFA players on txt
	int j;
	CString fil_SOFIFAdb;
	fil_SOFIFAdb = fil_nomeCD;
	fil_SOFIFAdb.Replace( ".bin", "_SOFIFAdb.txt" );
	myfile.open (fil_SOFIFAdb, ios::trunc);
	myfile << "NO;NAME;POSITIONS;WEIGHT;HEIGHT;AGE;FOOT;WEAKFOOTSKILL;SKILLMOVES;OFFWEIGHT;DEFWEIGHT;NATIONALNO;CLUBNO;ATTRIBUTES...\n"; //header
	for(i=0;i<GIOCATORI_TOT;i++)
	{
		//index
		myfile << i << ";";

		string fifaVer = gioc[i].url;
		if(fifaVer.find("http://sofifa.com/")!=string::npos){
			fifaVer = "15"; //hardcoded

			//write base attributes
			myfile << gioc_fifa[i].name << ";";
			myfile << gioc_fifa[i].positions << ";";
			myfile << gioc_fifa[i].weight << ";";
			myfile << gioc_fifa[i].height << ";";
			myfile << gioc_fifa[i].age << ";";
			myfile << gioc_fifa[i].foot << ";";
			myfile << gioc_fifa[i].weakFootSkill << ";";
			myfile << gioc_fifa[i].skillMoves << ";";
			myfile << gioc_fifa[i].offWeight << ";";
			myfile << gioc_fifa[i].defWeight << ";";
			myfile << gioc_fifa[i].number[0] << ";";
			myfile << gioc_fifa[i].number[1] << ";";

			//get the number of custom attributes
			int nf = fifaVerNumFields[fifaVer];

			//write custom attributes
			for(j = 0;j < nf; j++)
			{
				myfile << gioc_fifa[i].attributeValues[j] << ";";
			}
		}
		myfile << endl; //"/n"
	}
	myfile.close();

	AfxMessageBox("Done.");

}

void CEdDlg::OnImportSoFIFATxt()
{

	//read SOFIFA players from txt
	int i, j;
	string line;
	CString fil_SOFIFAdb;
	fil_SOFIFAdb = fil_nomeCD;
	fil_SOFIFAdb.Replace( ".bin", "_SOFIFAdb.txt" );
	ifstream myfile;
	myfile.open (fil_SOFIFAdb);
	if (myfile.is_open())
	{
		getline(myfile,line); //header
		for(i=0;i<GIOCATORI_TOT;i++)
		{
			getline(myfile,line);
			vector<string> fields = split(line, ';');
			if(fields.size()>12)
			{
				//read base attributes
				gioc_fifa[i].name = fields[1];
				gioc_fifa[i].positions = fields[2];
				gioc_fifa[i].weight = stoi(fields[3]);
				gioc_fifa[i].height = stoi(fields[4]);
				gioc_fifa[i].age = stoi(fields[5]);
				gioc_fifa[i].foot = (fields[6] == "L") ? 'L' : 'R';
				gioc_fifa[i].weakFootSkill = stoi(fields[7]);
				gioc_fifa[i].skillMoves = stoi(fields[8]);
				gioc_fifa[i].offWeight = fields[9];
				gioc_fifa[i].defWeight = fields[10];
				gioc_fifa[i].number[0] = stoi(fields[11]);
				gioc_fifa[i].number[1] = stoi(fields[12]);

				//get the number of custom attributes
				delete [] gioc_fifa[i].attributeValues;
				if(fields.size() > 13)
				{
					int nf = fields.size() - 13;
					gioc_fifa[i].attributeValues = new int[nf];

					//write custom attributes
					for(j = 0;j < nf; j++)
					{
						gioc_fifa[i].attributeValues[j] = stoi(fields[13+j]);
					}
				}
			}
		}
		myfile.close();
		AfxMessageBox("Done.");
	}
}

void CEdDlg::OnEditOptForm()
{
	dlg_edopt.DoModal();
}

void CEdDlg::OnEditAllFromFIFA()
{
	int i, p;
	//read online SOFIFA db
	for(i=0;i<GIOCATORI_TOT;i++)
	{
		if (gioc_fifa[i].height > 0)
		{
			gioc[i].editFromFIFA(gioc_fifa[i], dlg_edopt.edit_names, dlg_edopt.edit_age_height_weight_foot, dlg_edopt.edit_characteristics);
		}
	}

	if(dlg_edopt.edit_shirt_numbers)
	{
		//set shirt numbers
		//national teams
		for(i=0;i<54;i++)
		{
			p = GIOCATORI_NC+(i*23) - 1; //-1 to start increasing
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_1 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_2 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_3 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_4 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_5 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_6 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_7 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_8 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_9 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_10 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_11 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_12 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_13 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_14 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_15 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_16 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_17 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_18 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_19 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_20 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_21 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_22 = gioc_fifa[p].number[0] - 1;}
			p++; if(gioc_fifa[p].height > 0) {squad_nazall[i].stc_numeri.order_23 = gioc_fifa[p].number[0] - 1;}
		}

		//club teams
		for(i=63;i<95;i++)
		{
			p = trovaIDml(&squad_ml[i-63].link[0]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[0] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[2]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[1] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[4]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[2] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[6]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[3] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[8]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[4] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[10]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[5] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[12]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[6] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[14]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[7] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[16]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[8] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[18]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[9] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[20]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[10] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[22]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[11] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[24]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[12] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[26]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[13] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[28]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[14] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[30]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[15] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[32]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[16] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[34]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[17] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[36]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[18] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[38]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[19] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[40]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[20] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[42]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[21] = gioc_fifa[p].number[1] - 1;}
			p = trovaIDml(&squad_ml[i-63].link[44]); if(gioc_fifa[p].height > 0) {squad_ml[i-63].str_numeri[22] = gioc_fifa[p].number[1] - 1;}
		}
	}

	OnSelezioneSquadraV();
	AfxMessageBox("Done.");
}

void setPlayerNo(int pl, int natNo, int clubNo)

{
	int i,p;
	//set shirt numbers
	//national teams
	if(pl>=GIOCATORI_NC)
	{
		i = (int)((pl-GIOCATORI_NC) / 23);
		p = (pl-GIOCATORI_NC) - i * 23;
		switch(p)
		{
			case 0: squad_nazall[i].stc_numeri.order_1 = natNo - 1;	break;
			case 1: squad_nazall[i].stc_numeri.order_2 = natNo - 1; break;
			case 2: squad_nazall[i].stc_numeri.order_3 = natNo - 1; break;
			case 3: squad_nazall[i].stc_numeri.order_4 = natNo - 1; break;
			case 4: squad_nazall[i].stc_numeri.order_5 = natNo - 1; break;
			case 5: squad_nazall[i].stc_numeri.order_6 = natNo - 1; break;
			case 6: squad_nazall[i].stc_numeri.order_7 = natNo - 1; break;
			case 7: squad_nazall[i].stc_numeri.order_8 = natNo - 1; break;
			case 8: squad_nazall[i].stc_numeri.order_9 = natNo - 1; break;
			case 9: squad_nazall[i].stc_numeri.order_10 = natNo - 1; break;
			case 10: squad_nazall[i].stc_numeri.order_11 = natNo - 1; break;
			case 11: squad_nazall[i].stc_numeri.order_12 = natNo - 1; break;
			case 12: squad_nazall[i].stc_numeri.order_13 = natNo - 1; break;
			case 13: squad_nazall[i].stc_numeri.order_14 = natNo - 1; break;
			case 14: squad_nazall[i].stc_numeri.order_15 = natNo - 1; break;
			case 15: squad_nazall[i].stc_numeri.order_16 = natNo - 1; break;
			case 16: squad_nazall[i].stc_numeri.order_17 = natNo - 1; break;
			case 17: squad_nazall[i].stc_numeri.order_18 = natNo - 1; break;
			case 18: squad_nazall[i].stc_numeri.order_19 = natNo - 1; break;
			case 19: squad_nazall[i].stc_numeri.order_20 = natNo - 1; break;
			case 20: squad_nazall[i].stc_numeri.order_21 = natNo - 1; break;
			case 21: squad_nazall[i].stc_numeri.order_22 = natNo - 1; break;
			case 22: squad_nazall[i].stc_numeri.order_23 = natNo - 1; break;
		}
	}

	//club teams
	for(i=63;i<95;i++)
	{
		p = trovaIDml(&squad_ml[i-63].link[0]); if(p == pl) {squad_ml[i-63].str_numeri[0] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[2]); if(p == pl) {squad_ml[i-63].str_numeri[1] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[4]); if(p == pl) {squad_ml[i-63].str_numeri[2] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[6]); if(p == pl) {squad_ml[i-63].str_numeri[3] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[8]); if(p == pl) {squad_ml[i-63].str_numeri[4] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[10]); if(p == pl) {squad_ml[i-63].str_numeri[5] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[12]); if(p == pl) {squad_ml[i-63].str_numeri[6] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[14]); if(p == pl) {squad_ml[i-63].str_numeri[7] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[16]); if(p == pl) {squad_ml[i-63].str_numeri[8] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[18]); if(p == pl) {squad_ml[i-63].str_numeri[9] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[20]); if(p == pl) {squad_ml[i-63].str_numeri[10] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[22]); if(p == pl) {squad_ml[i-63].str_numeri[11] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[24]); if(p == pl) {squad_ml[i-63].str_numeri[12] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[26]); if(p == pl) {squad_ml[i-63].str_numeri[13] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[28]); if(p == pl) {squad_ml[i-63].str_numeri[14] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[30]); if(p == pl) {squad_ml[i-63].str_numeri[15] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[32]); if(p == pl) {squad_ml[i-63].str_numeri[16] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[34]); if(p == pl) {squad_ml[i-63].str_numeri[17] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[36]); if(p == pl) {squad_ml[i-63].str_numeri[18] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[38]); if(p == pl) {squad_ml[i-63].str_numeri[19] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[40]); if(p == pl) {squad_ml[i-63].str_numeri[20] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[42]); if(p == pl) {squad_ml[i-63].str_numeri[21] = clubNo - 1; break;}
		p = trovaIDml(&squad_ml[i-63].link[44]); if(p == pl) {squad_ml[i-63].str_numeri[22] = clubNo - 1; break;}
	}
}

void CEdDlg::OnEditAllPlayersLook()
{
	int i;

	map<string,int> skinMap;
	i = 0;
	skinMap["A"]=i++;
	skinMap["B"]=i++;
	skinMap["C"]=i++;
	skinMap["D"]=i++;

	map<string,int> hairMap;
	i = 0;
	hairMap["A1"]=i++;	hairMap["A2"]=i++;	hairMap["A3"]=i++;
	hairMap["B1"]=i++;	hairMap["B2"]=i++;	hairMap["B3"]=i++;	hairMap["B4"]=i++;	hairMap["B5"]=i++;	hairMap["B6"]=i++;
	hairMap["C1"]=i++;	hairMap["C2"]=i++;
	hairMap["D1"]=i++;	hairMap["D2"]=i++;
	hairMap["E1"]=i++;	hairMap["E2"]=i++;
	hairMap["F1"]=i++;	hairMap["F2"]=i++;	hairMap["F3"]=i++;
	hairMap["G1"]=i++;
	hairMap["H1"]=i++;
	hairMap["I1"]=i++;	hairMap["I2"]=i++;	hairMap["I3"]=i++;
	hairMap["J1"]=i++;
	hairMap["K1"]=i++;
	hairMap["L1"]=i++;	hairMap["L2"]=i++;	hairMap["L3"]=i++;
	hairMap["M1"]=i++;
	hairMap["N1"]=i++;
	hairMap["O1"]=i++;
	hairMap["P1"]=i++;
						  
	map<string,int> hairColMap;
	i = 0;
	hairColMap["A"]=i++;
	hairColMap["B"]=i++;
	hairColMap["C"]=i++;
	hairColMap["D"]=i++;
	hairColMap["E"]=i++;
	hairColMap["F"]=i++;
	hairColMap["G"]=i++;
	hairColMap["H"]=i++;

	map<string,int> facHairMap;
	i = 0;
	facHairMap["A"]=i++;
	facHairMap["B"]=i++;
	facHairMap["C"]=i++;
	facHairMap["D"]=i++;
	facHairMap["E"]=i++;
	facHairMap["F"]=i++;
	facHairMap["G"]=i++;

	map<string,int> facHairColMap;
	i = 0;
	facHairColMap["A"]=i++;
	facHairColMap["B"]=i++;
	facHairColMap["C"]=i++;
	facHairColMap["D"]=i++;
	facHairColMap["E"]=i++;
	facHairColMap["F"]=i++;
	facHairColMap["G"]=i++;

	int defaultCharacteristic[95][5];
	string line;
	ifstream myfile;
	myfile.open("defaultlook.txt");
	if (myfile.is_open())
	{
		getline(myfile,line); //header
		for(i=0;i<95;i++)
		{
			getline(myfile,line);
			vector<string> fields = split(line, ';');
			if(fields.size()==7)
			{
				if(fields[2].size()>0) defaultCharacteristic[i][0] = skinMap[fields[2]]; else defaultCharacteristic[i][0] = -1;
				if(fields[3].size()>0) defaultCharacteristic[i][1] = hairMap[fields[3]]; else defaultCharacteristic[i][1] = -1;
				if(fields[4].size()>0) defaultCharacteristic[i][2] = hairColMap[fields[4]]; else defaultCharacteristic[i][2] = -1;
				if(fields[5].size()>0) defaultCharacteristic[i][3] = facHairMap[fields[5]]; else defaultCharacteristic[i][3] = -1;
				if(fields[6].size()>0) defaultCharacteristic[i][4] = facHairColMap[fields[6]]; else defaultCharacteristic[i][4] = -1;
			}
		}
		myfile.close();
	}
	else
	{
		AfxMessageBox("Failed to open file defaultlook.txt!");
	}

	int j, p;
	//national teams
	for(i=0;i<54;i++)
	{
		p = GIOCATORI_NC+(i*23) - 1; //-1 to start increasing
		for(j=0;j<23;j++)
		{
			p++;
			if(defaultCharacteristic[i][0]>=0) gioc[p].col_pelle = defaultCharacteristic[i][0];
			if(defaultCharacteristic[i][1]>=0) gioc[p].stile_capelli = defaultCharacteristic[i][1];
			if(defaultCharacteristic[i][2]>=0) gioc[p].col_capelli = defaultCharacteristic[i][2];
			if(defaultCharacteristic[i][3]>=0) gioc[p].stile_barba = defaultCharacteristic[i][3];
			if(defaultCharacteristic[i][4]>=0) gioc[p].col_barba = defaultCharacteristic[i][4];
		}
	}

	//club teams
	for(i=63;i<95;i++)
	{
		for(j=0;j<46;j=j+2)
		{
			p = trovaIDml(&squad_ml[i-63].link[j]);
			if(p<GIOCATORI_NC) //else look has already been done
			{
				if(defaultCharacteristic[i][0]>=0) gioc[p].col_pelle = defaultCharacteristic[i][0];
				if(defaultCharacteristic[i][1]>=0) gioc[p].stile_capelli = defaultCharacteristic[i][1];
				if(defaultCharacteristic[i][2]>=0) gioc[p].col_capelli = defaultCharacteristic[i][2];
				if(defaultCharacteristic[i][3]>=0) gioc[p].stile_barba = defaultCharacteristic[i][3];
				if(defaultCharacteristic[i][4]>=0) gioc[p].col_barba = defaultCharacteristic[i][4];
			}
		}
	}

	AfxMessageBox("Done.");
}

void CEdDlg::OnEditAllBars()
{
	int i, j, p;
	double vsum[5], wsum[5];

	int offense_weights[8] = {
		0, //GK
		0, //CB
		0, //SB
		0, //DH
		1, //SH
		3, //OH
		5, //CF
		3  //WG
	};

	int defense_weights[8] = {
		5, //GK
		4, //CB
		2, //SB
		2, //DH
		0, //SH
		0, //OH
		0, //CF
		0  //WG
	};

	int power_weights[8] = {
		3, //GK
		5, //CB
		1, //SB
		4, //DH
		1, //SH
		2, //OH
		4, //CF
		1  //WG
	};

	int speed_weights[8] = {
		0, //GK
		1, //CB
		3, //SB
		1, //DH
		5, //SH
		2, //OH
		4, //CF
		5  //WG
	};

	int tecnique_weights[8] = {
		0, //GK
		0, //CB
		0, //SB
		3, //DH
		2, //SH
		5, //OH
		4, //CF
		2  //WG
	};

	//national and all star
	for(i=0;i<56;i++)
	{
		for(j=0;j<5;j++)
		{
			vsum[j] = 0; 
			wsum[j] = 0; 
		}

		p = GIOCATORI_NC+(i*23) - 1; //-1 to start increasing
		for(j=0;j<11;j++) //solo gli 11 titolari!
		{
			p++;

			//OFFENSE
			vsum[0] = vsum[0] + gioc[p].attacco * offense_weights[gioc[p].posizione];
			wsum[0] = wsum[0] + offense_weights[gioc[p].posizione];

			//DEFENSE
			vsum[1] = vsum[1] + gioc[p].difesa * defense_weights[gioc[p].posizione];
			wsum[1] = wsum[1] + defense_weights[gioc[p].posizione];

			//POWER
			vsum[2] = vsum[2] + gioc[p].forza * power_weights[gioc[p].posizione];
			wsum[2] = wsum[2] + power_weights[gioc[p].posizione];

			//SPEED
			vsum[3] = vsum[3] + gioc[p].velocita * speed_weights[gioc[p].posizione];
			wsum[3] = wsum[3] + speed_weights[gioc[p].posizione];

			//TECNIQUE
			vsum[4] = vsum[4] + gioc[p].tecnica * tecnique_weights[gioc[p].posizione];
			wsum[4] = wsum[4] + tecnique_weights[gioc[p].posizione];

		}

		//set bars
		squad_nazall[i].bar_attacco	= (int)(vsum[0] / wsum[0] - 10 + 0.5);
		squad_nazall[i].bar_difesa	= (int)(vsum[1] / wsum[1] - 10 + 0.5);
		squad_nazall[i].bar_potenza = (int)(vsum[2] / wsum[2] - 10 + 0.5);
		squad_nazall[i].bar_velocita= (int)(vsum[3] / wsum[3] - 10 + 0.5);
		squad_nazall[i].bar_tecnica = (int)(vsum[4] / wsum[4] - 10 + 0.5);
	}

	//club teams
	for(i=63;i<95;i++)
	{
		for(j=0;j<5;j++)
		{
			vsum[j] = 0; 
			wsum[j] = 0; 
		}

		for(j=0;j<22;j=j+2) //solo gli 11 titolari!
		{
			p = trovaIDml(&squad_ml[i-63].link[j]);

			//OFFENSE
			vsum[0] = vsum[0] + gioc[p].attacco * offense_weights[gioc[p].posizione];
			wsum[0] = wsum[0] + offense_weights[gioc[p].posizione];

			//DEFENSE
			vsum[1] = vsum[1] + gioc[p].difesa * defense_weights[gioc[p].posizione];
			wsum[1] = wsum[1] + defense_weights[gioc[p].posizione];

			//POWER
			vsum[2] = vsum[2] + gioc[p].forza * power_weights[gioc[p].posizione];
			wsum[2] = wsum[2] + power_weights[gioc[p].posizione];

			//SPEED
			vsum[3] = vsum[3] + gioc[p].velocita * speed_weights[gioc[p].posizione];
			wsum[3] = wsum[3] + speed_weights[gioc[p].posizione];

			//TECNIQUE
			vsum[4] = vsum[4] + gioc[p].tecnica * tecnique_weights[gioc[p].posizione];
			wsum[4] = wsum[4] + tecnique_weights[gioc[p].posizione];

		}

		//set bars
		squad_ml[i-63].bar_attacco	= (int)(vsum[0] / wsum[0] - 10 + 0.5);
		squad_ml[i-63].bar_difesa	= (int)(vsum[1] / wsum[1] - 10 + 0.5);
		squad_ml[i-63].bar_potenza = (int)(vsum[2] / wsum[2] - 10 + 0.5);
		squad_ml[i-63].bar_velocita= (int)(vsum[3] / wsum[3] - 10 + 0.5);
		squad_ml[i-63].bar_tecnica = (int)(vsum[4] / wsum[4] - 10 + 0.5);
	}

	OnSelezioneSquadraV();
	AfxMessageBox("Done.");

}

void CEdDlg::carica_SOFIFAConversionRules()
{

	WEToIntPositionMap["GK"]=0;
	WEToIntPositionMap["CB"]=1;
	WEToIntPositionMap["SB"]=2;
	WEToIntPositionMap["DH"]=3;
	WEToIntPositionMap["SH"]=4;
	WEToIntPositionMap["OH"]=5;
	WEToIntPositionMap["CF"]=6;
	WEToIntPositionMap["WG"]=7;

	int k;
	string line;
	string myIFileName = "WE attributes conversion rules.txt";
	ifstream myIFile;
	myIFile.open (myIFileName);
	if(myIFile.is_open())
	{
		getline (myIFile,line);

		//POSITIONS
		while(line != "Position:{")
		{
			getline (myIFile,line);
		}

		getline (myIFile,line);
		while(line != "}")
		{
			vector<string> thisPositionMap = split(line, ':');
			vector<string> fifaPositions = split(thisPositionMap[1], ',');
			for(k=0;k < fifaPositions.size();k++)
			{
				fifaToWEPositionMap[fifaPositions[k]]=WEToIntPositionMap[thisPositionMap[0]];
			}
			getline (myIFile,line);
		}

		//CUSTOM FIELDS
		while(line != "$FIELDS:{")
		{
			getline (myIFile,line);
		}
		getline (myIFile,line);
		while(line != "")
		{
			//WE fields
			string WEAttribute = line.substr(0,line.find(':'));
			getline (myIFile,line);
			fieldConversionFunction fcf;
			while(line != "}")
			{
				//sub-function for a list of positions
				vector<string> WEPositions = split(line.substr(0,line.find(':')), ',');
				fieldConversionSubFunction scf;

				//sub-function description
				getline (myIFile,line);//"Function:{"
				getline (myIFile,line);//"Aggregation:{"

				getline (myIFile,line);//type:Min/Max/Avg
				string fType = line.substr(line.find(':')+1,line.size()-5);
				scf.aggregationFunctionType=-999;
				if(fType=="Avg")
				{
					scf.aggregationFunctionType=0;
				}
				else if(fType=="Max")
				{
					scf.aggregationFunctionType=1;
				}
				else if(fType=="Min")
				{
					scf.aggregationFunctionType=-1;
				}

				//fields
				//delete [] scf.fieldIndexes; scf.fieldIndexes = new int[3];
				scf.nAggrFields = 0;
				for(k=0;k<3;k++)
				{
					getline (myIFile,line);//fieldN
					if(line.size()>8)
					{
						string fifa_version = "15"; //?
						string group = line.substr(line.find(':')+1,line.find('/')-7);
						string attribute = line.substr(line.find('/')+1);

						scf.fieldIndexes[scf.nAggrFields] = fifaVerGroupFieldIndexMap[fifa_version][group][attribute];
						scf.nAggrFields++;
					}
				}

				//weights
				//delete [] scf.fieldWeights; scf.fieldWeights = new float[3];
				for(k=0;k<3;k++)
				{
					getline (myIFile,line);//weightN
					if(line.size()>8)
					{
						line = line.substr(line.find(':')+1);
						float wg = stof(line);
						scf.fieldWeights[k] = wg;
					}
				}

				getline (myIFile,line);//end Aggregation
				getline (myIFile,line);//"Discrete:{"
					
				getline (myIFile,line);//discrete field
				string discrField = line.substr(line.find(':')+1);
				scf.discreteField = 0;
				if(discrField=="Offensive work rate"){scf.discreteField = 1;};
				if(discrField=="Defensive work rate"){scf.discreteField = 2;};
				if(discrField=="Skill moves"){scf.discreteField = 3;};

				getline (myIFile,line);//"Values:{"
				getline (myIFile,line);//discrete values
				while(line != "}")
				{
					vector<string> discreteValuesMapEntry = split(line, ':');
					scf.discreteFieldValuesMap[discreteValuesMapEntry[0]]=stof(discreteValuesMapEntry[1]);
					getline (myIFile,line);//discrete values
				}

				getline (myIFile,line);//discrete value weight
				if(line.size()>7){scf.discreteFieldWeight=stof(line.substr(line.find(':')+1));}
				getline (myIFile,line);//end discrete
				getline (myIFile,line);//end aggregation function

				//conversion values
				getline (myIFile,line);//"Range:{"
				getline (myIFile,line);//values

				int k = 0;
				while(line!="}")
				{
					string upperBoundStr = line.substr(line.find(':')+1);
					if(upperBoundStr!="-")
					{
						scf.weIntervalUpperBound[k] = stof(upperBoundStr);
						k++;
					}
					getline (myIFile,line);//next value
				}
				
				if(WEPositions[0]=="ALL")
				{
					fcf.subFunctionsMap[0]=scf; //"GK"
					fcf.subFunctionsMap[1]=scf; //"CB"
					fcf.subFunctionsMap[2]=scf; //"SB"
					fcf.subFunctionsMap[3]=scf; //"DH"
					fcf.subFunctionsMap[4]=scf; //"SH"
					fcf.subFunctionsMap[5]=scf; //"OH"
					fcf.subFunctionsMap[6]=scf; //"CF"
					fcf.subFunctionsMap[7]=scf; //"WG"
				}
				else
				{
					for(k=0;k < WEPositions.size();k++)
					{
						fcf.subFunctionsMap[WEToIntPositionMap[WEPositions[k]]]=scf;
					}
				}
				
				getline (myIFile,line);//close sub-function
				getline (myIFile,line);//next sub-function
			}

			fieldConversionFunctionMap[WEAttribute]=fcf;
			getline (myIFile,line);//empty line
			getline (myIFile,line);//next function
		} //END OF CUSTOM FIELDS

		myIFile.close();
	}
}

void CEdDlg::OnWriteCD() 
{
	int i,j,p;
	char auxstr[50], auxstr1[50];
	unsigned short auxcol[16];
	CFile fil_ctrl;
	if(fil_ctrl.Open(fil_nomeCD, CFile::modeReadWrite | CFile::typeBinary) == 0)
	{
		AfxMessageBox("Error ! Impossible to write into CD image !");
		return;
	}
// squadre
	//salvare i nomi -
		// lotto kanji - ml
	fil_ctrl.Seek(OFS_NOMI_SQK, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		asciitokanji((unsigned char*)squad_ml[31-i].nomek, (unsigned char*)squad_ml[31-i].nomekanji, lun_nomik[94-i]);
		fil_ctrl.Write(&squad_ml[31-i].nomekanji,lun_nomik[94-i]*2);
	}
	for(i = 0;i < 63;i ++)
	{
		asciitokanji((unsigned char*)squad_nazall[62-i].nomek, (unsigned char*)squad_nazall[62-i].nomekanji, lun_nomik[62-i]);
		if(i == 58)
		{
			fil_ctrl.Write(&squad_nazall[62-i].nomekanji,4);
			fil_ctrl.Seek(OFS_NOMI_SQK1, CFile::begin);
			for(j = 0;j < 8;j++)
				auxstr[j] = squad_nazall[62-i].nomekanji[4+j];
			fil_ctrl.Write(auxstr,8);
		} else
			fil_ctrl.Write(&squad_nazall[62-i].nomekanji,lun_nomik[62-i]*2);
	}

		//1° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[0], lun_nomi1[94-i]);
	}
		//1° lotto - naz/alls - salto - jugoslavia (24°)
	for(i = 0;i < 63;i ++)
	{
		if(i == 40)
			fil_ctrl.Seek(OFS_NOMI_SQ1A, CFile::begin);
		fil_ctrl.Write(squad_nazall[62-i].nomi[0], lun_nomi1[62-i]);
	}
		//2° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[1],lun_nomi2[94-i]);
	}
		//2° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi[1],lun_nomi2[62-i]);
	}
		//3° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ3, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[2],lun_nomi3[94-i]);
	}
		//3° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi[2],lun_nomi3[62-i]);
	}

		//4° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ4, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[3],lun_nomi4[94-i]);
	}
		//4° lotto - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi[3],lun_nomi4[62-i]);
	}
		//5° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ5, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[4],lun_nomi5[94-i]);
	}
		//5° lotto - naz/alls - salto - francia (7°)
	for(i = 0;i < 63;i ++)
	{
		if(i == 57)
		{
			fil_ctrl.Write(squad_nazall[62-i].nomi[4], 4);
			fil_ctrl.Seek(OFS_NOMI_SQ5A, CFile::begin);
			for(j=0;j<4;j++)
				auxstr[j] = squad_nazall[62-i].nomi[4][j+4]; 
			fil_ctrl.Write(auxstr, 4);
		} else
			fil_ctrl.Write(squad_nazall[62-i].nomi[4],lun_nomi5[62-i]);
	}
		//6° lotto - ml
	fil_ctrl.Seek(OFS_NOMI_SQ6, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		if(i == 15)
			fil_ctrl.Seek(OFS_NOMI_SQ6A, CFile::begin);
		fil_ctrl.Write(squad_ml[31-i].nomi[5],lun_nomi6[94-i]);
	}
		//6° lotto - naz/alls 
	fil_ctrl.Seek(OFS_NOMI_SQ6B, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi[5],lun_nomi6[62-i]);
	}
		//minuscolo - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_M, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nome_m,lun_nomi_min[94-i]);
	}
		//minuscolo - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nome_m,lun_nomi_min[62-i]);
	}
		//abbrev.1 - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_AB1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi_a[0],4);
	}
		//abbrev.1 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi_a[0],4);
	}
		//abbrev.2 - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_AB2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi_a[1],4);
	}
		//abbrev.2 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi_a[1],4);
	}
		//abbrev.3 - ml
	fil_ctrl.Seek(OFS_NOMI_SQ_AB3, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi_a[2],4);
	}
		//abbrev.3 - naz/alls 
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(squad_nazall[62-i].nomi_a[2],4);
	}
		// nomi aggiuntivi ml - 1° lotto
	fil_ctrl.Seek(OFS_NOMI_PML1, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[31-i].nomi[6],lun_nomi_add1[31-i]);
	}
		// nomi aggiuntivi ml - 2° lotto
	fil_ctrl.Seek(OFS_NOMI_PML2, CFile::begin);
	for(i = 0;i < 32;i ++)
	{
		if(i == 30)
		{
			fil_ctrl.Write(squad_ml[31-i].nomi[7], 4);
			fil_ctrl.Seek(OFS_NOMI_PML2A, CFile::begin);
			for(j=0;j<4;j++)
				auxstr[j] = squad_ml[31-i].nomi[7][j+4]; 
			fil_ctrl.Write(auxstr, 4);
		} else
			fil_ctrl.Write(squad_ml[31-i].nomi[7],lun_nomi_add2[31-i]);
	}
	//salvare bar forza
		//nazionali-allstar
	fil_ctrl.Seek(OFS_BAR, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(&squad_nazall[i].bar_attacco,1);
		if(i == 3)
			fil_ctrl.Seek(OFS_BAR1, CFile::begin);
		fil_ctrl.Write(&squad_nazall[i].bar_difesa,1);
		fil_ctrl.Write(&squad_nazall[i].bar_potenza,1);
		fil_ctrl.Write(&squad_nazall[i].bar_velocita,1);
		fil_ctrl.Write(&squad_nazall[i].bar_tecnica,1);
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(&squad_ml[i].bar_attacco,1);
		fil_ctrl.Write(&squad_ml[i].bar_difesa,1);
		fil_ctrl.Write(&squad_ml[i].bar_potenza,1);
		fil_ctrl.Write(&squad_ml[i].bar_velocita,1);
		fil_ctrl.Write(&squad_ml[i].bar_tecnica,1);
	}

	//salvare kik
		//nazionali-allstar
	fil_ctrl.Seek(OFS_KICKER, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		fil_ctrl.Write(&squad_nazall[i].kik_punl, 1);
		fil_ctrl.Write(&squad_nazall[i].kik_punc, 1);
		fil_ctrl.Write(&squad_nazall[i].kik_angdx, 1);
		fil_ctrl.Write(&squad_nazall[i].kik_angsx, 1);
		fil_ctrl.Write(&squad_nazall[i].kik_rigori, 1);
		fil_ctrl.Write(&squad_nazall[i].kik_cap, 1);
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(&squad_ml[i].kik_punl, 1);
		fil_ctrl.Write(&squad_ml[i].kik_punc, 1);
		fil_ctrl.Write(&squad_ml[i].kik_angdx, 1);
		fil_ctrl.Write(&squad_ml[i].kik_angsx, 1);
		fil_ctrl.Write(&squad_ml[i].kik_rigori, 1);
		fil_ctrl.Write(&squad_ml[i].kik_cap, 1);
	}
		//default ml
	fil_ctrl.Seek(2,CFile::current);
	fil_ctrl.Write(&squad_defml.kik_punl, 1);
	fil_ctrl.Write(&squad_defml.kik_punc, 1);
	fil_ctrl.Write(&squad_defml.kik_angdx, 1);
	fil_ctrl.Write(&squad_defml.kik_angsx, 1);
	fil_ctrl.Write(&squad_defml.kik_rigori, 1);
	fil_ctrl.Write(&squad_defml.kik_cap, 1);

	//salvare tattiche - vedere salto
		//nazionali-allstar
	fil_ctrl.Seek(OFS_TATTICHE, CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		if(i == 32)
		{
			fil_ctrl.Write(squad_nazall[i].str_tattica,20);
			for(j=0;j<10;j++)
				auxstr[j] = squad_nazall[i].str_tattica[j+20];
			fil_ctrl.Seek(OFS_TATTICHEA, CFile::begin);
			fil_ctrl.Write(auxstr, 10);
		} else
			fil_ctrl.Write(squad_nazall[i].str_tattica,30);
	}
		//ml
	for(i = 0;i < 32;i ++)
	{
		fil_ctrl.Write(squad_ml[i].str_tattica,30);
	}
		//default ml
	fil_ctrl.Seek(2,CFile::current);
	fil_ctrl.Write(squad_defml.str_tattica,30);

	//salvare stringa numeri
		//per squadre ml
	fil_ctrl.Seek(OFS_NUMERI_ML, CFile::begin);
	fil_ctrl.Write(squad_defml.str_numeri,23);
	fil_ctrl.Seek(1,CFile::current);
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(squad_ml[i].str_numeri,23);
		//per squadre naz/all
	fil_ctrl.Seek(OFS_NUMERI_NAZ, CFile::begin);
	for(i = 0;i < 64;i ++)
		fil_ctrl.Write(&squad_nazall[i].stc_numeri,16);

	//anteprima maglia !!!!!!!!!!!!!!!!
	fil_ctrl.Seek(OFS_ANT_MAGLIE,CFile::begin);
	for(i = 0;i < 63;i ++)
	{
		switch(i)
		{	
			case 30 :
				fil_ctrl.Write(&squad_nazall[i].maglia1,32);
				fil_ctrl.Write(&squad_nazall[i].maglia2,32);
				fil_ctrl.Seek(OFS_ANT_MAGLIE1,CFile::begin);
				break;
			default :
				fil_ctrl.Write(&squad_nazall[i].maglia1,32);
				fil_ctrl.Write(&squad_nazall[i].maglia2,32);
				break;
		}
	}
	fil_ctrl.Seek(OFS_ANT_MAGLIE2,CFile::begin);
	for(i = 0;i < SQUADRE_ML;i ++)
	{
		fil_ctrl.Write(&squad_ml[i].maglia1,32);
		fil_ctrl.Write(&squad_ml[i].maglia2,32);
	}
// giocatori
	//salvare nomi
		//giocatori nazionali-alls
	fil_ctrl.Seek(OFS_NOMI_G, CFile::begin);
	fil_ctrl.Write(gioc[GIOCATORI_NC].nome, 8);
	fil_ctrl.Seek(OFS_NOMI_G+312, CFile::begin);
	for(j=0;j<2;j++)
		auxstr[j] = gioc[GIOCATORI_NC].nome[j+8];
	fil_ctrl.Write(auxstr, 2);
	for(i=1+GIOCATORI_NC;i<GIOCATORI_TOT;i++)
	{
		switch(i)
		{
			case 205+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 6);
				fil_ctrl.Seek(OFS_NOMI_G2, CFile::begin);
				for(j=0;j<4;j++)
					auxstr[j] = gioc[i].nome[j+6];
				fil_ctrl.Write(auxstr, 4);
				break;
			case 410+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 4);
				fil_ctrl.Seek(OFS_NOMI_G3, CFile::begin);
				for(j=0;j<6;j++)
					auxstr[j] = gioc[i].nome[j+4];
				fil_ctrl.Write(auxstr, 6);
				break;
			case 615+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 2);
				fil_ctrl.Seek(OFS_NOMI_G4, CFile::begin);
				for(j=0;j<8;j++)
					auxstr[j] = gioc[i].nome[j+2];
				fil_ctrl.Write(auxstr, 8);
				break;
			case 820+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_NOMI_G5, CFile::begin);
				fil_ctrl.Write(gioc[i].nome, 10);
				break;
			case 1024+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 8);
				fil_ctrl.Seek(OFS_NOMI_G6, CFile::begin);
				for(j=0;j<2;j++)
					auxstr[j] = gioc[i].nome[j+8];
				fil_ctrl.Write(auxstr, 2);
				break;
			case 1229+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 6);
				fil_ctrl.Seek(OFS_NOMI_G7, CFile::begin);
				for(j=0;j<4;j++)
					auxstr[j] = gioc[i].nome[j+6];
				fil_ctrl.Write(auxstr, 4);
				break;
			case 1434+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].nome, 4);
				fil_ctrl.Seek(OFS_NOMI_G8, CFile::begin);
				for(j=0;j<6;j++)
					auxstr[j] = gioc[i].nome[j+4];
				fil_ctrl.Write(auxstr, 6);
				break;
			default :
				fil_ctrl.Write(gioc[i].nome, 10);
				break;
		}
	}
		//giocatori non contact ml
	fil_ctrl.Seek(OFS_NOMI_GML, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		switch(i)
		{
			case 203 :
				fil_ctrl.Write(gioc[i].nome, 10);
				fil_ctrl.Seek(OFS_NOMI_GML2, CFile::begin);
				break;
			case 408 :
				fil_ctrl.Write(gioc[i].nome, 8);
				fil_ctrl.Seek(OFS_NOMI_GML3, CFile::begin);
				for(j=0;j<2;j++)
					auxstr[j] = gioc[i].nome[j+8];
				fil_ctrl.Write(auxstr, 2);
				break;
			default :
				fil_ctrl.Write(gioc[i].nome, 10);
				break;
		}
	}

	//assegnare link ml
		//default
	fil_ctrl.Seek(OFS_LINK_ML, CFile::begin);
	fil_ctrl.Write(squad_defml.link, 46);
		// tutte ml
	fil_ctrl.Seek(OFS_LINK_ML1, CFile::begin);
	for(i=0;i<SQUADRE_ML;i++)
	{
		if(i == 6)
		{
			fil_ctrl.Write(squad_ml[i].link, 28);
			fil_ctrl.Seek(OFS_LINK_ML2, CFile::begin);
			for(j=0;j<18;j++)
				auxstr[j] = squad_ml[i].link[j+28];
			fil_ctrl.Write(auxstr, 18);
		} else
		{
			fil_ctrl.Write(squad_ml[i].link, 46);
		}
	}

	//salvare bandiera, forma * 5
		//naz-all
	fil_ctrl.Seek(OFS_BANDIERE_FORMA1, CFile::begin);
	for(i = 0;i < 63;i ++)
		fil_ctrl.Write(&squad_nazall[i].stile_bandiera,1);
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(&squad_ml[i].stile_bandiera,1);
	fil_ctrl.Seek(OFS_BANDIERE_FORMA2,CFile::begin);
	for(i = 0;i < 63;i ++)
		fil_ctrl.Write(&squad_nazall[i].stile_bandiera,1);
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(&squad_ml[i].stile_bandiera,1);
	fil_ctrl.Seek(OFS_BANDIERE_FORMA3, CFile::begin);
	for(i = 0;i < 63;i ++)
		fil_ctrl.Write(&squad_nazall[i].stile_bandiera,1);
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(&squad_ml[i].stile_bandiera,1);
	fil_ctrl.Seek(OFS_BANDIERE_FORMA4, CFile::begin);
	for(i = 0;i < 63;i ++)
		fil_ctrl.Write(&squad_nazall[i].stile_bandiera,1);
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(&squad_ml[i].stile_bandiera,1);
	fil_ctrl.Seek(OFS_BANDIERE_FORMA5, CFile::begin);
	for(i = 0;i < 63;i ++)
		fil_ctrl.Write(&squad_nazall[i].stile_bandiera,1);
		//ml
	for(i = 0;i < SQUADRE_ML;i ++)
		fil_ctrl.Write(&squad_ml[i].stile_bandiera,1);
		//colori  !!!!!!!!!!!!!!!!
		//naz/all 
	fil_ctrl.Seek(OFS_BANDIERE_COLORE, CFile::begin);
	for(i = 0;i < 56;i ++)
	{
		switch(i)
		{
			case 13:
				fil_ctrl.Write(&squad_nazall[i].col_bandiera,26);
				fil_ctrl.Seek(OFS_BANDIERE_COLORE1, CFile::begin);
				for(j=0;j<3;j++)
					auxcol[j] = squad_nazall[i].col_bandiera[j+13];
				fil_ctrl.Write(auxcol,6);
				break;
			// le nuove nazionali non sono li...
			case 36:
			case 39:
			case 47:
				break;
			// ci sono nel mezzo le vecchie nazionali nord irlanda, giamaica, uae
			case 1:
			case 40:
			case 52:
				fil_ctrl.Seek(32,CFile::current);
			default :
				fil_ctrl.Write(&squad_nazall[i].col_bandiera,32);
				break;
		}
	}

	fil_ctrl.Seek(64,CFile::current);
	for(i = 0;i < 5;i ++)
		fil_ctrl.Write(&squad_ml[i].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[10].col_bandiera,32);
	for(i = 0;i < 3;i ++)
		fil_ctrl.Write(&squad_ml[i+7].col_bandiera,32);
	for(i = 0;i < 2;i ++)
		fil_ctrl.Write(&squad_ml[i+11].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[15].col_bandiera,32);
	for(i = 0;i < 4;i ++)
		fil_ctrl.Write(&squad_ml[i+18].col_bandiera,32);
	fil_ctrl.Seek(32,CFile::current);
	fil_ctrl.Write(&squad_ml[14].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[24].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[25].col_bandiera,32);
	//bayern monaco
	fil_ctrl.Write(&squad_ml[26].col_bandiera,26);
	fil_ctrl.Seek(OFS_BANDIERE_COLORE2, CFile::begin);
	for(j=0;j<3;j++)
		auxcol[j] = squad_ml[26].col_bandiera[j+13];
	fil_ctrl.Write(auxcol,6);
	fil_ctrl.Write(&squad_ml[27].col_bandiera,32);
	for(i = 0;i < 2;i ++)
		fil_ctrl.Write(&squad_ml[i+16].col_bandiera,32);
	fil_ctrl.Seek(64,CFile::current);
	fil_ctrl.Write(&squad_ml[13].col_bandiera,32);
	fil_ctrl.Seek(288,CFile::current);
	fil_ctrl.Write(&squad_nazall[39].col_bandiera,32);
	fil_ctrl.Seek(64,CFile::current);
	fil_ctrl.Write(&squad_nazall[47].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[6].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[23].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[28].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[29].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[30].col_bandiera,32);
	fil_ctrl.Write(&squad_ml[31].col_bandiera,32);
	//senegal
	fil_ctrl.Seek(OFS_BANDIERE_COLORE_SEN,CFile::begin);
	fil_ctrl.Write(&squad_nazall[36].col_bandiera,32);

	//salvare abilita - decodifica
		//naz-all
	fil_ctrl.Seek(OFS_CARAT_G, CFile::begin);
	for(p=GIOCATORI_NC;p<GIOCATORI_TOT;p++)
	{
		if( p >= 1704 && p <= 1749 )
		{
			if( p < 1727 )
			{i=trovaIDml(&link_euroas[(p-1704)*2]);}
			else
			{i=trovaIDml(&link_worldas[(p-1727)*2]);}
		}
		else
		{i=p;}

		gioc[i].decodifica();
		switch(p)
		{
			case 44+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 4);
				fil_ctrl.Seek(OFS_CARAT_G1, CFile::begin);
				for(j=0;j<8;j++)
					auxstr1[j] = gioc[i].str_carat[j+4];
				fil_ctrl.Write(auxstr1, 8);
				break;
			case 215+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G2, CFile::begin);
				fil_ctrl.Write(gioc[i].str_carat, 12);
				break;
			case 385+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 8);
				fil_ctrl.Seek(OFS_CARAT_G3, CFile::begin);
				for(j=0;j<4;j++)
					auxstr1[j] = gioc[i].str_carat[j+8];
				fil_ctrl.Write(auxstr1, 4);
				break;
			case 556+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 4);
				fil_ctrl.Seek(OFS_CARAT_G4, CFile::begin);
				for(j=0;j<8;j++)
					auxstr1[j] = gioc[i].str_carat[j+4];
				fil_ctrl.Write(auxstr1, 8);
				break;
			case 727+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G5, CFile::begin);
				fil_ctrl.Write(gioc[i].str_carat, 12);
				break;
			case 897+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 8);
				fil_ctrl.Seek(OFS_CARAT_G6, CFile::begin);
				for(j=0;j<4;j++)
					auxstr1[j] = gioc[i].str_carat[j+8];
				fil_ctrl.Write(auxstr1, 4);
				break;
			case 1068+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 4);
				fil_ctrl.Seek(OFS_CARAT_G7, CFile::begin);
				for(j=0;j<8;j++)
					auxstr1[j] = gioc[i].str_carat[j+4];
				fil_ctrl.Write(auxstr1, 8);
				break;
			case 1239+GIOCATORI_NC :
				fil_ctrl.Seek(OFS_CARAT_G8, CFile::begin);
				fil_ctrl.Write(gioc[i].str_carat, 12);
				break;
			case 1409+GIOCATORI_NC :
				fil_ctrl.Write(gioc[i].str_carat, 8);
				fil_ctrl.Seek(OFS_CARAT_G9, CFile::begin);
				for(j=0;j<4;j++)
					auxstr1[j] = gioc[i].str_carat[j+8];
				fil_ctrl.Write(auxstr1, 4);
				break;
			default :
				fil_ctrl.Write(gioc[i].str_carat, 12);
				break;
		}
	}
		//giocatori non contact ml
	fil_ctrl.Seek(OFS_CARAT_GML, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		gioc[i].decodifica();
		switch(i)
		{
			case 148 :
				fil_ctrl.Write(gioc[i].str_carat, 8);
				fil_ctrl.Seek(OFS_CARAT_GML1, CFile::begin);
				for(j=0;j<4;j++)
					auxstr1[j] = gioc[i].str_carat[j+8];
				fil_ctrl.Write(auxstr1, 4);
				break;
			case 319 :
				fil_ctrl.Write(gioc[i].str_carat, 4);
				fil_ctrl.Seek(OFS_CARAT_GML2, CFile::begin);
				for(j=0;j<8;j++)
					auxstr1[j] = gioc[i].str_carat[j+4];
				fil_ctrl.Write(auxstr1, 8);
				break;
			default :
				fil_ctrl.Write(gioc[i].str_carat, 12);
				break;
		}
	}

	//salvare costi ml
	fil_ctrl.Seek(OFS_COSTI_NAZ, CFile::begin);
	auxstr[0] = auxstr[1] = NULL;
	for(i=GIOCATORI_NC;i<GIOCATORI_TOT;i++)
	{
		if(i==1704)
		{
			fil_ctrl.Write(auxstr,2);
			i = 1750;
		}
		fil_ctrl.Write(&gioc[i].costo, 1);
	}
	fil_ctrl.Seek(OFS_COSTI_NC, CFile::begin);
	for(i=0;i<GIOCATORI_NC;i++)
	{
		fil_ctrl.Write(&gioc[i].costo, 1);
	}

	//link delle all-star
	fil_ctrl.Seek(2328964, CFile::begin);
	fil_ctrl.Write(link_euroas, 46);
	fil_ctrl.Seek(2329010, CFile::begin);
	fil_ctrl.Write(link_worldas, 46);

	//tattiche predefinite
	fil_ctrl.Seek(4822152, CFile::begin);
	auxstr[0] = auxstr[1] = auxstr[2] = NULL;
	for(i=0;i<16;i++)
	{
		fil_ctrl.Write(tattpred[15-i].nome, 6);
		fil_ctrl.Write(auxstr, 2);
	}
	fil_ctrl.Seek(374188, CFile::begin);
	for(i=0;i<16;i++)
		fil_ctrl.Write(tattpred[i].ruoli, 11);
	fil_ctrl.Seek(374780, CFile::begin);
	for(i=0;i<16;i++)
	{
		fil_ctrl.Write(tattpred[i].x, 10);
		fil_ctrl.Write(tattpred[i].y, 10);
	}

	fil_ctrl.Close();

	CString fil_nomeURL;
	fil_nomeURL = fil_nomeCD;
	fil_nomeURL.Replace( ".bin", "_url.txt" );
	ofstream fil_url;
	fil_url.open (fil_nomeURL, ios::trunc );
	for(i=0;i<GIOCATORI_TOT;i++)
	{
		fil_url << gioc[i].url << endl;
	}
	fil_url.close();

	AfxMessageBox("CD image edited !");	

}

void CEdDlg::OnKillfocusTat2() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[0] = cmb_tat2.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[0] = cmb_tat2.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[0] = cmb_tat2.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat3() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[1] = cmb_tat3.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[1] = cmb_tat3.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[1] = cmb_tat3.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat4() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[2] = cmb_tat4.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[2] = cmb_tat4.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[2] = cmb_tat4.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat5() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[3] = cmb_tat5.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[3] = cmb_tat5.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[3] = cmb_tat5.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat6() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[4] = cmb_tat6.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[4] = cmb_tat6.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[4] = cmb_tat6.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat7() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[5] = cmb_tat7.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[5] = cmb_tat7.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[5] = cmb_tat7.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat8() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[6] = cmb_tat8.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[6] = cmb_tat8.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[6] = cmb_tat8.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat9() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[7] = cmb_tat9.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[7] = cmb_tat9.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[7] = cmb_tat9.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat10() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[8] = cmb_tat10.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[8] = cmb_tat10.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[8] = cmb_tat10.GetCurSel()+2;
}

void CEdDlg::OnKillfocusTat11() 
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id<64)
		squad_nazall[id-1].str_tattica[9] = cmb_tat11.GetCurSel()+2;
	if(id>63 && id<96)
		squad_ml[id-64].str_tattica[9] = cmb_tat11.GetCurSel()+2;
	if(id == 96)
		squad_defml.str_tattica[9] = cmb_tat11.GetCurSel()+2;
}

void CEdDlg::OnKillfocusNsquad1() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad1.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[0],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[0],aux);
}

void CEdDlg::OnKillfocusNsquad2() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad2.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[1],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[1],aux);
}

void CEdDlg::OnKillfocusNsquad3() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad3.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[2],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[2],aux);
}

void CEdDlg::OnKillfocusNsquad4() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad4.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[3],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[3],aux);
}

void CEdDlg::OnKillfocusNsquad5() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad5.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[4],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[4],aux);
}

void CEdDlg::OnKillfocusNsquad6() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad6.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi[5],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[5],aux);
}

void CEdDlg::OnKillfocusNsquadk() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squadk.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomek,aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomek,aux);
}

void CEdDlg::OnKillfocusNsquadM() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad_m.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nome_m,aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nome_m,aux);
}

void CEdDlg::OnKillfocusNsquadA1() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad_a1.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi_a[0],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi_a[0],aux);
}

void CEdDlg::OnKillfocusNsquadA2() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad_a2.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi_a[1],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi_a[1],aux);
}

void CEdDlg::OnKillfocusNomiml1() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nomi_addml1.GetWindowText(aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[6],aux);
}

void CEdDlg::OnKillfocusNomiml2() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nomi_addml2.GetWindowText(aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi[7],aux);
}

void CEdDlg::OnKillfocusBarOff() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_bar_off.GetWindowText(aux);
	i = atoi(aux);
	if(id<64)
		squad_nazall[id-1].bar_attacco = i;
	if(id>63 && id<96)
		squad_ml[id-64].bar_attacco = i;
}

void CEdDlg::OnKillfocusBarDef() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_bar_def.GetWindowText(aux);
	i = atoi(aux);
	if(id<64)
		squad_nazall[id-1].bar_difesa = i;
	if(id>63 && id<96)
		squad_ml[id-64].bar_difesa = i;
}

void CEdDlg::OnKillfocusBarPow() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_bar_pow.GetWindowText(aux);
	i = atoi(aux);
	if(id<64)
		squad_nazall[id-1].bar_potenza = i;
	if(id>63 && id<96)
		squad_ml[id-64].bar_potenza = i;
}

void CEdDlg::OnKillfocusBarSpe() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_bar_spe.GetWindowText(aux);
	i = atoi(aux);
	if(id<64)
		squad_nazall[id-1].bar_velocita = i;
	if(id>63 && id<96)
		squad_ml[id-64].bar_velocita = i;
}

void CEdDlg::OnKillfocusBarTec() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_bar_tec.GetWindowText(aux);
	i = atoi(aux);
	if(id<64)
		squad_nazall[id-1].bar_tecnica = i;
	if(id>63 && id<96)
		squad_ml[id-64].bar_tecnica = i;
}

void CEdDlg::OnKillfocusKikPunl() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_punl.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_punl = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_punl = i;
	if(id == 96)
		squad_defml.kik_punl = i;
}

void CEdDlg::OnKillfocusKikPunc() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_punc.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_punc = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_punc = i;
	if(id == 96)
		squad_defml.kik_punc = i;
}

void CEdDlg::OnKillfocusKikAngsx() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_angsx.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_angsx = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_angsx = i;
	if(id == 96)
		squad_defml.kik_angsx = i;
}

void CEdDlg::OnKillfocusKikAngdx() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_angdx.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_angdx = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_angdx = i;
	if(id == 96)
		squad_defml.kik_angdx = i;
}

void CEdDlg::OnKillfocusKikRig() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_rig.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_rigori = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_rigori = i;
	if(id == 96)
		squad_defml.kik_rigori = i;
}

void CEdDlg::OnKillfocusKikCap() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	i = cmb_kik_cap.GetCurSel();
	if(id<64)
		squad_nazall[id-1].kik_cap = i;
	if(id>63 && id<96)
		squad_ml[id-64].kik_cap = i;
	if(id == 96)
		squad_defml.kik_cap = i;
}


void CEdDlg::OnKillfocusNsquadA3() 
{
	int id;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_nome_squad_a3.GetWindowText(aux);
	if(id<64)
		strcpy(squad_nazall[id-1].nomi_a[2],aux);
	if(id>63 && id<96)
		strcpy(squad_ml[id-64].nomi_a[2],aux);
}

void CEdDlg::OnKillfocusNum1() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc1.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc1.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_1 = i-1;
		gioc[462+((id-1)*23)].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[0] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[0] = i-1;
}

void CEdDlg::OnKillfocusNum2() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc2.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc2.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_2 = i-1;
		gioc[1+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[1] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[1] = i-1;
}

void CEdDlg::OnKillfocusNum3() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc3.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc3.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_3 = i-1;
		gioc[2+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[2] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[2] = i-1;
}

void CEdDlg::OnKillfocusNum4() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc4.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc4.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_4 = i-1;
		gioc[3+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[3] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[3] = i-1;
}

void CEdDlg::OnKillfocusNum5() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc5.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc5.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_5 = i-1;
		gioc[4+462+(id-1)*23];
		gioc[4+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[4] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[4] = i-1;
}

void CEdDlg::OnKillfocusNum6() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc6.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc6.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_6 = i-1;
		gioc[5+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[5] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[5] = i-1;
}

void CEdDlg::OnKillfocusNum7() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc7.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc7.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_7 = i-1;
		gioc[6+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[6] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[6] = i-1;
}

void CEdDlg::OnKillfocusNum8() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc8.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc8.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_8 = i-1;
		gioc[7+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[7] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[7] = i-1;
}

void CEdDlg::OnKillfocusNum9() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc9.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc9.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_9 = i-1;
		gioc[8+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[8] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[8] = i-1;
}

void CEdDlg::OnKillfocusNum10() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc10.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc10.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_10 = i-1;
		gioc[9+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[9] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[9] = i-1;
}

void CEdDlg::OnKillfocusNum11() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc11.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc11.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_11 = i-1;
		gioc[10+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[10] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[10] = i-1;
}

void CEdDlg::OnKillfocusNum12() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc12.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc12.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_12 = i-1;
		gioc[11+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[11] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[11] = i-1;
}

void CEdDlg::OnKillfocusNum13() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc13.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc13.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_13 = i-1;
		gioc[12+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[12] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[12] = i-1;
}

void CEdDlg::OnKillfocusNum14() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc14.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc14.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_14 = i-1;
		gioc[13+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[13] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[13] = i-1;
}

void CEdDlg::OnKillfocusNum15() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc15.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc15.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_15 = i-1;
		gioc[14+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[14] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[14] = i-1;
}

void CEdDlg::OnKillfocusNum16() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc16.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc16.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_16 = i-1;
		gioc[15+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[15] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[15] = i-1;
}

void CEdDlg::OnKillfocusNum17() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc17.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc17.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_17 = i-1;
		gioc[16+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[16] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[16] = i-1;
}

void CEdDlg::OnKillfocusNum18() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc18.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc18.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_18 = i-1;
		gioc[17+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[17] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[17] = i-1;
}

void CEdDlg::OnKillfocusNum19() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc19.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc19.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_19 = i-1;
		gioc[18+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[18] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[18] = i-1;
}

void CEdDlg::OnKillfocusNum20() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc20.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc20.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_20 = i-1;
		gioc[19+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[19] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[19] = i-1;
}

void CEdDlg::OnKillfocusNum21() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc21.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc21.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_21 = i-1;
		gioc[20+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[20] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[20] = i-1;
}

void CEdDlg::OnKillfocusNum22() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc22.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc22.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_22 = i-1;
		gioc[21+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[21] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[21] = i-1;
}

void CEdDlg::OnKillfocusNum23() 
{
	int id,i;
	CString aux;
	id = cmb_squadra.GetCurSel();
	txt_num_gioc23.GetWindowText(aux);
	i = atoi(aux);
	if(id>0 && id<64)
	{
		if(i>32)
		{
			i = 32;
			txt_num_gioc23.SetWindowText("32");
		}
		squad_nazall[id-1].stc_numeri.order_23 = i-1;
		gioc[22+462+(id-1)*23].numero = i;
	} else if(id>63 && id<96)
		squad_ml[id-64].str_numeri[22] = i-1;
	else if(id == 96)
		squad_defml.str_numeri[22] = i-1;
}

void CEdDlg::caratteristiche(int k)
{
	int id;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id<55 || id>56 && id<64)
	{
		dlg_car.id_giocatore = ((id-1)*23)+GIOCATORI_NC+k;
		dlg_car.auxgioc = gioc;
		dlg_car.auxfifapl = gioc_fifa;
		dlg_car.DoModal();
	}
	if(id == 55)
	{
		dlg_car.id_giocatore = trovaIDml(&link_euroas[k*2]);
		dlg_car.auxgioc = gioc;
		dlg_car.auxfifapl = gioc_fifa;
		dlg_car.DoModal();
	}
	if(id == 56)
	{
		dlg_car.id_giocatore = trovaIDml(&link_worldas[k*2]);
		dlg_car.auxgioc = gioc;
		dlg_car.auxfifapl = gioc_fifa;
		dlg_car.DoModal();
	}
	if(id>63 && id<96)
	{
		dlg_car.id_giocatore = trovaIDml(&squad_ml[id-64].link[k*2]);
		dlg_car.auxgioc = gioc;
		dlg_car.auxfifapl = gioc_fifa;
		dlg_car.DoModal();
	}
	if(id == 96)
	{
		dlg_car.id_giocatore = trovaIDml(&squad_defml.link[k*2]);
		dlg_car.auxgioc = gioc;
		dlg_car.auxfifapl = gioc_fifa;
		dlg_car.DoModal();
	}
	CEdDlg::OnSelezioneSquadraV();
}

void CEdDlg::OnCarat1() 
{
	caratteristiche(0);
}

void CEdDlg::OnCarat2() 
{
	caratteristiche(1);
}

void CEdDlg::OnCarat3() 
{
	caratteristiche(2);
}

void CEdDlg::OnCarat4() 
{
	caratteristiche(3);
}

void CEdDlg::OnCarat5() 
{
	caratteristiche(4);
}

void CEdDlg::OnCarat6() 
{
	caratteristiche(5);
}

void CEdDlg::OnCarat7() 
{
	caratteristiche(6);
}

void CEdDlg::OnCarat8() 
{
	caratteristiche(7);
}

void CEdDlg::OnCarat9() 
{
	caratteristiche(8);
}

void CEdDlg::OnCarat10() 
{
	caratteristiche(9);
}

void CEdDlg::OnCarat11() 
{
	caratteristiche(10);
}

void CEdDlg::OnCarat12() 
{
	caratteristiche(11);
}

void CEdDlg::OnCarat13() 
{
	caratteristiche(12);
}

void CEdDlg::OnCarat14() 
{
	caratteristiche(13);
}

void CEdDlg::OnCarat15() 
{
	caratteristiche(14);
}

void CEdDlg::OnCarat16() 
{
	caratteristiche(15);
}

void CEdDlg::OnCarat17() 
{
	caratteristiche(16);
}

void CEdDlg::OnCarat18() 
{
	caratteristiche(17);
}

void CEdDlg::OnCarat19() 
{
	caratteristiche(18);
}

void CEdDlg::OnCarat20() 
{
	caratteristiche(19);
}

void CEdDlg::OnCarat21() 
{
	caratteristiche(20);
}

void CEdDlg::OnCarat22() 
{
	caratteristiche(21);
}

void CEdDlg::OnCarat23() 
{
	caratteristiche(22);
}

void CEdDlg::sostituzione(int k)
{
	int id,i;
	squadra_ml auxml;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id<55 || id>56 && id<64)
	{
		dlg_sel.id_giocatore = ((id-1)*23)+GIOCATORI_NC+k;
		dlg_sel.auxgioc = gioc;
		dlg_sel.ml = FALSE;
		dlg_sel.DoModal();
	}
	if(id == 55)
	{
		dlg_sel.id_giocatore = trovaIDml(&link_euroas[k*2]);
		dlg_sel.auxgioc = gioc;
		for(i=0;i<46;i++)
			auxml.link[i] = link_euroas[i];
		dlg_sel.auxml = &auxml;
		dlg_sel.pos = k*2;
		dlg_sel.ml = TRUE;
		dlg_sel.DoModal();
		for(i=0;i<46;i++)
			 link_euroas[i] = auxml.link[i];
		nomiallstar();
	}
	if(id == 56)
	{
		dlg_sel.id_giocatore = trovaIDml(&link_worldas[k*2]);
		dlg_sel.auxgioc = gioc;
		for(i=0;i<46;i++)
			auxml.link[i] = link_worldas[i];
		dlg_sel.auxml = &auxml;
		dlg_sel.pos = k*2;
		dlg_sel.ml = TRUE;
		dlg_sel.DoModal();
		for(i=0;i<46;i++)
			 link_worldas[i] = auxml.link[i];
		nomiallstar();
	}
	if(id>63 && id<96)
	{
		dlg_sel.id_giocatore = trovaIDml(&squad_ml[id-64].link[k*2]);
		dlg_sel.auxgioc = gioc;
		dlg_sel.auxml = &squad_ml[id-64];
		dlg_sel.pos = k*2;
		dlg_sel.ml = TRUE;
		dlg_sel.DoModal();
	}
	if(id == 96)
	{
		dlg_sel.id_giocatore = trovaIDml(&squad_defml.link[k*2]);
		dlg_sel.auxgioc = gioc;
		dlg_sel.auxml = &squad_defml;
		dlg_sel.pos = k*2;
		dlg_sel.ml = TRUE;
		dlg_sel.DoModal();
	}
	CEdDlg::OnSelezioneSquadraV();
}

void CEdDlg::OnSost1() 
{
	sostituzione(0);	
}

void CEdDlg::OnSost2() 
{
	sostituzione(1);	
}

void CEdDlg::OnSost3() 
{
	sostituzione(2);	
}

void CEdDlg::OnSost4() 
{
	sostituzione(3);	
}

void CEdDlg::OnSost5() 
{
	sostituzione(4);	
}

void CEdDlg::OnSost6() 
{
	sostituzione(5);	
}

void CEdDlg::OnSost7() 
{
	sostituzione(6);	
}

void CEdDlg::OnSost8() 
{
	sostituzione(7);	
}

void CEdDlg::OnSost9() 
{
	sostituzione(8);	
}

void CEdDlg::OnSost10() 
{
	sostituzione(9);	
}

void CEdDlg::OnSost11() 
{
	sostituzione(10);	
}

void CEdDlg::OnSost12() 
{
	sostituzione(11);	
}

void CEdDlg::OnSost13() 
{
	sostituzione(12);	
}

void CEdDlg::OnSost14() 
{
	sostituzione(13);	
}

void CEdDlg::OnSost15() 
{
	sostituzione(14);	
}

void CEdDlg::OnSost16() 
{
	sostituzione(15);	
}

void CEdDlg::OnSost17() 
{
	sostituzione(16);	
}

void CEdDlg::OnSost18() 
{
	sostituzione(17);	
}

void CEdDlg::OnSost19() 
{
	sostituzione(18);	
}

void CEdDlg::OnSost20() 
{
	sostituzione(19);	
}

void CEdDlg::OnSost21() 
{
	sostituzione(20);	
}

void CEdDlg::OnSost22() 
{
	sostituzione(21);	
}

void CEdDlg::OnSost23() 
{
	sostituzione(22);	
}


void CEdDlg::OnEsporta() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "file MANIA 2002 (*.2002)|*.2002|";
	CString nome_file;
	int i,id = cmb_squadra.GetCurSel();

	if(id>0)
	{
		GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
		_splitpath(path, drive, dir, NULL, NULL);
		fil_path_programma = drive;
		fil_path_programma += dir;

		CFileDialog dlg(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST, filtro, NULL );
		dlg.m_ofn.lpstrInitialDir = fil_path_programma;
		dlg.m_ofn.lpstrTitle = "NEW TEAM FILE EXPORT";
		if( IDOK == dlg.DoModal() )
			nome_file = dlg.m_ofn.lpstrFile;
		else
			return;
		if(nome_file.Right(5) != ".2002")
			nome_file += ".2002";
		CFile fil_ctrl(nome_file, CFile::modeReadWrite | CFile::typeBinary | CFile::modeCreate);
		fil_ctrl.Seek(0,CFile::begin);
		// salvataggio sul nuovo file
		if(id<64)
		{
			fil_ctrl.Write("f.m.nz",6);
			fil_ctrl.Write(&squad_nazall[id-1],sizeof(squadra));
			for(i = 0;i<23;i++)
				fil_ctrl.Write(&gioc[462+i+((id-1)*23)],sizeof(giocatore));
		} else if(id>63 && id<96)
		{
			fil_ctrl.Write("f.m.ml",6);
			fil_ctrl.Write(&squad_ml[id-64],sizeof(squadra_ml));
			for(i = 0;i<23;i++)
				fil_ctrl.Write(&gioc[trovaIDml(&squad_ml[id-64].link[i*2])],sizeof(giocatore));
		} else if(id==96)
		{
			fil_ctrl.Write("f.m.ml",6);
			fil_ctrl.Write(&squad_defml,sizeof(squadra_ml));
			for(i = 0;i<23;i++)
				fil_ctrl.Write(&gioc[trovaIDml(&squad_defml.link[i*2])],sizeof(giocatore));
		}
		fil_ctrl.Close();
		AfxMessageBox("Team exported !");
	} else
		AfxMessageBox("Choose a team !");
}

void CEdDlg::OnImporta() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "file MANIA 2002 (*.2002)|*.2002|";
	char aux[10];
	CString nome_file;
	int i,id = cmb_squadra.GetCurSel();

	if(id>0)
	{
		GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
		_splitpath(path, drive, dir, NULL, NULL);
		fil_path_programma = drive;
		fil_path_programma += dir;

 		CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
		dlg.m_ofn.lpstrInitialDir = fil_path_programma;
		dlg.m_ofn.lpstrTitle = "TEAM FILE TO IMPORT";
		if( IDOK == dlg.DoModal() )
			nome_file = dlg.m_ofn.lpstrFile;
		else
			return;
		CFile fil_ctrl(nome_file, CFile::modeRead | CFile::typeBinary );
		fil_ctrl.Seek(0,CFile::begin);
		// lettura dati dal file
		if(id<64)
		{
			fil_ctrl.Read(aux,6);
			aux[6] = NULL;
			if(strcmp(aux,"f.m.nz") != 0 || fil_ctrl.GetLength() != 3814)
			{
				AfxMessageBox("Not right file  (impossible to import in national team a ml team and vice versa) !");
				return;
			}
			fil_ctrl.Read(&squad_nazall[id-1],sizeof(squadra));
			//controllo lunghezza nomi!
			squad_nazall[id-1].nomi[0][lun_nomi1[id-1]-1] = NULL;
			squad_nazall[id-1].nomi[1][lun_nomi2[id-1]-1] = NULL;
			squad_nazall[id-1].nomi[2][lun_nomi3[id-1]-1] = NULL;
			squad_nazall[id-1].nomi[3][lun_nomi4[id-1]-1] = NULL;
			squad_nazall[id-1].nomi[4][lun_nomi5[id-1]-1] = NULL;
			squad_nazall[id-1].nomi[5][lun_nomi6[id-1]-1] = NULL;
			squad_nazall[id-1].nome_m[lun_nomi_min[id-1]-1] = NULL;
			squad_nazall[id-1].nomek[lun_nomik[id-1]-1] = NULL;
			for(i = 0;i<23;i++)
				fil_ctrl.Read(&gioc[462+i+((id-1)*23)],sizeof(giocatore));
		} else if(id>63 && id<96)
		{
			fil_ctrl.Read(aux,6);
			aux[6] = NULL;
			if(strcmp(aux,"f.m.ml") != 0 || fil_ctrl.GetLength() != 3910)
			{
				AfxMessageBox("Not right file  (impossible to import in national team a ml team and vice versa) !");
				return;
			}
			fil_ctrl.Read(&squad_ml[id-64],sizeof(squadra_ml));
			squad_ml[id-64].nomi[0][lun_nomi1[id-1]-1] = NULL;
			squad_ml[id-64].nomi[1][lun_nomi2[id-1]-1] = NULL;
			squad_ml[id-64].nomi[2][lun_nomi3[id-1]-1] = NULL;
			squad_ml[id-64].nomi[3][lun_nomi4[id-1]-1] = NULL;
			squad_ml[id-64].nomi[4][lun_nomi5[id-1]-1] = NULL;
			squad_ml[id-64].nomi[5][lun_nomi6[id-1]-1] = NULL;
			squad_ml[id-64].nome_m[lun_nomi_min[id-1]-1] = NULL;
			squad_ml[id-64].nomek[lun_nomik[id-1]-1] = NULL;
			squad_ml[id-64].nomi[6][lun_nomi_add1[id-64]-1] = NULL;
			squad_ml[id-64].nomi[7][lun_nomi_add2[id-64]-1] = NULL;
			for(i = 0;i<23;i++)
				fil_ctrl.Read(&gioc[trovaIDml(&squad_ml[id-64].link[i*2])],sizeof(giocatore));
		} else if(id==96)
		{
			fil_ctrl.Read(aux,6);
			aux[6] = NULL;
			if(strcmp(aux,"f.m.ml") != 0 || fil_ctrl.GetLength() != 3910)
			{
				AfxMessageBox("Not right file  (impossible to import in national team a ml team and vice versa) !");
				return;
			}
			fil_ctrl.Read(&squad_defml,sizeof(squadra_ml));
			for(i = 0;i<23;i++)
				fil_ctrl.Read(&gioc[trovaIDml(&squad_defml.link[i*2])],sizeof(giocatore));
		}
		fil_ctrl.Close();
		CEdDlg::OnSelezioneSquadraV();		
		AfxMessageBox("Team imported !");
	} else
		AfxMessageBox("Choose a team !");
}

void CEdDlg::OnButtgraf() 
{
	int id,i;
	id = cmb_squadra.GetCurSel();
	if(id>0 && id<64)
	{
		dlg_graf.id = id;
		dlg_graf.stile_bandiera = squad_nazall[id-1].stile_bandiera;
		for(i=0;i<16;i++)
			dlg_graf.col_bandiera[i] = squad_nazall[id-1].col_bandiera[i];
		for(i=0;i<16;i++)
			dlg_graf.col_maglia1[i] = squad_nazall[id-1].maglia1[i];
		for(i=0;i<16;i++)
			dlg_graf.col_maglia2[i] = squad_nazall[id-1].maglia2[i];
		dlg_graf.DoModal();
		squad_nazall[id-1].stile_bandiera = dlg_graf.stile_bandiera;
		for(i=0;i<16;i++)
			squad_nazall[id-1].col_bandiera[i] = dlg_graf.col_bandiera[i];
		for(i=0;i<16;i++)
			squad_nazall[id-1].maglia1[i] = dlg_graf.col_maglia1[i];
		for(i=0;i<16;i++)
			squad_nazall[id-1].maglia2[i] = dlg_graf.col_maglia2[i];
	}
	if(id>63 && id<96)
	{
		dlg_graf.id = id;
		dlg_graf.stile_bandiera = squad_ml[id-64].stile_bandiera;
		for(i=0;i<16;i++)
			dlg_graf.col_bandiera[i] = squad_ml[id-64].col_bandiera[i];
		for(i=0;i<16;i++)
			dlg_graf.col_maglia1[i] = squad_ml[id-64].maglia1[i];
		for(i=0;i<16;i++)
			dlg_graf.col_maglia2[i] = squad_ml[id-64].maglia2[i];
		dlg_graf.DoModal();
		squad_ml[id-64].stile_bandiera = dlg_graf.stile_bandiera;
		for(i=0;i<16;i++)
			squad_ml[id-64].col_bandiera[i] = dlg_graf.col_bandiera[i];
		for(i=0;i<16;i++)
			squad_ml[id-64].maglia1[i] = dlg_graf.col_maglia1[i];
		for(i=0;i<16;i++)
			squad_ml[id-64].maglia2[i] = dlg_graf.col_maglia2[i];
	}
}

void CEdDlg::OnNumeriDefault() 
{
	int i;
	for(i=0;i<64;i++)
	{
		gioc[462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_1+1;
		gioc[1+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_2+1;
		gioc[2+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_3+1;
		gioc[3+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_4+1;
		gioc[4+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_5+1;
		gioc[5+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_6+1;
		gioc[6+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_7+1;
		gioc[7+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_8+1;
		gioc[8+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_9+1;
		gioc[9+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_10+1;
		gioc[10+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_11+1;
		gioc[11+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_12+1;
		gioc[12+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_13+1;
		gioc[13+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_14+1;
		gioc[14+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_15+1;
		gioc[15+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_16+1;
		gioc[16+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_17+1;
		gioc[17+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_18+1;
		gioc[18+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_19+1;
		gioc[19+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_20+1;
		gioc[20+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_21+1;
		gioc[21+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_22+1;
		gioc[22+462+(i*23)].numero = (int)squad_nazall[i].stc_numeri.order_23+1;
	}
	AfxMessageBox("Operation done!");
}

void CEdDlg::OnReload() 
{
	carica_dabin();
	carica_url();
	OnSelezioneSquadraV();
}

int CalcolaCostoGiocatore(int i)
{
//{"GK", "CB", "SB", "DH", "SH", "OH", "CF", "WG"};
	double k = 16;
	switch(gioc[i].posizione)
	{
		//portiere
		case 0:
			k += (gioc[i].accel-15) * 0.45;
			k += (gioc[i].velocita-15) * 0.45;
			k += (gioc[i].aggress-12) * 0.05;
			k += (gioc[i].riflessi-16) * 0.7;
			k += (gioc[i].altezza-180) * 0.07;
			k += gioc[i].fuori_ruolo * 0.5;
			k += (gioc[i].forza-16) * 0.7;
			k += (gioc[i].resistenza-14) * 0.15;
			k += (gioc[i].tecnica-13) * 0.15;
			k += (gioc[i].attacco-12) * 0.05;
			k += (gioc[i].difesa-16) * 0.8;
			k += (gioc[i].dribbling-14) * 0.08;
			k += (gioc[i].effetto-14) * 0.08;
			k += (gioc[i].passaggio-14) * 0.08;
			k += (gioc[i].pot_tiro-15) * 0.3;
			k += (gioc[i].prec_tiro-14) * 0.2;
			k += (gioc[i].salto-15) * 0.8;
			k += (gioc[i].testa-13) * 0.15;
				
			// i 9!!
			if(gioc[i].accel == 19)
				k += 0.4;
			if(gioc[i].velocita == 19)
				k += 0.4;
			if(gioc[i].riflessi == 19)
				k += 0.8;
			if(gioc[i].forza == 19)
				k += 0.8;
			if(gioc[i].resistenza == 19)
				k += 0.3;
			if(gioc[i].tecnica == 19)
				k += 0.4;
			if(gioc[i].attacco == 19)
				k += 0.2;
			if(gioc[i].difesa == 19)
				k += 0.9;
			if(gioc[i].effetto == 19)
				k += 0.15;
			if(gioc[i].passaggio == 19)
				k += 0.25;
			if(gioc[i].pot_tiro == 19)
				k += 0.2;
			if(gioc[i].prec_tiro == 19)
				k += 0.2;
			if(gioc[i].salto == 19)
				k += 0.8;
			if(gioc[i].testa == 19)
				k += 0.2;

			break;
		//difensore
		case 1:
		case 2:
			k += 1;
			if(gioc[i].piede == 2) k += 1;
			k += (gioc[i].accel-16) * 0.55;
			k += (gioc[i].velocita-16) * 0.55;
			k += (gioc[i].aggress-13) * 0.2;
			k += (gioc[i].riflessi-15) * 0.35;
			k += (gioc[i].altezza-170) * 0.045;
			k += gioc[i].fuori_ruolo * 1;
			k += (gioc[i].forza-16) * 0.6;
			k += (gioc[i].resistenza-16) * 0.4;
			k += (gioc[i].tecnica-15) * 0.4;
			k += (gioc[i].attacco-14) * 0.3;
			k += (gioc[i].difesa-16) * 0.85;
			k += (gioc[i].dribbling-14) * 0.25;
			k += (gioc[i].effetto-14) * 0.25;
			k += (gioc[i].passaggio-15) * 0.35;
			k += (gioc[i].pot_tiro-16) * 0.35;
			k += (gioc[i].prec_tiro-14) * 0.3;
			k += (gioc[i].salto-16) * 0.5;
			k += (gioc[i].testa-15) * 0.5;
				
			// i 9!!
			if(gioc[i].accel == 19)
				k += 0.5;
			if(gioc[i].velocita == 19)
				k += 0.5;
			if(gioc[i].riflessi == 19)
				k += 0.35;
			if(gioc[i].aggress == 19)
				k += 0.25;
			if(gioc[i].forza == 19)
				k += 0.8;
			if(gioc[i].resistenza == 19)
				k += 0.45;
			if(gioc[i].tecnica == 19)
				k += 0.5;
			if(gioc[i].attacco == 19)
				k += 0.5;
			if(gioc[i].difesa == 19)
				k += 0.9;
			if(gioc[i].dribbling == 19)
				k += 0.4;
			if(gioc[i].effetto == 19)
				k += 0.5;
			if(gioc[i].passaggio == 19)
				k += 0.4;
			if(gioc[i].pot_tiro == 19)
				k += 0.5;
			if(gioc[i].prec_tiro == 19)
				k += 0.5;
			if(gioc[i].salto == 19)
				k += 0.7;
			if(gioc[i].testa == 19)
				k += 0.7;

			break;
		//centrocampista
		case 3:
		case 4:
		case 5:
			k += 3;
			if(gioc[i].piede == 2) k += 1.5;
			k += (gioc[i].accel-16) * 0.4;
			k += (gioc[i].velocita-16) * 0.4;
			k += (gioc[i].aggress-12) * 0.1;
			k += (gioc[i].riflessi-14) * 0.3;
			k += (gioc[i].altezza-170) * 0.04;
			k += gioc[i].fuori_ruolo * 1;
			k += (gioc[i].forza-16) * 0.3;
			k += (gioc[i].resistenza-16) * 0.45;
			k += (gioc[i].tecnica-16) * 0.6;
			k += (gioc[i].attacco-15) * 0.4;
			k += (gioc[i].difesa-15) * 0.3;
			k += (gioc[i].dribbling-14) * 0.4;
			k += (gioc[i].effetto-14) * 0.5;
			k += (gioc[i].passaggio-16) * 0.6;
			k += (gioc[i].pot_tiro-16) * 0.5;
			k += (gioc[i].prec_tiro-16) * 0.6;
			k += (gioc[i].salto-16) * 0.5;
			k += (gioc[i].testa-15) * 0.55;
				
			// i 9!!
			if(gioc[i].accel == 19)
				k += 0.4;
			if(gioc[i].velocita == 19)
				k += 0.4;
			if(gioc[i].riflessi == 19)
				k += 0.3;
			if(gioc[i].aggress == 19)
				k += 0.2;
			if(gioc[i].forza == 19)
				k += 0.5;
			if(gioc[i].resistenza == 19)
				k += 0.5;
			if(gioc[i].tecnica == 19)
				k += 0.8;
			if(gioc[i].attacco == 19)
				k += 0.7;
			if(gioc[i].difesa == 19)
				k += 0.5;
			if(gioc[i].dribbling == 19)
				k += 0.5;
			if(gioc[i].effetto == 19)
				k += 0.8;
			if(gioc[i].passaggio == 19)
				k += 0.7;
			if(gioc[i].pot_tiro == 19)
				k += 0.7;
			if(gioc[i].prec_tiro == 19)
				k += 0.8;
			if(gioc[i].salto == 19)
				k += 0.5;
			if(gioc[i].testa == 19)
				k += 0.6;
			break;
		//attaccante
		case 6:
		case 7:
			k += 7;
			if(gioc[i].piede == 2) k += 2;
			k += (gioc[i].accel-16) * 0.6;
			k += (gioc[i].velocita-16) * 0.6;
			k += (gioc[i].aggress-14) * 0.4;
			k += (gioc[i].riflessi-16) * 0.4;
			k += (gioc[i].altezza-170) * 0.04;
			k += gioc[i].fuori_ruolo * 1.5;
			k += (gioc[i].forza-16) * 0.45;
			k += (gioc[i].resistenza-16) * 0.45;
			k += (gioc[i].tecnica-16) * 0.9;
			k += (gioc[i].attacco-16) * 0.9;
			k += (gioc[i].difesa-13) * 0.3;
			k += (gioc[i].dribbling-16) * 0.8;
			k += (gioc[i].effetto-16) * 0.8;
			k += (gioc[i].passaggio-16) * 0.7;
			k += (gioc[i].pot_tiro-16) * 0.9;
			k += (gioc[i].prec_tiro-16) * 0.9;
			k += (gioc[i].salto-16) * 0.6;
			k += (gioc[i].testa-16) * 0.7;
				
			// i 9!!
			if(gioc[i].accel == 19)
				k += 0.6;
			if(gioc[i].velocita == 19)
				k += 0.6;
			if(gioc[i].riflessi == 19)
				k += 0.5;
			if(gioc[i].aggress == 19)
				k += 0.4;
			if(gioc[i].forza == 19)
				k += 0.5;
			if(gioc[i].resistenza == 19)
				k += 0.5;
			if(gioc[i].tecnica == 19)
				k += 0.9;
			if(gioc[i].attacco == 19)
				k += 0.9;
			if(gioc[i].difesa == 19)
				k += 0.3;
			if(gioc[i].dribbling == 19)
				k += 0.9;
			if(gioc[i].effetto == 19)
				k += 0.9;
			if(gioc[i].passaggio == 19)
				k += 0.9;
			if(gioc[i].pot_tiro == 19)
				k += 0.9;
			if(gioc[i].prec_tiro == 19)
				k += 0.9;
			if(gioc[i].salto == 19)
				k += 0.7;
			if(gioc[i].testa == 19)
				k += 0.8;
			break;
	}
	if(k<1) k = 1;
	return (int)ceil(k);
}

void CEdDlg::OnCalcolaCostiML() 
{
	int i;
	double k;
	for(i=0;i<GIOCATORI_TOT;i++)
	{
		gioc[i].costo = CalcolaCostoGiocatore(i);
	}
	AfxMessageBox("Operation done!");
}


void CEdDlg::OnOrdinaPanchina() 
{
	giocatore gapp;
	int i,k,id,j,lk[12];
	char auxlk[2];
	k = cmb_squadra.GetCurSel();
	if(k>0 && k<64)
	{
		//portieri !
		id = ((k-1)*23)+11+462;
		for(i=0;i<12;i++)
		{
			if(gioc[id+i].posizione == 0)
			{
				gioc[id+i].posizione = 57;
			}
		}
		// ordine !
		for(i=0;i<12;i++)
		{
			id = ((k-1)*23)+11+i+462;
			for(j=1;j<12-i;j++)
			{
				if(gioc[id].posizione > gioc[id+j].posizione)
				//&& gioc[id].posizione != 0 && gioc[id+j].posizione != 0
				{
				//appoggia giocatore da sostituire
				strcpy(gapp.nome,gioc[id].nome);
				gapp.accel = gioc[id].accel;
				gapp.aggress = gioc[id].aggress;
				gapp.altezza = gioc[id].altezza;
				gapp.attacco = gioc[id].attacco;
				gapp.col_barba = gioc[id].col_barba;
				gapp.col_capelli = gioc[id].col_capelli;
				gapp.col_pelle = gioc[id].col_pelle;
				gapp.corporatura = gioc[id].corporatura;
				gapp.costo = gioc[id].costo;
				gapp.difesa = gioc[id].difesa;
				gapp.dribbling = gioc[id].dribbling;
				gapp.effetto = gioc[id].effetto;
				gapp.eta = gioc[id].eta;
				gapp.forza = gioc[id].forza;
				gapp.fuori_ruolo = gioc[id].fuori_ruolo;
				gapp.numero = gioc[id].numero;
				gapp.passaggio = gioc[id].passaggio;
				gapp.piede = gioc[id].piede;
				gapp.posizione = gioc[id].posizione;
				gapp.pot_tiro = gioc[id].pot_tiro;
				gapp.prec_tiro = gioc[id].prec_tiro;
				gapp.resistenza = gioc[id].resistenza;
				gapp.riflessi = gioc[id].riflessi;
				gapp.salto = gioc[id].salto;
				gapp.scarpe = gioc[id].scarpe;
				gapp.stile_barba = gioc[id].stile_barba;
				gapp.stile_capelli = gioc[id].stile_capelli;
				gapp.tecnica = gioc[id].tecnica;
				gapp.testa = gioc[id].testa;
				gapp.velocita = gioc[id].velocita;
				//copia giocatore sostituto
				strcpy(gioc[id].nome,gioc[id+j].nome);
				gioc[id].accel = gioc[id+j].accel;
				gioc[id].aggress = gioc[id+j].aggress;
				gioc[id].altezza = gioc[id+j].altezza;
				gioc[id].attacco = gioc[id+j].attacco;
				gioc[id].col_barba = gioc[id+j].col_barba;
				gioc[id].col_capelli = gioc[id+j].col_capelli;
				gioc[id].col_pelle = gioc[id+j].col_pelle;
				gioc[id].corporatura = gioc[id+j].corporatura;
				gioc[id].costo = gioc[id+j].costo;
				gioc[id].difesa = gioc[id+j].difesa;
				gioc[id].dribbling = gioc[id+j].dribbling;
				gioc[id].effetto = gioc[id+j].effetto;
				gioc[id].eta = gioc[id+j].eta;
				gioc[id].forza = gioc[id+j].forza;
				gioc[id].fuori_ruolo = gioc[id+j].fuori_ruolo;
				gioc[id].numero = gioc[id+j].numero;
				gioc[id].passaggio = gioc[id+j].passaggio;
				gioc[id].piede = gioc[id+j].piede;
				gioc[id].posizione = gioc[id+j].posizione;
				gioc[id].pot_tiro = gioc[id+j].pot_tiro;
				gioc[id].prec_tiro = gioc[id+j].prec_tiro;
				gioc[id].resistenza = gioc[id+j].resistenza;
				gioc[id].riflessi = gioc[id+j].riflessi;
				gioc[id].salto = gioc[id+j].salto;
				gioc[id].scarpe = gioc[id+j].scarpe;
				gioc[id].stile_barba = gioc[id+j].stile_barba;
				gioc[id].stile_capelli = gioc[id+j].stile_capelli;
				gioc[id].tecnica = gioc[id+j].tecnica;
				gioc[id].testa = gioc[id+j].testa;
				gioc[id].velocita = gioc[id+j].velocita;
				//ripassa 
				gioc[id+j].accel = gapp.accel;
				gioc[id+j].aggress = gapp.aggress;
				gioc[id+j].altezza = gapp.altezza;
				gioc[id+j].attacco = gapp.attacco;
				gioc[id+j].col_barba = gapp.col_barba;
				gioc[id+j].col_capelli = gapp.col_capelli;
				gioc[id+j].col_pelle = gapp.col_pelle;
				gioc[id+j].corporatura = gapp.corporatura;
				gioc[id+j].costo = gapp.costo;
				gioc[id+j].difesa = gapp.difesa;
				gioc[id+j].dribbling = gapp.dribbling;
				gioc[id+j].effetto = gapp.effetto;
				gioc[id+j].eta = gapp.eta;
				gioc[id+j].forza = gapp.forza;
				gioc[id+j].fuori_ruolo = gapp.fuori_ruolo;
				strcpy(gioc[id+j].nome,gapp.nome);
				gioc[id+j].numero = gapp.numero;
				gioc[id+j].passaggio = gapp.passaggio;
				gioc[id+j].piede = gapp.piede;
				gioc[id+j].posizione = gapp.posizione;
				gioc[id+j].pot_tiro = gapp.pot_tiro;
				gioc[id+j].prec_tiro = gapp.prec_tiro;
				gioc[id+j].resistenza = gapp.resistenza;
				gioc[id+j].riflessi = gapp.riflessi;
				gioc[id+j].salto = gapp.salto;
				gioc[id+j].scarpe = gapp.scarpe;
				gioc[id+j].stile_barba = gapp.stile_barba;
				gioc[id+j].stile_capelli = gapp.stile_capelli;
				gioc[id+j].tecnica = gapp.tecnica;
				gioc[id+j].testa = gapp.testa;
				gioc[id+j].velocita = gapp.velocita;
				}
			}
		}
		//portieri !
		id = ((k-1)*23)+11+462;
		j = 0;
		for(i=0;i<12;i++)
		{
			if(gioc[id+i].posizione == 57)
			{
				gioc[id+i].posizione = 0;
				j ++;
			}
		}
		id += 11;
		if(j == 1)
		{
			//appoggia giocatore da sostituire
			strcpy(gapp.nome,gioc[id].nome);
			gapp.accel = gioc[id].accel;
			gapp.aggress = gioc[id].aggress;
			gapp.altezza = gioc[id].altezza;
			gapp.attacco = gioc[id].attacco;
			gapp.col_barba = gioc[id].col_barba;
			gapp.col_capelli = gioc[id].col_capelli;
			gapp.col_pelle = gioc[id].col_pelle;
			gapp.corporatura = gioc[id].corporatura;
			gapp.costo = gioc[id].costo;
			gapp.difesa = gioc[id].difesa;
			gapp.dribbling = gioc[id].dribbling;
			gapp.effetto = gioc[id].effetto;
			gapp.eta = gioc[id].eta;
			gapp.forza = gioc[id].forza;
			gapp.fuori_ruolo = gioc[id].fuori_ruolo;
			gapp.numero = gioc[id].numero;
			gapp.passaggio = gioc[id].passaggio;
			gapp.piede = gioc[id].piede;
			gapp.posizione = gioc[id].posizione;
			gapp.pot_tiro = gioc[id].pot_tiro;
			gapp.prec_tiro = gioc[id].prec_tiro;
			gapp.resistenza = gioc[id].resistenza;
			gapp.riflessi = gioc[id].riflessi;
			gapp.salto = gioc[id].salto;
			gapp.scarpe = gioc[id].scarpe;
			gapp.stile_barba = gioc[id].stile_barba;
			gapp.stile_capelli = gioc[id].stile_capelli;
			gapp.tecnica = gioc[id].tecnica;
			gapp.testa = gioc[id].testa;
			gapp.velocita = gioc[id].velocita;
			//copia giocatore sostituto
			strcpy(gioc[id].nome,gioc[id-1].nome);
			gioc[id].accel = gioc[id-1].accel;
			gioc[id].aggress = gioc[id-1].aggress;
			gioc[id].altezza = gioc[id-1].altezza;
			gioc[id].attacco = gioc[id-1].attacco;
			gioc[id].col_barba = gioc[id-1].col_barba;
			gioc[id].col_capelli = gioc[id-1].col_capelli;
			gioc[id].col_pelle = gioc[id-1].col_pelle;
			gioc[id].corporatura = gioc[id-1].corporatura;
			gioc[id].costo = gioc[id-1].costo;
			gioc[id].difesa = gioc[id-1].difesa;
			gioc[id].dribbling = gioc[id-1].dribbling;
			gioc[id].effetto = gioc[id-1].effetto;
			gioc[id].eta = gioc[id-1].eta;
			gioc[id].forza = gioc[id-1].forza;
			gioc[id].fuori_ruolo = gioc[id-1].fuori_ruolo;
			gioc[id].numero = gioc[id-1].numero;
			gioc[id].passaggio = gioc[id-1].passaggio;
			gioc[id].piede = gioc[id-1].piede;
			gioc[id].posizione = gioc[id-1].posizione;
			gioc[id].pot_tiro = gioc[id-1].pot_tiro;
			gioc[id].prec_tiro = gioc[id-1].prec_tiro;
			gioc[id].resistenza = gioc[id-1].resistenza;
			gioc[id].riflessi = gioc[id-1].riflessi;
			gioc[id].salto = gioc[id-1].salto;
			gioc[id].scarpe = gioc[id-1].scarpe;
			gioc[id].stile_barba = gioc[id-1].stile_barba;
			gioc[id].stile_capelli = gioc[id-1].stile_capelli;
			gioc[id].tecnica = gioc[id-1].tecnica;
			gioc[id].testa = gioc[id-1].testa;
			gioc[id].velocita = gioc[id-1].velocita;
			//ripassa 
			gioc[id-1].accel = gapp.accel;
			gioc[id-1].aggress = gapp.aggress;
			gioc[id-1].altezza = gapp.altezza;
			gioc[id-1].attacco = gapp.attacco;
			gioc[id-1].col_barba = gapp.col_barba;
			gioc[id-1].col_capelli = gapp.col_capelli;
			gioc[id-1].col_pelle = gapp.col_pelle;
			gioc[id-1].corporatura = gapp.corporatura;
			gioc[id-1].costo = gapp.costo;
			gioc[id-1].difesa = gapp.difesa;
			gioc[id-1].dribbling = gapp.dribbling;
			gioc[id-1].effetto = gapp.effetto;
			gioc[id-1].eta = gapp.eta;
			gioc[id-1].forza = gapp.forza;
			gioc[id-1].fuori_ruolo = gapp.fuori_ruolo;
			strcpy(gioc[id-1].nome,gapp.nome);
			gioc[id-1].numero = gapp.numero;
			gioc[id-1].passaggio = gapp.passaggio;
			gioc[id-1].piede = gapp.piede;
			gioc[id-1].posizione = gapp.posizione;
			gioc[id-1].pot_tiro = gapp.pot_tiro;
			gioc[id-1].prec_tiro = gapp.prec_tiro;
			gioc[id-1].resistenza = gapp.resistenza;
			gioc[id-1].riflessi = gapp.riflessi;
			gioc[id-1].salto = gapp.salto;
			gioc[id-1].scarpe = gapp.scarpe;
			gioc[id-1].stile_barba = gapp.stile_barba;
			gioc[id-1].stile_capelli = gapp.stile_capelli;
			gioc[id-1].tecnica = gapp.tecnica;
			gioc[id-1].testa = gapp.testa;
			gioc[id-1].velocita = gapp.velocita;
		}
	} else if(k>63 && k<96)
	{
		for(i=0;i<12;i++)
			lk[i] = trovaIDml(&squad_ml[k-64].link[22+(i*2)]);
		//portieri !
		for(i=0;i<12;i++)
		{
			if(gioc[lk[i]].posizione == 0)
			{
				gioc[lk[i]].posizione = 57;
			}
		}
		// ordine !
		for(i=0;i<12;i++)
		{
			for(j=1;j<12-i;j++)
			{
				if(gioc[lk[i]].posizione > gioc[lk[i+j]].posizione)
				{
					auxlk[1] = squad_ml[k-64].link[22+(i*2)];
					auxlk[2] = squad_ml[k-64].link[22+(i*2)+1];
					squad_ml[k-64].link[22+(i*2)] = squad_ml[k-64].link[22+((i+j)*2)];
					squad_ml[k-64].link[22+(i*2)+1] = squad_ml[k-64].link[22+((i+j)*2)+1];
					squad_ml[k-64].link[22+((i+j)*2)] = auxlk[1];
					squad_ml[k-64].link[22+((i+j)*2)+1] = auxlk[2];
				}
			}
		}
		//portieri !
		j = 0;
		for(i=0;i<12;i++)
		{
			if(gioc[lk[i]].posizione == 57)
			{
				gioc[lk[i]].posizione = 0;
				j ++;
			}
		}
		if(j == 1)
		{
			auxlk[1] = squad_ml[k-64].link[42];
			auxlk[2] = squad_ml[k-64].link[43];
			squad_ml[k-64].link[42] = squad_ml[k-64].link[44];
			squad_ml[k-64].link[43] = squad_ml[k-64].link[45];
			squad_ml[k-64].link[44] = auxlk[1];
			squad_ml[k-64].link[45] = auxlk[2];
		}
	
	} else if(k == 96)
	{
		for(i=0;i<12;i++)
			lk[i] = trovaIDml(&squad_defml.link[22+(i*2)]);
		//portieri !
		for(i=0;i<12;i++)
		{
			if(gioc[lk[i]].posizione == 0)
			{
				gioc[lk[i]].posizione = 57;
			}
		}
		// ordine !
		for(i=0;i<12;i++)
		{
			for(j=1;j<12-i;j++)
			{
				if(gioc[lk[i]].posizione > gioc[lk[i+j]].posizione)
				{
					auxlk[1] = squad_defml.link[22+(i*2)];
					auxlk[2] = squad_defml.link[22+(i*2)+1];
					squad_defml.link[22+(i*2)] = squad_defml.link[22+((i+j)*2)];
					squad_defml.link[22+(i*2)+1] = squad_defml.link[22+((i+j)*2)+1];
					squad_defml.link[22+((i+j)*2)] = auxlk[1];
					squad_defml.link[22+((i+j)*2)+1] = auxlk[2];
				}
			}
		}
		//portieri !
		j = 0;
		for(i=0;i<12;i++)
		{
			if(gioc[lk[i]].posizione == 57)
			{
				gioc[lk[i]].posizione = 0;
				j ++;
			}
		}
		if(j == 1)
		{
			auxlk[1] = squad_defml.link[42];
			auxlk[2] = squad_defml.link[43];
			squad_defml.link[42] = squad_defml.link[44];
			squad_defml.link[43] = squad_defml.link[45];
			squad_defml.link[44] = auxlk[1];
			squad_defml.link[45] = auxlk[2];
		}
	
	}

	AfxMessageBox("Operation done!");
	OnSelezioneSquadraV();
}

void CEdDlg::OnImportaTot() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "TOTAL file MANIA 2002 (*.tt2002)|*.tt2002|";
	char aux[10];
	CString nome_file;
	int i,j;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

 	CFileDialog dlg(TRUE, NULL, NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "IMPORT FILE";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	CFile fil_ctrl(nome_file, CFile::modeRead | CFile::typeBinary );
	fil_ctrl.Seek(0,CFile::begin);
	// lettura dati dal file
	fil_ctrl.Read(aux,6);
	aux[6] = NULL;
	if(strcmp(aux,"f.m.tt") != 0 || fil_ctrl.GetLength() != 369538)
	{
		AfxMessageBox("Not right file !");
		return;
	}
	for(i=0;i<63;i++)
	{
		fil_ctrl.Read(&squad_nazall[i],sizeof(squadra));
		//controllo lunghezza nomi!
		squad_nazall[i].nomi[0][lun_nomi1[i]-1] = NULL;
		squad_nazall[i].nomi[1][lun_nomi2[i]-1] = NULL;
		squad_nazall[i].nomi[2][lun_nomi3[i]-1] = NULL;
		squad_nazall[i].nomi[3][lun_nomi4[i]-1] = NULL;
		squad_nazall[i].nomi[4][lun_nomi5[i]-1] = NULL;
		squad_nazall[i].nomi[5][lun_nomi6[i]-1] = NULL;
		squad_nazall[i].nome_m[lun_nomi_min[i]-1] = NULL;
		squad_nazall[i].nomek[lun_nomik[i]-1] = NULL;
		for(j = 0;j<23;j++)
			fil_ctrl.Read(&gioc[462+j+(i*23)],sizeof(giocatore));
	} 
	for(i=0;i<32;i++)
	{
		fil_ctrl.Read(&squad_ml[i],sizeof(squadra_ml));
		squad_ml[i].nomi[0][lun_nomi1[i+63]-1] = NULL;
		squad_ml[i].nomi[1][lun_nomi2[i+63]-1] = NULL;
		squad_ml[i].nomi[2][lun_nomi3[i+63]-1] = NULL;
		squad_ml[i].nomi[3][lun_nomi4[i+63]-1] = NULL;
		squad_ml[i].nomi[4][lun_nomi5[i+63]-1] = NULL;
		squad_ml[i].nomi[5][lun_nomi6[i+63]-1] = NULL;
		squad_ml[i].nome_m[lun_nomi_min[i+63]-1] = NULL;
		squad_ml[i].nomek[lun_nomik[i+63]-1] = NULL;
		squad_ml[i].nomi[6][lun_nomi_add1[i]-1] = NULL;
		squad_ml[i].nomi[7][lun_nomi_add2[i]-1] = NULL;
		for(j = 0;j<23;j++)
			fil_ctrl.Read(&gioc[trovaIDml(&squad_ml[i].link[j*2])],sizeof(giocatore));
	}
	fil_ctrl.Read(&squad_defml,sizeof(squadra_ml));
	for(j = 0;j<23;j++)
		fil_ctrl.Read(&gioc[trovaIDml(&squad_defml.link[j*2])],sizeof(giocatore));
	fil_ctrl.Read(&link_euroas,46);
	fil_ctrl.Read(&link_worldas,46);
	for(j=0;j<16;j++)
		fil_ctrl.Read(&tattpred[j],sizeof(tattica));
	fil_ctrl.Close();
	CEdDlg::OnSelezioneSquadraV();		
	AfxMessageBox("Operation done !");
}

void CEdDlg::OnEsportaTot() 
{
	char path[_MAX_PATH];
	char drive[_MAX_DRIVE];
	char dir[_MAX_DIR];
	char filtro[] = "TOTAL file MANIA 2002 (*.tt2002)|*.tt2002|";
	CString nome_file;
	int i,j;

	GetModuleFileName(AfxGetInstanceHandle(), path, MAX_PATH);
	_splitpath(path, drive, dir, NULL, NULL);
	fil_path_programma = drive;
	fil_path_programma += dir;

	CFileDialog dlg(FALSE, NULL, NULL, OFN_HIDEREADONLY | OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST, filtro, NULL );
	dlg.m_ofn.lpstrInitialDir = fil_path_programma;
	dlg.m_ofn.lpstrTitle = "NEW FILE TO EXPORT ";
	if( IDOK == dlg.DoModal() )
		nome_file = dlg.m_ofn.lpstrFile;
	else
		return;
	if(nome_file.Right(7) != ".tt2002")
		nome_file += ".tt2002";
	CFile fil_ctrl(nome_file, CFile::modeReadWrite | CFile::typeBinary | CFile::modeCreate);
	fil_ctrl.Seek(0,CFile::begin);
	// salvataggio sul nuovo file
	fil_ctrl.Write("f.m.tt",6);
	for(i=0;i<63;i++)
	{
		fil_ctrl.Write(&squad_nazall[i],sizeof(squadra));
		for(j = 0;j<23;j++)
			fil_ctrl.Write(&gioc[462+j+(i*23)],sizeof(giocatore));
	} 
	for(i=0;i<32;i++)
	{
		fil_ctrl.Write(&squad_ml[i],sizeof(squadra_ml));
		for(j = 0;j<23;j++)
			fil_ctrl.Write(&gioc[trovaIDml(&squad_ml[i].link[j*2])],sizeof(giocatore));
	} 
	fil_ctrl.Write(&squad_defml,sizeof(squadra_ml));
	for(j=0;j<23;j++)
		fil_ctrl.Write(&gioc[trovaIDml(&squad_defml.link[j*2])],sizeof(giocatore));
	fil_ctrl.Write(&link_euroas,46);
	fil_ctrl.Write(&link_worldas,46);
	for(j=0;j<16;j++)
		fil_ctrl.Write(&tattpred[j],sizeof(tattica));
	fil_ctrl.Close();
	AfxMessageBox("Operation done !");

}

void CEdDlg::nomiallstar()
{
	// assegna nomi all-star in base ai link
	for(int i=0;i<23;i++)
	{
		//euro
		strcpy(gioc[462+(54*23)+i].nome,gioc[trovaIDml(&link_euroas[i*2])].nome);
		//world
		strcpy(gioc[462+(55*23)+i].nome,gioc[trovaIDml(&link_worldas[i*2])].nome);
	}

}

void CEdDlg::OnTattPredef() 
{
	dlg_tatt.ttt = tattpred;
	dlg_tatt.DoModal();
	aggiornaNtatt();
}

void CEdDlg::aggiornaNtatt()
{
	cmd_nometat1.SetWindowText(tattpred[0].nome);
	cmd_nometat2.SetWindowText(tattpred[1].nome);
	cmd_nometat3.SetWindowText(tattpred[2].nome);
	cmd_nometat4.SetWindowText(tattpred[3].nome);
	cmd_nometat5.SetWindowText(tattpred[4].nome);
	cmd_nometat6.SetWindowText(tattpred[5].nome);
	cmd_nometat7.SetWindowText(tattpred[6].nome);
	cmd_nometat8.SetWindowText(tattpred[7].nome);
	cmd_nometat9.SetWindowText(tattpred[8].nome);
	cmd_nometat10.SetWindowText(tattpred[9].nome);
	cmd_nometat11.SetWindowText(tattpred[10].nome);
	cmd_nometat12.SetWindowText(tattpred[11].nome);
	cmd_nometat13.SetWindowText(tattpred[12].nome);
	cmd_nometat14.SetWindowText(tattpred[13].nome);
	cmd_nometat15.SetWindowText(tattpred[14].nome);
	cmd_nometat16.SetWindowText(tattpred[15].nome);
}
