---
id: K2D-TASK-09
---

# K2D-TASK-09 — sprites.py e render.py: listas de 10 bytes e o compositor, api.render e api.render_model

## Goal

`source.models()` devolve os 190 `Model` com a regra de delimitação medida na K2D-TASK-04, `source.kit(team, set)` devolve `Kit2D`, e `api.render` / `api.render_model` compõem o uniforme em RGBA com a transparência medida na K2D-TASK-05.

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/sprites.py`
  - `tools/kit2d/core/render.py`
  - `tools/kit2d/core/api.py`
  - `tools/kit2d/selftest.py`
- Out:
  - confronto com o emulador (fase 2)

## Done criteria

- [ ] `source.models()` devolve 190 modelos distintos; contagem colada no Log
- [ ] os 95 times × 2 uniformes renderizam sem índice fora da paleta e sem sprite fora da imagem (`0 problema(s)` colado do comando)
- [ ] planta: um registro com `v+h` além das três imagens é recusado com o nome do registro, visto vermelho
- [ ] planta: base de carga deslocada de 10 bytes faz o render recusar ou divergir, visto vermelho

## Notes

—

## Log de Execução
