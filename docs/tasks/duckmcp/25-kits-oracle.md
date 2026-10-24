---
id: DMCP-TASK-25
---

# DMCP-TASK-25 — `kits`: `dump_slot`, `matrix_stops`, `pose_capture`, `read_frame` e `vram` sobre a lib

## Goal

`dump_slot` passa a `Session` (e ganha a guarda de joystick que não tinha); `matrix_stops` e `pose_capture` usam `duckmcp.debug`; `read_frame` usa o `frame_commands` do `looks` em vez da cópia; o empacotamento BGR555 vem do `duckmcp.vram`.

## Arquivos a criar ou modificar

- In:
  - as funções nomeadas
  - `tools/duckmcp/selftest.py`: encolher no mesmo commit as entradas do `PENDING` da regra (b) que esta task remove; sem isso o check de entrada velha fica vermelho (CORR-DMCP-023)
- Out:
  - controles e monkeypatch (DMCP-TASK-26)

## Done criteria

- [x] `ctest --test-dir build -R kits_replay` com o ambiente do perfil do `kits` no comando: mesmo veredito antes e depois, colado no Log
- [x] `grep -cE 'client\.call\(' tools/kits/*.py` dá 0
- [x] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [x] `python3 tools/kits/selftest.py` sai 0

## Notes

## Log de Execução

2026-10-24 — HEAD de partida `b5505823`. `J` abaixo é a cópia da trilha japonesa em `/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin` (a da DMCP-TASK-22), e `E` é `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue`. As corridas "antes" ao vivo rodaram sobre uma cópia da HEAD de partida (`git archive b5505823 tools src/core/include data`, extraída no scratchpad), as "depois" sobre a árvore entregue, as duas do raiz do repositório. Depois de cada corrida ao vivo, `python3 tools/duckmcp/cli.py procs` → `pids: []`. Nenhum controle físico plugado (`fork.joysticks()` → `[]`).

**O que mudou.** Em `tools/kits/oracle.py`: `dump_slot` recusa controle (`fork.refuse_joysticks()`, de `duckmcp.fork`) antes de lançar, lança e esconde a janela como antes, e dirige o cliente lançado por uma `Session(client=...)` — handshake e pausa, `load_state(slot, settle=DUMP_SETTLE)` (os mesmos 30 quadros), `step`, `dump_vram` e `capture`, que apagam o arquivo antes e recusam arquivo ausente; quem mata o fork continua sendo o `finally` da função. `matrix_stops` e `pose_capture` armam por `debug.breakpoints(game.session, …, "execute")`, retomam por `Session.resume`, esperam pelo `_wait_for_hit` do `looks` (`debug.wait_for_pause`, `HIT_POLL = 0`), leem registradores por `_gpr` e o GTE por `Session.gte_registers()`; `hx`/`register_value` são os de `duckmcp.debug`. `read_frame` é `textured_samples(looks_oracle.frame_commands(game))`, sem a cópia do passeio da lista. `load_slot` usa `Session.load_state(slot, settle=LOAD_FRAMES)`, `_edit_kit` usa `Session.dump_vram`, `edit_capture` aperta por `Oracle.hold`, `frame_now` lê `Oracle.status()`. O BGR555 sai de `duckmcp.vram`: `vram_rows` é `rows_to_bytes`, os quatro empacotamentos à mão são `to_halfword`, e `five` (e a comparação de `_outside_gaps`, que repetia a máscara) usa `COLOUR_BITS`. Em `tools/kits/replay.py`, `fork` e `savestate` vêm de `duckmcp`. Os dois arquivos põem `tools/` no fim do `sys.path` para achar o pacote.

**Decisão: a guarda do `dump_slot` mora nele, não na `Session`.** `Session(image)` recusaria controle por conta própria, e aí tirar a recusa do `dump_slot` deixaria tudo verde: o controle que a DMCP-TASK-26 planta não teria o que derrubar. É a mesma escolha que a DMCP-TASK-22 fez para o `Oracle` do `looks`. Conferido com uma sonda de rascunho, não versionada (o controle versionado é da DMCP-TASK-26): com `duckmcp.fork.joysticks` devolvendo `/dev/input/js0` e `launch` trocado por uma função que acusa o lançamento, o `dump_slot` da HEAD de partida dá `NOT refused: the fork was launched`, e o entregue dá `refused: a game controller is plugged in (/dev/input/js0): the fork's [Pad1] is SDL-0 and`.

