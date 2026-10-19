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

### 2026-10-19

As duas sondas da KRP-TASK-14 viraram opção do `tools/kits/replay.py`:

- `replay.py anime-ram <state.sav>...` lê a RAM de cada save state (`savestate.SaveState(...).ram`),
  compara byte a byte a janela em `layout.ANIME_BASE` com o `ANIME.BIN` inteiro (`anime.read`, pelo
  `iso_source.open_disc` de `WE2002_LOOKS_IMAGE`, o mesmo `read_anime` do `pose --against-anime`) e a
  palavra em `layout.ANIME_BUILD` com `ANIME_BUILD_WORD`, e sai 1 se qualquer state falhar.
- `replay.py pose A --same-as B` compara as duas poses peça por peça, em ordem, nos campos
  `SAME_POSE_FIELDS` (seção, rotação, translação); peça diferente ou contagem diferente é falha. O par
  e a câmera que a recaptura acrescenta não entram, porque a pose antiga não os tem.

**De onde vem a palavra esperada.** `ANIME_BUILD_WORD` não é número lido do replay: é o `jal
0x8003D4BC` (`RotMatrix`) que a docstring de `layout.ANIME_BUILD` e a de `anime.rotation` registram
desde o ciclo `looks`, codificado (opcode 3 e os 26 bits de palavra do alvo) — `0x0C00F52F`. A mesma
palavra está nas duas cópias mestras da `LOOKS SET`, `work/looks-states/SLPM-87056_1.sav` e `_2.sav`,
e o próprio `anime-ram` sobre elas é quem mostra isso (abaixo).

Uma ressalva medida: a sonda não separa state de replay de state de outra tela. Os da `LOOKS SET`
passam, e os slots `3` e `8` de `work/kits-states/` também (transcrição abaixo) — o `ANIME.BIN`
fica residente. Por isso o vermelho é por controle plantado, não por "outro slot de state". O
vermelho com dado real fica no `--same-as`: a pose do goleiro do slot 9 contra a do slot 10.

A §5.1 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#5.1) e a docstring de `pose_capture` no
`tools/kits/oracle.py` passaram a citar os dois comandos. O `selftest.py` ganhou
`_replay_anime_ram_checks`, sobre uma RAM sintética de 2 MiB com `anime._synthetic()` na base, e o
`controls.py` três controles: `replay-anime-ram-base-shifted` (base um byte adiante),
`replay-anime-ram-word-unjudged` (palavra impressa e não comparada) e `replay-same-pose-section-only`
(`SAME_POSE_FIELDS` só com a seção). Cada controle exige a linha `FAIL` da asserção que diz cobrir.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py anime-ram work/kits-states/SLPM-87056_9.sav work/kits-states/SLPM-87056_10.sav; echo "exit $?"
work/kits-states/SLPM-87056_9.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
work/kits-states/SLPM-87056_10.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
exit 0
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py anime-ram work/looks-states/SLPM-87056_1.sav work/looks-states/SLPM-87056_2.sav; echo "exit $?"
work/looks-states/SLPM-87056_1.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
work/looks-states/SLPM-87056_2.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
exit 0
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py anime-ram work/kits-states/SLPM-87056_3.sav work/kits-states/SLPM-87056_8.sav; echo "exit $?"
work/kits-states/SLPM-87056_3.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
work/kits-states/SLPM-87056_8.sav: 396804 of 396804 bytes of ANIME.BIN at ANIME_BASE 0x8017EE00; word 0x0C00F52F at ANIME_BUILD 0x80011EF0 (expected 0x0C00F52F)
exit 0
$ for f in slot9-keeper-front slot10-keeper-front slot9-focus3-first slot10-focus2-first slot10-focus3-first; do python3 tools/kits/replay.py pose work/kits-oracle/anime/$f.json --same-as work/kits-pose/$f.json; echo "exit $?"; done
work/kits-oracle/anime/slot9-keeper-front.json against work/kits-pose/slot9-keeper-front.json: 11 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
exit 0
work/kits-oracle/anime/slot10-keeper-front.json against work/kits-pose/slot10-keeper-front.json: 11 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
exit 0
work/kits-oracle/anime/slot9-focus3-first.json against work/kits-pose/slot9-focus3-first.json: 11 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
exit 0
work/kits-oracle/anime/slot10-focus2-first.json against work/kits-pose/slot10-focus2-first.json: 11 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
exit 0
work/kits-oracle/anime/slot10-focus3-first.json against work/kits-pose/slot10-focus3-first.json: 11 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
exit 0
$ python3 tools/kits/replay.py pose work/kits-oracle/anime/slot9-keeper-front.json --same-as work/kits-pose/slot10-keeper-front.json; echo "exit $?"
work/kits-oracle/anime/slot9-keeper-front.json against work/kits-pose/slot10-keeper-front.json: 0 of 11 piece(s) the same in section, rotation, translation (11 against 11 piece(s))
  FAIL  piece 0 (section 34) differs in rotation, translation
  FAIL  piece 1 (section 13) differs in rotation, translation
  FAIL  piece 2 (section 14) differs in rotation, translation
  FAIL  piece 3 (section 16) differs in rotation, translation
  FAIL  piece 4 (section 92) differs in rotation, translation
  FAIL  piece 5 (section 17) differs in rotation, translation
  FAIL  piece 6 (section 18) differs in rotation, translation
  FAIL  piece 7 (section 20) differs in rotation, translation
  FAIL  piece 8 (section 11) differs in rotation, translation
  FAIL  piece 9 (section 19) differs in rotation, translation
  FAIL  piece 10 (section 21) differs in rotation, translation
exit 1
$ python3 tools/kits/controls.py --only replay-anime-ram-base-shifted
  base   unplanted sandbox            selftest exit 0
  RED    replay-anime-ram-base-shifted kits/replay.py :: anime_ram_report
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-anime-ram-word-unjudged
  base   unplanted sandbox            selftest exit 0
  RED    replay-anime-ram-word-unjudged kits/replay.py :: anime_ram_report
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only replay-same-pose-section-only
  base   unplanted sandbox            selftest exit 0
  RED    replay-same-pose-section-only kits/replay.py :: module constant
controls: 1 of 1 red
```
