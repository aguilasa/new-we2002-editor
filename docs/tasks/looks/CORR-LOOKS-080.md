---
id: CORR-LOOKS-080
title: "Marcar as entregas da Fase 10 das tasks 36, 37 e 38 no progresso"
origin: LOOKS-TASK-38
severity: low
files: [docs/tasks/looks/progresso.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-080 — Marcar as entregas da Fase 10 das tasks 36, 37 e 38 no progresso

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

A lista de entregas da Fase 10 no `progresso.md` do ciclo ainda mostra
`- [ ] Os valores alinhados como no jogo (LOOKS-TASK-38)` com a task em `done`.
O mesmo vale para a 36 e a 37; a 30 e a 31, também `done`, estão marcadas — a
convenção é por task, e três caixas estão atrasadas.

## Evidência

```text
$ sed -n '299,301p' docs/tasks/looks/progresso.md
- [ ] Os sprites estáticos e as setas desenhados do disco ([LOOKS-TASK-36]…).
- [ ] O texto desenhado com os glifos do `EDT_2D.BIN` ([LOOKS-TASK-37]…).
- [ ] Os valores alinhados como no jogo ([LOOKS-TASK-38]…).

$ grep -n "LOOKS-TASK-3[678]" docs/tasks/looks/progresso.md | grep done
| LOOKS-TASK-36 … | done | 2026-09-21 | 2026-09-21 |
| LOOKS-TASK-37 … | done | 2026-09-22 | 2026-09-22 |
| LOOKS-TASK-38 … | done | 2026-09-22 | pending |
```

## Causa raiz

A lista é prosa mantida à mão, **fora** da região gerada pelo Rite, então o
`rite check` não a enxerga. A omissão começou na LOOKS-TASK-36 e cada task
desde então a repetiu.

## Correção

Marcar as três linhas (36, 37, 38) na lista da Fase 10, cada uma com a linha de
resultado que as entradas já marcadas carregam. Como é fora da região
`<!-- rite:begin -->`, a edição à mão é o caminho certo aqui.

## Arquivos

- docs/tasks/looks/progresso.md (linhas 299-301)

## Verificação

Nenhum `- [ ]` sobra na lista da Fase 10 para uma task que a tabela gerada
reporta como `done`.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
$ sed -n '299,301p' docs/tasks/looks/progresso.md
- [ ] Os sprites estáticos e as setas desenhados do disco ([LOOKS-TASK-36]...).
- [ ] O texto desenhado com os glifos do `EDT_2D.BIN` ([LOOKS-TASK-37]...).
- [ ] Os valores alinhados como no jogo ([LOOKS-TASK-38]...).
# a tabela gerada dá as três como done (a 38 já com reviewed_on 2026-09-22)
$ grep -n "rite:begin\|rite:end" docs/tasks/looks/progresso.md
48:<!-- rite:begin tasks -->
91:<!-- rite:end -->      # as caixas estão nas linhas 297-303, FORA da região gerada
```

As duas entradas já marcadas (tasks 30 e 31) trazem uma frase de resultado
medido depois do título; marcar as três novas pede a mesma frase, não só a
caixa.
