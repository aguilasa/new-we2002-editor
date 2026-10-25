---
id: CORR-DMCP-033
---

# CORR-DMCP-033 — Refechar a Fase 6 depois que a CORR-DMCP-031 for consertada

Origin: [DMCP-TASK-24](/docs/tasks/duckmcp/24-fechamento-fase-6.md)

## Problem

O critério 1 do fechamento pede que nenhuma CORR aberta a partir das tasks da Fase 6 continue aberta.
Na HEAD a [CORR-DMCP-031](/docs/tasks/duckmcp/CORR-DMCP-031.md) (origem DMCP-TASK-22, medium, pendente)
está aberta, então a Fase 6 não está fechada como a task afirma. A CORR foi aberta em `fd69c6b4`, depois
do commit de fechamento `b5505823` — por isso o status do Log (0 correções abertas) era verdade na hora.
O defeito em si é anterior ao ciclo: o `attempt(name, OracleError, lambda: ...)` que não afirma nada em
`tools/looks/oracle.py:9675` vem do `d58ce274`, e estava na árvore que a DMCP-TASK-24 deu por revisada;
ele faz o check de fase "looks_selftest verde" se apoiar num check que não afirma nada.

## Evidência

```text
$ grep -n 'CORR-DMCP-031' -A10 docs/tasks/duckmcp/fixes.json
"origin": "DMCP-TASK-22", "severity": "medium", "status": "pending"
$ sh "$RITE_HOME/bin/rite" status --cycle duckmcp
open fixes: critical 0, high 0, medium 1, low 1
next fix: CORR-DMCP-031
$ git log --oneline b5505823..HEAD
887b096c chore(rite): open CORR-DMCP-032
fd69c6b4 chore(rite): open CORR-DMCP-031
$ sed -n 9675,9677p tools/looks/oracle.py
attempt("two sections pointed at by one matrix load are refused",
        OracleError,
        lambda: _drawn_section(...
```

## Root cause

O fechamento confiou no `looks_selftest` verde e no estado limpo da revisão da DMCP-TASK-22. Um check
com os argumentos do `attempt()` em ordem errada continuava na árvore e só apareceu numa revisão
posterior (hipótese sobre por que escapou: o fechamento não plantou defeito contra os checks do
selftest em que se apoiou).

## Fix

Consertar a CORR-DMCP-031 pelo fluxo do ciclo (`tools/looks/oracle.py`, sem CORR nova). Depois, refazer
o critério 1 desta task e o gate `looks_selftest` na HEAD nova e acrescentá-los ao Log da
`docs/tasks/duckmcp/24-fechamento-fase-6.md`.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py` (pela CORR-DMCP-031)
- `docs/tasks/duckmcp/24-fechamento-fase-6.md`

## Verificação

`sh "$RITE_HOME/bin/rite" status --cycle duckmcp --json` não pode mostrar fix aberto com origem
DMCP-TASK-22 ou DMCP-TASK-23 (hoje lista a CORR-DMCP-031), e o Log da 24 traz o critério 1 e o
`looks_selftest` refeitos depois do conserto.

## Log de Execução
