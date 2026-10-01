---
id: KITS-TASK-18
---

# KITS-TASK-18 — Janela mínima: Abrir, combobox de tags, aba Plano, estilo Fusion fixo

## Goal

A janela abre ROM ou TEX por um só "Abrir…"; com ROM mostra o combobox (tags, com nome onde já se sabe); a aba Plano tem imagem, paleta, zoom, xadrez, grade, zonas, leitura sob o mouse e Exportar PNG. Fusion, `QPalette` fixa, fonte em pixels, layouts do Qt.

## Arquivos a criar ou modificar

- `tools/kits/ui/app.py`
- `tools/kits/ui/*.py`

## Done criteria

- [ ] `grep -rnE '^(from|import) ' tools/kits/ui/` só mostra PySide6, stdlib e `core.api`
- [ ] `work/venv-looks/Scripts/python.exe tools/kits/ui/app.py <rom> --screenshot <png>` grava a captura sem janela visível (fora da tela no Windows)
- [ ] Uma opção `--tag`/`--image`/`--palette` percorre as 105 tags sem exceção (contagem no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4).

## Log de Execução
