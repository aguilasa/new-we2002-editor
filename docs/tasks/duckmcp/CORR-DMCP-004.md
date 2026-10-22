---
id: CORR-DMCP-004
---

# CORR-DMCP-004 — Tirar do shim mcp.py o monkeypatch de vivacidade e a lógica de teste própria

Origin: [DMCP-TASK-06](/docs/tasks/duckmcp/06-cli-e-shim-mcp.md)

## Problem

A checagem da Fase 1 diz que `tools/pes2/mcp.py` "só reexporta", e o critério 4 pede nenhuma função
além do `self_check` "delegado". O shim faz mais que isso. Importá-lo religa uma global da lib
(`duckmcp.client.process_alive`, linha 36) para um `lambda`: qualquer processo que importe `mcp` muda o
comportamento de `duckmcp.client`, inclusive para quem importa a lib direto. E o `self_check` dele não
delega: traz um segundo `lambda` (linha 55) e dois casos de teste próprios. O Log admite ler o critério
"ao pé da letra" para contornar isso. O comportamento está certo, e o Log o chama de provisório até a
DMCP-TASK-08.

## Evidência

```text
$ grep -n '^class\|^def\|^main\|lambda' tools/pes2/mcp.py
36:client.process_alive = lambda: bool(
40:def self_check(verbose=True):
55:        fork.running_pids = lambda pids=pids: pids
78:main = functools.partial(cli.legacy_main, self_check=self_check)
$ python3 -c "import sys; sys.path[:0]=['tools','tools/pes2']
from duckmcp import client; a=client.process_alive
import mcp; print(a is client.process_alive)"
False
```

## Root cause

Hipótese: o diagnóstico vivo/morto do antigo `mcp.py --list` precisava sobreviver, mas o ponto de
encaixe da lib só é preenchido na DMCP-TASK-08. O shim o preencheu de fora, e isso passou do "só
reexporta".

## Fix

Uma de duas, e a DMCP-TASK-07 (fechamento da Fase 1) diz qual vale:

- (a) manter o código e registrar a exceção medida no docstring do `tools/pes2/mcp.py` e na entrada da
  Fase 1 do `docs/prompts/perfil-duckmcp.md`, nomeando a DMCP-TASK-08 como onde a sonda entra na lib
  (declarar a edição do perfil com `rite set --files`); ou
- (b) mover a sonda e as duas checagens para `tools/duckmcp/` e reduzir o shim a imports,
  `self_check = client.self_check` e `main`.

## Arquivos a criar ou modificar

- `tools/pes2/mcp.py`
- `docs/prompts/perfil-duckmcp.md` (opção a) ou `tools/duckmcp/client.py` (opção b)

## Verificação

```text
python3 -c "import sys; sys.path[:0]=['tools','tools/pes2']; from duckmcp import client; a=client.process_alive; import mcp; sys.exit(0 if a is client.process_alive else 1)"
```

Hoje sai 1. Na opção (b) tem de sair 0; na opção (a), a exceção documentada tem de estar presente nos
dois arquivos. Nos dois casos, `python3 tools/pes2/selftest.py` e `python3 tools/duckmcp/selftest.py`
continuam saindo 0.

## Log de Execução

2026-10-22 — reproduzido na HEAD `ddb8f489`: `grep` acha os dois `lambda` (linhas 36 e 55), e o
`print(a is client.process_alive)` imprime `False`.

Escolhida a **opção (a)**. A DMCP-TASK-07 não decide, porque é só o fechamento da fase. Quem decide é a
(b), que não cabe agora: `tools/duckmcp/` não tem `fork.py` (`ls tools/duckmcp/` → `audit.py client.py
cli.py controls.py env.py errors.py __init__.py selftest.py`). A sonda na lib importaria
`tools/pes2/fork.py`, contra as regras (b) e (c) do §3.3, ou adiantaria o `running_pids` da DMCP-TASK-08.
Código sem mudança. A exceção medida está no docstring do `tools/pes2/mcp.py` e na entrada da Fase 1 do
`docs/prompts/perfil-duckmcp.md`, e os dois nomeiam a DMCP-TASK-08 como o lugar onde a sonda entra na lib.
Edição do perfil declarada com `rite set CORR-DMCP-004 --files …`.

Verificação:

```text
$ python3 -c "…sys.exit(0 if a is client.process_alive else 1)"; echo probe=$?
probe=1                      # esperado na opção (a): a religação continua, documentada
$ grep -c 'CORR-DMCP-004' tools/pes2/mcp.py docs/prompts/perfil-duckmcp.md
tools/pes2/mcp.py:1
docs/prompts/perfil-duckmcp.md:1
$ python3 tools/pes2/selftest.py; echo pes2=$?
OK
pes2=0
$ python3 tools/duckmcp/selftest.py --quiet; echo dmcp=$?
duckmcp_selftest: 137 check(s) ran, 0 failure(s)
dmcp=0
```
- **Closed** — commit `6c37f6a4` (2026-10-22): docs(duckmcp): record the shim's liveness rebinding as a measured exception
  - Files (`git show --name-status 6c37f6a4`):
    - `M docs/prompts/perfil-duckmcp.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-004.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/pes2/mcp.py`
