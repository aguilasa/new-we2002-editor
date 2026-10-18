---
id: KRP-TASK-12
---

# KRP-TASK-12 — Goleiro pela família 13, com a pose medida e a 92

## Goal

A figura de goleiro da aba e do CLI é a família 13 do `MODEL.BIN` (torso 13, braços 14/16 e 15/17, pernas 18/20/19/21, a 11, cabeça do jogador), com a 92 no lugar da 15 quando capitão, posada pela pose de `work/kits-pose/slot9-keeper-front.json` promovida a arquivo versionado do núcleo. A reabertura da K3D-TASK-10 fica escrita datada no plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/core/keeper_pose.json` (novo, a pose promovida)
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§4)
- Out:
  - a pose de corrida (KRP-TASK-15)
  - faixa e manga do jogador de linha

## Done criteria

- [x] a ordem de seções desenhada do goleiro é `34 13 14 16 92 17 18 20 11 19 21` com faixa e com a 15 no lugar da 92 sem, como o [item 3](/docs/KITS-REPLAYS-9-10.md#3); impressa por uma opção versionada
- [x] nenhum UV ou vértice escrito à mão: toda seção vem do `MODEL.BIN` (grep no diff, e o Log diz de onde)
- [x] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite), no Marcos dos slots 9 e 10
- [x] o `kits_ui` cobre o goleiro novo com uma planta (o corpo do `EDT_MOD.BIN` de volta fica vermelho)
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Decisão do usuário (2026-10-12): implementar. A pose sai de `work/` para o núcleo com o digest no Log.

## Log de Execução

- **done** (2026-10-18): a figura 1 da aba e do CLI é o goleiro de partida, `core/figure.py:keeper_scene`, e o §4 do plano diz o que entrou, com a reabertura da K3D-TASK-10 datada.

A pose promovida, byte a byte:

```
$ cp work/kits-pose/slot9-keeper-front.json tools/kits/core/keeper_pose.json
$ sha256sum work/kits-pose/slot9-keeper-front.json tools/kits/core/keeper_pose.json
062ccf003561dbbb383581519cdb6b8e70bb03538b76df0d2f4cf6e062f24c27  work/kits-pose/slot9-keeper-front.json
062ccf003561dbbb383581519cdb6b8e70bb03538b76df0d2f4cf6e062f24c27  tools/kits/core/keeper_pose.json
```

A ordem desenhada, impressa pelo `cli.py figure` (a linha `order` é nova) e afirmada no `kits_image` (`_keeper_image_checks`, constante `KEEPER_ORDER`, K1):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B
set 1 figure 1  140 parts, 140 textured, 6 surfaces, bounds (-119,-296,-195)..(125,131,47)  4d1c0a5da9c46f72f33171c6b26cc9d991ba5e830fd26a834e2965a309e8e4eb  head 34: (32,480)x20 (160,480)x3
  order 34 13 14 16 15 17 18 20 11 19 21
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B --armband
set 1 figure 1  140 parts, 140 textured, 7 surfaces, bounds (-119,-296,-195)..(125,131,47)  d4e66c0103fb709e6f9c92af7f137d44819ddfa3a81e43ab6f08fba48baf9783  head 34: (32,480)x20 (160,480)x3
  order 34 13 14 16 92 17 18 20 11 19 21
```

De onde vem cada seção: `keeper_scene` lê os números da pose, troca só 92 e 15 (`keeper_order`) e desenha cada um pelo `_model_scene`, que pega vértices e primitivas de `section.scan(geometry[layout.MODEL], …)` e texturiza pelo `_model_part`, como o `match_scene`. O `match_scene` passou a usar o mesmo `_model_scene`, com o digest igual antes e depois nas três variantes (sem jogador, com o Balaban, e com o Bokšić de manga curta e faixa). Nada escrito à mão; o grep das linhas novas que tocam geometria acha só o laço sobre `one.vertices` da seção lida:

```
$ git diff -U0 -- tools/kits/core/figure.py | grep '^+' | grep -nE "texcoords|uvs?\b|\.vertices|_Vertex\(|points"
112:+        for v in one.vertices:
117:+            moved.append(_Vertex(*p))
```

