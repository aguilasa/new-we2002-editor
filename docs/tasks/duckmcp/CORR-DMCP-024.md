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
