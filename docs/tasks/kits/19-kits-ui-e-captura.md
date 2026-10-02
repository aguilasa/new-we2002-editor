---
id: KITS-TASK-19
---

# KITS-TASK-19 — Gate `kits_ui` e a mesma captura no Windows e no Linux

## Goal

`kits_ui` julga os PNGs de fora, sem o código sob teste; a captura do mesmo estado sai igual nas duas plataformas.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tests/CMakeLists.txt`

## Done criteria

- [x] `ctest -R kits_ui` passa com venv e tela, e sai 77 sem eles
- [x] Controle: tirar o `setStyle("Fusion")` (ou a `QPalette` fixa) numa cópia derruba o `kits_ui`
- [x] Captura do mesmo estado no Windows e no Linux (`:98`), comparadas por comando versionado; diferença em pixels colada no Log

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4). O Linux é outra máquina: se não estiver à mão, a task fica bloqueada com o comando que a destrava, não fechada.

O que ficou decidido:

- **O juiz da aparência é a cor, contada no PNG.** Medido nesta task, sobre o estado do gate (`TEX_00`, bitmap de trabalho do 1º conjunto, paleta 2, zoom 3, zonas): a cor de janela da `QPalette` fixa, `#ececec`, cobre 22,8 % da captura e some sem `setPalette` (vem a do sistema, `#f0f0f0`); o painel da aba que o Fusion pinta a partir dela, `#ebebeb`, cobre 18,8 % e some sem `setStyle("Fusion")` (o estilo nativo o pinta de branco). O `kits_ui` exige as duas acima de 10 %.
- **Os dois controles moram no próprio gate:** o `ui_check.py` copia `tools/{kits,looks,pes2}` para um temporário, tira uma das duas linhas do `app.py` e exige que o juiz de estilo reprove a cópia. Planta que não casa uma vez só é falha, não vermelho.
- **A leitura sob o mouse entra no gate** (a [CORR-KITS-032](/docs/tasks/kits/CORR-KITS-032.md) deixou a asserção para esta task): `app.py --hover X,Y` em quatro pixels do `TEX_00` — frente da camisa, meia do goleiro, manga curta e a lacuna do torso — tem de dizer o índice e o RGB que o `cli.py export --work-bitmap` grava no PNG indexado daquele pixel, e a grade tem de marcar o mesmo índice. O PNG da CLI é lido pelo decodificador do próprio `ui_check.py`. A planta é o `app.py` lendo o pixel à direita.
- **`--compare A B`** é o comando versionado do critério 3. O caminho aberto aparece na barra de cima, então as duas capturas têm de abrir o disco pelo mesmo caminho relativo, a partir da raiz do repositório: medido aqui, o mesmo estado com o caminho absoluto em vez do relativo muda a cor de janela de 22,8 % para 23,1 %.

## Log de Execução

### 2026-10-02

