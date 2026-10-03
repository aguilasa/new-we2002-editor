---
id: KITS-TASK-22
---

# KITS-TASK-22 — Parâmetro `kit_set`: o banco do TEX entrega o 2º par de registros

## Goal

`kit_set=1` (titular, default) e `kit_set=2` (suplente) no `Builder` e no caminho de tupla; a escolha é de ordem de busca no banco e o resto do `looks` não muda.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/assembly.py`
- `tools/looks/texture.py`
- `tools/looks/controls.py` — os controles moram no catálogo, que o `selftest.py` planta inteiro; nem o `atlas.py` nem o `selftest.py` precisaram mudar

## Done criteria

- [x] `ctest -R looks` com as quatro (`looks_selftest`, `looks_image`, `looks_ui`, `looks_live`) verdes, ou *skipped* só pela falta declarada, **antes e depois** — as duas transcrições no Log
- [x] Controle do §5: o suplente do `TEX_A4` dá o mesmo quadro que o titular; de uma tag do §1.1 que difere, um quadro diferente — digests no Log
- [x] Controle: forçar `kit_set` ignorado numa cópia derruba o self-check

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2). Depende da 21 porque as duas tocam `scene.py`.

## Log de Execução

### 2026-10-02

Na máquina Linux, com o `:98`, o venv, os dois discos e os dois states:

```
export DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
       WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
```

**Antes**, na HEAD `839dd31`, sem nada mexido:

```
$ ctest --test-dir build -R looks
1/4 Test #14: looks_selftest ...................   Passed   13.35 sec
2/4 Test #15: looks_image ......................   Passed    2.24 sec
3/4 Test #16: looks_ui .........................   Passed  219.61 sec
4/4 Test #17: looks_live .......................   Passed   12.20 sec
100% tests passed, 0 tests failed out of 4
```

**O banco, medido antes de mexer.** Os registros do `TEX_00`, pela leitura do próprio `texture.py`, confirmam o §1.1: duas imagens e duas paletas repetidas no mesmo retângulo, e a bandeira e o árbitro uma vez só.

```
$ python3 - <<'X'   # texture.images/palettes sobre /BIN/TEX_00.BIN
img 48 (576, 256, 64, 128)       img 10556 (576, 256, 64, 128)
img 5088 (576, 384, 64, 128)     img 15908 (576, 384, 64, 128)
img 21420 (704, 256, 64, 64)     img 24392 (768, 384, 64, 128)
clut 9468 (0, 486, 256, 1)       clut 20332 (0, 486, 256, 1)
clut 10012 (0, 488, 256, 1)      clut 20876 (0, 488, 256, 1)
clut 23848 (256, 480, 256, 1)
X
```

**O que mudou.** `texture.in_set_order(records, kit_set)`: em cada grupo de registros com o mesmo retângulo, o `kit_set`-ésimo vai para o lugar do primeiro; conjunto 1 é a lista intacta, e conjunto que não seja 1 ou 2 levanta `NoSuchSet`. O `assembly.draw_list` busca as imagens e as paletas do TEX nessa ordem — o `DAT2D` não é tocado —, e o `scene.build` ordena as paletas do kit do mesmo jeito, para que uma imagem de um conjunto nunca seja pintada com a paleta do outro. `kit_set=1` de default em `draw_list`, `build`, `from_image` e `Builder`; o `Builder` recusa o conjunto antes de abrir o disco, como recusa a tag.

O critério 2, no `scene.py --check-image` (o `looks_image`): o digest do quadro por **conteúdo** (`scene.picture_digest`: pontos, (u, v) e as cores de cada superfície) — por chave não serve, porque o 2º conjunto do `TEX_A4` são os mesmos bytes em outro offset. E, porque quadro diferente não basta (ver o vermelho abaixo), o registro do TEX que cada conjunto amostrou:

```
$ python3 tools/looks/scene.py --check-image | grep -E 'set 1|scene --check'
      TEX_A4 set 1 samples [48], set 2 samples [10796]
      TEX_A4 set 1 9b9410e6d2591824, set 2 9b9410e6d2591824: the same picture
      TEX_00 set 1 samples [48], set 2 samples [10556]
      TEX_00 set 1 66f166d86fa5a396, set 2 9a44dba5ad6145df: another picture
      TEX_98 set 1 samples [48], set 2 samples [11400]
      TEX_98 set 1 4a8089cb1a6b6a5a, set 2 b9c612c97571e98b: another picture
