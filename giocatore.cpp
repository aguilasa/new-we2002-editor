// giocatore.cpp: implementation of the giocatore class.
//
//////////////////////////////////////////////////////////////////////

#include "stdafx.h"
#include "ed.h"
#include "giocatore.h"
#include "myiotxt.h"
#include "edDlg.h"
#include <fstream>

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[]=__FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

giocatore::giocatore()
{

}

giocatore::~giocatore()
{

}

void giocatore::codifica_carat()
{
// codifica dalla stringa alle varibili membro
	posizione = str_carat[0]&0x07;
	col_pelle = str_carat[4]&0x03;
	stile_capelli = ((str_carat[0]>>4)&0x0f) + ((str_carat[1]<<4)&0x10);
	col_capelli = (str_carat[1]>>1)&0x07;
	stile_barba = (str_carat[1]>>5)&0x07;
	col_barba = (str_carat[2]>>1)&0x07;
	altezza = 148 + ((str_carat[2]>>4)&0x0f) + ((str_carat[3]<<4)&0x30);
	corporatura = (str_carat[4]>>2)&0x07;
	eta = 15 + ((str_carat[4]>>5)&0x07) + ((str_carat[5]<<3)&0x18);
	scarpe = (str_carat[11]>>3)&0x07;
	piede = (str_carat[11]>>6)&0x03;
	attacco = 12 + ((str_carat[7]>>5)&0x07);
	difesa = 12 + (str_carat[8]&0x07);
	forza = 12 + ((str_carat[5]>>6)&0x03) + ((str_carat[6]<<2)&0x04);
	resistenza = 12 + ((str_carat[6]>>1)&0x07);
	velocita = 12 + ((str_carat[6]>>7)&0x01) + ((str_carat[7]<<1)&0x06);
	accel = 12 + ((str_carat[7]>>2)&0x07);
	passaggio = 12 + ((str_carat[9]>>1)&0x07);
	pot_tiro = 12 + ((str_carat[8]>>3)&0x07);
	prec_tiro = 12 + ((str_carat[8]>>6)&0x03) + ((str_carat[9]<<2)&0x04);
	salto = 12 + ((str_carat[10]>>2)&0x07);
	testa = 12 + ((str_carat[9]>>7)&0x01) + ((str_carat[10]<<1)&0x06);
	tecnica = 12 + ((str_carat[9]>>4)&0x07);
	dribbling = 12 + ((str_carat[6]>>4)&0x07);
	effetto = 12 + ((str_carat[10]>>5)&0x07);
	aggress = 12 + (str_carat[11]&0x07);
	riflessi = 12 + ((str_carat[5]>>2)&0x07);
	fuori_ruolo = (str_carat[3]>>7)&0x01;
	numero = 1 + ((str_carat[3]>>2)&0x1f);
}

