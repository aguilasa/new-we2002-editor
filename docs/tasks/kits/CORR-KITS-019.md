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

### Reprodução (HEAD `201c7915`)

O `rite reproduce --scratch` rodou fora da árvore e não achou `roms/`; refeita no repositório:

```text
$ python tools/kits/cli.py open --negative roms/golden-european-deluxe.bin
  ...
  File "C:\github\new-we2002-editor\tools\kits\core\source.py", line 381, in build_open_fixtures
    kit_bytes = image.read_file(kit_path)
  ...
iso.Form2Sector: sector 8415 is Form 2; it has no 2048-byte area
exit 1
```

REPRODUCED. Causa raiz confirmada pelo traceback: `build_open_fixtures` lia o `TEX_00` por `iso.Image.read_file`, que recusa setor marcado Form 2; o resto do `source.py` lê por `read_disc_file`, que sabe do bit errado da European Deluxe.

### O que foi feito

- `tools/kits/core/source.py`, `build_open_fixtures`: o `TEX_00` sai de `read_disc_file(image, kit_path)`. Na ED o kit tem 32.496 bytes (lido até o fim que o cabeçalho declara) e o registro 0 está em 6484; o byte da tag é achado da lista, então segue certo sem mudar nada além da leitura.
- KITS-TASK-08: o vermelho da ED retranscrito inteiro, com a nota das duas linhas FAIL que sumiram e por quê.

### Verificação

```text
$ python tools/kits/cli.py open --negative roms/golden-european-deluxe.bin | tail -1; echo "exit ${PIPESTATUS[0]}"
11 of 11 expectations held
exit 0
$ python tools/kits/cli.py open --negative roms/japanese-shift-jis.bin | tail -1
11 of 11 expectations held
$ WE2002_LOOKS_IMAGE=roms/golden-european-deluxe.bin python tools/kits/selftest.py --image | grep -c FAIL
1
```
