---
id: CORR-KITS-054
---

# CORR-KITS-054 — Resolver EDITOR_EXE a partir de REPO_DIR, não do diretório de trabalho

Origin: [KITS-TASK-30](/docs/tasks/kits/30-tabela-time-tag.md)

## Problem

Todo caminho do `tools/kits/gen_tables.py` se ancora em `REPO_DIR`, menos `EDITOR_EXE = os.path.join("we-team-editor", "we-team-editor.exe")` (linha 64), que depende do diretório de trabalho. Rodado de fora da raiz do repositório, `--editor` e `--negative-editor` dizem que o exe falta e saem 77 (pulo), embora ele esteja no disco — pulo silencioso da única verificação que relê a regra do editor.

## Evidência

```text
$ cd /tmp && python3 /home/ingmar/desenvolvimento/github/new-we2002-editor/tools/kits/gen_tables.py --editor; echo rc=$?
gen_tables --editor: skipped -- no exe at we-team-editor/we-team-editor.exe (it is not in git)
rc=77
$ ls -la /home/ingmar/desenvolvimento/github/new-we2002-editor/we-team-editor/we-team-editor.exe
-rw-r--r-- 1 ingmar ingmar 1151488 mai 27 2006 .../we-team-editor.exe
```

## Root cause

`EDITOR_EXE` não é juntado a `REPO_DIR`.

## Fix

Em `tools/kits/gen_tables.py`, `EDITOR_EXE = os.path.join(REPO_DIR, "we-team-editor", "we-team-editor.exe")`.

## Arquivos a criar ou modificar

- `tools/kits/gen_tables.py`

## Verificação

`cd /tmp && python3 /home/ingmar/desenvolvimento/github/new-we2002-editor/tools/kits/gen_tables.py --editor` sai 77 hoje; depois do conserto sai 0 com "the exe computes EDITOR_RULE".

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `a1b1dca`:

```
$ cd /tmp && python3 /home/ingmar/desenvolvimento/github/new-we2002-editor/tools/kits/gen_tables.py --editor; echo rc=$?
gen_tables --editor: skipped -- no exe at we-team-editor/we-team-editor.exe (it is not in git)
rc=77
```

Conserto: `EDITOR_EXE = os.path.join(REPO_DIR, "we-team-editor", "we-team-editor.exe")`, como os outros caminhos do gerador.

```
$ cd /tmp && python3 /home/ingmar/desenvolvimento/github/new-we2002-editor/tools/kits/gen_tables.py --editor; echo rc=$?
gen_tables --editor: 2 site(s) at 0xd451, 0xe5db give {'divisor': 95, 'skip': 9, 'base': 19756824, 'stride': 47040}
gen_tables --editor: the exe computes EDITOR_RULE
rc=0
$ cd /tmp && python3 /home/ingmar/desenvolvimento/github/new-we2002-editor/tools/kits/gen_tables.py --negative-editor | tail -1
control: --editor <copy> exit 1 -- red, held
$ python3 tools/kits/gen_tables.py --check
gen_tables: tools/kits/core/generated/team_names.py is up to date
gen_tables: tools/kits/core/generated/team_kits.py is up to date
```
- **Closed** — commit `2d123c5` (2026-10-04): fix(kits): gen_tables resolves the editor exe from the repository root
  - Files (`git show --name-status 2d123c5`):
    - `M docs/tasks/kits/CORR-KITS-054.md`
    - `M tools/kits/gen_tables.py`