void giocatore::decodifica()
{
// decodifica dalle varibili membro alla stringa
	str_carat[3] &= 0x01;
	str_carat[3] |= (numero-1)<<2;

	str_carat[3] &= 0x7f;
	str_carat[3] |= fuori_ruolo<<7;
	str_carat[0] &= 0xf8;
	str_carat[0] |= posizione;
	str_carat[4] &= 0xfc;
	str_carat[4] |= col_pelle;
	str_carat[0] &= 0x0f;
	str_carat[0] |= stile_capelli<<4;
	str_carat[1] &= 0xfe;
	str_carat[1] |= stile_capelli>>4;
	str_carat[1] &= 0xf1;
	str_carat[1] |= col_capelli<<1;
	str_carat[1] &= 0x1f;
	str_carat[1] |= stile_barba<<5;
	str_carat[2] &= 0xf1;
	str_carat[2] |= col_barba<<1;
	str_carat[2] &= 0x0f;
	str_carat[2] |= (altezza-148)<<4;
	str_carat[3] &= 0xfc;
	str_carat[3] |= (altezza-148)>>4;
	str_carat[4] &= 0xe3;
	str_carat[4] |= corporatura<<2;
	str_carat[4] &= 0x1f;
	str_carat[4] |= (eta-15)<<5;
	str_carat[5] &= 0xfc;
	str_carat[5] |= (eta-15)>>3;		
	str_carat[11] &= 0xc7;
	str_carat[11] |= scarpe<<3;
	str_carat[11] &= 0x3f;
	str_carat[11] |= piede<<6;
	str_carat[7] &= 0x1f;
	str_carat[7] |= (attacco-12)<<5;
	str_carat[8] &= 0xf8;
	str_carat[8] |= difesa-12;	
	str_carat[5] &= 0x3f;
	str_carat[5] |= (forza-12)<<6;
	str_carat[6] &= 0xfe;
	str_carat[6] |= (forza-12)>>2;
	str_carat[6] &= 0xf1;
	str_carat[6] |= (resistenza-12)<<1;
	str_carat[6] &= 0x7f;
	str_carat[6] |= (velocita-12)<<7;
	str_carat[7] &= 0xfc;
	str_carat[7] |= (velocita-12)>>1;
	str_carat[7] &= 0xe3;
	str_carat[7] |= (accel-12)<<2;
	str_carat[9] &= 0xf1;
	str_carat[9] |= (passaggio-12)<<1;
	str_carat[8] &= 0xc7;
	str_carat[8] |= (pot_tiro-12)<<3;
	str_carat[8] &= 0x3f;
	str_carat[8] |= (prec_tiro-12)<<6;
	str_carat[9] &= 0xfe;
	str_carat[9] |= (prec_tiro-12)>>2;
	str_carat[10] &= 0xe3;
	str_carat[10] |= (salto-12)<<2;	
	str_carat[9] &= 0x7f;
	str_carat[9] |= (testa-12)<<7;
	str_carat[10] &= 0xfc;
	str_carat[10] |= (testa-12)>>1;
	str_carat[9] &= 0x8f;
	str_carat[9] |= (tecnica-12)<<4;
	str_carat[6] &= 0x8f;
	str_carat[6] |= (dribbling-12)<<4;
	str_carat[10] &= 0x1f;
	str_carat[10] |= (effetto-12)<<5;
	str_carat[11] &= 0xf8;
	str_carat[11] |= aggress-12;
	str_carat[5] &= 0xe3;
	str_carat[5] |= (riflessi-12)<<2;
}

void fifa_player::SetPlayerToDummy()
{

	extern map<string,int> fifaVerNumFields;

	string sTemp;

	name = "Dummy";
	positions = "CB";
	number[1] = 50; //number for national team should not be needed because dummy players only exist in clubs
	weight = 70;
	height = 170;
	age = 16;
	foot = 'R';
	weakFootSkill = 1;
	skillMoves = 1;
	offWeight = "Medium";
	defWeight = "Medium";

	int nf = fifaVerNumFields["15w"]; //force one version
	delete [] attributeValues;
	attributeValues = new int[nf];
	int i;
	for(i = 0;i < nf; i++)
	{
		attributeValues[i] = 1;
	}
}

