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
(`work/krp02/after/*.txt`, KRP-TASK-02), com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`:

```
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-9.json --json
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-10.json --json
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --json
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-10-3.json --json
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --json
(campos schema, figure.root, figure.head, figure.armband, figure.replaces, still, turned, panel.panel, panel.number)
replay-9 kits-replay/1 root 13 head 34 armband 92 replaces 15 still 0 turned back panel [576, 100, 104] number 1
replay-10 kits-replay/1 root 13 head 34 armband 92 replaces 15 still 0 turned back panel [576, 100, 104] number 1
replay-9-3 kits-replay/1 root 2 head 46 armband 90 replaces 4 still 0 turned back panel [640, 60, 104] number 11
replay-10-3 kits-replay/1 root 2 head 46 armband 93 replaces 97 still 0 turned back panel [640, 60, 104] number 11
replay-10-2 kits-replay/1 root 2 head 46 armband None replaces None still 0 turned back panel [640, 80, 104] number 20
```

Linhas `ok` do oracle: `opens at section 13 with head 34, draws 92 in place of 15, holds still,
… panel (576, 100, 104) with number 1` (9 e 10); `section 2 with head 46, draws 90 in place of 4,
… (640, 60, 104) with number 11` (9-3); `draws 93 in place of 97, … (640, 60, 104) with number
11` (10-3); `draws no armband, … (640, 80, 104) with number 20` (10-2). Campo a campo iguais.

```
$ python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 90 --json
(campo section) {'cluts': [[0, 487]], 'error': 0.9345334053996881, 'far': 2.265486725663717, 'far_shaded': 2.5486725663716814, 'matched': 2, 'n': 2, 'pages': [[640, 256]], 'raw': 0, 'section': 90, 'semi': 0, 'shaded': 0, 'zones': ['armband, short sleeve', 'short sleeve, left, captain', 'short sleeve, left, captain, under the armband']}
```

Bate com a linha `90:` do `oracle.py --replay 9 --focus 3` (`2 prim(s), 0 shaded, 0 raw, 0 semi;
CLUT (0,487); page (640,256)`, far 2.27 e 2.55) e com o item 4 do relatório.

```
$ python3 tools/kits/replay.py walk work/kits-oracle/replay-field-9-capture.json --json
(schema, foci, follows) kits-replay/1 25 {'goalkeeper': 2, 'other': 0, 'outfield': 20}
(k head root armband panel number)
0 34 13 92 None None    1 34 13 92 None None    2 46 2 None [640, 80, 104] 20
3 46 2 90 [640, 60, 104] 11    4 24 2 None [640, 40, 104] 10    5 47 2 None [640, 20, 104] 8
6 34 2 None [640, 0, 104] 7    7 24 2 None [640, 80, 80] 3    8 34 2 None [640, 60, 80] 4
9 24 2 None [640, 40, 80] 14    10 28 2 None [640, 20, 80] 5    11 46 2 None [640, 0, 80] 2
12 24 13 None [640, 100, 104] 1    13 34 2 None [576, 80, 104] 9    14 34 2 None [576, 60, 104] 11
15 34 2 None [576, 40, 104] 10    16 34 2 None [576, 20, 104] 2    17 32 2 None [576, 0, 104] 6
18 34 2 None [576, 80, 80] 16    19 34 2 None [576, 60, 80] 7    20 34 2 None [576, 40, 80] 4
21 34 2 None [576, 20, 80] 3    22 24 2 None [576, 0, 80] 5    23 34 13 92 None None
24 34 13 92 None None (end ball)
```

Linha a linha a tabela do item 7 (cabeça, raiz, faixa, painel, número), 20 de linha e 2 goleiros
seguidos.

`kits_replay`:

```
$ env -u WE2002_KITS_REPLAY_DIR WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_replay
1/1 Test #22: kits_replay ......................***Skipped   0.05 sec
$ WE2002_KITS_REPLAY_DIR=<pasta com replay-10-3.json no lugar de replay-10-2.json> WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_replay --output-on-failure
1/1 Test #22: kits_replay ......................***Failed    7.91 sec
  FAIL  <pasta>/replay-10-2.json has sha256 d362901327da8d5efba910f6f456cbb357fb19eb53807751751a401c1fe6ace8, not the e9b785b2a6cf80029293fbbd20fc873eeeeebe919d6e08cc11ef03e0928d2a7b it was kept with
kits_replay: 1 failure(s)
```

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
