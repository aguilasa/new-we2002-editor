---
id: CORR-K3D-019
---

# CORR-K3D-019 — PLAN-KITS-PY ainda diz braçadeira do goleiro desligada e quatro plantas

Origin: [K3D-TASK-11](/docs/tasks/kits-3d/11-caixas-livres.md)

## Problem

A [K3D-TASK-11](/docs/tasks/kits-3d/11-caixas-livres.md) reabriu a decisão em `docs/PLAN-KITS-PY.md`, mas deixou como estavam duas frases
mais antigas do mesmo parágrafo:

- a linha 393 ainda diz, no presente, que os vestires não medidos ficam desligados,
  nomeando "a braçadeira no goleiro" — que agora está ligada e habilitada no goleiro;
- as linhas 402-403 ainda dizem que o `kits_ui` tem "quatro plantas: cada checkbox
  ignorado e o de manga sempre visível". A task removeu a planta "Long sleeves always
  shown" e hoje são seis plantas de vestir.

Fere a regra "fechar um veredito é varrer quem dizia o anterior".

## Evidência

```text
$ grep -n 'quatro plantas\|manga sempre visível\|a braçadeira no goleiro e o número' docs/PLAN-KITS-PY.md
393:  do próprio checkbox: a braçadeira no goleiro e o número na figura de
402:  checkboxes por figura e língua, e quatro plantas: cada checkbox ignorado e o
403:  de manga sempre visível.
$ grep -c 'Long sleeves always shown' tools/kits/ui_check.py
0
```

## Root cause

A edição pôs uma frase "Reaberto em 2026-10-09" no meio do parágrafo sem reescrever as
frases de antes e de depois.

## Fix

No item "Os três checkboxes da aba 3D" de `docs/PLAN-KITS-PY.md` (perto das linhas
385-403): passar o estado desligado da "braçadeira no goleiro" para o passado, como
histórico, e trocar "quatro plantas … manga sempre visível" por um apontamento ao
comando que imprime as plantas (`ui_check.py` / `kits_ui`), sem contagem escrita à mão.

## Arquivos a criar ou modificar

- docs/PLAN-KITS-PY.md

## Verificação

```sh
grep -c 'quatro plantas\|manga sempre visível' docs/PLAN-KITS-PY.md
```

Hoje dá 2; depois, 0.

## Log de Execução

- 2026-10-09 — triagem inline: **REPRODUCED**. Linhas 393 e 402-403 do plano; a planta "Long
  sleeves always shown" não existe mais no `ui_check.py`.
- §3.4 do `PLAN-KITS-PY.md`: o desligado da braçadeira no goleiro foi para o passado ("até a
  K3D-TASK-11"), e "quatro plantas … manga sempre visível" virou o apontamento às linhas `plant '…'`
  que o `ui_check.py` imprime, sem contagem à mão.
- Verificação: `grep -c 'quatro plantas\|manga sempre visível' docs/PLAN-KITS-PY.md` dá 0.
- **Closed** — commit `2b711d6` (2026-10-09): docs(kits): sweep the plan's checkbox paragraph after K3D-TASK-11
  - Files (`git show --name-status 2b711d6`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits-3d/CORR-K3D-019.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
