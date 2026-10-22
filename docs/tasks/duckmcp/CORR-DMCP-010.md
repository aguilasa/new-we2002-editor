---
id: CORR-DMCP-010
---

# CORR-DMCP-010 — Provar o critério 6 com comando cuja saída nomeia o controle

Origin: [DMCP-TASK-09](/docs/tasks/duckmcp/09-cli-fork-e-lancadores.md)

## Problem

O critério 6 pede que a linha de controles do `kits/selftest.py --quiet` mostre
`fork-joystick-let-through` vermelho no arquivo novo. O `--quiet` só imprime o agregado. O vermelho é
real, mas só aparece pelo `controls.py --only`, que foi o substituto do Log.

## Evidência

```text
$ python3 tools/kits/selftest.py --quiet | tail -4
  ..... 87 of 87 controls red
controls: 0 failure(s)
kits_selftest: 0 failure(s)
$ python3 tools/kits/controls.py --only fork-joystick-let-through | tail -2
  RED    fork-joystick-let-through    duckmcp/fork.py :: refuse_joysticks
controls: 1 of 1 red
```

## Root cause

O critério cita uma saída que o modo `--quiet` nunca imprime.

## Fix

Reescrever o critério 6 da `docs/tasks/duckmcp/09-cli-fork-e-lancadores.md` para
`python3 tools/kits/controls.py --only fork-joystick-let-through` (mais `kits/selftest.py --quiet`
saindo 0).

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/09-cli-fork-e-lancadores.md`

## Verificação

`python3 tools/kits/selftest.py --quiet | grep -c fork-joystick-let-through` dá 0 hoje; o critério 6
tem de citar um comando cuja saída contenha o nome do controle, e esse comando, rodado, tem de mostrar
`RED    fork-joystick-let-through`.

## Log de Execução
