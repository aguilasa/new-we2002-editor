---
id: CORR-KITS-044
---

# CORR-KITS-044 — Cobrir no gate o TEX avulso que tira a geometria da variável de ambiente

Origin: [KITS-TASK-24](/docs/tasks/kits/24-figura.md)

## Problem

O Objetivo da KITS-TASK-24 diz que, com um TEX avulso, a geometria vem de `WE2002_LOOKS_IMAGE`. Nenhum gate confere esse caminho positivo: o `kits_selftest` só confere a recusa com a variável ausente, e o `kits_image` só chama `palette_swap` sobre kits da ROM, passando geometria explícita. O caminho funciona rodado à mão.

## Evidência

```text
$ python3 tools/pes2/iso.py extract roms/japanese-shift-jis.bin /BIN/TEX_00.BIN -o $S/TEX_00.BIN
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 - <<X
import sys; sys.path.insert(0,"tools/kits"); from core import api
s = api.open_source("$S/TEX_00.BIN"); print(s.kind)
k = s.kit(None)
sc = api.figure(k, 2, 1); print(type(sc).__name__, len(sc.surfaces))
X
tex
Scene 6
$ grep -n "api.figure(" tools/kits/selftest.py
238:                  lambda: api.figure(kit, 1, 0), "needs the Japanese disc", kind=api.NoGeometry)
```

## Root cause

Hipótese: os selftests cobrem a recusa e a troca, mas não o default de geometria por variável de ambiente com TEX avulso.

## Fix

Em `_figure_checks` (`tools/kits/selftest.py`), abrir um TEX avulso (extraído da imagem) e afirmar que `api.figure(kit, 1, 0)` devolve uma `Scene` com superfície de kit quando só `WE2002_LOOKS_IMAGE` está definido. Em `tools/kits/controls.py`, plantar um controle em que `geometry_path_for` ignora a variável.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep -c 'lone TEX'
```

Dá 0 hoje; pelo menos 1 depois do conserto, e o controle novo fica RED.

## Log de Execução
