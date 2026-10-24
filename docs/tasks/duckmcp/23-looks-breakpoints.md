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

- [x] `python3 tools/looks/oracle.py --screen` antes e depois, ambos sem diferença contra `tools/looks/screen.json`
- [x] `python3 tools/looks/oracle.py --pose 1` dá as mesmas matrizes antes e depois (o `diff` dos JSONs de `work/looks-pose/` vazio)
- [x] `grep -cE 'call\("breakpoint"' tools/looks/*.py` dá 0
- [x] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [x] `python3 tools/looks/selftest.py` sai 0

## Notes

O `_wait_for_hit` sonda sem dormir; o intervalo novo se escolhe medindo que a contagem de paradas do `--pose` não muda.

## Log de Execução

2026-10-23 — HEAD de partida `4d9f99ee`. `J` abaixo é a cópia da trilha japonesa em `/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin` (a mesma da DMCP-TASK-22), e `E` é `WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`. Depois de cada corrida ao vivo, `python3 tools/duckmcp/cli.py procs` → `pids: []`.

**O que mudou.** Em `tools/looks/oracle.py`, `_wait_for_hit` é `debug.wait_for_pause(game.session, s, interval=HIT_POLL, required=False) is not None`, e com isso confere a vida do processo a cada volta (armadilha 35: morte no meio é `Fail`, não silêncio). `catch_write` é `debug.who_writes`, com as janelas do próprio módulo (`WINDOW_BEFORE`, `WINDOW_AFTER`, `CALLER_BEFORE`) e `press_frames=CONFIRM_FRAMES`; `_stops` é `debug.stops` (`seconds=CYCLE_SECONDS`); `_watch_reads` é `debug.watch_reads`. Os laços `gpu_list_heads`, `_burst`, `krom_answers`, `_fired_among`, `_pose_cycle`, `_camera_matrix`, `_walk_stops`, `pose_builds`, `capture_camera` e `_camera_chain` armam por `debug.breakpoints(game.session, …)`, retomam por `Session.resume`, leem registradores por `_gpr` (`Session.call("read_registers")`), o quadro por `Oracle.status()`, o GTE por `Session.gte_registers()`, e apertam por `Oracle.hold`. O `--help-box` usa `debug.vram_watch` e `debug.last_vram_hit`. Em `tools/looks/confront.py`, `game_at` e `walk_photo` armam por `debug.breakpoints`, `still_frame` usa `Session.dump_vram`, e o `main` passa a responder 1 a `Fail`/`NotRunning`/`ToolError` com `confront FAILED: <Tipo>: …`, como o do `oracle` (antes, uma falha da lib saía em traceback). A análise de pose, câmera e tela não mudou.

**Toda espera armada termina pausada.** Os que antes saíam rodando eram `catch_write`, `_burst`, `_help_writes` (fim do `vram_watch`), `game_at` e `walk_photo`. Conferido caso a caso: os chamadores seguintes já pausam (`load_looks`, `restore_state`, `step`) ou capturam a tela (`_burst` → `capture`), e `game_at`/`walk_photo` já estavam parados na própria parada, de onde o `step(1)` segue.

**`_fired_among` conta pelo `pc` de cada parada**, não por `breakpoint list`: a lib não tem listagem de breakpoint de execução e o critério 3 não deixa chamada crua. Numa parada de execução o `pc` é o endereço armado (é assim que `_pose_cycle` separa os dois), e uma parada por `continue` é um acerto. Medido: o `--pose 1` imprime a mesma linha antes e depois, `5 run on this screen: 0x80012168 x18, 0x8001229C x18, 0x8003C990 x2, 0x80010E38 x1, 0x800407C0 x1`.

**`catch_write(..., required=False)`.** O `check_hair` já chamava assim e a assinatura não aceitava `required` (um `TypeError` latente). Agora ela aceita: com `required` falso, "nothing wrote" vira `None`, e a morte do emulador continua sendo `Fail`. Não rodou ao vivo.

