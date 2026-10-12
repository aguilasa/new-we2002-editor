---
id: K3D-TASK-14
---

# K3D-TASK-14 — A vista mostra o rasterizador

## Goal

A aba 3D mostra a imagem que o rasterizador do núcleo desenha, no tamanho do widget, no lugar do desenho triângulo a triângulo por `QPainter`. A vista e a contagem passam a ser o mesmo desenho.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/figure_view.py` (`paintEvent` desenha a imagem do `core`; saem `_affine` e o `quadToQuad`)
  - `tools/kits/ui/app.py` (opção `--export-3d PNG`, que grava a imagem do rasterizador, e o tempo de um quadro)
  - `tools/kits/ui_check.py`
- Out: mudar a câmera, o giro ou o reset (KITS-TASK-37)

## Done criteria

- [x] o `kits_ui` compara a área da vista no screenshot com o `app.py --export-3d`, pixel a pixel, de costas (yaw 0) e de frente, nas duas figuras; a planta que volta ao desenho por triângulo fica vermelha
- [x] o `app.py` imprime o tempo de um quadro no tamanho padrão (980×640); o limite é medido, registrado como constante no `ui_check.py` e afirmado pelo `kits_ui`
- [x] continuam verdes `figure_judge`, `dress_judge`, `reset_judge`, `match_judge` e `back_judge`
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Depende do `raster.draw` da K3D-TASK-13, que a fachada expõe como `api.draw_figure(scene, yaw, pitch, width, height)` (RGBA, alfa 0 onde nada foi pintado). O tempo de quadro não foi medido na 13 por ferramenta; o deste item sai do `app.py`.

Da K3D-TASK-13 (varredura): a tabela "O que ainda falta" de G5 (`docs/KITS-AJUSTES-3D.md`) atribui `skipped` e `misordered` ao `ui/figure_view.py`. Quando a vista passar a mostrar o rasterizador, essas duas linhas viram história: atualizar G5 apontando para G6, com a contagem nova.

## Log de Execução

**O que mudou.**

- `ui/figure_view.py` não tem mais câmera nem desenho próprios: saem `rotate`, `MARGIN`, `_projected` e `_affine`.
- O `paintEvent` mostra `picture()`, que é o `api.draw_figure` no tamanho e no giro do widget, por cima do fundo (`composed`).
- `app.py --export-3d PNG` chama a fachada direto, sem passar pelo `paintEvent`, e imprime `3d view: at X,Y, WxH, yaw, pitch, frame N ms`.
- `api.draw_figure` ganhou `order` e `skip_degenerate`, só para a planta trazer o desenho antigo de volta.
- O caso de câmera do `selftest.py` (que executava o `rotate` da vista) virou: "a vista não tem câmera nem desenho próprios" (`core/api.py` e `selftest.py`, fora dos `files`).
- G5 diz agora que `skipped` e `misordered` foram consertados em G6.

O limite do quadro, `FRAME_LIMIT_MS = 400` no `ui_check.py`, é medido a 940×409 no Xvfb, com folga para máquina mais lenta. A faixa sai da linha do juiz, não de memória: a transcrição abaixo dá 100 a 121 ms; depois das CORR-K3D-007 a 009, que passaram a cronometrar o `picture()` da própria vista, a mesma linha dá 106 a 111 ms:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep "core's drawing"
  ok    the 3D view is the core's drawing, pixel for pixel, from the back and the front of both figures (figure 0 yaw 0 0 px off, 108 ms; figure 0 yaw 180 0 px off, 111 ms; figure 1 yaw 0 0 px off, 108 ms; figure 1 yaw 180 0 px off, 106 ms)
```

O `files` desta task ganhou `tools/kits/core/api.py`, `tools/kits/selftest.py` e `docs/KITS-AJUSTES-3D.md`, que o commit `d4edbcc` tocou e o Log já citava (CORR-K3D-009).

Evidência (2026-10-08):

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    the 3D view is the core's drawing, pixel for pixel, from the back and the front of both figures (figure 0 yaw 0 0 px off, 121 ms; figure 0 yaw 180 0 px off, 101 ms; figure 1 yaw 0 0 px off, 102 ms; figure 1 yaw 180 0 px off, 100 ms)
        plant 'the view back to the old drawing': figure 0 yaw 0: 995 of 384460 px of the view are not the core's drawing; figure 0 yaw 180: 714 of 384460 px ...; figure 1 yaw 0: 873 ...; figure 1 yaw 180: 816 ...
  ok    plant 'the view back to the old drawing' fails the core drawing judge
  ok    3D TEX_00: the four combinations draw a figure, and set 1 is not set 2 for either figure ...      (figure_judge)
  ok    3D TEX_14: the match player is drawn, and the captain's armband changes only a box on its arm ... (match_judge)
  ok    3D TEX_14 from the back: each measured dressing changes the view (Number 1197 px, ...)          (dress_judge)
  ok    Reset view and a double click after --yaw 0 --pitch 30 are the 3D as it opens, ...             (reset_judge)
  ok    Number unticked, the torso gap shows through at no turn of either figure (48 turn(s), 0 ...)    (back_judge)
kits_ui: 0 failure(s)

$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 32 of 32 red
```

A planta é do `PLANTS` do `ui_check.py` (alvo `figure_view.py`); o `controls.py` roda sem tela e não ganhou entrada.
- **Closed** — commit `d4edbcc` (2026-10-08): feat(kits): show the core's per-pixel drawing in the 3D tab
  - Files (`git show --name-status d4edbcc`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/14-vista-rasterizador.md`
    - `M tools/kits/core/api.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/figure_view.py`
    - `M tools/kits/ui_check.py`
  - **Outside declared files** (`tools/kits/ui/figure_view.py`, `tools/kits/ui/app.py`, `tools/kits/ui_check.py`):
    - `docs/KITS-AJUSTES-3D.md`
    - `tools/kits/core/api.py`
    - `tools/kits/selftest.py`
- **Reviewed** (2026-10-08) at `b9efea8`: CORR-K3D-007, CORR-K3D-008, CORR-K3D-009