A pele do corpo (KRP-TASK-24) continua seguindo a do jogador no goleiro novo. A regra é `player_body_clut`: coluna 0 para a linha da pele, colunas 1 e 9 pela regra da cabeça. Ela vem do laço do slot 9 (sondado nesta task), e no Marcos de perto confere:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9.json --section 13 --json   # .section.cluts
[[0, 488], [32, 480]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9.json --section 18 --json   # .section.cluts
[[0, 480], [0, 488]]
```

A checagem da KRP-TASK-24 no `kits_image` excluía tudo do MODEL.BIN para separar a cabeça. Passou a excluir só a seção da cabeça, e no goleiro dá `18 of 117 body primitive(s) move, by [3] row(s)`.

`confront --tab` antes (worktree limpo da HEAD `e74e2fd6`) e depois, no Marcos dos slots 9 e 10 (capturas com os dois buffers, `work/kits-replay/tab/`). Registra número, não afirma limite: a frente sobe uns 0,03 nos dois slots, e as costas ficam iguais ou caem até 0,019.

```
$ (worktree da HEAD e74e2fd6) python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --out work/krp12/tab-before
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.501, 0.670 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.403, 0.720 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --out work/krp12/tab-after
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.532, 0.671 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.397, 0.717 over the colours the tab draws
$ (worktree da HEAD e74e2fd6) python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out work/krp12/tab-before
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out work/krp12/tab-after
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.531, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.404, 0.699 over the colours the tab draws
$ (worktree da HEAD e74e2fd6) python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --out work/krp12/tab-before
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.499, 0.677 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.557, 0.739 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --out work/krp12/tab-after
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.525, 0.680 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.555, 0.731 over the colours the tab draws
$ (worktree da HEAD e74e2fd6) python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --player --out work/krp12/tab-before
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.497, 0.667 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.562, 0.744 over the colours the tab draws
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-R1.json --tab --player --out work/krp12/tab-after
  tab front (yaw 180) against the game's front capture: 4746 px, histogram intersection 0.524, 0.674 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 4642 px, histogram intersection 0.543, 0.710 over the colours the tab draws
```

Figura 0 e `match_scene` sem jogador: digest igual antes e depois (`cli.py figure --tag 22 --figure 0` e `--match --set 1`).

Plantas:

- `kits_ui`: o juízo `family_judge` mede o contorno do goleiro de frente. Deu 194 x 343 px, proporção 0,566 (antes da task, 132 x 343, 0,385), e o limite é 0,5. A planta "the goalkeeper of EDT_MOD.BIN back" o derruba. A planta antiga "goalkeeper's armband ignored" passou a mirar o `keeper_order`, porque o goleiro não passa mais pelo `arm_dress`.
- `controls.py`: `figure-keeper-armband-always`.

Lacuna escrita no §4: a pose medida tem uma chuteira só (11), e a segunda não se inventa.

O `kits_ui` nesta árvore (`DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py`, linhas cortadas em 260 colunas):

```
  ok    3D TEX_41: the goalkeeper is the match one, family 13, his silhouette from the front at least 0.50 as wide as tall (194 x 343 px, 0.566)
        plant 'goalkeeper's armband ignored': figure 1: Captain armband ticked draws the same back as unticked, with nothing else; figure 1: Captain armband ticked draws the same back as unticked, with Number
  ok    plant 'goalkeeper's armband ignored' fails the dressing judge
        plant 'the goalkeeper of EDT_MOD.BIN back': the goalkeeper from the front is 132 x 343 px, 0.385, under 0.50: the LOOKS SET figure, not the match one
  ok    plant 'the goalkeeper of EDT_MOD.BIN back' fails the match goalkeeper judge
kits_ui: 0 failure(s)
```

Na primeira corrida dos gates, dois controles antigos quebraram (`matched 2x`, `matched 0x`), porque as linhas que eles plantam mudaram: `figure-player-skin-unmoved`, cuja linha passou a existir também no `player_body_clut`, e `figure-match-player-clut`, cujo laço foi para o `_model_scene`. Os literais foram ajustados, e os dois voltaram a `RED`.

Gates, na árvore entregue:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  333.55 sec
2/5 Test #19: kits_image .......................   Passed   28.29 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  258.27 sec
5/5 Test #22: kits_replay ......................   Passed   11.74 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
  RED    figure-keeper-armband-on-the-player-arm kits/core/figure.py :: arm_dress
  RED    figure-keeper-armband-always kits/core/figure.py :: keeper_order
controls: 82 of 82 red
```
- **Closed** — commit `e4b2535e` (2026-10-18): feat(kits): draw the goalkeeper as the match one, family 13 of MODEL.BIN
  - Files (`git show --name-status e4b2535e`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/12-goleiro-pela-familia-13-com-a-pose-medida-e-a-92.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/figure.py`
    - `A tools/kits/core/keeper_pose.json`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui_check.py`
