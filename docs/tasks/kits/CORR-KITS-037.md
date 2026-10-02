---
id: CORR-KITS-037
---

# CORR-KITS-037 — Cobrir no gate o kit que Builder.walk_build passa ao build()

Origin: [KITS-TASK-21](/docs/tasks/kits/21-looks-builder-kit.md)

## Problem

`Builder.walk_build` (`tools/looks/scene.py:499-506`) passa `self.kit` ao `build()`, como `Builder.build` faz — e é por ele que a janela `LOOKS SET` desenha (`tools/looks/ui/looks_set.py:324`, `378`). Nenhuma verificação cobre esse caminho: trocar ali `self.kit` por `layout.KIT_ON_SCREEN` numa cópia deixa verdes o self-check e o `--check-image`. Só `Builder.build` está coberto — a mesma planta lá derruba os dois. Metade dos caminhos de desenho do `Builder` pode largar o argumento `kit` em silêncio.

## Evidência

```text
$ S=$(mktemp -d); git archive HEAD | tar -x -C $S; cd $S
$ python3 - <<'PY'
p='tools/looks/scene.py'; s=open(p).read()
old="""                self._unposed = {text: build(self._data, values, self.figure,
                                                 None, self.kit)}"""
assert old in s
s=s.replace(old, old.replace("self.kit","layout.KIT_ON_SCREEN"))
open(p,'w').write(s)
PY
$ python3 tools/looks/scene.py --check | tail -1
scene.py: 0 failure(s)
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/looks/scene.py --check-image | tail -1
scene --check-image: ok
```

Controle: a mesma troca dentro de `Builder.build` dá `FAIL and builds with the tag it was given ['A4', 'A4']` e `scene --check-image: 2 problem(s)`.

## Root cause

`_builder_kit` em `scene.py` exercita só `default.build`/`other.build`, nunca `walk_build`; o `--check-image` também só constrói por `.build`.

## Fix

Em `_builder_kit` (`tools/looks/scene.py`), chamar também `other.walk_build(assembly.CORPUS_REFERENCE, <visita>, <slot>)` com o `build` capturado e afirmar a tag. Em `tools/looks/controls.py`, acrescentar um controle que troca `None, self.kit)}` do `walk_build` por `None, layout.KIT_ON_SCREEN)}` e exige o vermelho.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/controls.py`

## Verificação

A planta acima no `walk_build` tem de deixar `python3 tools/looks/scene.py --check` vermelho, e `python3 tools/looks/controls.py --only <controle novo>` tem de imprimir RED. `ctest -R looks` continua verde.

## Log de Execução