**Intervalo (§4.3).** `HIT_POLL = 0`, ou seja, sem dormir, como a cópia substituída. Medido com `$ E python3 tools/looks/oracle.py --pose 1`: antes `0x80012168: 207 stop(s) before the sequence repeated`; depois, em duas corridas, `207` e `207`. As linhas de `--pose 1` antes e depois são idênticas, tirando pid e relógio (`diff` vazio). Nenhum outro intervalo foi medido. Um sono antes de cada volta poria o seu tamanho sob cada uma das milhares de paradas do `--screen`.

**`--pose 1`, matrizes.** `$ E python3 tools/looks/oracle.py --pose 1 0 20 40 60 80 100 120 140`, antes de qualquer edição e na árvore entregue, os dois com `oracle --pose: 0 problem(s) over 8 frame(s) and 1 slot(s)` e saída 0. Os oito `work/looks-pose/slot1-frame*.json` foram copiados para `…/scratchpad/dmcp23/pose-before/` e `pose-after/`, e `diff -r pose-before pose-after` deu saída 0, sem linha nenhuma.

**`--screen`.** Antes: a corrida da DMCP-TASK-22, `screen measured in 2702s` / `oracle --screen: 0 difference(s) from screen.json`. `git diff --quiet 17592d25 HEAD -- tools/looks/` sai 0, então foi feita sobre a mesma árvore `tools/looks/` da HEAD de partida. Depois: `$ E python3 tools/looks/oracle.py --screen` → `screen measured in 3137s` / `oracle --screen: 0 difference(s) from screen.json`, saída 0. Os 435 s a mais vêm, ao que parece, da sonda de vida que a espera da lib roda a cada volta não pausada (`pgrep`). A contagem de paradas não muda.

**`--check-live`.** `$ E python3 tools/looks/oracle.py --check-live` → `shot slot1-goalkeeper  mean=0.182425 sd=0.189376`, `shot slot2-outfield  mean=0.183158 sd=0.190350`, `the plate differs by 0.119963 between the slots`, `203 of 36072 byte(s) differ`, `20 of 64800 byte(s) differ`, `Right moved it by 0.108086`, `oracle --check-live: 0 failure(s)`, saída 0. São os números da DMCP-TASK-22.

**Não rodados ao vivo.** `--hair` (`catch_write`), `check_writes` (`_burst`), `--help-box`, `--walk`/`--walk-watch`, `--rhythm`, `--camera`/`--closeups`, `--stature` e os `--silhouette*` do `confront`. Nesses, a chamada ao servidor é a mesma de antes; o que muda é a pausa na saída (ver acima).

**`audit.py`, antes** (HEAD `4d9f99ee`, antes de qualquer edição). Abaixo, os sítios que saíram, contados por chave (`comm -23` entre as linhas `tools/` do `audit.py` de antes e de depois, sem número de linha, `uniq -c | sort -rn`), seguidos dos totais:

