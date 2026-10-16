---
id: KRP-TASK-10
---

# KRP-TASK-10 — Cabeça pela tupla do jogador no scene_of e no match_scene, no CLI e na aba

## Goal

`core/figure.py:scene_of` e `match_scene` aceitam a tupla do jogador no lugar de `TUPLE = assembly.CORPUS_REFERENCE`, e o CLI e a aba ganham a opção; a cabeça desenhada segue a regra medida na KRP-TASK-09, e só ela.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/core/api.py` (a opção chega à aba por ele)
  - `tools/kits/core/replay.py` (`head_expected` passa a usar a regra de seção do `figure.py`: um lugar só)
  - `tools/kits/replay.py` (`confront --tab` repassa a tupla do jogador da captura; `head --drawn` confronta o desenho com a captura)
  - `tools/kits/cli.py`
  - `tools/kits/ui/app.py`
  - `tools/kits/ui/i18n.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.2: o que entrou)
- Out:
  - o seletor de jogador real (KRP-TASK-17)
  - o goleiro (KRP-TASK-12)

## Done criteria

- [x] sem a opção, o digest da figura é o mesmo de antes da task (default `CORPUS_REFERENCE`)
- [x] com a tupla do Bokšić e a do Balaban, a seção da cabeça e a CLUT amostrada batem com as da captura (`replay.py figure … --section 46 --json`)
- [x] `replay.py confront <captura> --tab` antes e depois, nas capturas de perto que a task toca, colado da HEAD no Log (registra número, não afirma limite)
- [x] texto novo da aba nas duas línguas do `i18n.py`, e o `kits_ui` cobre a opção com uma planta
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Se a KRP-TASK-09 fechou só parte da regra, desenha-se só essa parte, e o resto fica no default — escrito no §3.2.

## Log de Execução

- **done** (2026-10-16): a cabeça do jogador entra pela regra da KRP-TASK-09, no `scene_of` e no `match_scene`, no CLI (`figure --player`) e na aba (caixa "Cabeça do jogador", `--player-looks`). A KRP-TASK-09 fechou a regra inteira, então nada fica no default por falta de medida. O §3.2 diz o que entrou. Arquivos além dos de início, declarados por `rite set --files`: `core/api.py`, `core/replay.py` (`head_expected` usa `figure.player_head_section`, uma regra só), `replay.py` (`head --drawn` e `confront --tab --player`) e o plano.

Sem a opção, o digest é o de antes. Mesmo comando na HEAD `abed4cd3` (worktree limpo) e na árvore da task, `diff` vazio:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  9b136766e64f5bc1ae1b961002014bdc5e1e2bbf3f7fa39cb9fbf338afaa96ec
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  aab125ff5eb9f7d40d8498fb4c4aec868d86745a2d53ba9301ca83477794726c
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  e32b14c8e91bed5efa8d0c514780689f4e7f049b647182e27265faa9ed6a8ca6
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  c3d349fdd92419692989e849617d158465f656e6e65b721e77c442901a24a6dd
figure 0: set 1 and set 2 differ
figure 1: set 1 and set 2 differ
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  a68ac8aca6428b0d2fdb5daa6f2c066bbe383e853dc562d85347f57ee01fa97b
$ diff work/krp10/digest-before.txt work/krp10/digest-after.txt && echo SAME
SAME
```

A seção e a CLUT da captura contra as do desenho (Bokšić na 9-3, Balaban na 10-2). O desenho põe toda primitiva da 46 na coluna do jogo. O CLI conta as 34 primitivas da seção, e as (144,480) e (160,480) são a coluna da barba. A (144,480) não aparece na captura 9-3, que só amostra a (128,480); a (160,480) aparece na 10-2 (refeito pela CORR-KRP-017, 2026-10-16; medição no fim deste Log).

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 46 --json
  section 46 n 14 cluts [[128, 480]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --section 46 --json
  section 46 n 18 cluts [[32, 480], [160, 480]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --set 1 --figure 0 --player A-L3-H-A-A
set 1 figure 0  609 parts, 609 textured, 8 surfaces, bounds (-113,-33,-281)..(65,422,27)  e5d692df0f923715f75b8b6cc46150e09fbe9b3532eeb6c7b1a84bfe0017567a  head 46: (128,480)x31 (144,480)x3
$ ... --match --player A-L3-H-A-A
set 1 match figure, long sleeves: order 46 2 95 96 97 98 7 9 11 8 10 12  156 parts, 156 textured, 8 surfaces  b9a58f519e61687c5c05d76873a92ca070eadae221f00681f204d3d2a21a2ebe  head 46: (128,480)x31 (144,480)x3
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --set 1 --figure 0 --player A-L3-B-A-B
set 1 figure 0  609 parts, 609 textured, 9 surfaces, bounds (-113,-33,-281)..(65,422,27)  7134cd784e48c706f6a73f1c4100d5f07777ec140587b8347a727c21374f44c7  head 46: (32,480)x31 (160,480)x3
$ ... --match --player A-L3-B-A-B
set 1 match figure, long sleeves: order 46 2 95 96 97 98 7 9 11 8 10 12  156 parts, 156 textured, 8 surfaces  47ccd0e78d2415980efe4c0e2282ad99306f7e6650f82d91ef8f226637720795  head 46: (32,480)x31 (160,480)x3
```

