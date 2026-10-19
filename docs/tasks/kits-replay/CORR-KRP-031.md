---
id: CORR-KRP-031
---

# CORR-KRP-031 — Decisões confirmadas do plano e do perfil ainda trazem o goleiro pela família 13 sem nota de desfeito

Origin: [KRP-TASK-25](/docs/tasks/kits-replay/25-desfazer-a-krp-task-12-goleiro-volta-ao-edt-mod.md)

## Problem

Duas listas de decisões confirmadas ainda dão como vigente o goleiro desenhado pela família 13, sem
nota datada de que isso foi desfeito: a do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md) (linha 35)
e a do [perfil-kits-replay.md](/docs/prompts/perfil-kits-replay.md) (linha 14). O desfazer está
registrado só na §4 e no cabeçalho da Fase 4a do perfil.

Nem a KRP-TASK-25 nem a KRP-TASK-26 (a de fechamento, cujo escopo é só a linha "Feito na fase 4" da
§4 e a §10) atualizam essas listas. A regra do `CLAUDE.md` "Fechar um veredito é varrer quem dizia o
anterior" cita o perfil e o plano pelo nome.

## Evidência

```text
$ grep -n "família 13" docs/prompts/perfil-kits-replay.md docs/PLAN-KITS-REPLAY.md
docs/prompts/perfil-kits-replay.md:14:- **O goleiro passa a ser desenhado pela família 13**, com a pose medida e a 92 no lugar da 15; reabre a [K3D-TASK-10](...) (usuário, 2026-10-12; [§4](...)).
docs/PLAN-KITS-REPLAY.md:35:- **O goleiro passa a ser desenhado pela família 13**, com a pose medida e a 92 no lugar da 15.
$ grep -n "Desfeito em" docs/PLAN-KITS-REPLAY.md
357:**Desfeito em 2026-10-18, por decisão do usuário**
```

O `grep` de "família 13" também acha linhas de §4 e da tabela da §10; as citadas acima são as duas
listas de decisões.

## Root cause

(Hipótese.) O escopo da KRP-TASK-25 citava só a §4 do plano, e o perfil não está entre os arquivos
dela, então a varredura parou na seção revertida.

## Fix

Acrescentar o desfazer de 2026-10-18, datado, como linha junto da decisão da família 13 (ou marcando
essa decisão) nas "Decisões confirmadas" do `docs/PLAN-KITS-REPLAY.md` e no "Contexto essencial" do
`docs/prompts/perfil-kits-replay.md`.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-REPLAY.md`
- `docs/prompts/perfil-kits-replay.md`

## Verificação

```sh
grep -n -A3 "passa a ser desenhado pela família 13" docs/PLAN-KITS-REPLAY.md docs/prompts/perfil-kits-replay.md | grep -c "desfeit"
```

Hoje imprime 0. Depois do conserto tem de imprimir 2.

## Log de Execução

### 2026-10-19

Reprodução (`rite reproduce --all --cycle kits-replay`, HEAD `ab98809b`): `grep -n "família 13"`
mostrou a decisão vigente em `docs/prompts/perfil-kits-replay.md:14` e `docs/PLAN-KITS-REPLAY.md:35`,
sem nota de desfeito; a Verificação dava 0.

Conserto: nas duas listas de decisões, uma linha datada logo abaixo da decisão da família 13 diz que
ela foi desfeita em 2026-10-19 (o revert `afbcf78c`, `git log -1 --format=%ad --date=short afbcf78c`
dá `2026-10-19`), por decisão do usuário de 2026-10-18 (Notas da KRP-TASK-25, linha 39), com link
para a KRP-TASK-25 e para a §4.

Verificação:

```text
$ grep -n -A3 "passa a ser desenhado pela família 13" docs/PLAN-KITS-REPLAY.md docs/prompts/perfil-kits-replay.md | grep -c "desfeit"
2
```
