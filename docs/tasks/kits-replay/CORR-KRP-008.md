---
id: CORR-KRP-008
---

# CORR-KRP-008 — Intervalos entre toques de R1 na virada não são guardados nem julgados contra os 390 quadros

Origin: [KRP-TASK-07](/docs/tasks/kits-replay/07-replay-py-capture-com-as-guardas-medidas-e-o.md)

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
