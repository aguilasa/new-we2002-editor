---
id: CORR-DMCP-024
---

# CORR-DMCP-024 — Fazer a regra (b) pegar imports qualificados de mcp, fork e savestate

Origin: [DMCP-TASK-18](/docs/tasks/duckmcp/18-fechamento-fase-4.md)

## Problem

O `_IMPORT_RE` do `audit.py` (`tools/duckmcp/audit.py:65`) só casa `import mcp|fork|savestate` nu ou
`from mcp|fork|savestate import`. O `tools/pes2/` não tem `__init__.py`, então com `tools/` no
`sys.path` ele importa como namespace package: `from pes2 import mcp` e `import pes2.mcp` alcançam os
módulos antigos do emulador em `tools/pes2/`, o que a regra (b) da §3.3 proíbe, e o audit não os conta.
O selftest fica verde, e a Fase 4 fechou como "regra (b) completa" com essa forma sem guarda. Na HEAD
nenhum arquivo usa a forma — falta o check, não há defeito hoje.

## Evidência

```text
$ T=$(mktemp -d) && git archive HEAD tools | tar -x -C "$T" && printf 'import pes2.mcp  # planted\nfrom pes2.fork import launch  # planted\n' > "$T/tools/kit2d/probe_q.py" && (cd "$T" && python3 tools/duckmcp/audit.py | tail -1; python3 tools/duckmcp/selftest.py --quiet; echo "exit=$?")
audit: 206 raw site(s) in 14 file(s)
duckmcp_selftest: 434 check(s) ran, 0 failure(s)
exit=0
$ (cd "$T/tools" && python3 -I -c "import sys; sys.path.insert(0,'.'); from pes2 import mcp; print('importable', mcp.__file__)")
importable .../tools/pes2/mcp.py
```

Controle (o verificador sabe ficar vermelho; forma nua no mesmo arquivo):

```text
$ printf 'import fork  # planted\n' > "$T/tools/kit2d/probe_q.py" && (cd "$T" && python3 tools/duckmcp/selftest.py --quiet; echo "exit=$?")
FAIL  rule (b): no raw site outside PENDING  tools/kit2d/probe_q.py: import: import fork # planted (x1)
FAIL  rule (b): PENDING lists 206 site(s) in 108 entries, audit.py counts 207
exit=1
```

## Root cause

Hipótese: o padrão de módulo só considerou o estilo de import que os projetos usam hoje
(`sys.path.insert` mais import nu), e o caminho qualificado pelo projeto hospedeiro nunca foi coberto.

## Fix

No `tools/duckmcp/audit.py`, estender o percurso de AST e o `_IMPORT_RE` para casar também
`import <host>.(mcp|fork|savestate)`, `from <host> import (mcp|fork|savestate)` e
`from <host>.(mcp|fork|savestate) import`, montando `<host>` a partir do diretório hospedeiro que a
ferramenta já descobre (não literal, pela regra (c)). Acrescentar o controle plantado
`b-import-qualified-kit2d` no `tools/duckmcp/controls.py`, ao lado do `b-import-fork-kit2d`. As
contagens que dependem do controle novo se refazem pelas ferramentas, não à mão.

## Arquivos a criar ou modificar

- `tools/duckmcp/audit.py`
- `tools/duckmcp/controls.py`

## Verificação

O primeiro bloco da Evidência (plantar `import pes2.mcp` / `from pes2.fork import launch` numa cópia
da HEAD) imprime `audit: 208 raw site(s) in 15 file(s)` e o selftest sai `exit=1`; e
`python3 tools/duckmcp/controls.py` acusa o controle novo vermelho. Na árvore real o selftest sai 0.

## Log de Execução

2026-10-23 — reproduzido na HEAD `e6322970`: com `import pes2.mcp` e `from pes2.fork import launch`
plantados numa cópia, o audit dava `206 raw site(s) in 14 file(s)` e o selftest saía `exit=0`.

Conserto no `audit.py`:
- **O casador de AST** (`_imports_module`) e o do fallback por regex (`_import_re`) recebem o projeto
  hospedeiro `home`, que o `find_home` já descobre. Os dois passam a casar `import <home>.mcp`,
  `from <home>.mcp import x` e `from <home> import mcp`. O nome do hospedeiro não aparece literal no
  código, pela regra (c). `import <home>` sozinho continua de fora, porque não traz módulo de emulador.
- **O `self_check`** ganhou um caso com as três formas num arquivo que parseia e num que não parseia.

O `controls.py` ganhou `b-import-qualified-kit2d`.

Verificação:

```text
$ <primeiro bloco da Evidência, numa cópia da árvore com o conserto>
audit: 208 raw site(s) in 15 file(s)
  FAIL  rule (b): no raw site outside PENDING  tools/kit2d/probe_q.py: import: from pes2.fork import launch # planted (x1); tools/kit2d/probe_q.py: import: import pes2.mcp # planted (x1)
  FAIL  rule (b): PENDING lists 206 site(s) in 108 entries, audit.py counts 208
duckmcp_selftest: 434 check(s) ran, 2 failure(s)
exit=1
$ python3 tools/duckmcp/controls.py --only b-import-qualified-kit2d | sed -n 2,3p
red    b-import-qualified-kit2d (rule b): FAIL  rule (b): no raw site outside PENDING  tools/kit2d/dmcp_probe_b.py: import: from pes2 import fork # planted (x1); tools/kit2d/dmcp_probe_b.py: import: import pes2.mcp # planted (x1)
duckmcp_controls: 1 control(s), 1 red as required; 1/1 cover rules (a) to (d); per rule (b) 1/1
$ <cópia com `if not home:` trocado por `if True:` no _import_re>; python3 …/selftest.py | grep FAIL
  FAIL  audit: imports qualified by the host count, parsed or not (CORR-DMCP-024)  got [('q.py', 1), ('q.py', 2), ('q.py', 3)], want [… ('r.py', 1), ('r.py', 2), ('r.py', 3)]
$ python3 tools/duckmcp/audit.py | tail -1        # árvore real, total inalterado
audit: 206 raw site(s) in 14 file(s)
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 41 control(s), 41 red as required; 22/22 cover rules (a) to (d); per rule (a) 2/2, (b) 8/8, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
```

Na contagem 208 da primeira linha, o selftest dá 434 checks porque a cópia foi feita antes do caso novo
do `self_check`. Na árvore entregue são 435.
- **Closed** — commit `f5f3771f` (2026-10-23): fix(duckmcp): count emulator imports qualified by the host package in rule (b)
  - Files (`git show --name-status f5f3771f`):
    - `M docs/tasks/duckmcp/CORR-DMCP-024.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/audit.py`
    - `M tools/duckmcp/controls.py`