int fifa_player::UpdatePlayerFromURL(string link)
{
	extern map<string,vector<string>> fifaVerGroupsMap;
	extern map<string,map<string,vector<string>>> fifaVerGroupFieldMap;
	extern map<string,int> fifaVerNumFields;
	extern map<string,map<string,map<string,int>>> fifaVerGroupFieldIndexMap;

	if(link.find("http://sofifa.com/")==string::npos){return 0;}

	int i, r, j;
	string line, sTemp, sTemp2;
	vector<string> arrTemp, arrTemp2;

	string fifaVer = "15"; //hardcoded
	if(fifaVerNumFields.count(fifaVer) == 0){return 0;}

	int nf = fifaVerNumFields[fifaVer];
	delete [] attributeValues;
	attributeValues = new int[nf];
	
	string html = getURLcontent(link);
	vector<string> arr = split(html,'\n');

	if(FALSE) //for debug write result on txt
	{
		//
		ofstream myfile;
		myfile.open("debugio.txt", ios::trunc);
		for(i=0;i<arr.size();i++)
		{
			myfile << arr[i];
		}
		myfile.close();
	}

	bool readFinished = (arr.size() == 0);
	if(readFinished){return 0;}
	r=0;

	//import base data
	//(name, height, etc.)
	//which are stored in non-standard positions

	//NAME
	sTemp = "<li class=\"active\"><a href=\"javascript:void(0);\">";
	do
	{r++;line = arr[r];}
	while(line.find(sTemp)==string::npos);
	i = arr[r].find(sTemp) + sTemp.size();
	j = arr[r].size() - 9 - 1; //9 = "</a></li>".size()
	name = remove_spaces(arr[r].substr(i, j-i));

	do
	{r++;line = arr[r];}
	while(line.find("<span class=")==string::npos);

	arrTemp = splitOutsideDelimitingChars(arr[r],'<','>');
	sTemp = remove_spaces(arrTemp[arrTemp.size()-2]);
	arrTemp2 = split(sTemp, ' ');

	//AGE
	i=-1;
	do
	{i++;line = arrTemp2[i];}
	while(line.find("Age")==string::npos);
	age = stoi(arrTemp2[i+1]);

	//HEIGHT
	do
	{i++;line = arrTemp2[i];}
	while(line.find("cm")==string::npos);
	sTemp=line.substr(0,line.find("cm"));
	height = stoi(sTemp);

	//WEIGHT
	do
	{i++;line = arrTemp2[i];}
	while(line.find("kg")==string::npos);
	sTemp=line.substr(0,line.find("kg"));
	weight = stoi(sTemp);

	//POSITIONS
	arrTemp2 = split(arr[r],'>');
	sTemp = "";
	for(i = 0;i < arrTemp2.size(); i++)
	{
		if (arrTemp2[i].find("<span class=\"pos ")!=string::npos)
		{
			sTemp.append(",").append(arrTemp[i+1]);
		}
	}
	sTemp.erase (sTemp.begin());
	positions = sTemp;

	//FOOT
	do
	{r++;line = arr[r];}
	while(line.find("Preferred Foot")==string::npos);
	foot = 'R'; //default
	if(arr[r].find("Left")!=string::npos) foot = 'L';

	//WEAK FOOT
	do
	{r++;line = arr[r];}
	while(line.find("Weak Foot")==string::npos);
	r++;
	sTemp = arr[r];
	sTemp = sTemp.substr(sTemp.find("title=")+7,1);
	weakFootSkill=stoi(sTemp);

	//SKILL MOVES
	do
	{r++;line = arr[r];}
	while(line.find("Skill Moves")==string::npos);
	r++;
	sTemp = arr[r];
	sTemp = sTemp.substr(sTemp.find("title=")+7,1);
	skillMoves=stoi(sTemp);

	//OFFENSIVE/DEFENSIVE WEIGHT
	do
	{r++;line = arr[r];}
	while(line.find("Work Rate")==string::npos);
	arrTemp = splitOutsideDelimitingChars(arr[r],'<','>');
	arrTemp2 = split(arrTemp[1],'/');
	arrTemp2[0] = remove_spaces(arrTemp2[0]);
	arrTemp2[1] = remove_spaces(arrTemp2[1]);
	offWeight = arrTemp2[0];
	defWeight = arrTemp2[1];

	//SHIRT NUMBER
	number[0]=-1;
	number[1]=-1;
	
	if(line.find("<div id=\"chartdiv\"></div>")==string::npos)
	{
		do
		{r++;line = arr[r];}
		while(line.find("Player Number")==string::npos && line.find("<div id=\"chartdiv\"></div>")==string::npos);
		if(line.find("Player Number")!=string::npos)
		{
			r=r-8;
			line = arr[r];
			if(line.find("Free Agents")==string::npos)
			{
				//read the number
				r=r+7;
				arrTemp = splitOutsideDelimitingChars(arr[r],'<','>');
				j = stoi(arrTemp[1]);
				
				//read if it is the number of the national or club team
				r=r+7;
				line = arr[r];
				if(line.find("Contract Valid Until")==string::npos) {number[0] = j;} else {number[1] = j;};
				r=r-6;
			}
		}
	}

	if(line.find("<div id=\"chartdiv\"></div>")==string::npos)
	{
		do
		{r++;line = arr[r];}
		while(line.find("Player Number")==string::npos && line.find("<div id=\"chartdiv\"></div>")==string::npos);
		if(line.find("Player Number")!=string::npos)
		{
			r=r-8;
			line = arr[r];
			if(line.find("Free Agents")==string::npos)
			{
				//read the number
				r=r+7;
				arrTemp = splitOutsideDelimitingChars(arr[r],'<','>');
				j = stoi(arrTemp[1]);
				
				//read if it is the number of the national or club team
				r=r+7;
				line = arr[r];
				if(line.find("Contract Valid Until")==string::npos) {number[0] = j;} else {number[1] = j;};
				r=r-6;
			}
		} 
	}

	//import custom fields (ordered)
	do
	{r++;line = arr[r];}
	while(line.find("row attribute")==string::npos);
	string currGroup, currField;
	int h = 0;
	int k;
	int f=0;
	int nGroups=fifaVerGroupsMap[fifaVer].size();
	while(h < nGroups)
	{
		//take the group name
		currGroup = fifaVerGroupsMap[fifaVer][h];
		//reach the group line
		do
		{r++;line = arr[r];}
		while(line.find(currGroup)==string::npos);

		k=0;
		int nGroupSkills=fifaVerGroupFieldMap[fifaVer][currGroup].size();
		while(k < nGroupSkills)
		{
			currField = fifaVerGroupFieldMap[fifaVer][currGroup][k];
			
			//reach the field line
			do
			{r++;line = arr[r];}
			while(line.find(currField)==string::npos);
			
			//take the value
			arrTemp = splitOutsideDelimitingChars(line,'<','>');
			int myFieldValue = stoi(arrTemp[1]);

			attributeValues[fifaVerGroupFieldIndexMap[fifaVer][currGroup][currField]]=myFieldValue;
			f++;

			k++;
		}

		h++;
	}

	return 1;

};

