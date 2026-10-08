---
id: CORR-K3D-009
---

# CORR-K3D-009 — Faixa 99 a 104 ms não colada da ferramenta, e files da K3D-TASK-14 desatualizado

Origin: [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md)

## Problem

O docstring de `FRAME_LIMIT_MS` e o Log da [K3D-TASK-14](/docs/tasks/kits-3d/14-vista-rasterizador.md) dizem "99 to 104 ms", mas o bloco de
evidência do próprio Log, colado da mesma ferramenta, mostra 121 ms na figura 0 de
frente; o revisor mediu de 100 a 121 ms. À parte, o `files` da task ainda nomeia três
arquivos, e o commit `d4edbcc` toca também `tools/kits/core/api.py` (parâmetros novos
`order` e `skip_degenerate`), `tools/kits/selftest.py` e `docs/KITS-AJUSTES-3D.md`. O Log
cita os três, mas a declaração não foi atualizada.

## Evidência

```text
$ grep -n "99 to 104" tools/kits/ui_check.py
923:99 to 104 ms for TEX_00 front and back (`app.py --export-3d`); the limit
$ grep -n "121 ms" docs/tasks/kits-3d/14-vista-rasterizador.md
50:  ok    the 3D view is the core's drawing, pixel for pixel, ... figure 0 yaw 0 0 px off, 121 ms; ...
$ git show --stat d4edbcc | grep -E "api.py|selftest.py|KITS-AJUSTES"
 docs/KITS-AJUSTES-3D.md | 9 +-
 tools/kits/core/api.py | 12 ++-
 tools/kits/selftest.py | 29 +++----
```

## Root cause

Hipótese: a faixa foi escrita a partir de um subconjunto das corridas em vez de colada da
transcrição final do gate; o escopo cresceu para a fachada e o selftest e o `files` não
acompanhou.

## Fix

No docstring de `tools/kits/ui_check.py` e no Log, citar a faixa de uma corrida colada da
linha "seen" do juiz (por exemplo "100 to 121 ms"). Acrescentar os três arquivos com
`rite set K3D-TASK-14 --files ...`, ou justificá-los no Escopo da task.

## Arquivos a criar ou modificar

- tools/kits/ui_check.py
- docs/tasks/kits-3d/14-vista-rasterizador.md

## Verificação

```sh
grep -n "99 to 104" tools/kits/ui_check.py
```

Hoje casa; depois tem de sumir, ou casar com uma transcrição colada.

## Log de Execução
