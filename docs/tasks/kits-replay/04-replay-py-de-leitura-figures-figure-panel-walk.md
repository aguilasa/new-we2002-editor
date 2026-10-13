---
id: KRP-TASK-04
---

# KRP-TASK-04 — replay.py de leitura: figures, figure, panel, walk e describe com --json kits-replay/1, e o alvo kits_replay

## Goal

Existe a linha de comando `tools/kits/replay.py` com os leitores `figures`, `figure [--on-axis|--nearest|--nth N] [--section S]`, `panel`, `walk` e `describe`, todos com `--json` no schema `kits-replay/1`, e o alvo `ctest` `kits_replay` do [§2.6](/docs/PLAN-KITS-REPLAY.md#2.6).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (novo)
  - `tools/kits/core/replay.py`
  - `tests/CMakeLists.txt` (alvo `kits_replay`)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (o §2.6 dizia uma pasta default que o critério de 77 contradiz)
- Out:
  - `show`, `confront` (KRP-TASK-05/06)
  - `capture` (KRP-TASK-07)

## Done criteria

- [x] `python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --json`: o objeto tem `"schema": "kits-replay/1"` e reproduz campo a campo a linha `ok` de `oracle.py --replay 9 --focus 3 --frame-json …` (raiz 2, cabeça 46, faixa 90 no lugar da 4, pose parada, painel (640, 60, 104), número 11); o mesmo nas outras quatro capturas de perto, cada `$` no Log
- [x] `replay.py figure work/kits-oracle/replay-9-3.json --section 90 --json` devolve a seção 90 com CLUT (0,487) e página (640,256), como o [item 4](/docs/KITS-REPLAYS-9-10.md#4)
- [x] `replay.py walk work/kits-oracle/replay-field-9-capture.json --json` devolve os 25 focos da tabela do [item 7](/docs/KITS-REPLAYS-9-10.md#7), com 20 de linha e 2 goleiros
- [x] `kits_replay` visto saindo 77 (*skipped*) sem `WE2002_KITS_REPLAY_DIR`, e vermelho com uma captura de digest trocado (planta no `controls.py`)
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

O schema é contrato com agente: chaves fixas, sem campo opcional que some. Saída humana curta por padrão. A contagem de alvos `kits` vive só no §9 do plano; ao criar o alvo, varra quem repetia "4/4" (perfil, plano) na mesma task.

## Log de Execução

### 2026-10-13

`tools/kits/replay.py`: `describe`, `figures`, `figure`, `panel`, `walk` e `check` (o gate). Todo
`--json` traz `"schema": "kits-replay/1"`; chave que não se aplica sai `null`, nunca some. No
núcleo, `core/replay.py` ganhou `model_index(image)` (o MODEL.BIN pelo `read_geometry` do
`core.figure`), `UNIFORM_WIDTH` (64, o registro 0 do `tex.EXPECTED_SHAPE`) como default de
largura de `Figure.panel` e `Walk`, `ARMBAND_REPLACES` (90→4 e 93→97 do `SLEEVE_LENGTHS`, 92→15)
e `Figure.replaces`; `Figure.panel` devolve também o painel lido (`read`: dígitos e pixels não
explicados), que o gate passa ao `panels_judge` do oracle. O `check` importa o oracle **por
caminho** (o `import oracle` acharia o da looks, que o `core.tex` põe primeiro no `sys.path`) e
julga com `REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT` e `REPLAY_IDLE` de lá: o esperado é a constante
do oracle, não a captura (K1).

As cinco capturas de perto, contra a linha `ok` do `oracle.py --replay … --frame-json`
(`work/krp02/after/*.txt`, KRP-TASK-02). Os blocos de saída daqui até a corrida vermelha do
`kits_replay` foram refeitos pela [CORR-KRP-005](/docs/tasks/kits-replay/CORR-KRP-005.md) em
2026-10-13: a versão anterior colava um resumo do `--json` tirado por um extrator que não estava no
Log e uma pasta placeholder. Agora é a saída humana dos próprios leitores, colada como saiu; ela é
impressa do mesmo documento que o `--json` emite com `"schema": "kits-replay/1"`.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9.json
work/kits-oracle/replay-9.json, nearest: goalkeeper 13, head 34, sleeves None, armband 92 for 15; still 0; depth 4681
  order 34 13 14 16 92 17 18 20 11 19 21
  panel [576, 100, 104] from the back capture, number 1
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10.json
work/kits-oracle/replay-10.json, nearest: goalkeeper 13, head 34, sleeves None, armband 92 for 15; still 0; depth 4682
  order 34 13 14 16 92 17 18 20 11 19 21
  panel [576, 100, 104] from the back capture, number 1
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json
work/kits-oracle/replay-9-3.json, on_axis: outfield 2, head 46, sleeves short, armband 90 for 4; still 0; depth 4694
  order 46 2 3 5 90 6 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-3.json
work/kits-oracle/replay-10-3.json, on_axis: outfield 2, head 46, sleeves long, armband 93 for 97; still 0; depth 4699
  order 46 2 95 96 93 98 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json
work/kits-oracle/replay-10-2.json, on_axis: outfield 2, head 46, sleeves long, armband None; still 0; depth 4699
  order 46 2 95 96 97 98 7 9 11 8 10
  panel [640, 80, 104] from the front capture, number 20
```

Linhas `ok` do oracle: `opens at section 13 with head 34, draws 92 in place of 15, holds still,
… panel (576, 100, 104) with number 1` (9 e 10); `section 2 with head 46, draws 90 in place of 4,
… (640, 60, 104) with number 11` (9-3); `draws 93 in place of 97, … (640, 60, 104) with number
11` (10-3); `draws no armband, … (640, 80, 104) with number 20` (10-2). Campo a campo iguais.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 90
work/kits-oracle/replay-9-3.json, on_axis: outfield 2, head 46, sleeves short, armband 90 for 4; still 0; depth 4694
  order 46 2 3 5 90 6 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
  section 90: 2 prim(s), 0 shaded, 0 raw, 0 semi; CLUT [[0, 487]]; page [[640, 256]]; error 0.9345334053996881
```

Bate com a linha `90:` do `oracle.py --replay 9 --focus 3` (`2 prim(s), 0 shaded, 0 raw, 0 semi;
CLUT (0,487); page (640,256)`) e com o item 4 do relatório.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py walk work/kits-oracle/replay-field-9-capture.json
   0  -      head 34   root 13   None  armband 92   panel None             number None
   1  -      head 34   root 13   None  armband 92   panel None             number None
   2  follow head 46   root 2    short armband None panel [640, 80, 104]   number 20
   3  follow head 46   root 2    short armband 90   panel [640, 60, 104]   number 11
   4  follow head 24   root 2    short armband None panel [640, 40, 104]   number 10
   5  follow head 47   root 2    short armband None panel [640, 20, 104]   number 8
   6  follow head 34   root 2    short armband None panel [640, 0, 104]    number 7
   7  follow head 24   root 2    short armband None panel [640, 80, 80]    number 3
   8  follow head 34   root 2    short armband None panel [640, 60, 80]    number 4
   9  follow head 24   root 2    short armband None panel [640, 40, 80]    number 14
  10  follow head 28   root 2    short armband None panel [640, 20, 80]    number 5
  11  follow head 46   root 2    short armband None panel [640, 0, 80]     number 2
  12  follow head 24   root 13   None  armband None panel [640, 100, 104]  number 1
  13  follow head 34   root 2    short armband None panel [576, 80, 104]   number 9
  14  follow head 34   root 2    short armband None panel [576, 60, 104]   number 11
  15  follow head 34   root 2    short armband None panel [576, 40, 104]   number 10
  16  follow head 34   root 2    short armband None panel [576, 20, 104]   number 2
  17  follow head 32   root 2    short armband None panel [576, 0, 104]    number 6
  18  follow head 34   root 2    short armband None panel [576, 80, 80]    number 16
  19  follow head 34   root 2    short armband None panel [576, 60, 80]    number 7
  20  follow head 34   root 2    short armband None panel [576, 40, 80]    number 4
  21  follow head 34   root 2    short armband None panel [576, 20, 80]    number 3
  22  follow head 24   root 2    short armband None panel [576, 0, 80]     number 5
  23  follow head 34   root 13   None  armband 92   panel None             number None
  24  ball   head 34   root 13   None  armband 92   panel None             number None
25 foci; followed {'outfield': 20, 'goalkeeper': 2, 'other': 0}
```

Linha a linha a tabela do item 7 (cabeça, raiz, faixa, painel, número), 20 de linha e 2 goleiros
seguidos.

`kits_replay`. Sem a variável sai 77 (*skipped*). A corrida vermelha monta uma pasta com as seis
capturas boas por symlink e põe a `replay-10-3.json` no lugar da `replay-10-2.json`; o `check` lê os
digests do `CAPTURES` do `replay.py` e recusa a trocada:

```
$ env -u WE2002_KITS_REPLAY_DIR WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_replay
Internal ctest changing into directory: /home/ingmar/desenvolvimento/github/new-we2002-editor/build
Test project /home/ingmar/desenvolvimento/github/new-we2002-editor/build
    Start 22: kits_replay
1/1 Test #22: kits_replay ......................***Skipped   0.05 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.05 sec

The following tests did not run:
	 22 - kits_replay (Skipped)
$ d=$(mktemp -d /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/krp-red.XXXXXX); echo $d
/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/krp-red.8kmdjo
$ for c in replay-9 replay-9-3 replay-10 replay-10-3 replay-field-9-capture replay-field-10-capture; do ln -s $PWD/work/kits-oracle/$c.json $d/$c.json; done
$ ln -s $PWD/work/kits-oracle/replay-10-3.json $d/replay-10-2.json
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check $d; echo "rc=$?"
  ok    replay-9.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1
  ok    replay-9-3.json: root 2 head 46 armband 90 for 4, still 0, panel [640, 60, 104] number 11
  ok    replay-10.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1
  FAIL  /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/krp-red.8kmdjo/replay-10-2.json has sha256 d362901327da8d5efba910f6f456cbb357fb19eb53807751751a401c1fe6ace8, not the e9b785b2a6cf80029293fbbd20fc873eeeeebe919d6e08cc11ef03e0928d2a7b it was kept with
  ok    replay-10-3.json: root 2 head 46 armband 93 for 97, still 0, panel [640, 60, 104] number 11
  ok    replay-field-9-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed
  ok    replay-field-10-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed
kits_replay: 1 failure(s)
rc=1
$ WE2002_KITS_REPLAY_DIR=$d WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_replay --output-on-failure
Internal ctest changing into directory: /home/ingmar/desenvolvimento/github/new-we2002-editor/build
Test project /home/ingmar/desenvolvimento/github/new-we2002-editor/build
    Start 22: kits_replay
1/1 Test #22: kits_replay ......................***Failed    7.65 sec
  ok    replay-9.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1
  ok    replay-9-3.json: root 2 head 46 armband 90 for 4, still 0, panel [640, 60, 104] number 11
  ok    replay-10.json: root 13 head 34 armband 92 for 15, still 0, panel [576, 100, 104] number 1
  FAIL  /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/krp-red.8kmdjo/replay-10-2.json has sha256 d362901327da8d5efba910f6f456cbb357fb19eb53807751751a401c1fe6ace8, not the e9b785b2a6cf80029293fbbd20fc873eeeeebe919d6e08cc11ef03e0928d2a7b it was kept with
  ok    replay-10-3.json: root 2 head 46 armband 93 for 97, still 0, panel [640, 60, 104] number 11
  ok    replay-field-9-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed
  ok    replay-field-10-capture.json: 25 foci, 20 outfield, 2 goalkeeper(s) followed
kits_replay: 1 failure(s)


0% tests passed, 1 tests failed out of 1

Total Test time (real) =   7.65 sec

The following tests FAILED:
	 22 - kits_replay (Failed)
Errors while running CTest
```

O `mktemp -d` vale com qualquer modelo; o caminho acima é o da corrida.

Planta no catálogo: `replay-digest-unasked` (`kits/replay.py :: digest_problem`, `if got !=
want:` vira `if False:`), contra o caso novo do selftest `replay.py: a capture with another digest
is refused`; `python3 tools/kits/controls.py --only replay-digest-unasked` dá `RED`.

O §2.6 do plano dizia "default `work/kits-oracle/`"; o critério pede 77 sem a variável, e um
default relativo pularia em silêncio no `ctest` (que roda de `build/tests`). O texto do §2.6 foi
alinhado ao critério, com o plano declarado nos arquivos. Varredura de "4/4", "4 alvos": só o §9
do plano, que já diz "5 depois", e transcrições de Log de tasks fechadas.

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  227.58 sec
2/5 Test #19: kits_image .......................   Passed   27.57 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  205.67 sec
5/5 Test #22: kits_replay ......................   Passed    7.73 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 57 of 57 red
```
- **Closed** — commit `28f0b702` (2026-10-13): feat(kits): replay.py readers with --json kits-replay/1, and kits_replay
  - Files (`git show --name-status 28f0b702`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tests/CMakeLists.txt`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/replay.py`
    - `A tools/kits/replay.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/replay.py`, `tools/kits/core/replay.py`, `tests/CMakeLists.txt`, `tools/kits/selftest.py`, `tools/kits/controls.py`, `docs/PLAN-KITS-REPLAY.md`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-13) at `81039436`: CORR-KRP-004, CORR-KRP-005
