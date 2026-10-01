---
id: CORR-KITS-020
---

# CORR-KITS-020 — Fail kits_image when WE2002_LOOKS_IMAGE points at no file

Origin: [KITS-TASK-08](/docs/tasks/kits/08-selftest-e-ctest.md)

## Problem

Se `WE2002_LOOKS_IMAGE` está definida mas aponta para um arquivo que não existe (um erro de digitação), o `kits_image` se reporta *Skipped* em vez de falhar. O gate do disco fica cinza em silêncio numa corrida que pediu por ele.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=C:/nope/typo.bin ctest -R kits_image
1/1 Test #15: kits_image .......................***Skipped   0.12 sec
$ WE2002_LOOKS_IMAGE=C:/nope/typo.bin python tools/kits/selftest.py --image; echo $?
77
```

`selftest.py:357-360` devolve SKIP quando `not os.path.isfile(image_path)`.

## Root cause

O `run_image` trata "definida mas errada" igual a "não definida".

## Fix

No `run_image` de `tools/kits/selftest.py`, devolver 1 com uma linha FAIL quando a variável está definida e o caminho não é arquivo. O 77 fica só para o caso de variável não definida.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`

## Verificação

```text
$ WE2002_LOOKS_IMAGE=C:/nope/typo.bin python tools/kits/selftest.py --image; echo $?
```

Hoje imprime 77; depois tem de imprimir 1.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `201c7915`)

```text
$ WE2002_LOOKS_IMAGE=C:/nope/typo.bin python tools/kits/selftest.py --image; echo $?
kits_image: skipped -- WE2002_LOOKS_IMAGE points at C:/nope/typo.bin, which is not a file
77
```

REPRODUCED (o `ctest` da Evidência não achou teste porque o `--scratch` rodou fora de um build).

### O que foi feito

`tools/kits/selftest.py`, `run_image`: variável definida e caminho que não é arquivo agora imprime uma linha `FAIL` e sai 1. O 77 ficou só para a variável não definida; o `tests/CMakeLists.txt` (`SKIP_RETURN_CODE 77`) não muda.

### Verificação

```text
$ WE2002_LOOKS_IMAGE=C:/nope/typo.bin python tools/kits/selftest.py --image; echo $?
  FAIL  WE2002_LOOKS_IMAGE points at a file  C:/nope/typo.bin is not one
kits_image: 1 failure(s)
1
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --image; echo $?
kits_image: skipped -- WE2002_LOOKS_IMAGE is not set (the Japanese data track .bin)
77
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python tools/kits/selftest.py --image | tail -1; echo $?
kits_image: 0 failure(s)
0
```
- **Closed** — commit `a9b57017` (2026-10-01): fix(kits): fail kits_image when WE2002_LOOKS_IMAGE points at no file
  - Files (`git show --name-status a9b57017`):
    - `M docs/tasks/kits/CORR-KITS-020.md`
    - `M tools/kits/selftest.py`
