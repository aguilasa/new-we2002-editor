---
id: CORR-KRP-008
---

# CORR-KRP-008 — Intervalos entre toques de R1 na virada não são guardados nem julgados contra os 390 quadros

Origin: [KRP-TASK-07](/docs/tasks/concluidos/kits-replay/07-replay-py-capture-com-as-guardas-medidas-e-o.md)

## Problem

A §2.5 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#2.5) exige "toda sequência abaixo dos 390
quadros". Numa captura virada, `sequences()` julga só a frente e o trecho do último toque de R1 até o
fim (`back_frames`). A virada em si (610, 581 e 601 quadros a partir do reload) sai como "not
judged".

O motivo declarado é que cada toque zera a contagem de ociosidade
([KITS-REPLAYS-9-10.md](/docs/KITS-REPLAYS-9-10.md), linha 46). Mas os intervalos entre toques
consecutivos de R1 nunca são registrados, impressos nem julgados, e cada um inclui até
`REPLAY_YAW_STOPS` paradas de matriz (36, depois 300). A afirmação "a virada nunca chega ao timeout"
se apoia numa média (cerca de 610/15 quadros), não num intervalo máximo medido.

## Evidência

```text
$ grep -n '("turn", data\["turn_frames"\], False)' tools/kits/replay.py
532:        out += [("turn", data["turn_frames"], False), ("back", data["back_frames"], True)]
$ python3 -c "import json;d=json.load(open('work/kits-replay/replay-9-3-R1.json'));print(sorted(k for k in d if 'frame' in k))"
['back_frames', 'front_frames', 'turn_frames']
```

Nenhum intervalo por toque fica guardado.

## Root cause

`replay_capture` guarda só `tapped`, a contagem de quadros no último toque, e descarta os intervalos
anteriores (comprovado pelo código acima).

## Fix

- Em `tools/kits/replay.py`, `replay_capture`: a cada toque, acrescentar o intervalo desde o toque
  anterior a uma lista (por exemplo `tap_gaps`).
- Em `sequences()`: reportar o maior intervalo como sequência julgada ("turn gap").
- Acrescentar um caso de selftest e um controle que plante um intervalo de 390 ou mais.

## Arquivos a criar ou modificar

- `tools/kits/replay.py`
- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

```sh
python3 -c "import json;d=json.load(open('work/kits-replay/replay-9-3-R1.json'));print(max(d['tap_gaps']))"
```

Hoje dá `KeyError`. Depois de recapturar, tem de imprimir um valor abaixo de 390.

## Log de Execução

`replay_capture` passa a guardar, na captura virada, a lista `tap_gaps`: a cada toque de R1/L1, os
quadros desde o toque anterior, o primeiro contado do último toque de L2 do reload (o `start` de
`replay_arrive`). O último trecho, do último toque ao fim, continua sendo o `back_frames`, então
`sum(tap_gaps) + back_frames == turn_frames`. `sequences()` julga o maior intervalo como `turn gap`
contra o timeout do slot; a virada inteira (`turn`) continua impressa e não julgada. Captura sem
`tap_gaps` (as de antes desta correção, e as de `work/kits-oracle/`) continua carregando: a chave é
opcional, `core/replay.py` não a exige, e `sequences()` só omite o `turn gap`. O schema segue
`kits-replay/1`; as capturas de `work/kits-oracle/` não foram recapturadas.

Selftest: três casos novos em `tools/kits/selftest.py` (maior intervalo 389 julgado e verde; um
intervalo de 390 falha como `turn gap`; captura sem `tap_gaps` dá `front`, `turn`, `back`). Controle
novo `replay-capture-tap-gap-unjudged`, que planta o `turn gap` como não julgado.

```text
$ python3 tools/kits/controls.py --only replay-capture-tap-gap-unjudged
  base   unplanted sandbox            selftest exit 0
  RED    replay-capture-tap-gap-unjudged kits/replay.py :: sequences
controls: 1 of 1 red
$ python3 tools/kits/controls.py | tail -1
controls: 68 of 68 red
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
```

Recaptura das três viradas, com `DISPLAY=:98 XAUTHORITY=
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin
WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue` (linhas finais de cada corrida):

```text
$ python3 tools/kits/replay.py capture --slot 9 --focus 3 --turn R1 --out work/kits-replay
  front     65 frame(s) from its last tap to the end of its capture; timeout 390
  turn      610 frame(s) from the reload, across its taps (each starts the idle again): not judged
  turn gap  60 frame(s) the largest between two taps of the turn; timeout 390
  back      44 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-9-3-R1.json (schema v1, sha256 0df47edfc7a2870ce702b4f353d46caee6252d90b64dcbd2e901d32e23f52a03)
$ python3 tools/kits/replay.py capture --slot 10 --focus 3 --turn R1 --out work/kits-replay
  front     64 frame(s) from its last tap to the end of its capture; timeout 390
  turn      581 frame(s) from the reload, across its taps (each starts the idle again): not judged
  turn gap  60 frame(s) the largest between two taps of the turn; timeout 390
  back      45 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-10-3-R1.json (schema v1, sha256 594be39b8b2a69e11b870f294b4e8fd649a5a9bfe87876043a00c6ac070124dc)
$ python3 tools/kits/replay.py capture --slot 10 --focus 2 --turn R1 --out work/kits-replay
  front     65 frame(s) from its last tap to the end of its capture; timeout 390
  turn      601 frame(s) from the reload, across its taps (each starts the idle again): not judged
  turn gap  60 frame(s) the largest between two taps of the turn; timeout 390
  back      35 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-10-2-R1.json (schema v1, sha256 d19113ae9f91d1f06d8472ed7a95eeedb2dc163d08ba0dd8685e9b7a2f5683cf)
```

Verificação:

```text
$ python3 -c "import json;d=json.load(open('work/kits-replay/replay-9-3-R1.json'));print(max(d['tap_gaps']))"
60
$ python3 -c "import json;d=json.load(open('work/kits-replay/replay-10-3-R1.json'));print(max(d['tap_gaps']))"
60
$ python3 -c "import json;d=json.load(open('work/kits-replay/replay-10-2-R1.json'));print(max(d['tap_gaps']))"
60
```

O maior intervalo é, nas três, o primeiro: ele inclui os `REPLAY_FIELD_SETTLE` (60) quadros de
assentamento da câmera depois do último L2. Entre toques de R1 os intervalos ficam entre 28 e 43
quadros. Os totais de virada (610, 581, 601) e os `back` (44, 45, 35) repetem os da KRP-TASK-07.
- **Closed** — commit `41f3fc2f` (2026-10-14): fix(kits): keep and judge the gaps between turn taps against the replay timeout
  - Files (`git show --name-status 41f3fc2f`):
    - `M docs/tasks/kits-replay/CORR-KRP-008.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/replay.py`
    - `M tools/kits/selftest.py`
