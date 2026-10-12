---
id: CORR-K3D-026
---

# CORR-K3D-026 — Coluna still do --replay-field sai None em 23 de 25 focos

Origin: [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md)

## Problem

O G8 diz que a [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md) repete em todo foco o item 5 da K3D-TASK-17, a pose parada; o
documento diz que ela "faz uma pose_capture de dois quadros", e o docstring de
`REPLAY_FIELD_SUBMITS` diz "two whole frames". Mas o `replay_frames` entrega um quadro só
para quase todo foco, então `pose_change` nunca é calculado: a coluna `still` imprime
`None` em 23 das 25 linhas de cada slot (0 só em k = 9 e 19 no slot 9, e em k = 11 e 18
no slot 10). Nada a julga, e nenhuma conclusão do G8 a menciona.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json | awk '$1 ~ /^[0-9]+$/ && NF>=15 {print $15}' | sort | uniq -c
      2 0
     23 None
$ grep -n 'REPLAY_FIELD_SUBMITS = ' -A3 tools/kits/oracle.py
REPLAY_FIELD_SUBMITS = POSE_SUBMITS
"""Submits each focus's capture takes: two whole frames. ...
```

O revisor viu as mesmas contagens numa corrida ao vivo de `--replay-field 10` na HEAD.

## Root cause

Hipótese, não provada: em campo um quadro leva mais submissões de lista à GPU do que as 3
por quadro que `POSE_SUBMITS = 7` supõe, e o `pose_frames` fecha só um quadro inteiro
depois de descartar o primeiro, cortado.

## Fix

Em `tools/kits/oracle.py`, dimensionar `REPLAY_FIELD_SUBMITS` pelos quadros contados, ou
repetir até o `replay_frames` entregar ao menos 2. Fazer o `replay_field_judge` falhar com
`still` igual a `None` ou acima do limite, com caso no selftest e um controle. Corrigir o
docstring e a frase "pose_capture de dois quadros" do G8, e acrescentar ao G8 uma
conclusão sobre a pose parada.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- tools/kits/selftest.py
- tools/kits/controls.py
- docs/KITS-AJUSTES-3D.md

## Verificação

`python3 tools/kits/oracle.py --replay-field 9` (ao vivo) não imprime `None` na coluna
`still`, e um foco com `still` igual a `None` faz o `replay_field_judge` devolver FAIL. Hoje
o comando de cima conta 23 `None`.

## Log de Execução

### 2026-10-11 — nove submissões por foco, e o juiz pede a pose parada

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `75ae037`. A contagem
da Evidência saiu `2 0` e `23 None`, e o `grep` mostrou `REPLAY_FIELD_SUBMITS = POSE_SUBMITS` com o
docstring "two whole frames".

**Causa, medida.** Cada quadro manda três listas à GPU, e só uma tem as figuras. A captura começa
em qualquer uma das três. Com sete submissões, só dois submits com figura caem na janela na maior
parte das fases. O `pose_frames` descarta o primeiro bloco, que começou no meio do quadro, e sobra
um quadro inteiro. A hipótese da CORR (mais de três submits por quadro em campo) não se confirmou:
são três, como na `LOOKS SET`. O que falhava era a conta das sete.

**Conserto** (`tools/kits/oracle.py`):
- `REPLAY_FIELD_SUBMITS = 9`, com o docstring refeito: nove sempre trazem três submits com figura,
  e portanto dois quadros inteiros.
- O `field_row` guarda `whole`, os quadros inteiros da captura.
- O `--replay-field` imprime a linha `whole frames per capture: …, from N submit(s); still pose: …`,
  com os submits contados nos eventos da captura, não tirados da constante.
- O `replay_field_judge` falha num foco com `still` em `None` ou acima de `REPLAY_STILL` (0).
- Caso novo no `selftest.py`: `oracle --replay-field: a focus with no still pose, or one that moved,
  fails`.
- Controle novo no `controls.py`: `oracle-replay-field-still-unasked`.

**Medido ao vivo**, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`
e as cópias mestras `54c79792…` e `bdf47644…`:
- `python3 tools/kits/oracle.py --replay-field 9`: saída 0, `whole frames per capture: 2 to 2, from 9 submit(s); still pose: 0`
  e `ok    22 focus(es) follow a player …`;
- `--replay-field 10`: saída 0, a mesma linha de quadros e `ok    22 focus(es) …`;
- `--replay-field 9 --field-button R2`: saída 0, a mesma linha de quadros, só impresso.

A Verificação vale: o comando da Evidência, agora na captura nova, conta `25 0` e nenhum `None`. A
captura antiga, de sete submissões, ficou guardada em
`work/kits-oracle/replay-field-9-seven-capture.json`. Relida pela HEAD nova
(`--replay-field 9 --frame-json work/kits-oracle/replay-field-9-seven-capture.json`), ela sai 1 com
23 `FAIL  focus …: the figure's matrices differ by None between the last two frames, not within 0`
e com `whole frames per capture: 1 to 2, from 7 submit(s)`: o vermelho do juiz com dado real.

**G8:** as três saídas foram recoladas da HEAD, a frase "pose_capture de dois quadros" foi
corrigida, e entrou a conclusão 9, sobre a pose parada.

Varredura: a planta inteira passou de 42 `FAIL` para 48, porque a figura plantada também cai no juiz
da pose. A conclusão 8 do tempo passou a "64 a 66 quadros (até 67 no R2)". A forma impressa desses
dois números é trabalho da [CORR-K3D-029](/docs/tasks/kits-3d/CORR-K3D-029.md).

**No caminho.** As quatro primeiras corridas deram quatro tabelas diferentes:
- quadro preto no k = 8 do slot 9;
- MCP sem resposta no slot 10;
- câmera voando no R2;
- o k = 0 do slot 9 com `still 282`.

A causa era um controle sem fio ligado (`Wireless Controller`, js0), que o `[Pad1]` (`SDL-0`) lia.
O usuário o desligou, e as três corridas acima foram feitas sem ele. Abri duas fixes:
- [CORR-K3D-030](/docs/tasks/kits-3d/CORR-K3D-030.md): o juiz aceitou tabelas de 3 e 7 focos;
- [CORR-K3D-031](/docs/tasks/kits-3d/CORR-K3D-031.md): nenhuma guarda contra o controle.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 47 of 47 red`.
