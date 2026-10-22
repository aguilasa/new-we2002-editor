---
id: DMCP-TASK-02
---

# DMCP-TASK-02 — `audit.py` — os sítios crus de MCP por projeto, o número do antes

## Goal

Existe `tools/duckmcp/audit.py`, a sonda versionada da regra (b) do §3.3: varre `tools/` fora de `tools/duckmcp/` e imprime, por projeto e por arquivo, os imports de `mcp`/`fork`/`savestate` de `tools/pes2/`, os `.client.call(` e `Client(` crus, e os `sys.path.insert` que apontam para `tools/pes2` ou `tools/looks`. O número que ele imprime nesta task é o "antes" do ciclo.

## Arquivos a criar ou modificar

- In:
  - `tools/duckmcp/audit.py`
  - um check no `selftest.py` que roda o audit sobre uma árvore sintética
- Out:
  - fazer a regra (b) falhar — ela só vira gate na Fase 4

## Done criteria

- [x] `python3 tools/duckmcp/audit.py` sai 0 e a última linha dá o total; a saída inteira colada no Log
- [x] `python3 tools/duckmcp/audit.py --json` dá o mesmo total que o modo texto
- [x] o selftest roda o audit sobre uma árvore temporária com um `import fork` plantado e exige contagem 1, visto no Log
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram

## Notes

Os números do §1.2 do plano vieram de leitura, não desta ferramenta; o Log não os repete.

## Log de Execução

### 2026-10-22

Criado `tools/duckmcp/audit.py`, só stdlib. Varre `tools/` (ou `--root`), pulando `tools/duckmcp/` e `__pycache__`, e conta três categorias de sítio, cada uma separada e somadas no total:

- `import` — `import`/`from … import` de `mcp`, `fork`, `savestate`, em nível de módulo ou de função, lidos por `ast`. Os três módulos em si não contam (viram shims); qualquer outro arquivo do projeto que os hospeda conta (`pad.py`, `who_writes.py`, `mcp_drive.py`, `selftest.py`).
- `client` — `client.call(`, `<x>.client.call(` e `Client(`, por `ast`, fora do módulo que define `Client`. O `fork.py` conta: as duas aberturas de sessão dele são sítio a migrar.
- `sys.path` — `sys.path.insert` cujo alvo nomeia outro projeto que carrega o caminho do emulador. O alvo é resolvido pelos nomes que a chamada usa (o laço `for _sub in (...)`, a variável montada dele), só por ligação de nome inteiro — `os.environ[k] = v` não liga `os`, e esse falso positivo apareceu na primeira corrida (`kits/selftest.py:46`, `KITS_DIR`) e foi consertado, com caso no `self_check`.

Uma decisão de desenho: o audit **não contém nome de projeto**, por causa da regra (c) do §3.3, que vale para todo arquivo de `tools/duckmcp/`. Quem hospeda os módulos é **achado** — o diretório sob a raiz que tem `mcp.py`, `fork.py` e `savestate.py` —, e um projeto "carrega o caminho do emulador" se hospeda os módulos ou os importa. Hoje isso dá `pes2`, `looks` e `kits`.

Arquivo que não faz parse cai num varredor por regex linha a linha e é anunciado na saída; nesta árvore nenhum caiu. A saída sai 0 sempre (é sonda, não gate — o gate da regra (b) é a DMCP-TASK-17), e 2 só com `--root` que não é diretório. `importlib` por caminho (`kits/replay.py`, `kits/oracle.py`, `kits/selftest.py`) não é categoria: o pedido da task são os três padrões acima.

O `selftest.py` ganhou o `audit.self_check()`, que monta três árvores sintéticas num diretório temporário: limpa (os módulos importando uns aos outros, um `import fork` dentro de `duckmcp/` e outro dentro de `__pycache__/`, todos não contados) dá 0; a mesma com um `import fork` plantado em `proj/a.py` dá 1; e uma com um sítio de cada categoria — import dentro de função e alvo de `sys.path` resolvido por laço — dá `import 1, client 3, sys.path 1`.

**O número do antes.** Saída inteira:

