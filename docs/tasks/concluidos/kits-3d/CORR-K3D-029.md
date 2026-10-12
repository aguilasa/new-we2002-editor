---
id: CORR-K3D-029
---

# CORR-K3D-029 — Números das conclusões do G8 escritos à mão, e "onze painéis" errado

Origin: [K3D-TASK-18](/docs/tasks/concluidos/kits-3d/18-medir-os-22-replay.md)

## Problem

Alguns números das conclusões do G8 sobre a [K3D-TASK-18](/docs/tasks/concluidos/kits-3d/18-medir-os-22-replay.md) foram escritos à mão e não estão em
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

### 2026-10-11 — margem e faixa de quadros impressas pelo `--replay-field`

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `75ae037`, com as
mesmas saídas da Evidência:
- `page 576: 10 focus(es), …`;
- as três linhas do `grep`, 1054, 1115 e 1121;
- o `66` do R2.

Conserto em `tools/kits/oracle.py`: o `run_replay_field` imprime duas linhas novas.
- `closest next figure inside 8 px: focus K, X px farther off the axis and D apart in depth (the
  margin asks 1000)`. Entre os focos cuja figura seguinte fica a menos de `REPLAY_FOCUS_MARGIN[0]`
  px a mais do eixo, a linha mostra o de menor distância em profundidade, que é o par que a margem
  julga. Sem nenhum, imprime `no next figure inside 8 px of any followed one`.
- `frames from the last tap to the end of each capture: A to B, under the idle 390`.

As capturas são as que a [CORR-K3D-026](/docs/tasks/concluidos/kits-3d/CORR-K3D-026.md) fez ao vivo, relidas
com `--frame-json`. As três saídas foram recoladas no G8:
- `--replay-field 9`: `closest next figure inside 8 px: focus 3, 3.46 px farther off the axis and
  2108 apart in depth (the margin asks 1000)`, e `… capture: 64 to 66, under the idle 390`;
- `--replay-field 10`: `no next figure inside 8 px of any followed one`, e `… 64 to 65 …`;
- `--replay-field 9 --field-button R2`: `closest … focus 20, 3.46 px … 2108 …`, e `… 64 to 67 …`.

G8:
- a conclusão 2 cita a linha da margem;
- a 7 diz "dez na página do Brasil (o do Marcos, pela K3D-TASK-17) e onze na da Croácia";
- a 8 cita as três faixas impressas.

Os quadros mudaram desde a Evidência (63 a 66), porque a captura passou a nove submissões. A faixa
agora sai da ferramenta.

Verificação: `grep -n 'onze painéis de cada' docs/KITS-AJUSTES-3D.md` não imprime nada, e o
`--replay-field 9` imprime a linha de margem que o G8 cita.

Varredura: `grep -rn '63 a 65\|3,4 px\|onze painéis'` em G8, task 19, perfil e `oracle.py` só acha a
linha 943. Ela fala dos onze painéis da página de textura do Brasil, goleiro incluído, e está certa.
O Log da K3D-TASK-18 fica como registro.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 47 of 47 red`.
- **Closed** — commit `2d21fd7f` (2026-10-11): fix(kits): print the closest margin pair and the frame range in --replay-field
  - Files (`git show --name-status 2d21fd7f`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-029.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`
