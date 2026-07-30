// squadra_ml.h: interface for the squadra_ml class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(AFX_SQUADRA_ML_H__31D17527_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
#define AFX_SQUADRA_ML_H__31D17527_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class squadra_ml  
{
public:
	char nomi[8][20];
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

	char str_numeri[23];
	unsigned char link[46];
	char str_strategia[4];

	squadra_ml();
	virtual ~squadra_ml();

};

#endif // !defined(AFX_SQUADRA_ML_H__31D17527_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
