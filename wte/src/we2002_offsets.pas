{ GERADO por wte/tools/gen_tables_pas.py -- NAO editar a mao.
  Fonte de verdade: src/core/include/we2002/Offsets.hpp

  Regenerar:  python3 wte/tools/gen_tables_pas.py
  Conferir:   python3 wte/tools/gen_tables_pas.py --check
              (ou `make -C wte check`, que roda todos os geradores) }

unit we2002_offsets;

{$mode objfpc}{$H+}
{$J-}  { constante com tipo e SO leitura -- em C++ elas sao `const` }

interface

type
  { `using Offset = std::int64_t` do Offsets.hpp. Largura fixa por definicao do
    FPC -- nunca Integer, Cardinal, PtrInt ou NativeInt (wte/re/tipos.md). }
  TOffset = Int64;

const
  { Deslocamento absoluto em bytes na imagem MODE2/2352 crua.

    NAO sao offsets de arquivo do ISO9660. Apontam para o fluxo de setores cru e
    foram calibrados a mao para cair dentro da regiao de dados de 2048 bytes de
    um setor (bytes 24..2071); as leituras que cruzariam fronteira de setor sao
    quebradas por seeks explicitos para as variantes *_A / *_B.

    Constantes SEM tipo de proposito: o FPC avalia inteiro constante em Int64,
    e sem tipo elas nao podem ser escritas nem com $J ligado. }

  OFS_TEAM_NAME_1            = 1012640;  { was OFS_NOMI_SQ1 }
  OFS_TEAM_NAME_1_END        = 1013431;  { was OFS_NOMI_SQ1_F }
  OFS_TEAM_NAME_1_A          = 1013736;  { was OFS_NOMI_SQ1A }
  OFS_TEAM_NAME_2            = 1881968;  { was OFS_NOMI_SQ2 }
  OFS_TEAM_NAME_3            = 2003996;  { was OFS_NOMI_SQ3 }
  OFS_TEAM_NAME_4            = 2830160;  { was OFS_NOMI_SQ4 }
  OFS_TEAM_NAME_5            = 4822908;  { was OFS_NOMI_SQ5 }
  OFS_TEAM_NAME_5_A          = 4823976;  { was OFS_NOMI_SQ5A }
  OFS_TEAM_NAME_6            = 5651448;  { was OFS_NOMI_SQ6 }
  OFS_TEAM_NAME_6_A          = 5651880;  { was OFS_NOMI_SQ6A }
  OFS_TEAM_NAME_6_B          = 5652364;  { was OFS_NOMI_SQ6B }
  OFS_TEAM_NAME_KANJI        = 2002316;  { was OFS_NOMI_SQK }
  OFS_TEAM_NAME_KANJI_A      = 2003928;  { was OFS_NOMI_SQK1 }
  OFS_TEAM_MIXED_CASE_NAME   = 4598596;  { was OFS_NOMI_SQ_M }
  OFS_TEAM_ABBREV_1          = 2004996;  { was OFS_NOMI_SQ_AB1 }
  OFS_TEAM_ABBREV_2          = 5651068;  { was OFS_NOMI_SQ_AB2 }
  OFS_TEAM_ABBREV_3          = 4234484;  { was OFS_NOMI_SQ_AB3 }
  OFS_ML_TEAM_NAME_7         = 2028267;  { was OFS_NOMI_PML1 }
  OFS_ML_TEAM_NAME_8         = 2476048;  { was OFS_NOMI_PML2 }
  OFS_ML_TEAM_NAME_8_A       = 2476680;  { was OFS_NOMI_PML2A }
  OFS_TEAM_BARS              = 2328184;  { was OFS_BAR }
  OFS_TEAM_BARS_A            = 2328504;  { was OFS_BAR1 }
  OFS_KICKER                 = 2329056;
  OFS_PLAYER_NAME            = 387792;  { was OFS_NOMI_G }
  OFS_PLAYER_NAME_2          = 390456;  { was OFS_NOMI_G2 }
  OFS_PLAYER_NAME_3          = 392808;  { was OFS_NOMI_G3 }
  OFS_PLAYER_NAME_4          = 395160;  { was OFS_NOMI_G4 }
  OFS_PLAYER_NAME_5          = 397512;  { was OFS_NOMI_G5 }
  OFS_PLAYER_NAME_6          = 399864;  { was OFS_NOMI_G6 }
  OFS_PLAYER_NAME_7          = 402216;  { was OFS_NOMI_G7 }
  OFS_PLAYER_NAME_8          = 404568;  { was OFS_NOMI_G8 }
  OFS_ML_PLAYER_NAME         = 2006288;  { was OFS_NOMI_GML }
  OFS_ML_PLAYER_NAME_2       = 2008632;  { was OFS_NOMI_GML2 }
  OFS_ML_PLAYER_NAME_3       = 2010984;  { was OFS_NOMI_GML3 }
  OFS_PLAYER_ATTR            = 2179492;  { was OFS_CARAT_G }
  OFS_PLAYER_ATTR_1          = 2180328;  { was OFS_CARAT_G1 }
  OFS_PLAYER_ATTR_2          = 2182680;  { 2352 (OFS_CARAT_G2) }
  OFS_PLAYER_ATTR_3          = 2185032;  { was OFS_CARAT_G3 }
  OFS_PLAYER_ATTR_4          = 2187384;  { was OFS_CARAT_G4 }
  OFS_PLAYER_ATTR_5          = 2189736;  { was OFS_CARAT_G5 }
  OFS_PLAYER_ATTR_6          = 2192088;  { was OFS_CARAT_G6 }
  OFS_PLAYER_ATTR_7          = 2194440;  { was OFS_CARAT_G7 }
  OFS_PLAYER_ATTR_8          = 2196792;  { was OFS_CARAT_G8 }
  OFS_PLAYER_ATTR_9          = 2199144;  { was OFS_CARAT_G9 }
  OFS_ML_PLAYER_ATTR         = 2204112;  { was OFS_CARAT_GML }
  OFS_ML_PLAYER_ATTR_1       = 2206200;  { was OFS_CARAT_GML1 }
  OFS_ML_PLAYER_ATTR_2       = 2208552;  { was OFS_CARAT_GML2 }
  OFS_FLAG_SHAPE_COPY_1      = 1929004;  { was OFS_BANDIERE_FORMA1 }
  OFS_FLAG_SHAPE_COPY_2      = 2005412;  { was OFS_BANDIERE_FORMA2 }
  OFS_FLAG_SHAPE_COPY_3      = 2328060;  { was OFS_BANDIERE_FORMA3 }
  OFS_FLAG_SHAPE_COPY_4      = 4904664;  { was OFS_BANDIERE_FORMA4 }
  OFS_FLAG_SHAPE_COPY_5      = 5711640;  { was OFS_BANDIERE_FORMA5 }
  OFS_FLAG_COLOURS           = 12549518;  { was OFS_BANDIERE_COLORE }
  OFS_FLAG_COLOURS_A         = 12550296;  { was OFS_BANDIERE_COLORE1 }
  OFS_FLAG_COLOURS_B         = 12552648;  { was OFS_BANDIERE_COLORE2 }
  OFS_FLAG_COLOURS_SENEGAL   = 12545758;  { was OFS_BANDIERE_COLORE_SEN }
  OFS_COST_NATIONAL          = 3067404;  { was OFS_COSTI_NAZ }
  OFS_COST_NC                = 3069512;  { was OFS_COSTI_NC }
  OFS_SQUAD_NUMBERS_ML       = 2014504;  { was OFS_NUMERI_ML }
  OFS_SQUAD_NUMBERS_NATIONAL = 404716;  { was OFS_NUMERI_NAZ }
  OFS_FORMATIONS             = 2303700;  { was OFS_TATTICHE }
  OFS_FORMATIONS_A           = 2304984;  { was OFS_TATTICHEA }
  OFS_LINK_ML                = 2012680;
  OFS_LINK_ML1               = 2012728;
  OFS_LINK_ML2               = 2013336;
  OFS_KIT_PREVIEW            = 2667256;  { was OFS_ANT_MAGLIE }
  OFS_KIT_PREVIEW_A          = 2669544;  { was OFS_ANT_MAGLIE1 }
  OFS_KIT_PREVIEW_B          = 2671896;  { was OFS_ANT_MAGLIE2 }
  OFS_KIT_PREVIEW_C          = 2674248;  { was OFS_ANT_MAGLIE3 }
  SECTOR_SIZE                = 2352;
  SECTOR_DATA_BEGIN          = 24;
  SECTOR_DATA_END            = 2072;

implementation

end.
