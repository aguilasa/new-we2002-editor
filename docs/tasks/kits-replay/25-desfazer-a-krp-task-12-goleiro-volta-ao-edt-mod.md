---
id: KRP-TASK-25
---

# KRP-TASK-25 — Desfazer a KRP-TASK-12: o goleiro volta ao do EDT_MOD.BIN, com a 92 trocada

## Goal

A figura 1 da aba e do CLI volta a ser o goleiro de antes da [KRP-TASK-12](/docs/tasks/kits-replay/12-goleiro-pela-familia-13-com-a-pose-medida-e-a-92.md): o do `EDT_MOD.BIN`, com só a 92 trocada quando capitão, vestido pelo `arm_dress`. O código que o commit `e4b2535e` trouxe sai — `keeper_scene`, `keeper_order`, `core/keeper_pose.json`, a linha `order` do `cli.py figure`, o juízo `family_judge` e a planta dele, o controle `figure-keeper-armband-always` —, e o §4 do plano diz, datado, que a família 13 foi desfeita.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/core/keeper_pose.json` (removido)
  - `tools/kits/cli.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§4: a reversão datada; o texto do "Feito" da KRP-TASK-12 fica, marcado como desfeito)
- Out:
  - a linha "Feito na fase 4" do §4 e o fechamento da fase (KRP-TASK-26)
  - o link `#3.3` da CORR-KRP-027, que a KRP-TASK-13 consertou: o conserto fica
  - a regra da cabeça e a pele do corpo da KRP-TASK-24 no goleiro do `EDT_MOD.BIN`: voltam ao que eram antes da KRP-TASK-12, não mudam

## Done criteria

- [x] `git diff e4b2535e^ -- tools/kits/core/figure.py tools/kits/cli.py tools/kits/ui_check.py` vazio, ou cada linha que sobra justificada no Log (por exemplo um conserto de uma task posterior que toca o mesmo trecho)
- [x] `test ! -e tools/kits/core/keeper_pose.json` e `grep -rn "keeper_scene\|keeper_order\|keeper_pose" tools/kits` vazio
- [x] `cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B`, com e sem `--armband`: digest igual ao da árvore de `e4b2535e^`, as duas corridas coladas no Log
- [x] `cli.py figure --tag 22` e `--tag 22 --match --set 1`: digest igual antes e depois desta task (o `match_scene` não muda)
- [x] `replay.py confront <captura> --tab` e `--tab --player`, no Marcos dos slots 9 e 10 (`work/kits-replay/tab/replay-{9,10}-R1.json`), colados da HEAD no Log: os números do lado "antes" do Log da KRP-TASK-12 (registra número, não afirma limite)
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, sem `figure-keeper-armband-always` no catálogo
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] o §4 do plano diz, datado, que a família 13 foi desfeita por decisão do usuário

## Notes

Decisão do usuário (2026-10-18): desfazer as KRP-TASK-12 e 13, numa fase 4a depois da 4.

O ponto de partida é `git revert e4b2535e` — o único commit de código da KRP-TASK-12; depois dele, só `87dc98a6` (KRP-TASK-13) tocou o plano. O revert não pode levar o arquivo da task 12 nem o `progress.json`: tasks fechadas ficam como estão, e o estado só muda pelo `rite`. Ao rodar, confira o que a KRP-TASK-14 mudou nos mesmos arquivos (`controls.py`, `selftest.py`), que estava em andamento quando esta task foi criada.
## Log de Execução

- **done** (2026-10-19): `git revert --no-commit e4b2535e`, com `PLAN-KITS-REPLAY.md`, o arquivo da KRP-TASK-12, `progress.json` e `progresso.md` devolvidos à HEAD (`git checkout HEAD -- …`): o revert entrou em conflito nos dois `.md`, e os de estado só mudam pelo `rite`. `controls.py` e `selftest.py` fundiram sozinhos com o que a KRP-TASK-14 acrescentou depois. O §4 ganhou a reversão datada, à mão, e o "Feito" da KRP-TASK-12 ficou, marcado "Feito, e desfeito depois".

```
$ git diff e4b2535e^ -- tools/kits/core/figure.py tools/kits/cli.py tools/kits/ui_check.py
(vazio)
$ test ! -e tools/kits/core/keeper_pose.json && echo gone; grep -rn "keeper_scene\|keeper_order\|keeper_pose" tools/kits; echo "grep exit=$?"
gone
grep exit=1
```

`cli.py figure`, na árvore de `e4b2535e^` (worktree) e na de trabalho, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`; as duas dão a mesma linha:

```
$ python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B
set 1 figure 1  634 parts, 634 textured, 9 surfaces, bounds (-113,-33,-281)..(60,420,27)  a9f61e7f06e24aab1b6634fbf936ea4d68b416ded8eb0b8a399c7d84b6e122b5
$ python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B --armband
set 1 figure 1  634 parts, 634 textured, 9 surfaces, bounds (-113,-33,-281)..(60,420,27)  a9f61e7f06e24aab1b6634fbf936ea4d68b416ded8eb0b8a399c7d84b6e122b5
```

(Com e sem `--armband` o digest é o mesmo, como em `e4b2535e^`: antes da KRP-TASK-12 a opção não chegava às figuras da aba.) Na HEAD antes desta task eram `4d1c0a5d…` e `d4e66c01…`, a família 13.

`--tag 22` e `--tag 22 --match --set 1`, HEAD antes (worktree) e árvore de trabalho: figura 0 dos dois conjuntos e `match_scene` iguais; a figura 1 muda, porque é o goleiro, e volta ao digest de `e4b2535e^`:

```
$ python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  9b136766e64f5bc1ae1b961002014bdc5e1e2bbf3f7fa39cb9fbf338afaa96ec
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  aab125ff5eb9f7d40d8498fb4c4aec868d86745a2d53ba9301ca83477794726c
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  e32b14c8e91bed5efa8d0c514780689f4e7f049b647182e27265faa9ed6a8ca6
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  c3d349fdd92419692989e849617d158465f656e6e65b721e77c442901a24a6dd
$ python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --match --set 1
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  a68ac8aca6428b0d2fdb5daa6f2c066bbe383e853dc562d85347f57ee01fa97b
```

(Na HEAD antes: figura 1 `36b17876…` e `1ef3b3a2…`; figura 0 e `match_scene` com os mesmos digests de acima.)

`confront --tab` no Marcos, árvore de trabalho; os oito números são os do lado "antes" do Log da KRP-TASK-12:

```
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --out work/krp25/tab
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.501, 0.670 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.403, 0.720 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out work/krp25/tab
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --out work/krp25/tab
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.499, 0.677 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.557, 0.739 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --player --out work/krp25/tab
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.497, 0.667 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.562, 0.744 over the colours the tab draws
```

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  363.12 sec
2/5 Test #19: kits_image .......................   Passed   29.06 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  262.30 sec
5/5 Test #22: kits_replay ......................   Passed   12.09 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 87 of 87 red
$ python3 tools/kits/controls.py --list | grep -c keeper-armband-always
0
```
- **Closed** — commit `afbcf78c` (2026-10-19): revert(kits): draw the goalkeeper from EDT_MOD.BIN again, undoing family 13
  - Files (`git show --name-status afbcf78c`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/25-desfazer-a-krp-task-12-goleiro-volta-ao-edt-mod.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/figure.py`
    - `D tools/kits/core/keeper_pose.json`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui_check.py`
