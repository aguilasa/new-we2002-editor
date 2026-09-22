---
id: CORR-LOOKS-073
title: Fix the width-0 self-check that claims the pen stays put
origin: LOOKS-TASK-37
severity: low
files: [tools/looks/glyphs.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: 59a3ad96
---

# CORR-LOOKS-073 — Fix the width-0 self-check that claims the pen stays put

Origin: [LOOKS-TASK-37](/docs/tasks/looks/37-a-tabela-de-glifos.md)

## Problema identificado

O self-check do `glyphs.py` "a code of width 0 draws nothing and does not move
the pen" e o comentário de `_check_image` ("the routine draws nothing and does
not move the pen") afirmam que um código de largura 0 deixa a caneta onde está.
`Font.run` ainda anda `spacing`, e `Font.width` também. O teste só passa porque
chama `width("@", 0)`. Com o espaçamento 2 dos rótulos, `@` anda 2 pixels, e se
o jogo faz isso não está medido.

## Evidência

```text
$ sed -n 140,152p tools/looks/glyphs.py
if char != " " and width: out.append(...)
x += width + spacing
$ grep -n "does not move the pen" tools/looks/glyphs.py
ok("a code of width 0 draws nothing and does not move the pen", empty.run("@", (0, 0), 2, ...) == [] and empty.width("@", 0) == 0)
$ python -c "import sys;sys.path.insert(0,'tools/looks');import glyphs;f=glyphs.Font(glyphs._toy_table());b=bytearray(f.table);b[2*(64-32)+1]=0;print(glyphs.Font(bytes(b)).width('@',2))"
2
```

## Causa raiz

(hipótese) A frase foi copiada do comportamento da fonte do título (kind 33,
§10.3 q), que de fato pula as duas coisas; não foi conferida contra o
tratamento de largura 0 no `SCREEN_GLYPH`.

## Correção

Ou medir o que o `SCREEN_GLYPH` faz com largura 0 mais espaçamento e alinhar
`Font.run`/`Font.width`, ou reescrever o check e o comentário e testar
explicitamente `empty.width("@", 2) == 2`.

## Arquivos

- tools/looks/glyphs.py

## Verificação

O comando `python -c` da evidência imprime o valor escolhido, e o nome e a
asserção do self-check concordam com ele; `python tools/looks/glyphs.py` segue
com `0 failure(s)`.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `16550b53`: **reproduzida**.

```text
glyphs.py:146  x += width + spacing
glyphs.py:152  return sum(self.glyph(ord(char))[2] + spacing for char in text)
glyphs.py:192  ok("a code of width 0 draws nothing and does not move the pen", ... empty.width("@", 0) == 0)
glyphs.py:252  # does not move the pen -- ...
$ python -c "... glyphs.Font(bytes(b)).width('@',2)"
2
```

Execução em 2026-09-22: **medido lendo o código do disco**, e o jogo faz o
que o `Font` já fazia — a caneta anda o espaçamento num código de largura 0.
Mudou o self-check e o comentário, não o código.

O que se leu, em `/SELECTC.BIN` (base `0x800FC000`), com os mesmos bytes no
disco japonês e no inglês (sha256 dos três trechos: `dc359aa0…`, `7365d847…`,
`3610cf53…`, iguais nos dois):

```text
SCREEN_GLYPH 8010bb4c..bb74  códigos 32..127: w = tabela[2*(c-32)+1] -> sh 0x1F8000C0, sem desvio para 0
passada que mede (SCREEN_PRINT)
  8010ae2c  lhu v0,192(0x1F80) ; addu s5,s5,v0          largura
  8010ae58  lb  v0,14(s4)      ; addu s5,s5,v0          espaçamento, pulado só para 0xDE/0xDF
passada que desenha (8010c4dc, kind 32 -> jal 8010bb04 com a3=0)
  8010c93c  espaço (32) pula o GsSortSprite (0x8003e8bc); largura 0 não pula
  8010c9c0  lhu v0,192 ; lb v1,14(s1) ; addu v0,v0,v1 ; addu s2,a0,v0   x += w + espaçamento
```

Antes e depois:

```text
antes  ok("a code of width 0 draws nothing and does not move the pen", ... empty.width("@", 0) == 0)
depois ok("a code of width 0 draws nothing and the pen moves by the spacing",
          run("@")==[] and width("@", 2) == 2 and run("@A") põe o A em x = 2)
$ python -c "... glyphs.Font(bytes(b)).width('@',2)"
2
$ python tools/looks/glyphs.py
  ok    a code of width 0 draws nothing and the pen moves by the spacing
glyphs.py: 0 failure(s)
controle: Font.run com `x += width + (spacing if width else 0)` numa cópia
  FAIL  a code of width 0 draws nothing and the pen moves by the spacing
glyphs.py: 1 failure(s)
```

Gates: `selftest.py` 0 failure(s) (101 de 101 controles vermelhos), `cli.py check`
12 ok, `glyphs.py --check-image` 0 problem(s) (`@ ^ ~` sem glifo).

Não medido ao vivo: nenhuma string da tela tem `@`, `^` ou `~` (`screen.json`),
então nenhum quadro do jogo exercita o caso; a leitura é estática, como a das
`V_BANDS`. E ela mostra uma diferença que fica registrada, não consertada: o
jogo **entrega** ao `GsSortSprite` um sprite de largura 0 (só o espaço é
pulado), e o `Font.run` não põe nada na lista. Na tela não aparece nada nos
dois casos; numa comparação de lista de sprites, apareceria.
- **Closed** — commit `59a3ad96` (2026-09-22): fix(looks): say a width-0 glyph still moves the pen by the spacing, as the game's code does
  - Files (`git show --name-status 59a3ad96`):
    - `M docs/tasks/looks/CORR-LOOKS-073.md`
    - `M tools/looks/glyphs.py`
