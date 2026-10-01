---
id: CORR-KITS-017
---

# CORR-KITS-017 — Run self-checks of looks modules kits uses indirectly

Origin: [KITS-TASK-08](/docs/tasks/kits/08-selftest-e-ctest.md)

## Problem

O `looks_modules_imported()` de `tools/kits/selftest.py` varre só as linhas `import X` de dentro de `tools/kits`. Os módulos do `looks` que o kits alcança através desses imports têm `self_check` próprio, mas o `kits_selftest` nunca os roda: são `modelfile`, `skin`, `pieces`, `oracle` e `screen` (o `assembly` importa o `skin` na linha 103; `atlas`, `texture` e `assembly` importam o `modelfile`). Uma quebra num deles deixa o `kits_selftest` verde, o que desfaz o propósito do §6 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md): "para a quebra aparecer aqui".

## Evidência

```text
$ T=<scratch>; git -C C:/github/new-we2002-editor archive HEAD tools/kits tools/looks tools/pes2 src/core data | tar -x -C $T
$ python plant.py   # em $T: em tools/looks/skin.py troca "out |= set(field.primitives or ())" por "out = set(...)" (o skin-union-of-one-field do catálogo do looks)
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant --quiet   # em $T
..... 8 looks self-check(s): assembly, atlas, harness, iso_source, layout, looks, section, texture
kits_selftest: 0 failure(s)        exit=0
$ cd $T/tools/looks && python -c "import skin; print(skin.self_check())"
skin.py: 2 failure(s)
```

Com o `modelfile-list-order` do looks plantado o resultado é o mesmo: `kits_selftest` sai 0, enquanto `modelfile.self_check` levanta `AssertionError`.

## Root cause

A lista são os imports diretos de `tools/kits`, não o fecho transitivo deles dentro de `tools/looks`. As Notas da task escolheram isso de propósito ("varre tools/kits/**/*.py").

## Fix

Em `looks_modules_imported` (`tools/kits/selftest.py`), seguir os imports recursivamente pelos `tools/looks/*.py` encontrados, inclusive imports dentro de função. Acrescentar em `tools/kits/controls.py` um controle que plante o `skin-union-of-one-field` ou o `modelfile-list-order` e espere "FAIL  looks skin.self_check()" ou o equivalente do `modelfile`.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`

## Verificação

Os passos de plantio acima, e então `python tools/kits/selftest.py --no-plant --quiet` na cópia. Hoje sai 0; depois tem de sair 1, com uma linha FAIL nomeando o `skin`.

## Log de Execução

### Reprodução (HEAD `201c7915`)

O `rite reproduce --scratch` não montou `$T`; refeita à mão, com a árvore de `HEAD` extraída para uma pasta do scratchpad e o plantio por `sed`:

```text
$ git archive HEAD tools/kits tools/looks tools/pes2 src/core data | tar -x -C $T
$ sed -i 's/out |= set(field.primitives or ())/out = set(field.primitives or ())/' $T/tools/looks/skin.py
$ cd $T && env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant --quiet | tail -3; echo "exit ${PIPESTATUS[0]}"
rules: 0 failure(s)
controls: not planted (--no-plant)
kits_selftest: 0 failure(s)
exit 0
$ cd $T/tools/looks && python -c "import skin; print(skin.self_check())" | tail -1
2
```

REPRODUCED. Causa raiz confirmada: `looks_modules_imported` só olhava os imports diretos de `tools/kits`.

### O que foi feito

- `tools/kits/selftest.py`: `looks_modules_reached()` segue os imports pelos `tools/looks/*.py` até fechar — o regex já pegava import indentado, de dentro de função —, e `looks_modules_imported()` fica com os alcançados que têm `self_check`. Um nome que é módulo do próprio kits (`cli`) não conta como do looks. Passou de 8 para **21** módulos (`anime`, `assembly`, `atlas`, `cli`, `confront`, `glyphs`, `harness`, `iso_source`, `layout`, `looks`, `modelfile`, `oracle`, `pieces`, `scene`, `screen`, `section`, `skin`, `sprites`, `stature`, `texture`, `ui_check`); o `kits_selftest` continua em ~3 s.
- `tools/kits/controls.py`: controle `looks-skin-union`, o `skin-union-of-one-field` do catálogo do `looks`, que espera `FAIL  looks skin.self_check()`.

### Verificação

Os passos da Reprodução sobre a árvore corrigida:

```text
$ cd $T && env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant --quiet | grep -E "FAIL|looks self-check|kits_selftest"; echo "exit ${PIPESTATUS[0]}"
  FAIL  the three colour fields move fourteen of section 24's eighteen  got 2: [8, 13]
  FAIL  and four are left when they are taken out: 3, 6, 10 and 11  got [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17]
  FAIL  looks skin.self_check() reports no failure  failures=2
  ..... 21 looks self-check(s): anime, assembly, atlas, cli, confront, glyphs, harness, iso_source, layout, looks, modelfile, oracle, pieces, scene, screen, section, skin, sprites, stature, texture, ui_check
kits_selftest: 1 failure(s)
exit 1
$ python tools/kits/controls.py; echo "exit $?"
  base   unplanted sandbox            selftest exit 0
  RED    tex-shape-referee            kits/core/tex.py :: EXPECTED_SHAPE
  RED    tex-flag-double              kits/core/tex.py :: plain_size
  RED    tex-size-check               kits/core/tex.py :: read_kit
  RED    tex-stream-control-literal   kits/core/tex.py :: module constant
  RED    tex-header-extent            kits/core/tex.py :: declared_extent
  RED    source-form2-tail            kits/core/source.py :: _sector_data
  RED    source-next-file             kits/core/source.py :: _slot_end
  RED    core-prints                  kits/core/errors.py :: KitsError
  RED    looks-layout-empty-slot      looks/layout.py :: the pointer-list walk
  RED    looks-skin-union             looks/skin.py :: the union of a field's primitives
controls: 10 of 10 red
exit 0
```
- **Closed** — commit `fd819f77` (2026-10-01): fix(kits): run the self-checks of every looks module the kits code reaches
  - Files (`git show --name-status fd819f77`):
    - `M docs/tasks/kits/CORR-KITS-017.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
