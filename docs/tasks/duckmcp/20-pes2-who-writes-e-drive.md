---
id: DMCP-TASK-20
---

# DMCP-TASK-20 — `pes2`: `who_writes.py`, `drive.py` e `selftest.py` sobre `debug` e `env`

## Goal

`who_writes.py` vira CLI fina sobre `duckmcp.debug.who_writes`; `drive.py` tira `SKIP`, `Fail`, `Skip`, `STATE_DIR`, o AppImage e o display do `env`, e passa a zerar `XAUTHORITY` só no `:98`; `drive.preflight` usa `env.is_roms`; o `selftest.py` do `pes2` deixa de rodar os self-checks que migraram.

## Arquivos a criar ou modificar

- In:
  - os três `.py` e o `boot_check.sh`
  - `tools/pes2/check_image.py`: o `SKIP = 77` dele é um dos alvos do `grep` do terceiro critério
  - `tools/duckmcp/controls.py`: os controles da regra (b) que miram entradas da `PENDING` desta task (`b-duplicate-key`) passam a mirar entradas que sobrevivem
- Out:
  - o caminho do AppImage oficial, que fica (§0)

## Done criteria

- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] `python3 tools/pes2/selftest.py` sai 0
- [x] `grep -nE 'class (Fail|Skip)|^SKIP = ' tools/pes2/*.py` não acha nada
- [x] `python3 tools/duckmcp/audit.py` colado no Log antes e depois da mudança, na HEAD entregue
- [x] `ctest --test-dir build -R pes2_boot` com `PES2_IMAGE=<cópia>.cue DISPLAY=:98 XAUTHORITY=` no comando: mesmo veredito de antes, as duas linhas coladas no Log

## Notes

## Log de Execução

2026-10-23 — HEAD de partida `e2dbefe2`, árvore com as mudanças desta task.

**O que mudou.** `who_writes.py` virou CLI fina sobre `duckmcp.debug.who_writes`: anexa com `Session.attach()`, passa `before=4, after=4` (a janela `pc - 16`, 8 linhas, que o CLI sempre imprimiu; o default da lib é 8 + 4) e imprime o mesmo relatório. `hx`, `parse_address`, `split_store`, `register_value`, `is_paused` e `Fail` continuam importáveis dele, reexportados da lib, porque `tools/kits/oracle.py` e `tools/looks/oracle.py` os usam. Duas diferenças de saída, as duas da lib: a linha `the watchpoint fired after Ns` virou `fired at <pc>` (a `debug.who_writes` não devolve o tempo), e a corrida termina **pausada** (DMCP-TASK-16). O `self_check` dele passou a provar só a camada do CLI — relatório e códigos de saída sobre um cliente falso —; o que ele provava antes (endereços, stores, registradores, as duas esperas) mora nas linhas `debug:` do `duckmcp/selftest.py`.

`drive.py`: `SKIP`, `Skip` e `Fail` são os de `duckmcp.errors`, reexportados (o `mcp_drive.py` os importa de `drive` e não foi tocado); `STATE_DIR` e `state_path` saem de `env.savestates_dir()`/`env.state_path`; o AppImage de `env.appimage()` — o caminho do AppImage oficial continua o binário do `drive.py` (§0) —; o display de `env.display()`; os três ambientes de X (`xdotool`, `import`, o `preflight`) de `env.x_env`, que zera `XAUTHORITY` **só no `:98`** (§4.3, terceiro item); o `preflight` recusa `roms/` por `env.is_roms`. O lançador recebe `DUCKSTATION_DISPLAY` além de `PES2_DISPLAY`, porque o `run_duckstation.sh` lê o nome novo primeiro e um herdado ganharia do display da sessão. `boot_check.sh` ganhou a mesma regra numa função `x_env` (antes zerava em todo display). `check_image.py` tira o `SKIP` de `duckmcp.errors`.

`tools/pes2/selftest.py` deixou de rodar `mcp.self_check` e `savestate.self_check` — os dois shims só repassavam para a lib, cujos checks já rodam no `duckmcp_selftest` — e o `who_writes` agora roda o check novo do CLI. O `fork.py` ficou: o shim tem checks próprios (o `match` do PES2 e as costuras que o selftest do `kits` usa). A `PENDING` perdeu as 12 entradas (15 sítios) da DMCP-TASK-20. O controle `b-duplicate-key` mirava uma entrada do `who_writes.py` e passou a mirar `tools/kits/core/tex.py` (DMCP-TASK-30, a última migração); como toda entrada da 30 conta 1, a divisão é 1 + 0, o multiconjunto não muda e a linha de contagem zero fica vermelha ao lado da exigida.

**`audit.py`, antes** (HEAD `e2dbefe2`, antes de qualquer edição):

