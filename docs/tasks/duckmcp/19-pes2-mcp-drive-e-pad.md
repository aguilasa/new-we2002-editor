---
id: DMCP-TASK-19
---

# DMCP-TASK-19 — `pes2`: `mcp_drive.py` e `pad.py` sobre `Session`

## Goal

`McpSession` vira camada de rota sobre `duckmcp.Session` e `pad.Live` sobre `Session.attach()`; somem os `PRESS_FRAMES`/`AFTER_FRAMES` e `STATE_DIR` duplicados, o `capitalize()` e a captura própria. As rotas produzem o mesmo PNG.

## Arquivos a criar ou modificar

- In:
  - os dois arquivos
  - a lista `PENDING` encolhida
  - `tools/duckmcp/controls.py`: o `b-stale-entry` mirava a entrada do `pad.py` que esta task remove; passa a mirar uma que só sai na DMCP-TASK-30
- Out:
  - `who_writes.py`, `drive.py` (DMCP-TASK-20)

## Done criteria

- [x] antes da mudança, `python3 tools/pes2/mcp_drive.py <cópia>.cue --screen <rota>` para `team-select`, `edit`, `result` e `replay`, com o `sha256sum` de cada PNG colado no Log; depois, os mesmos quatro digests
- [x] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue, com o `pes2` caindo nos sítios destes dois arquivos
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0

## Notes

O `pad.Live.press` pausa antes de cada aperto e o `McpSession.press` não (§4.3): a escolha se registra no Log com o porquê.

## Log de Execução

2026-10-23 — HEAD de partida `6f6d7c7b`. Emulador: o fork com MCP no `:98`, sobre a cópia `work/pes2-EsIt/…(Es,It).cue`; uma instância por vez, `cli.py procs` → `pids: []` depois de cada corrida. Save states e cartão com o mesmo `sha256sum` antes e depois de todas as corridas (nenhuma rota pediu `--save-state`).

**O que mudou.** `McpSession` é subclasse de `duckmcp.session.Session`: relógio (`pause`, `resume`, `step`, `run`), `press`, lançamento, morte na saída, `load_state` (com `settle=2`, o mesmo `step(2)` de antes) e a espera do `save_state` são da lib. Ficam no `pes2` o `SERIAL`, o `GAME_WINDOW` (passado como `match`, que o shim `fork.py` passava por default), `state_path(slot)` sobre `env.state_path(SERIAL, slot)`, a captura rotulada decodificada em `drive.Frame`, as esperas, os menus contados e as rotas. `--keep-alive` agora zera `owned`. `pad.Live` embrulha `Session.attach()`; o nome do botão é validado por `duckmcp.buttons.canonical` antes de qualquer chamada (o `BUTTONS` minúsculo e o `capitalize()` saíram). Saíram também `PRESS_FRAMES`/`AFTER_FRAMES` dos dois arquivos e `STATE_DIR`: o self-check do `mcp_drive.py` agora afirma que o par da lib é o medido (3/17), que o `match` é o título do PES2 e que `state_path` é o da lib.

**§4.3, o `pause` antes do aperto: cada um fica como estava.** `McpSession.press` segue sem `pause_first` — a sessão que ela lança já está pausada desde o `__enter__` e continua pausada entre chamadas, então a contagem de quadros começa onde a anterior parou; um `pause` a mais seria uma ida e volta inútil e não é o que as rotas mediram. `pad.Live.press` passa `pause_first=True`, porque entre dois comandos do `pad.py` o jogo corre, e sem a pausa os três quadros de aperto começariam onde o relógio estivesse. É a escolha que preserva a saída medida dos dois: os digests abaixo são de rotas que não pausam antes.

**Digests das rotas.** Comando: `DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "<cópia>.cue" --screen <rota> --out-dir <dir>` e `sha256sum *.png` no diretório. Antes, duas corridas na HEAD de partida (para ver se a rota é determinística); depois, uma na árvore entregue. **As três colunas são idênticas, arquivo por arquivo.**

```text
team-select  (antes x2 e depois: MCP DRIVE OK, 3 presses, 92 frames stepped)
5a77d7f0a8529201f72fad5fd994a84cc6613bde79d1317375bb39233b6808f3  match-submenu.png
5d2bb39992a70af033b53932d8a7a629bceed81053feee87396bd3f4d4dfdbeb  pad-assignment.png
16ebd4e1501db436d0b2088f381fc4b79ffb562efa36bab9fb4b37a7fe4374ab  team-select.png
edit  (antes x2 e depois: MCP DRIVE OK, 6 presses, 132 frames stepped)
190bbf6bed37d1be8e93d1b22432fc8141f0cc03ac041fd1b73015628efa1046  edit.png
ad17346e9cbdb71a9f73d885534d881647637aafee597f85ede960e6b2d4d16e  menu-edit.png
result  (antes x2 e depois: MCP DRIVE FAILED, ver abaixo)
62b59dc5253e55fb7fdfa5723da81dfda24dec3602397b7bc1b601c248beb7cb  match-options-lit.png
a82482387cc79b3cdf2d4c84e3cd17ee7fce434e2691e33076bce9f876543660  match-options.png
90497a1b7d6e57cce8faa8adf70c9317d631ca5087df8a6c7811be7160ba2a4b  penalty-submenu.png
fffb20923cfd08f6ac0c891887512b3aa943b526d72c3631a4f688b636845e4a  penalty-teams.png
replay  (antes x2 e depois: MCP DRIVE OK, 0 presses, 32 frames stepped)
84349ce458779d50c9afef7773aaa25913506d149f98d5163465d4ef9cfec83f  replay.png
```

