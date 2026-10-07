---
id: CORR-KITS-039
---

# CORR-KITS-039 — Controle para scene.build ignorar o kit_set nas paletas

Origin: [KITS-TASK-22](/docs/tasks/concluidos/kits/22-looks-kit-set.md)

## Problem

Em `scene.build`, a linha `palettes = texture.in_set_order(palettes, kit_set)` (`tools/looks/scene.py:344`) faz parte do caminho do `kit_set`, mas nenhum controle do catálogo a cobre. Trocada por `in_set_order(palettes, 1)` numa cópia, o self-check sem disco continua verde (`scene.py: 0 failure(s)`), então o critério 3 da task ("forçar `kit_set` ignorado numa cópia derruba o self-check") não vale para essa linha. Só o `looks_image` percebe, e só pelo `TEX_98`, o kit que difere apenas nas paletas — o `TEX_00` continua dando "outra figura". O Log nunca mostra essa linha ficando vermelha.

## Evidência

```text
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C $S
$ sed -i 's/            palettes = texture.in_set_order(palettes, kit_set)/            palettes = texture.in_set_order(palettes, 1)/' $S/tools/looks/scene.py
$ (cd $S && python3 tools/looks/scene.py --check | tail -1)
scene.py: 0 failure(s)
$ (cd $S && WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/looks/scene.py --check-image | grep -E 'TEX_98 set 1 [0-9a-f]|problem|says')
TEX_98 set 1 4a8089cb1a6b6a5a, set 2 4a8089cb1a6b6a5a: the same picture
scene --check-image: 1 problem(s)
    TEX_98: set 2 gave the same picture, and section 1.1 says they differ
```

## Root cause

O self-check sem disco `_kit_set_reaches_the_bank` segue o `kit_set` do `build` até o `draw_list`, e do `draw_list` até o `in_set_order`, mas nunca até o banco de paletas do próprio `build`. Hipótese: passou porque o vermelho plantado no `draw_list` foi por `TEX_00`. À parte: a reordenação de paleta do próprio `draw_list` (`assembly.py:720`) não muda saída — plantada como set 1, `--check` e `--check-image` ficam verdes, porque o `draw_list` só usa o retângulo da paleta, igual nos dois conjuntos.

## Fix

Em `tools/looks/scene.py`, estender `_kit_set_reaches_the_bank` para registrar a ordenação de paletas do `build()` com o conjunto pedido. Em `tools/looks/controls.py`, acrescentar um controle (por exemplo `scene-kit-set-palettes-ignored`) que troca essa linha por `in_set_order(palettes, 1)` e exige o vermelho.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/controls.py`

## Verificação

```sh
python3 tools/looks/controls.py --only scene-kit-set-palettes-ignored
```

Hoje o controle não existe; depois do conserto tem de imprimir RED. A planta acima tem de deixar `python3 tools/looks/scene.py --check` vermelho.

## Log de Execução

### 2026-10-03

Reproduzido na HEAD `4da9add`, numa cópia `git archive HEAD tools` (a planta casa uma vez):

```
$ sed -i 's/            palettes = texture.in_set_order(palettes, kit_set)/            palettes = texture.in_set_order(palettes, 1)/' $S/tools/looks/scene.py
$ (cd $S && python3 tools/looks/scene.py --check | tail -1)
scene.py: 0 failure(s)
```

Conserto: `_kit_set_reaches_the_bank` ganha a terceira perna — `build()` com um `draw_list` falso que nomeia o container do kit vestido, e `in_set_order` anotando o conjunto pedido e parando —, e afirma `[1, 2]`. Controle novo `scene-kit-set-palettes-ignored` em `tools/looks/controls.py`.

```
$ python3 tools/looks/scene.py --check | grep -E 'palettes in|failure'
  ok    and build() searches the kit's palettes in that set's order too
scene.py: 0 failure(s)
$ (cópia com o scene.py novo e a planta) python3 tools/looks/scene.py --check | grep -E 'FAIL|failure'
  FAIL  and build() searches the kit's palettes in that set's order too  [1, 1]
scene.py: 1 failure(s)
$ python3 tools/looks/controls.py --only scene-kit-set-palettes-ignored
  RED    scene-kit-set-palettes-ignored scene.py :: build
controls: 1 of 1 red (1 substitution)
$ python3 tools/looks/selftest.py | tail -3
  ..... 114 of 114 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R 'looks|kits'
4/8 Test #17: looks_live .......................***Skipped   0.10 sec
100% tests passed, 0 tests failed out of 8
```

A observação da causa raiz — a reordenação de paleta do `draw_list` (`assembly.py:720`) não muda saída — fica como estava: não é o que esta CORR pede.
- **Closed** — commit `e36c6f7` (2026-10-03): test(looks): cover build() searching the kit's palettes in the set asked
  - Files (`git show --name-status e36c6f7`):
    - `M docs/tasks/kits/CORR-KITS-039.md`
    - `M tools/looks/controls.py`
    - `M tools/looks/scene.py`
