---
id: CORR-KITS-080
---

# CORR-KITS-080 — Tirar da §4.3 o 'espera um save state' da task 46

Origin: [KITS-TASK-46](/docs/tasks/concluidos/kits/46-manga-curta-partida.md)

## Problem

O parágrafo final da §4.3 ainda descreve a KITS-TASK-46 como pendente, e descreve a figura de partida só com "a 93 no lugar da 97", embora a mesma seção agora tenha a regra de manga curta.

## Evidência

```text
$ sed -n '702,710p' docs/PLAN-KITS-PY.md
  desenhar a figura de partida: as seções do `MODEL.BIN` na ordem medida, com a
  93 no lugar da 97, ...
  [KITS-TASK-46](/docs/tasks/kits/46-manga-curta-partida.md) mede a manga curta,
  que espera um save state dele, e
$ grep -n 'que espera um save state dele' docs/PLAN-KITS-PY.md
708:que espera um save state dele, e
```

## Root cause

Ao fechar o veredito, a varredura atualizou o item da KITS-TASK-43 e o parágrafo da KITS-TASK-44, mas pulou o parágrafo "O que isso pede da aba 3D".

## Fix

No parágrafo "O que isso pede da aba 3D" da §4.3 de `docs/PLAN-KITS-PY.md`, dizer que a 46 mediu a manga curta e acrescentar a 90 no lugar da 4.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

`grep -n 'que espera um save state dele' docs/PLAN-KITS-PY.md` casa a linha 708 hoje; nada depois.

## Log de Execução

Reproduzido em 2026-10-06 sobre `ff9c8e4`: `grep -n 'que espera um save state dele'
docs/PLAN-KITS-PY.md` casa a linha 718 (a 708 da Evidência, deslocada por edições anteriores da
§4.3).

Conserto: o parágrafo "O que isso pede da aba 3D" diz que a KITS-TASK-46 mediu a manga curta no
slot 6, e a figura de partida passa a ter as duas trocas, a 93 no lugar da 97 (manga longa) e a
90 no lugar da 4 (manga curta).

```text
$ grep -n 'que espera um save state dele' docs/PLAN-KITS-PY.md
(sem saída)
```
- **Closed** — commit `8c0af61` (2026-10-06): docs(kits): section 4.3 no longer says task 46 waits for a save state
  - Files (`git show --name-status 8c0af61`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-080.md`
