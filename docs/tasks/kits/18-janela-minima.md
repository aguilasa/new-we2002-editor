---
id: KITS-TASK-18
---

# KITS-TASK-18 — Janela mínima: Abrir, combobox de tags, aba Plano, estilo Fusion fixo

## Goal

A janela abre ROM ou TEX por um só "Abrir…"; com ROM mostra o combobox (tags, com nome onde já se sabe); a aba Plano tem imagem, paleta, zoom, xadrez, grade, zonas, leitura sob o mouse e Exportar PNG. Fusion, `QPalette` fixa, fonte em pixels, layouts do Qt.

## Arquivos a criar ou modificar

- `tools/kits/ui/app.py`
- `tools/kits/ui/*.py`
- `tools/kits/core/api.py` — `WORK_PALETTE`, `UNIFORM_OF_SET`, `SLEEVES_OF_SET`: que imagem e que paleta cada conjunto e figura usam, que a janela precisava e só o `flat.py` sabia
- `tools/kits/selftest.py` — a regra de fachada do §3.1 passa a valer para `ui/`, com PySide6 permitido só lá
- `tools/kits/controls.py` — o controle `ui-imports-core`

## Done criteria

- [x] `grep -rnE '^(from|import) ' tools/kits/ui/` só mostra PySide6, stdlib e `core.api`
- [x] `work/venv-looks/Scripts/python.exe tools/kits/ui/app.py <rom> --screenshot <png>` grava a captura sem janela visível (fora da tela no Windows)
- [x] Uma opção `--tag`/`--image`/`--palette` percorre as 105 tags sem exceção (contagem no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4).

O que ficou decidido:

- **Um arquivo só, `ui/app.py`.** O critério 1 é o `grep` dos imports ao pé da letra; um módulo irmão (`import canvas`) seria import que não é PySide6, stdlib nem `core.api`.
- **Seletores:** "Imagem" lista os dois bitmaps de trabalho (`work1`, `work2`) e as imagens do `api.GAME_PAIRS`; "Paleta" lista só as que o jogo usa com a imagem escolhida. O árbitro fica fora pelo mesmo motivo do `GAME_PAIRS` (§4.5).
- **Grade 16×16 é a paleta**, ao lado da imagem, com o índice sob o mouse marcado. **Zonas** desenha `ZONES` (rosa) e `GAPS` (azul) sobre o bitmap de trabalho e sobre uniforme e mangas, deslocadas pela metade que cada um ocupa; na bandeira o mapa não vale e a caixa fica desligada.
- **O combobox mostra a tag, e o nome do time só onde `TeamEntry.tag` já o sabe** — hoje nenhum, porque é a §4.2 (KITS-TASK-30).
- **Estilo:** Fusion, `QPalette` clara definida no código (`COLOURS`), fonte `Arial`/`Liberation Sans`/`DejaVu Sans` a 13 px. Textos de tela em português, como o plano os nomeia.
- **`--walk`** percorre tag × imagem × paleta pelos próprios seletores da janela; `--plant TAG` tira o kit daquela tag no meio, e a contagem tem de ver.

## Log de Execução

### 2026-10-02

O critério 1:

```
$ grep -rnE '^(from|import) ' tools/kits/ui/
tools/kits/ui/app.py:27:from __future__ import annotations
tools/kits/ui/app.py:29:import argparse
tools/kits/ui/app.py:30:import os
tools/kits/ui/app.py:31:import sys
tools/kits/ui/app.py:35:from core import api  # noqa: E402
tools/kits/ui/app.py:36:from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402
$ python tools/kits/selftest.py --no-plant | grep "ui/"
  ok    ui/ imports only PySide6, core.api and the standard library (section 3.1)
$ python tools/kits/controls.py --only ui-imports-core
  RED    ui-imports-core              kits/ui/app.py :: module imports
```

O critério 2 — ROM e TEX avulso, fora da tela:

```
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --zones --screenshot <tmp>/k18.png      # exit 0
  wrote <tmp>/k18.png, 980x640
  TEX_00 · imagem bitmap de trabalho, 1º conjunto · paleta player palette, first set · /BIN/TEX_00.BIN on roms/japanese-shift-jis.bin, 29944 bytes
  window up, at -32000,-32000
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py <tmp>/TEX_A4.BIN --image 8 --export <tmp>/flag.png --screenshot <tmp>/k18tex.png      # exit 0
  TEX avulso · imagem flag · paleta flag palette · exportado: <tmp>/flag.png
  window up, at -32000,-32000
```

(`TEX_A4.BIN` tirado do disco por `MSYS_NO_PATHCONV=1 python tools/pes2/iso.py extract roms/japanese-shift-jis.bin /BIN/TEX_A4.BIN -o <tmp>/TEX_A4.BIN`; o PNG exportado é 128×64 RGBA.) As duas capturas foram olhadas: imagem com xadrez, zonas sobre o bitmap, a grade da paleta à direita.

O critério 3 e o seu vermelho:

```
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --walk      # exit 0
walked 105 tag(s): 1365 picture(s) drawn, 0 kit(s) refused, 0 exception(s)
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --walk --plant A4      # exit 1
  EXCEPTION  A4: RuntimeError: nothing drawn for 'work1' / 2
walked 105 tag(s): 1352 picture(s) drawn, 0 kit(s) refused, 1 exception(s)
```

1365 = 105 × 13 (dois bitmaps de trabalho × duas paletas, quatro imagens de conjunto × duas, a bandeira × uma).

A leitura sob o mouse, por um `QMouseEvent` sintético sobre (15,10) do `TEX_00`: `x 15, y 10 · zona: shirt front · índice 36 · BGR555 0x29e8 · RGB 66,123,82`, e a grade marca o 36.

O gate `kits_ui` e a captura igual no Linux são a KITS-TASK-19.
- **Closed** — commit `45ebcd04` (2026-10-02): feat(kits): the minimal window: open ROM or TEX, tag combobox, Plan tab, fixed Fusion look
  - Files (`git show --name-status 45ebcd04`):
    - `M docs/tasks/kits/18-janela-minima.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/selftest.py`
    - `A tools/kits/ui/app.py`
