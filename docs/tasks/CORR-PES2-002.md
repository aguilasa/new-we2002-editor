---
id: CORR-PES2-002
title: "Correção: as regras e os prompts dizem CORR-WTE, o pool vivo é CORR-PES2"
type: correção
category: processo
status: pendente
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

- [ ] `grep -rn 'CORR-WTE' docs/prompts/ .claude/rules/` não devolve nada
- [ ] `grep -rn 'CORR-WTE' docs/tasks/concluidos/ | wc -l` continua no valor de
      antes — o arquivo histórico não foi tocado
- [ ] A regra nova nomeia o `correcoes-progresso.md` como fonte do prefixo
- [ ] `python3 tools/check_tasks.py` verde
- [ ] Conferência de link de `.claude/rules/links.md` sem quebrado novo

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
