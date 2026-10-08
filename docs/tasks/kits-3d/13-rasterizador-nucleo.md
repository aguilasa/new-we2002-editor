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

- [ ] `python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00` (com `WE2002_LOOKS_IMAGE`): `skipped 0` e `misordered 0` em todas as 48 linhas; `transparent` só vindo das zonas e lacunas do colarinho; transcrição no Log
- [ ] o `misordered` continua definido contra a ordem antiga por profundidade média, como controle: um caso do selftest com a ordem antiga mostra `misordered` > 0
- [ ] caso sintético no selftest: um triângulo de UV degenerado é pintado; o controle `controls.py` que volta a pulá-lo fica vermelho
- [ ] caso sintético no selftest: dois quads que se cruzam saem na ordem da profundidade em cada pixel; o controle que troca o z-buffer pela ordem por média fica vermelho
- [ ] a câmera do rasterizador é a da vista (`_turn` e `HOLE_MARGIN`), conferida pelo selftest como hoje
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Medido em G6 (2026-10-08): de costas, a bermuda (seção 5) perde 218 px por triângulos de UV degenerado, e a seção 7 sai pintada sobre a 5 (70 px).

## Log de Execução