scene --check-image: ok
```

`TEX_00` é das 103 em que as imagens diferem, `TEX_98` a única em que só as paletas diferem (§1.1). O digest inteiro é o `sha256`; o Log guarda os 16 primeiros dígitos que o `--check-image` imprime.

**O vermelho que mudou a asserção.** Com o `kit_set` tirado da chamada ao `draw_list` numa cópia da árvore (`assembly.draw_list(disc, values, figure, kit, 1)`), a primeira versão da conferência — só "quadro igual ou diferente" — **passou**: o `TEX_00` ainda saía diferente (`set 2 5729e4cf4fc55c08`), porque o `scene` trocava a paleta sozinho e pintava a imagem do titular com as cores do suplente. Depois da asserção por registro, a mesma cópia:

```
scene --check-image: 3 problem(s)
    TEX_A4 set 2 sampled [48], not the second set [10796, 16232]
    TEX_00 set 2 sampled [48], not the second set [10556, 15908]
    TEX_98 set 2 sampled [48], not the second set [11400, 17108]
```

O critério 3 — os controles no catálogo do `controls.py`, julgados pelo self-check do `scene`, sem disco: o `kit_set` é seguido do `Builder` ao `build` (por um `build` que anota), do `build` ao `draw_list` (um `draw_list` que anota) e do `draw_list` à ordem do banco (um `in_set_order` que anota):

```
$ python3 tools/looks/controls.py --only scene-kit-set-ignored
  RED    scene-kit-set-ignored      scene.py :: build
controls: 1 of 1 red (1 substitution)
$ python3 tools/looks/controls.py --only assembly-kit-set-ignored
  RED    assembly-kit-set-ignored   assembly.py :: draw_list
controls: 1 of 1 red (1 substitution)
```

E o `texture.self_check` confere a própria ordem, num contêiner de mentira com o formato do TEX: conjunto 1 intacto, conjunto 2 `shirt 2, sleeve 2, shirt 1, sleeve 1, flag, player 2, player 1`, conjunto 3 recusado.

Dois controles antigos deixaram de casar com a assinatura nova e o `selftest` acusou (`scene-builder-walk-kit matches exactly once in scene.py  matched 0 time(s)`; o `scene-builder-default-kit` dava `matched 0x`). As âncoras foram refeitas, e os dois voltaram ao vermelho.

**Depois:**

```
$ ctest --test-dir build -R looks
1/4 Test #14: looks_selftest ...................   Passed   13.02 sec
2/4 Test #15: looks_image ......................   Passed    2.83 sec
3/4 Test #16: looks_ui .........................   Passed  216.73 sec
4/4 Test #17: looks_live .......................   Passed   12.04 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/looks/selftest.py | grep -E 'controls red|looks_selftest:'
  ..... 113 of 113 controls red
looks_selftest: 0 failure(s)
$ ctest --test-dir build -R 'kits_selftest|kits_image'
1/2 Test #18: kits_selftest ....................   Passed   39.36 sec
2/2 Test #19: kits_image .......................   Passed   22.50 sec
```

(Os dois do `kits` porque o `kits/core/survey.py` chama o `draw_list`; com o `kit_set` de default ele não mudou.)
- **Closed** — commit `b94af6f` (2026-10-02): feat(looks): kit_set picks the kit's second set by search order
  - Files (`git show --name-status b94af6f`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/22-looks-kit-set.md`
    - `M tools/looks/assembly.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/texture.py`
- **Reviewed** (2026-10-03) at `f59c557`: CORR-KITS-039, CORR-KITS-040
