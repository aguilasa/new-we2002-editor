---
id: CORR-PES2-003
title: "Correção: os prompts e os wrappers cravam WTE-TASK-XX; o ciclo vivo é PES2-TASK-XX"
type: correção
category: processo
status: concluído
depends_on: [CORR-PES2-002]
---

# CORR-PES2-003: o prefixo de *task* está cravado nos prompts, pela mesma razão que o de correção estava

## Problema identificado

A [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md) tirou o prefixo de **correção**
dos prompts e dos wrappers, e deixou intacto o irmão dele: o prefixo de
**task**. Os cinco prompts e os cinco wrappers mandam executar `WTE-TASK-XX` na
letra — 39 e 11 ocorrências —, enquanto o `progresso.md` vivo lista
`PES2-TASK-01` a `PES2-TASK-25`.

É a mesma violação, do mesmo parágrafo da mesma regra:

> **Não codifique num prompt** o nome de um plano, um **prefixo de ID**, uma
> fase ou um mapeamento `ID → arquivo`.
> — [`.claude/rules/tasks.md`](../../.claude/rules/tasks.md)

E a regra explica por quê com este caso exato: *"prompt que conhece um deles
pelo nome quebra no próximo"*. Quebrou. As três exclusões que dizem "nunca
execute `WTE-TASK-XX` por aqui" hoje não nomeiam **nenhuma** task existente, e
uma exclusão que não alcança o objeto proibido não exclui coisa nenhuma.

Ficou de fora da CORR-PES2-002 de propósito: dívida independente, nem criada
nem revelada por aquele conserto, e redimensionar CORR no meio de um lote é o
que o [`04-corrigir-tudo.md`](/docs/prompts/04-corrigir-tudo.md) desaconselha.

## Evidência

```
$ grep -rno 'WTE-TASK' docs/prompts/*.md .claude/commands/*.md \
    | cut -d: -f1 | sort | uniq -c
      2 .claude/commands/corrigir.md
      1 .claude/commands/corrigir-tudo.md
      3 .claude/commands/executar-lote.md
      4 .claude/commands/executar.md
      1 .claude/commands/revisar.md
     18 docs/prompts/01-executar.md
     10 docs/prompts/02-revisar.md
      2 docs/prompts/03-corrigir.md
      3 docs/prompts/04-corrigir-tudo.md
      6 docs/prompts/05-executar-lote.md

$ grep -o 'PES2-TASK-[0-9]*' docs/tasks/progresso.md | head -2
PES2-TASK-01
PES2-TASK-02
```

Uma das exclusões, verbatim, para mostrar o que ela alcança hoje:

```
$ grep -n 'exclusivo para' docs/prompts/03-corrigir.md
> Este prompt é exclusivo para `CORR-<PREFIXO>-XXX`. **Nunca** execute `WTE-TASK-XX`
```

O lado esquerdo já é agnóstico (CORR-PES2-002); o direito nomeia um prefixo que
não existe mais no `progresso.md` vivo.

## Causa raiz

A CORR-PES2-002 nasceu de escolher o nome do primeiro **arquivo de correção**
do ciclo, então mediu só esse prefixo. O de task tem a mesma origem — o ciclo
`WTE` foi arquivado e o prefixo mudou junto — e não foi medido porque ninguém
precisou dele naquela invocação.

## Correção

### Arquivos: `docs/prompts/0{1,2,3,4,5}-*.md` e `.claude/commands/*.md`

Mesma forma que a CORR-PES2-002 aplicou ao outro prefixo: `<PREFIXO>-TASK-XX`,
com uma linha por prompt dizendo que `<PREFIXO>` sai do
[`progresso.md`](/docs/tasks/progresso.md) — que é a fonte análoga do
`correcoes-progresso.md`, e o arquivo que o prompt já lê no primeiro passo.

Duas distinções a manter, e são o trabalho:

- **Citação de task real do ciclo fechado fica como está.** Vale para
  `WTE-TASK-08` no `01-executar.md`, e para toda menção acompanhada de link
  para `/docs/tasks/concluidos/` — é evidência do que aconteceu, e a
  CORR-PES2-002 já provou que a varredura ingênua a apaga.
- **Glob executável fica genérico.** `ls docs/tasks/*-TASK-*.md` roda em
  qualquer prefixo; `<PREFIXO>-TASK-*.md` não roda em nenhum.

### Arquivo: `.claude/rules/tasks.md`

