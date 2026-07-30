// squadra.h: interface for the squadra class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SQUADRA_H__31D17526_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
#define AFX_SQUADRA_H__31D17526_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "giocatore.h"


struct NUMERI
{
	DWORD order_1:5;
	DWORD order_2:5;
	DWORD order_3:5;
	DWORD order_4:5;
	DWORD order_5:5;
	DWORD order_6:5;
	DWORD pad1:2;

	DWORD order_7:5;
	DWORD order_8:5;
	DWORD order_9:5;
	DWORD order_10:5;
	DWORD order_11:5;
	DWORD order_12:5;
	DWORD pad2:2;

	DWORD order_13:5;
	DWORD order_14:5;
	DWORD order_15:5;
	DWORD order_16:5;
	DWORD order_17:5;
	DWORD order_18:5;
	DWORD pad3:2;

	DWORD order_19:5;
	DWORD order_20:5;
	DWORD order_21:5;
	DWORD order_22:5;
	DWORD order_23:5;
	DWORD pad4:7;
} ;

class squadra  
{
public:
	char nomi[6][20];
	char nome_m[20];
	char nomi_a[3][4];
	char nomek[20];
	char nomekanji[40];

	char bar_attacco,
		 bar_difesa,
		 bar_potenza,
		 bar_velocita,
		 bar_tecnica;

	char kik_punl,
		 kik_punc,
		 kik_angsx,
		 kik_angdx,
		 kik_rigori,
		 kik_cap;

	char str_tattica[30],
		 tat_ruolo[10],
		 tat_x[10],
		 tat_y[10];
	
	char stile_bandiera;
	unsigned short col_bandiera[16];
	unsigned short maglia1[16];
	unsigned short maglia2[16];

	char str_strategia[4];
	struct NUMERI stc_numeri;

	squadra();
	virtual ~squadra();

};

#endif // !defined(AFX_SQUADRA_H__31D17526_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
