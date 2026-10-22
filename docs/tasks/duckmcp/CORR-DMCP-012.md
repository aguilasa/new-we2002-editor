---
id: CORR-DMCP-012
---

# CORR-DMCP-012 — Colar no Log da 12 as transcrições do selftest e do controle press-without-duration

Origin: [DMCP-TASK-12](/docs/tasks/duckmcp/12-session.md)

## Problem

O critério 4 diz que o controle vermelho é "visto no Log", e as regras do repositório pedem que o Log
mostre o vermelho e traga números colados da ferramenta. O Log da `12-session.md` não tem comando nem
saída: diz que o controle "fica vermelho na asserção ..." e manda a evidência para "o relatório do
worker", que não está no repositório. A contagem `361 check(s)` do critério 1 não aparece na task. O
comportamento reproduz hoje (ver a Evidência); o achado é de rastreabilidade, não de função quebrada.

## Evidência

```text
$ git show 0c58ebd7 -- docs/tasks/duckmcp/12-session.md | grep -c '^+\s*\$ '
0
$ grep -n 'relatório do worker' docs/tasks/duckmcp/12-session.md
**Verificação** (comandos e saída decisiva no relatório do worker): ...
$ python3 tools/duckmcp/selftest.py | tail -1
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
$ python3 tools/duckmcp/controls.py --only press-without-duration
red    press-without-duration (rule session): FAIL  session: press always sends duration_frames (pitfall 36)  [{'button': 'Down'}, {'button': 'Cross'}, {'button': 'Start'}]
```

## Root cause

Hipótese: o worker guardou as transcrições no relatório de entrega e escreveu só um resumo no Log.

## Fix

Acrescentar ao Log da `docs/tasks/duckmcp/12-session.md` a linha `$ python3 tools/duckmcp/selftest.py`
com a última linha e as linhas de session/buttons, e a linha
`$ python3 tools/duckmcp/controls.py --only press-without-duration` com a saída vermelha, refeitas na
HEAD entregue.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/12-session.md`

## Verificação

`grep -n 'controls.py --only press-without-duration' docs/tasks/duckmcp/12-session.md && grep -n 'check(s) ran' docs/tasks/duckmcp/12-session.md`
— hoje os dois vazios; depois do conserto os dois casam.

## Log de Execução
