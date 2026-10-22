# Profile — duckmcp

<!--
The cycle profile is read by every /rite command in this cycle. Keep it short
(rite.toml [profile].max_kb); dated pitfall histories go to the pitfalls file,
which commands search instead of reading whole.
-->

## Contexto essencial — decisões já confirmadas

<!-- Decisions the user confirmed. One line each, with the date and where it was decided. -->

- 2026-10-22 — a lib é o pacote `tools/duckmcp/`, importado como `import duckmcp` com `tools/` no `sys.path` ([§2](/docs/PLAN-DUCKMCP-PY.md#2)).
- 2026-10-22 — **agnóstica de jogo**: só hardware PS1 e emulador; nada de serial, título, endereço de RAM de jogo, rota ou slot ([§2.1](/docs/PLAN-DUCKMCP-PY.md#2.1)).
- 2026-10-22 — `tools/pes2/mcp.py`, `fork.py` e `savestate.py` são shims só durante o ciclo; o fechamento os apaga ([§2](/docs/PLAN-DUCKMCP-PY.md#2)).
- 2026-10-22 — variáveis `DUCKSTATION_*` novas, com as `PES2_*` lidas como fallback e marcadas legado; a nova ganha ([§2](/docs/PLAN-DUCKMCP-PY.md#2)).
- 2026-10-22 — o cliente parte do `mcp.py` da PES2-TASK-03, commit `f21182ea` ([§2](/docs/PLAN-DUCKMCP-PY.md#2)).

## Sources of truth

<!-- Plan sections, specs, reference outputs. Items point here through `source_of_truth`. -->

- [PLAN-DUCKMCP-PY.md](/docs/PLAN-DUCKMCP-PY.md) — o plano do ciclo.

## Generated artifacts

<!-- Output -> generator -> check command. Never edit the output. -->

## Gates deste ciclo

<!-- Commands that must pass before any item of this cycle closes (in addition to rite.toml [gates].global). -->

## Hot files

<!-- Files many items touch; batches serialize on them. -->

## Serialized resources

<!-- Cycle-specific resources that cannot be used by two workers at once (rite.toml [resources] has repo-wide ones). -->

## Pull-ahead precedents

<!-- When the user allowed work from a later task to be done early, and why. -->

## Verificações específicas por fase

<!-- One entry per phase used by tasks ("### Phase 1 — ..."). The reviewer runs these; a phase without an entry is a finding. -->
