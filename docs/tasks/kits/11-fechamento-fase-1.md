---
id: KITS-TASK-11
---

# KITS-TASK-11 — Fechamento da fase 1 — núcleo, lado TEX

## Goal

A fase 1 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] `ctest -R kits` na HEAD, saída colada com os nomes dos alvos
- [x] `python tools/kits/controls.py` na HEAD, todos vermelhos
- [x] Confrontos 1 e 2 refeitos, números colados
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

Da KITS-TASK-09: o confronto 1 roda dentro do `kits_image` (`cli.py export --confront` e o `--negative`, ~31 s cada). Continua aberta, sem dono, a discordância da KITS-TASK-02 entre `texture.tables` (do `looks`) e `bin_archive.entries` sobre `/BIN/DATSEL2.BIN` — não é TEX, e o confronto 1 não a toca.

## Log de Execução

### 2026-10-01 — na HEAD `d11f7415`

Build fora da árvore (`%TEMP%/build-kits08`, reconfigurado na HEAD):

```
$ ctest -N -R kits
  Test #14: kits_selftest
  Test #15: kits_image
Total Tests: 2

$ env -u WE2002_LOOKS_IMAGE ctest -R kits
1/2 Test #14: kits_selftest ....................   Passed   50.02 sec
2/2 Test #15: kits_image .......................***Skipped   0.13 sec
100% tests passed out of 2

$ WE2002_LOOKS_IMAGE=.../roms/japanese-shift-jis.bin ctest -R kits -V
14:   ..... 21 looks self-check(s): anime, assembly, atlas, cli, confront, glyphs, harness, iso_source, layout, looks, modelfile, oracle, pieces, scene, screen, section, skin, sprites, stature, texture, ui_check
14:   ..... 12 of 12 controls red
14: kits_selftest: 0 failure(s)
1/2 Test #14: kits_selftest ....................   Passed   51.01 sec
15:   ..... 105 of 105 kits pass the guard
15:   ..... confront 1: 105 of 105 tags equal
15: kits_image: 0 failure(s)
2/2 Test #15: kits_image .......................   Passed   61.69 sec
100% tests passed out of 2
```

Os controles:

```
$ python tools/kits/controls.py      # exit 0
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
  RED    cli-imports-survey           kits/cli.py :: the imports
  RED    confront2-blind              kits/confront.py :: compare_pair
controls: 12 of 12 red
```

Confronto 1 (o disco japonês) e o controle dele:

```
$ python tools/kits/cli.py export --confront roms/japanese-shift-jis.bin      # exit 0
confront 1: 105 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin | tail -3   # exit 0
  DIFFER TEX_01_05.png palette 0: palettes differ
confront 1: 103 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
control: TEX_00 image 0 pixel 4096 +1, and TEX_01 palette 0 colour 1 red ^1, on our side -- red, held
```

Confronto 2 (`WE2002_KITS_CORPUS=C:/games/we2002/Superpackv6/We2002/TEX/Banderas 3D`):

```
$ python tools/kits/confront.py      # exit 0
confront 2: 160 pairs read, 160 match byte for byte (no mismatch)
$ python tools/kits/confront.py --negative | tail -1      # exit 0
control held: the changed copy is refused
```

As outras verificações da fase 1 do perfil:

```
$ grep -nE '^(from|import) ' tools/kits/cli.py      # fora da stdlib, só:
34:from core import api  # noqa: E402
$ sed -n '/^## Lineage of the kit viewer/,/^## Copyright/p' NOTICE.md | grep -ci superpack
0
$ sed -n '/^## Lineage of the kit viewer/,/^## Copyright/p' NOTICE.md | grep -o "^| \*\*[^|]*"
| **Maximiliano Ducoli (CARP)**
| **Darkensses**
| **LaGaRTo**, with **WarlockDC** and **Jordinator**
$ python tools/kits/cli.py tex roms/golden-european-deluxe.bin | tail -1
105 kits: 97 pass, 8 refused; 64 read past the ISO size, 67 with sectors marked Form 2 read as Form 1
$ python tools/kits/cli.py tex roms/golden-european-deluxe.bin | grep -E "^(PASS|REFUSE) +TEX_(13|48)"
PASS   TEX_13 (32146 bytes): 6 images, 5 palettes
REFUSE TEX_48 (31464 bytes): record 0 (uniform, first set) has an LZSS stream that does not decode: stream at 48: distance 0 at 4810
$ python tools/kits/cli.py tex --iso-size roms/golden-european-deluxe.bin > i.txt; tail -1 i.txt
105 kits: 40 pass, 65 refused; 0 read past the ISO size, 18 with sectors marked Form 2 read as Form 1
$ grep -B1 "note:" i.txt | grep -c "^PASS"
16
```

```
$ rite check --cycle kits --json      # exit 0
{'errors': 0, 'warnings': 0}
```

A discordância sobre `/BIN/DATSEL2.BIN` (nota acima) continua aberta e sem dono: não é TEX, nada da fase 1 depende dela.