```
     27 tools/looks/oracle.py: client: client.call("breakpoint", action="clear")
     17 tools/looks/oracle.py: client: client.call("continue")
     11 tools/looks/oracle.py: client: client.call("pause")
     11 tools/looks/oracle.py: client: client.call("breakpoint", action="add", type="execute",
      9 tools/looks/oracle.py: client: registers = client.call("read_registers", group="gpr")
      4 tools/looks/confront.py: client: client.call("breakpoint", action="clear")
      2 tools/looks/oracle.py: client: listed = client.call("breakpoint", action="list")
      2 tools/looks/oracle.py: client: client.call("press_button", button=button,
      2 tools/looks/confront.py: client: client.call("continue")
      2 tools/looks/confront.py: client: client.call("breakpoint", action="add", type="execute",
      1 tools/looks/oracle.py: client: window = client.call(
      1 tools/looks/oracle.py: client: watch = client.call("vram_watch", action="add",
      1 tools/looks/oracle.py: client: seen.append(gte_projection(client.call("get_gte_registers")))
      1 tools/looks/oracle.py: client: reply = client.call(
      1 tools/looks/oracle.py: client: out.append(read(client.call("read_registers", group="gpr")))
      1 tools/looks/oracle.py: client: out.append((client.call("get_status")["frame_number"], pair))
      1 tools/looks/oracle.py: client: if who_writes.is_paused(game.client.call("wait_for_pause")):
      1 tools/looks/oracle.py: client: if not who_writes.is_paused(client.call("wait_for_pause")):
      1 tools/looks/oracle.py: client: hit = client.call("vram_watch", action="last_hit")
      1 tools/looks/oracle.py: client: game.client.call("continue")
      1 tools/looks/oracle.py: client: "frame_number": client.call("get_status").get("frame_number"),
      1 tools/looks/oracle.py: client: client.call("vram_watch", action="remove",
      1 tools/looks/oracle.py: client: client.call("read_registers", group="all"), "pc")
      1 tools/looks/oracle.py: client: client.call("press_button", button=press,
      1 tools/looks/oracle.py: client: client.call("press_button", button="Down", duration_frames=CONFIRM_FRAMES)
      1 tools/looks/oracle.py: client: client.call("breakpoint", action="add", type="write",
      1 tools/looks/oracle.py: client: client.call("breakpoint", action="add", type="read",
      1 tools/looks/confront.py: client: registers = client.call("read_registers", group="gpr")
      1 tools/looks/confront.py: client: number = client.call("get_status")["frame_number"]
      1 tools/looks/confront.py: client: game.client.call("dump_vram", path=path, format="png")
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 111 site(s) in 5 file(s) (import 0, client 107, sys.path 4)
by category: import 4, client 130, sys.path 7
audit: 141 raw site(s) in 10 file(s)
```

**`audit.py`, depois** (árvore entregue). Em `[looks]` sobram só os quatro `sys.path`, que não são desta task:

```
tools/looks/atlas.py:105: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
tools/looks/iso_source.py:27: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pes2"))
tools/looks/oracle.py:75: sys.path: sys.path.insert(0, PES2)
tools/looks/sprites.py:45: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pes2"))

kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 4 site(s) in 4 file(s) (import 0, client 0, sys.path 4)
by category: import 4, client 23, sys.path 7
audit: 34 raw site(s) in 9 file(s)
```

**`PENDING`.** Saíram as 30 entradas da DMCP-TASK-23, com 107 sítios ao todo, ou seja, todas as que a task tinha. `python3 tools/duckmcp/selftest.py` → `ok    rule (b): no stale PENDING entry (listed, no longer found)` / `ok    rule (b): PENDING lists 34 site(s) in 25 entries, audit.py counts 34` / `duckmcp_selftest: 435 check(s) ran, 0 failure(s)`, saída 0. `python3 tools/duckmcp/controls.py; echo exit $?` → `duckmcp_controls: 42 control(s), 42 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 3/3, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1`, `exit 0`. Nenhum controle da regra (b) mirava entrada removida.

**Critérios.**

- `grep -cE 'call\("breakpoint"' tools/looks/*.py` → `0` nos 25 arquivos, `tools/looks/oracle.py:0` e `tools/looks/confront.py:0` entre eles.
- `python3 tools/looks/selftest.py` → `..... 113 of 113 controls red` / `controls: 0 failure(s)` / `looks_selftest: 0 failure(s)`, saída 0. É a mesma contagem da DMCP-TASK-22: nenhum controle do `looks` mirava código movido (`grep` dos nomes migrados em `tools/looks/controls.py` não acha nada), então `controls.py` ficou como estava.
- `python3 tools/looks/oracle.py --check` → `oracle.py: 0 failure(s)`, e `python3 tools/looks/confront.py --check` → `confront.py: 0 failure(s)`, os dois com saída 0.
- `ctest --test-dir build -R 'duckmcp_selftest|looks_selftest|tasks'` → `100% tests passed, 0 tests failed out of 3`.
