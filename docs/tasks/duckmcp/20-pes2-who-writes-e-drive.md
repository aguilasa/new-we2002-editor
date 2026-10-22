---
id: DMCP-TASK-20
---

# DMCP-TASK-20 — `pes2`: `who_writes.py`, `drive.py` e `selftest.py` sobre `debug` e `env`

## Goal

`who_writes.py` vira CLI fina sobre `duckmcp.debug.who_writes`; `drive.py` tira `SKIP`, `Fail`, `Skip`, `STATE_DIR`, o AppImage e o display do `env`, e passa a zerar `XAUTHORITY` só no `:98`; `drive.preflight` usa `env.is_roms`; o `selftest.py` do `pes2` deixa de rodar os self-checks que migraram.

## Arquivos a criar ou modificar

- In:
  - os três `.py` e o `boot_check.sh`
- Out:
  - o caminho do AppImage oficial, que fica (§0)

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0
- [ ] `grep -nE 'class (Fail|Skip)|^SKIP = ' tools/pes2/*.py` não acha nada
- [ ] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [ ] `ctest --test-dir build -R pes2_boot` com `PES2_IMAGE=<cópia>.cue DISPLAY=:98 XAUTHORITY=` no comando: mesmo veredito de antes, as duas linhas coladas no Log

## Notes

## Log de Execução
