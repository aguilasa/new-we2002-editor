---
id: CORR-WTE-108
title: "Correção: a WTE-TASK-35 deixa \"o plano é o que falta conferir\" e o plano nunca afirmou aquilo"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-WTE-108: um "falta conferir" que já está conferido

## Problema identificado

A candidata do vaivém dos cobradores, na
[WTE-TASK-35](/docs/tasks/35-divergencias-deliberadas.md), fecha assim:

> *Decisão:* corrigir o enunciado da fase 6 para dizer `ed.exe` onde hoje diz
> "o editor". A [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) já foi
> reconciliada; **o plano é o que falta conferir.**

Conferido nesta revisão: **o plano nunca afirmou aquilo.** O
`docs/PLAN-WTE-LAZARUS.md` não contém `idempot`, `cobrador`, `OFS_KICKER` nem
`vaivém` em lugar nenhum. A afirmação morava em dois sítios, e os dois já
dizem `ed.exe`: o enunciado da WTE-TASK-34 e a prosa gerada do
[`golden.md`](../../wte/re/golden.md).

A frase manda alguém procurar um texto que não existe — que é, palavra por
palavra, o defeito que esta mesma task nomeia como princípio ao explicar por
que **removeu** a isenção `pendente_32` em vez de registrá-la: *"uma entrada
falsa manda alguém procurar um problema que não existe"*.

O registro durável — o [`divergencias.md`](../../wte/re/divergencias.md) — está
**correto**: a entrada 6 não carrega a pendência. O resto é só no arquivo da
task.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -c "idempot\|cobrador\|OFS_KICKER\|vaivém\|vaivem" docs/PLAN-WTE-LAZARUS.md
grep -n "plano é o que falta conferir" docs/tasks/35-divergencias-deliberadas.md
grep -n "não é" wte/re/golden.md | head -1
```

```text
0
260:  reconciliada; o plano é o que falta conferir.
98:carrega `OFS_KICKER`: o `newWe2002` registra que o **`ed.exe`** não é
```

| Sítio | O que diz hoje |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | **nada** sobre idempotência — zero ocorrências |
| `docs/tasks/34-…md` linha 46 | *"o `newWe2002` registra que o **`ed.exe`** não é idempotente"* — já reconciliado |
| `wte/re/golden.md` linha 98 | idem, gerado pelo `check_golden.py` |
| `wte/re/divergencias.md` entrada 6 | correto, sem pendência |

## Causa raiz

A decisão foi escrita supondo que o plano repetia a frase da task 34, e a
suposição não foi conferida antes de virar pendência.

## Correção

### Arquivo: `docs/tasks/35-divergencias-deliberadas.md`

Trocar *"o plano é o que falta conferir"* pelo resultado da conferência:

> A [WTE-TASK-34](/docs/tasks/34-bateria-golden-completa.md) já foi
> reconciliada e o `golden.md` é gerado dizendo `ed.exe`; **o plano nunca
> afirmou o vaivém** — conferido em 2026-08-25, zero ocorrências de
> `idempot`/`cobrador`/`OFS_KICKER` no `PLAN-WTE-LAZARUS.md`. Não sobra nada a
> corrigir.

Resultado negativo escrito vale mais que pendência apagada: quem reler daqui a
um mês não refaz a busca.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/35-divergencias-deliberadas.md` | modificar |

## Verificação

- [ ] `grep -n "falta conferir" docs/tasks/35-divergencias-deliberadas.md` sai vazio
- [ ] `grep -c "idempot\|cobrador\|OFS_KICKER" docs/PLAN-WTE-LAZARUS.md` continua `0`
- [ ] `make -C wte check` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
