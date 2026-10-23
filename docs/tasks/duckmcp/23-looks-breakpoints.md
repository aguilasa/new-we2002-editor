---
id: DMCP-TASK-23
---

# DMCP-TASK-23 — `looks`: esperas e laços de breakpoint sobre `debug`

## Goal

`_wait_for_hit`, `_stops`, `catch_write` e os laços de breakpoint do §1.2 em `looks/oracle.py` e `looks/confront.py` passam a usar `duckmcp.debug`; nenhum `breakpoint` cru sobra no `looks`.

## Arquivos a criar ou modificar

- In:
  - as funções listadas no §1.2
  - `tools/duckmcp/selftest.py`: encolher no mesmo commit as entradas do `PENDING` da regra (b) que esta task remove; sem isso o check de entrada velha fica vermelho (CORR-DMCP-023)
- Out:
  - a análise de pose, câmera e tela, que não muda

## Done criteria

- [ ] `python3 tools/looks/oracle.py --screen` antes e depois, ambos sem diferença contra `tools/looks/screen.json`
- [ ] `python3 tools/looks/oracle.py --pose 1` dá as mesmas matrizes antes e depois (o `diff` dos JSONs de `work/looks-pose/` vazio)
- [ ] `grep -cE 'call\("breakpoint"' tools/looks/*.py` dá 0
- [ ] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [ ] `python3 tools/looks/selftest.py` sai 0

## Notes

O `_wait_for_hit` sonda sem dormir; o intervalo novo se escolhe medindo que a contagem de paradas do `--pose` não muda.

## Log de Execução
