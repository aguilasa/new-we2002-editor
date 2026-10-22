---
id: CORR-K2D-001
---

# CORR-K2D-001 — Isentar só kit2d/core/layout.py e selftest.py da regra de endereço, não qualquer arquivo homônimo

Origin: [K2D-TASK-01](/docs/tasks/kit2d/01-esqueleto.md)

## Problem

`address_breaks()` em `tools/kit2d/selftest.py` isenta um arquivo pelo **nome base** (`os.path.basename(path) in (LAYOUT_FILE, SELF_FILE)`). Qualquer `layout.py` ou `selftest.py` em qualquer ponto de `tools/kit2d/` fica fora da regra "só o `layout.py` soletra os endereços da §1.1" — por exemplo um futuro `tools/kit2d/ui/layout.py`, nome plausível para helper de layout Qt. O mesmo literal num arquivo de outro nome é pego, e isso é o controle.

## Evidência

Rode da raiz do repositório (o `git archive` mede a HEAD numa cópia):

```text
$ S=$(mktemp -d); git archive HEAD tools src | tar -x -C $S; mkdir -p $S/tools/kit2d/ui; echo 'X = 172096' > $S/tools/kit2d/ui/layout.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
kit2d_selftest: 12 check(s) ran, 0 failure(s)
exit=0
$ mv $S/tools/kit2d/ui/layout.py $S/tools/kit2d/ui/w.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
FAIL  no address of section 1.1 is spelled outside layout.py  [('ui/w.py', 1, '172096')]
exit=1
```

## Root cause

A isenção compara nome base em vez do caminho resolvido de `tools/kit2d/core/layout.py` e `tools/kit2d/selftest.py`.

## Fix

Em `address_breaks()`, comparar `os.path.abspath(path)` contra os dois arquivos exatos (`layout.__file__`, `__file__`). Somar um controle em `PLANTS` com o literal num arquivo chamado `ui/layout.py`, que tem de derrubar a regra.

## Arquivos a criar ou modificar

- `tools/kit2d/selftest.py`

## Verificação

O primeiro comando da Evidência passa a sair `exit=1`, listando `('ui/layout.py', 1, '172096')`; `python3 tools/kit2d/selftest.py` continua verde na árvore real.

## Log de Execução

- 2026-10-22 — reproduzido na HEAD `88f9e194` (`rite reproduce`): `kit2d_selftest: 12 check(s) ran, 0 failure(s)` / `exit=0` com o literal em `ui/layout.py`.
- Correção: `EXEMPT_FILES` guarda `os.path.abspath(layout.__file__)` e `os.path.abspath(__file__)`, e `address_breaks()` compara o caminho absoluto. Controle novo em `PLANTS`: `ui/layout.py` com `OFFSET = 172096` (o laço de plantio cria o subdiretório).

## Verificação feita

```text
$ S=$(mktemp -d); git ls-files tools src | tar -c -T - | tar -x -C $S; mkdir -p $S/tools/kit2d/ui; echo 'X = 172096' > $S/tools/kit2d/ui/layout.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
  FAIL  no address of section 1.1 is spelled outside layout.py  [('ui/layout.py', 1, '172096')]
kit2d_selftest: 13 check(s) ran, 1 failure(s)
exit=1
$ python3 tools/kit2d/selftest.py --quiet; echo exit=$?
kit2d_selftest: 13 check(s) ran, 0 failure(s)
exit=0
```

Controle do controle — a isenção antiga por nome base, devolvida numa cópia, derruba o plantio novo:

```text
$ sed -i 's/if os.path.abspath(path) in EXEMPT_FILES:/if os.path.basename(path) in ("layout.py", "selftest.py"):/' $S/tools/kit2d/selftest.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
  FAIL  planted an address literal in a file merely named layout.py turns its rule red
kit2d_selftest: 13 check(s) ran, 1 failure(s)
exit=1
```

Gates: `kit2d_selftest` e `ctest -R kit2d_selftest` verdes; o terceiro (`tools/kit2d/controls.py`) sai 2, esperado até a K2D-TASK-16, como a K2D-TASK-01 registra.
