---
id: CORR-LOOKS-078
title: "A linha de falha de glifo mostra o primeiro da linha, não o que difere"
origin: LOOKS-TASK-38
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
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
