---
id: CORR-LOOKS-093
title: "Recolar a transcrição dos gates: ela é anterior a 150 linhas do código entregue"
origin: LOOKS-TASK-32
severity: low
files: [docs/tasks/looks/32-o-ciclo-da-caminhada.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-25
done_commit: ad75e7e1
---

# CORR-LOOKS-093 — Recolar a transcrição dos gates: ela é anterior a 150 linhas do código entregue

Origin: [LOOKS-TASK-32](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)

## Problema identificado

A seção de Gates da task diz "Todos verdes sobre esta árvore; depois deles só
mudou prosa" e cita `rule 1 swept 27 file(s), 32405 line(s)`. A árvore entregue
pelo `6a2c16fb` varre **32.555** linhas — 150 a mais. Como o único commit
depois do de trabalho é o fechamento, que só mexe em documento (`42c23a32`),
essas 150 linhas de Python entraram **dentro do próprio commit da task**,
depois da corrida citada: a transcrição é de um estado intermediário, e a frase
que afirma o contrário ficou no lugar.

Os gates em si estão bem — o revisor re-rodou os quatro e estão verdes na
árvore entregue.

## Evidência

Medido na HEAD `a3e6809b`, antes da correção (saídas do `rite-reproducer`,
registradas no Log abaixo):

```text
$ grep -n "rule 1 swept" docs/tasks/looks/32-o-ciclo-da-caminhada.md
258:   ..... rule 1 swept 27 file(s), 32405 line(s)
$ python tools/looks/selftest.py --quiet | grep "rule 1 swept"
  ..... rule 1 swept 27 file(s), 32555 line(s)
```

O laço sobre revisões fixas de git que ficava aqui foi trocado por estes dois comandos: ele documentava o sintoma e não
podia verificar a correção, porque revisão de git não muda.

## Causa raiz

O bloco de Gates foi colado de uma corrida feita no meio da task e não foi
refeito depois das últimas edições de código.

## Correção

Recolar as quatro transcrições de uma corrida sobre a árvore entregue
(`32555`), ou tirar as contagens de linha da citação e manter a afirmação. A
guarda reaproveitável é **rodar os gates por último e colar por último**.

## Arquivos

- docs/tasks/looks/32-o-ciclo-da-caminhada.md (seção Gates, linhas ~252-276)

## Verificação

`python tools/looks/selftest.py --quiet | grep "rule 1 swept"` imprime a mesma
linha que a task cita. Hoje imprime 32555 contra os 32405 citados.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

As saídas das revisões são as registradas (e sempre serão: revisão de git não muda). O sintoma em si está em `32-o-ciclo-da-caminhada.md:258`, que ainda cita `32405 line(s)` — conferido com `grep -n 32405`. O `tail -3` do selftest hoje termina em `controls: 0 failure(s)` em vez da linha `rule 1 swept`, o que muda a forma da saída, não o veredito.

```text
$ python tools/looks/selftest.py --quiet | tail -3
  ..... 108 of 108 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)
$ for rev in 42c23a32 6a2c16fb 7717326c; do git ls-tree -r --name-only $rev tools/looks \
42c23a32 32555
6a2c16fb 32555
7717326c 31517
```

### 2026-09-25 — triagem por agente (`/rite:fix-all looks CORR-LOOKS-091 CORR-LOOKS-093`, Rite 0.9.3)

Resíduo da triagem inline: as saídas da Evidência batem com as registradas, mas nenhum comando lê a task 32, onde mora o sintoma. Um `rite-reproducer` mediu na HEAD `a3e6809b`: **REPRODUCED**.

```text
$ grep -n -E "rule 1 swept|32405|32555|só\s*mudou" docs/tasks/looks/32-o-ciclo-da-caminhada.md
254: Todos verdes sobre esta árvore; depois deles só mudou prosa.
258:   ..... rule 1 swept 27 file(s), 32405 line(s)
$ python tools/looks/selftest.py --quiet | grep "rule 1 swept"
  ..... rule 1 swept 27 file(s), 32555 line(s)
```

### 2026-09-25 — correção (`/rite:fix-all looks`, Rite 0.9.3)

`git diff --stat 6a2c16fb HEAD -- tools/looks` sai vazio na HEAD `a3e6809b`: o
código sob os gates é o entregue. Na task 32, re-rodados e recolados os quatro
gates que não precisam de emulador nem de janela (`selftest.py --quiet`,
`cli.py check`, `anime.py --against-walk` com `WE2002_LOOKS_IMAGE` na imagem
japonesa, `check_tasks.py`), e a frase de abertura passou a dizer data e
árvore. O `oracle.py --walk` (emulador) e o `ui_check.py` (janela) ficaram com
a transcrição da corrida da task, marcada como tal. A Evidência daqui trocou o
laço sobre revisões fixas por dois comandos sobre a árvore de trabalho, com a
saída de antes da correção.

```text
$ grep -n "rule 1 swept" docs/tasks/looks/32-o-ciclo-da-caminhada.md
261:$ python tools/looks/selftest.py --quiet | grep -E "rule 1 swept|controls red|^looks_selftest"
262:  ..... rule 1 swept 27 file(s), 32555 line(s)
$ python tools/looks/selftest.py --quiet | grep "rule 1 swept"
  ..... rule 1 swept 27 file(s), 32555 line(s)
$ python tools/check_tasks.py | tail -1
check: 0 error(s), 13 warning(s) in 4 cycle(s)
```

O aviso "reads a fixed git revision" desta CORR sumiu do `check_tasks.py`.
- **Closed** — commit `ad75e7e1` (2026-09-25): docs(looks): re-paste LOOKS-TASK-32 gate transcripts over the delivered tree
  - Files (`git show --name-status ad75e7e1`):
    - `M docs/tasks/looks/32-o-ciclo-da-caminhada.md`
    - `M docs/tasks/looks/CORR-LOOKS-093.md`
