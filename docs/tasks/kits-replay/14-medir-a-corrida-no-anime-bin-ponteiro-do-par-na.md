---
id: KRP-TASK-14
---

# KRP-TASK-14 — Medir a corrida no ANIME.BIN: ponteiro do par na captura e pose --against-anime

## Goal

Fica medido que animação e quadro do `ANIME.BIN` explicam a pose de corrida do replay: a captura passa a gravar o ponteiro do par (como o `--pose` do `looks`), e `replay.py pose <captura> --against-anime` imprime animação e quadro das cinco poses — ou a negativa, com comando e saída. O resultado vai no §5.1 do plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (`pose`)
  - `tools/kits/core/replay.py`
  - `tools/kits/oracle.py` (o `pose_capture` lê o ponteiro)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§5.1: o resultado)
- Out:
  - posar a aba (KRP-TASK-15)

## Done criteria

- [x] `replay.py pose <captura> --against-anime --json` nas cinco poses de perto recapturadas com o ponteiro: animação, quadro e quantas peças o par explica, colados no Log
- [x] o esperado (animação e quadro) é constante por (slot, foco) no código (K1); uma planta que aponta outra animação fica vermelha com dado real (K2)
- [x] negativa é resultado: se nenhum par explicar, o §5.1 diz isso com comando e saída, e a 15 usa a pose capturada
- [x] sem uma das cópias mestras: `rite mark KRP-TASK-14 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário — não se aplica: as duas cópias existem (Log)
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Leitura do arquivo por `tools/looks/anime.py` (`no_pair_explains`, `pose`, `compose`, `against_walk`). O atraso de desenho do `looks` vale aqui: o ponteiro vivo numa parada nomeia a peça anterior.

## Log de Execução

- **done** (2026-10-18): positivo nas cinco poses de perto. O `ANIME.BIN` está inteiro na RAM das duas cópias mestras, em `layout.ANIME_BASE` (`0x8017EE00`, o mesmo da `LOOKS SET`), e o `ANIME_BUILD` é a mesma instrução (`0c00f52f`, `jal 0x8003D4BC`). Isso saiu de uma sonda descartável sobre a RAM dos `.sav` (`savestate.SaveState(...).ram`): 396804 de 396804 bytes iguais em cada slot. (Nota de 2026-10-19: a sonda virou `replay.py anime-ram <state.sav>...`, e a comparação com `work/kits-pose/` virou `replay.py pose <A> --same-as <B>`; transcrições na [CORR-KRP-029](/docs/tasks/kits-replay/CORR-KRP-029.md).) O que fica versionado é o par na captura: o `pose_capture` agora para no `ANIME_BUILD` e no `POSE_MATRIX`, e cada parada de matriz leva `pair` e `camera`; o `matrix_pieces` os passa à peça, e `pose_piece` os grava na pose. O critério "sem uma das cópias mestras" não se aplica: as duas existem (`test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav` sai 0). A negativa também não: nenhum par deixou de explicar.

As cinco recapturadas, cada uma com a captura num caminho novo (para não tocar as fixadas do gate) e a pose em `work/kits-oracle/anime/`:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/kits/oracle.py --replay 9 --focus 0 --pose-dir work/kits-oracle/anime --frame-json $S/krp14/replay-9-0.json
  followed figure, head first: 34 13 14 16 92 17 18 20 11 19 21  (one more piece the draw lag leaves unnamed)
  pose kept at work/kits-oracle/anime/slot9-keeper-front.json (projection H 1376, OFX 0.0, OFY 0.0)
$ ... --replay 10 --focus 0 ...   pose kept at work/kits-oracle/anime/slot10-keeper-front.json
$ ... --replay 9 --focus 3 ...    followed figure, head first: 46 2 3 5 90 6 7 9 11 8 10
$ ... --replay 10 --focus 2 ...   followed figure, head first: 46 2 95 96 97 98 7 9 11 8 10
$ ... --replay 10 --focus 3 ...   followed figure, head first: 46 2 95 96 93 98 7 9 11 8 10
```