**Resultado negativo: a rota `result` não chega à tela de resultado, nem antes da mudança.** As duas corridas na HEAD de partida e a de depois param no mesmo ponto, com `MCP DRIVE FAILED: Right on Dia/Noche changed nothing -- the cursor is not on the first row`. O aperto funcionou — `match-options.png` mostra `Día/Noche  Al azar` e `match-options-lit.png` mostra `Día/Noche  Día` —, mas a diferença entre os dois quadros é `0.00048095095544579156` (`drive.Frame.difference`), abaixo do `0.0005` da guarda: a troca de uma palavra não basta para ela. O defeito é da guarda da rota, anterior a esta task, e não foi tocado aqui para a migração continuar pura. A comparação possível é a dos quatro PNG que a rota grava até a falha, e ela é idêntica; o PNG da tela de resultado não existe em nenhum dos lados. Por isso o primeiro critério não está marcado.

**Exercício ao vivo do que as rotas não cobrem.** `--screen main-menu --keep-alive` → `MCP DRIVE OK … 8 presses, 160 frames stepped` e o fork de pé (`pids: [348190]`); `--measure-menu` (o `McpSession.attach`) → `the main menu has 7 rows (measured, not declared)` e `RED CASE OK: asking for 7 rows failed -- press 7 of 7 landed back on row 0`; `pad.py stats`, `pad.py press DOWN up` e `pad.py shot` respondem; `pad.py press Triangel` sai 1 com `'Triangel' is not a pad button; press_button takes one of: …`. Depois, `cli.py kill` e `pids: []`.

**`audit.py`, antes (HEAD `6f6d7c7b`) e depois (árvore entregue).** As linhas do `pes2` e o total:

```text
antes:
pes2: 37 site(s) in 4 file(s) (import 8, client 29, sys.path 0)
by category: import 19, client 180, sys.path 7
audit: 206 raw site(s) in 14 file(s)
depois:
pes2: 15 site(s) in 2 file(s) (import 4, client 11, sys.path 0)
by category: import 15, client 162, sys.path 7
audit: 184 raw site(s) in 12 file(s)
```

Os 22 sítios que saíram são os de `tools/pes2/mcp_drive.py` (14) e `tools/pes2/pad.py` (8); sobram os de `who_writes.py` e o `import savestate` do `selftest.py`, que são da DMCP-TASK-20. A `PENDING` perdeu as 22 entradas da DMCP-TASK-19, e a regra (b) imprime `PENDING lists 184 site(s) in 86 entries, audit.py counts 184`.

**Para as próximas.** (1) A guarda de `Dia/Noche` em `route_result` precisa de outra medida (a diferença real de uma troca de valor é 0,00048 no quadro inteiro) — candidata a CORR; sem ela, a Fase 5 não tem como mostrar o PNG da tela de resultado igual antes e depois. (2) O controle `b-stale-entry` do `tools/duckmcp/controls.py` mirava a linha `'from mcp import Client, NotRunning # noqa: E402', 1),` da `PENDING`, que era do `pad.py` e saiu nesta task, e o `controls.py` acusava `BROKEN b-stale-entry: old text matches 0 time(s) in selftest.py, not 1` e saía 1. O escopo da task ganhou o `controls.py` (`rite set DMCP-TASK-19 --files …` e a linha em "Arquivos") e o controle passou a mirar `'sys.path.insert(0, PES2)', 1),`, entrada do `tools/looks/oracle.py` que só sai na DMCP-TASK-30. (3) `mcp_drive.py` ainda importa `Fail`, `Skip` e `SKIP` de `drive.py`, que a DMCP-TASK-20 migra. (4) O `GAME_WINDOW` está agora em `mcp_drive.py` e no shim `fork.py`, com o mesmo valor; o do shim some com ele na DMCP-TASK-30.

**Fechamento parcial (thread principal, 2026-10-23).** Refeito na árvore entregue:

