---
id: DMCP-TASK-15
---

# DMCP-TASK-15 — Fechamento da Fase 3 — as primitivas

## Goal

A Fase 3 (as primitivas) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 3 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
  - `tools/duckmcp/live.py`, estendido com `read_ram`, `dump_vram` e `game()` — o critério 3 pede, e por isso a task declara o arquivo e os recursos `emulador` e `tela` (`rite set`, 2026-10-22)
- Out:
  - código novo

## Done criteria

- [x] `rite status --cycle duckmcp` mostra as tasks da Fase 3 `done` e revistas, com nenhuma CORR aberta delas
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `duckmcp_live` estendido com `read_ram` (2 MiB), `dump_vram` (1024×512) e `game()` passa, saída colada no Log
- [x] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

2026-10-22 — HEAD de trabalho `0456371f` (depois das CORR-DMCP-012 a 016).

- `rite status --cycle duckmcp` → `tasks: 14 done, 1 in-progress, 17 pending`, `review queue: 0`, `open fixes: critical 0, high 0, medium 0, low 0`. No `progress.json`: DMCP-TASK-12, 13 e 14 `done`, `reviewed_on 2026-10-22`; no `fixes.json`: CORR-DMCP-012 (origem 12), 013, 014 e 015 (origem 13) e 016 (origem 14), todas `done`.
- `python3 tools/duckmcp/selftest.py --quiet; echo self=$?` → `duckmcp_selftest: 361 check(s) ran, 0 failure(s)`, `self=0`.
- `ctest --test-dir build -R '^tasks$'` → `1/1 Test #6: tasks ... Passed 4.99 sec`.

**O `duckmcp_live` estendido.** `live.run` passa a envolver o mesmo cliente numa `Session` (`Session(client=client)`, que não é dona do processo — quem mata continua sendo o `finally` do `run`) e chama `read_back`: `read_ram(psx.RAM_BASE, psx.RAM_SIZE)`, `dump_vram` para um PNG temporário decodificado por `png.read_png`, e `game()`. Passa só se, além do `frame_step`, a RAM vier com `psx.RAM_SIZE` bytes, a VRAM com `psx.VRAM_WIDTH` x `psx.VRAM_HEIGHT` e `game()` der um serial. Nenhum serial esperado no código: a regra (c) não deixa, e a lib não sabe que disco é.

`DUCKSTATION_TEST_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= ctest --test-dir build -R duckmcp_live -V`:

```text
25: duckmcp_live: /home/ingmar/desenvolvimento/github/new-we2002-editor/work/looks-disc/we2002-english.cue, 5 steps
25:   tools declared: 95
25:   frame_number 76 -> 81 after 5 frame_step
25:   read_ram: 2097152 bytes from 0x80000000
25:   dump_vram: 1024x512
25:   game(): serial='SLPM-87056' title='ワールド・サッカー・ウイニング・イレブン２００２'
25: duckmcp_live: ok -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 76->81; ram=2097152 vram=1024x512 serial=SLPM-87056
1/1 Test #25: duckmcp_live .....................   Passed    4.48 sec
```

É a primeira medida ao vivo do `game()`: o `get_status` traz `game_serial` e `game_title`, como o esquema dizia na DMCP-TASK-12. O serial é o japonês (`SLPM-87056`) porque a tradução inglesa mantém o executável.

Vermelho visto: com a VRAM esperada trocada por `(psx.VRAM_WIDTH, psx.VRAM_HEIGHT + 1)` no `live.py`, `DUCKSTATION_TEST_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/duckmcp/live.py` → `duckmcp_live: FAIL -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 42->47; ram=2097152 vram=1024x512 serial=SLPM-87056`, `exit=1`; arquivo restaurado da cópia (`cmp` igual), e a mesma corrida → `duckmcp_live: ok -- ...`, `exit=0`. `python3 tools/duckmcp/cli.py procs` antes e depois de todas as corridas → `pids: []`.

Verificações da Fase 3 do perfil, uma a uma:

- `Session.press` com `duration_frames`: `ok    session: press always sends duration_frames (pitfall 36)` no selftest acima.
- `png.py` e `vram.py` em ida e volta, `gpu.py` recusando laço: `ok    vram: to_halfword(to_rgb(h)) == h for all 32768 values`, `ok    gpu: walk refuses a list looping back to its head as a loop`, `... to the middle as a loop`, `ok    gpu: walk sees a loop through two mirrors`, e as linhas `png: filter 0..4` do mesmo selftest.
- `savestate.py` com histórico: `git log --follow --oneline tools/duckmcp/savestate.py | tail -1` → `d9d090e9 feat(pes2): read PSX RAM out of a save state, and drop the emulator fork`; `grep -nE '^class|^def' tools/pes2/savestate.py` → só `34:def self_check(tmpdir=None, verbose=True):`, o adaptador do contrato antigo.
- `duckmcp_live` com 2 MiB de RAM, 1024×512 de VRAM e serial pelo `game()`: a corrida acima.

`python3 tools/duckmcp/controls.py > /dev/null; echo ctl=$?` → `ctl=0`.

Sweep: `live.py` mudou de contrato (linha final e o que afirma). O docstring dele foi atualizado; o §5.1 do plano já descrevia RAM, VRAM e `game()` no `duckmcp_live` — sem outra menção a corrigir.