```
[pes2]
tools/pes2/selftest.py:260: import: import savestate # noqa: E402
tools/pes2/who_writes.py:55: import: import mcp # noqa: E402
tools/pes2/who_writes.py:56: import: from mcp import NotRunning, ToolError # noqa: E402
tools/pes2/who_writes.py:59: import: import fork # noqa: E402
tools/pes2/who_writes.py:214: client: client.call("continue")
tools/pes2/who_writes.py:224: client: if is_paused(client.call("wait_for_pause")):
tools/pes2/who_writes.py:236: client: client.call("press_button", button=nudge.capitalize()
tools/pes2/who_writes.py:241: client: if is_paused(client.call("wait_for_pause")):
tools/pes2/who_writes.py:250: client: if is_paused(client.call("wait_for_pause")):
tools/pes2/who_writes.py:264: client: client = mcp.Client()
tools/pes2/who_writes.py:268: client: client.call("breakpoint", action="clear")
tools/pes2/who_writes.py:269: client: client.call("breakpoint", action="add", type="write", address=hx(address))
tools/pes2/who_writes.py:277: client: registers = client.call("read_registers", group="gpr")
tools/pes2/who_writes.py:286: client: window = client.call("disassemble", address=hx(pc - 16), count=8)
tools/pes2/who_writes.py:326: client: client.call("breakpoint", action="clear")
pes2: 15 site(s) in 2 file(s) (import 4, client 11, sys.path 0)
by category: import 15, client 162, sys.path 7
audit: 184 raw site(s) in 12 file(s)
```

**`audit.py`, depois** (árvore entregue): nenhuma seção `[pes2]` e nenhuma linha `tools/pes2/`; as linhas por projeto e o total:

```
kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 139 site(s) in 5 file(s) (import 7, client 128, sys.path 4)
by category: import 11, client 151, sys.path 7
audit: 169 raw site(s) in 10 file(s)
```

E a regra (b): `ok    rule (b): PENDING lists 169 site(s) in 74 entries, audit.py counts 169`.

**`pes2_boot`**, com `PES2_IMAGE="$PWD/work/pes2-EsIt/Pro Evolution Soccer 2 (Europe) (Es,It).cue" DISPLAY=:98 XAUTHORITY= ctest --test-dir build -R pes2_boot`:

- antes: `1/1 Test #13: pes2_boot ........................   Passed   61.53 sec` / `100% tests passed, 0 tests failed out of 1`
- depois: `1/1 Test #13: pes2_boot ........................   Passed   61.56 sec` / `100% tests passed, 0 tests failed out of 1`

**Critérios.**

- `python3 tools/duckmcp/selftest.py` → `duckmcp_selftest: 435 check(s) ran, 0 failure(s)`, saída 0.
- `python3 tools/pes2/selftest.py` → última linha `OK`, saída 0; as linhas do laço: `ok   fork.py shim: PES2 defaults and seams`, `ok   mcp_drive.py routes and thresholds`, `ok   who_writes.py report and exit codes`.
- `grep -nE 'class (Fail|Skip)|^SKIP = ' tools/pes2/*.py` → nada, saída 1.

**Vermelhos vistos.** O check da janela do `who_writes` nasceu tautológico (comparava com `BEFORE + AFTER`) e ficou verde com `BEFORE = 8` plantado; reescrito com os números literais, o mesmo plantio dá `FAIL   the window is the 8 rows from pc - 16 this CLI always printed  (12 rows, first ['  0x80083558  nop'])` e `SELF-CHECK FAILED`. O controle retargetado: `python3 tools/duckmcp/controls.py --only b-duplicate-key` → `red    b-duplicate-key (rule b): FAIL  rule (b): no key appears twice in PENDING  [('tools/kits/core/tex.py', 'sys.path', 'sys.path.insert(0, _path)')]`. A bateria inteira, `python3 tools/duckmcp/controls.py` → `duckmcp_controls: 41 control(s), 41 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1`, saída 0.

**Ao vivo.** Com o fork de pé na cópia (`cli.py launch … --match '^Pro Evolution Soccer 2$'`), `python3 tools/pes2/who_writes.py 0x801FFF8C --width 4 --timeout 20` (uma palavra de pilha) → `written by   0x80112D90  sw s3, 0x0000001C(sp)` / `sp = 0x801FFF70, 0x801FFF70 + 0x0000001C = 0x801FFF8C` / `called from  ra = 0x8011384C`, saída 0; depois, `breakpoint action=list` → `[]` e `get_status` → `"state": "paused"`. Sem emulador, o mesmo comando sai 77 com `skipping: no MCP server at http://127.0.0.1:2346/mcp …`. `cli.py procs` → `pids: []` depois de cada corrida.

**Resultado negativo, anterior a esta task.** `drive.py <cópia>.cue --screen title` (o AppImage oficial, `:98`) falha igual na árvore entregue e no `drive.py` da HEAD `e2dbefe2`: `DRIVE FAILED: no frame matched mean=0.55 sd=0.341 (+-0.02) within 240s; closest was mean=0.160099 sd=0.316763` (HEAD: `mean=0.160117 sd=0.316803`). A janela é achada e capturada nos dois (`window 2097159 on :98`), então o `x_env` funciona; o que não bate é a assinatura do título, e não foi tocada aqui.
- **Closed** — commit `be5e5484` (2026-10-23): refactor(pes2): who_writes over duckmcp.debug, drive and boot_check over env and errors
  - Files (`git show --name-status be5e5484`):
    - `M docs/tasks/duckmcp/20-pes2-who-writes-e-drive.md`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
    - `M tools/pes2/boot_check.sh`
    - `M tools/pes2/check_image.py`
    - `M tools/pes2/drive.py`
    - `M tools/pes2/selftest.py`
    - `M tools/pes2/who_writes.py`
- **Reviewed** (2026-10-23) at `9bd20b79`: CORR-DMCP-028
