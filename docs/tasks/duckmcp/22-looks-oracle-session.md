---
id: DMCP-TASK-22
---

# DMCP-TASK-22 — `looks`: `Oracle` sobre `Session`, e o `OneSession` some

## Goal

`looks.oracle.Oracle` passa a envolver `duckmcp.Session`: `pause`, `step`, `press`, `capture`, `read_ram`, `load_looks` delegam; `hide_window`/`size_window` e os caminhos de estado vêm da lib; o `OneSession` sai, e o controle `oracle-session-never-renewed` do `looks` migra para o `duckmcp/controls.py`. `main` mapeia `Fail`, `NotRunning` e `ToolError` (§4.3).

## Arquivos a criar ou modificar

- In:
  - `Oracle`, `OneSession`, `hide_window`, `size_window`, `emulator_states_dir`
  - o import de `OneSession`/`hide_window` em `tools/kits/oracle.py`
  - os controles reapontados
- Out:
  - as esperas e os laços de breakpoint (DMCP-TASK-23)

## Done criteria

- [x] `python3 tools/looks/oracle.py --check-live` passa antes e depois, as duas saídas no Log, com `WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE` absolutos no comando
- [x] `python3 tools/looks/selftest.py` sai 0, com a contagem de controles colada antes e depois (a diferença é o controle que migrou)
- [x] `grep -n 'class OneSession' tools/looks/oracle.py` não acha nada
- [x] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue

## Notes

`kits/oracle.py` importa `OneSession` e `hide_window` do `looks`: o import passa para a lib nesta task, ou o `kits_selftest` quebra.

## Log de Execução

2026-10-23 — HEAD de partida `09effe53`, árvore com as mudanças desta task. `J` abaixo é a cópia da trilha japonesa em `/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin`, conferida por `WE2002_LOOKS_IMAGE=$J python3 tools/looks/cli.py check` → `cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok`.

**O que mudou.** `Oracle` passou a envolver `duckmcp.Session`: `pause`, `step`, `press` (`Session.press(button, frames=CONFIRM_FRAMES, after=SETTLE_FRAMES)`, os mesmos 8 + 20 quadros), `capture` (`Session.capture`, que apaga o arquivo antes), `read_ram` e `load_looks` (`Session.load_state(slot, settle=LOAD_FRAMES)`) delegam. Duas costuras novas no `Oracle`, ambas sobre `Session.call`, porque a `Session` não tem o método: `hold(button)` — `press_button` **sem** passo depois, para `--turn` e `--rhythm`, que contam os quadros a partir do aperto e mudariam de medida com os 28 do `press` — e `status()`, o `get_status` inteiro que `clock_span` lê. Fora do `Oracle`, os sítios que não estão em laço de breakpoint foram para a `Session`: `vram_region` (`read_vram_region`), dois `dump_vram`, dois `write_vram_region`, `tap`, dois `get_gpu_state`. `hide_window`/`size_window` saíram do `looks` (ficou `SHOT_SIZE`, que é do jogo) e são os de `duckmcp.fork`; `emulator_states_dir`/`emulator_state` são `env.savestates_dir()`/`env.state_path(SERIAL, slot)`, com `WE2002_LOOKS_EMULATOR_STATES` ainda ganhando; `media_of` e o self-check leem `duckmcp.savestate`. `OneSession` e `SESSION_LOST` sumiram: quem retoma a sessão é o `Client` da lib (`reclaim`), e o `Oracle.__exit__` diz quantas vezes isso aconteceu, então não fica silencioso. `tools/kits/oracle.py` (`dump_slot`) importa `hide_window` de `duckmcp.fork` e deixou de embrulhar o cliente.

**Decisão: o `Oracle` lança, a `Session` envolve.** `Session(image)` refaria a recusa de controle dentro de `Session.__enter__`, e o controle `looks-oracle-joystick-unasked` do `kits` (§4.1) planta justamente a remoção de `fork.refuse_joysticks()` no `Oracle.__enter__`: com a recusa duplicada ele ficaria verde. Por isso o `Oracle` recusa, lança e esconde/dimensiona a janela antes da primeira pausa, como sempre fez, e entra numa `Session(client=...)`, que faz o handshake (idempotente) e a pausa. Da `Session` dona veio a regra de matar só se um pid novo apareceu quando o `launch` falha (CORR-DMCP-011); antes, uma falha depois do `Popen` deixava o fork de pé. `python3 tools/kits/controls.py --only looks-oracle-joystick-unasked` → `RED    looks-oracle-joystick-unasked looks/oracle.py :: Oracle.__enter__` / `controls: 1 of 1 red`.