**`kits_replay`, antes e depois.** `$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$J WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits_replay --output-on-failure`:

- antes: `1/1 Test #22: kits_replay ......................   Passed   12.14 sec` / `100% tests passed, 0 tests failed out of 1`.
- depois: `1/1 Test #22: kits_replay ......................   Passed   11.91 sec` / `100% tests passed, 0 tests failed out of 1`.

Não é pulo: `$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$J WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle python3 tools/kits/replay.py check` imprime as dez linhas `ok` e termina em `kits_replay: 0 failure(s)`, saída 0, com saída idêntica (`diff` vazio) na cópia da HEAD de partida.

**Corridas ao vivo das funções migradas**, antes e depois, cada uma com `diff` da saída inteira:

- `dump_slot`: `$ E python3 tools/kits/oracle.py --slot 3 --out <scratch>/slot3-<lado>` — saída 0 nos dois; a única diferença é o pid do fork; `control: two dumps a frame apart give the same 8 match(es)`; `vram-0.png` idêntico byte a byte (`cmp`).
- `read_frame`: `$ E python3 tools/kits/oracle.py --sleeves 5 --expect-sleeves drawn` — saída 0 nos dois; diferem só o pid e o caminho do quadro (`mean=0.348669 sd=0.116747` nos dois); `ok    154 primitive(s) sample the uniform image; sleeves drawn`.
- `pose_capture`: `$ E python3 tools/kits/oracle.py --match-pose 5 --frame-json <scratch>/pose5-<lado>.json --pair-by corners` — saída 1 nos dois, com as mesmas linhas `FAIL  outfield: section 8 is 3.77 px from the frame, over 2.00` (e 10, 12); `--pair-by corners` é relatório. A captura gravada é idêntica byte a byte (`cmp`). O `--pair-by indices` não rodou ao vivo porque grava `work/kits-pose/slot5-*.json`.
- `matrix_stops`, `_edit_kit`, `_edit_page`, `hold`: `$ E python3 tools/kits/oracle.py --edit-number 8 --button Cross --frame-json <scratch>/edit8-<lado>.json` — saída 1 nos dois, com as mesmas linhas `FAIL` (`the turn took 0 frame(s), 30 expected (slack 2)` à frente). A captura é idêntica byte a byte entre os dois lados e também igual à guardada em `work/kits-oracle/edit-8-0-Cross.json`, então o vermelho já existia antes desta task. A única diferença de saída além do pid é a média do quadro `-back` (`0.223441` antes, `0.223350` depois). Uma segunda corrida da HEAD de partida deu `0.223583`: é o relógio da espera parcial, não a migração. Os PNG e JSON que a corrida reescreve em `work/kits-oracle/` e `work/kits-pose/` foram restaurados das cópias tiradas antes.
- `replay.py anime-ram` (o `savestate` da lib), sem emulador: `$ WE2002_LOOKS_IMAGE=$J python3 tools/kits/replay.py anime-ram work/kits-states/SLPM-87056_9.sav work/kits-states/SLPM-87056_10.sav` — saída 0 e idêntica nos dois lados, `396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)` para cada estado.
- BGR555, sem emulador: `$ WE2002_LOOKS_IMAGE=$J python3 tools/kits/oracle.py --png $PWD/work/kits-oracle/match-3/vram-0.png --lines` — saída 0 e idêntica nos dois lados.

**Não rodados ao vivo**: `frame_now` (só pelo `replay.py capture`), `--attach`, `--keeper-armband`, `--replay*`. A chamada que sai é a mesma de antes, e a espera armada termina pausada, como antes.

**`audit.py`, antes** (HEAD `b5505823`, antes de qualquer edição): os sítios que saíram, contados por chave (`comm -23` entre as linhas `tools/` de antes e de depois, sem número de linha, `uniq -c | sort -rn`), e os totais:

