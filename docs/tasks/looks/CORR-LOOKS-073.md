---
id: CORR-LOOKS-073
title: Fix the width-0 self-check that claims the pen stays put
origin: LOOKS-TASK-37
severity: low
files: [tools/looks/glyphs.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
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
