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
