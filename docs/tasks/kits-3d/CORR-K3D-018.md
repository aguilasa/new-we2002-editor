---
id: CORR-K3D-018
---

# CORR-K3D-018 — Corpo da K3D-TASK-11 não declara oracle.py, selftest.py e PLAN-KITS-PY.md

Origin: [K3D-TASK-11](/docs/tasks/kits-3d/11-caixas-livres.md)

## Problem

O commit de trabalho `1549f06` da [K3D-TASK-11](/docs/tasks/kits-3d/11-caixas-livres.md) modifica `tools/kits/oracle.py`,
`tools/kits/selftest.py` e `docs/PLAN-KITS-PY.md`. O `files` só ganhou os três no commit
de fechamento `c70d127`, depois do trabalho, e a seção "Arquivos a criar ou modificar" da
task continua listando só os sete arquivos originais. Fere a armadilha "Edição fora do
`files` declarado": os arquivos entram com `rite set --files` mais uma linha na seção, no
mesmo commit.

## Evidência

```text
$ git show c70d127 -- docs/tasks/kits-3d/progress.json | grep '"files"'
-      "files": [..., "tools/kits/controls.py", "docs/KITS-AJUSTES-3D.md"],
+      "files": [..., "docs/KITS-AJUSTES-3D.md", "tools/kits/oracle.py", "tools/kits/selftest.py", "docs/PLAN-KITS-PY.md"],
$ sed -n '/## Arquivos/,/## Done/p' docs/tasks/kits-3d/11-caixas-livres.md | grep -c 'oracle.py\|selftest.py\|PLAN-KITS-PY.md'
0
```

## Root cause

Hipótese: os arquivos extras entraram no fechamento para satisfazer a conferência de
escopo, e a seção do corpo não foi atualizada.

## Fix

Acrescentar os três caminhos, cada um com uma linha de motivo, em "In:" de
`docs/tasks/kits-3d/11-caixas-livres.md` (o `files` já está certo).

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/11-caixas-livres.md

## Verificação

```sh
sed -n '/## Arquivos/,/## Done/p' docs/tasks/kits-3d/11-caixas-livres.md | grep -c 'oracle.py\|selftest.py\|PLAN-KITS-PY.md'
```

Hoje dá 0; depois, 3.

## Log de Execução

- 2026-10-09 — triagem inline: **REPRODUCED**. O `files` ganhou os três só em `c70d127`; a seção
  "Arquivos" contava 0.
- "In:" da K3D-TASK-11 com `oracle.py`, `selftest.py` e `PLAN-KITS-PY.md`, cada um com o motivo
  tirado do diff de `1549f06`, e uma linha dizendo que entraram no `files` no fechamento.
- Verificação: o `sed … | grep -c` dá 3.
- **Closed** — commit `bf76def` (2026-10-09): docs(kits): declare oracle.py, selftest.py and the plan in K3D-TASK-11
  - Files (`git show --name-status bf76def`):
    - `M docs/tasks/kits-3d/11-caixas-livres.md`
    - `M docs/tasks/kits-3d/CORR-K3D-018.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
