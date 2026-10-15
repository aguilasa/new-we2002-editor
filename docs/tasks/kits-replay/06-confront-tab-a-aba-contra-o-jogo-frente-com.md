---
id: KRP-TASK-06
---

# KRP-TASK-06 — confront --tab: a aba contra o jogo, frente com frente e costas com costas

## Goal

`replay.py confront <captura> --tab` sobe o `ui/app.py --export-3d` com a figura que a captura diz (figura, faixa, manga, número) e compara a aba com o jogo por histograma, frente com frente e costas com costas, fechando a lacuna da [CORR-K3D-034](/docs/tasks/concluidos/kits-3d/CORR-K3D-034.md). É a métrica de antes e depois das fases 3 a 7.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/confront.py` (reuso de `histogram`/`intersection`)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - fora do git: as capturas giradas de frente dos focos de linha, feitas com `replay.py capture --turn` (KRP-TASK-07)
- Out:
  - afirmar limite de histograma
  - mudar o desenho da aba

## Done criteria

- [x] `replay.py confront <captura> --tab --json` nas cinco figuras de perto (Marcos 9 e 10, Bokšić 9 e 10, Balaban 10) dá `front` e `back` comparados com a mesma vista do jogo; os dez números colados no Log, ao lado dos do [item 5](/docs/KITS-REPLAYS-9-10.md#5)
- [x] planta: comparar a frente da aba com as costas do jogo fica vermelha no `controls.py`
- [x] (não se aplicou: as duas cópias mestras existem — `test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav` sai 0) sem uma das cópias mestras: `rite mark KRP-TASK-06 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Depende da 07 porque a frente de um jogador de linha só existe na captura girada. A aba sobe no `:98`.

## Log de Execução

### 2026-10-15

A comparação "frente com frente" pedia os pixels do jogo **dos dois lados**, e a captura só
guardava o frame buffer da primeira (`buffer`). `replay_capture` passou a ler também o da captura
girada (`back_buffer`, pelo mesmo `frame_buffer` sob a caixa da figura seguida), e as cinco figuras
foram capturadas de novo com giro, em `work/kits-replay/tab/` (as da KRP-TASK-07 ficaram
intocadas). `replay.py confront <captura> --tab` pareia os lados por `game_side`: no replay como
salvo a primeira captura é a **frente** do goleiro; atrás de um jogador ela é as **costas** dele, e
a frente é a girada. A aba sobe pelo `ui/app.py --export-3d` (o venv da looks, `:98`) com o que a
captura diz — kit pela paleta amostrada, figura, faixa, manga longa no slot 10 e número do
`REPLAY_EXPECT` — e as duas fotos são comparadas pelo `histogram`/`intersection`/`restrict` do
`confront.py`, que não mudou. Registra; não afirma limite.

Capturas, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin
WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`:

```
$ python3 tools/kits/replay.py capture --slot 9 --turn R1 --out work/kits-replay/tab
  capture kept at work/kits-replay/tab/replay-9-R1.json (schema v1, sha256 845bbda3dc6857066aa39a326f284413a33eea5c8701c44961aeccc625a19781)
$ python3 tools/kits/replay.py capture --slot 10 --turn R1 --out work/kits-replay/tab
  capture kept at work/kits-replay/tab/replay-10-R1.json (schema v1, sha256 98504ddbde4e1003757b74efb5f0e7e7cac36079b11af063c41bde38b7a5471b)
$ python3 tools/kits/replay.py capture --slot 9 --focus 3 --turn R1 --out work/kits-replay/tab
  capture kept at work/kits-replay/tab/replay-9-3-R1.json (schema v1, sha256 e775c5a5bcf9bf27143a4739a796d3db5c1c4b400e11f76f293304664f79a949)
$ python3 tools/kits/replay.py capture --slot 10 --focus 3 --turn R1 --out work/kits-replay/tab
  capture kept at work/kits-replay/tab/replay-10-3-R1.json (schema v1, sha256 4de9296e6269e212b75b2901557a8b4527563341ba49f2fcece8b23f6596844d)
