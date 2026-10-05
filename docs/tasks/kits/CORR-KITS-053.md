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

### 2026-10-04

Reproduzido na HEAD `e6c5882`: `python3 tools/kits/gen_tables.py --negative-kits` dá `error: unrecognized arguments: --negative-kits`, e o `--negative` só planta em `TEAM_NAMES`.

Conserto: `--negative-kits` em `tools/kits/gen_tables.py`.

- (a) acrescenta `(2, "05", "planted")` às `EMULATOR_ROWS` e exige o `GenError` com `team 2 TEX_02`;
- (b) troca uma vez `'41'` por `'14'` no `TEAM_KIT` de uma cópia do `team_kits.py` e exige que o `--check` saia 1 sobre ela (o `check` ganhou `outputs=` para isso).

Nomeado na linha do `team_kits.py` em "artefatos gerados" do perfil, e a saída colada no Log da KITS-TASK-30 no lugar dos vermelhos remendados à mão.

```
$ python3 tools/kits/gen_tables.py --negative-kits
control: EMULATOR_ROWS + (2, '05', 'planted') -- the rule gives team 2 TEX_02, and the game wore TEX_05 (planted)
control: a row the rule contradicts -- red, held
control: '41' -> '14' once in TEAM_KIT of a copy of tools/kits/core/generated/team_kits.py
gen_tables: ../../../../../tmp/kits-gen-7onb1rgs/team_kits.py is stale -- rerun python tools/kits/gen_tables.py
  --- committed
  +++ regenerated
  @@ -15,3 +15,3 @@
       '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31',
  -    '32', '33', '34', '35', '36', '37', '38', '39', '40', '14', '42', '43', '44', '45', '46', '47',
  +    '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47',
       '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63',
control: --check <copy> exit 1 -- red, held
(exit 0)
```

Controle do controle: numa cópia da árvore com a guarda de `render_kits` desligada (`if tags[index] != tag:` → `if False:`), o `--negative-kits` reprova:

```
control: a row the rule contradicts -- FAILED
control: --check <copy> exit 1 -- red, held
rc=1
```

```
$ python3 tools/kits/gen_tables.py --check
gen_tables: tools/kits/core/generated/team_names.py is up to date
gen_tables: tools/kits/core/generated/team_kits.py is up to date
$ ctest --test-dir build -R kits_gen
100% tests passed, 0 tests failed out of 1
```
- **Closed** — commit `9e1a6d8` (2026-10-04): test(kits): gen_tables --negative-kits plants both team_kits.py guards
  - Files (`git show --name-status 9e1a6d8`):
    - `M docs/prompts/perfil-kits.md`
    - `M docs/tasks/kits/30-tabela-time-tag.md`
    - `M docs/tasks/kits/CORR-KITS-053.md`
    - `M tools/kits/gen_tables.py`
