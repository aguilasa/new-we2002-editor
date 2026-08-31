# PES2 — os 69 `OFS_*` do WE2002 como (arquivo, offset relativo)

Gerado por `tools/pes2/ofs_map.py`. A coluna *absoluto* é o valor de [`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp), medido na imagem do WE2002; as duas seguintes são o mesmo ponto expresso de um jeito que atravessa discos.

**Isto não afirma que o offset relativo vale no PES2.** As tabelas se deslocam entre releases do próprio PES2 (§1.12), que dirá entre jogos. O que a tabela dá é o arquivo onde procurar e a ordem de grandeza — que é a diferença entre busca dirigida e varredura cega.

| Arquivo | `OFS_*` | Existe no PES2 | Tamanho WE2002 | Tamanho PES2 |
|---|---:|---|---:|---:|
| `/SELECT.BIN` | 32 | sim | 300648 | 216472 |
| `/SLPM_870.56` | 9 | sim, como `SLES_039.57` | 337920 | 333824 |
| `/SELECT2.BIN` | 6 | sim | 271540 | 304464 |
| `/REPLAYS.BIN` | 5 | sim | 62969 | 68708 |
| `/BIN/DAT2D.BIN` | 4 | sim | 81124 | 68556 |
| `/ENDING.BIN` | 3 | sim | 399224 | 395400 |
| `/SELFORM.BIN` | 3 | sim | 96439 | 96224 |
| `/SELECT4.BIN` | 2 | sim | 254020 | 248352 |
| `/RESULT.BIN` | 1 | sim | 18137 | 19481 |
| `/SELECT3.BIN` | 1 | sim | 202064 | 206432 |
| `/SELECTC.BIN` | 1 | sim | 106966 | 88780 |
| `/SELECT8.BIN` | 1 | sim | 125176 | 131156 |
| `/OPENNING.BIN` | 1 | sim | 25232 | 26280 |

## Os cinco pares que já se pode afirmar

Mesma tabela, mesmo arquivo, nos dois jogos. O deslocamento é o que sobra depois de tirar arquivo e tipo de conteúdo da conta.

| `OFS_*` | Arquivo | WE2002 | PES2 `(EsIt)` | Δ |
|---|---|---:|---:|---:|
| `OFS_TEAM_NAME_1` | `/ENDING.BIN` | 1256 | 1256 | +0 |
| `OFS_TEAM_NAME_2` | `/RESULT.BIN` | 344 | 524 | +180 |
| `OFS_TEAM_MIXED_CASE_NAME` | `/SELECTC.BIN` | 10652 | 16576 | +5924 |
| `OFS_TEAM_ABBREV_2` | `/REPLAYS.BIN` | 5636 | 11000 | +5364 |
| `OFS_TEAM_ABBREV_3` | `/SELECT8.BIN` | 860 | 1016 | +156 |

### `/SELECT.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_NAME_KANJI` | 2002316 | 2788 |
| `OFS_TEAM_NAME_KANJI_A` | 2003928 | 4096 |
| `OFS_TEAM_NAME_3` | 2003996 | 4164 |
| `OFS_TEAM_ABBREV_1` | 2004996 | 5164 |
| `OFS_FLAG_SHAPE_COPY_2` | 2005412 | 5580 |
| `OFS_ML_PLAYER_NAME` | 2006288 | 6152 |
| `OFS_ML_PLAYER_NAME_2` | 2008632 | 8192 |
| `OFS_ML_PLAYER_NAME_3` | 2010984 | 10240 |
| `OFS_LINK_ML` | 2012680 | 11936 |
| `OFS_LINK_ML1` | 2012728 | 11984 |
| `OFS_LINK_ML2` | 2013336 | 12288 |
| `OFS_SQUAD_NUMBERS_ML` | 2014504 | 13456 |
| `OFS_ML_TEAM_NAME_7` | 2028267 | 25395 |
| `OFS_PLAYER_ATTR` | 2179492 | 157164 |
| `OFS_PLAYER_ATTR_1` | 2180328 | 157696 |
| `OFS_PLAYER_ATTR_2` | 2182680 | 159744 |
| `OFS_PLAYER_ATTR_3` | 2185032 | 161792 |
| `OFS_PLAYER_ATTR_4` | 2187384 | 163840 |
| `OFS_PLAYER_ATTR_5` | 2189736 | 165888 |
| `OFS_PLAYER_ATTR_6` | 2192088 | 167936 |
| `OFS_PLAYER_ATTR_7` | 2194440 | 169984 |
| `OFS_PLAYER_ATTR_8` | 2196792 | 172032 |
| `OFS_PLAYER_ATTR_9` | 2199144 | 174080 |
| `OFS_ML_PLAYER_ATTR` | 2204112 | 178440 |
| `OFS_ML_PLAYER_ATTR_1` | 2206200 | 180224 |
| `OFS_ML_PLAYER_ATTR_2` | 2208552 | 182272 |
| `OFS_FORMATIONS` | 2303700 | 265260 |
| `OFS_FORMATIONS_A` | 2304984 | 266240 |
| `OFS_FLAG_SHAPE_COPY_3` | 2328060 | 286580 |
| `OFS_TEAM_BARS` | 2328184 | 286704 |
| `OFS_TEAM_BARS_A` | 2328504 | 286720 |
| `OFS_KICKER` | 2329056 | 287272 |

### `/SLPM_870.56`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_PLAYER_NAME` | 387792 | 288760 |
| `OFS_PLAYER_NAME_2` | 390456 | 290816 |
| `OFS_PLAYER_NAME_3` | 392808 | 292864 |
| `OFS_PLAYER_NAME_4` | 395160 | 294912 |
| `OFS_PLAYER_NAME_5` | 397512 | 296960 |
| `OFS_PLAYER_NAME_6` | 399864 | 299008 |
| `OFS_PLAYER_NAME_7` | 402216 | 301056 |
| `OFS_PLAYER_NAME_8` | 404568 | 303104 |
| `OFS_SQUAD_NUMBERS_NATIONAL` | 404716 | 303252 |

### `/SELECT2.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_ML_TEAM_NAME_8` | 2476048 | 5816 |
| `OFS_ML_TEAM_NAME_8_A` | 2476680 | 6144 |
| `OFS_KIT_PREVIEW` | 2667256 | 172096 |
| `OFS_KIT_PREVIEW_A` | 2669544 | 174080 |
| `OFS_KIT_PREVIEW_B` | 2671896 | 176128 |
| `OFS_KIT_PREVIEW_C` | 2674248 | 178176 |

### `/REPLAYS.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_ABBREV_2` | 5651068 | 5636 |
| `OFS_TEAM_NAME_6` | 5651448 | 6016 |
| `OFS_TEAM_NAME_6_A` | 5651880 | 6144 |
| `OFS_TEAM_NAME_6_B` | 5652364 | 6628 |
| `OFS_FLAG_SHAPE_COPY_5` | 5711640 | 58304 |

### `/BIN/DAT2D.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_FLAG_COLOURS_SENEGAL` | 12545758 | 69798 |
| `OFS_FLAG_COLOURS` | 12549518 | 73254 |
| `OFS_FLAG_COLOURS_A` | 12550296 | 73728 |
| `OFS_FLAG_COLOURS_B` | 12552648 | 75776 |

### `/ENDING.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_NAME_1` | 1012640 | 1256 |
| `OFS_TEAM_NAME_1_END` | 1013431 | 2047 |
| `OFS_TEAM_NAME_1_A` | 1013736 | 2048 |

### `/SELFORM.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_NAME_5` | 4822908 | 1284 |
| `OFS_TEAM_NAME_5_A` | 4823976 | 2048 |
| `OFS_FLAG_SHAPE_COPY_4` | 4904664 | 72400 |

### `/SELECT4.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_COST_NATIONAL` | 3067404 | 8564 |
| `OFS_COST_NC` | 3069512 | 10368 |

### `/RESULT.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_NAME_2` | 1881968 | 344 |

### `/SELECT3.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_NAME_4` | 2830160 | 6824 |

### `/SELECTC.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_MIXED_CASE_NAME` | 4598596 | 10652 |

### `/SELECT8.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_TEAM_ABBREV_3` | 4234484 | 860 |

### `/OPENNING.BIN`

| `OFS_*` | absoluto | relativo |
|---|---:|---:|
| `OFS_FLAG_SHAPE_COPY_1` | 1929004 | 20820 |

