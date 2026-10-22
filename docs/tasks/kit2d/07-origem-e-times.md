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

- Da K2D-TASK-01: `tools/kits/core` e `tools/kit2d/core` são os dois pacotes `core`, e o primeiro no `sys.path` ganha para os dois (`ImportError: cannot import name 'layout' from 'core'`, visto). O `selftest.py` importa o do `kits` sob outro nome (`kits_core`, por `importlib.util.spec_from_file_location`); o `source.py`/`teams.py` daqui precisa do mesmo arranjo, de preferência movido para o núcleo e usado pelo selftest.

## Log de Execução
