---
id: CORR-LOOKS-036
title: "Correção: o critério da LOOKS-TASK-15 conta 11.789 linhas e a árvore dela tem 11.831"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-036: a varredura da regra 1 foi anotada antes do fim da task

## Problema identificado

O último critério de conclusão da LOOKS-TASK-15 fecha com o número da
varredura:

```text
docs/tasks/looks/15-visualizador-opengl.md
- [x] … A regra 1 alcança `ui/`: 17 arquivos, 11.789 linhas.
```

A contagem de arquivos bate. A de linhas não: a árvore que a task commitou tem
**11.831**. São 42 linhas de diferença, e a direção diz o que houve — o número
foi lido no meio da execução e o arquivo continuou crescendo depois.

É a mesma família da [`CORR-LOOKS-032`](/docs/tasks/looks/CORR-LOOKS-032.md),
que a LOOKS-TASK-14 pagou com 8.916 contra 10.182, e a lição de lá vale aqui
inteira: **o bloco de gate se roda no fim, e diz de qual árvore fala.**

## Evidência

Medido num worktree destacado no commit que fechou a task, duas vezes, o mesmo
número:

```text
$ git worktree add --detach <tmp> f2df3fc
$ cd <tmp> && python tools/looks/selftest.py --quiet
  ..... rule 1 swept 17 file(s), 11831 line(s)
  ..... 37 of 37 controls red
looks_selftest: 0 failure(s)
```

| afirmado | medido na árvore da própria task |
|---|---|
| 17 arquivos | 17 — bate |
| 11.789 linhas | **11.831** |

Os outros números do mesmo Log reproduzem todos, o que torna este mais fácil de
acreditar do que de conferir: `37 of 37 controls red`, os quatro controles
novos (33 → 37 entre `38705b2` e `f2df3fc`), e a saída inteira do
`scene.py --check-image`.

## Causa raiz

A contagem foi copiada para o critério antes das últimas edições da própria
task, e o gate não foi reexecutado ao fechar.

## Correção

### Arquivo: `docs/tasks/looks/15-visualizador-opengl.md`

Trocar 11.789 por **11.831** no critério, e nomear o commit ao lado — `f2df3fc`
—, que é o que a CORR-LOOKS-032 já fez com o bloco da 14 e o que impede o
número de envelhecer no commit seguinte: a árvore anda a cada correção, e um
número que declara "a árvore" sem dizer qual volta a estar errado.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/15-visualizador-opengl.md` | modificar |

## Verificação

- [ ] o número do critério é o que a varredura imprime no commit que ele nomeia
- [ ] `python tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
