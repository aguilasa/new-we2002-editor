---
id: CORR-KITS-057
---

# CORR-KITS-057 — Desinverter os sha256 das duas capturas no Log da task 31

Origin: [KITS-TASK-31](/docs/tasks/concluidos/kits/31-combobox-de-times.md)

## Problem

O Log da KITS-TASK-31 põe o sha256 `461f0cbede9cf201…` em `work/kits-combo-teams-top.png` e `9dbc0595bf0ff484…` em `work/kits-combo-teams-end.png`. Medido agora, é o contrário. A descrição do conteúdo de cada imagem está certa (topo: Ireland…Chile; fim: Clas. Brazil…`TEX_A3`); só os hashes estão trocados. Os PNGs moram em `work/`, fora do git, então o hash é a única coisa que liga o Log a eles.

## Evidência

```text
$ sha256sum work/kits-combo-teams-*.png
461f0cbede9cf201c110a7b31488be7843a6d5f2ea7b163985aa4ed26cea2188  work/kits-combo-teams-end.png
9dbc0595bf0ff484a2a458f57bf7553f129b65b2f230384e69c98ef61f4aa8f5  work/kits-combo-teams-top.png
$ grep -n '461f0cbede9cf201\|9dbc0595bf0ff484' docs/tasks/kits/31-combobox-de-times.md
58:sha256 `461f0cbede9cf201…`) e, com `End`, `work/kits-combo-teams-end.png`
60:default — TEX_A4" e `TEX_95` … `TEX_A3`; sha256 `9dbc0595bf0ff484…`). Fechado,
```

(o 461f… da linha 58 é o da captura do topo, citada antes dela)

## Root cause

Hipótese: os hashes foram transcritos à mão de uma corrida de `sha256sum`, que imprime em ordem alfabética (`end` antes de `top`), e casados com o arquivo errado.

## Fix

No parágrafo do critério 2 de `docs/tasks/kits/31-combobox-de-times.md`, trocar os dois hashes entre si, colando da saída de `sha256sum`.

## Arquivos a criar ou modificar

- `docs/tasks/kits/31-combobox-de-times.md`

## Verificação

```sh
grep -n 'sha256 `461f0cbede9cf201' docs/tasks/kits/31-combobox-de-times.md
```

Hoje casa a linha 58 (a captura do topo); depois do conserto casa só a frase da captura do fim, e `9dbc0595bf0ff484` passa para a do topo.

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `17125e3`:

```
$ sha256sum work/kits-combo-teams-*.png
461f0cbede9cf201c110a7b31488be7843a6d5f2ea7b163985aa4ed26cea2188  work/kits-combo-teams-end.png
9dbc0595bf0ff484a2a458f57bf7553f129b65b2f230384e69c98ef61f4aa8f5  work/kits-combo-teams-top.png
```

e o Log punha `461f0cbede9cf201…` na captura do topo. Olhada a `work/kits-combo-teams-top.png`: é a lista aberta de "Ireland — TEX_00" a "Chile — TEX_43", então o conteúdo descrito estava certo e só os hashes trocados.

Conserto: os dois hashes trocados entre si no parágrafo do critério 2.

```
$ grep -n 'sha256 `461f0cbede9cf201\|sha256 `9dbc0595bf0ff484' docs/tasks/kits/31-combobox-de-times.md
58:sha256 `9dbc0595bf0ff484…`) e, com `End`, `work/kits-combo-teams-end.png`
60:default — TEX_A4" e `TEX_95` … `TEX_A3`; sha256 `461f0cbede9cf201…`). Fechado,
```
- **Closed** — commit `20b9063` (2026-10-04): docs(kits): un-swap the two capture hashes in the KITS-TASK-31 log
  - Files (`git show --name-status 20b9063`):
    - `M docs/tasks/kits/31-combobox-de-times.md`
    - `M docs/tasks/kits/CORR-KITS-057.md`