A recaptura é a mesma pose: 11 de 11 peças com seção, rotação e translação iguais às de `work/kits-pose/` nas cinco (comparação campo a campo dos dois JSON). Digests: `18fbf3c3…` (9 goleiro), `a2d4e3bb…` (10 goleiro), `4f5221f9…` (9 foco 3), `27da64f7…` (10 foco 2), `63c427bf…` (10 foco 3), fixados em `ANIME_POSES`.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-keeper-front.json --against-anime
slot 9 focus 0: 10 of 11 piece(s) carry a pair, 10 explained; animation [0, 1] frame 0 explains 10; expected [0, 0]
$ ... slot10-keeper-front.json --against-anime
slot 10 focus 0: 10 of 11 piece(s) carry a pair, 10 explained; animation [0, 1] frame 0 explains 10; expected [0, 0]
$ ... slot9-focus3-first.json --against-anime
slot 9 focus 3: 10 of 11 piece(s) carry a pair, 10 explained; animation [146] frame 8 explains 10; expected [146, 8]
$ ... slot10-focus2-first.json --against-anime
slot 10 focus 2: 10 of 11 piece(s) carry a pair, 10 explained; animation [134] frame 9 explains 10; expected [134, 9]
$ ... slot10-focus3-first.json --against-anime
slot 10 focus 3: 10 of 11 piece(s) carry a pair, 10 explained; animation [4] frame 9 explains 10; expected [4, 9]
```

Por peça, o `--json` dá o par, o quadro, o slot do par e a regra: no slot 9 goleiro e no 10 foco 2, `mirror` no torso e `flip` nos membros, que leem o par do irmão (`anime.WALK_SIDE_RULES`); nos outros três, `plain`. A cabeça fica sem par: ela vem antes de qualquer parada de `ANIME_BUILD`.

Nota de 2026-10-19 ([CORR-KRP-030](/docs/tasks/kits-replay/CORR-KRP-030.md)): o critério 1 pede o `--json`, e o bloco acima só tinha o resumo em texto. As cinco saídas `--json`, rerodadas na HEAD `d5a52c01`, com o resumo e uma linha por peça (`[seção, par, animações, quadro, slot do par, regras]`; `null` é a cabeça, sem par):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-keeper-front.json --against-anime --json | jq '{animations, frame, explains, explained, linked, pieces, expect, failures}'
{
  "animations": [
    0,
    1
  ],
  "frame": 0,
  "explains": 10,
  "explained": 10,
  "linked": 10,
  "pieces": 11,
  "expect": [
    0,
    0
  ],
  "failures": []
}
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-keeper-front.json --against-anime --json | jq -c '.rows[] | if . then [.section, .pair, .animations, .frame, .slot, .rules] else null end'
null
[13,824,[0,1],0,1,["mirror"]]
[14,848,[0,1],0,4,["flip"]]
[16,856,[0,1],0,5,["flip"]]
[92,832,[0,1],0,2,["flip"]]
[17,840,[0,1],0,3,["flip"]]
[18,888,[0,1],0,9,["flip"]]
[20,896,[0,1],0,10,["flip"]]
[11,904,[0,1],0,11,["flip"]]
[19,864,[0,1],0,6,["flip"]]
[21,872,[0,1],0,7,["flip"]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-keeper-front.json --against-anime --json | jq '{animations, frame, explains, explained, linked, pieces, expect, failures}'
{
  "animations": [
    0,
    1
  ],
  "frame": 0,
  "explains": 10,
  "explained": 10,
  "linked": 10,
  "pieces": 11,
  "expect": [
    0,
    0
  ],
  "failures": []
}
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-keeper-front.json --against-anime --json | jq -c '.rows[] | if . then [.section, .pair, .animations, .frame, .slot, .rules] else null end'
null
[13,824,[0,1],0,1,["plain"]]
[14,832,[0,1],0,2,["plain"]]
[16,840,[0,1],0,3,["plain"]]
[92,848,[0,1],0,4,["plain"]]
[17,856,[0,1],0,5,["plain"]]
[18,864,[0,1],0,6,["plain"]]
[20,872,[0,1],0,7,["plain"]]
[11,880,[0,1],0,8,["plain"]]
[19,888,[0,1],0,9,["plain"]]
[21,896,[0,1],0,10,["plain"]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-focus3-first.json --against-anime --json | jq '{animations, frame, explains, explained, linked, pieces, expect, failures}'
{
  "animations": [
    146
  ],
  "frame": 8,
  "explains": 10,
  "explained": 10,
  "linked": 10,
  "pieces": 11,
  "expect": [
    146,
    8
  ],
  "failures": []
}
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-focus3-first.json --against-anime --json | jq -c '.rows[] | if . then [.section, .pair, .animations, .frame, .slot, .rules] else null end'
null
[2,8828,[146],8,1,["plain"]]
[3,8836,[146],8,2,["plain"]]
[5,8844,[146],8,3,["plain"]]
[90,8852,[146],8,4,["plain"]]
[6,8860,[146],8,5,["plain"]]
[7,8868,[146],8,6,["plain"]]
[9,8876,[146],8,7,["plain"]]
[11,8884,[146],8,8,["plain"]]
[8,8892,[146],8,9,["plain"]]
[10,8900,[146],8,10,["plain"]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-focus2-first.json --against-anime --json | jq '{animations, frame, explains, explained, linked, pieces, expect, failures}'
{
  "animations": [
    134
  ],
  "frame": 9,
  "explains": 10,
  "explained": 10,
  "linked": 10,
  "pieces": 11,
  "expect": [
    134,
    9
  ],
  "failures": []
}
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-focus2-first.json --against-anime --json | jq -c '.rows[] | if . then [.section, .pair, .animations, .frame, .slot, .rules] else null end'
null
[2,89508,[134],9,1,["mirror"]]
[95,89532,[134],9,4,["flip"]]
[96,89540,[134],9,5,["flip"]]
[97,89516,[134],9,2,["flip"]]
[98,89524,[134],9,3,["flip"]]
[7,89572,[134],9,9,["flip"]]
[9,89580,[134],9,10,["flip"]]
[11,89588,[134],9,11,["flip"]]
[8,89548,[134],9,6,["flip"]]
[10,89556,[134],9,7,["flip"]]
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-focus3-first.json --against-anime --json | jq '{animations, frame, explains, explained, linked, pieces, expect, failures}'
{
  "animations": [
    4
  ],
  "frame": 9,
  "explains": 10,
  "explained": 10,
  "linked": 10,
  "pieces": 11,
  "expect": [
    4,
    9
  ],
  "failures": []
}
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py pose work/kits-oracle/anime/slot10-focus3-first.json --against-anime --json | jq -c '.rows[] | if . then [.section, .pair, .animations, .frame, .slot, .rules] else null end'
null
[2,17248,[4],9,1,["plain"]]
[95,17256,[4],9,2,["plain"]]
[96,17264,[4],9,3,["plain"]]
[93,17272,[4],9,4,["plain"]]
[98,17280,[4],9,5,["plain"]]
[7,17288,[4],9,6,["plain"]]
[9,17296,[4],9,7,["plain"]]
[11,17304,[4],9,8,["plain"]]
[8,17312,[4],9,9,["plain"]]
[10,17320,[4],9,10,["plain"]]
```

