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
