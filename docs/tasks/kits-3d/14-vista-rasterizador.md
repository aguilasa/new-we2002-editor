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

- [ ] o `kits_ui` compara a área da vista no screenshot com o `app.py --export-3d`, pixel a pixel, de costas (yaw 0) e de frente, nas duas figuras; a planta que volta ao desenho por triângulo fica vermelha
- [ ] o `app.py` imprime o tempo de um quadro no tamanho padrão (980×640); o limite é medido, registrado como constante no `ui_check.py` e afirmado pelo `kits_ui`
- [ ] continuam verdes `figure_judge`, `dress_judge`, `reset_judge`, `match_judge` e `back_judge`
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Depende do `raster.draw` da K3D-TASK-13, que a fachada expõe como `api.draw_figure(scene, yaw, pitch, width, height)` (RGBA, alfa 0 onde nada foi pintado). Medido na 13: 0,10 s a 940×409, de costas, no TEX_00 — a medida é de sonda; a deste item sai do `app.py`.

Da K3D-TASK-13 (varredura): a tabela "O que ainda falta" de G5 (`docs/KITS-AJUSTES-3D.md`) atribui `skipped` e `misordered` ao `ui/figure_view.py`. Quando a vista passar a mostrar o rasterizador, essas duas linhas viram história: atualizar G5 apontando para G6, com a contagem nova.

## Log de Execução
