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

### Fase 0 — esqueleto ([§3.1](/docs/PLAN-DUCKMCP-PY.md#3.1), [§3.3](/docs/PLAN-DUCKMCP-PY.md#3.3))

- `python3 tools/duckmcp/selftest.py` sai 0 e diz quantos checks; `ctest -R duckmcp_selftest` passa sem *skipped*.
- Precedência das variáveis: com `DUCKSTATION_MCP_PORT=1` e `PES2_MCP_PORT=2`, o `env` dá 1; só a segunda, 2.
- `python3 tools/duckmcp/controls.py` sai 0, e cada regra (a), (c), (d) tem controle visto vermelho no Log.
- `python3 tools/duckmcp/audit.py` roda e o Log da DMCP-TASK-02 tem a saída inteira — o número do antes.

### Fase 1 — transporte ([§3.1](/docs/PLAN-DUCKMCP-PY.md#3.1), [§2](/docs/PLAN-DUCKMCP-PY.md#2))

- O selftest cobre sessão roubada (uma recuperação, segunda perda é erro) com o servidor de teste, sem emulador.
- `tools/pes2/mcp.py` só reexporta; `python3 tools/pes2/selftest.py` sai 0.
- Importar `duckmcp.client` não carrega PIL, PySide6 nem numpy.

### Fase 2 — lançador ([§2.1](/docs/PLAN-DUCKMCP-PY.md#2.1), [§4.4](/docs/PLAN-DUCKMCP-PY.md#4.4), [§5.1](/docs/PLAN-DUCKMCP-PY.md#5.1))

- `grep -rn 'Pro Evolution' tools/duckmcp` não acha nada.
- `grep -rn 'pes2/fork.py' Makefile make.ps1 tools/pes2/*.sh` não acha nada.
- `duckmcp_live` pula com razão sem `DUCKSTATION_TEST_IMAGE`, e passa com o `.cue` de uma cópia no `:98`; nenhum processo do DuckStation sobra depois.

### Fase 3 — primitivas ([§3.1](/docs/PLAN-DUCKMCP-PY.md#3.1))

- `Session.press` sempre manda `duration_frames` (armadilha 36), afirmado com cliente falso.
- `png.py` e `vram.py` fazem ida e volta exata; `gpu.py` recusa lista em laço.
- `savestate.py` movido com histórico (`git log --follow`), e o `tools/pes2/savestate.py` é shim.
- `duckmcp_live` lê 2 MiB de RAM, 1024×512 de VRAM e o serial pelo `game()`.

### Fase 4 — depuração ([§4.3](/docs/PLAN-DUCKMCP-PY.md#4.3), [§3.3](/docs/PLAN-DUCKMCP-PY.md#3.3))

- `breakpoints` limpa e pausa depois de exceção; `wait_for_pause` com processo morto é `Fail` citando a armadilha 35.
- Regra (b): sítio novo fora da lista `PENDING` é vermelho; o tamanho da lista bate com o `audit.py`.

### Fase 5 — migração do `pes2` ([§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2))

- Os PNG das rotas `team-select`, `edit`, `result`, `replay` têm o mesmo `sha256sum` antes e depois.
- `grep -nE 'class (Fail|Skip)|^SKIP = ' tools/pes2/*.py` vazio; `pes2_selftest` e `pes2_boot` com o veredito de antes.
- O `audit.py` não lista mais sítio do `pes2`.

### Fase 6 — migração do `looks` ([§4.1](/docs/PLAN-DUCKMCP-PY.md#4.1), [§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2))

- `oracle.py --check-live` passa; `oracle.py --screen` sem diferença contra `screen.json`; `--pose 1` com as mesmas matrizes.
- `class OneSession` não existe; o controle de sessão roubada está no `duckmcp/controls.py` e é visto vermelho.
- `looks_selftest` verde, com a contagem de controles antes e depois explicada.

### Fase 7 — migração do `kits` ([§4.2](/docs/PLAN-DUCKMCP-PY.md#4.2), [§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2))

- `kits_replay` e `kits_selftest` com o veredito de antes; `grep -c 'client.call(' tools/kits/*.py` dá 0.
- O monkeypatch do `kits/selftest.py` troca atributos de `duckmcp.fork`, não do shim.
- `dump_slot` recusa joystick, e o controle novo disso é visto vermelho.

### Fase 8 — documentação ([§6](/docs/PLAN-DUCKMCP-PY.md#6))

- Nenhuma menção viva a `tools/pes2/{mcp,fork,savestate}.py` fora de `docs/tasks/concluidos/` e de remissão histórica marcada.
- `CLAUDE.md` documenta as `DUCKSTATION_*` e marca as `PES2_*` como legado; `rite check --cycle kit2d` limpo.

### Fase 9 — fechamento ([§0](/docs/PLAN-DUCKMCP-PY.md#0), [§5.2](/docs/PLAN-DUCKMCP-PY.md#5.2))

- `python3 tools/duckmcp/audit.py` dá 0; os três shims não existem.
- `duckmcp_live` passa em dois jogos com `sha256sum` de trilha diferente.
- Toda linha da tabela do §5.2 com o veredito do começo do ciclo.
