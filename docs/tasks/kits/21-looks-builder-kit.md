---
id: KITS-TASK-21
---

# KITS-TASK-21 — `scene.Builder(kit=...)` no `looks`, com `TEX_A4` de default

## Goal

O `scene.Builder` aceita qualquer das 105 tags; sem o argumento desenha como hoje.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/selftest.py`
- `tools/looks/controls.py` — o controle mora no catálogo, que o `selftest.py` planta inteiro

## Done criteria

- [x] `ctest -R looks` com as quatro (`looks_selftest`, `looks_image`, `looks_ui`, `looks_live`) verdes, ou *skipped* só pela falta declarada, **antes e depois** — as duas transcrições no Log
- [x] Um self-check do `looks` constrói com uma tag que não é a `A4` e confere que o banco de textura usado é o dela
- [x] Controle: o default trocado numa cópia derruba o self-check que garante `TEX_A4`

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2). Toca `tools/looks/`, projeto arquivado (§6). Mudança aditiva.

## Log de Execução

### 2026-10-02

Na máquina Linux, com o `:98`, o venv, os dois discos e os dois states:

```
export DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
       WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
```

**Antes**, na HEAD `fb68c7c`, sem nada mexido:

```
$ ctest --test-dir build -R looks
1/4 Test #14: looks_selftest ...................   Passed   13.22 sec
2/4 Test #15: looks_image ......................   Passed    2.16 sec
3/4 Test #16: looks_ui .........................   Passed  237.75 sec
4/4 Test #17: looks_live .......................   Passed   11.23 sec
100% tests passed, 0 tests failed out of 4
```

**O que mudou.** `scene.Builder(image_path, figure, frame, kit=layout.KIT_ON_SCREEN)`: a tag passa por `layout.kit_path`, que recusa tag sem digest **antes** de abrir o disco, e é ela que o construtor lê e repassa ao `build`. Sem o argumento, `TEX_A4` como antes.

O critério 2, em dois lugares:

- no `scene.self_check` (sem disco — é o que o `looks_selftest` roda): um disco de mentira devolve cada arquivo como o próprio nome, e o `build` do módulo é trocado por um que anota a tag. O `Builder` sem argumento lê `/BIN/TEX_A4.BIN` e constrói com `"A4"`; o `Builder(kit="00")` lê `/BIN/TEX_00.BIN`, não lê o `TEX_A4` e constrói com `"00"`; `kit="ZZ"` é recusado com `WrongDisc`;
- no `scene.py --check-image` (o `looks_image`), contra o disco: o `Builder(kit="00")` constrói a tupla de referência, e todo container de onde a cena tirou textura é conferido.

```
$ python3 tools/looks/scene.py --check-image | grep Builder
      Builder(kit='00'): surfaces from ['/BIN/DAT2D.BIN', '/BIN/TEX_00.BIN']
```

O critério 3 — o controle `scene-builder-default-kit` no catálogo do `controls.py`, que troca o default por `"00"`:

```
$ python3 tools/looks/controls.py --only scene-builder-default-kit
  RED    scene-builder-default-kit  scene.py :: Builder.__init__
controls: 1 of 1 red (1 substitution)
$ (a mesma troca numa cópia da árvore, e o self-check do scene nela)
  FAIL  with no kit named, the Builder wears TEX_A4, the screen's kit  '00'
  FAIL  and builds with the tag it was given  ['00', '00']
scene.py: 2 failure(s)
```

**Depois:**

```
$ ctest --test-dir build -R looks
1/4 Test #14: looks_selftest ...................   Passed   13.57 sec
2/4 Test #15: looks_image ......................   Passed    2.34 sec
3/4 Test #16: looks_ui .........................   Passed  231.19 sec
4/4 Test #17: looks_live .......................   Passed   12.13 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/looks/selftest.py | grep -E 'controls red|looks_selftest:'
  ..... 110 of 110 controls red
looks_selftest: 0 failure(s)
$ ctest --test-dir build -R looks_image -V | grep scene
   ok    scene      exit 0   scene --check-image: ok
```

O `selftest.py` não precisou mudar: ele já planta o catálogo inteiro, e o controle novo entrou nele pelo `controls.py`, que passou a constar dos arquivos da task.
- **Closed** — commit `e6bf293` (2026-10-02): feat(looks): scene.Builder(kit=...), TEX_A4 by default
  - Files (`git show --name-status e6bf293`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/21-looks-builder-kit.md`
    - `M tools/looks/controls.py`
    - `M tools/looks/scene.py`
