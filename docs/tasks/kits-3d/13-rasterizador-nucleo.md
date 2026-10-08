---
id: K3D-TASK-13
---

# K3D-TASK-13 — Rasterizador por pixel no núcleo

## Goal

O núcleo desenha a figura 3D em software, por pixel: z-buffer, UV interpolado por pixel a partir da tela (o que também pinta o triângulo de UV degenerado) e texel mais próximo, com o texel transparente sem escrever cor nem profundidade. A contagem do `cli.py holes` passa a usar esse desenho, e a seção 5 da bermuda deixa de sair vazada de costas.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/raster.py` (novo): `draw(scene, yaw, pitch, width, height)` → RGBA e, por pixel, a peça e o texel
  - `tools/kits/core/figure.py` (`count_holes` sobre o rasterizador; reaproveita `_turn`, `HOLE_MARGIN`, `texel_zone`, `record_numbers`), `tools/kits/core/api.py`
  - `tools/kits/cli.py` (o `holes` continua com a mesma saída)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
- Out: a vista (`ui/figure_view.py`) — é a K3D-TASK-14; texel ou geometria inventados (§0)

## Done criteria

- [x] `python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00` (com `WE2002_LOOKS_IMAGE`): `skipped 0` e `misordered 0` em todas as 48 linhas; `transparent` só vindo das zonas e lacunas do colarinho; transcrição no Log
- [x] o `misordered` continua definido contra a ordem antiga por profundidade média, como controle: um caso do selftest com a ordem antiga mostra `misordered` > 0
- [x] caso sintético no selftest: um triângulo de UV degenerado é pintado; o controle `controls.py` que volta a pulá-lo fica vermelho
- [x] caso sintético no selftest: dois quads que se cruzam saem na ordem da profundidade em cada pixel; o controle que troca o z-buffer pela ordem por média fica vermelho
- [x] a câmera do rasterizador é a da vista (`_turn` e `HOLE_MARGIN`), conferida pelo selftest como hoje
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Medido em G6 (2026-10-08): de costas, a bermuda (seção 5) perde 218 px por triângulos de UV degenerado, e a seção 7 sai pintada sobre a 5 (70 px).

## Log de Execução

**O que existe.** `tools/kits/core/raster.py`: `draw(scene, yaw, pitch, width, height, triangles,
order=DEPTH, skip_degenerate=False)` devolve `Raster` (RGBA, e por pixel o fragmento mostrado e o
mais próximo). Ele usa z-buffer e UV interpolado por pixel a partir da tela, e o texel transparente
não escreve nada. `order=MEAN, skip_degenerate=True` é o desenho antigo, mantido só como controle.
`count_holes` (`core/figure.py`) passou a contar sobre ele, e a fachada ganhou
`api.draw_figure`. O `raster.py` não importa módulo do looks (§3.1): os triângulos vêm do
chamador, e `figure._turn`/`HOLE_MARGIN` passaram a ser os do `raster`, com a vista conferida
igual pelo selftest, como antes.

Evidência (2026-10-08):

```
$ python3 tools/kits/selftest.py --no-plant
  ..... flat UV: the drawing paints 2916 px of the near quad, skipped 0; the old drawing skips 2916
  ok    the drawing paints a triangle with no UV area (G6), and the old drawing's count still sees it skipped
  ..... crossing quads: by depth misordered 0, 0 px off the nearest, inks [1458, 1458]; by mean depth misordered 729
  ok    crossing quads: at every pixel the nearest wins (G6), and the old order by mean depth is seen misordered
  ok    hole count: its camera is ui/figure_view.py's rotate() and MARGIN
$ python3 tools/kits/controls.py --only raster-skips-flat-uv
  RED    raster-skips-flat-uv         kits/core/raster.py :: draw
$ python3 tools/kits/controls.py --only raster-mean-order
  RED    raster-mean-order            kits/core/raster.py :: draw
