---
id: K2D-TASK-14
---

# K2D-TASK-14 — edit.py: o buffer de edições, diff() em bytes e revert

## Goal

`api.Edit(source)` guarda `set_palette` / `set_model` / `set_radar` por time e uniforme, sabe se está sujo, devolve `diff()` como lista de `(offset, before, after)` e reverte um time.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/edit.py`
  - `tools/kit2d/core/api.py`
  - `tools/kit2d/selftest.py`
- Out:
  - gravar (K2D-TASK-15)

## Done criteria

- [ ] selftest: uma edição de cada tipo dá `diff()` de 32, 4 e 2 bytes nos offsets do §1.1, colado no Log
- [ ] editar e voltar ao valor original deixa o buffer limpo
- [ ] planta: paleta de 17 palavras e ponteiro fora dos 190 são recusados, vistos vermelhos

## Notes

—

## Log de Execução
