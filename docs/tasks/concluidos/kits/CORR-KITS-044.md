---
id: CORR-KITS-044
---

# CORR-KITS-044 — Cobrir no gate o TEX avulso que tira a geometria da variável de ambiente

Origin: [KITS-TASK-24](/docs/tasks/concluidos/kits/24-figura.md)

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

### 2026-10-03

Reproduzido na HEAD `7efd399`:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep -c 'lone TEX'
0
```

Conserto, dos dois lados:

- **Sem disco** (`kits_selftest`): com `WE2002_LOOKS_IMAGE` num nome inventado e nenhum caminho, `figure.geometry_path_for()` tem de devolver a variável, e um caminho dado tem de ganhar dela. A chamada é protegida, para a planta dar a linha `FAIL` e não um traceback.
- **Com disco** (`kits_image`, em `_figure_checks`): os bytes do `TEX_00` gravados num `TEX_00.BIN` temporário, aberto por `api.open_source` (tem de dar `kind == "tex"`) e desenhado por `api.figure(kit, 1, 0)` sem caminho de geometria; tem de sair uma `Scene` com superfície de kit.
- **Controle** `geometry-env-ignored` em `tools/kits/controls.py`: `path = path or os.environ.get(GEOMETRY_ENV)` vira `path = path`.

```
$ python3 tools/kits/selftest.py --no-plant | grep -E 'lone TEX|path given'
  ok    lone TEX: with no geometry path, the figure takes WE2002_LOOKS_IMAGE
  ok    and a path given wins over it
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep -E 'lone TEX|figure:'
  ok    lone TEX: opened as a TEX, its figure built from WE2002_LOOKS_IMAGE, 1 kit surface(s)
figure: 0 failure(s)
$ python3 tools/kits/controls.py --only geometry-env-ignored | tail -2
  RED    geometry-env-ignored         kits/core/figure.py :: geometry_path_for
controls: 1 of 1 red
```

A mesma planta numa cópia `git archive HEAD tools` com o `selftest.py` novo, do lado do disco:

```
  FAIL  build the lone TEX's figure: raised NoGeometry: The 3D figure needs the Japanese disc for its geometry: set WE2002_LOOKS_IMAGE to its data track (.bin).
  FAIL  lone TEX: opened as a TEX, its figure built from WE2002_LOOKS_IMAGE, 0 kit surface(s)  kind 'tex'
figure: 2 failure(s)
```

O primeiro controle escrito saiu `GREEN ... red, but not on 'FAIL  lone TEX: ...'`: sem a proteção, a planta fazia `geometry_path_for()` levantar dentro do argumento do `ok`, e o selftest caía antes de imprimir a linha. Daí a proteção.

Gates:

```
$ python3 tools/kits/selftest.py | grep -E 'controls red|kits_selftest:'
  ..... 23 of 23 controls red
kits_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `9ca3330` (2026-10-03): test(kits): cover the lone TEX that takes its geometry from the variable
  - Files (`git show --name-status 9ca3330`):
    - `M docs/tasks/kits/CORR-KITS-044.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
