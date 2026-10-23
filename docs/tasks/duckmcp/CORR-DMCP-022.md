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
