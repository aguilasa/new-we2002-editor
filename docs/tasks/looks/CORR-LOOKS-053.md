---
id: CORR-LOOKS-053
title: "Correção: a LOOKS-TASK-19 diz \"quatro alvos\" no título e \"três\" no objetivo, e mantém como convenção o `if(UNIX …)` que ela mediu errado"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-LOOKS-053: prosa vencida dentro da própria task

## Problema identificado

A execução da LOOKS-TASK-19 corrigiu no lugar o título, os critérios, a §4.4 e
a Definição de pronto do plano, e a tabela de gates do perfil — todos passaram a
dizer **quatro** alvos, com a data e o que diziam antes. Duas frases da própria
task ficaram para trás:

```text
docs/tasks/looks/19-alvos-de-ctest-e-cli.md
  title: "`cli.py` e os quatro alvos de `ctest`"            (frontmatter)

  ## Contexto
  - A convenção do repositório é um alvo por faixa de custo: … os de
    display/venv sob `if(UNIX AND Python3_FOUND)`.

  ## Objetivo
  `tools/looks/cli.py` responde pelas perguntas do projeto, e o `ctest`
  registra os três alvos.
```

O **Objetivo** contradiz o título duas linhas acima. E o **Contexto** apresenta
como regra a forma que o terceiro critério da mesma task declara **medida como
errada** para este ciclo — sob `if(UNIX …)` o `looks_ui` sumiria da máquina
Windows onde ele roda, e `ctest -R looks_ui` sairia zero.

A frase do Contexto é verdadeira como descrição do repositório (o `mcr_ui` está
sob `if(UNIX)`), e é por isso que ela engana: lida de cima, é instrução.

## Evidência

```text
$ grep -n "três alvos\|UNIX AND Python3_FOUND" docs/tasks/looks/19-alvos-de-ctest-e-cli.md
20:  sob `if(UNIX AND Python3_FOUND)`.
37:os três alvos.
59:      `if(UNIX AND Python3_FOUND)` e isso está **medido como errado**: …
84:      Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped** — e o
```

As linhas 59 e 84 estão certas: a 59 é o critério que registra a correção, e a
84 é o enunciado original **marcado como tal** ("O enunciado original segue").
As linhas 20 e 37 não têm marca nenhuma.

E a medição de hoje, com os quatro listados pelo nome:

```text
$ ctest --test-dir <build> -R looks
1/4 Test #10: looks_selftest ...................   Passed
2/4 Test #11: looks_image ......................***Skipped
3/4 Test #12: looks_ui .........................***Skipped
4/4 Test #13: looks_live .......................***Skipped
100% tests passed out of 4

$ grep -n "^if(\|^endif\|add_test(NAME looks_\|add_test(NAME mcr_ui" tests/CMakeLists.txt
158:if(UNIX AND Python3_FOUND)
159:    add_test(NAME mcr_ui
165:endif()
191:if(Python3_FOUND)
201:    add_test(NAME looks_selftest
231:    add_test(NAME looks_image
253:    add_test(NAME looks_ui
278:    add_test(NAME looks_live
287:endif()
```

Os quatro de `looks` estão no `if(Python3_FOUND)` da linha 191; o único de
display sob `if(UNIX AND Python3_FOUND)` é o `mcr_ui`, do outro projeto.

## Causa raiz

A reconciliação percorreu os documentos que outros leem e deixou de fora o
cabeçalho da própria task.

## Correção

### Arquivo: `docs/tasks/looks/19-alvos-de-ctest-e-cli.md`

No **Objetivo**, "os quatro alvos". No **Contexto**, manter a convenção do
repositório e dizer, na mesma linha, que **neste ciclo** o de display não é
`if(UNIX …)`, apontando o critério que mediu — a forma do resto da reconciliação
("dizia X até 2026-09-17").

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` | modificar |

## Verificação

- [x] nenhuma linha sem marca de "enunciado original" diz três alvos ou
      `if(UNIX …)` como regra deste ciclo
- [x] `python tools/check_tasks.py` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `54dba19`: as linhas 20 (`if(UNIX AND Python3_FOUND)`
como convenção) e 37 ("os três alvos") da LOOKS-TASK-19 sem marca nenhuma.

- **Objetivo:** "os quatro alvos", com a nota de que dizia "três" até
  2026-09-17, contra o título.
- **Contexto:** a convenção do repositório fica — o `mcr_ui` está mesmo sob
  `if(UNIX AND Python3_FOUND)` —, e a mesma linha diz que **neste ciclo não**:
  os quatro de `looks` estão no `if(Python3_FOUND)`, porque sob `if(UNIX …)` o
  `looks_ui` sumiria da máquina Windows e `ctest -R looks_ui` sairia zero,
  apontando o critério do `looks_ui`, que é onde isso foi medido.

### Gates

```text
$ grep -n "três alvos\|UNIX AND Python3_FOUND" docs/tasks/looks/19-alvos-de-ctest-e-cli.md
20:  sob `if(UNIX AND Python3_FOUND)` — **no repositório**, onde o `mcr_ui` está
65:      `if(UNIX AND Python3_FOUND)` e isso está **medido como errado**: a janela
```

Nenhuma linha diz "três alvos". A 20 nomeia a convenção como do repositório e
nega-a para o ciclo na mesma frase; a 65 é o critério que registra a medição.

```text
$ python tools/check_tasks.py
check_tasks: 123 task(s), ok
```

`roms/` intocada (só documentação).

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `docs/tasks/looks/19-alvos-de-ctest-e-cli.md` — Contexto e Objetivo
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
