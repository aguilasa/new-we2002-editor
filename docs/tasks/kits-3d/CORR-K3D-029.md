---
id: CORR-K3D-029
---

# CORR-K3D-029 — Números das conclusões do G8 escritos à mão, e "onze painéis" errado

Origin: [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md)

## Problem

Alguns números das conclusões do G8 sobre a [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md) foram escritos à mão e não estão em
nenhuma saída de ferramenta:

- a conclusão 7 diz "Os onze painéis de cada página saem distintos", mas a página 576 tem
  10 focos;
- a conclusão 2 diz "3,4 px a mais", que é 4,0 − 0,6 da tabela arredondada; a diferença
  real é 3,46, e nenhuma ferramenta a imprime;
- a conclusão 8 e o Log dizem "cada foco corre de 63 a 65 quadros", mas a corrida de R2
  colada na mesma seção tem um 66.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json | grep '^  page 576'
  page 576: 10 focus(es), numbers 9 11 10 2 6 16 7 4 3 5, ...
$ grep -n 'onze painéis de cada\|3,4 px a mais\|63 a 65' docs/KITS-AJUSTES-3D.md
1054: ... 3,4 px a mais, mas 2108 atrás ...
1115: ... Os onze painéis de cada
1121: 8. **O tempo.** Cada foco corre de 63 a 65 quadros ...
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay-field 9 --field-button R2 --frame-json work/kits-oracle/replay-field-9-R2-capture.json | awk '$1 ~ /^[0-9]+$/ {print $3}' | sort -n | tail -1
66
```

## Root cause

As conclusões foram derivadas à mão da tabela impressa, não impressas pelo `--replay-field`.

## Fix

No `run_replay_field` de `tools/kits/oracle.py`, imprimir o par de margem mais apertado (px
e diferença de profundidade) e a faixa de quadros. No G8 de `docs/KITS-AJUSTES-3D.md`,
dizer "dez painéis do Brasil (o do Marcos pela K3D-TASK-17), onze da Croácia", e colar a
margem e a faixa de quadros das linhas novas, cobrindo também a corrida de R2.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md

## Verificação

`grep -n 'onze painéis de cada' docs/KITS-AJUSTES-3D.md` não imprime nada, e
`--replay-field 9` imprime a linha de margem mais apertada que o G8 cita.

## Log de Execução
