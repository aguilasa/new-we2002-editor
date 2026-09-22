---
id: CORR-LOOKS-072
title: "Say 'within 16 per channel', not 'pixel a pixel', for the labels"
origin: LOOKS-TASK-37
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-072 — Say 'within 16 per channel', not 'pixel a pixel', for the labels

Origin: [LOOKS-TASK-37](/docs/tasks/looks/37-a-tabela-de-glifos.md)

## Problema identificado

O plano (§10.3 o), o log da LOOKS-TASK-37, a mensagem do commit `0297ea1c` e a
linha do gate no perfil dizem que os rótulos "batem pixel a pixel" com o jogo
(0 de 16.416). A comparação conta, na verdade, pixels cuja maior distância de
canal passa de `OUTSIDE_SLACK = 16`. Sem folga, 11.839 dos 16.416 pixels da
coluna de rótulos diferem nos dois slots, porque o fundo da faixa nosso fica a
~6 do do jogo. O check é útil, e o controle de 1 pixel de deslocamento fica
vermelho (2.875); a frase, porém, lê como igualdade exata.

## Evidência

```text
$ grep -n "^OUTSIDE_SLACK" tools/looks/confront.py
1913:OUTSIDE_SLACK = 16
$ python tools/looks/confront.py --outside
labels, pixel for pixel: 0 of 16416 differ (the game against itself: 0; the game one pixel off: 2875)
labels       game (0, 49, 49)     ours (0, 53, 55)       6 apart

# script de rascunho: still_frame do jogo contra work/looks-confront/ours-outside-N.png,
# caixa text_regions()["labels"], variando a folga
slot 2 slack 0 differ 11839 / slack 4 differ 11839 / slack 8 differ 0 / slack 16 differ 0
slot 1 slack 0 differ 11839 / slack 4 differ 11839 / slack 8 differ 0 / slack 16 differ 0
```

## Causa raiz

`ink_differences` reusa a folga da cor de fundo, e a prosa foi escrita a partir
da linha impressa "pixel for pixel".

## Correção

Reescrever `docs/PLAN-LOOKS-PY.md` §10.3 (o), `docs/prompts/perfil-looks.md`
(linha do gate `--outside`) e a linha impressa em `tools/looks/confront.py`
para dizer "dentro de `OUTSIDE_SLACK` (16) por canal". Alternativa: um limiar
de tinta próprio para os rótulos, derivado do desvio de fundo medido.

## Arquivos

- docs/PLAN-LOOKS-PY.md
- docs/prompts/perfil-looks.md
- tools/looks/confront.py

## Verificação

`grep -n "pixel a pixel\|pixel for pixel" docs/PLAN-LOOKS-PY.md
docs/prompts/perfil-looks.md tools/looks/confront.py` mostra cada ocorrência
qualificada pela folga.

## Log de Execução
