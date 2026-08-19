{ GERADO por wte/tools/conta_ml.py -- NAO EDITE A MAO.

  Quantos jogadores non-contract cada um dos 120 times tem.
  Lida de `0x00423424` do `we-team-editor/we-team-editor.exe`; a soma dos 120 da
  462, que e o `PLAYERS_NC` do `we2002_core`.

  O `wte.exe` soma o prefixo a cada chamada (`0x0040423c`); o
  `ed.exe` guarda o prefixo pronto em `START_LINK[]`. O gerador
  confere as duas codificacoes e recusa se divergirem onde a tabela
  esta definida. }
const
  ML_NC_POR_TIME: array[0..119] of LongWord = (
      5,   4,   1,  41,   7,  42,  68,   5,  37,   1,   { times   0..  9 }
     64,   1,  25,   3,   2,   5,   1,   1,   0,   1,   { times  10.. 19 }
      0,   0,   4,   3,   4,   0,   8,  10,   4,   2,   { times  20.. 29 }
      2,   0,   0,   1,   0,   0,   0,   1,   0,   0,   { times  30.. 39 }
      1,  36,   0,   0,   1,   3,  34,   0,   4,   0,   { times  40.. 49 }
      0,   0,   0,   2,   0,   0,   0,   0,   0,   0,   { times  50.. 59 }
      0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   { times  60.. 69 }
      0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   { times  70.. 79 }
      0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   { times  80.. 89 }
      0,   0,   0,   0,   0,   1,   1,   2,   2,   2,   { times  90.. 99 }
      0,   1,   0,   0,   0,   1,   7,   0,   5,   1,   { times 100..109 }
      1,   1,   0,   0,   1,   0,   2,   0,   0,   0   { times 110..119 }
  );