O critério 1:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir $TEMP/build-kits08 -R kits_ui
1/1 Test #17: kits_ui ..........................   Passed   10.00 sec
$ env -u WE2002_LOOKS_IMAGE ctest --test-dir $TEMP/build-kits08 -R kits_ui
1/1 Test #17: kits_ui ..........................***Skipped   0.28 sec
$ python tools/kits/ui_check.py; echo $?
kits_ui: skipped -- WE2002_LOOKS_IMAGE is not set (the Japanese data track .bin)
77
$ cp tools/kits/ui_check.py $TEMP/nouv/ && WE2002_LOOKS_IMAGE=x python $TEMP/nouv/ui_check.py; echo $?
kits_ui: skipped -- no venv at work
env-looks (python -m venv work
env-looks; pip install PySide6)
77
```

O que o gate diz, verde, na versão entregue:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir $TEMP/build-kits08 -R kits_ui -V
  ok    the window comes up off the desktop and writes a picture
  ok    the picture shows something
  ok    the look is the fixed one: palette window colour 22.8 %, Fusion pane 18.8 %
  ok    the same state twice is the same picture (0 px differ)
  ok    another kit is another picture (301598 px, 48.1 %)
  ok    a tag the disc does not have exits 2 and writes nothing (exit 2)
  ok    the reading under the mouse names the index and colour cli.py export writes, at 4 point(s): (15, 10)=36, (100, 40)=91, (40, 70)=4, (5, 90)=0
  ok    a point off the image reads blank and exits 1 (exit 1)
        plant 'no Fusion': Fusion's tab pane #ebebeb covers 0.0 %, under 10 %
  ok    plant 'no Fusion' fails the style judge
        plant 'no fixed palette': the fixed palette's window colour #ececec covers 0.0 %, under 10 %; Fusion's tab pane #ebebeb covers 0.0 %, under 10 %
  ok    plant 'no fixed palette' fails the style judge
        plant 'readout one pixel right': (100, 40): 'índice 91' not in the readout 'x 100, y 40 · zona: socks · índice 90 · BGR555 0x0000 · RGB 0,0,0 · transparente'; (100, 40): the grid marks '90', not 91; (40, 70): 'índice 4' not in the readout 'x 40, y 70 · zona: short sleeve, left · índice 5 · BGR555 0x737b · RGB 222,222,231'; (40, 70)
  ok    plant 'readout one pixel right' fails the hover judge
kits_ui: 0 failure(s)
1/1 Test #17: kits_ui ..........................   Passed   17.59 sec
```

O critério 2 — a linha tirada da janela numa cópia da árvore em `work/kits-ui-plant/` (fora do git, e de onde o gate ainda acha o venv), e o gate inteiro, na versão entregue, rodado nela:

```
$ (app.setStyle("Fusion") trocado por pass em work/kits-ui-plant/tools/kits/ui/app.py)
$ python work/kits-ui-plant/tools/kits/ui_check.py      # exit 1
  FAIL  the look is the fixed one: palette window colour 22.1 %, Fusion pane 0.0 %
  FAIL  plant 'no Fusion'
kits_ui: 2 failure(s)
$ (o mesmo com app.setPalette(fixed_palette()) tirado)      # exit 1
  FAIL  the look is the fixed one: palette window colour 0.0 %, Fusion pane 0.0 %
  FAIL  plant 'no fixed palette'
kits_ui: 2 failure(s)
```

(O segundo `FAIL` de cada um é a planta do gate que não casa mais na cópia já plantada — falha, não vermelho falso.)

O critério 3 — a metade do Windows, e o comando contra si mesmo e contra outro kit:

```
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-windows.png
  wrote work/kits-ui-windows.png, 980x640                  # sha256 e973a8aa5991a7ff…
$ python tools/kits/ui_check.py --compare work/kits-ui-windows.png work/kits-ui-windows.png | tail -1
0 of 627200 pixels differ (0.00 %)
$ python tools/kits/ui_check.py --compare work/kits-ui-windows.png <o mesmo com --tag A4> | tail -1
300308 of 627200 pixels differ (47.88 %)
```

**Falta o Linux**, que é outra máquina: a captura do mesmo estado no `:98`, e o `--compare` das duas. A task fica bloqueada com o comando que a destrava. A captura do Windows não entra no git (`work/` é ignorado), e não precisa ser copiada: o `C:\` desta máquina aparece no Linux em `/media/ingmar/win/` ([LOOKS-AMBIENTE.md](/docs/LOOKS-AMBIENTE.md)), então `C:\github\new-we2002-editor\work\kits-ui-windows.png` é, lá, `/media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png` (sha256 `e973a8aa5991a7ff…`). No Linux, a partir da raiz do repositório:

```
DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin \
  --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux.png
python3 tools/kits/ui_check.py --compare \
  /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png
```

O disco tem de ser aberto pelo mesmo caminho relativo `roms/japanese-shift-jis.bin`: ele aparece na barra de cima da janela, e um caminho diferente muda pixels que não são de plataforma.
### 2026-10-02 (Linux)

A metade do Linux do critério 3, na máquina Linux, com o Xvfb `:98` subido sem `-auth` e a captura do Windows lida pelo `/media/ingmar/win`:

```
$ sha256sum /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png
e973a8aa5991a7ff258ae482ea199b054ad7f0d4338c918a79ca38830f80d288
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin \
    --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux.png
  wrote work/kits-ui-linux.png, 980x640
  window up, at -32000,-32000
