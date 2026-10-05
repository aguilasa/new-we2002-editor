---
id: KITS-TASK-40
---

# KITS-TASK-40 — Checkboxes de número e braçadeira na aba 3D

## Goal

A aba 3D ganha dois checkboxes, **Number** e **Captain armband**, que desenham na figura só o que as KITS-TASK-38 e 39 mediram. O que não foi medido fica com o checkbox desligado e a frase "not measured" no catálogo. Remapear UV à mão não vale (§0).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py` e `tools/kits/core/api.py`, se a regra medida pedir composição de texels ou geometria a mais
  - `tools/kits/ui_check.py`: a verificação e a planta
  - `docs/PLAN-KITS-PY.md`: §3.4
- Out: manga longa e árbitro (§4.3, §4.5)

## Done criteria

- [ ] Para cada checkbox com regra medida: as capturas de costas (`--yaw 0`) ligado e desligado diferem dentro da vista, e a planta que ignora o checkbox fica vermelha no `kits_ui`
- [ ] Para cada checkbox sem regra: aparece desligado com a frase, nas duas línguas, e o `kits_ui` afirma que está desligado
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

Se as 38 e 39 terminarem as duas blocked, por falta do save state de partida, esta task também espera. Entregar só os checkboxes desligados é decisão do usuário.

## Log de Execução
