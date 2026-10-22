---
id: DMCP-TASK-16
---

# DMCP-TASK-16 — `debug.py` — uma espera, breakpoints que sempre limpam, `who_writes` e watches

## Goal

`debug.py` tem `wait_for_pause` (dorme por parâmetro, confere vida — armadilha 35 —, cutuca se pedido), `breakpoints(session, addresses, type)` que limpa e pausa no `finally`, `stops`, `who_writes` devolvendo dict (cobre o `catch_write` do `looks`), `watch_reads`, `vram_watch`, e os auxiliares `hx`, `parse_address`, `register_value`, `split_store`, `is_paused`.

## Arquivos a criar ou modificar

- In:
  - `debug.py` e os checks com cliente falso, vindos do `who_writes.self_check`
- Out:
  - migrar quem usa `who_writes` e os laços do `looks`/`kits`

## Done criteria

- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] o selftest afirma: watchpoint que nunca dispara é `Fail`; processo morto no meio é `Fail` com a armadilha 35 no texto; exceção dentro de `breakpoints` deixa `breakpoint clear` e `pause` registrados no cliente falso
- [ ] os controles `breakpoint-not-cleared` e `wait-without-liveness` ficam vermelhos, vistos no Log
- [ ] `who_writes` devolve as chaves `pc`, `registers`, `rows`, `store`, `caller`, as que `looks/oracle.catch_write` devolve hoje

## Notes

O intervalo de sondagem é parâmetro: o `looks` sonda sem dormir hoje, e a DMCP-TASK-23 mede antes e depois.

## Log de Execução
