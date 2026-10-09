---
id: CORR-K3D-024
---

# CORR-K3D-024 — Planta e juiz de foco do replay não testam figura errada, e a margem do G8 não existe

Origin: [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md)

## Problem

O G8 (linha 668 de `docs/KITS-AJUSTES-3D.md`) diz que a figura acompanhada é a de menor
z, "com margem exigida pelo juiz". Mas o `replay_focus` da [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md) só ordena por
profundidade, e o `replay_judge` não confere margem nenhuma. Os dois replays desenham só o
goleiro (todo quadro mostra "1 figure(s)"), então o `--plant-replay` pede uma segunda
figura que não existe e falha só com "no second figure in the frame" mais a cascata de
`None` em seguida. A conferência que pegaria a figura errada (raiz 103,
`PLANT_REPLAY_ROOT`) nunca é alcançada com dado real; só o caso sintético "the plant's root
fails" do selftest a cobre. As tasks 18 e 19 reusam o `replay_focus` com várias figuras em
quadro, e ali a margem que falta vai pesar.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json --plant-replay | tail -5
PLANT  the second-nearest figure followed, front and back, expected to open at section 103
FAIL  no second figure in the frame
FAIL  the pose changed by None between two frames, over 0
$ grep -n "margin" tools/kits/oracle.py | grep -ic "replay"
0
$ grep -n "margem" docs/KITS-AJUSTES-3D.md
668:das paradas é no espaço da vista, então o focado é a figura de **menor z**, com margem exigida pelo
```

## Root cause

Hipótese: os quadros ao vivo têm uma figura só, então nem a planta nem a regra de foco
podem ser exercitadas contra uma figura errada mas presente; a margem caiu quando se viu
que o quadro tinha uma figura, e o G8 não foi atualizado.

## Fix

Escolher um, em `tools/kits/oracle.py`: (a) acrescentar a margem de profundidade ao
`replay_focus`/`replay_judge`, falhando quando as duas figuras mais próximas estão mais
perto que a margem, com caso no selftest e entrada no `controls.py`; ou (b) tirar "com
margem exigida pelo juiz" do G8 e do perfil, e registrar que a planta nos slots 9 e 10 só
prova o caminho "nenhuma figura". De todo modo, levar a margem para a K3D-TASK-18.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- tools/kits/selftest.py
- tools/kits/controls.py
- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
grep -n "margin" tools/kits/oracle.py | grep -i "replay"
```

Hoje vazio; depois tem de nomear a conferência de margem — ou o G8 tem de parar de
afirmar uma.

## Log de Execução
