---
id: KITS-TASK-24
---

# KITS-TASK-24 — `figure.py` e `api.figure`: a única ponte com o `looks`

## Goal

`api.figure(kit, kit_set, figure, geometry_path, frame=None)` pede a cena ao `scene` do `looks`; com um TEX avulso, a geometria vem de `WE2002_LOOKS_IMAGE`, e sem ela a exceção tem a frase do motivo.

## Arquivos a criar ou modificar

- `tools/kits/core/figure.py`
- `tools/kits/core/api.py`
- `tools/kits/core/errors.py` — `FigureError`, `NoGeometry`, `GeometryRefused`
- `tools/kits/selftest.py`, `tools/kits/controls.py` — as asserções e os dois controles
- `NOTICE.md` — o `we3d` passa a alcançar o `kits` também pelo `figure.py`

## Done criteria

- [x] Só `core/figure.py` importa o `scene` do `looks`, afirmado pelo `kits_selftest` por AST e com controle plantado (o `grep 'looks'` literal não serve: ver o Log)
- [x] Sem `WE2002_LOOKS_IMAGE`, `api.figure` levanta a exceção tipada com a frase (saída colada)
- [x] Controle do §5: trocar as paletas 486 e 488 troca jogador e goleiro na cena (vermelho no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1).

## Log de Execução

### 2026-10-03

Na máquina Linux; base `3cfb2c4`.

**O que entrou.** `core/figure.py`: `scene_of(kit, kit_set, figure, geometry_path=None, frame=None, geometry=None)` lê `EDT_MOD`, `MODEL`, `DAT2D` e `ANIME` pela guarda do `looks` (`read_geometry`) e chama `scene.build` com os bytes do kit (`kit.data`, já atrás da guarda de forma) no lugar do contêiner — assim um TEX de patch ou de arquivo veste o corpo do disco confiável. `api.figure`, `api.read_geometry` e `api.palette_swap` na fachada; `FigureError`, `NoGeometry` e `GeometryRefused` em `errors.py`.

**O critério 1, e por que ele mudou de forma.** O `grep -rn 'looks' tools/kits/core/ -l` literal não lista só o `figure.py`, e não pode: o `teams.py` importa o `layout` do `looks` porque a §3.1 manda endereço morar lá, o `survey.py` são as sondas da fase 0 que a própria §3.1 lista, e a palavra aparece em comentário de `flat.py`, `tex.py`, `zones.py` e `source.py`. Medido por AST, antes desta task:

```
$ python3 - <<'X'   # módulos de tools/looks importados por cada arquivo de tools/kits/core
survey.py ['assembly', 'atlas', 'iso_source', 'layout', 'looks', 'section', 'texture']
teams.py ['layout']
(os outros sete: [])
X
```

A fonte de verdade ganha: o que a §3.1 diz é que o `figure.py` é a única ponte **que pede a cena**. O critério foi reescrito assim, e é o `kits_selftest` quem afirma, com controle (`scene-outside-figure` põe `import scene` no `teams.py`):

```
$ python3 tools/kits/selftest.py --no-plant | grep scene
  ok    only core/figure.py imports the looks scene (section 3.1)
$ python3 tools/kits/controls.py --only scene-outside-figure | tail -2
  RED    scene-outside-figure         kits/core/teams.py :: module imports
controls: 1 of 1 red
```

O critério 2:

```
$ env -u WE2002_LOOKS_IMAGE python3 -c 'import sys; sys.path.insert(0,"tools/kits"); from core import api
  kit = api.open_source("roms/japanese-shift-jis.bin").kit("00"); api.figure(kit, 1, 0)'
NoGeometry: The 3D figure needs the Japanese disc for its geometry: set WE2002_LOOKS_IMAGE to its data track (.bin).
$ (o mesmo com geometry_path="roms/golden-european-deluxe.bin")
GeometryRefused: roms/golden-european-deluxe.bin cannot give the figure's geometry: /BIN/DAT2D.BIN: read d0ff5ac291e1818c… from ro…
$ python3 tools/kits/selftest.py --no-plant | grep geometry
  ok    with no geometry disc, api.figure says why
```

O critério 3 — o controle 4 do §5 (`api.palette_swap`): o kit com as paletas 486 e 488 do conjunto trocadas é desenhado, e cada superfície do kit na cena tem de ser os índices da imagem original lidos pela paleta da **outra** linha. No `kits_image`, `TEX_A4` e `TEX_00`, as duas figuras, os dois conjuntos:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep -E 'TEX_00|figure:'
  ..... TEX_00 set 1 figure 0: rows (486,), 1 kit surface(s), 0 wrong
  ok    TEX_00 set 1 figure 0: 486/488 swapped draws the other figure's colours
  ..... TEX_00 set 2 figure 0: rows (486,), 1 kit surface(s), 0 wrong
  ..... TEX_00 set 1 figure 1: rows (488,), 1 kit surface(s), 0 wrong
  ..... TEX_00 set 2 figure 1: rows (488,), 1 kit surface(s), 0 wrong
figure: 0 failure(s)
```

O vermelho, numa cópia da árvore com `swapped_palettes` devolvendo o kit intacto:

```
  FAIL  TEX_00 set 1 figure 0: 486/488 swapped draws the other figure's colours  record 48, row 486: not the row 488 colours
  FAIL  TEX_00 set 2 figure 0: …  record 10556, row 486: not the row 488 colours
  FAIL  TEX_00 set 1 figure 1: …  record 48, row 488: not the row 486 colours
  FAIL  TEX_00 set 2 figure 1: …  record 10556, row 488: not the row 486 colours
figure: 4 failure(s)
```

**O `TEX_A4` passa mesmo plantado**, e é medição: nele a paleta de jogador é igual à de goleiro (§1.1), então trocá-las não muda cor nenhuma. Por isso o controle no disco é o `TEX_00`, e o catálogo tem um controle que não depende de disco (`figure-swap-noop`), contra o contêiner sintético do selftest, que exige os bytes das duas paletas trocados e nada mais:

```
$ python3 tools/kits/controls.py --only figure-swap-noop | tail -2
  RED    figure-swap-noop             kits/core/figure.py :: swapped_palettes
controls: 1 of 1 red
```

Na HEAD entregue:

```
$ python3 tools/kits/selftest.py | grep -E 'controls red|kits_selftest:'
  ..... 22 of 22 controls red
kits_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed   51.54 sec
2/4 Test #19: kits_image .......................   Passed   23.00 sec
3/4 Test #20: kits_gen .........................   Passed    0.02 sec
4/4 Test #21: kits_ui ..........................   Passed    8.92 sec
100% tests passed, 0 tests failed out of 4
```

Cada figura amostra **uma** superfície do kit (a de linha 486 no jogador, 488 no goleiro) — o resto vem do `DAT2D`.
- **Closed** — commit `3747272` (2026-10-03): feat(kits): api.figure, the core's one bridge to the looks scene
  - Files (`git show --name-status 3747272`):
    - `M NOTICE.md`
    - `M docs/prompts/perfil-kits.md`
    - `M docs/tasks/kits/24-figura.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/errors.py`
    - `A tools/kits/core/figure.py`
    - `M tools/kits/selftest.py`
