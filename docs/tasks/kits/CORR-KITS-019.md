---
id: CORR-KITS-019
---

# CORR-KITS-019 — Transcribe the full ED kits_image red, and fix open_controls on ED

Origin: [KITS-TASK-08](/docs/tasks/kits/08-selftest-e-ctest.md)

## Problem

O Log da KITS-TASK-08 cita o vermelho do `kits_image` na European Deluxe como uma linha FAIL só ("every kit passes the guard"). A corrida imprime outras duas: as fixtures de reconhecimento (`api.open_controls`, o mesmo código do `cli.py open --negative`) quebram com `iso.Form2Sector` na ED. O vermelho tem uma segunda causa, que não foi registrada, e o `cli.py open --negative` solta traceback nesse disco.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=C:/github/new-we2002-editor/roms/golden-european-deluxe.bin ctest -R kits_image -V   # build fora da árvore
15:   ..... 97 of 105 kits pass the guard
15:   FAIL  build the recognition fixtures: raised Form2Sector: sector 8415 is Form 2; it has no 2048-byte area
15:   FAIL  every recognition fixture gives what it has to  []
$ python tools/kits/cli.py open --negative roms/golden-european-deluxe.bin
iso.Form2Sector: sector 8415 is Form 2; it has no 2048-byte area   (traceback)
```

## Root cause

O trecho do Log foi aparado. Hipótese, não rastreada: o `open_controls` lê um arquivo por `iso.Image.read`, sem o tratamento de Form 2 que o `source.read_disc_file` tem.

## Fix

Fazer o `open_controls` de `tools/kits/core/source.py` ler por `read_disc_file`, ou pular essa fixture dizendo o motivo. Retranscrever o vermelho da ED em `docs/tasks/kits/08-selftest-e-ctest.md` com todas as linhas FAIL.

## Arquivos a criar ou modificar

- `tools/kits/core/source.py`
- `docs/tasks/kits/08-selftest-e-ctest.md`

## Verificação

```text
$ python tools/kits/cli.py open --negative roms/golden-european-deluxe.bin
```

Hoje levanta `Form2Sector`; depois tem de terminar sem traceback.

## Log de Execução
