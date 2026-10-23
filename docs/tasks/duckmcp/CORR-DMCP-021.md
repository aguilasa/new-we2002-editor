---
id: CORR-DMCP-021
---

# CORR-DMCP-021 — Atribuir as entradas PENDING do replay.py à task que o declara

Origin: [DMCP-TASK-17](/docs/tasks/duckmcp/17-regra-b.md)

## Problem

A `PENDING` diz que a DMCP-TASK-26 remove os dois sítios `import` do `tools/kits/replay.py`, mas os
arquivos declarados da 26 são só `tools/kits/controls.py`, `selftest.py` e `ui_check.py`; quem declara
o `replay.py` é a DMCP-TASK-25. O Log justifica a escolha dizendo que nenhuma task de migração nomeia o
`replay.py`, o que é falso. O check de entrada velha só fica vermelho quando um sítio some, então
depois que a 26 fechar essas entradas podem ficar com um dono que nunca toca o arquivo, e nada acusa
isso até a task 30.

## Evidência

```text
$ cd tools/duckmcp && python3 -c "import selftest;[print(e[0],e[1],e[2],e[4]) for e in selftest.PENDING if 'replay' in e[1]]"
DMCP-TASK-26 tools/kits/replay.py import 1
DMCP-TASK-26 tools/kits/replay.py import 1
$ sh "$RITE_HOME/bin/rite" context DMCP-TASK-25 --json | python3 -c "import json,sys;print(json.load(sys.stdin)['item']['files'])"
['tools/kits/oracle.py', 'tools/kits/replay.py']
$ sh "$RITE_HOME/bin/rite" context DMCP-TASK-26 --json | python3 -c "import json,sys;print(json.load(sys.stdin)['item']['files'])"
['tools/kits/controls.py', 'tools/kits/selftest.py', 'tools/kits/ui_check.py']
```

## Root cause

Hipótese: os donos foram atribuídos pelo título das tasks e pela prosa da §6 do plano, não pelos
`files` de cada task, que moram no estado do Rite e não no markdown.

## Fix

No `tools/duckmcp/selftest.py`, passar as duas entradas do `replay.py` (e o agrupamento
`# DMCP-TASK-26`) para a DMCP-TASK-25. Corrigir a frase nas Notas da
`docs/tasks/duckmcp/17-regra-b.md` (o Log é histórico: nota, não reescrita). Opcional: fazer o
`check_rule_b` afirmar que o arquivo de cada entrada está nos arquivos declarados da task dona.

## Arquivos a criar ou modificar

- `tools/duckmcp/selftest.py`
- `docs/tasks/duckmcp/17-regra-b.md`

## Verificação

```text
$ cd tools/duckmcp && python3 - <<'PY'
import json, subprocess, os, selftest
rite = ["sh", os.path.join(os.environ["RITE_HOME"], "bin", "rite")]
bad = []
for task, path, cat, snip, n in selftest.PENDING:
    if task == "DMCP-TASK-30":
        continue
    files = json.loads(subprocess.check_output(rite + ["context", task, "--json"], cwd="../..").decode())["item"]["files"]
    if path not in files:
        bad.append((task, path))
print(sorted(set(bad)))
raise SystemExit(1 if bad else 0)
PY
```

Hoje imprime `[('DMCP-TASK-26', 'tools/kits/replay.py')]` e sai 1; depois tem de imprimir `[]` e sair 0.

## Log de Execução

2026-10-23 — reproduzido: o laço da Verificação imprimia `[('DMCP-TASK-26', 'tools/kits/replay.py')]`.

Conserto: no `PENDING` do `tools/duckmcp/selftest.py`, as duas entradas `import` do `kits/replay.py`
passaram para o grupo da DMCP-TASK-25, que declara o arquivo. As Notas da `17-regra-b.md` ganharam a
correção da frase do Log, que continua como estava porque é histórico. A asserção opcional, conferir
os `files` da task dona dentro do selftest, não entrou: ela faria o gate depender do CLI do Rite.

Verificação:

```text
$ cd tools/duckmcp && python3 - <<'PY' … (laço da Verificação)
[]
exit=0
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 434 check(s) ran, 0 failure(s)
```
- **Closed** — commit `efe82757` (2026-10-23): fix(duckmcp): give the kits/replay.py PENDING entries to DMCP-TASK-25, which declares the file
  - Files (`git show --name-status efe82757`):
    - `M docs/tasks/duckmcp/17-regra-b.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-021.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/selftest.py`
