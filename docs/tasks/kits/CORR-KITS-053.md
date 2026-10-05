---
id: CORR-KITS-053
---

# CORR-KITS-053 — Controles negativos versionados para EMULATOR_ROWS e para team_kits.py desatualizado

Origin: [KITS-TASK-30](/docs/tasks/kits/30-tabela-time-tag.md)

## Problem

O `tools/kits/gen_tables.py` tem duas verificações que guardam o `team_kits.py`, e nenhuma tem vermelho versionado: a que recusa uma entrada de `EMULATOR_ROWS` que a regra contradiz, e o `--check` acusando `team_kits.py` desatualizado. Os vermelhos do Log da KITS-TASK-30 para as duas ("plantada (2, '05')" e "'41' trocado por '14'") saíram de cópias remendadas à mão. O `--negative` só mexe em `TEAM_NAMES`, e na própria corrida dele o `team_kits.py` continua "up to date". Ninguém consegue refazer o vermelho do Log, então nenhuma das duas conta como gate ainda.

## Evidência

```text
$ python3 tools/kits/gen_tables.py --negative
gen_tables: tools/kits/core/generated/team_names.py is stale -- ...
gen_tables: tools/kits/core/generated/team_kits.py is up to date
$ grep -n "negative" tools/kits/gen_tables.py
(só negative() para TEAM_NAMES e negative_editor() para o exe; nada planta em EMULATOR_ROWS nem em team_kits.py)
```

Refeito à mão a partir da HEAD (cópia por `git archive HEAD | tar -x -C <tmp>`):

```text
$ sed -i 's/^    (13, "13", /    (2, "05", "planted"), (13, "13", /' tools/kits/gen_tables.py; python3 tools/kits/gen_tables.py --check
gen_tables: the rule gives team 2 TEX_02, and the game wore TEX_05 (planted)   exit 1
$ (cópia nova) sed -i "s/'40', '41', '42'/'40', '14', '42'/" tools/kits/core/generated/team_kits.py; python3 tools/kits/gen_tables.py --check
gen_tables: tools/kits/core/generated/team_kits.py is stale -- ...   exit 1
```

## Root cause

Hipótese: quando o `team_kits.py` entrou, o conjunto de controles negativos não foi estendido para cobri-lo.

## Fix

Em `tools/kits/gen_tables.py`, um controle `--negative-kits` (ou estender o `--negative`) que planta (a) uma linha contraditória numa cópia de `EMULATOR_ROWS` e exige o `GenError`, e (b) uma tag trocada numa cópia de `team_kits.py` e exige que o `--check` falhe. Nomear o controle novo na linha de artefatos gerados do `docs/prompts/perfil-kits.md` e colar a saída dele no Log da task 30.

## Arquivos a criar ou modificar

- `tools/kits/gen_tables.py`
- `docs/prompts/perfil-kits.md`
- `docs/tasks/kits/30-tabela-time-tag.md`

## Verificação

`python3 tools/kits/gen_tables.py --negative-kits` falha hoje com `unrecognized arguments`; depois do conserto sai 0 com os dois vermelhos segurados.

## Log de Execução
