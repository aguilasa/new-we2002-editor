---
id: CORR-KRP-020
---

# CORR-KRP-020 — KRP-TASK-11 edita docs/PLAN-KITS-REPLAY.md sem declará-lo, e as tasks de fechamento pendentes repetem o modelo

Origin: [KRP-TASK-11](/docs/tasks/kits-replay/11-fechamento-da-fase-3.md)

## Problem

O commit de entrega 5a3e0df4 muda o `docs/PLAN-KITS-REPLAY.md` (+7 linhas, o parágrafo "Feito na
fase 3"). Mas o `files` da task está vazio, e o "Arquivos a criar ou modificar" dela diz "In: nenhum:
só reroda e corrige escrituração". O próprio Objetivo da task exige "o que a fase mudou está escrito
no plano".

A quinta regra entre ciclos do `CLAUDE.md` trata editar o plano sem `rite set <ID> --files …` e sem
uma linha em "Arquivos", no mesmo commit, como escopo não declarado. A KRP-TASK-10 declarou o plano;
a KRP-TASK-11 não.

As tasks de fechamento ainda pendentes (13, 16, 19 e 21) têm o mesmo modelo, com `files: []`, então
a falha vai se repetir.

## Evidência

```text
$ git show --stat 5a3e0df4
 docs/PLAN-KITS-REPLAY.md                          |  7 ++++
 docs/tasks/kits-replay/11-fechamento-da-fase-3.md | 39 ++++++++++++++++++++---
$ python3 -c "import json;d=json.load(open('docs/tasks/kits-replay/progress.json'));[print(t['id'],t.get('files')) for t in d['tasks'] if t['id'] in ('KRP-TASK-11','KRP-TASK-13','KRP-TASK-16','KRP-TASK-19','KRP-TASK-21')]"
KRP-TASK-11 []
KRP-TASK-13 []
KRP-TASK-16 []
KRP-TASK-19 []
KRP-TASK-21 []
$ sed -n 12,16p docs/tasks/kits-replay/11-fechamento-da-fase-3.md
- In:
  - nenhum: só reroda e corrige escrituração
```

## Root cause

(Hipótese.) O modelo de task de fechamento ("nenhum: só reroda") contradiz o "escrito no plano" do
Objetivo.

## Fix

- `rite set KRP-TASK-11 --files docs/PLAN-KITS-REPLAY.md`, e trocar o "nenhum" por uma linha
  `docs/PLAN-KITS-REPLAY.md` no "Arquivos a criar ou modificar" da task.
- Fazer o mesmo, já, nas tasks de fechamento pendentes 13, 16, 19 e 21, cujos Objetivos também
  escrevem no plano.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/11-fechamento-da-fase-3.md`
- `docs/tasks/kits-replay/13-fechamento-da-fase-4.md`
- `docs/tasks/kits-replay/16-fechamento-da-fase-5.md`
- `docs/tasks/kits-replay/19-fechamento-da-fase-6.md`
- `docs/tasks/kits-replay/21-fechamento-da-fase-7.md`

## Verificação

Rodar de novo o `python3 -c` da Evidência: as cinco linhas têm de listar
`['docs/PLAN-KITS-REPLAY.md']`. Hoje todas imprimem `[]`.

## Log de Execução

### 2026-10-16

Reprodução (`rite reproduce`, HEAD `397e9817`): `git show --stat 5a3e0df4` lista
`docs/PLAN-KITS-REPLAY.md | 7 ++++`; o `python3 -c` da Evidência imprime `[]` para as cinco tasks; o
"Arquivos" da 11 diz `nenhum: só reroda e corrige escrituração`.

Conserto: `rite set KRP-TASK-<N> --files docs/PLAN-KITS-REPLAY.md` para 11, 13, 16, 19 e 21, e no
"Arquivos a criar ou modificar" de cada uma o "nenhum" virou
`` `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no plano (o resto só reroda e corrige escrituração) ``.

Verificação:

```text
$ python3 -c "import json;d=json.load(open('docs/tasks/kits-replay/progress.json'));[print(t['id'],t.get('files')) for t in d['tasks'] if t['id'] in ('KRP-TASK-11','KRP-TASK-13','KRP-TASK-16','KRP-TASK-19','KRP-TASK-21')]"
KRP-TASK-11 ['docs/PLAN-KITS-REPLAY.md']
KRP-TASK-13 ['docs/PLAN-KITS-REPLAY.md']
KRP-TASK-16 ['docs/PLAN-KITS-REPLAY.md']
KRP-TASK-19 ['docs/PLAN-KITS-REPLAY.md']
KRP-TASK-21 ['docs/PLAN-KITS-REPLAY.md']
$ grep -c "nenhum: só reroda" docs/tasks/kits-replay/{11,13,16,19,21}-fechamento-*.md
docs/tasks/kits-replay/19-fechamento-da-fase-6.md:0
docs/tasks/kits-replay/21-fechamento-da-fase-7.md:0
docs/tasks/kits-replay/13-fechamento-da-fase-4.md:0
docs/tasks/kits-replay/11-fechamento-da-fase-3.md:0
docs/tasks/kits-replay/16-fechamento-da-fase-5.md:0
```
