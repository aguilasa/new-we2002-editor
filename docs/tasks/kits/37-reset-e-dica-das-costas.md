---
id: KITS-TASK-37
---

# KITS-TASK-37 — Botão de reset na aba 3D e a dica das costas

## Goal

A aba 3D ganha um botão **Reset view** / **Restaurar vista**, e o duplo clique na vista faz o mesmo: os dois voltam ao giro de abertura (`DEFAULT_YAW`, `DEFAULT_PITCH` de `ui/figure_view.py`). A dica da aba passa a dizer por que as costas saem vazadas: a área que o torso amostra está vazia no TEX (§4.7). O desenho continua fiel aos dados (decisão do usuário, 2026-10-05).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/figure_view.py`: `reset()`, que chama `turn_to(DEFAULT_YAW, DEFAULT_PITCH)`, e o `mouseDoubleClickEvent`
  - `tools/kits/ui/app.py`: o botão na linha de cima da aba 3D e `--reset`, que aplica `--yaw`/`--pitch` e depois o mesmo slot do botão
  - `tools/kits/ui/i18n.py`: o rótulo do botão e a frase das costas em `figure_hint`, em en-US e pt-BR
  - `tools/kits/ui_check.py`: a verificação do reset e uma planta
  - `docs/PLAN-KITS-PY.md`: §3.4, se a forma final mudar
- Out: número, braçadeira e qualquer preenchimento das costas (KITS-TASK-38 a 40)

## Done criteria

- [ ] `app.py <jp> --tag 00 --tab 3d --yaw 0 --pitch 30 --reset --screenshot A` e `… --tab 3d --screenshot B` dão o mesmo sha256 (no Log). A mesma captura sem `--reset` dá outro sha256: é o controle
- [ ] `kits_ui` afirma isso, e a planta `reset to the wrong yaw` (`reset()` com `DEFAULT_YAW + 90`) o deixa vermelho, com o vermelho no Log
- [ ] O selftest confere o catálogo: `language: 0 failure(s)`, com as chaves novas nas duas línguas
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4).

O `FigureView` não guarda zoom nem pan: a câmera reenquadra a figura a cada quadro, então o reset é só o giro. Para o vazado das costas, ver a [§4.7](/docs/PLAN-KITS-PY.md#4.7). Não é face descartada: o `FigureView` pinta as faces dos dois lados.

## Log de Execução
