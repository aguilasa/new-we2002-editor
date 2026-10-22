---
id: CORR-DMCP-004
---

# CORR-DMCP-004 — Tirar do shim mcp.py o monkeypatch de vivacidade e a lógica de teste própria

Origin: [DMCP-TASK-06](/docs/tasks/duckmcp/06-cli.md)

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