Primitiva a primitiva, desenho contra jogo (`replay.py head --drawn`): as três de perto dão `1 of 1 drawn head(s) sample the game's CLUT on every primitive`, e os laços dão:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-9-capture.json --drawn
24 of 24 drawn head(s) sample the game's CLUT on every primitive
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head work/kits-oracle/replay-field-10-capture.json --drawn
24 of 24 drawn head(s) sample the game's CLUT on every primitive
```

`confront --tab` antes (sem `--player`, a cabeça de referência) e depois (`--player`), nas três de perto refeitas com os dois buffers pela KRP-TASK-06 (`work/kits-replay/tab/`). Nas capturas de `work/kits-oracle/` um dos lados não tem buffer e sai com 0 px. Registra número, não afirma limite:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.439, 0.612 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.406, 0.666 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab --player
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.442, 0.668 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.439, 0.748 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.326, 0.476 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.393, 0.569 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab --player
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.335, 0.521 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.424, 0.636 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.501, 0.670 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.403, 0.720 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
```

A interseção sobe em 5 dos 6 lados medidos; no Marcos de frente (9-R1, yaw 180) fica igual (0,501 → 0,500), e isso ainda não tem explicação: a cabeça de referência é a 24, nas colunas 1/9, e com `--player` a aba desenha a 34 com as CLUTs do jogo (refeito pela CORR-KRP-017, 2026-10-16; medição abaixo).

**Nota de 2026-10-16, refeita pela CORR-KRP-017.** As duas explicações acima foram reescritas porque a medição as desmentia. A frente parada do Marcos (0,501 → 0,500) **continua sem explicação**: não é que a cabeça já fosse a do jogo. A figura de referência do kit 41 desenha a seção 24 nas colunas 1/9; com a tupla do Marcos desenha a 34 nas colunas 2/10, que são as (32,480)/(160,480) do jogo. As figuras 0 e 1 dão o mesmo:

```
$ cd tools/kits && WE2002_LOOKS_IMAGE=$PWD/../../roms/japanese-shift-jis.bin python3 - <<'PY'
import os
from core import figure as F, api
geo=F.read_geometry(os.environ['WE2002_LOOKS_IMAGE'])
kit=api.open_source(os.environ['WE2002_LOOKS_IMAGE']).kit("41")
for fig in (0,1):
    for pl in (None,"A-I1-B-A-B"):
        s=api.figure(kit,1,fig,frame=api.FIGURE_POSE,geometry=geo,player=pl)
        c={}
        for p in s.parts:
            if p.file==F.layout.MODEL: k=(p.section,F.skin.grid(p.clut)); c[k]=c.get(k,0)+1
        print(fig, pl, c)
PY
0 None {(24, (480, 1)): 16, (24, (480, 9)): 2}
0 A-I1-B-A-B {(34, (480, 2)): 20, (34, (480, 10)): 3}
1 None {(24, (480, 1)): 16, (24, (480, 9)): 2}
1 A-I1-B-A-B {(34, (480, 2)): 20, (34, (480, 10)): 3}
```

A coluna da barba nas duas capturas de perto, sem `--json`. De cada saída fica só a linha da seção 46; as de `on_axis`, `order` e `panel` foram omitidas:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json --section 46
  section 46: 14 prim(s), 0 shaded, 0 raw, 0 semi; CLUT [[128, 480]]; page [[512, 256]]; error 0.9468100891177211
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json --section 46
  section 46: 18 prim(s), 0 shaded, 0 raw, 0 semi; CLUT [[32, 480], [160, 480]]; page [[512, 256]]; error 1.0405544040781696
```

Plantas: `figure-player-hair-unmoved`, `figure-player-skin-unmoved` (controles) e `replay-head-twin-unasked`, que passou a mirar `figure.player_head_section`. No `kits_ui`, `player_judge` e duas plantas: `Player's head ignored` e `the player's hair colour not moved`. A planta antiga `Long sleeves ignored` teve o literal ajustado à linha nova do `draw_figure`.

O `kits_ui` cobre a opção e as plantas, nesta árvore (`… ctest --test-dir build -R kits_ui -V`, linhas cortadas em 260 colunas):

```
  ok    3D TEX_14: Player's head draws the looks tuple's head, and two players apart only in hair colour are drawn apart (reference against Croatia 11 7527 px, Croatia 11 against Croatia 2 617 px)
        plant 'Long sleeves ignored': figure 0: Long sleeves ticked draws the same back as unticked, with nothing else; figure 0: Long sleeves ticked draws the same back as unticked, with Captain armband; figure 0: Long sleeves ticked draws the same back as un
  ok    plant 'Long sleeves ignored' fails the dressing judge
        plant 'Player's head ignored': reference and Croatia 11 draw the same 3D view; Croatia 11 and Croatia 2 draw the same 3D view
  ok    plant 'Player's head ignored' fails the player head judge
        plant 'the player's hair colour not moved': Croatia 11 and Croatia 2 draw the same 3D view
  ok    plant 'the player's hair colour not moved' fails the player head judge
kits_ui: 0 failure(s)
```

Gates, na árvore entregue:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  324.97 sec
2/5 Test #19: kits_image .......................   Passed   30.02 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  227.77 sec
5/5 Test #22: kits_replay ......................   Passed   11.84 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
  RED    replay-head-twin-unasked     kits/core/figure.py :: player_head_section
  RED    figure-player-hair-unmoved   kits/core/figure.py :: player_head_clut
  RED    figure-player-skin-unmoved   kits/core/figure.py :: player_head_clut
controls: 76 of 76 red
```
- **Closed** — commit `a2952514` (2026-10-16): feat(kits): draw the player's head from his looks tuple
  - Files (`git show --name-status a2952514`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/core/replay.py`
    - `M tools/kits/replay.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-16) at `32283929`: CORR-KRP-017, CORR-KRP-018
