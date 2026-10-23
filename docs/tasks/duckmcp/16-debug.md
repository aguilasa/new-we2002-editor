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

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest afirma: watchpoint que nunca dispara é `Fail`; processo morto no meio é `Fail` com a armadilha 35 no texto; exceção dentro de `breakpoints` deixa `breakpoint clear` e `pause` registrados no cliente falso
- [x] os controles `breakpoint-not-cleared` e `wait-without-liveness` ficam vermelhos, vistos no Log
- [x] `who_writes` devolve as chaves `pc`, `registers`, `rows`, `store`, `caller`, as que `looks/oracle.catch_write` devolve hoje

## Notes

O intervalo de sondagem é parâmetro: o `looks` sonda sem dormir hoje, e a DMCP-TASK-23 mede antes e depois.

## Log de Execução

2026-10-23 — HEAD de trabalho `73e21f1d`, árvore com a lib nova (`tools/duckmcp/debug.py`) e as mudanças desta task no `selftest.py` e no `controls.py`.

**O que entrou.** `debug.py` traz os auxiliares do `who_writes.py` (`parse_address`, `hx`, `split_store`, `register_value`, `is_paused`) e uma espera só, `wait_for_pause(session, seconds, interval, nudge, every, required, alive)`. Por cima dela: `breakpoints(session, addresses, type)` (context manager que limpa antes de armar e, no `finally`, chama `breakpoint clear` e `pause`, cada um tentado mesmo se o outro falhar), `vram_watch` (remove pelo `id` e pausa no `finally`) com `last_vram_hit`, `who_writes` (o `catch_write`, com `presses` e o `nudge` do outro lado), `stops` e `watch_reads`. Toda função aceita uma `Session` ou qualquer objeto com `call`: fala com `session.client` quando ele existe. O `self_check` traz os casos do `who_writes.self_check` com endereços sintéticos (nenhum endereço de jogo: regra (c)) e os novos de limpeza e de vida.

**Decisão do §4.3, segundo item.** A versão única **confere vida a cada rodada** e o **intervalo é parâmetro** (`interval`, default `POLL_SECONDS = 1.0`, o do `who_writes`; `interval=0` é aceito e sonda sem dormir, como o `_wait_for_hit` de hoje; negativo é `ValueError`). Por quê: esperar breakpoint é execução livre, que é onde o fork morre sozinho (armadilha 35), e sem a sonda a morte vira "não disparou", a frase que manda procurar o defeito no endereço. A sonda é a do próprio cliente (`Client._liveness`, que já responde True/False/None), então quem injeta `Client(alive=...)` controla as duas; `None` (desconhecido) continua esperando até o prazo. O intervalo não foi fixado porque a DMCP-TASK-23 mede antes e depois que a contagem de paradas não muda: na migração os laços de sondagem sem pausa passam `interval=0`.

Outras duas escolhas, para as tasks de migração:

- `wait_for_pause` devolve os segundos como `float`, ou `None` com `required=False` no prazo. Compare com `is None`: uma parada na primeira sondagem pode levar `0.0`, e um `if not hit` a leria como silêncio.
- Toda espera armada termina **pausada**. O `catch_write` e o `who_writes.who_writes` deixavam a máquina andando depois de limpar; aqui o `finally` do `breakpoints` pausa sempre. A janela de desmontagem do `who_writes` usa os valores do `catch_write` (8 antes, 4 depois, 12 antes do `ra`), não os do CLI do `who_writes.py` (4 e 4, sem `caller`): o CLI passa `before=4, after=4` na DMCP-TASK-20 se quiser manter a saída.

Gates e critérios:

- `python3 tools/duckmcp/selftest.py --quiet; echo "exit=$?"` → `duckmcp_selftest: 427 check(s) ran, 0 failure(s)`, `exit=0`.
- `python3 tools/duckmcp/selftest.py | grep -E "debug: (a watchpoint that never|a death mid-wait|an exception inside breakpoints still|who_writes returns)"` →

```text
  ok    debug: a watchpoint that never fires is a Fail
  ok    debug: a death mid-wait is a Fail citing pitfall 35
  ok    debug: an exception inside breakpoints still clears and pauses
  ok    debug: who_writes returns pc, registers, rows, store, caller
```

  A armadilha 35 sai no texto como `pitfall 35`, com `PLAN-DUCKMCP-PY §1.3`, como nas mensagens do `client.py`. A de limpeza afirma que as duas últimas chamadas do cliente falso são `("breakpoint", "clear")` e `("pause", None)` depois de um `KeyError` dentro do bloco.

- Vermelho visto, um controle por vez:

```text
$ python3 tools/duckmcp/controls.py --only breakpoint-not-cleared
baseline: the untouched sandbox is green
red    breakpoint-not-cleared (rule debug): FAIL  debug: an exception inside breakpoints still clears and pauses  [('continue', None), ('pause', None)]
duckmcp_controls: 1 control(s), 1 red as required; per rule (debug) 1/1
$ python3 tools/duckmcp/controls.py --only wait-without-liveness
baseline: the untouched sandbox is green
red    wait-without-liveness (rule debug): FAIL  debug: a death mid-wait is a Fail citing pitfall 35  the CPU did not stop within 1.0s. Either nothing triggers the breakpoint in what the game is doing now -- put it where that happens first -- or the emulator stopped stepping. Silence is not an answer here
duckmcp_controls: 1 control(s), 1 red as required; per rule (debug) 1/1
```

  O segundo mostra a confusão que a sonda evita: sem ela, o processo morto sai como "did not stop", o texto do prazo.

- `python3 tools/duckmcp/controls.py; echo "exit=$?"`, última linha → `duckmcp_controls: 33 control(s), 33 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1`, `exit=0`.
- `ctest --test-dir build -R 'duckmcp_selftest|tasks'` → `1/2 Test  #6: tasks ... Passed 5.18 sec`, `2/2 Test #24: duckmcp_selftest ... Passed 7.71 sec`, `100% tests passed, 0 tests failed out of 2`.

Nenhum emulador subiu nesta task: tudo corre contra o cliente falso do `debug.self_check`.
- **Closed** — commit `b10bc6c8` (2026-10-23): feat(duckmcp): debug.py — one wait that watches the process, breakpoints that always clear and pause, who_writes as a dict
  - Files (`git show --name-status b10bc6c8`):
    - `M docs/tasks/duckmcp/16-debug.md`
    - `M tools/duckmcp/controls.py`
    - `A tools/duckmcp/debug.py`
    - `M tools/duckmcp/selftest.py`
- **Reviewed** (2026-10-23) at `62a174f2`: no finding
