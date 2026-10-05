---
id: CORR-KITS-060
---

# CORR-KITS-060 — Pôr WE2002_LOOKS_IMAGE no comando de captura do critério 1 no Log

Origin: [KITS-TASK-33](/docs/tasks/kits/33-aba-diagnostico.md)

## Problem

O Log da KITS-TASK-33 cita `work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --tag <T> --tab diag --screenshot …` e dá os sha256 `9c1ec4f0a88a` (48), `fdde711d5d1c` (70) e `cf7f3c54141e` (13). O comando exatamente como está dá `a3e2e0563e9f`, `b4ae922b5ce8` e `00736764d501`: cada captura difere da registrada em 5.297 px — a aba 3D cinza e a última linha "3D off: …" em vez de "3D geometry: …/japanese-shift-jis.bin". Os hashes do Log só voltam com `WE2002_LOOKS_IMAGE` exportado.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --tag 48 --tab diag --screenshot /tmp/x48.png; sha256sum /tmp/x48.png | cut -c1-12
a3e2e0563e9f
$ compare -metric AE /tmp/x48.png work/kits-diag-ed-48.png null:
5297
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --tag 48 --tab diag --screenshot /tmp/y48.png; sha256sum /tmp/y48.png | cut -c1-12
9c1ec4f0a88a
```

## Root cause

A captura rodou num shell com `WE2002_LOOKS_IMAGE` já exportado, e o Log deixou a variável fora do comando transcrito.

## Fix

No Log de `docs/tasks/kits/33-aba-diagnostico.md`, prefixar o comando do critério 1 com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin` (e `DISPLAY=:98 XAUTHORITY=`), ou refazer os hashes sem ela.

## Arquivos a criar ou modificar

- `docs/tasks/kits/33-aba-diagnostico.md`

## Verificação

O comando exatamente como citado no Log, seguido de `sha256sum`, imprime `9c1ec4f0a88a` / `fdde711d5d1c` / `cf7f3c54141e`.

## Log de Execução
