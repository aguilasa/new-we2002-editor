---
id: DMCP-TASK-10
---

# DMCP-TASK-10 — `duckmcp_live` — subir o fork com um `.cue` qualquer, andar, ler e matar

## Goal

`tools/duckmcp/live.py` é o alvo `duckmcp_live`: com `DUCKSTATION_TEST_IMAGE` apontando o `.cue` de uma cópia, sobe o fork, lista as ferramentas, pausa, dá `frame_step` e confere que `frame_number` avançou, e mata. Sai 77 sem a variável, sem o fork ou sem display. `RESOURCE_LOCK duckstation`. A Fase 3 acrescenta RAM, VRAM e `game()`.

## Arquivos a criar ou modificar

- In:
  - `live.py` e o `add_test`
- Out:
  - RAM, VRAM, `game()` (DMCP-TASK-15)

## Done criteria

- [x] `ctest --test-dir build -R duckmcp_live` sem a variável: *skipped*, com a razão impressa
- [x] com `DUCKSTATION_TEST_IMAGE=<cópia do WE2002>.cue DISPLAY=:98 XAUTHORITY=` dentro do comando (a japonesa de `roms/` não tem `.cue`; vale a cópia `work/looks-disc/we2002-english.cue`): `Passed`, e a saída do `live.py` colada no Log com o número de ferramentas que o servidor declarou
- [x] uma planta (`frame_step` trocado por `pause`) deixa o `live.py` vermelho, visto no Log
- [x] depois da corrida, `python3 tools/duckmcp/cli.py procs` dá `pids: []` (o `status` da lib é o `get_status` do servidor, desde a DMCP-TASK-09)

## Notes

A imagem é **cópia**, nunca `roms/`; o `launch` recusa. O teste usa só o que a lib tem, nada de jogo.

## Log de Execução

### 2026-10-22 — HEAD `5dcaf870`

`tools/duckmcp/live.py` sobe o fork sem `match`, pausa, conta o `tools/list`, lê o `frame_number` do `get_status`, dá cinco `frame_step` e exige que o `frame_number` tenha avançado **exatamente** cinco. A imagem vem de `--image` ou, na falta, de `DUCKSTATION_TEST_IMAGE`, lida por `env.get` — o leitor genérico que o `env.py` já tinha —, então a regra (d) continua valendo sem mexer no `env.py`. Sem imagem o script imprime a razão e sai 77; sem fork ou sem X o `fork.launch` levanta `Skip`, que vira 77; `Fail`, `NotRunning` e `ToolError` saem 1. O `fork.kill` roda no `finally`. O alvo `duckmcp_live` entrou no `tests/CMakeLists.txt` ao lado do `duckmcp_selftest`, com `SKIP_RETURN_CODE 77`, `RESOURCE_LOCK duckstation` e `TIMEOUT 180` (a corrida sozinha leva 3,6 s, mas o próprio `launch` pode esperar até 120 s um boot lento).

O que o servidor faz, medido: com o jogo pausado, um `frame_step` move o `frame_number` em exatamente um quadro — 40->45, 43->48, 45->50 em três corridas com cinco passos. O servidor declarou 95 ferramentas nas três.

Sem a variável:

```
$ cmake -S . -B build >/dev/null && ctest --test-dir build -R duckmcp_live -V
25: duckmcp_live: skipped -- no image: set DUCKSTATION_TEST_IMAGE to the .cue of a working copy, or pass --image
1/1 Test #25: duckmcp_live .....................***Skipped   0.04 sec
```

Com a cópia inglesa:

```
$ DUCKSTATION_TEST_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= ctest --test-dir build -R duckmcp_live -V
25: Test timeout computed to be: 180
25: duckmcp_live: /home/ingmar/desenvolvimento/github/new-we2002-editor/work/looks-disc/we2002-english.cue, 5 steps
25:   fork 445103 on :98, log /home/ingmar/desenvolvimento/github/new-we2002-editor/work/looks-disc/duckstation-fork.log
25:   window 4194311
25:   duckstation-mcp 1.0.0 answering
25:   tools declared: 95
25:   frame_number 43 -> 48 after 5 frame_step
25: duckmcp_live: ok -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 43->48
1/1 Test #25: duckmcp_live .....................   Passed    3.61 sec
100% tests passed, 0 tests failed out of 1
```

Planta: `client.call("frame_step")` trocado por `client.call("pause")` com `sed`, rodado com o mesmo ambiente, revertido do backup e rodado de novo:

```
$ DUCKSTATION_TEST_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/duckmcp/live.py; echo exit=$?
  frame_number 42 -> 42 after 5 frame_step
duckmcp_live: FAIL -- frame_number moved 0 for 5 frame_step (want 5); tools=95 frames 42->42
exit=1
# revertido
  frame_number 45 -> 50 after 5 frame_step
duckmcp_live: ok -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 45->50
exit=0
```

Depois de todas as corridas, nenhum processo. O critério diz `cli.py status`, mas desde a DMCP-TASK-09 `status` é o `get_status` do servidor (sai 77 sem servidor), e o que lista processo é o `procs`:

```
$ python3 tools/duckmcp/cli.py procs
pids: []
no DuckStation is running
```

Gates do pacote, que agora julgam o `live.py` também (regras (a), (c) e (d) aparecem com `live.py` no nome):

```
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 194 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/duckmcp/controls.py; echo exit=$?
duckmcp_controls: 16 control(s), 16 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4
exit=0
```

Para a DMCP-TASK-28 (documentação): o alvo `duckmcp_live` e a variável `DUCKSTATION_TEST_IMAGE` ainda não aparecem no `CLAUDE.md` nem nas listas de alvos do `ctest` dos documentos.
- **Closed** — commit `981b4860` (2026-10-22): feat(duckmcp): add live.py and the duckmcp_live ctest target
  - Files (`git show --name-status 981b4860`):
    - `M docs/tasks/duckmcp/10-duckmcp-live.md`
    - `M tests/CMakeLists.txt`
    - `A tools/duckmcp/live.py`
- **Reviewed** (2026-10-22) at `df6127e8`: CORR-DMCP-006, CORR-DMCP-011
