---
id: CORR-LOOKS-033
title: "Correção: a §6(c) do plano ainda se declara medida em parte, com a task pendente"
type: correção
category: processo
status: pendente
depends_on: []
---

# CORR-LOOKS-033: a fonte de verdade da LOOKS-TASK-14 diz que ela não fechou

## Problema identificado

O `fonte_de_verdade` da LOOKS-TASK-14 é `/docs/PLAN-LOOKS-PY.md` §6, e o
cabeçalho da §6(c) é:

```text
docs/PLAN-LOOKS-PY.md:1632
**(c) A tabela de montagem — MEDIDA EM PARTE, 2026-09-15**, pela
[`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md), que **continua
pendente**.
```

O corpo da seção, logo abaixo, traz a âncora do cabelo medida em **2026-09-16**,
a rotina do jogo, o mapa das treze seções e a tabela do cross-check contra o
corpus — isto é, a medição que fecha a task. O `progresso.md` a marca
`✅ Concluído` em 2026-09-16, e o frontmatter da task diz `status: concluído`.

Só o cabeçalho ficou para trás, e ele é a primeira linha que alguém lê ao abrir
a fonte de verdade. O perfil do ciclo é explícito: "o plano se corrige na seção
que muda, nunca num apêndice de erratas" — a seção mudou, o título dela não.

## Evidência

```text
$ grep -n "continua pendente\|MEDIDA EM PARTE" docs/PLAN-LOOKS-PY.md
1632:**(c) A tabela de montagem — MEDIDA EM PARTE, 2026-09-15**, pela

$ grep -n "LOOKS-TASK-14" docs/tasks/looks/progresso.md
50:| [LOOKS-TASK-14](…) | … | 4 | 12, 13 | ✅ Concluído | 2026-09-16 | …

$ sed -n '9p' docs/tasks/looks/14-tabela-de-montagem.md
status: concluído
```

E o corpo da mesma §6(c), nas linhas 1656 a 1706, já é a medição de 2026-09-16:
o `--patched`, o `--hair`, o `--writes`, os dezesseis pares e a tabela do corpus
com `rho = 0,80`.

## Causa raiz

A quarta passagem acrescentou a medição ao corpo da §6(c) e não tocou o
cabeçalho, que carregava o veredito parcial da primeira.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` (§6(c))

Reescrever o cabeçalho com o veredito de hoje: **medida em 2026-09-16, com
resíduo nomeado** — os três estilos que não escreveram nada, as três seções
pares nunca nomeadas, os quads de nove das treze cabeças e o mapa medido só no
jogador de linha —, dizendo para onde cada resíduo foi encaminhado (as tasks 15
e 17). A data de 2026-09-15 fica no corpo, onde descreve a primeira metade.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |

## Verificação

- [ ] nenhum "continua pendente" sobra no plano para uma task `✅ Concluído`
- [ ] `python tools/check_tasks.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
