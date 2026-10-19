---
id: CORR-KRP-025
---

# CORR-KRP-025 — Altura da vista 3D depende do comprimento do caminho da imagem (940x409 contra 940x379)

Origin: [KRP-TASK-22](/docs/tasks/concluidos/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

## Problem

O defeito é anterior à KRP-TASK-22, mas a evidência dela depende dele. A altura da vista 3D muda com
o comprimento do caminho da imagem, e com ela mudam os números do `confront --tab` e uma checagem do
`kits_ui`:

- com caminho relativo ou do tamanho do repositório, a vista tem 940x409;
- com um caminho absoluto longo, tem 940x379, também em ca147a8e.

Sob o caminho longo, o `confront --tab --player` dá 0,746/0,635/0,501/0,413/0,728, em vez dos
0,748/0,636/0,500/0,414/0,730 do Log. O `kits_ui` falha em "with no geometry disc the 3D tab is off
… Plan is the same" ("278719 pixel(s) differ above the note rows, in a 962x532 box"). A mesma HEAD
passa com um `WE2002_LOOKS_IMAGE` do tamanho do repositório.

A §3.3 agora diz que "a altura não muda", o que só vale para caminho curto.

## Evidência

Numa cópia `git archive 34809e3f`, com `$PWD` de uns 150 caracteres:

```text
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d /tmp/x.png | grep "3d view"
  3d view: at 20,169, 940x409, ...
$ work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d /tmp/x.png | grep "3d view"
  3d view: at 20,169, 940x379, ...
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=<caminho de 150 caracteres>/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep FAIL
  FAIL  with no geometry disc the 3D tab is off with the sentence, and Plan is the same
```

Numa cópia `git archive ca147a8e`, a mesma corrida com caminho longo também dá `940x379`.

## Root cause

(Hipótese, não provada.) Um rótulo da janela com o caminho inteiro da imagem quebra linha quando o
caminho é longo e tira uns 30 px da vista.

## Fix

Em `tools/kits/ui/app.py`, elidir o rótulo do caminho (`QFontMetrics.elidedText`, ou sem quebra de
linha) para que o layout não dependa do comprimento do caminho.

## Arquivos a criar ou modificar

- `tools/kits/ui/app.py`

## Verificação

De uma cópia sob um caminho de 150 caracteres ou mais:

```sh
work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d /tmp/x.png | grep "940x409"
```

Hoje falha. Depois do conserto tem de imprimir a linha.

## Log de Execução

Reproduzido em 7486416c, no `:98`, com a árvore do repositório (caminho de 81 caracteres para a imagem) e
com um diretório de rascunho de caminho longo, `L=<scratchpad>/krp025-a-deliberately-long-directory-name-to-push-the-image-path-past-one-hundred-fifty-chars`,
cujo `roms/japanese-shift-jis.bin` é symlink para o do repositório (240 caracteres):

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d $S/x.png | grep "3d view"
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 102 ms
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $L/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d $S/x.png | grep "3d view"
  3d view: at 20,169, 940x379, yaw 180, pitch 0, frame 120 ms
```

**Causa raiz, medida.** A hipótese estava certa no mecanismo e errada no rótulo: não é o
`path_label` do topo (ele já tinha política horizontal `Ignored` e fica em 23 px nos dois casos), e
sim os **dois** rótulos de baixo, `status` e `figure_note`, ambos com `setWordWrap(True)` e ambos
carregando o caminho da imagem (`/BIN/TEX_22.BIN on <caminho>, 30772 bytes` e `3D geometry:
<caminho>`). Com o caminho longo cada um quebra numa segunda linha, 15 px cada, e os 30 px saem da
vista 3D, que é o único item elástico da aba. Medido com uma sonda que abre a janela do mesmo jeito
que o `main()` (980x640, tag 22, aba 3D) e lê a altura de cada rótulo depois do layout:

A sonda inteira (`probe.py`, rodada de dentro de uma árvore `git archive`; o campo que ela chama
de `lines` é o comprimento do texto, não o número de linhas):

```python
import sys
sys.path.insert(0, "tools/kits/ui"); sys.path.insert(0, "tools/kits")
import app as A
from PySide6 import QtWidgets
qa = QtWidgets.QApplication([])
A.apply_style(qa)
w = A.Window(); w.resize(980, 640); A.park(w, False)
w.open_path(sys.argv[1]); w.select_tag(22); w.tabs.setCurrentIndex(1)
for _ in range(20): qa.processEvents()
for n in ("status", "figure_note", "path_label"):
    l = getattr(w, n); print("  %s: height %d, lines %r" % (n, l.height(), len(l.text())))
print("  3d view %dx%d" % (w.figure_view.width(), w.figure_view.height()))
```

Rerodada no `:98` em 2026-10-16, na HEAD `7486416c` (cópia `git archive HEAD tools`) e na árvore com
o conserto, com o caminho do repositório (81 caracteres) e com o de 240 (`$L`):

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python probe.py $PWD/roms/japanese-shift-jis.bin   # HEAD
  status: height 15, lines 113
  figure_note: height 15, lines 94
  path_label: height 23, lines 81
  3d view 940x409
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python probe.py $L/roms/japanese-shift-jis.bin   # HEAD
  status: height 30, lines 272
  figure_note: height 30, lines 253
  path_label: height 23, lines 240
  3d view 940x379
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python probe.py $PWD/roms/japanese-shift-jis.bin   # com o conserto
  status: height 15, lines 113
  figure_note: height 15, lines 94
  path_label: height 23, lines 81
  3d view 940x409
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python probe.py $L/roms/japanese-shift-jis.bin   # com o conserto
  status: height 15, lines 272
  figure_note: height 15, lines 253
  path_label: height 23, lines 240
  3d view 940x409
```

**Conserto.** `tools/kits/ui/app.py` ganha `OneLineLabel`, um `QLabel` sem quebra de linha, com
política `Ignored` na horizontal e `Fixed` na vertical, que desenha o texto elidido no meio
(`QFontMetrics.elidedText`, `ElideMiddle`) e guarda o texto inteiro em `text()` e no tooltip. O
`status` e o `figure_note` passam a ser `OneLineLabel`. Quem lê `window.status.text()` (a linha
impressa do `--export-3d`, o `could not open`) continua recebendo o texto inteiro; só a pintura
corta. Conferido na captura da janela com o caminho de 240: as duas linhas de baixo saem numa linha
cada, com `…` no meio e o nome do arquivo à direita.

Depois do conserto, a vista tem a mesma altura com os três comprimentos:

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d $S/x.png | grep "3d view"
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 110 ms
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d $S/x.png | grep "3d view"
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 110 ms
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $L/roms/japanese-shift-jis.bin --tag 22 --tab 3d --export-3d $S/x.png | grep "3d view"
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 105 ms
```

A sonda, com o caminho de 240 e o conserto, dá a última corrida do bloco acima.

O `kits_ui` passa com os dois comprimentos, inclusive a checagem que falhava com o caminho longo:

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$L/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep -E "no geometry disc|failure"
  ok    with no geometry disc the 3D tab is off with the sentence, and Plan is the same
kits_ui: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep -E "no geometry disc|failure"
  ok    with no geometry disc the 3D tab is off with the sentence, and Plan is the same
kits_ui: 0 failure(s)
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
$ python3 tools/kits/controls.py | tail -1
controls: 81 of 81 red
```

O `ctest -R kits` completo do perfil não foi rodado nesta corrida; o `kits_ui` e o `kits_selftest`
acima são dois dos alvos dele.
- **Closed** — commit `14c44501` (2026-10-16): fix(kits): status and geometry note stay one line, so the 3D view height no longer depends on the image path
  - Files (`git show --name-status 14c44501`):
    - `M docs/tasks/kits-replay/CORR-KRP-025.md`
    - `M tools/kits/ui/app.py`
