---
id: CORR-WTE-108
title: "Correção: a WTE-TASK-35 deixa \"o plano é o que falta conferir\" e o plano nunca afirmou aquilo"
type: correção
category: processo
status: concluído
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

- [x] `grep -n "falta conferir" docs/tasks/35-divergencias-deliberadas.md` sai vazio
- [x] `grep -c "idempot\|cobrador\|OFS_KICKER" docs/PLAN-WTE-LAZARUS.md` continua `0`
- [x] `make -C wte check` verde (809 testes)
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-25

**Resumo do que foi feito:**

*"O plano é o que falta conferir"* virou o resultado da conferência: o
`PLAN-WTE-LAZARUS.md` tem **zero** ocorrências de
`idempot`/`cobrador`/`OFS_KICKER`/`vaivém`, e a fase 6 dele não fala em gravar
duas vezes — conferido também por `grep "duas vezes"` no plano inteiro, que só
acha duas linhas sobre outro assunto. Não sobra nada a corrigir ali.

A frase mandava alguém procurar um texto que não existe, que é palavra por
palavra o defeito que esta mesma task nomeia ao explicar por que **removeu** a
isenção `pendente_32`: *"uma entrada falsa manda alguém procurar um problema
que não existe"*.

**Problemas encontrados:**

**A frase era minha, escrita uma execução antes.** Ela entrou pela
[CORR-WTE-105](/docs/tasks/CORR-WTE-105.md), no mesmo lote em que a
[CORR-WTE-104](/docs/tasks/CORR-WTE-104.md) fez a medição — e a 105 supôs que o
plano repetia a frase da task 34 sem conferir. Registrado porque é o tipo de
erro que a revisão pegou depressa e que a execução não teria pego sozinha.

**E a varredura achou coisa maior, que ficou fora de propósito.** Quatro sítios
vivos do lado WTE atribuem a não-idempotência a *"o original"* / *"o editor
original"* — e neste projeto "o original" é o **`wte.exe`**, não o `ed.exe`:
`gravacao_controle.py:197` (gerador) e o `gravacao-controle.md:19` que ele gera,
mais as tasks 19 e 27. O `golden-24` diz o mesmo mas **atribui** (*"o
`newWe2002` registra que…"*), o que o salva; os do `PLAN-LINUX.md` e do
`CLAUDE.md` estão certos, porque lá o oráculo é o `ed.exe`.

Não consertei junto, e a razão é de medida, não de escopo: a CORR-WTE-104 mediu
**um** caminho de gravação — o da tática, que é o que carrega `OFS_KICKER` — e a
frase dos quatro sítios é sobre o ciclo `Load`+`Save` em geral. Trocar "o
original" por "o `ed.exe`" seria provavelmente certo e não está medido; se
outro caminho reproduzir o vaivém, a troca teria criado a mentira simétrica.
Aberta a [CORR-WTE-109](/docs/tasks/CORR-WTE-109.md), com o caminho barato de
medir a pergunta geral (o próprio `gravacao-controle`, rodado duas vezes), e a
entrada da task 35 aponta para ela.

**Arquivos criados/modificados:**

- `docs/tasks/35-divergencias-deliberadas.md` — a decisão, com o resultado
- `docs/tasks/CORR-WTE-109.md` — criada, a discrepância maior
- `docs/tasks/correcoes-progresso.md` — o `[x]` da 108 e a linha da 109
