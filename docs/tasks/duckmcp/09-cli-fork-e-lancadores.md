---
id: DMCP-TASK-09
---

# DMCP-TASK-09 — `cli.py launch/kill/status/recipe/which`, shim do `pes2/fork.py`, e os lançadores apontados

## Goal

`python3 tools/duckmcp/cli.py launch|kill|status|recipe|which` existe; `tools/pes2/fork.py` vira shim que reexporta `duckmcp.fork` e passa o título do PES2 como `match` no `launch` dele; `boot_check.sh`, `run_duckstation.sh`, `Makefile` e `make.ps1` chamam a lib onde chamavam `tools/pes2/fork.py`, e a lista de nomes de processo do `kill_leftovers` sai de um lugar só.

## Arquivos a criar ou modificar

- In:
  - `cli.py`
  - o shim
  - os quatro lançadores
- Out:
  - mudar `mcp_drive.py`, `pad.py` (Fase 5)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0
- [ ] `python3 tools/duckmcp/cli.py recipe` imprime a receita, e `status` sem fork imprime `pids: []`
- [ ] `grep -rn 'pes2/fork.py' Makefile make.ps1 tools/pes2/*.sh` não acha nada
- [ ] `make -n pes2-status` mostra a chamada à lib

## Notes

O `run_duckstation.sh` continua sendo o caminho do AppImage oficial (não-objetivo do §0); muda só de onde tira as constantes.

## Log de Execução

- **pending** (2026-10-22): batch stopped before wave 2: kits_selftest red since 4de49640 (CORR-DMCP-005); the pes2/fork.py shim would make it worse
