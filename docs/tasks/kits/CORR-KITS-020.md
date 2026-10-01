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