$ python3 tools/kits/ui_check.py --compare \
    /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png work/kits-ui-linux.png
kits-ui-windows.png: 980x640, window colour 23.1 %, Fusion pane 18.8 %
kits-ui-linux.png: 980x640, window colour 22.9 %, Fusion pane 18.7 %
12224 of 627200 pixels differ (1.95 %)
$ python3 tools/kits/ui_check.py --compare work/kits-ui-linux.png work/kits-ui-linux.png | tail -1
0 of 627200 pixels differ (0.00 %)
```

Mesmo tamanho, mesma paleta e mesmo painel do Fusion nas duas. Onde estão os 12.224 pixels, visto no diff do ImageMagick (`compare A B -compose src diff.png`): só em texto — rótulos, botões, combos e a barra de baixo —, com o desenho do bitmap, a grade, as zonas e o painel de paleta sem diferença. A família é a mesma nos dois (`Arial`, que o `fc-match Arial` acha aqui), em 13 px; o que muda é a rasterização da fonte, que desloca a largura de cada rótulo e empurra o que vem depois na linha (o combo de times, os checkboxes). Não é estilo nem paleta.

O `kits_ui` rodado no Linux achou um controle cego. Na versão de `19a3e733`:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
        plant 'no Fusion': judge passed
  FAIL  plant 'no Fusion' fails the style judge
kits_ui: 1 failure(s)
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python -c "from PySide6 import QtWidgets as W; a=W.QApplication([]); print(W.QStyleFactory.keys(), a.style().name())"
['Windows', 'Fusion'] fusion
```

O juiz não é cego: no Linux o estilo default do Qt **já é** Fusion, então tirar o `setStyle("Fusion")` não muda a janela, e a planta não planta nada. A planta passou a trocar a linha por `app.setStyle("Windows")` — o outro estilo que o Qt desenha ele mesmo nas duas plataformas — em vez de tirá-la. Depois disso, no Linux:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
        plant 'no Fusion': Fusion's tab pane #ebebeb covers 0.0 %, under 10 %
  ok    plant 'no Fusion' fails the style judge
  ok    plant 'no fixed palette' fails the style judge
kits_ui: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_ui
1/1 Test #21: kits_ui ..........................   Passed    8.03 sec
$ env -u WE2002_LOOKS_IMAGE ctest --test-dir build -R kits_ui
1/1 Test #21: kits_ui ..........................***Skipped   0.09 sec
```

A planta nova não foi rodada no Windows: lá a corrida de `19a3e733` viu a antiga ficar vermelha, e a nova troca o estilo nativo por um que o próprio Qt desenha, que é o mesmo código nas duas. Fica para a próxima corrida do gate no Windows conferir.

- **blocked** (2026-10-02): criterion 3 needs the Linux machine (:98): criteria 1-2 done in 19a3e733 (kits_ui passes, 77 without venv/image, the Fusion and QPalette plants red); the Windows capture is work/kits-ui-windows.png (sha256 e973a8aa5991a7ff..). Unblock on Linux, from the repo root, with that PNG copied to work/: DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux.png && python3 tools/kits/ui_check.py --compare work/kits-ui-windows.png work/kits-ui-linux.png
- **pending** (2026-10-02): Linux machine at hand: :98 up, venv-looks present, Windows capture readable at /media/ingmar/win (sha256 e973a8aa5991a7ff..)
- **Closed** — commit `f85aa85` (2026-10-02): test(kits): Linux half of KITS-TASK-19 -- the Windows/Linux capture compared, and a Fusion plant that bites on Linux
  - Files (`git show --name-status f85aa85`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/19-kits-ui-e-captura.md`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-02) at `05f246b`: CORR-KITS-033, CORR-KITS-034
