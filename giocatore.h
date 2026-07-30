// giocatore.h: interface for the giocatore class.
//
//////////////////////////////////////////////////////////////////////

#include <string>
#include <map>
#include <list>
using namespace std;

#if !defined(AFX_GIOCATORE_H__31D17522_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
#define AFX_GIOCATORE_H__31D17522_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class fifa_player
{
public:
	int UpdatePlayerFromURL(string link);
	void SetPlayerToDummy();

	string name;
	string positions;
	int number[2]; //index 0 = national team, 1 = club team
	int weight;
	int height;
	int age;
	char foot;
	int weakFootSkill;
	int skillMoves;
	string offWeight;
	string defWeight;
	int* attributeValues;
};

class giocatore  
{
public:
	void decodifica();
	void codifica_carat();
	void editFromFIFA(fifa_player fpl, int editName, int editLook, int editPosSkills);
	
	char url[500];
	char nome[11];
	int posizione;
	int col_pelle;
	int stile_capelli;
	int col_capelli;
	int stile_barba;
	int col_barba;
	int altezza;
	int corporatura;
	int eta;
	int scarpe;
	int piede;
	int attacco;
	int difesa;
	int forza;
	int resistenza;
	int velocita;
	int accel;
	int passaggio;
	int pot_tiro;
	int prec_tiro;
	int salto;
	int testa;
	int tecnica;
	int dribbling;
	int effetto;
	int aggress;
	int riflessi;
	int fuori_ruolo;
	int numero;
	int costo;

	char str_carat[12];
	giocatore();
	virtual ~giocatore();

};

#endif // !defined(AFX_GIOCATORE_H__31D17522_8BF4_11D6_9298_C8285EE6CE1D__INCLUDED_)
