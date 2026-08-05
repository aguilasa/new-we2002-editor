# `tests/` — testes do lado Pascal

Vazio na fase 0. O primeiro conteúdo real é da **WTE-TASK-20** (round-trip
headless contra o `we2002_core`, nas duas ROMs).

O golden test — o gate de verdade, a partir da WTE-TASK-22 — **não mora aqui**:
ele é script de shell em `tools/`, porque precisa de Wine, do `:99` e de ~1 GB
de temporário por rodada. Nada disso roda em CI.