$ python3 tools/kits/replay.py capture --slot 10 --focus 2 --turn R1 --out work/kits-replay/tab
  capture kept at work/kits-replay/tab/replay-10-2-R1.json (schema v1, sha256 94a10535f9cb8da188fb2bf05bdef831dac70d04e5a2bb9d274b44b22a7165ea)
```

As cinco saem 0 (logs em `work/krp06/`, de 11:39 a 12:03).

O confronto, cada uma com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`:

```
$ python3 tools/kits/replay.py confront work/kits-replay/tab/replay-<f>.json --tab --json
(schema; tab: tag, figura, faixa, manga longa, número | lado da aba <- captura do jogo, px, interseção / sobre as cores da aba)
9-R1 kits-replay/1 tag 41 fig 1 armband True long False num 1 | back<-back 7381 px 0.403/0.720 front<-front 4440 px 0.501/0.670
10-R1 kits-replay/1 tag 41 fig 1 armband True long False num 1 | back<-back 4642 px 0.557/0.739 front<-front 4746 px 0.499/0.677
9-3-R1 kits-replay/1 tag 22 fig 0 armband True long False num 11 | back<-front 3520 px 0.406/0.666 front<-back 3200 px 0.439/0.612
10-3-R1 kits-replay/1 tag 22 fig 0 armband True long True num 11 | back<-front 3117 px 0.413/0.625 front<-back 3538 px 0.362/0.556
10-2-R1 kits-replay/1 tag 22 fig 0 armband False long True num 20 | back<-front 2777 px 0.393/0.569 front<-back 3401 px 0.326/0.476
```

Ao lado do [item 5](/docs/KITS-REPLAYS-9-10.md#5), que comparava as duas vistas da aba com **um**
lado do jogo:

| Figura | Item 5, costas | Item 5, frente | Agora, costas com costas | Agora, frente com frente |
|---|---|---|---|---|
| Marcos, slot 9 | 0,548 | 0,501 | **0,403** | 0,501 |
| Marcos, slot 10 | 0,544 | 0,499 | **0,557** | 0,499 |
| Bokšić, slot 9 | 0,406 | 0,365 | 0,406 | **0,439** |
| Bokšić, slot 10 | 0,413 | 0,385 | 0,413 | **0,362** |
| Balaban, slot 10 | 0,393 | 0,375 | 0,393 | **0,326** |

Os números que já eram do mesmo lado repetem (frente do goleiro; costas dos jogadores de linha,
cuja primeira captura é as costas): é a mesma aba contra os mesmos pixels. Os em negrito são novos:
a costa do goleiro e a frente dos jogadores de linha, que antes eram comparadas com o lado oposto
do jogo. As costas do Marcos no slot 9 pegam 7.381 px, contra 4.440 da frente: a caixa da figura
girada abarca mais quadro, e o número é registrado assim.

Planta `replay-tab-sides-crossed` (`replay.py :: game_side` devolve o próprio lado):

```
$ python3 tools/kits/controls.py --only replay-tab-sides-crossed
  RED    replay-tab-sides-crossed     kits/replay.py :: game_side
(selftest --no-plant da cópia plantada, sai 1)
  FAIL  confront --tab compares the tab's front with the game's front, back with back  {(0, 'front'): 'front', (0, 'back'): 'back', (3, 'front'): 'front', (3, 'back'): 'back'}
```

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  281.31 sec
2/5 Test #19: kits_image .......................   Passed   27.84 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  214.24 sec
5/5 Test #22: kits_replay ......................   Passed    7.76 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 69 of 69 red
```
- **Closed** — commit `91f81ee2` (2026-10-15): feat(kits): confront --tab, the tab against the game side by side
  - Files (`git show --name-status 91f81ee2`):
    - `M docs/tasks/kits-replay/06-confront-tab-a-aba-contra-o-jogo-frente-com.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/replay.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/replay.py`, `tools/kits/confront.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-15) at `d24d2c43`: CORR-KRP-010, CORR-KRP-011, CORR-KRP-012, CORR-KRP-013, CORR-KRP-014