```text
$ python3 tools/duckmcp/controls.py --only b-stale-entry
red    b-stale-entry (rule b): FAIL  rule (b): no stale PENDING entry (listed, no longer found)  tools/looks/oracle.py: sys.path: sys.path.insert(0, PES2) (x1)
$ python3 tools/duckmcp/controls.py | tail -1; echo "exit=${pipestatus[1]}"
duckmcp_controls: 41 control(s), 41 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
exit=0
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/audit.py | tail -3
pes2: 15 site(s) in 2 file(s) (import 4, client 11, sys.path 0)
by category: import 15, client 162, sys.path 7
audit: 184 raw site(s) in 12 file(s)
```

A diferença da guarda, com o `drive.Frame.difference` dela sobre os PNG que a rota grava, igual nas três corridas: `before1 0.00048095095544579156`, `before2 0.00048095095544579156`, `after1 0.00048095095544579156`.

**Bloqueada** no primeiro critério, por decisão do usuário: a guarda de `Dia/Noche` vira a [CORR-DMCP-025](/docs/tasks/duckmcp/CORR-DMCP-025.md), e a task volta quando ela fechar, para medir o PNG de `result` antes (HEAD `6f6d7c7b` com o conserto) e depois. A migração entra como trabalho parcial coerente: `team-select`, `edit`, `replay` e os quatro PNG parciais de `result` com o mesmo digest.
- **blocked** (2026-10-23): criterion 1 (result route PNG before/after) cannot close: route_result stops at its Dia/Noche guard before and after the migration (difference 0.00048 < 0.0005); waits for CORR-DMCP-025. Partial work committed at 1baf69c6; team-select, edit, replay digests identical.
- **pending** (2026-10-23): CORR-DMCP-025 is done (ba7ee63a): the result route reaches its end, so criterion 1 can be measured

**Desbloqueio (2026-10-23).** A [CORR-DMCP-025](/docs/tasks/duckmcp/CORR-DMCP-025.md) fechou em `ba7ee63a`, e a task voltou a `pending` por `rite mark`. O "antes" de `result` sai de um worktree descartável na HEAD de partida `6f6d7c7b` com o diff do `ba7ee63a` aplicado ao `mcp_drive.py` antigo (`git show ba7ee63a -- tools/pes2/mcp_drive.py | git apply`, três hunks, nenhum rejeitado); o "depois" sai da árvore entregue, que já tem o conserto. Mesma cópia, mesmo `:98`:

```text
$ (worktree 6f6d7c7b + ba7ee63a) DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "<cópia Es,It>.cue" --screen result --out-dir fix-before
MCP DRIVE OK: …/fix-before  192.0s, 59 presses, 1212 frames stepped
$ (árvore entregue) DISPLAY=:98 XAUTHORITY= python3 tools/pes2/mcp_drive.py "work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" --screen result --out-dir fix-after
MCP DRIVE OK: …/fix-after  191.2s, 59 presses, 1212 frames stepped
$ diff <(cd fix-before && sha256sum *.png) <(cd fix-after && sha256sum *.png) && echo IDENTICAL
IDENTICAL
$ cd fix-after && sha256sum *.png
b7c7f8e18e726c22df8f567daf18a16dc067d0b417559a51356cb3e9568b9c26  kicker-order.png
62b59dc5253e55fb7fdfa5723da81dfda24dec3602397b7bc1b601c248beb7cb  match-options-lit.png
a82482387cc79b3cdf2d4c84e3cd17ee7fce434e2691e33076bce9f876543660  match-options.png
90497a1b7d6e57cce8faa8adf70c9317d631ca5087df8a6c7811be7160ba2a4b  penalty-submenu.png
fffb20923cfd08f6ac0c891887512b3aa943b526d72c3631a4f688b636845e4a  penalty-teams.png
7ea1a9e46012c39168190a6a15f02bc97c272095dd5fd05fce1371694952878d  result.png
```

Os quatro parciais têm os mesmos digests das corridas de antes do conserto (`after1-result`), e o `result.png` da tela de resultado é igual dos dois lados. `cli.py procs` → `pids: []` depois de cada corrida. Com isso o primeiro critério fecha: `team-select`, `edit`, `replay` e `result` com o mesmo PNG antes e depois.

Gates na árvore entregue: `python3 tools/duckmcp/selftest.py | tail -1` → `duckmcp_selftest: 435 check(s) ran, 0 failure(s)`; `python3 tools/pes2/selftest.py | tail -1` → `OK`; `python3 tools/duckmcp/audit.py | tail -1` → `audit: 169 raw site(s) in 10 file(s)` (o número caiu de 184 para 169 na DMCP-TASK-20, que veio depois; os sítios destes dois arquivos continuam fora).
- **Closed** — commit `47d953f4` (2026-10-23): docs(duckmcp): result route gives the same PNG before and after the migration
  - Files (`git show --name-status 47d953f4`):
    - `M docs/tasks/duckmcp/19-pes2-mcp-drive-e-pad.md`
