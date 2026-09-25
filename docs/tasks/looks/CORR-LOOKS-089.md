---
id: CORR-LOOKS-089
title: Marcar a linha da Fase 10 da LOOKS-TASK-40 no progresso
origin: LOOKS-TASK-40
severity: medium
files: [docs/tasks/looks/progresso.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-089 — Marcar a linha da Fase 10 da LOOKS-TASK-40 no progresso

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

O `docs/tasks/looks/progresso.md` tem uma lista da "Fase 10" mantida à mão,
**fora** da região gerada pelo Rite (linhas 48-91). A linha desta task continua
`- [ ]`, então o mesmo arquivo diz `done` na tabela gerada (linha 86) e
não-feito na prosa (linha 303) — e, ao contrário das linhas das tasks 30, 31,
36, 37 e 38, ela não carrega o resumo do que se mediu. A
[LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md), também `done`, tem a
mesma linha atrasada.

É o mesmo defeito da [CORR-LOOKS-080](/docs/tasks/looks/CORR-LOOKS-080.md),
reaparecendo na task seguinte.

## Evidência

```text
$ grep -n "rite:begin\|rite:end" docs/tasks/looks/progresso.md
48:<!-- rite:begin tasks -->
91:<!-- rite:end -->

$ sed -n '86p;302,303p' docs/tasks/looks/progresso.md
| [LOOKS-TASK-40](...) | A câmera do close-up ... | 10 | implementação | LOOKS-TASK-28 | done | 2026-09-23 | pending |
- [ ] A origem do texto da ajuda medida, e desenhada se for do disco ([LOOKS-TASK-39](...)).
- [ ] A câmera do close-up por linha de cabeça ([LOOKS-TASK-40](...)).
```

## Causa raiz

A lista é prosa, não é gerada: o `rite close` não a toca e o `rite check` não a
enxerga. O hábito de atualizá-la é seguido de forma desigual — as tasks 37 e 38
só foram marcadas depois, de passagem, no `de5403a6 chore(rite): close
CORR-LOOKS-077`.

## Correção

Marcar a linha à mão — é fora da região gerada, então editar ali é o caminho
certo — com o resumo de uma linha que as outras da Fase 10 carregam: seis
linhas aproximam, o `BOOTS` entre elas, e a janela troca por linha a partir dos
arquivos medidos. A linha da LOOKS-TASK-39 é da revisão dela.

## Arquivos

- docs/tasks/looks/progresso.md

## Verificação

`grep -n "LOOKS-TASK-40" docs/tasks/looks/progresso.md` não mostra linha
`- [ ]` para a task, e `python tools/check_tasks.py` segue em `0 error(s)`.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

A linha 303 continua `- [ ]`: o sintoma. A coluna de revisão da linha 86 mudou de `pending` para `2026-09-23` desde a Evidência, o que é a revisão da task, não este defeito.

```text
$ grep -n "rite:begin\|rite:end" docs/tasks/looks/progresso.md
48:<!-- rite:begin tasks -->
91:<!-- rite:end -->
$ sed -n '86p;302,303p' docs/tasks/looks/progresso.md
| [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md) | A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça | 10 | implementação | LOOKS-TASK-28 | done | 2026-09-23 | 2026-09-23 |
- [ ] A origem do texto da ajuda medida, e desenhada se for do disco ([LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)).
- [ ] A câmera do close-up por linha de cabeça ([LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)).
```
