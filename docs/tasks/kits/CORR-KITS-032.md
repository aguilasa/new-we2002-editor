---
id: CORR-KITS-032
---

# CORR-KITS-032 — Version the mouse-readout probe behind the Log's readout line

Origin: [KITS-TASK-18](/docs/tasks/kits/18-janela-minima.md)

## Problem

O Log da KITS-TASK-18 cita uma leitura do mouse ("x 15, y 10 · zona: shirt front · índice 36 · BGR555 0x29e8 · RGB 66,123,82", com a grade marcando 36) e diz que ela veio de "um QMouseEvent sintético sobre (15,10)". Nenhuma ferramenta versionada nem opção do `app.py` produz essa linha: `--screenshot`, `--export` e `--walk` não passam pelo `on_pixel`. O número é verdadeiro — o revisor o refez com um script próprio —, mas saiu de sonda descartável, o que a regra "sonda que produziu um número vira opção de uma ferramenta versionada" proíbe, e nada no repositório confere o caminho de leitura de zona, índice e cor.

## Evidência

```text
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --hover 15,10
app.py: error: unrecognized arguments: --hover 15,10
$ grep -cE 'QMouseEvent|--hover' tools/kits/ui/app.py
0
```

Sonda do revisor, sem versão (`app.Window()` estacionada fora da tela, `open_path` da imagem japonesa, `select_tag("00")` e `canvas.hovered.emit(15, 10)`):

```text
x 15, y 10 · zona: shirt front · índice 36 · BGR555 0x29e8 · RGB 66,123,82 marked 36
```

## Root cause

A leitura foi conferida à mão durante a task, e a sonda nunca virou opção do `app.py`.

## Fix

Acrescentar ao `tools/kits/ui/app.py` uma opção `--hover X,Y` que mande um `QMouseEvent` de verdade ao canvas no pixel (X,Y) da imagem, no zoom corrente, e imprima `window.readout.text()` e `palette_grid.marked`. Recitar a linha do Log a partir desse comando. O `kits_ui` da KITS-TASK-19 pode então afirmar sobre ela.

## Arquivos a criar ou modificar

- `tools/kits/ui/app.py`
- `docs/tasks/kits/18-janela-minima.md`

## Verificação

```text
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --hover 15,10
```

Hoje dá erro do argparse; depois imprime a leitura citada e "36", com a janela fora da tela.

## Log de Execução

### 2026-10-02

Reprodução (`rite reproduce --all --cycle kits`, triagem inline): `app.py: error: unrecognized arguments: --hover 15,10` (exit 2) e `grep -cE 'QMouseEvent|--hover'` dá `0` — REPRODUCED.

Feito: `tools/kits/ui/app.py` ganhou `--hover X,Y`, que manda um `QMouseEvent` (`MouseMove`, centro do pixel no zoom corrente) ao canvas pelo `sendEvent`, passa pelo `mouseMoveEvent` e pelo `on_pixel`, e imprime `window.readout.text()` e `palette_grid.marked`; leitura em branco sai 1. O Log da KITS-TASK-18 recita a linha a partir dele.

Verificação, e o vermelho (ponto fora da imagem):

```
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --hover 15,10      # exit 0
  readout: x 15, y 10 · zona: shirt front · índice 36 · BGR555 0x29e8 · RGB 66,123,82
  marked: 36
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --hover 15,10 --zoom 8      # exit 0
  readout: x 15, y 10 · zona: shirt front · índice 36 · BGR555 0x29e8 · RGB 66,123,82
  marked: 36
$ work/venv-looks/Scripts/python.exe tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --hover 9999,0      # exit 1
  readout: (blank)
  marked: -1
```

A asserção sobre esta linha num gate é da KITS-TASK-19 (`kits_ui`).
