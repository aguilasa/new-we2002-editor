---
id: DMCP-TASK-01
---

# DMCP-TASK-01 — Esqueleto de tools/duckmcp/: __init__, errors.py, env.py e duckmcp_selftest

## Goal

Existe o pacote `tools/duckmcp/` com `errors.py` (`SKIP = 77`, `Fail`, `Skip`, `NotRunning`, `ToolError`, `SessionLost`) e `env.py` (as variáveis `DUCKSTATION_*` com fallback `PES2_*`, `display()`, `x_env()`, `fork_home()`, `appimage()`, `data_dir()`, `savestates_dir()`, `state_path(serial, slot)`, `is_roms()`), um `selftest.py` que roda os self-checks deles, e o alvo `duckmcp_selftest` no `ctest`, que nunca pula. Nenhum projeto muda ainda.

## Arquivos a criar ou modificar

- In:
  - os quatro arquivos de `tools/duckmcp/` e o `add_test` em `tests/CMakeLists.txt`
- Out:
  - `client.py`, `fork.py` e o resto do §3.1 (fases 1 a 4)
  - qualquer arquivo de `tools/pes2/`, `tools/looks/`, `tools/kits/`

## Done criteria

- [x] `git merge-base --is-ancestor f21182ea HEAD` sai 0 (a PES2-TASK-03 está na base, §2 decisão 4)
- [x] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [x] o selftest afirma: `DUCKSTATION_MCP_PORT` ganha de `PES2_MCP_PORT`; só `PES2_MCP_PORT` definida vale; nenhuma das duas dá `2346`
- [x] o selftest afirma: `x_env(':98')` tem `XAUTHORITY == ''` e `x_env(':1')` não toca no `XAUTHORITY` herdado
- [x] uma planta (inverter a precedência de uma variável no `env.py`) deixa o selftest vermelho, visto no Log
- [x] `ctest --test-dir build -R duckmcp_selftest` passa, sem *skipped*

## Notes

Modelo de forma: `tools/kit2d/selftest.py` e o alvo `kit2d_selftest`. O `drive.py` zera `XAUTHORITY` em todo display; a regra certa é a do `fork.env_for` (só `:98`), §4.3.

## Log de Execução

2026-10-22 — HEAD de trabalho sobre `25d012af`.

- `git merge-base --is-ancestor f21182ea HEAD; echo $?` → `0`: a PES2-TASK-03 (o `mcp.py` com `SessionLost`) está na base, §2 decisão 4.
- `python3 tools/duckmcp/selftest.py; echo exit=$?` → última linha `duckmcp_selftest: 40 check(s) ran, 0 failure(s)`, `exit=0`. Os 40: três do pacote (importa de `tools/duckmcp/`, tem `__version__`, reexporta os seis nomes de `errors`), oito de `errors.self_check()` (`SKIP == 77`, `SessionLost` é `ToolError`, as quatro classes são `Exception` e não se derivam entre si, mais a guarda de que o self-check afirmou algo) e 29 de `env.self_check()`. Entre eles, nomeadas na saída:
  - `env: port: DUCKSTATION_MCP_PORT beats PES2_MCP_PORT`, `env: port: PES2_MCP_PORT alone beats the default`, `env: port: neither gives 2346` — o mesmo trio para host, display, e o par nova/legado para fork e AppImage;
  - `env: x_env(':98'): XAUTHORITY is ''` e `env: x_env(':1'): inherited XAUTHORITY untouched`;
  - `env: is_roms: forward slashes`, `env: is_roms: backslashes`, `env: state_path: file name is <serial>_<slot>.sav`.
- Planta 1, precedência invertida no `env.get` (o legado lido antes da nova), na árvore real: `python3 tools/duckmcp/selftest.py --quiet; echo exit=$?` →
  ```
    FAIL  env: port: DUCKSTATION_MCP_PORT beats PES2_MCP_PORT  got 2, want 1
    FAIL  env: host: DUCKSTATION_MCP_HOST beats PES2_MCP_HOST  got 'b', want 'a'
    FAIL  env: display: DUCKSTATION_DISPLAY beats PES2_DISPLAY  got ':8', want ':7'
    FAIL  env: fork: DUCKSTATION_FORK beats PES2_FORK  got '/b', want '/a'
    FAIL  env: appimage: DUCKSTATION_APPIMAGE beats PES2_DUCKSTATION  got '/b', want '/a'
  duckmcp_selftest: 40 check(s) ran, 5 failure(s)
  exit=1
  ```
  Revertido da cópia guardada; a corrida seguinte volta a `duckmcp_selftest: 40 check(s) ran, 0 failure(s)`, `exit=0`.
- Planta 2, a regra do `drive.py` (`XAUTHORITY` zerado em todo display: `if display_name == XVFB_DISPLAY:` trocado por `if True:`) →
  ```
    FAIL  env: x_env(':1'): inherited XAUTHORITY untouched  got '', want '/run/cookie'
    FAIL  env: x_env(':1'): no XAUTHORITY added when none inherited  got True, want False
  duckmcp_selftest: 40 check(s) ran, 2 failure(s)
  exit=1
  ```
  Revertido (`cmp` com a cópia guardada sai 0); de volta a `0 failure(s)`, `exit=0`.
- `cmake -S . -B build >/dev/null && ctest --test-dir build -R duckmcp_selftest` → `1/1 Test #24: duckmcp_selftest .................   Passed    0.02 sec`, `100% tests passed, 0 tests failed out of 1`, sem *skipped*. Timeout 30 s, muito acima de 1,5× os 0,01 s medidos por `/usr/bin/time -f %e` em três corridas.
- Decisões: string vazia conta como não definida (`DUCKSTATION_MCP_PORT=` cai para o legado, não vira `int("")`); toda função lê o ambiente na chamada, e recebe `environ` opcional para o self-check não tocar no processo; `x_env` só mexe em `DISPLAY` e `XAUTHORITY` — `LD_LIBRARY_PATH` e `QT_PLUGIN_PATH` ficam para o lançamento do fork (fase 1); `is_roms` normaliza `os.sep` **e** `\`, para a asserção das barras invertidas valer também no Linux.
- Os nomes legados `PES2_*` aparecem em `env.py` como literais — a tabela `LEGACY` e as asserções de precedência — e não só em comentário de linhagem. A regra (c) do §3.3, quando o `controls.py` a varrer, precisa isentar esses cinco nomes no `env.py`, ou a regra muda.
- **Closed** — commit `b5d381a7` (2026-10-22): build(duckmcp): add tools/duckmcp skeleton, errors.py, env.py and duckmcp_selftest
  - Files (`git show --name-status b5d381a7`):
    - `M docs/tasks/duckmcp/01-esqueleto.md`
    - `M tests/CMakeLists.txt`
    - `A tools/duckmcp/__init__.py`
    - `A tools/duckmcp/env.py`
    - `A tools/duckmcp/errors.py`
    - `A tools/duckmcp/selftest.py`
- **Reviewed** (2026-10-22) at `157ebb2e`: no finding
