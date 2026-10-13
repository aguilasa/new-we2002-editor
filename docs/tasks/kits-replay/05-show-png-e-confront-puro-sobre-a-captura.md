---
id: KRP-TASK-05
---

# KRP-TASK-05 — show --png e confront puro sobre a captura

## Goal

`replay.py show <captura> --png out.png [--section S|--box]` põe o recorte do frame buffer do jogo ao lado da figura desenhada pelo `core/raster` na pose capturada, sem Qt; `replay.py confront <captura> [--section S]` dá, por seção, o pixel do jogo contra o texel puro e o modulado.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - `confront --tab` (KRP-TASK-06)
  - qualquer mudança em `core/raster.py`

## Done criteria

- [x] `replay.py confront work/kits-oracle/replay-9-3.json --section 90 --json`: `far` puro 2,27 contra modulado 2,55, como o [item 1](/docs/KITS-REPLAYS-9-10.md#1)
- [x] `replay.py show work/kits-oracle/replay-9.json --png <scratch>/show.png` escreve um PNG com as duas metades; o Log traz o tamanho e o digest, e o PNG é enviado ao usuário
- [x] planta: o `show` desenhando a figura sem a pose capturada fica vermelho no `controls.py`
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

O PNG é para olhar; o número de fidelidade é o do `confront`.

## Log de Execução

### 2026-10-13

`core/replay.py` ganhou `pose_picture(figure, index, texture, box, only=None)`: cada seção do
MODEL.BIN da figura passa pela matriz da sua peça e pela projeção capturadas
(`pose_project`, o RTPS), e entra no `core/raster.draw` já em coordenada de tela (x e y negados,
profundidade `-z`), com um `FIT` de lado igual à caixa — então a figura cai **nos mesmos pixels**
do frame buffer que a captura guardou. A textura de cada seção é a página e a CLUT que os quads do
jogo para ela amostram (`section_source`), quando a captura as guardou; senão a seção sai sem
textura (cinza do raster). `core/raster.py` não mudou. `tools/kits/replay.py` ganhou `show` (PNG
RGB em escala 4, o jogo à esquerda, o desenho à direita; `--section S` desenha uma seção, `--box`
contorna a caixa da peça nas duas metades) e `confront` (por seção, o `colour_confront`).

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-oracle/replay-9-3.json --section 90 --json
(campo sections[0]) "far": 2.265486725663717, "far_shaded": 2.5486725663716814, "pixels": 113, "section": 90,
"game": [10.247787610619469, 7.823008849557522, 8.070796460176991],
"texel": [10.29203539823009, 6.929203539823009, 8.08849557522124],
"shaded": [9.29203539823009, 5.929203539823009, 7.345132743362832]
```

2,27 puro contra 2,55 modulado, os do item 1 do relatório (e a linha `90:` do `oracle.py --replay 9
--focus 3`: `113 px … (far 2.27) … (far 2.55)`).

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py show work/kits-oracle/replay-9.json --png <scratch>/show.png --json
(campos) {'width': 872, 'height': 476, 'sha256': 'c512eee7e0715fd4d57217813e7739857bcc517c2803d8acfd6f6b53edc94728', 'drawn': 2574, 'box': None, 'schema': 'kits-replay/1'}
$ stat -c '%s bytes' <scratch>/show.png
22107 bytes
```

872×476: as duas metades de 107×119 pixels do frame buffer, mais 4 de vão, em escala 4. O PNG foi
enviado ao usuário, junto com `replay-9-3 --box`, em que a caixa do torso do Bokšić cai no mesmo
lugar nas duas metades. Olhando: corpo, pernas e braços sobrepõem; a cabeça e a pele saem cinzas
(páginas que a captura não guardou), e o painel das costas do Bokšić sai com os texels da UV do
próprio modelo, não com o "11" que o jogo pinta ali — o PNG é para olhar, o número é o do `confront`.

Planta `replay-show-unposed` (`core/replay.py :: pose_picture`: a matriz da peça vira identidade e
translação zero), contra o caso novo do selftest — um quadrado de lado 20 a z 1000 com H 1000 tem
de cobrir o meio 21×21 de uma caixa 41×41 e nada nos cantos:

```
$ python3 tools/kits/controls.py --only replay-show-unposed
  RED    replay-show-unposed          kits/core/replay.py :: pose_picture
(selftest --no-plant da cópia plantada, sai 1)
  FAIL  show draws the figure in its captured pose, on the frame buffer's pixels  41x41, 0 px painted, first []
```

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  248.77 sec
2/5 Test #19: kits_image .......................   Passed   27.29 sec
3/5 Test #20: kits_gen .........................   Passed    0.02 sec
4/5 Test #21: kits_ui ..........................   Passed  212.35 sec
5/5 Test #22: kits_replay ......................   Passed    7.74 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 63 of 63 red
```
