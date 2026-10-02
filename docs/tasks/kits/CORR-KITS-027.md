---
id: CORR-KITS-027
---

# CORR-KITS-027 — Give the index-past-palette count a red control or drop it

Origin: [KITS-TASK-15](/docs/tasks/kits/15-flat.md)

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
