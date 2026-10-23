---
id: CORR-DMCP-022
---

# CORR-DMCP-022 — Plantar controles para as três asserções da regra (b) sem vigia

Origin: [DMCP-TASK-17](/docs/tasks/duckmcp/17-regra-b.md)

## Problem

O `check_rule_b` acrescenta seis asserções, e o `controls.py` planta defeito para só três (sítio novo,
entrada velha, task desconhecida). "every PENDING count is at least 1", "no key appears twice in
PENDING" e "PENDING lists N site(s) ... audit.py counts N" não têm controle nem vermelho no Log. O
critério 4 ("o tamanho da lista bate") se apoia na última, que nem pode ficar vermelha sozinha: com
"new" e "stale" vazios os contadores são iguais, então as somas também; só uma contagem negativa a
separa, e o check de contagem ≥ 1 também pega isso. "Verificador sem vermelho visto não é gate."

## Evidência

```text
$ grep -n 'count is at least\|appears twice\|lists %d site' tools/duckmcp/controls.py
(nenhuma saída)
$ python3 tools/duckmcp/controls.py --list | grep -c '^b-'
4
```

Os quatro são `b-import-fork-kit2d`, `b-client-call-kit2d`, `b-stale-entry`, `b-unknown-task`. Numa
cópia `git archive HEAD tools`, trocar no `selftest.py` a entrada
`('DMCP-TASK-20', 'tools/pes2/who_writes.py', 'client',\n     'client.call("breakpoint", action="clear")', 2),`
por duas entradas idênticas de contagem 1:

```text
$ python3 tools/duckmcp/selftest.py --quiet | grep FAIL
FAIL  rule (b): no key appears twice in PENDING  [('tools/pes2/who_writes.py', 'client', 'client.call("breakpoint", action="clear")')]
```

A asserção funciona, mas só um patch ad hoc o mostra; nenhum controle versionado a planta.

## Root cause

Os controles foram escritos para as duas direções nomeadas nos critérios (sítio novo, entrada velha)
mais o ID da task; as asserções de escrituração entraram sem planta correspondente.

## Fix

No `tools/duckmcp/controls.py`, controles `b-duplicate-key` (dividir uma entrada de contagem 2 em duas
de 1) e `b-zero-count` (uma contagem 0). Para a asserção de tamanho: retirá-la por estar implicada na
igualdade de multiconjunto, ou plantar um controle que só ela pegue (ex.: comparar com um total do
`audit.py` recontado à parte). Nos dois casos, dizer no docstring do selftest o que a linha de tamanho
guarda.

## Arquivos a criar ou modificar

- `tools/duckmcp/controls.py`
- `tools/duckmcp/selftest.py`

## Verificação

`python3 tools/duckmcp/controls.py --list | grep -cE '^b-(duplicate|zero)'` dá 0 hoje e tem de dar 2;
depois `python3 tools/duckmcp/controls.py --only b-duplicate-key` termina em "1 red as required".

## Log de Execução

2026-10-23 — reproduzido: `python3 tools/duckmcp/controls.py --list | grep -cE '^b-(duplicate|zero)'`
dava `0`, e havia quatro controles `b-`.

Conserto:
- **Dois controles para o que só o check de escrituração pega.**
  - `b-duplicate-key` divide a entrada `client.call("breakpoint", action="clear")` (contagem 2) em duas
    de 1. O multiconjunto não muda, então só "no key appears twice" fica vermelho.
  - `b-zero-count` zera uma contagem.
- **A asserção de tamanho ficou, com um papel que só ela tem.** Ela amarra o `PENDING` ao `total` que o
  `audit.py` imprime, que é o número colado nos Logs de migração. O controle `b-total-drifts`
  (`"total": len(sites) + 1` no `audit.py`) mostra que ela fica vermelha quando o total se descola dos
  sítios que o `site_keys` conta, algo que as linhas de multiconjunto não veem.
- **O docstring do `check_rule_b`** agora diz o que cada linha guarda.

Verificação:

```text
$ for c in b-duplicate-key b-zero-count b-total-drifts; do python3 tools/duckmcp/controls.py --only $c | sed -n 2p; done
red    b-duplicate-key (rule b): FAIL  rule (b): no key appears twice in PENDING  [('tools/pes2/who_writes.py', 'client', 'client.call("breakpoint", action="clear")')]
red    b-zero-count (rule b): FAIL  rule (b): every PENDING count is at least 1  [('tools/kit2d/selftest.py', 'sys.path', 'sys.path.insert(0, os.path.join(TOOLS_DIR, "pes2"))')]
red    b-total-drifts (rule b): FAIL  rule (b): PENDING lists 206 site(s) in 108 entries, audit.py counts 207
$ python3 tools/duckmcp/controls.py --list | grep -cE '^b-(duplicate|zero)'
2
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 40 control(s), 40 red as required; 21/21 cover rules (a) to (d); per rule (a) 2/2, (b) 7/7, (c) 8/8, (client) 2/2, (d) 4/4, (debug) 2/2, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 434 check(s) ran, 0 failure(s)
```
- **Closed** — commit `ef02cfe0` (2026-10-23): test(duckmcp): plant the rule (b) bookkeeping checks: duplicate key, zero count, total drift
  - Files (`git show --name-status ef02cfe0`):
    - `M docs/tasks/duckmcp/CORR-DMCP-022.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/selftest.py`