**Decisão do §4.3, último item.** O `main` responde 77 a `Skip`, como já respondia a `Unavailable`, e 1 a `Fail`, `NotRunning` e `ToolError` (o `SessionLost` vem junto, porque é um `ToolError`), com uma linha `oracle FAILED: <Tipo>: …` no stderr em vez de traceback. Fork que não subiu, morreu no meio (armadilha 35) ou recusou uma chamada é falha, não pulo; o pulo continua sendo a máquina que não tem o que precisa. O self-check afirma os cinco: `ok    main answers Skip with 77, and names it` e mais quatro linhas `… with 1, and names it`. Vermelho visto: numa cópia da árvore com `except (Fail, NotRunning, ToolError) as exc:` trocado por `except (Fail,) as exc:`, `python3 <cópia>/tools/looks/oracle.py --check` → `FAIL  main answers NotRunning with 1, and names it`, idem `ToolError` e `SessionLost`, `oracle.py: 6 failure(s)`, saída 6.

**O controle que migrou.** `oracle-session-never-renewed` saiu do `looks/controls.py` e entrou no `duckmcp/controls.py`, na regra `client`, plantado no caminho de retomada do `Client.call`: some a linha `self.session = self.server = None`, o `initialize()` vira no-op e a chamada é reenviada com o id velho. `python3 tools/duckmcp/controls.py --only oracle-session-never-renewed` → `red    oracle-session-never-renewed (rule client): FAIL  client: a stolen session is recovered once and the call goes through  SessionLost: HTTP 400 from the server: …`, `duckmcp_controls: 1 control(s), 1 red as required`. A bateria inteira, `python3 tools/duckmcp/controls.py` → `duckmcp_controls: 42 control(s), 42 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 3/3, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1`, saída 0. Nenhum controle da regra (b) mirava entrada removida.

**`PENDING`.** Saíram as 19 entradas (28 sítios) que esta task removeu. As 6 entradas da DMCP-TASK-22 que sobravam (17 sítios: os 11 `client.call("pause")` dos `finally` de breakpoint, os 4 `press_button` e os 2 `get_status` de dentro de laço de breakpoint ou de `vram_watch`) foram **reetiquetadas para DMCP-TASK-23**, sem mudar chave nem contagem: são os laços que o escopo desta task deixa para a 23.

**`audit.py`, antes** (HEAD `09effe53`, antes de qualquer edição) — os sítios de `tools/looks/oracle.py` que esta task tirou, contados por chave (`diff` entre o `audit.py --root` de uma cópia de `tools/` com os cinco arquivos da HEAD e o da árvore entregue, sem número de linha, `sort | uniq -c | sort -rn`), e os totais do `audit.py` da HEAD:

```
      3 tools/looks/oracle.py: import: import fork
      3 tools/looks/oracle.py: client: game.client.call("press_button", button="Down",
      2 tools/looks/oracle.py: import: import savestate
      2 tools/looks/oracle.py: import: import mcp
      2 tools/looks/oracle.py: client: gpu = game.client.call("get_gpu_state")
      2 tools/looks/oracle.py: client: game.client.call("press_button", button="Up",
      2 tools/looks/oracle.py: client: game.client.call("dump_vram", path=path, format="png")
      1 tools/looks/oracle.py: client: self.client.call("take_screenshot", path=path)
      1 tools/looks/oracle.py: client: self.client.call("read_memory", address=address, size=size, path=path)
      1 tools/looks/oracle.py: client: self.client.call("press_button", button=button,
      1 tools/looks/oracle.py: client: self.client.call("pause")
      1 tools/looks/oracle.py: client: self.client.call("load_state", slot=slot)
      1 tools/looks/oracle.py: client: self.client.call("frame_step")
      1 tools/looks/oracle.py: client: reply = game.client.call("read_vram_region", x=x, y=y,
      1 tools/looks/oracle.py: client: game.client.call("write_vram_region", x=page[0], y=page[1],
      1 tools/looks/oracle.py: client: game.client.call("write_vram_region", x=0, y=origin, width=width,
      1 tools/looks/oracle.py: client: game.client.call("press_button", button=button,
      1 tools/looks/oracle.py: client: before = game.client.call("get_status")
      1 tools/looks/oracle.py: client: after = game.client.call("get_status")
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 139 site(s) in 5 file(s) (import 7, client 128, sys.path 4)
by category: import 11, client 151, sys.path 7
audit: 169 raw site(s) in 10 file(s)
```

