---
id: DMCP-TASK-26
---

# DMCP-TASK-26 — `kits`: controles, `COPIED` e monkeypatch reapontados

## Goal

`fork-joystick-let-through`, `looks-oracle-joystick-unasked` e `replay-capture-joystick-late` plantam no arquivo onde o código mora agora; `COPIED` inclui `tools/duckmcp`; o monkeypatch de `kits/selftest.py` troca `duckmcp.fork.joysticks` e `duckmcp.fork.launch`; um controle novo cobre a guarda de joystick do `dump_slot`.

## Arquivos a criar ou modificar

- In:
  - os três arquivos
  - `tools/duckmcp/selftest.py`: encolher no mesmo commit as entradas do `PENDING` da regra (b) que esta task remove; sem isso o check de entrada velha fica vermelho (CORR-DMCP-023)
- Out:
  - —

## Done criteria

- [ ] `python3 tools/kits/controls.py` sai 0, com a contagem antes e depois no Log
- [ ] o controle novo do `dump_slot` aparece vermelho, visto no Log
- [ ] `grep -n 'pes2/fork.py' tools/kits/*.py` não acha nada
- [ ] `ctest --test-dir build -R kits_selftest` passa

## Notes

## Log de Execução