```
$ python3 tools/duckmcp/audit.py; echo exit=$?
audit: root /home/ingmar/desenvolvimento/github/new-we2002-editor/tools, 114 file(s) scanned, modules hosted by pes2

[kit2d]
tools/kit2d/selftest.py:40: sys.path: sys.path.insert(0, os.path.join(TOOLS_DIR, "pes2"))

[kits]
tools/kits/oracle.py:133: sys.path: sys.path.insert(0, _path)
tools/kits/oracle.py:429: import: import fork
tools/kits/oracle.py:437: client: client.call("pause")
tools/kits/oracle.py:438: client: client.call("load_state", slot=slot)
tools/kits/oracle.py:440: client: client.call("frame_step")
tools/kits/oracle.py:442: client: client.call("frame_step")
tools/kits/oracle.py:446: client: client.call("dump_vram", path=path, format="png")
tools/kits/oracle.py:451: client: client.call("take_screenshot", path=shot)
tools/kits/oracle.py:624: client: game.client.call("load_state", slot=slot)
tools/kits/oracle.py:1142: client: client.call("breakpoint", action="clear")
tools/kits/oracle.py:1143: client: client.call("breakpoint", action="add", type="execute",
tools/kits/oracle.py:1149: client: client.call("continue")
tools/kits/oracle.py:1155: client: registers = client.call("read_registers", group="gpr")
tools/kits/oracle.py:1165: client: client.call("breakpoint", action="clear")
tools/kits/oracle.py:1166: client: client.call("pause")
tools/kits/oracle.py:1342: client: client.call("breakpoint", action="clear")
tools/kits/oracle.py:1345: client: client.call("breakpoint", action="add", type="execute",
tools/kits/oracle.py:1352: client: client.call("continue")
tools/kits/oracle.py:1355: client: registers = client.call("read_registers", group="gpr")
tools/kits/oracle.py:1381: client: client.call("get_gte_registers")),
tools/kits/oracle.py:1386: client: client.call("breakpoint", action="clear")
tools/kits/oracle.py:1387: client: client.call("pause")
tools/kits/oracle.py:2575: client: game.client.call("dump_vram", path=path, format="png")
tools/kits/oracle.py:2612: client: game.client.call("press_button", button=button,
tools/kits/oracle.py:2852: client: return game.client.call("get_status").get("frame_number")
tools/kits/replay.py:711: import: import fork # tools/pes2
tools/kits/replay.py:1390: import: import savestate # tools/pes2
tools/kits/selftest.py:2061: import: import fork # tools/pes2
tools/kits/core/tex.py:35: sys.path: sys.path.insert(0, _path)

[looks]
tools/looks/atlas.py:105: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
tools/looks/confront.py:1280: client: game.client.call("dump_vram", path=path, format="png")
tools/looks/confront.py:1333: client: client.call("breakpoint", action="clear")
tools/looks/confront.py:1334: client: client.call("breakpoint", action="add", type="execute",
tools/looks/confront.py:1337: client: client.call("continue")
tools/looks/confront.py:1342: client: registers = client.call("read_registers", group="gpr")
tools/looks/confront.py:1348: client: client.call("breakpoint", action="clear")
tools/looks/confront.py:1523: client: client.call("breakpoint", action="clear")
tools/looks/confront.py:1524: client: client.call("breakpoint", action="add", type="execute",
tools/looks/confront.py:1527: client: client.call("continue")
tools/looks/confront.py:1532: client: number = client.call("get_status")["frame_number"]
tools/looks/confront.py:1535: client: client.call("breakpoint", action="clear")
tools/looks/iso_source.py:27: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pes2"))
tools/looks/oracle.py:76: sys.path: sys.path.insert(0, PES2)
tools/looks/oracle.py:343: import: import fork
tools/looks/oracle.py:372: import: import savestate
tools/looks/oracle.py:643: import: import mcp
tools/looks/oracle.py:686: import: import fork
tools/looks/oracle.py:715: import: import fork
tools/looks/oracle.py:723: client: self.client.call("pause")
tools/looks/oracle.py:727: client: self.client.call("frame_step")
tools/looks/oracle.py:740: client: self.client.call("press_button", button=button,
tools/looks/oracle.py:764: client: self.client.call("take_screenshot", path=path)
tools/looks/oracle.py:793: client: self.client.call("read_memory", address=address, size=size, path=path)
tools/looks/oracle.py:813: client: self.client.call("load_state", slot=slot)
tools/looks/oracle.py:1522: client: if who_writes.is_paused(game.client.call("wait_for_pause")):
tools/looks/oracle.py:1540: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:1541: client: client.call("breakpoint", action="add", type="write",
tools/looks/oracle.py:1544: client: client.call("continue")
tools/looks/oracle.py:1552: client: client.call("press_button", button=button,
tools/looks/oracle.py:1565: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:1570: client: window = client.call(
tools/looks/oracle.py:1589: client: reply = client.call(
tools/looks/oracle.py:1598: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:1785: client: reply = game.client.call("read_vram_region", x=x, y=y,
tools/looks/oracle.py:2443: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:2444: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:2449: client: client.call("continue")
tools/looks/oracle.py:2453: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:2458: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:2459: client: client.call("pause")
tools/looks/oracle.py:3105: client: game.client.call("dump_vram", path=path, format="png")
tools/looks/oracle.py:3204: client: game.client.call("write_vram_region", x=0, y=origin, width=width,
tools/looks/oracle.py:3338: client: game.client.call("write_vram_region", x=page[0], y=page[1],
tools/looks/oracle.py:3597: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:3598: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:3602: client: client.call("continue")
tools/looks/oracle.py:3604: client: client.call("press_button", button=press,
tools/looks/oracle.py:3609: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:3617: client: client.call("continue")
tools/looks/oracle.py:3620: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:4246: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:4248: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:4253: client: client.call("continue")
tools/looks/oracle.py:4260: client: if not who_writes.is_paused(client.call("wait_for_pause")):
tools/looks/oracle.py:4262: client: out.append(read(client.call("read_registers", group="gpr")))
tools/looks/oracle.py:4270: client: client.call("continue")
tools/looks/oracle.py:4273: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:4274: client: client.call("pause")
tools/looks/oracle.py:4492: client: game.client.call("dump_vram", path=path, format="png")
tools/looks/oracle.py:4513: client: game.client.call("press_button", button=button,
tools/looks/oracle.py:4735: client: gpu = game.client.call("get_gpu_state")
tools/looks/oracle.py:5902: client: game.client.call("continue")
tools/looks/oracle.py:5916: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:5917: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:5921: client: client.call("continue")
tools/looks/oracle.py:5922: client: client.call("press_button", button=button,
tools/looks/oracle.py:5928: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:5936: client: client.call("continue")
tools/looks/oracle.py:5939: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:5940: client: client.call("pause")
tools/looks/oracle.py:5967: client: client.call("press_button", button="Down", duration_frames=CONFIRM_FRAMES)
tools/looks/oracle.py:5971: client: hit = client.call("vram_watch", action="last_hit")
tools/looks/oracle.py:5977: client: client.call("continue")
tools/looks/oracle.py:6069: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6070: client: watch = client.call("vram_watch", action="add",
tools/looks/oracle.py:6086: client: client.call("vram_watch", action="remove",
tools/looks/oracle.py:6495: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6497: client: client.call("breakpoint", action="add", type="read",
tools/looks/oracle.py:6502: client: client.call("continue")
tools/looks/oracle.py:6506: client: client.call("read_registers", group="all"), "pc")
tools/looks/oracle.py:6508: client: listed = client.call("breakpoint", action="list")
tools/looks/oracle.py:6513: client: client.call("pause")
tools/looks/oracle.py:6516: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6669: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6671: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:6675: client: client.call("continue")
tools/looks/oracle.py:6678: client: listed = client.call("breakpoint", action="list")
tools/looks/oracle.py:6684: client: client.call("pause")
tools/looks/oracle.py:6687: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6828: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6833: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:6841: client: client.call("continue")
tools/looks/oracle.py:6847: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:6896: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:6897: client: client.call("pause")
tools/looks/oracle.py:7000: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:7001: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:7007: client: client.call("continue")
tools/looks/oracle.py:7012: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:7017: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:7018: client: client.call("pause")
tools/looks/oracle.py:7545: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:7547: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:7554: client: client.call("continue")
tools/looks/oracle.py:7559: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:7588: client: "frame_number": client.call("get_status").get("frame_number"),
tools/looks/oracle.py:7593: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:7594: client: client.call("pause")
tools/looks/oracle.py:8198: client: before = game.client.call("get_status")
tools/looks/oracle.py:8200: client: after = game.client.call("get_status")
tools/looks/oracle.py:8271: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8272: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:8277: client: client.call("continue")
tools/looks/oracle.py:8282: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:8286: client: out.append((client.call("get_status")["frame_number"], pair))
tools/looks/oracle.py:8289: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8290: client: client.call("pause")
tools/looks/oracle.py:8397: client: game.client.call("press_button", button="Down",
tools/looks/oracle.py:8445: client: game.client.call("press_button", button="Down",
tools/looks/oracle.py:8456: client: game.client.call("press_button", button="Up",
tools/looks/oracle.py:8459: client: game.client.call("press_button", button="Down",
tools/looks/oracle.py:8530: client: gpu = game.client.call("get_gpu_state")
tools/looks/oracle.py:8613: client: game.client.call("press_button", button="Up",
tools/looks/oracle.py:8716: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8717: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:8722: client: client.call("continue")
tools/looks/oracle.py:8728: client: seen.append(gte_projection(client.call("get_gte_registers")))
tools/looks/oracle.py:8731: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8732: client: client.call("pause")
tools/looks/oracle.py:8754: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8755: client: client.call("breakpoint", action="add", type="execute",
tools/looks/oracle.py:8759: client: client.call("continue")
tools/looks/oracle.py:8763: client: registers = client.call("read_registers", group="gpr")
tools/looks/oracle.py:8769: client: client.call("breakpoint", action="clear")
tools/looks/oracle.py:8770: client: client.call("pause")
tools/looks/oracle.py:9993: import: import mcp
tools/looks/oracle.py:10173: import: import savestate
tools/looks/sprites.py:45: sys.path: sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pes2"))

[pes2]
tools/pes2/fork.py:541: client: c = Client(**({"host": host} if host else {}),
tools/pes2/fork.py:752: client: with Client(timeout=3.0) as c:
tools/pes2/mcp_drive.py:108: import: import fork # noqa: E402
tools/pes2/mcp_drive.py:110: import: from mcp import NotRunning, ToolError # noqa: E402
tools/pes2/mcp_drive.py:331: import: from mcp import Client
tools/pes2/mcp_drive.py:333: client: s.client = Client()
tools/pes2/mcp_drive.py:346: client: self.client.call("pause")
tools/pes2/mcp_drive.py:349: client: self.client.call("continue")
tools/pes2/mcp_drive.py:352: client: return self.client.call("get_status")["frame_number"]
tools/pes2/mcp_drive.py:361: client: self.client.call("frame_step")
tools/pes2/mcp_drive.py:373: client: self.client.call("set_speed", fast_forward=True)
tools/pes2/mcp_drive.py:378: client: self.client.call("set_speed", fast_forward=False)
tools/pes2/mcp_drive.py:391: client: self.client.call("press_button", button=button.capitalize()
tools/pes2/mcp_drive.py:410: client: self.client.call("take_screenshot", path=path)
tools/pes2/mcp_drive.py:588: client: self.client.call("save_state", slot=slot)
tools/pes2/mcp_drive.py:601: client: self.client.call("load_state", slot=slot)
tools/pes2/pad.py:50: import: from mcp import Client, NotRunning # noqa: E402
tools/pes2/pad.py:75: client: self.client.call("pause")
tools/pes2/pad.py:76: client: self.client.call("press_button", button=button.capitalize(),
tools/pes2/pad.py:79: client: self.client.call("frame_step")
tools/pes2/pad.py:82: client: self.client.call("continue")
tools/pes2/pad.py:86: client: self.client.call("take_screenshot", path=path)
tools/pes2/pad.py:93: client: self.client.call("set_speed", fast_forward=bool(on))
tools/pes2/pad.py:113: client: client = Client()
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

kit2d: 1 site(s) in 1 file(s) (import 0, client 0, sys.path 1)
kits: 29 site(s) in 4 file(s) (import 4, client 23, sys.path 2)
looks: 139 site(s) in 5 file(s) (import 7, client 128, sys.path 4)
pes2: 39 site(s) in 5 file(s) (import 8, client 31, sys.path 0)
by category: import 19, client 182, sys.path 7
audit: 208 raw site(s) in 15 file(s)
exit=0
```

