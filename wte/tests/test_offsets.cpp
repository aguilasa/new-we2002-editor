// GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.
//
//   Despejo das constantes, em formato estavel e diffavel. Existe um irmao em
//   wte/tests/test_offsets.pas: os dois emitem exatamente as mesmas linhas, um lendo o
//   C++ original, o outro lendo o Pascal gerado.
//
//   Se as duas saidas divergirem, o gerador leu um literal errado -- e offset
//   errado so aparece quando a gravacao corromper a imagem de 474 MB.
//
//   Rodado por wte/tools/test_gen_tables_pas.py.

#include <cstdio>
#include <cstdint>
#include "we2002/Offsets.hpp"
#include "we2002/Tables.hpp"

using namespace we2002;

int main() {
  std::printf("CONST\tOFS_TEAM_NAME_1\t%lld\n", (long long)OFS_TEAM_NAME_1);
  std::printf("CONST\tOFS_TEAM_NAME_1_END\t%lld\n", (long long)OFS_TEAM_NAME_1_END);
  std::printf("CONST\tOFS_TEAM_NAME_1_A\t%lld\n", (long long)OFS_TEAM_NAME_1_A);
  std::printf("CONST\tOFS_TEAM_NAME_2\t%lld\n", (long long)OFS_TEAM_NAME_2);
  std::printf("CONST\tOFS_TEAM_NAME_3\t%lld\n", (long long)OFS_TEAM_NAME_3);
  std::printf("CONST\tOFS_TEAM_NAME_4\t%lld\n", (long long)OFS_TEAM_NAME_4);
  std::printf("CONST\tOFS_TEAM_NAME_5\t%lld\n", (long long)OFS_TEAM_NAME_5);
  std::printf("CONST\tOFS_TEAM_NAME_5_A\t%lld\n", (long long)OFS_TEAM_NAME_5_A);
  std::printf("CONST\tOFS_TEAM_NAME_6\t%lld\n", (long long)OFS_TEAM_NAME_6);
  std::printf("CONST\tOFS_TEAM_NAME_6_A\t%lld\n", (long long)OFS_TEAM_NAME_6_A);
  std::printf("CONST\tOFS_TEAM_NAME_6_B\t%lld\n", (long long)OFS_TEAM_NAME_6_B);
  std::printf("CONST\tOFS_TEAM_NAME_KANJI\t%lld\n", (long long)OFS_TEAM_NAME_KANJI);
  std::printf("CONST\tOFS_TEAM_NAME_KANJI_A\t%lld\n", (long long)OFS_TEAM_NAME_KANJI_A);
  std::printf("CONST\tOFS_TEAM_MIXED_CASE_NAME\t%lld\n", (long long)OFS_TEAM_MIXED_CASE_NAME);
  std::printf("CONST\tOFS_TEAM_ABBREV_1\t%lld\n", (long long)OFS_TEAM_ABBREV_1);
  std::printf("CONST\tOFS_TEAM_ABBREV_2\t%lld\n", (long long)OFS_TEAM_ABBREV_2);
  std::printf("CONST\tOFS_TEAM_ABBREV_3\t%lld\n", (long long)OFS_TEAM_ABBREV_3);
  std::printf("CONST\tOFS_ML_TEAM_NAME_7\t%lld\n", (long long)OFS_ML_TEAM_NAME_7);
  std::printf("CONST\tOFS_ML_TEAM_NAME_8\t%lld\n", (long long)OFS_ML_TEAM_NAME_8);
  std::printf("CONST\tOFS_ML_TEAM_NAME_8_A\t%lld\n", (long long)OFS_ML_TEAM_NAME_8_A);
  std::printf("CONST\tOFS_TEAM_BARS\t%lld\n", (long long)OFS_TEAM_BARS);
  std::printf("CONST\tOFS_TEAM_BARS_A\t%lld\n", (long long)OFS_TEAM_BARS_A);
  std::printf("CONST\tOFS_KICKER\t%lld\n", (long long)OFS_KICKER);
  std::printf("CONST\tOFS_PLAYER_NAME\t%lld\n", (long long)OFS_PLAYER_NAME);
  std::printf("CONST\tOFS_PLAYER_NAME_2\t%lld\n", (long long)OFS_PLAYER_NAME_2);
  std::printf("CONST\tOFS_PLAYER_NAME_3\t%lld\n", (long long)OFS_PLAYER_NAME_3);
  std::printf("CONST\tOFS_PLAYER_NAME_4\t%lld\n", (long long)OFS_PLAYER_NAME_4);
  std::printf("CONST\tOFS_PLAYER_NAME_5\t%lld\n", (long long)OFS_PLAYER_NAME_5);
  std::printf("CONST\tOFS_PLAYER_NAME_6\t%lld\n", (long long)OFS_PLAYER_NAME_6);
  std::printf("CONST\tOFS_PLAYER_NAME_7\t%lld\n", (long long)OFS_PLAYER_NAME_7);
  std::printf("CONST\tOFS_PLAYER_NAME_8\t%lld\n", (long long)OFS_PLAYER_NAME_8);
  std::printf("CONST\tOFS_ML_PLAYER_NAME\t%lld\n", (long long)OFS_ML_PLAYER_NAME);
  std::printf("CONST\tOFS_ML_PLAYER_NAME_2\t%lld\n", (long long)OFS_ML_PLAYER_NAME_2);
  std::printf("CONST\tOFS_ML_PLAYER_NAME_3\t%lld\n", (long long)OFS_ML_PLAYER_NAME_3);
  std::printf("CONST\tOFS_PLAYER_ATTR\t%lld\n", (long long)OFS_PLAYER_ATTR);
  std::printf("CONST\tOFS_PLAYER_ATTR_1\t%lld\n", (long long)OFS_PLAYER_ATTR_1);
  std::printf("CONST\tOFS_PLAYER_ATTR_2\t%lld\n", (long long)OFS_PLAYER_ATTR_2);
  std::printf("CONST\tOFS_PLAYER_ATTR_3\t%lld\n", (long long)OFS_PLAYER_ATTR_3);
  std::printf("CONST\tOFS_PLAYER_ATTR_4\t%lld\n", (long long)OFS_PLAYER_ATTR_4);
  std::printf("CONST\tOFS_PLAYER_ATTR_5\t%lld\n", (long long)OFS_PLAYER_ATTR_5);
  std::printf("CONST\tOFS_PLAYER_ATTR_6\t%lld\n", (long long)OFS_PLAYER_ATTR_6);
  std::printf("CONST\tOFS_PLAYER_ATTR_7\t%lld\n", (long long)OFS_PLAYER_ATTR_7);
  std::printf("CONST\tOFS_PLAYER_ATTR_8\t%lld\n", (long long)OFS_PLAYER_ATTR_8);
  std::printf("CONST\tOFS_PLAYER_ATTR_9\t%lld\n", (long long)OFS_PLAYER_ATTR_9);
  std::printf("CONST\tOFS_ML_PLAYER_ATTR\t%lld\n", (long long)OFS_ML_PLAYER_ATTR);
  std::printf("CONST\tOFS_ML_PLAYER_ATTR_1\t%lld\n", (long long)OFS_ML_PLAYER_ATTR_1);
  std::printf("CONST\tOFS_ML_PLAYER_ATTR_2\t%lld\n", (long long)OFS_ML_PLAYER_ATTR_2);
  std::printf("CONST\tOFS_FLAG_SHAPE_COPY_1\t%lld\n", (long long)OFS_FLAG_SHAPE_COPY_1);
  std::printf("CONST\tOFS_FLAG_SHAPE_COPY_2\t%lld\n", (long long)OFS_FLAG_SHAPE_COPY_2);
  std::printf("CONST\tOFS_FLAG_SHAPE_COPY_3\t%lld\n", (long long)OFS_FLAG_SHAPE_COPY_3);
  std::printf("CONST\tOFS_FLAG_SHAPE_COPY_4\t%lld\n", (long long)OFS_FLAG_SHAPE_COPY_4);
  std::printf("CONST\tOFS_FLAG_SHAPE_COPY_5\t%lld\n", (long long)OFS_FLAG_SHAPE_COPY_5);
  std::printf("CONST\tOFS_FLAG_COLOURS\t%lld\n", (long long)OFS_FLAG_COLOURS);
  std::printf("CONST\tOFS_FLAG_COLOURS_A\t%lld\n", (long long)OFS_FLAG_COLOURS_A);
  std::printf("CONST\tOFS_FLAG_COLOURS_B\t%lld\n", (long long)OFS_FLAG_COLOURS_B);
  std::printf("CONST\tOFS_FLAG_COLOURS_SENEGAL\t%lld\n", (long long)OFS_FLAG_COLOURS_SENEGAL);
  std::printf("CONST\tOFS_COST_NATIONAL\t%lld\n", (long long)OFS_COST_NATIONAL);
  std::printf("CONST\tOFS_COST_NC\t%lld\n", (long long)OFS_COST_NC);
  std::printf("CONST\tOFS_SQUAD_NUMBERS_ML\t%lld\n", (long long)OFS_SQUAD_NUMBERS_ML);
  std::printf("CONST\tOFS_SQUAD_NUMBERS_NATIONAL\t%lld\n", (long long)OFS_SQUAD_NUMBERS_NATIONAL);
  std::printf("CONST\tOFS_FORMATIONS\t%lld\n", (long long)OFS_FORMATIONS);
  std::printf("CONST\tOFS_FORMATIONS_A\t%lld\n", (long long)OFS_FORMATIONS_A);
  std::printf("CONST\tOFS_LINK_ML\t%lld\n", (long long)OFS_LINK_ML);
  std::printf("CONST\tOFS_LINK_ML1\t%lld\n", (long long)OFS_LINK_ML1);
  std::printf("CONST\tOFS_LINK_ML2\t%lld\n", (long long)OFS_LINK_ML2);
  std::printf("CONST\tOFS_KIT_PREVIEW\t%lld\n", (long long)OFS_KIT_PREVIEW);
  std::printf("CONST\tOFS_KIT_PREVIEW_A\t%lld\n", (long long)OFS_KIT_PREVIEW_A);
  std::printf("CONST\tOFS_KIT_PREVIEW_B\t%lld\n", (long long)OFS_KIT_PREVIEW_B);
  std::printf("CONST\tOFS_KIT_PREVIEW_C\t%lld\n", (long long)OFS_KIT_PREVIEW_C);
  std::printf("CONST\tSECTOR_SIZE\t%lld\n", (long long)SECTOR_SIZE);
  std::printf("CONST\tSECTOR_DATA_BEGIN\t%lld\n", (long long)SECTOR_DATA_BEGIN);
  std::printf("CONST\tSECTOR_DATA_END\t%lld\n", (long long)SECTOR_DATA_END);
  std::printf("CONST\tN_ROLES\t%lld\n", (long long)N_ROLES);
  std::printf("CONST\tSTART_LINK_COUNT\t%lld\n", (long long)START_LINK_COUNT);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_1\t%d\t%d\n", i, (int)TEAM_NAME_LEN_1[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_2\t%d\t%d\n", i, (int)TEAM_NAME_LEN_2[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_3\t%d\t%d\n", i, (int)TEAM_NAME_LEN_3[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_4\t%d\t%d\n", i, (int)TEAM_NAME_LEN_4[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_5\t%d\t%d\n", i, (int)TEAM_NAME_LEN_5[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_LEN_6\t%d\t%d\n", i, (int)TEAM_NAME_LEN_6[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_MIXED_CASE_NAME_LEN\t%d\t%d\n", i, (int)TEAM_MIXED_CASE_NAME_LEN[i]);
  for (int i = 0; i < 32; ++i)
    std::printf("NUM\tML_TEAM_NAME_LEN_7\t%d\t%d\n", i, (int)ML_TEAM_NAME_LEN_7[i]);
  for (int i = 0; i < 32; ++i)
    std::printf("NUM\tML_TEAM_NAME_LEN_8\t%d\t%d\n", i, (int)ML_TEAM_NAME_LEN_8[i]);
  for (int i = 0; i < 95; ++i)
    std::printf("NUM\tTEAM_NAME_KANJI_LEN\t%d\t%d\n", i, (int)TEAM_NAME_KANJI_LEN[i]);
  for (int i = 0; i < 21; ++i) {
    std::printf("TXT\tROLE_NAMES\t%d\t", i);
    for (int j = 0; j < 6; ++j)
      std::printf("%02X", (unsigned char)ROLE_NAMES[i][j]);
    std::printf("\n");
  }
  for (int i = 0; i < 120; ++i)
    std::printf("NUM\tSTART_LINK\t%d\t%d\n", i, (int)START_LINK[i]);
  for (int i = 0; i < 52; ++i)
    std::printf("NUM\tNC_TEAM_CODE\t%d\t%d\n", i, (int)NC_TEAM_CODE[i]);
  for (int i = 0; i < 52; ++i)
    std::printf("NUM\tNC_PLAYER_COUNT\t%d\t%d\n", i, (int)NC_PLAYER_COUNT[i]);
  for (int i = 0; i < 120; ++i) {
    std::printf("TXT\tTEAM_NAMES\t%d\t", i);
    for (int j = 0; j < 20; ++j)
      std::printf("%02X", (unsigned char)TEAM_NAMES[i][j]);
    std::printf("\n");
  }
  for (int i = 0; i < 120; ++i) {
    std::printf("TXT\tPICKER_TEAM_NAMES\t%d\t", i);
    for (int j = 0; j < 20; ++j)
      std::printf("%02X", (unsigned char)PICKER_TEAM_NAMES[i][j]);
    std::printf("\n");
  }
  return 0;
}
