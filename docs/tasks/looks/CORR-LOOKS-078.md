---
id: CORR-LOOKS-078
title: "A linha de falha de glifo mostra o primeiro da linha, não o que difere"
origin: LOOKS-TASK-38
severity: low
files: [tools/looks/oracle.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: ac1fa29b
---

# CORR-LOOKS-078 — A linha de falha de glifo mostra o primeiro da linha, não o que difere

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

O `_glyph_differences` imprime `theirs[:1]` e `ours[:1]` — o glifo mais à
esquerda da linha de cada lado. Quando o glifo mais à esquerda é o rótulo da
linha (que não mudou) e o valor deslocado está à direita dele, os dois lados
imprimem a mesma tupla e a linha de falha não diz nada sobre o defeito.

## Evidência

```text
$ python -c "import sys;sys.path.insert(0,'tools/looks');import oracle;\
print(oracle._glyph_differences([(200,41,184,146),(421,41,46,158)],[(200,41,184,146),(176,41,46,158)]))"
['the glyphs on line y 41: the game draws 2 starting [(200, 41, 184, 146)], our window 2 starting [(200, 41, 184, 146)]']
```

## Causa raiz

A intenção do docstring — "o começo de um valor deslocado é o que se lê" — não
casa com o código: o primeiro glifo da linha não é o primeiro glifo que difere.
A transcrição do defeito plantado na task pareceu informativa só porque o valor
alinhado à esquerda caiu à esquerda do rótulo.

## Correção

Relatar o primeiro glifo em que as duas listas ordenadas divergem (o primeiro
elemento da diferença simétrica de cada lado) em vez de `[:1]`.

## Arquivos

- tools/looks/oracle.py (`_glyph_differences`)

## Verificação

O comando acima nomeia `(421, 41, 46, 158)` contra `(176, 41, 46, 158)`.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**, saída idêntica à da Evidência.

```text
$ python -c "... oracle._glyph_differences([(200,41,184,146),(421,41,46,158)],[(200,41,184,146),(176,41,46,158)])"
['the glyphs on line y 41: the game draws 2 starting [(200, 41, 184, 146)], our window 2 starting [(200, 41, 184, 146)]']
```

### O conserto

`_glyph_differences` passou a nomear, de cada lado, o **primeiro glifo que o
outro lado não desenha** — a diferença de multiconjuntos da linha, calculada
por um auxiliar novo, `_glyphs_only_here`. Multiconjunto e não conjunto: o
mesmo glifo duas vezes na linha são dois glifos, e um valor que perdeu um de
um par repetido difere por esse um.

Duas consequências, as duas dentro do escopo do defeito:

- a linha entra no relatório quando **há um glifo a nomear**, em vez de por
  comparação elemento a elemento. Como os dois lados chegam ordenados
  (`frame_glyphs` e `ui_check.read_screen` ordenam), é o mesmo conjunto de
  linhas de antes, menos o único caso que a regra velha reportaria sem ter o
  que dizer;
- as duas listas são coagidas a tuplas na entrada, para que a comparação não
  dependa de a leitura ter passado ou não por JSON.

Depois:

```text
$ python -c "... oracle._glyph_differences([(200,41,184,146),(421,41,46,158)],[(200,41,184,146),(176,41,46,158)])"
['the glyphs on line y 41: the game draws 2, the first the window lacks [(421, 41, 46, 158)]; our window 2, the first the game lacks [(176, 41, 46, 158)]']
```

É o que a Verificação pede: `(421, 41, 46, 158)` contra `(176, 41, 46, 158)`,
e o rótulo `(200, 41, 184, 146)` — que não se moveu — fora da frase.

### O self-check

Quatro asserções novas no `_checks` do `oracle.py`, sobre glifos montados ali
mesmo (sem emulador, como o resto do gate), com o caso do rótulo intacto no
meio:

```text
  ok    a value moved beside an unchanged label names the moved glyph
  ok    and not the label, which the two sides draw alike
  ok    a line drawn the same on both sides says nothing
  ok    a glyph one side draws and the other does not is named on its own
```

A primeira é o defeito do CORR; a segunda é o **controle** que separa o
conserto da versão antiga (com `[:1]` ela ficava vermelha, porque a frase
nomeava o rótulo); a terceira exige silêncio onde não há diferença; a quarta
fixa a frase inteira quando um lado tem um glifo a mais.

### Gates

```text
$ python tools/looks/oracle.py --check
oracle.py: 0 failure(s)
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)      (rule 1 swept 27 file(s), 30094 line(s);
                                   102 of 102 controls red)
$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```

Sem emulador nesta corrida (outro trabalhador segurava o DuckStation), então
`--keys`, que é quem imprime essa frase de verdade, não foi rodado: o que se
mediu foi a função, direto, e é dela que a frase sai.
- **Closed** — commit `ac1fa29b` (2026-09-22): fix(looks): name the first glyph that differs, not the first of the line
  - Files (`git show --name-status ac1fa29b`):
    - `M docs/tasks/looks/CORR-LOOKS-078.md`
    - `M tools/looks/oracle.py`
