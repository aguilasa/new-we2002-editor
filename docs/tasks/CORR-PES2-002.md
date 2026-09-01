---
id: CORR-PES2-002
title: "Correção: as regras e os prompts dizem CORR-WTE, o pool vivo é CORR-PES2"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-PES2-002: o prefixo de correção está dito em dois lugares, e os dois discordam

## Problema identificado

O pool de correções vivo é `CORR-PES2-XXX`, decidido e escrito em
[`docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md):

> **A numeração deste pool começa em `CORR-PES2-001`.** […] O prefixo muda
> porque o projeto muda; a convenção de que **o pool é único dentro do ciclo**
> continua valendo.

Mas `.claude/rules/tasks.md` — instrução de projeto, carregada em toda sessão —
ainda afirma o contrário, e afirma como regra geral:

> O pool de correções é **único**, com a numeração `CORR-WTE-XXX` contínua,
> **qualquer que seja o projeto**.

E os quatro prompts de `docs/prompts/` mandam criar `CORR-WTE-XXX` na letra:
15 ocorrências no `02-revisar.md`, 11 no `03-corrigir.md`, 8 no `01-executar.md`,
7 no `04-corrigir-tudo.md`, 2 no `05-executar-lote.md`.

Isso é duas coisas erradas ao mesmo tempo:

1. **Contradição factual.** Quem seguir a regra ou o prompt abre
   `CORR-WTE-144.md` num ciclo cuja tabela e cujo arquivo de progresso
   esperam `CORR-PES2-001` — e o `check_tasks.py` não pega, porque CORR não
   entra na conferência dele.
2. **Violação da própria regra pela qual os prompts existem.** O mesmo
   `.claude/rules/tasks.md` diz, três parágrafos acima: *"**Não codifique num
   prompt** o nome de um plano, um **prefixo de ID**, uma fase ou um mapeamento
   `ID → arquivo`."* Prefixo de correção cravado em cinco prompts é exatamente
   o acoplamento que a regra proíbe, e é o que fez esta revisão ter de escolher
   entre dois textos.

## Evidência

```
$ grep -n 'CORR-WTE-XXX' .claude/rules/tasks.md
68:O pool de correções é **único**, com a numeração `CORR-WTE-XXX` contínua,

$ grep -c 'CORR-WTE' docs/prompts/*.md
docs/prompts/01-executar.md:8
docs/prompts/02-revisar.md:15
docs/prompts/03-corrigir.md:11
docs/prompts/04-corrigir-tudo.md:7
docs/prompts/05-executar-lote.md:2
docs/prompts/geral.md:0

$ grep -n 'CORR-PES2-001' docs/tasks/correcoes-progresso.md | head -2
15:**A numeração deste pool começa em `CORR-PES2-001`.** O pool anterior, com a
```

Datas de commit, que dizem qual texto é o mais novo — o pool venceu, e os
outros dois ficaram para trás:

```
$ git log -1 --format='%h %ad %s' --date=short -- docs/tasks/correcoes-progresso.md
0bdf350 2026-09-01 docs: put PES2 in the task pool -- 25 tasks for phases 2 to 6

$ git log -1 --format='%h %ad %s' --date=short -- .claude/rules/tasks.md
602218d 2026-09-01 docs(tasks): archive the closed cycle in docs/tasks/concluidos/
```

Esta revisão resolveu a favor do pool — as duas CORRs que ela abre se chamam
`CORR-PES2-001` e `CORR-PES2-002` —, e é essa escolha que precisa virar texto
para a próxima invocação não escolher diferente.

## Causa raiz

A troca de prefixo foi escrita no arquivo mais específico (o pool) e não foi
propagada para o mais geral (a regra) nem para os prompts, que a regra manda
manter agnósticos e que nunca foram.

## Correção

### Arquivo: `.claude/rules/tasks.md`

Trocar o parágrafo do pool por um que descreva a convenção sem cravar prefixo:

> O pool de correções é **único dentro do ciclo**, com numeração contínua a
> partir de `001`. **O prefixo é do ciclo, não da ferramenta** — o
> `correcoes-progresso.md` vivo é quem o declara, na primeira seção. Foi
> `CORR-WTE-` de 001 a 143 no ciclo arquivado em
> `docs/tasks/concluidos/`, e é `CORR-PES2-` no ciclo de PES2. Quem abre uma
> correção lê o prefixo ali, nunca deduz do prefixo das tasks.

### Arquivo: `docs/prompts/0{1,2,3,4,5}-*.md`

Trocar `CORR-WTE-XXX` por uma forma agnóstica — `CORR-<PREFIXO>-XXX`, com uma
linha dizendo que `<PREFIXO>` sai do `correcoes-progresso.md` —, do mesmo jeito
que os `*.template.md` de `docs/tasks/` já fazem com `/docs/tasks/CORR-<PREFIXO>-001.md`.
Os exemplos de caminho e de `git add` acompanham.

**Não renomear nada em `docs/tasks/concluidos/`.** Aqueles `CORR-WTE-*` são
história do ciclo fechado e o texto deles é evidência.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `.claude/rules/tasks.md` | modificar |
| `docs/prompts/01-executar.md` | modificar |
| `docs/prompts/02-revisar.md` | modificar |
| `docs/prompts/03-corrigir.md` | modificar |
| `docs/prompts/04-corrigir-tudo.md` | modificar |
| `docs/prompts/05-executar-lote.md` | modificar |

## Verificação

- [x] `grep -rn 'CORR-WTE' docs/prompts/ .claude/rules/` não devolve **nenhuma
      ocorrência prescritiva** — sobram 5, todas **citação de CORR real do ciclo
      fechado** (018, 137, 001, 122/123, e a frase da própria regra que nomeia o
      prefixo antigo). O item nasceu pedindo zero, o que contradiria a instrução
      desta mesma CORR de não mexer em história; a redação foi corrigida na
      execução, e a medida é o que está escrito aqui
- [x] `grep -rn 'CORR-WTE' docs/tasks/concluidos/ | wc -l` continua em **1155** —
      o arquivo histórico não foi tocado
- [x] A regra nova nomeia o `correcoes-progresso.md` como fonte do prefixo
- [x] `python3 tools/check_tasks.py` verde — 76 tasks, ok
- [x] Conferência de link de `.claude/rules/links.md` sem quebrado novo — a
      varredura de forma sobra só alvo fora de `docs/`, e a de existência sai
      vazia

## Log de Execução

**Executado em:** 2026-09-01

**Resumo do que foi feito.** As 43 ocorrências foram separadas em duas classes
antes de qualquer troca, e essa separação é o trabalho: **placeholder
prescritivo** — o que o prompt manda escrever — virou `CORR-<PREFIXO>-XXX`, e
**citação de CORR real do ciclo fechado** ficou como estava, porque é
evidência. As 8 do `01-executar.md` eram *todas* da segunda classe (linkadas a
`concluidos/`), então aquele prompt **não foi modificado**, ao contrário do que
a lista de arquivos previa. A regra passou a dizer que o prefixo é do ciclo e
que quem o declara é a primeira seção do `correcoes-progresso.md`. Os globs
executáveis viraram `CORR-*.md`, que funciona em qualquer prefixo —
`CORR-<PREFIXO>-*.md` não é glob que rode.

**Problemas encontrados.** Três, nenhum bloqueante.

1. **O item 1 da Verificação pedia o impossível certo.** `grep -rn 'CORR-WTE'
   docs/prompts/ .claude/rules/` devolvendo *nada* exigiria apagar a citação de
   CORR-WTE-018, -137, -001 e -122/123 — as armadilhas que os prompts registram
   —, o que contradiz a própria instrução desta CORR de não mexer em história.
   O item foi reescrito para a medida que importa: nenhuma ocorrência
   **prescritiva**.
2. **A varredura puxou dois arquivos que a lista da CORR não previa**, e os dois
   entraram nesta invocação: `.claude/rules/links.md` (o §"Template em bloco de
   código conta" citava `/docs/tasks/CORR-WTE-XXX.md` como o placeholder que os
   prompts escrevem — deixou de ser verdade no mesmo instante) e os quatro
   wrappers de `.claude/commands/`, com 9 ocorrências prescritivas, entre elas
   duas na linha `description:` do frontmatter, que é o texto que o usuário lê
   ao digitar a barra.
3. **Um segundo acoplamento da mesma família ficou de fora, e virou CORR nova.**
   Os prompts também cravam `WTE-TASK-XX` — prefixo de *task*, proibido pela
   mesma regra e pelo mesmo motivo —, e o ciclo vivo usa `PES2-TASK-XX`. É
   dívida independente desta correção: nem criada nem revelada por ela, e
   redimensionar no meio de um lote é o que o `04-corrigir-tudo.md` desaconselha.

**Arquivos criados/modificados:**

- `.claude/rules/tasks.md` — o parágrafo do pool
- `.claude/rules/links.md` — o placeholder citado no §"Template em bloco de código conta"
- `docs/prompts/02-revisar.md` — 13 trocas: modelo de frontmatter, de tabela, de
  checklist, de bloco, os dois exemplos de `git`
- `docs/prompts/03-corrigir.md` — 9 trocas
- `docs/prompts/04-corrigir-tudo.md` — 6 trocas
- `docs/prompts/05-executar-lote.md` — 2 trocas
- `.claude/commands/{corrigir,corrigir-tudo,revisar,executar-lote}.md` — 9 trocas
- `docs/prompts/01-executar.md` — **não modificado**; as 8 ocorrências são história
- `docs/tasks/correcoes-progresso.md` — tabela, checklist e data