```
      4 tools/kits/oracle.py: client: client.call("breakpoint", action="clear")
      3 tools/kits/oracle.py: client: client.call("pause")
      2 tools/kits/oracle.py: client: registers = client.call("read_registers", group="gpr")
      2 tools/kits/oracle.py: client: client.call("frame_step")
      2 tools/kits/oracle.py: client: client.call("continue")
      2 tools/kits/oracle.py: client: client.call("breakpoint", action="add", type="execute",
      1 tools/kits/replay.py: import: import savestate # tools/pes2
      1 tools/kits/replay.py: import: import fork # tools/pes2
      1 tools/kits/oracle.py: import: import fork
      1 tools/kits/oracle.py: client: return game.client.call("get_status").get("frame_number")
      1 tools/kits/oracle.py: client: game.client.call("press_button", button=button,
      1 tools/kits/oracle.py: client: game.client.call("load_state", slot=slot)
      1 tools/kits/oracle.py: client: game.client.call("dump_vram", path=path, format="png")
      1 tools/kits/oracle.py: client: client.call("take_screenshot", path=shot)
      1 tools/kits/oracle.py: client: client.call("load_state", slot=slot)
      1 tools/kits/oracle.py: client: client.call("get_gte_registers")),
      1 tools/kits/oracle.py: client: client.call("dump_vram", path=path, format="png")
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 4 site(s) in 4 file(s) (import 0, client 0, sys.path 4)
by category: import 4, client 23, sys.path 7
audit: 34 raw site(s) in 9 file(s)
```

**`audit.py`, depois** (árvore entregue). Em `[kits]` sobram os dois `sys.path` da DMCP-TASK-30 e o `import fork` do `kits/selftest.py`, da DMCP-TASK-26:

```
[kits]
tools/kits/oracle.py:133: sys.path: sys.path.insert(0, _path)
tools/kits/selftest.py:2061: import: import fork # tools/pes2, the shim over duckmcp.fork
tools/kits/core/tex.py:35: sys.path: sys.path.insert(0, _path)

kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 3 site(s) in 3 file(s) (import 1, client 0, sys.path 2)
looks: 4 site(s) in 4 file(s) (import 0, client 0, sys.path 4)
by category: import 1, client 0, sys.path 7
audit: 8 raw site(s) in 8 file(s)
```

**`PENDING`.** Saíram as 17 entradas da DMCP-TASK-25 (26 sítios), ou seja, todas as que a task tinha. `$ python3 tools/duckmcp/selftest.py` → `ok    rule (b): no stale PENDING entry (listed, no longer found)` / `ok    rule (b): PENDING lists 8 site(s) in 8 entries, audit.py counts 8` / `duckmcp_selftest: 435 check(s) ran, 0 failure(s)`, saída 0. `$ python3 tools/duckmcp/controls.py; echo exit $?` → `duckmcp_controls: 42 control(s), 42 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 3/3, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1`, `exit 0`. Nenhum controle da regra (b) mirava entrada removida.

**Critérios.**

- `kits_replay`: o mesmo `Passed` antes e depois (acima).
- `$ grep -cE 'client\.call\(' tools/kits/*.py` → `tools/kits/cli.py:0`, `tools/kits/replay.py:0`, `tools/kits/controls.py:0`, `tools/kits/selftest.py:0`, `tools/kits/confront.py:0`, `tools/kits/ui_check.py:0`, `tools/kits/oracle.py:0`, `tools/kits/gen_tables.py:0`.
- `audit.py` antes e depois: acima.
- `$ python3 tools/kits/selftest.py` → `..... 87 of 87 controls red` / `controls: 0 failure(s)` / `kits_selftest: 0 failure(s)`, saída 0, em 6:11. Nenhum controle nem monkeypatch do `kits` mirava código movido. O `replay-capture-joystick-late` continua achando `fork.refuse_joysticks()` no `run_capture`.
- `$ ctest --test-dir build -R 'duckmcp_selftest|kits_selftest|tasks'` → `100% tests passed, 0 tests failed out of 3` (`kits_selftest` 353.29 s).
