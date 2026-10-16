---
id: CORR-KRP-025
---

# CORR-KRP-025 — Altura da vista 3D depende do comprimento do caminho da imagem (940x409 contra 940x379)

Origin: [KRP-TASK-22](/docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

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
