{ wte_uniformes -- que arquivo de bandeira e de uniforme cada time usa.

  GERADO por wte/tools/dump_render2d.py a partir de
  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai
  no gerador, e depois se regenera.

  Sao as duas tabelas de `.data` da WTE-TASK-29, e elas respondem
  perguntas diferentes. A COR de tudo aqui vem da imagem de CD; o que
  estas tabelas dizem e a FORMA -- que estencil de bandeira, que
  padrao de tecido.

  FORMA_PADRAO (0x004231e8) e a bandeira *padrao* de cada
  time, e o desenho NAO a usa: quem manda e o byte lido da imagem
  (secao 3.2 do `wte/re/assets.md`). Ela existe para o combo de forma
  do `ficha_color`, que indexa esta tabela em vez de digitar o numero,
  e e por isso que os oito indices sem arquivo (44..51) nunca sao
  pedidos.

  UNIFORMES (0x004232a6) e a fonte real do desenho: a
  forma da camisa NAO esta na imagem de CD, e um par fixo por time e
  por jogo. `jogo` e 0 (Primeiro) ou 1 (Segundo). }
unit wte_uniformes;

{$mode objfpc}{$H+}

interface

const
  TIMES_TOTAL = 95;

  { A forma de bandeira padrao de cada time. }
  FORMA_PADRAO: array[0..TIMES_TOTAL - 1] of Byte = (
    0, 2, 3, 4, 5, 6, 0, 0, 7, 4, 0, 8,
    7, 9, 9, 9, 9, 8, 10, 7, 7, 11, 11, 7,
    0, 7, 12, 13, 8, 7, 14, 15, 7, 0, 0, 16,
    0, 17, 18, 52, 7, 19, 20, 8, 21, 12, 22, 53,
    23, 23, 24, 25, 26, 27, 43, 43, 4, 0, 7, 0,
    7, 19, 22, 28, 29, 30, 31, 0, 54, 55, 33, 34,
    35, 32, 28, 36, 21, 39, 0, 41, 42, 31, 37, 36,
    38, 56, 57, 7, 17, 40, 40, 58, 59, 60, 1
  );

  { `(camisa, calcao)` por time e por jogo: o indice 0 e o Primeiro
    uniforme, o 1 e o Segundo. }
type
  TJogoDeUniforme = record
    camisa: Byte;
    calcao: Byte;
  end;

