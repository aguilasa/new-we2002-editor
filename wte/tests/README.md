# `tests/` — testes do lado Pascal

Vazio na fase 0. O primeiro conteúdo real é da **WTE-TASK-20** (round-trip
headless contra o `we2002_core`, nas duas ROMs).

O golden test — o gate de verdade, a partir da WTE-TASK-22 — **não mora aqui**:
ele é script de shell em `tools/`, porque precisa de Wine, do `:99` e de ~1 GB
de temporário por rodada. Nada disso roda em CI.

Teste de **ferramenta Python** também não mora aqui: fica em
`tools/test_<gerador>.py`, ao lado do gerador que testa, e roda por
`make -C wte test` (de que `check` depende). Ver
[`../tools/README.md`](../tools/README.md). Esta pasta é só Pascal — a
pergunta "onde ponho o teste do `dfm_extract.py`?" ficou sem resposta uma vez,
e a verificação acabou em código descartável (CORR-WTE-005).
