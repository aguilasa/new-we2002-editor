---
id: CORR-WTE-099
title: "Correção: a lista de arquivos da WTE-TASK-32 não menciona a mudança no .gitignore"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-099: a lista de arquivos da WTE-TASK-32 omite o `.gitignore`

## Problema identificado

O commit que fechou a
[WTE-TASK-32](/docs/tasks/concluidos/32-preco-do-jogador.md) (`c566455`) tocou **31**
arquivos. A seção *"Arquivos criados/modificados"* do Log lista trinta; o que
falta é o `.gitignore`, que ganhou quinze linhas — as regras que impedem os
binários compilados de `wte/tests/` de entrarem no repositório.

A mudança é **certa** e está bem comentada no próprio arquivo (*"executável sem
extensão no meio de fonte versionado é fácil de commitar por engano, e foi o
que quase aconteceu com o `dump_preco` e o `test_preco`"*). O que falta é o
registro: é a única alteração da task que não é sobre preço, e é justamente o
tipo que alguém procuraria depois — "quando foi que passamos a ignorar os
binários de teste?".

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git show --stat --format= c566455 | head -3
git show c566455 -- .gitignore | grep -c '^+'
```

```text
 .gitignore                            |  15 ++
 docs/PLAN-WTE-LAZARUS.md              |   4 +-
 docs/tasks/32-preco-do-jogador.md     | 128 ++++++++++--
16
```

As regras acrescentadas, e a prova de que nenhum dos binários está versionado:

```bash
git ls-files wte/tests/ | grep -v '\.pas$\|\.cpp$\|roteiros/\|README'
```

```text
(vazio)
```

## Causa raiz

O `.gitignore` foi editado no meio da execução, ao ver o `dump_preco`
compilado aparecer no `git status`, e não voltou para a lista de arquivos ao
escrever o Log.

## Correção

### Arquivo: `docs/tasks/concluidos/32-preco-do-jogador.md`

Na lista *"Arquivos criados/modificados"*, acrescentar aos **modificados**:

> `.gitignore` — as dez regras dos binários compilados de `wte/tests/`
> (`dump_preco`, `test_preco` e os oito irmãos), que são gerados pelo
> `check_preco.py`, pelo `compara_tela.sh` e pelos testes de ferramenta

É a terceira vez que a lista de arquivos de uma task fica devendo um item
([CORR-WTE-078](/docs/tasks/concluidos/CORR-WTE-078.md),
[CORR-WTE-087](/docs/tasks/concluidos/CORR-WTE-087.md)). Se valer a pena fechar a porta, o
lugar é o `01-executar.md`: fechar a task conferindo a lista contra
`git show --stat --format= HEAD`, que é uma linha e responde sozinha.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/32-preco-do-jogador.md` | modificar |
| `docs/prompts/01-executar.md` | modificar (opcional — a conferência da lista) |

## Verificação

- [x] A lista da task cobre os 31 arquivos de `git show --stat --format= c566455`
      — conferidos um a um contra a lista; os sete que não aparecem em nome
      próprio estão em forma coletiva (`os dois .uses`, `os ep2002_*.pas`,
      `golden-22-precos{,.port}.txt`), e o trigésimo primeiro é o markdown da
      própria task, que é a omissão convencional
- [x] `git ls-files wte/tests/` continua sem binário
- [x] `make -C wte check` verde — 764 testes, `OK (skipped=1)`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

O `.gitignore` entrou na lista de modificados da WTE-TASK-32, com o que ele
ganhou e por quê, e com a frase que diz por que ele é o item que alguém procura
depois: é a única alteração da task que não é sobre preço.

**E a porta foi fechada**, porque a terceira ocorrência do mesmo formato é
padrão e não acaso. A conferência entrou no
[`01-executar.md`](/docs/prompts/01-executar.md), no ponto em que a lista é
escrita, e é literalmente uma linha:

```bash
git show --stat --format= HEAD
```

Todo caminho do commit tem de estar na lista, em nome próprio ou em forma
coletiva; o markdown da própria tarefa é a omissão convencional, e isso está
escrito para não virar dúvida. O bloco cita as três correções que a motivaram —
[078](/docs/tasks/concluidos/CORR-WTE-078.md), [087](/docs/tasks/concluidos/CORR-WTE-087.md) e esta.

**Problemas encontrados:**

1. **O wrapper `.claude/commands/executar.md` reafirma o mesmo rito com outras
   palavras**, e uma regra nova só no prompt teria durado até alguém ler o
   wrapper. Ele ganhou a mesma frase, curta. É o par prompt+wrapper que a
   matriz de conflito do `04-corrigir-tudo.md` já manda tratar como um item só.
2. **A forma coletiva é legítima e precisava ficar dita.** Sete dos 31 caminhos
   nunca apareceram em nome próprio na lista da 32 e a lista está certa — uma
   regra que exigisse nome por nome reprovaria trinta listas boas para pegar
   uma ruim.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `docs/tasks/concluidos/32-preco-do-jogador.md` | modificado — o `.gitignore` na lista |
| `docs/prompts/01-executar.md` | modificado — a conferência da lista contra o commit |
| `.claude/commands/executar.md` | modificado — a mesma frase, no wrapper |
