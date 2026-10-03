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

### 2026-10-02

Reproduzido na HEAD `37a934d`, numa cópia `git archive HEAD`. O `old` da Evidência tem indentação a mais e não casa (`AssertionError`); a planta na linha real (`scene.py:506`) casa uma vez:

```
$ sed -i 's/^                                             None, self.kit)}$/                                             None, layout.KIT_ON_SCREEN)}/' tools/looks/scene.py
$ python3 tools/looks/scene.py --check | tail -1
scene.py: 0 failure(s)
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/looks/scene.py --check-image | tail -1
scene --check-image: ok
```

Conserto: `_builder_kit` chama também `walk_build` nos dois `Builder`, com um `build` capturado que anota o kit e para com uma exceção sentinela (depois da chamada vem a pose, que o disco de nomes não tem), e afirma `['A4', '00']`. Controle novo `scene-builder-walk-kit` em `tools/looks/controls.py`, com a planta acima.

```
$ python3 tools/looks/scene.py --check | grep -E 'walks with|failure'
  ok    and walks with it too, the path the LOOKS SET window draws by
scene.py: 0 failure(s)
$ (cópia com o scene.py novo e a planta) python3 tools/looks/scene.py --check | grep -E 'FAIL|failure'
  FAIL  and walks with it too, the path the LOOKS SET window draws by  ['A4', 'A4']
scene.py: 1 failure(s)
$ python3 tools/looks/controls.py --only scene-builder-walk-kit
  RED    scene-builder-walk-kit     scene.py :: Builder.walk_build
controls: 1 of 1 red (1 substitution)
$ python3 tools/looks/selftest.py | tail -3
  ..... 111 of 111 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R 'looks|kits'
4/8 Test #17: looks_live .......................***Skipped   0.10 sec
100% tests passed, 0 tests failed out of 8
```
- **Closed** — commit `59691da` (2026-10-02): test(looks): cover the kit Builder.walk_build passes to build()
  - Files (`git show --name-status 59691da`):
    - `M docs/tasks/kits/CORR-KITS-037.md`
    - `M tools/looks/controls.py`
    - `M tools/looks/scene.py`
