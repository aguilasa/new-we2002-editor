---
id: DMCP-TASK-28
---

# DMCP-TASK-28 — Documentação: `CLAUDE.md`, a §6.11 do PES2 e a decisão no `perfil-kit2d.md`

## Goal

`CLAUDE.md` ganha uma seção da lib (comandos, variáveis `DUCKSTATION_*` e as `PES2_*` como legado, armadilhas do §1.3), e as tabelas do PES2 e do `looks` deixam de citar `tools/pes2/mcp.py`, `fork.py`, `savestate.py`; a §6.11 do `PLAN-PES2-PSX.md` remete ao [§1.3](/docs/PLAN-DUCKMCP-PY.md#1.3) nas armadilhas do emulador; o `perfil-kit2d.md` registra que o `oracle.py` do `kit2d` nasce sobre a lib.

## Arquivos a criar ou modificar

- In:
  - os arquivos listados
  - `docs/PES2-WINDOWS.md`, `docs/KITS-AJUSTES-3D.md`, `docs/PLAN-KIT2D-PY.md`, `docs/PLAN-LOOKS-PY.md`: o `grep` do primeiro critério acha neles menção viva aos caminhos antigos, e a varredura é desta task
- Out:
  - tasks do `kit2d`

## Done criteria

- [x] `grep -rnE 'tools/pes2/(mcp|fork|savestate)\.py|pes2/(mcp|fork|savestate)\.py' CLAUDE.md docs --include='*.md' | grep -v 'docs/tasks/concluidos'` lista só remissões históricas marcadas, coladas no Log
- [x] `grep -n 'DUCKSTATION_MCP_PORT' CLAUDE.md` acha a seção nova
- [x] `rite check --cycle kit2d` continua limpo
- [x] `ctest --test-dir build -R tasks` passa

## Notes

Regra do ciclo: fechar um veredito é varrer quem dizia o anterior — a lista do `grep` é a varredura.

## Log de Execução

2026-10-26.

- **`CLAUDE.md`**: seção nova "A lib do MCP do DuckStation — `tools/duckmcp/`", logo antes da do `.mcr` — o que é, comandos (`cli.py`, `savestate.py`, `selftest.py`, `controls.py`, `audit.py`), as cinco `DUCKSTATION_*` com o legado `PES2_*` (nomes e defaults lidos do `tools/duckmcp/env.py`), os alvos `duckmcp_selftest` e `duckmcp_live` (`DUCKSTATION_TEST_IMAGE`, 77, `RESOURCE_LOCK duckstation`, lidos de `tests/CMakeLists.txt`), e as armadilhas do emulador por remissão ao §1.3. Nenhum total copiado: a contagem de ferramentas do servidor saiu da tabela do PES2 e ficou no `cli.py list`. A tabela do PES2 aponta para `cli.py list|status|call`, `cli.py launch|kill|procs|recipe|which` e `tools/duckmcp/savestate.py`; a seção do `looks` diz que o emulador vem da lib.
- **`docs/PLAN-PES2-PSX.md` §6.11**: um parágrafo de remissão ao [§1.3](/docs/PLAN-DUCKMCP-PY.md#1.3) listando as armadilhas que passaram para a lib (as do §1.3, mais a do joystick, que nunca esteve na §6.11), e remissão no fim das 29, 30, 34, 35, 36 e 46. Nada reescrito: a 28 ganhou "fazia (histórico; hoje …)". Fora da §6.11, a tabela do emulador (§3.2) e a dica da §4.2 viraram lib; as menções datadas (§6.14, PES2-TASK-32/33) ficaram com o caminho velho e a marca "histórico".
- **`docs/prompts/perfil-kit2d.md`**: decisão de 2026-10-26, o `oracle.py` do `kit2d` nasce sobre `duckmcp.Session`/`debug`, com link ao [§2](/docs/PLAN-DUCKMCP-PY.md#2).
- **Os outros declarados**: instrução viva → lib (`perfil-pes2.md` — o bloco de comandos, a linha de gate "cliente ou lançador" agora é o `duckmcp/selftest.py`, e a do save state diz `duckmcp_selftest`, porque desde a DMCP-TASK-20 o `pes2/selftest.py` não roda mais esses checks —; `LOOKS-AMBIENTE.md`, `PLAN-LOOKS-PY.md`, `PLAN-KIT2D-PY.md`, `PES2-WINDOWS.md`, incluindo o bloco PowerShell com `tools\pes2\fork.py`, que o `grep` do critério não pega por causa da barra invertida). Registro datado → caminho velho marcado "histórico". No `PES2-WINDOWS.md` as linhas de `fork.py`/`savestate.py` passaram a nomear o módulo da lib, dizendo que a medição de 2026-09-11 foi do de `tools/pes2/` e que a mudança não teve corrida nova registrada ali.
- Fora do escopo por natureza: todo `docs/tasks/**` (registro de execução; menção ali é transcrição), o `PLAN-DUCKMCP-PY.md` (da DMCP-TASK-31) e o `perfil-duckmcp.md` (descrevem a migração).

Critério 1, `grep -rnE 'tools/pes2/(mcp|fork|savestate)\.py|pes2/(mcp|fork|savestate)\.py' CLAUDE.md docs --include='*.md' | grep -v 'docs/tasks/concluidos'`, agrupado.

(a) nos documentos declarados, cada uma marcada:

```
docs/LOOKS-AMBIENTE.md:20:corrida, `tools/pes2/fork.py`, registro histórico —, `make.ps1`) e
docs/PES2-WINDOWS.md:195:| `tools/duckmcp/fork.py` (medido como `tools/pes2/fork.py`, histórico) | **roda** desde 2026-09-11 | portado: `tasklist` no lugar do `pgrep`, `taskkill /F` no do `SIGKILL`, `ctypes`/`user32` no do `xdotool`, e nenhum display; a mudança para a lib não teve corrida nova registrada aqui |
docs/PES2-WINDOWS.md:200:| `tools/duckmcp/savestate.py` (medido como `tools/pes2/savestate.py`, histórico) | precisa de `zstd.exe` no `PATH` | ele descomprime o estado chamando o `zstd` de linha de comando; a mudança para a lib não teve corrida nova registrada aqui |
CLAUDE.md:698:Ela absorveu, a partir de 2026-10-22, o que morava em `tools/pes2/mcp.py`,
docs/PLAN-KIT2D-PY.md:265:| `tools/duckmcp/` (`Session`, `debug`, `fork`; [§2](/docs/PLAN-DUCKMCP-PY.md#2) do plano da lib, 2026-10-26 — antes, `tools/pes2/mcp.py` e `fork.py`, histórico), `tools/looks/oracle.py` | subir o fork, apertar botão, `read_memory`, `read_vram_region`, `take_screenshot`, `save_state`/`load_state` | a fase 0 e os confrontos |
docs/PLAN-LOOKS-PY.md:1170:`tools/pes2/savestate.py` (histórico; hoje `tools/duckmcp/savestate.py`) lê o
docs/KITS-AJUSTES-3D.md:618:**slot 10**, "nos mesmos moldes". O quadro dos dois states (histórico: `python3 tools/pes2/savestate.py shot
docs/PLAN-PES2-PSX.md:2096:    era o que o `tools/pes2/fork.py` fazia (histórico; hoje é o
docs/PLAN-PES2-PSX.md:2474:O leitor nasceu como `tools/pes2/savestate.py` (histórico; desde 2026-10-26
docs/PLAN-PES2-PSX.md:2732:é o procedimento, os números acima e `tools/pes2/savestate.py` (histórico; hoje
docs/PLAN-PES2-PSX.md:2814:PES2-TASK-33 e virou `tools/pes2/fork.py recipe` (histórico; hoje
docs/prompts/perfil-kit2d.md:20:- **O `oracle.py` do `kit2d` nasce sobre a lib `tools/duckmcp/` (`duckmcp.Session`, `duckmcp.debug`), nunca sobre `tools/pes2/mcp.py`/`fork.py` nem com cliente MCP próprio** (2026-10-26; [§2](/docs/PLAN-DUCKMCP-PY.md#2)).
```

(b) `docs/tasks/**`, por arquivo (`| grep '^docs/tasks/' | cut -d: -f1 | sort | uniq -c`), antes de este Log entrar — ele mesmo passa a casar, por colar a saída:

```
      2 docs/tasks/duckmcp/02-audit.md
      3 docs/tasks/duckmcp/03-regras-de-desenho.md
      4 docs/tasks/duckmcp/05-client.md
     13 docs/tasks/duckmcp/06-cli-e-shim-mcp.md
      1 docs/tasks/duckmcp/07-fechamento-fase-1.md
      9 docs/tasks/duckmcp/08-fork.md
     12 docs/tasks/duckmcp/09-cli-fork-e-lancadores.md
      1 docs/tasks/duckmcp/11-fechamento-fase-2.md
      1 docs/tasks/duckmcp/13-hardware-e-pixels.md
     11 docs/tasks/duckmcp/14-savestate.md
      1 docs/tasks/duckmcp/15-fechamento-fase-3.md
      3 docs/tasks/duckmcp/26-kits-controles.md
      1 docs/tasks/duckmcp/28-documentacao.md
      2 docs/tasks/duckmcp/30-apagar-shims.md
      9 docs/tasks/duckmcp/CORR-DMCP-004.md
      2 docs/tasks/duckmcp/CORR-DMCP-005.md
      1 docs/tasks/duckmcp/CORR-DMCP-008.md
      2 docs/tasks/duckmcp/CORR-DMCP-016.md
      1 docs/tasks/duckmcp/CORR-DMCP-024.md
      1 docs/tasks/duckmcp/correcoes-progresso.md
      4 docs/tasks/duckmcp/progresso.md
      3 docs/tasks/pes2/03-direcao-do-emulador.md
      3 docs/tasks/pes2/32-poc-do-mcp-do-duckstation.md
      2 docs/tasks/pes2/33-compilar-e-validar-o-mcp.md
      2 docs/tasks/pes2/34-rotas-mcp-no-lugar-do-drive.md
      4 docs/tasks/pes2/correcoes-progresso.md
      2 docs/tasks/pes2/CORR-PES2-024.md
      5 docs/tasks/pes2/CORR-PES2-025.md
      5 docs/tasks/pes2/CORR-PES2-026.md
      6 docs/tasks/pes2/CORR-PES2-028.md
      9 docs/tasks/pes2/CORR-PES2-029.md
      4 docs/tasks/pes2/CORR-PES2-031.md
     12 docs/tasks/pes2/CORR-PES2-032.md
```

(c) o plano e o perfil do próprio ciclo, que descrevem a migração:

```
docs/PLAN-DUCKMCP-PY.md:21:No fim do ciclo `tools/pes2/mcp.py`, `tools/pes2/fork.py` e
docs/PLAN-DUCKMCP-PY.md:22:`tools/pes2/savestate.py` **não existem mais**, e um gate recusa qualquer
docs/PLAN-DUCKMCP-PY.md:51:4. `tools/pes2/mcp.py`, `fork.py` e `savestate.py` apagados; nenhum import
docs/PLAN-DUCKMCP-PY.md:69:| `tools/pes2/mcp.py` | 518 | `Client` (Streamable HTTP, `MCP-Session-Id`), `NotRunning`, `ToolError`, CLI `--list/--status/--call` |
docs/PLAN-DUCKMCP-PY.md:70:| `tools/pes2/fork.py` | 921 | `launch`, `kill`, `status`, `recipe`, `which`, joystick, janela X e Win32, diálogo `Automatic Updater` |
docs/PLAN-DUCKMCP-PY.md:71:| `tools/pes2/savestate.py` | 647 | o `.sav` do DuckStation: RAM, miniatura, mídia, `scan`, `diff` — sem nada de jogo |
docs/PLAN-DUCKMCP-PY.md:168:2. **Shims só durante o ciclo**: `tools/pes2/mcp.py`, `fork.py` e
docs/PLAN-DUCKMCP-PY.md:215:| `client.py` | `Client`: transporte, `initialize`, `tools()`, `call()`, `reclaim`, decodificação JSON/SSE, diagnóstico de `NotRunning` (processo vivo × morto, armadilha 35) | `pes2/mcp.py` depois da PES2-TASK-03 |
docs/PLAN-DUCKMCP-PY.md:216:| `fork.py` | `launch(image, match=None, ...)`, `kill`, `running_pids`, `status`, `which_binary`, `RECIPE`, `joysticks`/`refuse_joysticks`, achar janela (X e Win32), dispensar o `Automatic Updater`, `hide_window`, `size_window` | `pes2/fork.py`, `looks/oracle.py:553-616` |
docs/PLAN-DUCKMCP-PY.md:223:| `savestate.py` | o `.sav` inteiro | `tools/pes2/savestate.py`, movido |
docs/PLAN-DUCKMCP-PY.md:273:- `kits/controls.py`: `fork-joystick-let-through` (`pes2/fork.py`,
docs/PLAN-DUCKMCP-PY.md:365:| 1 | **transporte**: `client.py` com `reclaim`, `cli.py list/status/call`, servidor de teste no selftest; `pes2/mcp.py` vira shim | 0 |
docs/PLAN-DUCKMCP-PY.md:366:| 2 | **lançador**: `fork.py` sem título de jogo, `hide_window`/`size_window`, `cli.py launch/kill/procs/recipe/which` (o status de processo é `procs`, porque `status` já é o `get_status` do servidor); `pes2/fork.py` vira shim que passa o título do PES2; `make.ps1`, `Makefile`, `boot_check.sh`, `run_duckstation.sh` apontados; `duckmcp_live` no `ctest` | 1 |
docs/PLAN-DUCKMCP-PY.md:395:   muda (`tools/pes2/mcp.py`, `fork.py`, `savestate.py`, as variáveis
docs/prompts/perfil-duckmcp.md:15:- 2026-10-22 — `tools/pes2/mcp.py`, `fork.py` e `savestate.py` são shims só durante o ciclo; o fechamento os apaga ([§2](/docs/PLAN-DUCKMCP-PY.md#2)).
docs/prompts/perfil-duckmcp.md:60:- `tools/pes2/mcp.py` só reexporta; `python3 tools/pes2/selftest.py` sai 0. A exceção medida da
docs/prompts/perfil-duckmcp.md:70:- `grep -rn 'pes2/fork.py' Makefile make.ps1 tools/pes2/*.sh` não acha nada.
docs/prompts/perfil-duckmcp.md:77:- `savestate.py` movido com histórico (`git log --follow`), e o `tools/pes2/savestate.py` é shim.
```
- **Closed** — commit `bbd0bd34` (2026-10-26): docs(duckmcp): document the lib in CLAUDE.md and point live instructions to tools/duckmcp
  - Files (`git show --name-status bbd0bd34`):
    - `M CLAUDE.md`
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/LOOKS-AMBIENTE.md`
    - `M docs/PES2-WINDOWS.md`
    - `M docs/PLAN-KIT2D-PY.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/PLAN-PES2-PSX.md`
    - `M docs/prompts/perfil-kit2d.md`
    - `M docs/prompts/perfil-pes2.md`
    - `M docs/tasks/duckmcp/28-documentacao.md`
