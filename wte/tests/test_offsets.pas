{ GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.

  Despejo das constantes, em formato estavel e diffavel. Existe um irmao em
  wte/tests/test_offsets.cpp: os dois emitem exatamente as mesmas linhas, um lendo o
  Pascal gerado, o outro lendo o C++ original.

  Se as duas saidas divergirem, o gerador leu um literal errado -- e offset
  errado so aparece quando a gravacao corromper a imagem de 474 MB.

  Rodado por wte/tools/test_gen_tables_pas.py.
}

program test_offsets;

{$mode objfpc}{$H+}

uses we2002_offsets, we2002_tables;

var
  i: LongInt;
  hex: string;
  j: LongInt;

begin
  WriteLn('CONST'#9'OFS_TEAM_NAME_1'#9, Int64(OFS_TEAM_NAME_1));
  WriteLn('CONST'#9'OFS_TEAM_NAME_1_END'#9, Int64(OFS_TEAM_NAME_1_END));
  WriteLn('CONST'#9'OFS_TEAM_NAME_1_A'#9, Int64(OFS_TEAM_NAME_1_A));
  WriteLn('CONST'#9'OFS_TEAM_NAME_2'#9, Int64(OFS_TEAM_NAME_2));
  WriteLn('CONST'#9'OFS_TEAM_NAME_3'#9, Int64(OFS_TEAM_NAME_3));
  WriteLn('CONST'#9'OFS_TEAM_NAME_4'#9, Int64(OFS_TEAM_NAME_4));
  WriteLn('CONST'#9'OFS_TEAM_NAME_5'#9, Int64(OFS_TEAM_NAME_5));
  WriteLn('CONST'#9'OFS_TEAM_NAME_5_A'#9, Int64(OFS_TEAM_NAME_5_A));
  WriteLn('CONST'#9'OFS_TEAM_NAME_6'#9, Int64(OFS_TEAM_NAME_6));
  WriteLn('CONST'#9'OFS_TEAM_NAME_6_A'#9, Int64(OFS_TEAM_NAME_6_A));
  WriteLn('CONST'#9'OFS_TEAM_NAME_6_B'#9, Int64(OFS_TEAM_NAME_6_B));
  WriteLn('CONST'#9'OFS_TEAM_NAME_KANJI'#9, Int64(OFS_TEAM_NAME_KANJI));
  WriteLn('CONST'#9'OFS_TEAM_NAME_KANJI_A'#9, Int64(OFS_TEAM_NAME_KANJI_A));
  WriteLn('CONST'#9'OFS_TEAM_MIXED_CASE_NAME'#9, Int64(OFS_TEAM_MIXED_CASE_NAME));
  WriteLn('CONST'#9'OFS_TEAM_ABBREV_1'#9, Int64(OFS_TEAM_ABBREV_1));
  WriteLn('CONST'#9'OFS_TEAM_ABBREV_2'#9, Int64(OFS_TEAM_ABBREV_2));
  WriteLn('CONST'#9'OFS_TEAM_ABBREV_3'#9, Int64(OFS_TEAM_ABBREV_3));
  WriteLn('CONST'#9'OFS_ML_TEAM_NAME_7'#9, Int64(OFS_ML_TEAM_NAME_7));
  WriteLn('CONST'#9'OFS_ML_TEAM_NAME_8'#9, Int64(OFS_ML_TEAM_NAME_8));
  WriteLn('CONST'#9'OFS_ML_TEAM_NAME_8_A'#9, Int64(OFS_ML_TEAM_NAME_8_A));
  WriteLn('CONST'#9'OFS_TEAM_BARS'#9, Int64(OFS_TEAM_BARS));
  WriteLn('CONST'#9'OFS_TEAM_BARS_A'#9, Int64(OFS_TEAM_BARS_A));
  WriteLn('CONST'#9'OFS_KICKER'#9, Int64(OFS_KICKER));
  WriteLn('CONST'#9'OFS_PLAYER_NAME'#9, Int64(OFS_PLAYER_NAME));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_2'#9, Int64(OFS_PLAYER_NAME_2));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_3'#9, Int64(OFS_PLAYER_NAME_3));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_4'#9, Int64(OFS_PLAYER_NAME_4));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_5'#9, Int64(OFS_PLAYER_NAME_5));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_6'#9, Int64(OFS_PLAYER_NAME_6));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_7'#9, Int64(OFS_PLAYER_NAME_7));
  WriteLn('CONST'#9'OFS_PLAYER_NAME_8'#9, Int64(OFS_PLAYER_NAME_8));
  WriteLn('CONST'#9'OFS_ML_PLAYER_NAME'#9, Int64(OFS_ML_PLAYER_NAME));
  WriteLn('CONST'#9'OFS_ML_PLAYER_NAME_2'#9, Int64(OFS_ML_PLAYER_NAME_2));
  WriteLn('CONST'#9'OFS_ML_PLAYER_NAME_3'#9, Int64(OFS_ML_PLAYER_NAME_3));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR'#9, Int64(OFS_PLAYER_ATTR));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_1'#9, Int64(OFS_PLAYER_ATTR_1));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_2'#9, Int64(OFS_PLAYER_ATTR_2));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_3'#9, Int64(OFS_PLAYER_ATTR_3));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_4'#9, Int64(OFS_PLAYER_ATTR_4));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_5'#9, Int64(OFS_PLAYER_ATTR_5));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_6'#9, Int64(OFS_PLAYER_ATTR_6));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_7'#9, Int64(OFS_PLAYER_ATTR_7));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_8'#9, Int64(OFS_PLAYER_ATTR_8));
  WriteLn('CONST'#9'OFS_PLAYER_ATTR_9'#9, Int64(OFS_PLAYER_ATTR_9));
  WriteLn('CONST'#9'OFS_ML_PLAYER_ATTR'#9, Int64(OFS_ML_PLAYER_ATTR));
  WriteLn('CONST'#9'OFS_ML_PLAYER_ATTR_1'#9, Int64(OFS_ML_PLAYER_ATTR_1));
  WriteLn('CONST'#9'OFS_ML_PLAYER_ATTR_2'#9, Int64(OFS_ML_PLAYER_ATTR_2));
  WriteLn('CONST'#9'OFS_FLAG_SHAPE_COPY_1'#9, Int64(OFS_FLAG_SHAPE_COPY_1));
  WriteLn('CONST'#9'OFS_FLAG_SHAPE_COPY_2'#9, Int64(OFS_FLAG_SHAPE_COPY_2));
  WriteLn('CONST'#9'OFS_FLAG_SHAPE_COPY_3'#9, Int64(OFS_FLAG_SHAPE_COPY_3));
  WriteLn('CONST'#9'OFS_FLAG_SHAPE_COPY_4'#9, Int64(OFS_FLAG_SHAPE_COPY_4));
  WriteLn('CONST'#9'OFS_FLAG_SHAPE_COPY_5'#9, Int64(OFS_FLAG_SHAPE_COPY_5));
  WriteLn('CONST'#9'OFS_FLAG_COLOURS'#9, Int64(OFS_FLAG_COLOURS));
  WriteLn('CONST'#9'OFS_FLAG_COLOURS_A'#9, Int64(OFS_FLAG_COLOURS_A));
  WriteLn('CONST'#9'OFS_FLAG_COLOURS_B'#9, Int64(OFS_FLAG_COLOURS_B));
  WriteLn('CONST'#9'OFS_FLAG_COLOURS_SENEGAL'#9, Int64(OFS_FLAG_COLOURS_SENEGAL));
  WriteLn('CONST'#9'OFS_COST_NATIONAL'#9, Int64(OFS_COST_NATIONAL));
  WriteLn('CONST'#9'OFS_COST_NC'#9, Int64(OFS_COST_NC));
  WriteLn('CONST'#9'OFS_SQUAD_NUMBERS_ML'#9, Int64(OFS_SQUAD_NUMBERS_ML));
  WriteLn('CONST'#9'OFS_SQUAD_NUMBERS_NATIONAL'#9, Int64(OFS_SQUAD_NUMBERS_NATIONAL));
  WriteLn('CONST'#9'OFS_FORMATIONS'#9, Int64(OFS_FORMATIONS));
  WriteLn('CONST'#9'OFS_FORMATIONS_A'#9, Int64(OFS_FORMATIONS_A));
  WriteLn('CONST'#9'OFS_LINK_ML'#9, Int64(OFS_LINK_ML));
  WriteLn('CONST'#9'OFS_LINK_ML1'#9, Int64(OFS_LINK_ML1));
  WriteLn('CONST'#9'OFS_LINK_ML2'#9, Int64(OFS_LINK_ML2));
  WriteLn('CONST'#9'OFS_KIT_PREVIEW'#9, Int64(OFS_KIT_PREVIEW));
  WriteLn('CONST'#9'OFS_KIT_PREVIEW_A'#9, Int64(OFS_KIT_PREVIEW_A));
  WriteLn('CONST'#9'OFS_KIT_PREVIEW_B'#9, Int64(OFS_KIT_PREVIEW_B));
  WriteLn('CONST'#9'OFS_KIT_PREVIEW_C'#9, Int64(OFS_KIT_PREVIEW_C));
  WriteLn('CONST'#9'SECTOR_SIZE'#9, Int64(SECTOR_SIZE));
  WriteLn('CONST'#9'SECTOR_DATA_BEGIN'#9, Int64(SECTOR_DATA_BEGIN));
  WriteLn('CONST'#9'SECTOR_DATA_END'#9, Int64(SECTOR_DATA_END));
  WriteLn('CONST'#9'N_ROLES'#9, Int64(N_ROLES));
  WriteLn('CONST'#9'START_LINK_COUNT'#9, Int64(START_LINK_COUNT));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_1'#9, i, #9, LongInt(TEAM_NAME_LEN_1[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_2'#9, i, #9, LongInt(TEAM_NAME_LEN_2[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_3'#9, i, #9, LongInt(TEAM_NAME_LEN_3[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_4'#9, i, #9, LongInt(TEAM_NAME_LEN_4[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_5'#9, i, #9, LongInt(TEAM_NAME_LEN_5[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_LEN_6'#9, i, #9, LongInt(TEAM_NAME_LEN_6[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_MIXED_CASE_NAME_LEN'#9, i, #9, LongInt(TEAM_MIXED_CASE_NAME_LEN[i]));
  for i := 0 to 31 do
    WriteLn('NUM'#9'ML_TEAM_NAME_LEN_7'#9, i, #9, LongInt(ML_TEAM_NAME_LEN_7[i]));
  for i := 0 to 31 do
    WriteLn('NUM'#9'ML_TEAM_NAME_LEN_8'#9, i, #9, LongInt(ML_TEAM_NAME_LEN_8[i]));
  for i := 0 to 94 do
    WriteLn('NUM'#9'TEAM_NAME_KANJI_LEN'#9, i, #9, LongInt(TEAM_NAME_KANJI_LEN[i]));
  for i := 0 to 20 do
  begin
    hex := '';
    for j := 0 to 5 do
      hex := hex + HexStr(Ord(ROLE_NAMES[i][j]), 2);
    WriteLn('TXT'#9'ROLE_NAMES'#9, i, #9, hex);
  end;
  for i := 0 to 119 do
    WriteLn('NUM'#9'START_LINK'#9, i, #9, LongInt(START_LINK[i]));
  for i := 0 to 51 do
    WriteLn('NUM'#9'NC_TEAM_CODE'#9, i, #9, LongInt(NC_TEAM_CODE[i]));
  for i := 0 to 51 do
    WriteLn('NUM'#9'NC_PLAYER_COUNT'#9, i, #9, LongInt(NC_PLAYER_COUNT[i]));
  for i := 0 to 119 do
  begin
    hex := '';
    for j := 0 to 19 do
      hex := hex + HexStr(Ord(TEAM_NAMES[i][j]), 2);
    WriteLn('TXT'#9'TEAM_NAMES'#9, i, #9, hex);
  end;
  for i := 0 to 119 do
  begin
    hex := '';
    for j := 0 to 19 do
      hex := hex + HexStr(Ord(PICKER_TEAM_NAMES[i][j]), 2);
    WriteLn('TXT'#9'PICKER_TEAM_NAMES'#9, i, #9, hex);
  end;
end.