O parágrafo do pool já diz que o prefixo de **correção** é do ciclo. Acrescentar
a metade que falta: o de **task** também é, e quem o declara é o `progresso.md`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `.claude/rules/tasks.md` | modificar |
| `docs/prompts/01-executar.md` | modificar |
| `docs/prompts/02-revisar.md` | modificar |
| `docs/prompts/03-corrigir.md` | modificar |
| `docs/prompts/04-corrigir-tudo.md` | modificar |
| `docs/prompts/05-executar-lote.md` | modificar |
| `.claude/commands/*.md` | modificar (os cinco) |

## Verificação

- [x] Nenhuma ocorrência **prescritiva** de `WTE-TASK` sobra em
      `docs/prompts/` e `.claude/commands/`. Das 50, **20 eram prescritivas** e
      viraram `<PREFIXO>-TASK-XX`; **28 são citação de task real do ciclo
      fechado** e ficaram (as duas exceções de antecipação, os gates datados,
      os cinco cabeçalhos de fase da Etapa 3 do `02-revisar.md`, as armadilhas
      da §"prosa vencida"); as **2 restantes** são as linhas novas de
      declaração, que nomeiam `WTE-TASK-XX` como o prefixo *anterior*
- [x] `grep -rn 'WTE-TASK' docs/tasks/concluidos/ | wc -l` inalterado em **1411**
- [x] As três exclusões "nunca execute … por aqui" passam a alcançar o objeto
      que proíbem no ciclo vivo — conferidas verbatim, as três dizem agora
      `<PREFIXO>-TASK-XX` com a fonte do prefixo ao lado
- [x] `python3 tools/check_tasks.py` verde — 76 tasks, ok
- [x] Conferência de link de `.claude/rules/links.md` sem quebrado novo — a de
      destino sai vazia; a de forma sobra só `../README.md` (alvo fora de
      `docs/`) e transcrição em `concluidos/`, ambos pré-existentes

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** Evidência reproduzida verbatim antes de editar:
**39 + 11 = 50** ocorrências, distribuídas exatamente como a CORR previa, e o
`progresso.md` vivo com **25** `PES2-TASK-*`. A classificação é o trabalho, e
repetiu o método da [CORR-PES2-002](/docs/tasks/CORR-PES2-002.md): **20
prescritivas** viraram `<PREFIXO>-TASK-XX` — as três exclusões "nunca execute …
por aqui", os quatro modelos de link de tabela, os dois `git commit -m` de
modelo, os exemplos de argumento dos wrappers, e as menções genéricas a
"trabalho de `WTE-TASK`" —, e **28 citações de task real do ciclo fechado**
ficaram intactas. Três prompts ganharam a linha que declara de onde sai o
`<PREFIXO>` (o `progresso.md`, análogo do `correcoes-progresso.md`), e a regra
ganhou a metade que faltava.

**Problemas encontrados.** Dois, nenhum bloqueante.

1. **Um caso em que trocar seria pior que não trocar**, e ele decidiu o
   critério. Os cinco cabeçalhos da Etapa 3 do `02-revisar.md` — `**Fase 0-1
   (WTE-TASK-01 a 09)**` e irmãos — indexam 73 linhas de checklist sobre `.dfm`,
   `.lfm`, stubs e assets do Obocaman. Reescrevê-los como `<PREFIXO>-TASK-01 a
   09` afirmaria que esse checklist vale para as fases de PES2, que não têm nada
   disso. Ficaram como estão: o texto está certo sobre o ciclo que descreve.
2. **Isso revelou uma discrepância maior que esta CORR**, e ela virou
   [CORR-PES2-004](/docs/tasks/CORR-PES2-004.md): os prompts ficaram agnósticos
   de plano e de prefixo e continuam com um corpo inteiro de conteúdo
   operacional do `wte/` — 64 caminhos `wte/` cravados, os gates datados por
   task de outro ciclo, a tabela de geradores, e o `04-corrigir-tudo.md`
   abrindo com *"Você vai trabalhar no projeto WE2002 Team Editor → Lazarus"*.
   Não é substituição, é separação, e a forma é decisão do usuário — exatamente
   o "se a discrepância for grande, abra a CORR nova e reporte" do
   `03-corrigir.md`.

**Arquivos criados/modificados:**

- `.claude/rules/tasks.md` — parágrafo novo: o prefixo de task também é do
  ciclo, e quem o declara é o `progresso.md`
- `docs/prompts/01-executar.md` — 2 (declaração + modelo de link)
- `docs/prompts/02-revisar.md` — 5
- `docs/prompts/03-corrigir.md` — 2
- `docs/prompts/04-corrigir-tudo.md` — 3
- `docs/prompts/05-executar-lote.md` — 4
- `.claude/commands/{executar,executar-lote,revisar,corrigir,corrigir-tudo}.md` — 7
- `docs/tasks/correcoes-progresso.md` — tabela, checklist e data
