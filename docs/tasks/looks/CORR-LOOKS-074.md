---
id: CORR-LOOKS-074
title: "Um código de largura 0 entra na lista de sprites do jogo e não na do Font.run"
origin: CORR-LOOKS-073
severity: low
files: [tools/looks/glyphs.py, tools/looks/oracle.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-074 — Um código de largura 0 entra na lista de sprites do jogo e não na do Font.run

Origin: [CORR-LOOKS-073](/docs/tasks/looks/CORR-LOOKS-073.md)

## Problema identificado

Na passada que desenha (kind 32), o jogo só deixa de chamar o `GsSortSprite`
(`0x8003E8BC`) para o **espaço** (`0x8010C93C`). Um código de largura 0 — `@`,
`^`, `~` nesta fonte — ainda entrega ao GPU um `GsSPRITE` de largura 0. O
`glyphs.Font.run` não põe nada na lista para esse código. Na tela nada aparece
nos dois casos, mas uma comparação de **lista de sprites** (o `oracle.py
--glyphs` conta sprites de fonte) contaria um a mais do lado do jogo.

Hoje é inalcançável: nenhuma string da tela `LOOKS SET` tem `@`, `^` ou `~`
(`screen.json`). Fica registrado para quando o `glyphs.py` servir a outra tela
ou a uma string nova.

## Evidência

Leitura estática do `/SELECTC.BIN` (base `0x800FC000`, igual nos dois discos),
feita na CORR-LOOKS-073 e transcrita no Log dela:

```text
$ sed -n 87,89p docs/tasks/looks/CORR-LOOKS-073.md
passada que desenha (8010c4dc, kind 32 -> jal 8010bb04 com a3=0)
  8010c93c  espaço (32) pula o GsSortSprite (0x8003e8bc); largura 0 não pula
  8010c9c0  lhu v0,192 ; lb v1,14(s1) ; addu v0,v0,v1 ; addu s2,a0,v0   x += w + espaçamento

$ python -c "import sys;sys.path.insert(0,'tools/looks');import glyphs;f=glyphs.Font(glyphs._toy_table());b=bytearray(f.table);b[2*(64-32)+1]=0;print(glyphs.Font(bytes(b)).run('@',(0,0),2,(128,128,128)))"
[]
```

Não medido ao vivo: nenhum quadro do jogo exercita o caso.

## Causa raiz

`Font.run` (`tools/looks/glyphs.py`) pula todo código com `width == 0`, junto
com o espaço (`if char != " " and width`); o jogo só pula o espaço.

## Correção

Decidir, com medição, se vale reproduzir: ou o `Font.run` passa a emitir o
sprite de largura 0 (e a janela ignora sprite vazio ao pintar), ou o `oracle.py
--glyphs` descarta sprite de largura 0 do lado do jogo ao contar, com a
leitura acima como justificativa. Se nenhuma tela alcançar o caso, `rite
mark-stale` com esse motivo é resposta válida.

## Arquivos a criar ou modificar

- `tools/looks/glyphs.py`
- `tools/looks/oracle.py`

## Verificação

Uma string com `@` desenhada no jogo (se alcançável) e pelo `Font.run`: as duas
listas de sprites têm o mesmo tamanho, ou o descarte é explícito e testado.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `3a864a4b`: **reproduzida**.

```text
$ sed -n 87,89p docs/tasks/looks/CORR-LOOKS-073.md   -> igual à Evidência
$ python -c "... Font(bytes(b)).run('@',(0,0),2,(128,128,128))"
[]
controle: tabela de brinquedo intacta, '@' tem largura 4 e o Font.run emite 1 sprite
tools/looks/glyphs.py:140  if char != " " and width:
alcance: screen.json tem 962 strings, nenhuma com '@', '^' ou '~' (grep -c '[@^~]' -> 0)
```

Execução em 2026-09-22, HEAD `3a864a4b`. **Lado escolhido: o descarte
explícito e testado**, do lado do jogo. Motivo: o sprite de largura 0 não põe
pixel na tela, a janela não teria o que fazer com ele, e emiti-lo no
`Font.run` obrigaria todo consumidor a filtrar sprite vazio; o caso é
inalcançável na `LOOKS SET` (Triagem acima), então reproduzi-lo não mediria
nada que o descarte não meça.

- `tools/looks/oracle.py`: `font_sprites(sprites)` — sprite na página da
  fonte **e** com largura > 0 —, com a leitura de `0x8010C93C` e esta CORR no
  docstring; o `--glyphs` conta com ela e pula código de largura 0 no laço de
  chamadas (contado como `of width 0` na linha do slot).
- `tools/looks/oracle.py` `_checks`: tabela de brinquedo com `@` de largura
  0, `Font.run("A@B")` dá 2 sprites; a lista "do jogo" com o sprite vazio e um
  de outra página dá 2 por `font_sprites`, e o controle sem o descarte dá 3.
- `tools/looks/glyphs.py`: o docstring do `Font.run` diz que o jogo emite o
  sprite vazio e que ele é omitido de propósito.

```text
$ python tools/looks/oracle.py --check | grep 0-wide -A1
  ok    Font.run lays no sprite for a 0-wide code
  ok    the game's font sprites, the 0-wide one dropped, count as Font.run's
  ok    and without the drop they would not: the control
oracle.py: 0 failure(s)

$ python tools/looks/oracle.py --glyphs      (ao vivo, fork fora da tela)
  -- slot 2 --
    134 glyph(s) drawn, 13 space(s), 0 of width 0; 121 of 121 font sprite(s) equal to the rule in uv, size and CLUT, 0 unclaimed
    control: the table read 1 pair(s) off matches 0 of them
    pen: 8 object(s), 86 advance(s) laid by Font.run from each run's first glyph, 0 run(s) off
  -- slot 1 --
    134 glyph(s) drawn, 13 space(s), 0 of width 0; 121 of 121 font sprite(s) equal to the rule in uv, size and CLUT, 0 unclaimed
oracle --glyphs: 0 problem(s) over 2 slot(s)

$ python tools/looks/selftest.py      -> looks_selftest: 0 failure(s), 101 of 101 controls red
$ python tools/looks/glyphs.py        -> glyphs.py: 0 failure(s)
$ python tools/looks/cli.py check     -> 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```

Não medido ao vivo: o `0 of width 0` confirma que a tela não exercita o caso;
o descarte só é provado pelo self-check sintético.
