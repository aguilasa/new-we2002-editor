---
id: K2D-TASK-22
---

# K2D-TASK-22 — Janela mínima: abrir, time, titular e suplente lado a lado, 16 cores, catálogo i18n

## Goal

`tools/kit2d/ui/app.py` em Fusion: Abrir…, caminho com cópia/original, combobox dos 95, titular e suplente lado a lado com zoom 1×–8× e fundo escolhível, as 16 caixas de cor, rodapé "uniforme 2D de menu, não o 3D"; todo texto do catálogo `ui/i18n.py` na forma do `tools/kits/ui/i18n.py` ([§3.4](/docs/PLAN-KIT2D-PY.md#3.4)).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/ui/app.py`
  - `tools/kit2d/ui/i18n.py`
  - `tools/kit2d/selftest.py`
- Out:
  - modelo, radar, undo (fase 6)
  - aba Diagnóstico (fase 8)

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kit2d/ui/*.py` só importa `core.api` do núcleo
- [ ] selftest: o catálogo tem as mesmas chaves e `{campos}` em `en-US` e `pt-BR`; planta de chave faltando sai vermelha
- [ ] captura no `:98` da janela aberta sobre o japonês, com um time de titular ≠ suplente, enviada e citada no Log

## Notes

—

## Log de Execução
