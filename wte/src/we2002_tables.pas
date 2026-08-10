{ GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.
  Fonte de verdade: src/core/include/we2002/Tables.hpp, src/core/Tables.cpp

  Regenerar:  python3 wte/tools/gen_tables_pas.py
  Conferir:   python3 wte/tools/gen_tables_pas.py --check
              (ou `make -C wte check`, que roda todos os geradores) }

unit we2002_tables;

{$mode objfpc}{$H+}
{$J-}  { constante com tipo e SO leitura -- em C++ elas sao `const` }

interface


const
  N_ROLES = 21;
  { Length of START_LINK. ResolveMlLink() indexes it with a byte straight off }
  { the disc, which on a file that is not a WE2002 image can be anything up to }
  { 255, so it needs to know where the table ends. }
  START_LINK_COUNT = 120;

  { Per-team byte length of each of the six all-caps name slots, in }
  { disc order (national teams, then all-stars, then Master League }
  { clubs). The trailing NUL separator is counted, which is why the }
  { reads use these verbatim rather than strlen(). }
  TEAM_NAME_LEN_1: array[0..94] of ShortInt = (
    8,12,8,8,12,8,8,8,12,12,8,8,8,8,8,8,8,8,12,8,8,12,8,12,8,12,8,8,8,8,
    8,8,8,8,12,16,8,12,8,12,12,8,8,8,12,8,12,8,8,8,8,8,16,12,
    16,16,16,16,20,16,16,16,20,
    8,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
    16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
  );

  TEAM_NAME_LEN_2: array[0..94] of ShortInt = (
    8,12,8,12,12,8,8,8,8,8,8,8,8,8,8,12,12,12,8,8,8,8,8,12,8,12,8,
    8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,8,4,12,8,12,8,8,8,8,8,12,12,
    16,16,16,12,16,12,12,16,16,
    8,8,8,12,8,8,16,8,8,12,12,12,12,12,8,12,
    12,8,8,8,12,8,8,8,12,12,8,8,12,16,8,12
  );

  TEAM_NAME_LEN_3: array[0..94] of ShortInt = (
    8,12,8,8,12,8,8,8,12,12,8,8,8,8,8,8,8,8,12,8,8,12,8,12,8,12,
    8,8,8,8,8,8,8,8,12,16,8,12,8,12,12,8,8,8,12,8,12,8,8,8,8,8,16,12,
    16,16,16,16,20,16,16,16,20,
    8,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
    16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
  );

  TEAM_NAME_LEN_4: array[0..94] of ShortInt = (
    8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,
    8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,4,4,4,8,8,8,8,8,16,12,12,
    12,12,12,16,8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,8,12,8,4,8,8,8,8,
    8,8,12,8,4,8,12,8,8
  );

  TEAM_NAME_LEN_5: array[0..94] of ShortInt = (
    8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,4,
    8,4,8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,12,8,
    12,16,12,12,12,12,12,12,12,
    8,8,8,8,8,8,12,8,8,8,8,12,12,8,8,8,
    12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
  );

  TEAM_NAME_LEN_6: array[0..94] of ShortInt = (
    8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,
    4,8,4,8,8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,
    12,8,12,16,16,12,12,12,12,16,16,8,8,8,8,8,8,12,8,8,8,8,12,12,8,8,
    8,12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
  );

  { Byte length of the mixed-case team name. }
  TEAM_MIXED_CASE_NAME_LEN: array[0..94] of ShortInt = (
    8,12,8,12,8,8,8,8,8,4,8,4,8,8,8,8,8,8,8,8,8,8,8,12,8,8,8,4,8,4,8,
    8,8,8,8,8,8,8,8,8,8,8,8,4,8,8,8,8,8,8,8,4,12,8,12,16,
    16,12,12,12,12,16,16,8,8,8,8,8,8,12,8,8,8,8,12,12,8,
    8,8,12,8,4,8,12,8,8,8,8,12,8,4,12,12,8,8
  );

  { Byte length of the 7th and 8th name slots, Master League only. }
  ML_TEAM_NAME_LEN_7: array[0..31] of ShortInt = (
    8,8,8,8,8,8,8,12,8,8,8,8,8,8,8,8,
    12,8,4,8,8,8,8,8,8,12,8,4,8,12,8,9
  );

  ML_TEAM_NAME_LEN_8: array[0..31] of ShortInt = (
    7,8,8,12,12,12,12,12,8,12,12,12,12,12,8,12,
    16,8,8,12,12,8,8,8,8,12,8,8,16,16,8,12
  );

  { Length in characters of the Japanese team name; the }
  { encoded form on disc is twice this many bytes. }
  TEAM_NAME_KANJI_LEN: array[0..94] of ShortInt = (
    8,8,6,8,6,6,6,6,6,6,6,6,6,6,6,8,8,6,6,8,6,6,6,8,6,6,6,6,6,6,
    6,6,6,8,6,6,6,6,6,6,6,6,6,6,6,6,8,6,6,6,6,6,8,8,
    12,12,14,12,12,12,10,12,14,
    6,6,6,8,8,6,10,8,6,8,8,8,8,8,6,8,
    10,6,6,6,8,6,6,6,8,10,6,6,8,10,6,6
  );

  { The 21 role abbreviations shown on the tactics screen. }
  ROLE_NAMES: array[0..20] of array[0..5] of AnsiChar = (
    'GK','CB SX','CB CN','SW','LIB','CB DX','LB','RB',
    'DH SX','DH CN','DH DX','LH','RH','OH SX','OH CN','OH DX',
    'CF SX','CF CN','CF DX','LW','RW'
  );

  { First squad index of each national team inside the shared player }
  { pool. ResolveMlLink() uses it to turn a two-byte link into an }
  { index into Database::players. }
  START_LINK: array[0..119] of LongInt = (
    0,  { irlanda }
    5,  { scozia }
    9,  { galles }
    10,  { inghilterra }
    51,  { portogallo }
    58,  { spagna }
    100,  { francia }
    168,  { belgio }
    173,  { olanda }
    210,  { svizzera }
    211,  { italia }
    275,  { r.ceca }
    276,  { germania }
    301,  { danimarca }
    304,  { norvegia }
    306,  { svezia }
    311,  { finlandia }
    312,  { polonia }
    0,  { slovacchia }
    313,  { austria }
    0,  { ungheria }
    0,  { slovenia }
    314,  { croazia }
    318,  { jugoslavia }
    321,  { romania }
    0,  { bulgaria }
    325,  { grecia }
    333,  { turchia }
    343,  { ucraina }
    347,  { russia }
    349,  { marocco }
    0,  { tunisia }
    350,  { egitto }
    351,  { nigeria }
    0,  { camerun }
    0,  { sudafrica }
    0,  { senegal }
    352,  { usa }
    0,  { messico }
    0,  { costa rica }
    353,  { colombia }
    354,  { brasile }
    0,  { peru }
    0,  { cile }
    390,  { paraguay }
    391,  { uruguay }
    394,  { argentina }
    0,  { ecuador }
    428,  { giappone }
    0,  { corea }
    0,  { cina }
    0,  { iran }
    0,  { arabia }
    432,  { australia }
    0,  { euro all-star }
    0,  { world all-star }
    0,  { cl. ing }
    0,  { cl. fra }
    0,  { cl. ola }
    0,  { cl. ita }
    0,  { cl. ger }
    0,  { cl. bra }
    0,  { cl. arg }
    -1,
    -1,  { le 32 ml }
    -1,  { che non si possono chiaramente linkare }
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
    434,  { islanda }
    435,  { uzbekistan }
    436,  { georgia }
    438,  { bielorussia }
    440,  { bosnia }
    0,  { macedonia }
    442,  { lussemburgo }
    4,  { n.irlanda }
    0,  { giamaica }
    0,  { uae }
    443,  { algeria }
    444,  { ghana }
    0,  { guinea }
    451,  { costa avorio }
    456,  { congo }
    457,  { togo }
    458,  { burundi }
    0,  { liberia }
    0,  { zambia }
    459,  { sierra leone }
    0,  { canada }
    460,  { trinidad }
    0,  { honduras }
    0,  { libano }
    0  { zelanda }
  );

  { The non-contract player pool is stored as runs, one per team: }
  { NC_TEAM_CODE gives the team and NC_PLAYER_COUNT how many of its }
  { players follow. }
  NC_TEAM_CODE: array[0..51] of LongInt = (
    0,  { irlanda }
    102,  { n.irlanda }
    1,  { scozia }
    2,  { galles }
    3,  { inghilterra }
    4,  { portogallo }
    5,  { spagna }
    6,  { francia }
    7,  { belgio }
    8,  { olanda }
    9,  { svizzera }
    10,  { italia }
    11,  { r.ceca }
    12,  { germania }
    13,  { danimarca }
    14,  { norvegia }
    15,  { svezia }
    16,  { finlandia }
    17,  { polonia }
    19,  { austria }
    22,  { croazia }
    23,  { jugoslavia }
    24,  { romania }
    26,  { grecia }
    27,  { turchia }
    28,  { ucraina }
    29,  { russia }
    30,  { marocco }
    32,  { egitto }
    33,  { nigeria }
    37,  { usa }
    40,  { colombia }
    41,  { brasile }
    44,  { paraguay }
    45,  { uruguay }
    46,  { argentina }
    48,  { giappone }
    53,  { australia }
    95,  { islanda }
    96,  { uzbekistan }
    97,  { georgia }
    98,  { bielorussia }
    99,  { bosnia }
    101,  { lussemburgo }
    105,  { algeria }
    106,  { ghana }
    108,  { costa avorio }
    109,  { congo }
    110,  { togo }
    111,  { burundi }
    114,  { sierra leone }
    116  { trinidad }
  );

  NC_PLAYER_COUNT: array[0..51] of ShortInt = (
    4,  { irlanda }
    1,  { n.irlanda }
    4,  { scozia }
    1,  { galles }
    41,  { inghilterra }
    7,  { portogallo }
    42,  { spagna }
    68,  { francia }
    5,  { belgio }
    37,  { olanda }
    1,  { svizzera }
    64,  { italia }
    1,  { r.ceca }
    25,  { germania }
    3,  { danimarca }
    2,  { norvegia }
    5,  { svezia }
    1,  { finlandia }
    1,  { polonia }
    1,  { austria }
    4,  { croazia }
    3,  { jugoslavia }
    4,  { romania }
    8,  { grecia }
    10,  { turchia }
    4,  { ucraina }
    2,  { russia }
    1,  { marocco }
    1,  { egitto }
    1,  { nigeria }
    1,  { usa }
    1,  { colombia }
    36,  { brasile }
    1,  { paraguay }
    3,  { uruguay }
    34,  { argentina }
    4,  { giappone }
    2,  { australia }
    1,  { islanda }
    1,  { uzbekistan }
    2,  { georgia }
    2,  { bielorussia }
    2,  { bosnia }
    1,  { lussemburgo }
    1,  { algeria }
    7,  { ghana }
    5,  { costa avorio }
    1,  { congo }
    1,  { togo }
    1,  { burundi }
    1,  { sierra leone }
    2  { trinidad }
  );

  { Team names as the editor displays them. }
  TEAM_NAMES: array[0..119] of array[0..19] of AnsiChar = (
    'Ireland',
    'Scotland',
    'Wales',
    'England',
    'Portugal',
    'Spain',
    'France',
    'Belgium',
    'Netherlands',
    'Switzerland',
    'Italy',
    'Czech Rep.',
    'Germany',
    'Denmark',
    'Norway',
    'Sweden',
    'Iceland',
    'Poland',
    'Slovakia',
    'Austria',
    'Hungary',
    'Albania',
    'Croatia',
    'Serbia',
    'Romania',
    'Bosnia',
    'Greece',
    'Turkey',
    'Ukraine',
    'Russia',
    'Morocco',
    'Ivory Coast',
    'Egypt',
    'Nigeria',
    'Cameroon',
    'Algeria',
    'Ghana',
    'U.S.A.',
    'Mexico',
    'Venezuela',
    'Colombia',
    'Brazil',
    'Peru',
    'Chile',
    'Paraguay',
    'Uruguay',
    'Argentina',
    'Ecuador',
    'Japan',
    'South Korea',
    'China',
    'India',
    'New Zealand',
    'Australia',  { 54 }
    'Euro All Stars',
    'World All Stars',
    'Clas. England',
    'Clas. France',
    'Clas. Netherlands',
    'Clas. Italy',
    'Clas. Germany',
    'Clas. Brazil',
    'Clas. Argentina',
    'Manchester U.',  { 64 }
    'Arsenal',
    'Chelsea',
    'Liverpool',
    'Manchester City',
    'Tottenham',
    'Atletico Madrid',
    'Barcelona',
    'Real Madrid',
    'Valencia',
    'Sevilla',
    'Monaco',
    'Porto',
    'P.S.G.',
    'Benfica',
    'Ajax',
    'CSKA Moskva',
    'Zenit',
    'Inter',
    'Juventus',
    'Milan',
    'Lazio',
    'Napoli',
    'Fiorentina',
    'Roma',
    'B. Dortmund',
    'B. Munchen',
    'B. Leverkusen',
    'Wolfsburg',
    'Galatasaray',
    'Shakhtar Donetsk',
    'Basilea',
    'Island',  { 95 }
    'Uzbekistan',
    'Georgia',
    'Bielorus',
    'Bosnia H.',
    'Macedonia',
    'Luxemburg',
    'N.Irland',
    'Jamaica',
    'UAE',
    'Algeria',
    'Ghana',
    'Guinea',
    'Ivory Cost',
    'Congo',
    'Togo',
    'Burundi',
    'Liberia',
    'Zambia',
    'Sierra Leone',
    'Canada',
    'Trinidad-Tobago',
    'Honduras',
    'Libano',
    'New Zeland'
  );

  { The same 120 teams as the player-picker dialog spells them. }
  { Six entries differ from TEAM_NAMES -- "Irland" for "Ireland", }
  { "Manchester Utd" for "Manchester U.", and four club names }
  { spaced differently. The original kept two tables; so do we, }
  { because both spellings are what the shipped editor shows. }
  PICKER_TEAM_NAMES: array[0..119] of array[0..19] of AnsiChar = (
    'Irland',
    'Scotland',
    'Wales',
    'England',
    'Portugal',
    'Spain',
    'France',
    'Belgium',
    'Netherlands',
    'Switzerland',
    'Italy',
    'Czech Rep.',
    'Germany',
    'Denmark',
    'Norway',
    'Sweden',
    'Iceland',
    'Poland',
    'Slovakia',
    'Austria',
    'Hungary',
    'Albania',
    'Croatia',
    'Serbia',
    'Romania',
    'Bosnia',
    'Greece',
    'Turkey',
    'Ukraine',
    'Russia',
    'Morocco',
    'Ivory Coast',
    'Egypt',
    'Nigeria',
    'Cameroon',
    'Algeria',
    'Ghana',
    'U.S.A.',
    'Mexico',
    'Venezuela',
    'Colombia',
    'Brazil',
    'Peru',
    'Chile',
    'Paraguay',
    'Uruguay',
    'Argentina',
    'Ecuador',
    'Japan',
    'South Korea',
    'China',
    'India',
    'New Zealand',
    'Australia',  { 54 }
    'Euro All Stars',
    'World All Stars',
    'Clas. England',
    'Clas. France',
    'Clas. Netherlands',
    'Clas. Italy',
    'Clas. Germany',
    'Clas. Brazil',
    'Clas. Argentina',
    'Manchester Utd',  { 64 }
    'Arsenal',
    'Chelsea',
    'Liverpool',
    'Manchester City',
    'Tottenham',
    'Atletico Madrid',
    'Barcelona',
    'Real Madrid',
    'Valencia',
    'Sevilla',
    'Monaco',
    'Porto',
    'P.S.G.',
    'Benfica',
    'Ajax',
    'CSKA Moscow',
    'Zenit',
    'Inter',
    'Juventus',
    'Milan',
    'Lazio',
    'Napoli',
    'Fiorentina',
    'Roma',
    'B.Dortmund',
    'B.Munchen',
    'B.Leverkusen',
    'Wolfsburg',
    'Galatasaray',
    'Shakhtar Donetsk',
    'Basilea',
    'Island',  { 95 }
    'Uzbekistan',
    'Georgia',
    'Bielorus',
    'Bosnia H.',
    'Macedonia',
    'Luxemburg',
    'N.Irland',
    'Jamaica',
    'UAE',
    'Algeria',
    'Ghana',
    'Guinea',
    'Ivory Cost',
    'Congo',
    'Togo',
    'Burundi',
    'Liberia',
    'Zambia',
    'Sierra Leone',
    'Canada',
    'Trinidad-Tobago',
    'Honduras',
    'Libano',
    'New Zeland'
  );

implementation

end.