**`--json` dá o mesmo total:**

```
$ python3 tools/duckmcp/audit.py | tail -1
audit: 208 raw site(s) in 15 file(s)
$ python3 tools/duckmcp/audit.py --json | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])"
208
```

**A árvore plantada, verde e vermelha.** Verde, as linhas do audit no selftest:

```
$ python3 tools/duckmcp/selftest.py | grep -E "audit|duckmcp_selftest:"
  ok    audit.self_check() asserted something
  ok    audit: audit finds the module home of a synthetic tree
  ok    audit: audit counts 0 sites in a clean synthetic tree
  ok    audit: audit counts 1 site for one planted `import fork`
  ok    audit: the planted site is an import in proj/a.py line 5
  ok    audit: the text report ends in the fixed-form total
  ok    audit: one site of every category, inline import and resolved sys.path target included
duckmcp_selftest: 47 check(s) ran, 0 failure(s)
```

Vermelho: a categoria `import` desligada de propósito (`if False and not is_module and _imports_module(node):` no `_sites_ast`), selftest rodado, e o arquivo restaurado de cópia:

```
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
  FAIL  audit: audit counts 1 site for one planted `import fork`  got 0, want 1
  FAIL  audit: the planted site is an import in proj/a.py line 5  got [], want [('import', 'planted/proj/a.py', 5)]
  FAIL  audit: the text report ends in the fixed-form total  got 'audit: 0 raw site(s) in 0 file(s)', want 'audit: 1 raw site(s) in 1 file(s)'
  FAIL  audit: one site of every category, inline import and resolved sys.path target included  got {'import': 0, 'client': 3, 'sys.path': 1}, want {'import': 1, 'client': 3, 'sys.path': 1}
duckmcp_selftest: 47 check(s) ran, 4 failure(s)
exit=1
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?   # restaurado
duckmcp_selftest: 47 check(s) ran, 0 failure(s)
exit=0
```

**Selftest inteiro:** `python3 tools/duckmcp/selftest.py; echo exit=$?` termina em `duckmcp_selftest: 47 check(s) ran, 0 failure(s)` e `exit=0` (transcrição acima); `ctest --test-dir build -R duckmcp_selftest` dá `100% tests passed, 0 tests failed out of 1`.
