---
id: CORR-LOOKS-072
title: "Say 'within 16 per channel', not 'pixel a pixel', for the labels"
origin: LOOKS-TASK-37
severity: medium
files: [docs/PLAN-LOOKS-PY.md, docs/prompts/perfil-looks.md, tools/looks/confront.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: e18fe0bb
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

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `16550b53`: **reproduzida**.

```text
1913:OUTSIDE_SLACK = 16
$ python tools/looks/confront.py --outside
labels, pixel for pixel: 0 of 16416 differ (the game against itself: 0; the game one pixel off: 2875)   [slots 2 e 1]
labels       game (0, 49, 49)     ours (0, 53, 55)       6 apart
confront --outside: 0 problem(s) over 2 slot(s)
# varredura de folga (rascunho sobre ink_differences, caixa text_regions()["labels"]), os dois slots:
slack 0 differ 11839 / slack 4 differ 11839 / slack 8 differ 0 / slack 16 differ 0
# grep "pixel a pixel|pixel for pixel", nenhuma qualificada pela folga:
tools/looks/confront.py:2101, 2109; docs/PLAN-LOOKS-PY.md:3115; docs/prompts/perfil-looks.md:761
```

Correção em 2026-09-22 (correção principal, sem emulador): as três frases
passam a dizer "dentro de `OUTSIDE_SLACK` (16) por canal", mantendo os números
medidos na triagem (0 de 16.416, controle 2.875; sem folga 11.839, fundo a ~6).
O limiar alternativo não entrou: ele exigiria rodar o `--outside` para medir.

- `tools/looks/confront.py`: o comentário antes de `label_box` explica a folga e
  o número sem ela; a linha impressa vira
  `labels, pixel for pixel within 16 per channel: …` (o 16 sai de `OUTSIDE_SLACK`).
- `docs/PLAN-LOOKS-PY.md` §10.3 (o): "pixel a pixel dentro de `OUTSIDE_SLACK`
  (16) por canal", mais o número sem folga e o link para esta CORR.
- `docs/prompts/perfil-looks.md`, linha do gate `--outside`: a mesma frase.

```text
$ grep -n "pixel a pixel\|pixel for pixel" docs/PLAN-LOOKS-PY.md docs/prompts/perfil-looks.md tools/looks/confront.py
# (antes: 3115, 761, 2101, 2109, nenhuma qualificada)
docs/PLAN-LOOKS-PY.md:3115:> **pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal** com o quadro do
docs/prompts/perfil-looks.md:761:… os **rótulos pixel a pixel dentro de `OUTSIDE_SLACK` (16) por canal** — sem folga divergem, o fundo fica a ~6 — …
tools/looks/confront.py:2112:        print("    labels, pixel for pixel within %d per channel: %d of %d "
# as demais (PLAN 112, 1707, 1830, 2394, 2469; perfil 998) falam da repetição
# da captura e da §5.6, não dos rótulos -- fora do escopo
$ python -c "import ast;ast.parse(open('tools/looks/confront.py',encoding='utf-8').read())"   -> ok
$ python tools/looks/selftest.py
..... 100 of 100 controls red
looks_selftest: 0 failure(s)
$ rite check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

A linha impressa nova não foi vista numa corrida do `--outside` (emulador
ocupado); a próxima corrida desse alvo a confirma.
- **Closed** — commit `e18fe0bb` (2026-09-22): docs(looks): say the labels match within OUTSIDE_SLACK per channel, not pixel for pixel
  - Files (`git show --name-status e18fe0bb`):
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/CORR-LOOKS-072.md`
    - `M tools/looks/confront.py`
