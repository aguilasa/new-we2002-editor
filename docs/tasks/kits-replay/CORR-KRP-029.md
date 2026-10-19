---
id: CORR-KRP-029
---

# CORR-KRP-029 — ANIME.BIN inteiro na RAM e recaptura igual à pose antiga medidos por sonda descartável, sem opção versionada

Origin: [KRP-TASK-14](/docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md)

## Problem

A §5.1 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#5.1) afirma duas coisas que nenhuma
ferramenta versionada imprime:

- o `ANIME.BIN` está inteiro na RAM do replay, em `layout.ANIME_BASE`, nas duas cópias mestras, e o
  `ANIME_BUILD` é a mesma instrução. A docstring de `pose_capture` diz "measured on both save states
  by content", e o próprio Log admite que isso saiu de uma "sonda descartável" que contou 396804 de
  396804 bytes;
- "a recaptura reproduz as cinco poses de `work/kits-pose/` peça por peça" (no Log, "11 de 11 …
  comparação campo a campo"), também sem comando versionado.

O `CLAUDE.md` exige que sonda que produziu um número vire opção de ferramenta versionada antes de o
número entrar em texto. Os números se reproduzem, mas só com o script ad hoc abaixo.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 - <<'PY'
import os, sys
sys.path[:0] = ["tools/looks", "tools/pes2"]
import anime, layout, savestate, iso_source
with iso_source.open_disc(os.environ["WE2002_LOOKS_IMAGE"]) as disc:
    data = anime.read(disc)
base = layout.ANIME_BASE & 0x1FFFFF
for slot in (9, 10):
    ram = savestate.SaveState("work/kits-states/SLPM-87056_%d.sav" % slot).ram
    same = sum(a == b for a, b in zip(ram[base:base + len(data)], data))
    print(slot, same, "of", len(data))
PY
9 396804 of 396804
10 396804 of 396804
$ grep -rn "396804" tools/kits/
(sem saída: nenhuma ferramenta de kits imprime esse número)
$ python3 - <<'PY'
import json
for f in ("slot9-keeper-front","slot10-keeper-front","slot9-focus3-first","slot10-focus2-first","slot10-focus3-first"):
    a=json.load(open("work/kits-pose/%s.json"%f))["pieces"]; b=json.load(open("work/kits-oracle/anime/%s.json"%f))["pieces"]
    k=("section","rotation","translation")
    print(f, len(a), len(b), sum(all(x[i]==y[i] for i in k) for x,y in zip(a,b)))
PY
slot9-keeper-front 11 11 11
```

As outras quatro poses também dão `11 11 11`.

## Root cause

(Hipótese.) O fato de o replay usar o mesmo mapeamento do `ANIME.BIN` da tela LOOKS SET foi conferido
uma vez, como pressuposto dos breakpoints novos, e nunca virou opção de ferramenta.

## Fix

- Uma opção de sonda, por exemplo `tools/kits/replay.py anime-ram <state.sav>...`, que compare a RAM
  em `layout.ANIME_BASE` com `anime.read(disc)` e a palavra em `layout.ANIME_BUILD` com o `jal`
  esperado, falhando quando diferirem.
- Opcionalmente, `replay.py pose A --same-as B`, comparando seção, rotação e translação.
- Fazer as frases da §5.1 e a docstring do `oracle.py` citarem esses comandos.
- Um controle plantado (outro slot de state, ou base deslocada) que deixe a sonda vermelha.

## Arquivos a criar ou modificar

- `tools/kits/replay.py`
- `tools/kits/oracle.py`
- `docs/PLAN-KITS-REPLAY.md`
- `tools/kits/controls.py`

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py anime-ram work/kits-states/SLPM-87056_9.sav work/kits-states/SLPM-87056_10.sav
```

Hoje falha, porque o subcomando não existe. Depois do conserto tem de imprimir `396804 of 396804`
para cada state e sair 0.

## Log de Execução