const
  UNIFORMES: array[0..TIMES_TOTAL - 1, 0..1] of TJogoDeUniforme = (
    ((camisa: 0; calcao: 0), (camisa: 1; calcao: 1)),
    ((camisa: 2; calcao: 0), (camisa: 2; calcao: 2)),
    ((camisa: 3; calcao: 2), (camisa: 3; calcao: 2)),
    ((camisa: 4; calcao: 2), (camisa: 4; calcao: 0)),
    ((camisa: 0; calcao: 2), (camisa: 5; calcao: 2)),
    ((camisa: 3; calcao: 0), (camisa: 0; calcao: 2)),
    ((camisa: 6; calcao: 3), (camisa: 7; calcao: 3)),
    ((camisa: 8; calcao: 3), (camisa: 8; calcao: 3)),
    ((camisa: 9; calcao: 2), (camisa: 10; calcao: 4)),
    ((camisa: 2; calcao: 0), (camisa: 2; calcao: 0)),
    ((camisa: 9; calcao: 2), (camisa: 9; calcao: 2)),
    ((camisa: 11; calcao: 2), (camisa: 11; calcao: 2)),
    ((camisa: 12; calcao: 2), (camisa: 13; calcao: 4)),
    ((camisa: 14; calcao: 5), (camisa: 14; calcao: 5)),
    ((camisa: 15; calcao: 5), (camisa: 16; calcao: 0)),
    ((camisa: 17; calcao: 4), (camisa: 5; calcao: 0)),
    ((camisa: 18; calcao: 4), (camisa: 18; calcao: 4)),
    ((camisa: 9; calcao: 0), (camisa: 9; calcao: 0)),
    ((camisa: 18; calcao: 0), (camisa: 5; calcao: 3)),
    ((camisa: 19; calcao: 4), (camisa: 10; calcao: 4)),
    ((camisa: 19; calcao: 0), (camisa: 20; calcao: 0)),
    ((camisa: 18; calcao: 4), (camisa: 18; calcao: 4)),
    ((camisa: 21; calcao: 0), (camisa: 22; calcao: 0)),
    ((camisa: 18; calcao: 0), (camisa: 18; calcao: 0)),
    ((camisa: 17; calcao: 4), (camisa: 19; calcao: 4)),
    ((camisa: 4; calcao: 4), (camisa: 23; calcao: 4)),
    ((camisa: 24; calcao: 0), (camisa: 25; calcao: 0)),
    ((camisa: 26; calcao: 4), (camisa: 18; calcao: 4)),
    ((camisa: 11; calcao: 0), (camisa: 11; calcao: 0)),
    ((camisa: 19; calcao: 4), (camisa: 27; calcao: 0)),
    ((camisa: 11; calcao: 0), (camisa: 11; calcao: 0)),
    ((camisa: 4; calcao: 0), (camisa: 4; calcao: 0)),
    ((camisa: 28; calcao: 0), (camisa: 28; calcao: 0)),
    ((camisa: 29; calcao: 0), (camisa: 29; calcao: 0)),
    ((camisa: 11; calcao: 0), (camisa: 11; calcao: 0)),
    ((camisa: 30; calcao: 4), (camisa: 31; calcao: 4)),
    ((camisa: 30; calcao: 0), (camisa: 5; calcao: 0)),
    ((camisa: 15; calcao: 0), (camisa: 15; calcao: 0)),
    ((camisa: 23; calcao: 0), (camisa: 32; calcao: 0)),
    ((camisa: 33; calcao: 0), (camisa: 34; calcao: 0)),
    ((camisa: 35; calcao: 0), (camisa: 35; calcao: 0)),
    ((camisa: 23; calcao: 0), (camisa: 23; calcao: 0)),
    ((camisa: 36; calcao: 0), (camisa: 36; calcao: 0)),
    ((camisa: 37; calcao: 0), (camisa: 37; calcao: 0)),
    ((camisa: 38; calcao: 0), (camisa: 39; calcao: 0)),
    ((camisa: 3; calcao: 4), (camisa: 40; calcao: 4)),
    ((camisa: 38; calcao: 3), (camisa: 41; calcao: 0)),
    ((camisa: 42; calcao: 4), (camisa: 43; calcao: 0)),
    ((camisa: 44; calcao: 0), (camisa: 44; calcao: 0)),
    ((camisa: 45; calcao: 0), (camisa: 45; calcao: 0)),
    ((camisa: 12; calcao: 0), (camisa: 12; calcao: 0)),
    ((camisa: 46; calcao: 0), (camisa: 46; calcao: 0)),
    ((camisa: 47; calcao: 0), (camisa: 48; calcao: 0)),
    ((camisa: 27; calcao: 0), (camisa: 27; calcao: 0)),
    ((camisa: 7; calcao: 0), (camisa: 7; calcao: 0)),
    ((camisa: 37; calcao: 0), (camisa: 37; calcao: 0)),
    ((camisa: 40; calcao: 0), (camisa: 40; calcao: 0)),
    ((camisa: 33; calcao: 0), (camisa: 37; calcao: 0)),
    ((camisa: 40; calcao: 0), (camisa: 40; calcao: 0)),
    ((camisa: 40; calcao: 0), (camisa: 28; calcao: 0)),
    ((camisa: 4; calcao: 0), (camisa: 4; calcao: 0)),
    ((camisa: 4; calcao: 0), (camisa: 4; calcao: 0)),
    ((camisa: 49; calcao: 3), (camisa: 4; calcao: 3)),
    ((camisa: 50; calcao: 0), (camisa: 51; calcao: 0)),
    ((camisa: 52; calcao: 0), (camisa: 53; calcao: 0)),
    ((camisa: 54; calcao: 0), (camisa: 54; calcao: 0)),
    ((camisa: 54; calcao: 0), (camisa: 54; calcao: 0)),
    ((camisa: 55; calcao: 4), (camisa: 54; calcao: 3)),
    ((camisa: 56; calcao: 0), (camisa: 54; calcao: 0)),
    ((camisa: 50; calcao: 4), (camisa: 57; calcao: 0)),
    ((camisa: 58; calcao: 3), (camisa: 59; calcao: 0)),
    ((camisa: 60; calcao: 0), (camisa: 61; calcao: 0)),
    ((camisa: 62; calcao: 0), (camisa: 54; calcao: 3)),
    ((camisa: 63; calcao: 0), (camisa: 64; calcao: 0)),
    ((camisa: 65; calcao: 0), (camisa: 66; calcao: 0)),
    ((camisa: 67; calcao: 0), (camisa: 68; calcao: 0)),
    ((camisa: 69; calcao: 3), (camisa: 70; calcao: 3)),
    ((camisa: 71; calcao: 0), (camisa: 72; calcao: 0)),
    ((camisa: 73; calcao: 0), (camisa: 68; calcao: 0)),
    ((camisa: 74; calcao: 0), (camisa: 50; calcao: 0)),
    ((camisa: 75; calcao: 0), (camisa: 76; calcao: 0)),
    ((camisa: 77; calcao: 0), (camisa: 78; calcao: 0)),
    ((camisa: 79; calcao: 0), (camisa: 54; calcao: 0)),
    ((camisa: 80; calcao: 0), (camisa: 81; calcao: 0)),
    ((camisa: 82; calcao: 0), (camisa: 83; calcao: 0)),
    ((camisa: 84; calcao: 3), (camisa: 85; calcao: 3)),
    ((camisa: 86; calcao: 0), (camisa: 87; calcao: 0)),
    ((camisa: 88; calcao: 0), (camisa: 88; calcao: 0)),
    ((camisa: 89; calcao: 0), (camisa: 90; calcao: 0)),
    ((camisa: 91; calcao: 0), (camisa: 92; calcao: 0)),
    ((camisa: 79; calcao: 0), (camisa: 50; calcao: 0)),
    ((camisa: 93; calcao: 0), (camisa: 54; calcao: 3)),
    ((camisa: 94; calcao: 0), (camisa: 95; calcao: 0)),
    ((camisa: 96; calcao: 4), (camisa: 97; calcao: 4)),
    ((camisa: 98; calcao: 0), (camisa: 98; calcao: 0))
  );

implementation

end.
