{ wte_blococor -- onde na imagem mora o bloco de cor de cada time.

  GERADO por wte/tools/dump_blococor.py a partir de
  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai
  no gerador, e depois se regenera.

  So DADO mora aqui. As sete regioes, os tamanhos e o `30` contra o
  `32` sao logica, e ficam no `wte_cor.pas` junto de quem os usa --
  a mesma divisao que a `wte_render2d` tem contra o `wte_uniformes`.

  A CONTA E DO `0x00404E70`, e ela e a geometria MODE2/2352 escrita a
  mao:

      absoluto = logico + 304 * (logico div 2048) + base

  Ela NAO passa pelo `EnderecoDeDados` do `we2002_estado` porque a
  base nao cai em fronteira de setor: `$0025AEF8` nao e multiplo de
  2352 mais 24. Fica como o original a escreve, com a base crua.

  PALETA_DA_BANDEIRA (0x00423247) e a unica coisa aqui que
  nao e formula, e por isso este gerador existe: os 95 bytes NAO sao
  identidade -- times compartilham paleta de bandeira. O time 36 vale
  255 nela e tem ramo proprio no original (`cmp eax,0x24`), com
  logico fixo.

  FORMA_DA_BANDEIRA (0x00423634) sao as CINCO copias do
  byte de forma. O carregador le so a do meio; o gravador escreve as
  cinco. Cada uma e offset absoluto, somado ao indice do time. }
unit wte_blococor;

{$mode objfpc}{$H+}

interface

uses
  we2002_offsets;

const
  BLOCOCOR_TIMES = 95;
  BLOCOCOR_CHUTEIRAS = 8;
  BLOCOCOR_TIME_SENEGAL = 36;

  { Os imediatos do `0x00404E70`, na ordem em que ele os usa. }
  BLOCOCOR_SALTO = 304;
  BLOCOCOR_DADOS = 2048;
  BLOCOCOR_BASE_PALETA   = $00BE35D8;
  BLOCOCOR_BASE_UNIFORME = $0025AEF8;
  BLOCOCOR_LOG_BANDEIRA  = $00011E26;
  BLOCOCOR_LOG_SENEGAL   = $000110A6;
  BLOCOCOR_LOG_UNIFORME0 = $0002A042;
  BLOCOCOR_LOG_UNIFORME1 = $0002A062;
  BLOCOCOR_PASSO_UNIFORME = 64;
  BLOCOCOR_LOG_CHUTEIRA  = $00010964;

  { Os dois que o original grava como imediato, sem conversao. }
  BLOCOCOR_QUARTA_PALETA = 12544268;
  BLOCOCOR_PADRAO_CAMISA = 14368636;

  { Qual paleta de bandeira cada time usa. 255 = tem ramo proprio. }
  PALETA_DA_BANDEIRA: array[0..BLOCOCOR_TIMES - 1] of Byte = (
    0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
    13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
    25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
    255, 37, 38, 96, 40, 41, 42, 43, 44, 45, 46, 97,
    47, 48, 49, 50, 52, 53, 54, 55, 4, 7, 9, 11,
    13, 41, 46, 58, 59, 60, 61, 62, 36, 98, 64, 65,
    66, 63, 67, 68, 84, 75, 69, 80, 81, 70, 71, 72,
    73, 63, 99, 76, 77, 78, 79, 100, 101, 102, 103
  );

  { As cinco copias do byte de forma de bandeira, conferidas contra
    os `OFS_FLAG_SHAPE_COPY_*` do `we2002_core` pelo gerador. }
  FORMA_DA_BANDEIRA: array[0..4] of TOffset = (
    OFS_FLAG_SHAPE_COPY_1, OFS_FLAG_SHAPE_COPY_2,
    OFS_FLAG_SHAPE_COPY_3, OFS_FLAG_SHAPE_COPY_4,
    OFS_FLAG_SHAPE_COPY_5
  );

implementation

end.
