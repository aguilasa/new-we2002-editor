# PES2 — inventário de texto do disco

Gerado por `tools/pes2/strings_inventory.py`. Trechos imprimíveis de 6 caracteres ou mais, em todos os arquivos Form 1, agrupados em **blocos densos** — que é a forma que uma tabela tem daqui de fora.

217 arquivos com trecho imprimível, 171161 trechos, **281 blocos**.

| Balde | Trechos | O que é |
|---|---:|---|
| `team` | 707 | casa com a lista canônica de nome de time |
| `abbrev` | 0 | casa com a tabela de abreviações |
| `player` | 1977 | casa com o pool de nomes de jogador |
| `namelike` | 4367 | **tem forma de nome e não está em nenhuma das listas** |
| `path` | 14 | caminho ou nome de arquivo do disco |
| `interface` | 98207 | texto de interface — tem espaço ou minúscula |
| `unknown` | 65889 | **o que a Fase 2 ainda não explicou** |

## Os maiores blocos

Um bloco é uma sequência de trechos separados por no máximo 24 bytes. Os que interessam à Fase 2 são os de balde `unknown`.

| Arquivo | Offset | Trechos | Bytes | Balde | Primeiro … último |
|---|---:|---:|---:|---|---|
| `/SELECT.BIN` | 19280 | 476 | 15096 | `interface` | `Dati Formazione N. ` … `ingresso MEMORY CARD` |
| `/SELECTC.BIN` | 17152 | 467 | 5143 | `player` | `Ecuador` … `Contero` |
| `/SELECT2.BIN` | 274194 | 457 | 6685 | `interface` | `WORLD SOCCER` … `WE STAFF` |
| `/SELECT2.BIN` | 4 | 422 | 14065 | `interface` | `Regola la posizione pr` … `a/Noche` |
| `/SLES_039.57` | 293830 | 400 | 5380 | `player` | `Contero` … `Di Sephoro` |
| `/SELECTC.BIN` | 4 | 332 | 12455 | `interface` | `Memorizzato. Questo gi` … `MEMORY CARD assente da` |
| `/REPLAYS.BIN` | 2220 | 277 | 7704 | `interface` | `Dati Formazione N. ` … `ingresso MEMORY CARD` |
| `/SELECT3.BIN` | 1360 | 274 | 7808 | `interface` | `Release:` … `Tabla de clasificacion` |
| `/SELECTC.BIN` | 45772 | 237 | 2598 | `namelike` | `Davinno` … `Beckenboer` |
| `/SELECTC.BIN` | 33476 | 228 | 2644 | `namelike` | `Tomazi` … `Reinmeyr` |
| `/SLES_039.57` | 261036 | 212 | 5335 | `interface` | `Manuale` … `Iniciar el partido.` |
| `/SELECT2.BIN` | 17876 | 204 | 9592 | `interface` | `Su "Campionato Master"` … `WARNING: Unexpected st` |
| `/SELECTC.BIN` | 12516 | 176 | 4600 | `interface` | `Caricamento file opzio` … `Saudi Arabia` |
| `/SELECTC.BIN` | 38376 | 166 | 1848 | `namelike` | `Navaji` … `Lupateli` |
| `/SELECTC.BIN` | 28256 | 154 | 1818 | `player` | `Killar` … `Hargreaves` |
| `/SELECT.BIN` | 5990 | 148 | 2426 | `namelike` | `M.Salgado` … `Pirsic` |
| `/SELECTC.BIN` | 24184 | 146 | 1788 | `player` | `Romezi` … `Zovkovic` |
| `/SELECT3.BIN` | 10024 | 129 | 3245 | `interface` | `Ecuador` … `Busca el triunfo para ` |
| `/SELECTC.BIN` | 36148 | 129 | 1542 | `namelike` | `Redundo` … `Osmanovski` |
| `/SELECTC.BIN` | 26688 | 123 | 1527 | `player` | `Perheschka` … `Nowotny` |

## Blocos que a Fase 2 ainda não explicou

46 de 281.

| Arquivo | Offset | Trechos | Primeiro … último |
|---|---:|---:|---|
| `/SD/PES2000.RA` | 1084626 | 45 | `AAQRbaaRQA1! .I` … `[[\L]klzkkL][L` |
| `/BIN/GDC_GDJ.BIN` | 8406 | 40 | `;6237ENTVV[[U` … `;QFOQHX^T6` |
| `/BIN/GDC_GNJ.BIN` | 8406 | 40 | `;6237ENTVV[[U` … `;QFOQHX^T6` |
| `/BIN/DATSEL_I.BIN` | 143180 | 37 | `|@|@h@h"` … `|%|@|@|@` |
| `/FNOTE_G.BIN` | 130 | 36 | `Position editieren` … `4-5-1A` |
| `/SD/PES2000.RA` | 1106820 | 36 | `+*;<Ml\n]nm^(` … `..-.--,` |
| `/BIN/GDC_GDJ.BIN` | 10211 | 35 | `YOBNP?NTTLTYH;JTMLHS` … `?9QVE09VDQYVSLE:NSL\O@FKAG` |
| `/BIN/GDC_GNJ.BIN` | 10211 | 35 | `YOBNP?NTTLTYH;JTMLHS` … `?9QVE09VDQYVSLE:NSL\O@FKAG` |
| `/BIN/GDC_MN.BIN` | 2967 | 28 | `D?FFGPP^W`W<1/|@Al@11<4G` … `ACMLO>CN>D0%` |
| `/BIN/GDC_GDJ.BIN` | 36657 | 26 | `27H?5899HT=NPFL<LITE[;1QCC` … `RRMMKBBA:<<WWIS[[` |
| `/BIN/GDC_GNJ.BIN` | 36341 | 26 | `27H?5899HT=NPFL<LITE[;1QCC` … `RRMMKBBA:<<WWIS[[` |
| `/SD/PES2000.RA` | 1081394 | 26 | `^ON<,*` … `}n}|l\Mlj[k[zy` |
| `/BIN/GDC_VD.BIN` | 4368 | 24 | `8:D8@;9?<<A<6;;` … `>3145<787:@GG:8` |
| `/BIN/GDC_VN.BIN` | 4368 | 24 | `8:D8@;9?<<A<6;;` … `>3145<787:@GG:8` |
| `/BIN/GDC_AD.BIN` | 24322 | 23 | `#&T>C(,7z` … `<@&ZT+D9AU` |
| `/FNOTE_I.BIN` | 408 | 19 | `Predef.` … `Tiratore` |
| `/FNOTE_S.BIN` | 368 | 19 | `Defecto` … `Lanzad.` |
| `/BIN/GDC_DD.BIN` | 47547 | 18 | `|@|@|@|@|@` … `|@|@|@|@` |
| `/SD/PES2000.RA` | 1085426 | 18 | `KkiL\]zkl\mMm\)` … `=>>NMN]]]M]\][` |
| `/BIN/GDC_GDJ.BIN` | 36137 | 17 | `ptxagh`j}%` … `6NUF7610?P` |