K1 e K2: o esperado é `ANIME_EXPECT` em `tools/kits/replay.py`, constante por (slot, foco), e o `kits_replay` o julga sobre as cinco poses. A planta muda a animação esperada e derruba as 50 peças explicadas com dado real:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check work/kits-oracle --quiet
kits_replay: 0 failure(s)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check work/kits-oracle --quiet --plant-anime
  FAIL  ANIME_EXPECT: anime/slot10-focus3-first.json: section 10 reads animation 4 frame 9, not 5 frame 9
kits_replay: 50 failure(s)
```

Gates na árvore de trabalho:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  330.80 sec
2/5 Test #19: kits_image .......................   Passed   26.42 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  239.66 sec
5/5 Test #22: kits_replay ......................   Passed   11.39 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
  RED    replay-anime-rule-ignored    kits/core/replay.py :: anime_piece
  RED    replay-anime-pair-slot       kits/core/replay.py :: anime_piece
  RED    replay-anime-pose-drops-pair kits/core/replay.py :: pose_piece
controls: 85 of 85 red
```

`$S` é o scratchpad da sessão; as capturas ali não são lidas por nada versionado.
- **Closed** — commit `5fc15802` (2026-10-18): feat(kits): read the ANIME.BIN pair in the replay capture and judge the pose against it
  - Files (`git show --name-status 5fc15802`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/14-medir-a-corrida-no-anime-bin-ponteiro-do-par-na.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/replay.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/replay.py`
    - `M tools/kits/selftest.py`
- **Reviewed** (2026-10-19) at `f064a839`: CORR-KRP-029, CORR-KRP-030
