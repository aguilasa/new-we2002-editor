---
id: KITS-TASK-15
---

# KITS-TASK-15 — `flat.py`: imagem + paleta em RGBA, o bitmap de trabalho e a grade 16×16

## Goal

`kit.flat`, `kit.work_bitmap(kit_set, figure)` e `kit.palette_grid` existem; a transparência é a regra do console, pela cor — no índice 0 onde a paleta tem preto ali, que não é todo TEX (Log); `cli.py export` grava PNG.

## Arquivos a criar ou modificar

- `tools/kits/core/flat.py`
- `tools/kits/core/api.py`
- `tools/kits/cli.py`
- `tools/kits/core/tex.py` — os três métodos do `Kit` (`flat`, `work_bitmap`, `palette_grid`), que delegam ao `flat.py`
- `docs/PLAN-KITS-PY.md` (§1.3, a medição do índice 0)

## Done criteria

- [x] Os 105 TEX × as combinações de imagem e paleta que o jogo usa saem sem índice fora da paleta e sem imagem de uma cor só (contagem da ferramenta)
- [x] `kit.work_bitmap` tem 256×128 e o `export` do titular e do suplente de uma tag do §1.1 que difere dá PNGs diferentes; do `TEX_A4`, iguais (digests no Log)
- [x] Sem Qt e sem Pillow no núcleo: `grep -rn 'PySide\|PIL' tools/kits/core/` vazio

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1). PNG escrito sem Pillow no núcleo (`zlib` da stdlib) ou pela CLI; a escolha fica no Log.

Da KITS-TASK-09: o `cli.py` já tem `bgr555_rgba`, `write_png` e `read_png` (stdlib), feitos para o `export` e o confronto 1 antes de existir `flat.py`. Quando o `flat.py` trouxer a conversão BGR555 → RGBA para o núcleo, o `cli.py` passa a usar a da fachada — uma regra de transparência em dois lugares é a que diverge.

O que ficou decidido:

- **O PNG é da CLI**, não do núcleo: o núcleo devolve `FlatImage(width, height, indices, palette, rgba)` e a CLI escreve o PNG indexado com `zlib` da stdlib (o `write_png` que já existia para o confronto 1). O núcleo não grava nada, como no `looks`.
- **A conversão BGR555 → RGBA mora no `flat.py`** (`flat.colour`, `api.palette_rgba`), e o `bgr555_rgba` do `cli.py` passou a chamá-la — uma regra de transparência num lugar só (a nota da KITS-TASK-09). O confronto 1 continua `105 of 105` depois da troca.
- **A transparência é a regra do console, pela cor** (`0x0000` com STP limpo). O Goal desta task diz "índice 0 é transparente", e isso **não vale para todo TEX**: o índice 0 é `0x0000` em 95 dos 105 kits em cada paleta de jogador e goleiro, e em 17 das 105 de bandeira (72 têm `0x7fff`, branco). Nos outros, o índice 0 é uma cor opaca (`0x0f5d` é a mais comum) e o `flat.py` a pinta opaca, como o console. Registrado no §1.3 do plano.
- **"As combinações que o jogo usa"** são `api.GAME_PAIRS`, nove por kit: uniforme e mangas de cada conjunto com a paleta de jogador e a de goleiro do mesmo conjunto, e a bandeira com a dela. O árbitro fica de fora: qual paleta o jogo dá a ele é a pergunta aberta da §4.5.
- **O bitmap de trabalho** é `kit.work_bitmap(kit_set, figure)`: uniforme (128×128) à esquerda, mangas (128×128) à direita, na paleta do `figure` (0 jogador, 1 goleiro) daquele conjunto — a disposição do SUPERPACK-UNIFORMES §2 e do `survey.BITMAP_X`.

## Log de Execução

### 2026-10-02

O critério 1 — `cli.py flat`, a ferramenta que pinta e conta:

```
$ python tools/kits/cli.py flat roms/japanese-shift-jis.bin      # exit 0
945 pairings painted (9 per kit): 0 with an index past its palette, 0 of a single colour; 420 of 420 work bitmaps 256x128; index 0 transparent in 397 of 525 palettes; 0 kit(s) refused
  index 0 of player palette, first set:      0x0000 in 95, 0x0f5d in 7, 0x62ea in 2, 0x02fa in 1
  index 0 of goalkeeper palette, first set:  0x0000 in 95, 0x0f5d in 5, 0x62ea in 2, 0x109b in 2, 0x02fa in 1
  index 0 of player palette, second set:     0x0000 in 95, 0x0f5d in 8, 0x6f7b in 1, 0x02fa in 1
  index 0 of goalkeeper palette, second set: 0x0000 in 95, 0x0f5d in 6, 0x109b in 1, 0x6f7b in 1, 0x62ea in 1, 0x02fa in 1
  index 0 of flag palette:                   0x7fff in 72, 0x0000 in 17, 0x0ca1 in 2, 0x77bd in 2, ...
```

O vermelho dele — a paleta de jogador do primeiro conjunto achatada numa cor, num TEX avulso temporário:

```
$ python tools/kits/cli.py flat --negative roms/japanese-shift-jis.bin      # exit 0
control: TEX_00, player palette, first set (bytes 9468..9979) set to its first colour, as a lone TEX
  SINGLE  uniform, first set / player palette, first set
  SINGLE  sleeves, first set / player palette, first set
control held: exactly the 2 pairing(s) wearing it are single-coloured
```

O critério 2 — os quatro bitmaps de trabalho do `TEX_00` (titular e suplente diferem, §1.1) e do `TEX_A4`:

```
$ python tools/kits/cli.py export --work-bitmap --tag 00 --tag A4 --out <tmp>/wb15 roms/japanese-shift-jis.bin
wrote 8 work bitmap PNG(s) (256x128) to <tmp>/wb15; 0 kit(s) refused
$ sha256sum *.png | cut -c1-16,65-
b3517648a88e779b *TEX_00_set1_keeper.png
70d60662480fdcc4 *TEX_00_set1_player.png
18c0350565201d56 *TEX_00_set2_keeper.png
6401ecddc1b97f74 *TEX_00_set2_player.png
706796b4b1f29fdf *TEX_A4_set1_keeper.png
706796b4b1f29fdf *TEX_A4_set1_player.png
706796b4b1f29fdf *TEX_A4_set2_keeper.png
706796b4b1f29fdf *TEX_A4_set2_player.png
```

No `TEX_00` os quatro diferem; no `TEX_A4` os quatro são o mesmo arquivo — titular = suplente, e jogador = goleiro, como o §1.1 mediu. O cabeçalho dos PNGs diz `256 128`.

O critério 3:

```
$ grep -rn 'PySide\|PIL' tools/kits/core/; echo "grep exit $?"
grep exit 1
```

Regressões:

```
$ python tools/kits/cli.py export --confront roms/japanese-shift-jis.bin | tail -1
confront 1: 105 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
$ python tools/kits/selftest.py --quiet | grep -E "FAIL|controls red|kits_selftest:"
  ..... 12 of 12 controls red
kits_selftest: 0 failure(s)
```
- **Closed** — commit `36ec9b3b` (2026-10-02): feat(kits): paint a kit in 2D: image + palette, the work bitmap, the palette grid
  - Files (`git show --name-status 36ec9b3b`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/15-flat.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `A tools/kits/core/flat.py`
    - `M tools/kits/core/tex.py`
