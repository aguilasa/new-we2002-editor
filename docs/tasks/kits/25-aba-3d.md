---
id: KITS-TASK-25
---

# KITS-TASK-25 — Aba 3D: titular/suplente, jogador/goleiro, giro livre

## Goal

A aba 3D desenha a figura pela fachada; sem geometria fica desligada com a frase do motivo, e o 2D funciona igual.

## Arquivos a criar ou modificar

- `tools/kits/ui/*.py`
- `tools/kits/ui_check.py`
- `tools/kits/core/figure.py`, `tools/kits/core/api.py` — `api.FIGURE_POSE` e `api.FIGURE_TRIANGLES`, para a janela não importar o `looks`
- `tools/kits/selftest.py` — `TAB_NAMES` entre as constantes que não são texto de tela

## Done criteria

- [x] Captura das quatro combinações de uma tag do §1.1 que difere: titular ≠ suplente (digests no Log)
- [x] Sem `WE2002_LOOKS_IMAGE`, a aba aparece desligada com a frase (captura)
- [x] `kits_ui` estendido às quatro combinações, verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.2).

## Log de Execução

### 2026-10-03

Na máquina Linux, `:98` sem `-auth`; base `3df28e4`.

**O que entrou.** `ui/figure_view.py`: a figura desenhada por `QPainter` em software — cada triângulo (`api.FIGURE_TRIANGLES`, a diagonal do `looks`) pintado de trás para frente por um mapa afim do triângulo de textura para o de tela, recortado nele; câmera ortográfica, giro por arraste (`yaw`, `pitch`), e de frente por default (`yaw` 180: em 0 a figura mostra as costas, visto na primeira captura). Não OpenGL: o mesmo quadro no Windows e no Xvfb, que é o que o gate compara. A primeira captura saiu **de cabeça para baixo** — o `y` do modelo cresce para cima e o da tela para baixo —, e a projeção ganhou o sinal.

No `app.py`: a aba "3D" com conjunto (titular/suplente) e figura (jogador/goleiro); a figura vem de `api.figure(..., frame=api.FIGURE_POSE)`, desenhada só com a aba à mostra. A geometria (`find_geometry`) é o disco aberto quando a guarda do `looks` o aceita, senão `WE2002_LOOKS_IMAGE`; sem nenhum, a aba fica **desligada** e a linha de baixo da janela mostra a frase do núcleo (`3D off: …`). `--tab`, `--kit-set`, `--figure`, `--yaw`, `--pitch` no argparse; `--tab 3d` com a aba desligada sai **3**. Texto novo no catálogo, nas duas línguas (`tab_3d`, `kit_set`, `set_first`/`set_second` — titular/suplente —, `figure`, `figure_player`/`figure_keeper`, `figure_hint`, `figure_geometry`, `figure_off`).

O critério 1 — as quatro combinações do `TEX_00` (das 103 em que os conjuntos diferem nas imagens, §1.1), olhadas:

```
$ for c in "1 0" "2 0" "1 1" "2 1"; do set -- ${=c}; WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
    work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --tab 3d \
    --kit-set $1 --figure $2 --screenshot work/kits-3d-$1-$2.png >/dev/null; done; sha256sum work/kits-3d-?-?.png
f2f4809e75eaa4400beae23355d2e7701b6a9b21cd28a6de899354a6d1c0b5a2  work/kits-3d-1-0.png
b0202035f17166bcc56433b571841b165deed3b10646463e9ee874597727c705  work/kits-3d-1-1.png
7cc4e6779d1780d4c96a49d1b08c60e38a4cb96ca90e6b1f9aef6aaf66c6fc32  work/kits-3d-2-0.png
12e0835edf7270c9d3c03d0a91b7843c5bf258b876d632f21184d09503da6d00  work/kits-3d-2-1.png
```

(`kits-3d-<conjunto>-<figura>`.) Titular: camisa verde, meia verde; suplente: camisa branca. Goleiro titular cinza, suplente rosa. O digest do arquivo inteiro diferir não basta, e o gate não o usa: o combo do conjunto muda de texto entre as duas capturas.

