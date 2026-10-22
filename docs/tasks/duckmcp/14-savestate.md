---
id: DMCP-TASK-14
---

# DMCP-TASK-14 — `savestate.py` movido para a lib, com shim no `pes2`

## Goal

`tools/pes2/savestate.py` vai inteiro para `tools/duckmcp/savestate.py` (`git mv` + shim), sem nada de jogo, e o `savestate.self_check` passa a rodar no selftest da lib.

## Arquivos a criar ou modificar

- In:
  - o move e o shim
- Out:
  - trocar quem importa `savestate` (Fases 5 a 7)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0
- [ ] `git log --follow --oneline tools/duckmcp/savestate.py | tail -1` mostra o primeiro commit do arquivo original
- [ ] `python3 tools/duckmcp/savestate.py info <um .sav do looks>` dá a mesma saída que o `tools/pes2/savestate.py info` dava na HEAD anterior, colada no Log

## Notes

## Log de Execução