$ python3 tools/kits/controls.py --only holes-alpha-ignored      (retargeted to raster.py)
  RED    holes-alpha-ignored          kits/core/raster.py :: draw
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 32 of 32 red
```

**Transcrição inteira**, TEX_00, kit 1, Number desmarcado: `skipped 0` e `misordered 0` nas 48
linhas, e `transparent` (até 30 px) só vindo das zonas e lacunas do colarinho:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00 --negative
figure 0 yaw   0: silhouette 15161, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  15: silhouette 15274, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  30: silhouette 15007, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  45: silhouette 14785, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  60: silhouette 14768, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  75: silhouette 14617, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw  90: silhouette 14960, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 105: silhouette 15322, missing 7 (transparent 7, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 4; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 3
figure 0 yaw 120: silhouette 15518, missing 14 (transparent 14, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 9; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 3; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 1
figure 0 yaw 135: silhouette 15306, missing 23 (transparent 23, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 13; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 4; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1
figure 0 yaw 150: silhouette 14786, missing 26 (transparent 26, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 15; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 5; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1
figure 0 yaw 165: silhouette 14274, missing 30 (transparent 30, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 15; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 7; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 6; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 2
figure 0 yaw 180: silhouette 15161, missing 30 (transparent 30, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 18; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 5; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 2
figure 0 yaw 195: silhouette 15274, missing 28 (transparent 28, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 15; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 7; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1
figure 0 yaw 210: silhouette 15007, missing 27 (transparent 27, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 15; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 6; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1
figure 0 yaw 225: silhouette 14785, missing 21 (transparent 21, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 12; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 4; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 4; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1
figure 0 yaw 240: silhouette 14768, missing 14 (transparent 14, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 8; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, first 3; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 3
figure 0 yaw 255: silhouette 14617, missing 5 (transparent 5, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar 3; transparent /BIN/EDT_MOD.BIN section 0 gap collar, between its tips (21,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 0 zone shirt front, collar tip, second 1
figure 0 yaw 270: silhouette 14960, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 285: silhouette 15322, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 300: silhouette 15518, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 315: silhouette 15306, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 330: silhouette 14786, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 0 yaw 345: silhouette 14274, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
negative: figure 0, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
figure 1 yaw   0: silhouette 15254, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  15: silhouette 15217, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  30: silhouette 14911, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  45: silhouette 14773, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  60: silhouette 14887, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  75: silhouette 14821, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw  90: silhouette 15188, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 105: silhouette 15490, missing 2 (transparent 2, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 1
figure 1 yaw 120: silhouette 15641, missing 5 (transparent 5, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 2; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 1
figure 1 yaw 135: silhouette 15385, missing 9 (transparent 9, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 4; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 4; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1
figure 1 yaw 150: silhouette 14842, missing 11 (transparent 11, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 5; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 4; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 165: silhouette 14361, missing 11 (transparent 11, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 4; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 180: silhouette 15254, missing 13 (transparent 13, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 6; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 5; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 195: silhouette 15217, missing 11 (transparent 11, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 5; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 4; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 210: silhouette 14911, missing 10 (transparent 10, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 5; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 4; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 225: silhouette 14773, missing 8 (transparent 8, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 3; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 3; transparent /BIN/EDT_MOD.BIN section 11 gap collar, between its tips (85,6) 2x1 1; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1
figure 1 yaw 240: silhouette 14887, missing 5 (transparent 5, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 3; transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, first 1
figure 1 yaw 255: silhouette 14821, missing 2 (transparent 2, backdrop 0; skipped 0; misordered 0)  transparent /BIN/EDT_MOD.BIN section 11 gap collar, the notch between the shoulders (84,5) 4x1 1; transparent /BIN/EDT_MOD.BIN section 11 zone shirt front, collar tip, second 1
figure 1 yaw 270: silhouette 15188, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 285: silhouette 15490, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 300: silhouette 15641, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 315: silhouette 15385, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 330: silhouette 14842, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
figure 1 yaw 345: silhouette 14361, missing 0 (transparent 0, backdrop 0; skipped 0; misordered 0)  -
negative: figure 1, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
```

De olho, numa sonda que gravou o PNG do `api.draw_figure` a 940×409, de costas: a junção da
bermuda com a camiseta sai inteira, sem o fundo aparecendo. A janela continua com o desenho antigo
até a K3D-TASK-14.
- **Closed** — commit `3982070` (2026-10-08): feat(kits): draw the 3D figure per pixel in the core
  - Files (`git show --name-status 3982070`):
    - `M docs/tasks/kits-3d/13-rasterizador-nucleo.md`
    - `M docs/tasks/kits-3d/14-vista-rasterizador.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `A tools/kits/core/raster.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/core/raster.py`, `tools/kits/core/figure.py`, `tools/kits/core/api.py`, `tools/kits/cli.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`):
    - `docs/tasks/kits-3d/14-vista-rasterizador.md`
