---
id: K2D-TASK-07
---

# K2D-TASK-07 — source.py e api.open_source: a ROM pelo conteúdo, e os 95 times por import do kits

## Goal

`api.open_source(path)` reconhece a ROM pelo conteúdo (`.bin`, `.iso`, `.cue`) reusando `tools/kits/core/source.py`, lê os quatro arquivos pelo `iso.py`, e `source.teams()` devolve os 95 `TeamEntry` na ordem do jogo com `name_origin`, importando `tools/kits/core/teams.py` — nenhuma tabela nova ([§3.2](/docs/PLAN-KIT2D-PY.md#3.2), [§3.3](/docs/PLAN-KIT2D-PY.md#3.3)).

## Arquivos a criar ou modificar

- In:
  - `tools/kit2d/core/source.py`
  - `tools/kit2d/core/teams.py`
  - `tools/kit2d/core/api.py`
  - `tools/kit2d/selftest.py`
- Out:
  - escrita (fase 3)

## Done criteria

- [ ] `grep -rn "TEAM_NAMES\|Ireland" tools/kit2d/` não acha tabela de nomes própria
- [ ] `source.teams()` sobre o japonês devolve 95 entradas, primeira `Ireland` com origem inglesa; sobre o European, nome da ROM; contagens coladas no Log
- [ ] arquivo que não é ROM WE2002 é recusado com a frase da interface, visto vermelho no selftest

## Notes

—

## Log de Execução