O critério 2 — um TEX avulso (`/BIN/TEX_00.BIN` tirado pelo `tools/pes2/iso.py extract`) com a variável desligada:

```
$ env -u WE2002_LOOKS_IMAGE work/venv-looks/bin/python tools/kits/ui/app.py work/TEX_00.BIN --tab 3d --screenshot /tmp/x.png; echo exit $?
the 3D tab is off: 3D off: The 3D figure needs the Japanese disc for its geometry: set WE2002_LOOKS_IMAGE to its data track (.bin).
exit 3
$ env -u WE2002_LOOKS_IMAGE work/venv-looks/bin/python tools/kits/ui/app.py work/TEX_00.BIN --screenshot work/kits-3d-off.png
  wrote work/kits-3d-off.png, 980x640
```

Na captura, a aba "3D" cinza e a frase na última linha; o Plano desenhado como sempre.

O critério 3 — o `kits_ui` ganhou duas verificações e duas plantas:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    3D TEX_00: the four combinations draw a figure, and set 1 is not set 2 for either figure (set 1 fig 0 a8c1d8c41f8e, set 1 fig 1 03702f40ee6a, set 2 fig 0 07cec720d657, set 2 fig 1 ca30876e718d)
  ok    with no geometry disc the 3D tab is off with the sentence, and Plan is the same
        plant '3D set ignored': figure 0: set 2 draws the same figure as set 1; figure 1: set 2 draws the same figure as set 1
  ok    plant '3D set ignored' fails the 3D judge
        plant '3D tab never off': --tab 3d with no geometry: exit 0, …
  ok    plant '3D tab never off' fails the 3D off judge
kits_ui: 0 failure(s)
```

(Os digests do gate são das capturas da corrida dele, com caminho absoluto, e não os da lista acima.)

**Dois juízes que tiveram de ser apertados.** (1) A planta `3D set ignored` (`api.figure(self.kit, 1, …)`) **passou** na primeira versão, que comparava a captura inteira: o texto do combo `first`/`second` já bastava para a diferença. O juiz passou a comparar só dentro da vista 3D (`view_box`, a caixa da cor de fundo dela), e a planta ficou vermelha. (2) O juiz do "Plano igual" proibia diferença acima da linha de nota, e acusou 125 pixels: o rótulo da aba "3D" acinzentado (x 71–87, y 48–56). É a aba desligada aparecendo, então o juiz passou a **exigir** essa mudança, limitada a uma caixa de rótulo (`TAB_LABEL`), e nada mais.

Na HEAD entregue:

```
$ python3 tools/kits/selftest.py | grep -E 'controls red|kits_selftest:'
  ..... 23 of 23 controls red
kits_selftest: 0 failure(s)
$ ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed   61.15 sec
2/4 Test #19: kits_image .......................   Passed   26.74 sec
3/4 Test #20: kits_gen .........................   Passed    0.03 sec
4/4 Test #21: kits_ui ..........................   Passed   24.83 sec
100% tests passed, 0 tests failed out of 4
$ env -u WE2002_LOOKS_IMAGE ctest --test-dir build -R kits_ui
1/1 Test #21: kits_ui ..........................***Skipped   0.09 sec
```

A primeira corrida do selftest acusou `ui/app.py shows no text outside tr()  [(848, '3d')]` — o nome da aba numa comparação; virou a constante `TAB_NAMES`, posta entre as que não são texto de tela.

**Não medido:** se a orientação esquerda/direita da figura é a do jogo. A projeção não espelha x, e o confronto com o emulador é a fase 7 (KITS-TASK-27/28).
- **Closed** — commit `a47275a` (2026-10-03): feat(kits): the 3D tab -- set, figure, free turn, off with the core's sentence
  - Files (`git show --name-status a47275a`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/25-aba-3d.md`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `A tools/kits/ui/figure_view.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
