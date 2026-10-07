---
id: CORR-KITS-027
---

# CORR-KITS-027 — Give the index-past-palette count a red control or drop it

Origin: [KITS-TASK-15](/docs/tasks/concluidos/kits/15-flat.md)

## Problem

O critério 1 da KITS-TASK-15 diz "sem índice fora da paleta (contagem da ferramenta)", e o `cli.py flat` imprime "0 with an index past its palette". Essa contagem não tem como passar de zero para nenhum kit que passe pela guarda de forma: a guarda (`tex.EXPECTED_SHAPE`) exige toda CLUT em 256×1, então toda paleta tem 512 bytes e 256 cores, e o `flat.paint` testa `i >= len(lut)` com `i` vindo de `bytes` de índices de 8 bits, cujo máximo é 255. O controle `--negative` só planta o defeito de cor única; nenhum controle deixa o OUTSIDE vermelho, e o selftest não o menciona. Pela regra "verificador sem vermelho visto não é gate", metade do critério 1 se apoia numa tautologia, não numa medição.

## Evidência

```text
$ grep -n "KIND_CLUT" tools/kits/core/tex.py | head -5
(KIND_CLUT, 0, 486, 256, 1),       # 2 player palette, first set   (as cinco CLUTs em 256x1)
$ python -c "...api.open_source('roms/japanese-shift-jis.bin').kit('A4')... print([(p.record,len(p.raw)) for p in k.palettes])"
[(2, 512), (3, 512), (6, 512), (7, 512), (9, 512)]
$ grep -n "OUTSIDE\|index past" tools/kits/cli.py tools/kits/selftest.py
tools/kits/cli.py:551:    wrong: an index past its palette, a picture of a single colour."""
tools/kits/cli.py:571:                print("  OUTSIDE %s %s / %s: %s" % (name, api.RECORD_NAMES[image],
tools/kits/cli.py:588:    print("%d pairings painted (%d per kit): %d with an index past its palette, "
$ python tools/kits/cli.py flat --negative roms/japanese-shift-jis.bin | grep -c "OUTSIDE"
0
```

## Root cause

Hipótese: o contador copiou a redação do critério sem conferir se a guarda já descartava o caso.

## Fix

No `flat_negative` de `tools/kits/cli.py` (ou num self-check do `flat.paint` no selftest), plantar uma paleta com menos de 256 entradas direto no `flat.paint`/`palette_rgba` e exigir o `KitRefused`. Alternativa: reescrever a linha de resumo e o Log do critério 1 dizendo que a guarda garante CLUT de 256 entradas e índice de 8 bits, então a condição vale por construção e não é contada.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/flat.py`
- `tools/kits/selftest.py`
- `docs/tasks/kits/15-flat.md`

## Verificação

```text
$ python tools/kits/cli.py flat --negative roms/japanese-shift-jis.bin | grep -c "OUTSIDE"
```

Hoje dá 0; depois tem de mostrar a linha OUTSIDE da paleta curta plantada, terminando em "control held". Ou, na alternativa, `grep -n "index past its palette" tools/kits/cli.py` deixa de afirmar uma contagem.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `b08c3cb1`)

```text
$ grep -n "KIND_CLUT" tools/kits/core/tex.py | head -5
43:KIND_CLUT = "clut"
48:    (KIND_CLUT, 0, 486, 256, 1),       # 2 player palette, first set
49:    (KIND_CLUT, 0, 488, 256, 1),       # 3 goalkeeper palette, first set
52:    (KIND_CLUT, 0, 486, 256, 1),       # 6 player palette, second set
53:    (KIND_CLUT, 0, 488, 256, 1),       # 7 goalkeeper palette, second set
$ python tools/kits/cli.py flat --negative roms/japanese-shift-jis.bin | grep -c "OUTSIDE"
0
```

REPRODUCED. Causa raiz confirmada: a guarda só passa CLUT de 256×1, e o `paint` testa índice de 8 bits contra 256 cores — por construção, zero.

### O que foi feito

Escolhida a primeira forma do conserto (dar vermelho ao contador), não a alternativa (deixar de contar): a condição continua no `flat.paint`, e é ela que recusaria uma paleta curta se uma origem futura a trouxesse.

- `tools/kits/core/api.py`: `paint` exportado pela fachada, ao lado de `palette_rgba`.
- `tools/kits/cli.py`: `flat --negative` ganhou um segundo controle, `_flat_short_palette`: pinta o uniforme do primeiro conjunto com as `FLAT_SHORT_COLOURS = 128` primeiras cores da paleta de jogador, conta os pixels de índice além delas, e exige `KitRefused` com linha `OUTSIDE`. O código de saída é o pior dos dois controles.
- KITS-TASK-15: o vermelho novo colado no Log, com a explicação de por que o zero do critério 1 não tinha vermelho.

### Verificação

```text
$ python tools/kits/cli.py flat --negative roms/japanese-shift-jis.bin; echo "exit $?"
control: TEX_00, player palette, first set (bytes 9468..9979) set to its first colour, as a lone TEX
  SINGLE  uniform, first set / player palette, first set
  SINGLE  sleeves, first set / player palette, first set
control held: exactly the 2 pairing(s) wearing it are single-coloured
control: TEX_00, uniform, first set painted with the first 128 colours of player palette, first set (454 pixel(s) index past them)
  OUTSIDE TEX_00 uniform, first set / player palette, first set: an index of the image is past the 128 colours of its palette
control held: the short palette is refused
exit 0
```

O controle visto falhando — com as 256 cores mantidas não há índice além, o `paint` aceita e o controle acusa:

```text
$ python -c "import sys; sys.path.insert(0,'tools/kits'); import cli
k=cli.api.open_source('roms/japanese-shift-jis.bin').kit('00'); cli.FLAT_SHORT_COLOURS=256
print('256 ->', cli._flat_short_palette('TEX_00', k))"
control: TEX_00, uniform, first set painted with the first 256 colours of player palette, first set (0 pixel(s) index past them)
control FAILED
256 -> 1
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant --quiet | tail -1
kits_selftest: 0 failure(s)
```
- **Closed** — commit `20bed465` (2026-10-02): fix(kits): give flat's index-past-palette count a planted red
  - Files (`git show --name-status 20bed465`):
    - `M docs/tasks/kits/15-flat.md`
    - `M docs/tasks/kits/CORR-KITS-027.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