int valid_positions[8];

void giocatore::editFromFIFA(fifa_player fpl, int editName, int editLook, int editPosSkills)
{
	int i;

	if(editName==1) //to edit without overwriting the names
	{
		string sTemp = fpl.name;
		if(sTemp.find('.')!=string::npos)
		{
			i = sTemp.rfind('.');
			sTemp=sTemp.substr(i+2,sTemp.length()-(i+2)); //?
		}
		//sTemp = remove_spaces(sTemp);
		sTemp.copy(nome,10);
		for(i = sTemp.length();i < 11; i++)
		{
			nome[i] = 0;
		}
	}

	if(editPosSkills==1)
	{
		string pos = fpl.positions;
		vector<string> v_pos = split(pos, ',');
		posizione = getWEPositionFromFifaPosition(v_pos[0]);

		for(i=0;i<8;i++){valid_positions[i] = 0;}
		for(i=0;i<v_pos.size();i++){valid_positions[getWEPositionFromFifaPosition(v_pos[i])] = 1;}
		int sum_pos = 0;
		for(i=0;i<8;i++){sum_pos = sum_pos + valid_positions[i];}
		fuori_ruolo = (sum_pos>1) ? 1 : 0;
	}

	if(editLook==1)
	{
		//col_pelle;
		//stile_capelli;
		//col_capelli;
		//stile_barba;
		//col_barba;

		altezza = fpl.height;

		//body heuristic
		int ratio = fpl.weight - (fpl.height - 100);
		if		(ratio<=-11){corporatura = 1;}
		else if	(ratio<=-7)	{corporatura = 2;}
		else if	(ratio<=-3)	{corporatura = 3;}
		else if	(ratio<= 2)	{corporatura = 4;}
		else if	(ratio<= 6)	{corporatura = 5;}
		else if	(ratio<=10)	{corporatura = 6;}
		else if	(ratio<=14)	{corporatura = 7;}
		else				{corporatura = 8;}

		eta = fpl.age;

		//scarpe;
		if(fpl.weakFootSkill == 5) {piede = 2;}
		else piede = (fpl.foot=='L') ? 1 : 0;
	}

	if(editPosSkills)
	{
		attacco		= getValue("Offense", fpl);
		difesa		= getValue("Defense", fpl);
		forza		= getValue("Body Balance", fpl);
		resistenza	= getValue("Stamina", fpl);
		velocita	= getValue("Speed", fpl);
		accel		= getValue("Acceleration", fpl);
		passaggio	= getValue("Pass", fpl);
		pot_tiro	= getValue("Shoot Power", fpl);
		prec_tiro	= getValue("Shoot Accuracy", fpl);
		salto		= getValue("Jump", fpl);
		testa		= getValue("Head accuracy", fpl);
		tecnica		= getValue("Tecnique", fpl);
		dribbling	= getValue("Dribble", fpl);
		effetto		= getValue("Curve", fpl);
		aggress		= getValue("Aggressive", fpl);
		riflessi	= getValue("Response", fpl);

		costo = CalcolaCostoGiocatore(i);
	}
	
}