**`audit.py`, depois** (árvore entregue): nenhuma das linhas acima; o `[kits]` igual (o `from oracle import OneSession` nunca foi sítio); os totais:

```
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 111 site(s) in 5 file(s) (import 0, client 107, sys.path 4)
by category: import 4, client 130, sys.path 7
audit: 141 raw site(s) in 10 file(s)
```

E a regra (b): `python3 tools/duckmcp/selftest.py` → `ok    rule (b): PENDING lists 141 site(s) in 55 entries, audit.py counts 141` / `duckmcp_selftest: 435 check(s) ran, 0 failure(s)`, saída 0.

**`--check-live`**, com `WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/looks/oracle.py --check-live`, os dois com saída 0 e `cli.py procs` → `pids: []` depois:

- antes: `restored slot 1 from the project copy (the emulator's was different)`, idem slot 2; `shot slot1-goalkeeper  mean=0.182425 sd=0.189376`; `ok    a reloaded state is the same picture to the last bit`; `shot slot2-outfield  mean=0.183158 sd=0.190350`; `the plate differs by 0.119963 between the slots`; `/BIN/EDT_MOD.BIN at 0x8011c000: 203 of 36072 byte(s) differ (99.44% equal)`; `/BIN/MODEL.BIN at 0x8016e800: 20 of 64800 byte(s) differ (99.97% equal)`; `Right moved it by 0.108086`; `oracle --check-live: 0 failure(s)`.
- depois: as mesmas linhas com os mesmos números (`mean=0.182425 sd=0.189376`, `mean=0.183158 sd=0.190350`, `0.119963`, `203 of 36072`, `20 of 64800`, `Right moved it by 0.108086`), `oracle --check-live: 0 failure(s)`. Só faltam as duas linhas `restored slot …`: os slots do emulador já eram a cópia mestra da corrida anterior.

**`--screen`**, com as mesmas variáveis: `screen measured in 2702s` / `oracle --screen: 0 difference(s) from screen.json`, saída 0, `pids: []` depois. É a corrida que passa por `tap`, pelo `dump_vram` das caixas e pelo `get_gpu_state` migrados. **Não rodados ao vivo**: `--pose 1` (fica para o fechamento da fase), `--turn`/`--rhythm` (`hold`, `status`), `--repaint`/`--pages` (`write_vram_region`), `--palettes` (`read_vram_region`) e o `dump_vram` da proveniência. Nesses a chamada que sai é a mesma de antes (mesma ferramenta, mesmos argumentos; o `read_vram_region` passa a mandar `format="png"` explícito, e os dois `dump_vram` apagam o arquivo antes).

**Critérios.**

- `python3 tools/looks/selftest.py` → antes `..... 114 of 114 controls red` / `looks_selftest: 0 failure(s)`; depois `..... 113 of 113 controls red` / `looks_selftest: 0 failure(s)`, saída 0. A diferença é o `oracle-session-never-renewed`.
- `grep -n 'class OneSession' tools/looks/oracle.py` → nada, saída 1.
- `ctest --test-dir build -R 'duckmcp_selftest|looks_selftest|kits_selftest|tasks'` → `100% tests passed, 0 tests failed out of 4` (`kits_selftest` 351.79 s).
- **Closed** — commit `17592d25` (2026-10-23): refactor(looks): Oracle over duckmcp.Session, OneSession gone, main maps the lib's errors
  - Files (`git show --name-status 17592d25`):
    - `M docs/tasks/duckmcp/22-looks-oracle-session.md`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
    - `M tools/kits/oracle.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/oracle.py`
- **Reviewed** (2026-10-24) at `6cefa11d`: no finding
