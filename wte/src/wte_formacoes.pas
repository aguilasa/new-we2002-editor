{ wte_formacoes -- as 18 formacoes predefinidas do campinho tatico.

  GERADO por wte/tools/dump_formacoes.py a partir de
  we-team-editor/we-team-editor.exe. NAO EDITAR A MAO: a correcao vai
  no gerador, e depois se regenera.

  E a tabela que o `estrategia.FormCreate` monta em 0x00433f0c a
  partir de quatro blobs de `.data`, e que o
  `estrategia.lista_formacionesClick` indexa. Cada registro tem 44
  bytes: quatro colunas de 11.

  `x` e `y` NAO sao pixel: viram destino por
  `DestinoX = x*8 - 2` e `DestinoY = ((y - 3) div 2)*5 - 7`, que e o
  que o `0x004097d4` faz. `zona` indexa o `wte_zonas.pas`; `papel`
  indexa as abreviaturas de posicao do `wte_legendas.pas`. }
unit wte_formacoes;

{$mode objfpc}{$H+}

interface

type
  TFormacao = record
    nome: string;
    papel: array[0..10] of Byte;
    x: array[0..10] of Byte;
    y: array[0..10] of Byte;
    zona: array[0..10] of Byte;
  end;

const
  FORMACOES_TOTAL = 18;
  FORMACAO_JOGADORES = 11;

  { O `long double` de 80 bits em 0x004099b0, decodificado. }
  PASSO_DA_ANIMACAO = 0.2;

  { As 22 abreviaturas de posicao de 0x00423b8c, que a coluna
    `papel` indexa. Elas NAO saem daqui: saem do `legendas.tsv`, do
    `dump_legendas.py`, que ja as varria como tabela `resto` -- e
    este gerador aborta se nao achar as 22. Uma cadeia, um dono. }
  POSICOES_TOTAL = 22;

  POSICOES: array[0..POSICOES_TOTAL - 1] of string = (
    '--', 'Gl', 'Za', 'Za', 'Zl', 'Lib', 'Za', 'Le', 'Ld', 'Vl', 'Vl', 'Vl', 'Ae', 'Ad', 'Me', 'Me', 'Me', 'At', 'At', 'At', 'Pe', 'Pd'
  );

  { AS OITO CORES DE RADAR de 0x00423624, em BGR555 -- uma por item dos dois combos
    do `estrategia`. O `0x0040A0B4` NAO as usa como paleta: ele
    percorre a tabela procurando o par de bytes que a imagem trouxe, e
    o indice que casar e o item que o combo seleciona. O que importa
    aqui e a ORDEM. }
  CORES_DE_RADAR_TOTAL = 8;

  CORES_DE_RADAR: array[0..CORES_DE_RADAR_TOTAL - 1] of Word = (
    $7FFF, $0421, $03E0, $03FF, $001F, $7C00, $7FE0, $7C1F
  );

  { OS DEZ PARES QUE O ` Accept` AVISA de 0x00423f14. Nao sao cores: sao os
    indices dos dois combos. O `estrategia.BitBtn3Click` copia os
    vinte dwords para a pilha no prologo e, se o par escolhido casar
    com um deles, abre o `ficha_warning_2` e desiste se a resposta
    nao for `Sim`. Casar com um par NAO impede -- pergunta. }
  PARES_DE_RADAR_TOTAL = 10;

  PARES_DE_RADAR: array[0..PARES_DE_RADAR_TOTAL - 1, 0..1] of Byte = (
    (0, 3),
    (0, 6),
    (1, 5),
    (3, 6),
    (4, 7),
    (3, 0),
    (6, 0),
    (5, 1),
    (6, 3),
    (7, 4)
  );

  FORMACOES: array[0..FORMACOES_TOTAL - 1] of TFormacao = (
    (nome: 'STOCK';
     papel: (0, 2, 6, 7, 8, 10, 12, 13, 15, 17, 19);
     x: (0, 9, 9, 11, 11, 18, 26, 26, 34, 43, 43);
     y: (0, 41, 63, 19, 85, 52, 29, 75, 52, 38, 66);
     zona: (0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8)),
    (nome: 'DEFAULT';
     papel: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
     x: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
     y: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
     zona: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
    (nome: '4 - 5 - 1  A';
     papel: (0, 2, 6, 7, 8, 10, 12, 13, 14, 16, 18);
     x: (0, 9, 9, 11, 11, 18, 26, 26, 34, 34, 43);
     y: (0, 41, 63, 19, 85, 52, 29, 75, 40, 64, 52);
     zona: (0, 1, 1, 2, 3, 4, 5, 6, 7, 7, 8)),
    (nome: '4 - 5 - 1  B';
     papel: (0, 2, 6, 7, 8, 9, 11, 12, 13, 15, 18);
     x: (0, 9, 9, 11, 11, 18, 18, 26, 26, 34, 43);
     y: (0, 41, 63, 19, 85, 43, 61, 29, 75, 52, 52);
     zona: (0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 8)),
    (nome: '4 - 4 - 2  A';
     papel: (0, 2, 6, 7, 8, 10, 12, 13, 15, 17, 19);
     x: (0, 9, 9, 11, 11, 18, 26, 26, 34, 43, 43);
     y: (0, 41, 63, 19, 85, 52, 29, 75, 52, 38, 66);
     zona: (0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 8)),
    (nome: '4 - 4 - 2  B';
     papel: (0, 2, 6, 7, 8, 9, 11, 14, 16, 17, 19);
     x: (0, 9, 9, 11, 11, 18, 18, 30, 30, 43, 43);
     y: (0, 41, 63, 19, 85, 43, 61, 34, 70, 38, 66);
     zona: (0, 1, 1, 2, 3, 4, 4, 7, 7, 8, 8)),
    (nome: '4 - 3 - 3  A';
     papel: (0, 2, 6, 7, 8, 10, 14, 16, 18, 20, 21);
     x: (0, 9, 9, 11, 11, 18, 30, 30, 43, 43, 43);
     y: (0, 41, 63, 19, 85, 52, 40, 64, 52, 32, 72);
     zona: (0, 1, 1, 2, 3, 4, 7, 7, 8, 9, 10)),
    (nome: '4 - 3 - 3  B';
     papel: (0, 2, 6, 7, 8, 9, 11, 15, 18, 20, 21);
     x: (0, 9, 9, 11, 11, 18, 18, 30, 43, 43, 43);
     y: (0, 41, 63, 19, 85, 43, 61, 52, 52, 32, 72);
     zona: (0, 1, 1, 2, 3, 4, 4, 7, 8, 9, 10)),
    (nome: '3 - 6 - 1  A';
     papel: (0, 2, 3, 6, 10, 12, 13, 15, 14, 16, 18);
     x: (0, 9, 9, 9, 18, 26, 26, 26, 34, 34, 43);
     y: (0, 32, 52, 72, 52, 27, 77, 52, 40, 64, 52);
     zona: (0, 1, 1, 1, 4, 5, 6, 7, 7, 7, 8)),
    (nome: '3 - 6 - 1  B';
     papel: (0, 2, 3, 6, 9, 11, 12, 13, 14, 16, 18);
     x: (0, 9, 9, 9, 18, 18, 26, 26, 34, 34, 43);
     y: (0, 32, 52, 72, 43, 61, 27, 77, 40, 64, 52);
     zona: (0, 1, 1, 1, 4, 4, 5, 6, 7, 7, 8)),
    (nome: '3 - 5 - 2  A';
     papel: (0, 2, 3, 6, 10, 12, 13, 14, 16, 17, 19);
     x: (0, 9, 9, 9, 18, 26, 26, 34, 34, 43, 43);
     y: (0, 32, 52, 72, 52, 27, 77, 40, 64, 38, 66);
     zona: (0, 1, 1, 1, 4, 5, 6, 7, 7, 8, 8)),
    (nome: '3 - 5 - 2  B';
     papel: (0, 2, 3, 6, 9, 11, 12, 13, 15, 17, 19);
     x: (0, 9, 9, 9, 18, 18, 26, 26, 34, 43, 43);
     y: (0, 32, 52, 72, 43, 61, 27, 77, 52, 38, 66);
     zona: (0, 1, 1, 1, 4, 4, 5, 6, 7, 8, 8)),
    (nome: '3 - 4 - 3  A';
     papel: (0, 2, 3, 6, 10, 12, 13, 15, 18, 20, 21);
     x: (0, 9, 9, 9, 18, 26, 26, 34, 43, 43, 43);
     y: (0, 32, 52, 72, 52, 27, 77, 52, 52, 32, 72);
     zona: (0, 1, 1, 1, 4, 5, 6, 7, 8, 9, 10)),
    (nome: '3 - 4 - 3  B';
     papel: (0, 2, 3, 6, 9, 11, 14, 16, 18, 20, 21);
     x: (0, 9, 9, 9, 18, 18, 30, 30, 43, 43, 43);
     y: (0, 32, 52, 72, 43, 61, 34, 70, 52, 32, 72);
     zona: (0, 1, 1, 1, 4, 4, 7, 7, 8, 9, 10)),
    (nome: '5 - 4 - 1  A';
     papel: (0, 2, 3, 6, 7, 8, 10, 12, 13, 15, 18);
     x: (0, 9, 9, 9, 12, 12, 18, 26, 26, 34, 43);
     y: (0, 32, 52, 72, 17, 87, 52, 29, 75, 52, 52);
     zona: (0, 1, 1, 1, 2, 3, 4, 5, 6, 7, 8)),
    (nome: '5 - 4 - 1  B';
     papel: (0, 2, 3, 6, 7, 8, 9, 11, 14, 16, 18);
     x: (0, 9, 9, 9, 12, 12, 18, 18, 30, 30, 43);
     y: (0, 32, 52, 72, 17, 87, 43, 61, 34, 70, 52);
     zona: (0, 1, 1, 1, 2, 3, 4, 4, 7, 7, 8)),
    (nome: '5 - 3 - 2  A';
     papel: (0, 2, 3, 6, 7, 8, 10, 14, 16, 17, 19);
     x: (0, 9, 9, 9, 12, 12, 18, 34, 34, 43, 43);
     y: (0, 32, 52, 72, 17, 87, 52, 40, 64, 38, 66);
     zona: (0, 1, 1, 1, 2, 3, 4, 7, 7, 8, 8)),
    (nome: '5 - 3 - 2  B';
     papel: (0, 2, 3, 6, 7, 8, 9, 11, 15, 17, 19);
     x: (0, 9, 9, 9, 12, 12, 18, 18, 34, 43, 43);
     y: (0, 32, 52, 72, 17, 87, 43, 61, 52, 38, 66);
     zona: (0, 1, 1, 1, 2, 3, 4, 4, 7, 8, 8))
  );

implementation

end.
