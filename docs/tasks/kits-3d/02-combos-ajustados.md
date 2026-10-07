---
id: K3D-TASK-02
---

# K3D-TASK-02 — Combos do tamanho da opção mais longa

## Goal

Todo combo da janela mostra inteira a opção mais longa do idioma em uso e se reajusta quando o idioma troca ao vivo — o defeito que o `image_box` já corrigiu (`ui/app.py:326-327`) deixa de existir nos outros.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`
  - `tools/kits/ui_check.py`, `tools/kits/controls.py`
- Out: mudar textos do catálogo (é a K3D-TASK-01)

## Done criteria

- [ ] `kits_ui` afirma, para cada combo, abrindo em en-US e trocando para pt-BR ao vivo (e o inverso), que a largura do combo é ≥ a largura do texto mais longo dos seus itens; a saída cita o combo e as duas larguras
- [ ] a planta que tira o ajuste de um combo (ex.: `set_box`) fica vermelha
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Combos hoje com a política default: `set_box`, `figure_box`, `language_box`, `palette_box`, `zoom_box` (G2).

## Log de Execução
