---
id: CORR-DMCP-002
---

# CORR-DMCP-002 — Reconhecer import os com alias na regra (d) do selftest

Origin: [DMCP-TASK-03](/docs/tasks/duckmcp/03-regras-de-desenho.md)

## Problem

`env_reads()` em `tools/duckmcp/selftest.py` só acusa acesso de atributo quando o objeto é o nome
nu `os` (`node.value.id == "os"`). Um módulo fora do `env.py` que faça `import os as _os` e leia
`_os.environ` passa verde na regra (d). A §3.3 do plano diz que só o `env.py` lê variável de ambiente,
e esta checagem é a que deveria afirmar isso.

## Evidência

```text
$ T=$(mktemp -d); git -C /home/ingmar/desenvolvimento/github/new-we2002-editor archive HEAD tools/duckmcp | tar -x -C $T; python3 - "$T/tools/duckmcp/errors.py" <<'PY'
import sys
p = sys.argv[1]; t = open(p).read(); assert t.count("\nSKIP = 77\n") == 1
open(p, "w").write(t.replace("\nSKIP = 77\n", "\nimport os as _os\nSKIP = int(_os.environ.get('SKIP', '77'))\n"))
PY
$ python3 $T/tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 86 check(s) ran, 0 failure(s)
exit=0
```

## Root cause

A regra casa a grafia `os.<attr>` em vez de seguir a que nome o módulo `os` foi ligado; os aliases de
`import os as X` (e de `import posix`/`nt`) nunca são resolvidos. Hipótese sobre a intenção; a brecha
em si está medida acima.

## Fix

Em `env_reads()` do `tools/duckmcp/selftest.py`, coletar os nomes ligados por `import os as X` (e
`posix`/`nt`) e tratar `X.<ENV_ATTRS>` como leitura. Acrescentar ao `tools/duckmcp/controls.py` um
controle `d-aliased-os` com a substituição acima, esperando
`FAIL  rule (d): errors.py does not read the environment`.

## Arquivos a criar ou modificar

- `tools/duckmcp/selftest.py`
- `tools/duckmcp/controls.py`

## Verificação

`python3 tools/duckmcp/controls.py --only d-aliased-os` sai 0 com linha `red` (hoje responde
"no control named"), e a cópia plantada da Evidência passa a sair 1. `python3 tools/duckmcp/selftest.py`
continua saindo 0 na árvore real.

## Log de Execução

2026-10-22 — reproduzido (cópia plantada com `import os as _os`: selftest 86 checks, exit 0). Causa
confirmada: `env_reads()` comparava `node.value.id == "os"` literal.

Conserto: `env_reads()` coleta os nomes ligados por `import os|posix|nt [as X]` (nova constante
`OS_MODULES`) e trata `X.<ENV_ATTRS>` como leitura; o `from … import` passou a aceitar os três
módulos. `controls.py` ganhou `d-aliased-os`, com a substituição da Evidência.

Verificação:

```text
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 88 check(s) ran, 0 failure(s)
exit=0
$ python3 tools/duckmcp/controls.py --only d-aliased-os; echo exit=$?
baseline: the untouched sandbox is green
red    d-aliased-os (rule d): FAIL  rule (d): errors.py does not read the environment  line 12: _os.environ
duckmcp_controls: 1 control(s), 1 red as required; per rule (d) 1/1
exit=0
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 12 control(s), 12 red as required; per rule (a) 2/2, (c) 6/6, (d) 4/4
$ python3 $T/tools/duckmcp/selftest.py --quiet; echo exit=$?   # cópia plantada da Evidência
  FAIL  rule (d): errors.py does not read the environment  line 12: _os.environ
duckmcp_selftest: 88 check(s) ran, 1 failure(s)
exit=1
```
- **Closed** — commit `63bf946b` (2026-10-22): fix(duckmcp): resolve os aliases in rule (d) and plant d-aliased-os
  - Files (`git show --name-status 63bf946b`):
    - `M docs/tasks/duckmcp/CORR-DMCP-002.md`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
