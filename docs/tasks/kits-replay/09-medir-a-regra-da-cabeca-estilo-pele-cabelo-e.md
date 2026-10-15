---
id: KRP-TASK-09
---

# KRP-TASK-09 — Medir a regra da cabeça (estilo, pele, cabelo e barba) contra o registro do disco nos 22

## Goal

Fica medido se a hipótese (a)+(b) do relatório vale: `replay.py head <captura> [--player <registro>]` decodifica estilo (pela `assembly.HAIR_MAP`, com o *twin* da `FACE_TWINS`), pele, cabelo e barba (pela CLUT, regra do `looks`) e confronta com o registro de 12 bytes do jogador no disco, nos 22 dos dois laços. O resultado — regra que fecha, ou o que não fecha — vai escrito no §3.1 do plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (`head`)
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.1: o resultado)
- Out:
  - o desenho da cabeça (KRP-TASK-10)

## Done criteria

- [x] `replay.py head work/kits-oracle/replay-field-9-capture.json --player all --json` e o mesmo no `-10-`: por foco, seção, CLUT, estilo/pele/cabelo/barba decodificados e o registro do disco; a linha de resumo diz quantos dos 22 batem, colada no Log
- [x] as três figuras de perto (`replay-9-3.json`, `replay-10-2.json`, `replay-9.json`) dão o estilo e as colunas da tabela de [(a)](/docs/KITS-REPLAYS-9-10.md#a-cabelo-barba-e-pele-do-jogador-vêm-da-clut-da-cabeça-pela-regra-da-looks-set)
- [x] o esperado por jogador é constante no código (K1), e uma planta que troca a coluna do cabelo derruba a asserção com dado real (K2)
- [x] negativa é resultado: o que não bate fica escrito no §3.1 com comando e saída, e não bloqueia a task
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Achar o registro de cada um dos 22 (time e número pelo painel, item 7 do relatório) é parte da medição. Leitura do disco por `tools/looks/looks.py` (`records`, `decode`). Dois slots medidos dizem "nos dois", não "sempre".

## Log de Execução

- **done** (2026-10-15): a regra (a)+(b) fecha nos 22 dos dois laços e nas três capturas de perto; o resultado está no [§3.1](/docs/PLAN-KITS-REPLAY.md#3.1).

O que entrou:

- `core/replay.py`: `head_samples`, só as primitivas da seção da cabeça dentro do box da própria peça. O box da figura inteira pega a cabeça do vizinho: no slot 10, (16,482) no 4 da Croácia e (32,480) no 10 do Brasil. Também `head_styles`, `head_reading` (linha da CLUT → pele, coluna → cabelo ou barba), `head_expected` (estilo pelo `HAIR_MAP`, gêmea pelo `FACE_TWINS` desde `FACE_TWIN_FROM`) e `head_judge`;
- `replay.py head <captura> [--player all|N] [--plant-hair-column] [--json]`. O número de camisa vem de `OFS_SQUAD_NUMBERS_NATIONAL` (`ofs_map.read_offsets`, nunca digitado), e o registro é `time * 23 + vaga`. Também `HEAD_TEAMS` (576 → 41 Brasil, 640 → 22 Croácia) e `HEAD_EXPECT`, as 22 tuplas como constante (K1);
- `check`: confere `HEAD_EXPECT` contra o disco e julga a cabeça de toda figura seguida nas sete capturas; `--plant-hair-column` é a planta com dado real (K2);
- `selftest.py` `_replay_head_checks`: 11 casos sintéticos. Três controles: `replay-head-hair-column`, `replay-head-twin-unasked` e `replay-head-squad-unbiased`.

Os dois laços, por foco: seção, CLUT, leitura, registro do disco e o resumo.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-9-capture.json --player all
  focus 0  page 576  team 41   number 1    section 34  I, 9 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 1  page 576  team 41   number 1    section 34  I, 9 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 2  page 640  team 22   number 20   section 46  L, 17 prim(s), CLUT (32,480): skin A hair B beard -
           record 516 (slot 10) A-L3-B-A-B: section 46 skin A hair B beard B -- ok
  focus 3  page 640  team 22   number 11   section 46  L, 14 prim(s), CLUT (128,480): skin A hair H beard -
           record 515 (slot 9) A-L3-H-A-A: section 46 skin A hair H beard A -- ok
  focus 4  page 640  team 22   number 10   section 24  A, 12 prim(s), CLUT (32,480): skin A hair B beard -
           record 514 (slot 8) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 5  page 640  team 22   number 8    section 47  L twin, 17 prim(s), CLUT (128,480) (176,480): skin A hair H beard C
           record 513 (slot 7) A-L3-H-F-C: section 47 skin A hair H beard C -- ok
  focus 6  page 640  team 22   number 7    section 34  I, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 512 (slot 6) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 7  page 640  team 22   number 3    section 24  A, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 511 (slot 5) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 8  page 640  team 22   number 4    section 34  I, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 510 (slot 4) A-I2-B-A-B: section 34 skin A hair B beard B -- ok
  focus 9  page 640  team 22   number 14   section 24  A, 11 prim(s), CLUT (32,480): skin A hair B beard -
           record 509 (slot 3) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 10 page 640  team 22   number 5    section 28  G, 6 prim(s), CLUT (32,480): skin A hair B beard -
           record 508 (slot 2) A-G1-B-A-B: section 28 skin A hair B beard B -- ok
  focus 11 page 640  team 22   number 2    section 46  L, 17 prim(s), CLUT (32,480): skin A hair B beard -
           record 507 (slot 1) A-L3-B-A-A: section 46 skin A hair B beard A -- ok
  focus 12 page 640  team 22   number 1    section 24  A, 12 prim(s), CLUT (32,480): skin A hair B beard -
           record 506 (slot 0) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 13 page 576  team 41   number 9    section 34  I, 9 prim(s), CLUT (16,480): skin A hair A beard -
           record 953 (slot 10) A-I1-A-A-A: section 34 skin A hair A beard A -- ok
  focus 14 page 576  team 41   number 11   section 34  I, 11 prim(s), CLUT (16,483): skin D hair A beard -
           record 952 (slot 9) D-I3-A-A-A: section 34 skin D hair A beard A -- ok
  focus 15 page 576  team 41   number 10   section 34  I, 13 prim(s), CLUT (16,482): skin C hair A beard -
           record 951 (slot 8) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 16 page 576  team 41   number 2    section 34  I, 10 prim(s), CLUT (16,482): skin C hair A beard -
           record 950 (slot 7) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 17 page 576  team 41   number 6    section 32  K, 10 prim(s), CLUT (32,482): skin C hair B beard -
           record 949 (slot 6) C-K1-B-A-A: section 32 skin C hair B beard A -- ok
  focus 18 page 576  team 41   number 16   section 34  I, 9 prim(s), CLUT (16,482): skin C hair A beard -
           record 948 (slot 5) C-I1-A-B-A: section 34 skin C hair A beard A -- ok
  focus 19 page 576  team 41   number 7    section 34  I, 10 prim(s), CLUT (16,482): skin C hair A beard -
           record 947 (slot 4) C-I1-A-A-B: section 34 skin C hair A beard B -- ok
  focus 20 page 576  team 41   number 4    section 34  I, 10 prim(s), CLUT (16,483): skin D hair A beard -
           record 946 (slot 3) D-I1-A-A-A: section 34 skin D hair A beard A -- ok
  focus 21 page 576  team 41   number 3    section 34  I, 13 prim(s), CLUT (16,482): skin C hair A beard -
           record 945 (slot 2) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 22 page 576  team 41   number 5    section 24  A, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 944 (slot 1) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 23 page 576  team 41   number 1    section 34  I, 9 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
22 of 22 distinct player(s) match their disc record
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-10-capture.json --player all
  focus 0  page 576  team 41   number 1    section 34  I, 10 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 1  page 576  team 41   number 1    section 34  I, 10 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 2  page 640  team 22   number 20   section 46  L, 18 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 516 (slot 10) A-L3-B-A-B: section 46 skin A hair B beard B -- ok
  focus 3  page 640  team 22   number 11   section 46  L, 15 prim(s), CLUT (128,480): skin A hair H beard -
           record 515 (slot 9) A-L3-H-A-A: section 46 skin A hair H beard A -- ok
  focus 4  page 640  team 22   number 10   section 24  A, 11 prim(s), CLUT (32,480): skin A hair B beard -
           record 514 (slot 8) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 5  page 640  team 22   number 8    section 47  L twin, 17 prim(s), CLUT (128,480) (176,480): skin A hair H beard C
           record 513 (slot 7) A-L3-H-F-C: section 47 skin A hair H beard C -- ok
  focus 6  page 640  team 22   number 7    section 34  I, 11 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 512 (slot 6) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
  focus 7  page 640  team 22   number 3    section 24  A, 9 prim(s), CLUT (32,480): skin A hair B beard -
           record 511 (slot 5) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 8  page 640  team 22   number 4    section 34  I, 9 prim(s), CLUT (32,480): skin A hair B beard -
           record 510 (slot 4) A-I2-B-A-B: section 34 skin A hair B beard B -- ok
  focus 9  page 640  team 22   number 14   section 24  A, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 509 (slot 3) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 10 page 640  team 22   number 5    section 28  G, 9 prim(s), CLUT (32,480): skin A hair B beard -
           record 508 (slot 2) A-G1-B-A-B: section 28 skin A hair B beard B -- ok
  focus 11 page 640  team 22   number 2    section 46  L, 17 prim(s), CLUT (32,480): skin A hair B beard -
           record 507 (slot 1) A-L3-B-A-A: section 46 skin A hair B beard A -- ok
  focus 12 page 640  team 22   number 1    section 24  A, 10 prim(s), CLUT (32,480): skin A hair B beard -
           record 506 (slot 0) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 13 page 576  team 41   number 9    section 34  I, 9 prim(s), CLUT (16,480): skin A hair A beard -
           record 953 (slot 10) A-I1-A-A-A: section 34 skin A hair A beard A -- ok
  focus 14 page 576  team 41   number 11   section 34  I, 10 prim(s), CLUT (16,483) (144,483): skin D hair A beard A
           record 952 (slot 9) D-I3-A-A-A: section 34 skin D hair A beard A -- ok
  focus 15 page 576  team 41   number 10   section 34  I, 10 prim(s), CLUT (16,482): skin C hair A beard -
           record 951 (slot 8) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 16 page 576  team 41   number 2    section 34  I, 10 prim(s), CLUT (16,482): skin C hair A beard -
           record 950 (slot 7) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 17 page 576  team 41   number 6    section 32  K, 12 prim(s), CLUT (32,482) (144,482): skin C hair B beard A
           record 949 (slot 6) C-K1-B-A-A: section 32 skin C hair B beard A -- ok
  focus 18 page 576  team 41   number 16   section 34  I, 10 prim(s), CLUT (16,482): skin C hair A beard -
           record 948 (slot 5) C-I1-A-B-A: section 34 skin C hair A beard A -- ok
  focus 19 page 576  team 41   number 7    section 34  I, 11 prim(s), CLUT (16,482) (160,482): skin C hair A beard B
           record 947 (slot 4) C-I1-A-A-B: section 34 skin C hair A beard B -- ok
  focus 20 page 576  team 41   number 4    section 34  I, 11 prim(s), CLUT (16,483): skin D hair A beard -
           record 946 (slot 3) D-I1-A-A-A: section 34 skin D hair A beard A -- ok
  focus 21 page 576  team 41   number 3    section 34  I, 12 prim(s), CLUT (16,482): skin C hair A beard -
           record 945 (slot 2) C-I1-A-A-A: section 34 skin C hair A beard A -- ok
  focus 22 page 576  team 41   number 5    section 24  A, 11 prim(s), CLUT (32,480) (144,480): skin A hair B beard A
           record 944 (slot 1) A-A1-B-A-A: section 24 skin A hair B beard A -- ok
  focus 23 page 576  team 41   number 1    section 34  I, 10 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
22 of 22 distinct player(s) match their disc record
```

O `--json` das duas corridas (`… --player all --json`) traz `"schema": "kits-replay/1"`, `match` 22 e `players` 22. As chaves de topo são `capture match plant player players rows schema`, e as de cada linha `disc expected failures k number page primitives reading record slot team`.

As três de perto. A tabela de [(a)](/docs/KITS-REPLAYS-9-10.md#a-cabelo-barba-e-pele-do-jogador-vêm-da-clut-da-cabeça-pela-regra-da-looks-set) diz: Bokšić 46 (128,480) → pele A, cabelo H; Balaban 46 (32,480) e (160,480) → A, cabelo B, barba B; Marcos 34, as mesmas duas. As três batem:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-9-3.json --player all
  up close page 640  team 22   number 11   section 46  L, 14 prim(s), CLUT (128,480): skin A hair H beard -
           record 515 (slot 9) A-L3-H-A-A: section 46 skin A hair H beard A -- ok
1 of 1 distinct player(s) match their disc record
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-10-2.json --player all
  up close page 640  team 22   number 20   section 46  L, 18 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 516 (slot 10) A-L3-B-A-B: section 46 skin A hair B beard B -- ok
1 of 1 distinct player(s) match their disc record
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-9.json --player all
  up close page 576  team 41   number 1    section 34  I, 9 prim(s), CLUT (32,480) (160,480): skin A hair B beard B
           record 943 (slot 0) A-I1-B-A-B: section 34 skin A hair B beard B -- ok
1 of 1 distinct player(s) match their disc record
```

Controle do confronto: o registro do Balaban (516) contra a cabeça do Bokšić falha, e a corrida sai 1:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-9-3.json --player 516
  up close page 640  team 22   number 11   section 46  L, 14 prim(s), CLUT (128,480): skin A hair H beard -
           record 516 (slot None) A-L3-B-A-B: section 46 skin A hair B beard B -- hair colour H, not B
0 of 1 distinct player(s) match their disc record
exit=1
```

O gate, e a planta que troca a coluna do cabelo, com dado real (K2). A planta dá `kits_replay: 70 failure(s)`, uma por linha `head of …` das sete capturas:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check work/kits-oracle
  ok    HEAD_EXPECT: the disc records the 22 players' looks it says
  ok    replay-9.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1; every head reads its player's HEAD_EXPECT
  ok    replay-9-3.json: root 2 head 46 armband 90 for 4, still 0, panel [640, 60, 104] number 11; every head reads its player's HEAD_EXPECT
  ok    replay-10.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1; every head reads its player's HEAD_EXPECT
  ok    replay-10-2.json: root 2 head 46 armband None for None, still 0, panel [640, 80, 104] number 20; every head reads its player's HEAD_EXPECT
  ok    replay-10-3.json: root 2 head 46 armband 93 for 97, still 0, panel [640, 60, 104] number 11; every head reads its player's HEAD_EXPECT
  ok    replay-field-9-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed; every head reads its player's HEAD_EXPECT
  ok    replay-field-10-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed; every head reads its player's HEAD_EXPECT
kits_replay: 0 failure(s)
exit=0
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check work/kits-oracle --plant-hair-column
  ok    HEAD_EXPECT: the disc records the 22 players' looks it says
  FAIL  replay-9.json: head of up close, team 41 number 1: hair colour C, not B
  FAIL  replay-9.json: head of up close, team 41 number 1: beard colour C, not B
  FAIL  replay-9-3.json: head of up close, team 22 number 11: hair colour none, not H
...
  FAIL  replay-field-10-capture.json: head of focus 0, team 41 number 1: hair colour C, not B
  FAIL  replay-field-10-capture.json: head of focus 0, team 41 number 1: beard colour C, not B
...
kits_replay: 70 failure(s)
exit=1
```

Negativa: nenhuma. O que não se julga é a barba de uma cabeça cuja vista não amostra a coluna da barba (Bokšić, os dois slots). Está escrito no §3.1, e não é falha da regra.

Gates, na HEAD do código entregue:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  302.15 sec
2/5 Test #19: kits_image .......................   Passed   27.50 sec
3/5 Test #20: kits_gen .........................   Passed    0.02 sec
4/5 Test #21: kits_ui ..........................   Passed  212.38 sec
5/5 Test #22: kits_replay ......................   Passed   12.49 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
  RED    replay-head-hair-column      kits/core/replay.py :: head_reading
  RED    replay-head-twin-unasked     kits/core/replay.py :: head_expected
  RED    replay-head-squad-unbiased   kits/replay.py :: squad_numbers
controls: 73 of 73 red
```
