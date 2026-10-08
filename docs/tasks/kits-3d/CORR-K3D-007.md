---
id: CORR-K3D-007
---

# CORR-K3D-007 — Limite de tempo de quadro do raster_judge nunca visto vermelho

Origin: [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md)

## Problem

O `raster_judge` da [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md) afirma `frame_ms > FRAME_LIMIT_MS` (`tools/kits/ui_check.py:962`),
mas a única planta `RASTER` do catálogo `PLANTS` (linha 233) volta a vista ao desenho
antigo, e essa fica vermelha pela diferença de pixel, não pelo tempo. Nem o Log nem
planta versionada mostram o ramo de tempo falhando. Pela regra "verificador sem vermelho
visto não é gate", a asserção de tempo não é gate ainda.

## Evidência

```text
$ grep -n "RASTER\|FRAME_LIMIT" tools/kits/ui_check.py
164:    BACK, RASTER = ("style", "hover", "3D", "3D off", "selector", "diagnosis",
233:    ("the view back to the old drawing", RASTER,
917:RASTER_TURNS = ((0, 0), (0, 180), (1, 0), (1, 180))
920:FRAME_LIMIT_MS = 400.0
...
962:        if frame_ms > FRAME_LIMIT_MS:
```

O revisor mostrou que o ramo consegue falhar baixando a constante para 50 em processo
(`bad ['figure 0 yaw 0: one frame took 107 ms, over 50', ...]`), sem tocar o repositório.
Isso é medição avulsa, não planta versionada.

## Root cause

Hipótese: tomou-se a planta de pixel como cobertura do juiz inteiro, mas o tempo é uma
asserção separada.

## Fix

Acrescentar a `PLANTS` em `tools/kits/ui_check.py` uma entrada `RASTER` que torne o
quadro medido lento — por exemplo um `time.sleep(0.5)` plantado antes de
`frame_ms = ...` no ramo `--export-3d` de `tools/kits/ui/app.py` —, exigir que a falha
traga "one frame took", e colar esse vermelho no Log.

## Arquivos a criar ou modificar

- tools/kits/ui_check.py
- tools/kits/ui/app.py

## Verificação

```sh
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep -n "one frame took"
```

Hoje não casa nada; depois, mostra a linha vermelha da planta.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. O `grep` da Evidência mostrava uma única planta
  `RASTER`, a de pixel.
- `ui_check.py`: juiz novo `FRAME` ("frame time") e a planta "a slow frame of the view", que põe
  `time.sleep(0.5)` antes do `self.frame_ms = ...` de `figure_view.py`. O juiz roda o
  `raster_judge` e só conta as falhas que trazem "one frame took", então a planta só fica vermelha
  pelo ramo de tempo. Vermelho visto:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
        plant 'a slow frame of the view': figure 0 yaw 0: one frame took 610 ms, over 400; figure 0 yaw 180: one frame took 613 ms, over 400; figure 1 yaw 0: one frame took 619 ms, over 400; figure 1 yaw 180: one frame took 647 ms, over 400
  ok    plant 'a slow frame of the view' fails the frame time judge
kits_ui: 0 failure(s)
```

- O `app.py` ficou fora: a planta cai em `figure_view.py`, porque o tempo passou a vir do
  `picture()` da vista (CORR-K3D-008). `controls.py`: `controls: 32 of 32 red`.
