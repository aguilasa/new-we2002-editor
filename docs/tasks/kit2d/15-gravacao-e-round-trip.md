---
id: K2D-TASK-15
---

# K2D-TASK-15 — writer.py: api.apply in-place na cópia, refuse_roms e round-trip

## Goal

`api.apply(edit, path)` grava o `diff()` pelo `iso.write_file`, tamanho fixo, sem EDC/ECC, e recusa `roms/` por `refuse_roms`; o item 3 do [§5](/docs/PLAN-KIT2D-PY.md#5) — round-trip — fica provado.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/writer.py`
  - `tools/kit2d/core/api.py`
  - `tools/kit2d/selftest.py`
- Out:
  - —

## Done criteria

- [ ] aplicar sem editar numa cópia deixa sha256 idêntico, antes e depois no Log
- [ ] aplicar uma edição e reabrir devolve a edição; `cmp -l` da cópia contra o original lista só os bytes do diff, contagem no Log
- [ ] gravar em `roms/` é recusado, visto vermelho

## Notes

—

## Log de Execução
