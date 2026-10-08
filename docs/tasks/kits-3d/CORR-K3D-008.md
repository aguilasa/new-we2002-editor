---
id: CORR-K3D-008
---

# CORR-K3D-008 — Tempo de quadro medido numa chamada à parte, não no desenho da vista

Origin: [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md)

## Problem

Na [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md), o quadro cronometrado é uma segunda chamada a `api.draw_figure` feita no ramo
`--export-3d` de `app.py`. O caminho da própria vista (`FigureView.picture()` →
`composed()` → `drawImage`) grava `self.frame_ms`, mas ninguém lê esse atributo. Uma
lentidão em `picture()` ou `composed()` deixaria o gate verde, e `FigureView.frame_ms` é
código morto.

## Evidência

```text
$ grep -rn "frame_ms" tools/kits | grep -v ui_check.py
tools/kits/ui/figure_view.py:52:        self.frame_ms = None             # how long the last picture took to draw
tools/kits/ui/figure_view.py:76:        self.frame_ms = (time.perf_counter() - started) * 1000.0
tools/kits/ui/app.py:1082:        frame_ms = (time.perf_counter() - started) * 1000.0
tools/kits/ui/app.py:1088:              % (at.x(), at.y(), view.width(), view.height(), view.yaw, view.pitch, frame_ms))
```

## Root cause

Hipótese: `--export-3d` chama a fachada direto para a imagem exportada não depender do
`paintEvent`, e a cronometragem foi junto.

## Fix

No `--export-3d` de `tools/kits/ui/app.py`, imprimir o `frame_ms` da vista depois de uma
pintura forçada (ou cronometrar `view.picture()`), mantendo a chamada à fachada só para o
PNG. Ou então remover `FigureView.frame_ms`.

## Arquivos a criar ou modificar

- tools/kits/ui/app.py
- tools/kits/ui/figure_view.py

## Verificação

```sh
grep -n "view.frame_ms\|figure_view.frame_ms" tools/kits/ui/app.py
```

Hoje vazio; depois tem de casar — ou o atributo tem de sumir de `figure_view.py`.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. `frame_ms` da vista só era escrito, nunca lido.
- `figure_view.py`: `picture()` cronometra desenho e composição. `app.py --export-3d`: o PNG
  continua sendo `api.draw_figure` chamado à parte (é o que deixa o juiz de pixel ver uma vista que
  desenha outra coisa), e o tempo impresso é o `view.frame_ms` depois de `view.picture()`. O
  `import time` do `app.py` ficou sem uso e saiu.
- Verificação: `grep -n "view.frame_ms" tools/kits/ui/app.py` → `1084:        frame_ms = view.frame_ms`.
  `ui_check.py`: `  ok    the 3D view is the core's drawing, pixel for pixel, …` com 106 a 111 ms, `kits_ui: 0 failure(s)`.
  `selftest.py`: `kits_selftest: 0 failure(s)`.
- **Closed** — commit `794d9db` (2026-10-08): fix(kits): time the 3D view's own picture in --export-3d
  - Files (`git show --name-status 794d9db`):
    - `M docs/tasks/kits-3d/CORR-K3D-008.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/figure_view.py`
