---
id: K3D-TASK-06
---

# K3D-TASK-06 — Fechamento da fase 2

## Goal

A fase 2 conferida na HEAD.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [x] as verificações da Fase 2 do perfil, cada uma com comando e saída no Log
- [x] `rite check --cycle kits-3d`: 0 erros
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

Conferência na HEAD `7df641b` (2026-10-07), com `export DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`.

**Fase 2, item 1 — a contagem por ângulo vista vermelha com lacuna plantada:**

```
$ python3 tools/kits/controls.py --only holes-alpha-ignored
  RED    holes-alpha-ignored          kits/core/figure.py :: count_holes
controls: 1 of 1 red
$ python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00 --negative | grep negative
negative: figure 0, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
negative: figure 1, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
```

**Fase 2, item 2 — nenhum texel entra sem regra medida, o único preenchimento novo é o
`BACK_COPY`.** Na fase, o código que escreve pixel em `core/` e `ui/` é só isto:

```
$ git diff 448ea7b..HEAD -- tools/kits/core tools/kits/ui | grep -E "^\+.*(rgba\[|panel\[|bytearray)"
+                    opaque = surface.rgba[(ty * surface.width + tx) * 4 + 3] != 0
+        rgba = bytearray(surface.rgba)
+                rgba[(y * surface.width + x) * 4 + 3] = 0
```

A primeira linha é leitura (a contagem). As outras duas são do `planted_gap`, que só a opção
`--negative` do `cli.py holes` chama: ele faz a lacuna do controle e não entra no desenho. A cópia
das costas reaproveita o `numbered_indices`, que já existia (§4.7). Dois chamadores novos, os dois
com `number=None`, o que quer dizer só `BACK_COPY`:

```
$ grep -rn "planted_gap\|numbered_scene(\|numbered_indices(" tools/kits/*.py tools/kits/ui/*.py tools/kits/core/*.py | grep -v "def "
tools/kits/core/figure.py:108:    return numbered_scene(built, kit, kit_set, figure, None)
tools/kits/core/figure.py:161:        indices = numbered_indices(indices, width, figure, None)
tools/kits/core/figure.py:425:        indices = numbered_indices(indices, width, figure, number)
tools/kits/cli.py:1237:        planted = api.planted_gap(drawn, kit, figure, HOLE_ZONE)
(e os de selftest/ui_check/api, que são teste, planta e fachada)
```

**Fase 2, item 3, e os critérios de ctest, controles e check:**

```
$ ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed  128.44 sec
2/4 Test #19: kits_image .......................   Passed   29.32 sec
3/4 Test #20: kits_gen .........................   Passed    0.03 sec
4/4 Test #21: kits_ui ..........................   Passed   97.28 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 30 of 30 red
$ rite check --cycle kits-3d --json
  "errors": 0,
  "warnings": 0,
```
- **Closed** — commit `206f204` (2026-10-07): docs(kits): record the phase 2 checks of kits-3d at HEAD
  - Files (`git show --name-status 206f204`):
    - `M docs/tasks/kits-3d/06-fechamento-fase-2.md`
