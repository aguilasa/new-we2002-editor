---
id: CORR-KITS-063
---

# CORR-KITS-063 — Escrever caminhos absolutos de imagem na receita de ctest do Log

Origin: [KITS-TASK-35](/docs/tasks/kits/35-fechamento-fase-9.md)

## Problem

O cabeçalho do Log da KITS-TASK-35 diz que o gate rodou com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin` e `WE2002_KITS_ED_IMAGE=roms/golden-european-deluxe.bin`. O `ctest` roda esses testes a partir de `build/tests`, então os caminhos relativos não resolvem: rodado como escrito, `kits_image` e `kits_ui` falham, em vez do "100% … out of 4, nenhum skipped" registrado. O verde só se reproduz com caminhos absolutos — a receita registrada não refaz o resultado registrado.

## Evidência

```text
$ cd <repo>; DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_KITS_ED_IMAGE=roms/golden-european-deluxe.bin ctest --test-dir build -R 'kits_(image|ui)'
19 - kits_image (Failed)
21 - kits_ui (Failed)
(LastTest.log: `FAIL  WE2002_LOOKS_IMAGE points at a file  roms/japanese-shift-jis.bin is not one`)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_ED_IMAGE=$PWD/roms/golden-european-deluxe.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ grep -n 'WE2002_LOOKS_IMAGE=roms' docs/tasks/kits/35-fechamento-fase-9.md
27:`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
```

## Root cause

Hipótese: a corrida usou caminhos absolutos (ou `$PWD/`), e o Log os encurtou para a forma relativa ao repositório ao transcrever.

## Fix

No cabeçalho do Log de `docs/tasks/kits/35-fechamento-fase-9.md`, escrever as variáveis como `$PWD/roms/...` (ou caminhos absolutos). Opcional: fazer `tools/kits/selftest.py` e `ui_check.py` dizerem que caminho relativo é resolvido a partir do diretório de trabalho do `ctest`.

## Arquivos a criar ou modificar

- `docs/tasks/kits/35-fechamento-fase-9.md`

## Verificação

A linha de ambiente do Log, colada num shell na raiz do repositório, seguida de `ctest --test-dir build -R kits`, imprime `100% tests passed, 0 tests failed out of 4`. Hoje falha 2 de 4, e `grep -c 'WE2002_LOOKS_IMAGE=roms' docs/tasks/kits/35-fechamento-fase-9.md` dá 1 (0 depois do conserto).

## Log de Execução

Reproduzido em 2026-10-05 sobre `e976571`: com o caminho relativo do Log, o `kits_image` falha:

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin ctest --test-dir build -R kits_image
0% tests passed, 1 tests failed out of 1
$ grep -n "is not one" build/Testing/Temporary/LastTest.log
10:  FAIL  WE2002_LOOKS_IMAGE points at a file  roms/japanese-shift-jis.bin is not one
```

Conserto: o cabeçalho do Log da task 35 escreve as duas variáveis como `$PWD/roms/...`, rodadas da
raiz, e diz por quê. A parte opcional (as ferramentas explicarem o caminho relativo) ficou de
fora, porque alargaria o escopo.

```text
$ grep -c 'WE2002_LOOKS_IMAGE=roms' docs/tasks/kits/35-fechamento-fase-9.md
0
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_ED_IMAGE=$PWD/roms/golden-european-deluxe.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `df15625` (2026-10-05): docs(kits): task 35 log gives the image paths ctest can resolve
  - Files (`git show --name-status df15625`):
    - `M docs/tasks/kits/35-fechamento-fase-9.md`
    - `M docs/tasks/kits/CORR-KITS-063.md`
