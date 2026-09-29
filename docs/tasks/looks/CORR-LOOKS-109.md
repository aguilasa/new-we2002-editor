---
id: CORR-LOOKS-109
title: "BOOTS desenha a mesma chuteira para todo valor na tela LOOKS SET"
origin: LOOKS-TASK-13
severity: high
files: [tools/looks/looks.py, tools/looks/screen.py, tools/looks/ui_check.py, tools/looks/controls.py]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-29
done_commit: 533d16b
---

# CORR-LOOKS-109 — BOOTS desenha a mesma chuteira para todo valor na tela LOOKS SET

Origin: [LOOKS-TASK-13](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)

## Problem

Teste manual de 2026-09-29: na tela `LOOKS SET`, trocar o valor da linha
`BOOTS` muda o texto (`A TYPE` .. `H TYPE`) e não muda a figura — o painel
desenha sempre a chuteira A, preta. No jogo, `E TYPE` é vermelha.

## Evidência

O efeito em si estava certo: a lista de desenho, pedida com `boots` nos
valores, anda a janela de paleta das 112 primitivas das seções 9 e 10 de
`(0,484)` a `(112,484)`, e as oito janelas diferem no disco. O que não chegava
era o valor:

```text
$ work/venv-looks/bin/python tools/looks/ui/app.py --keys "Up x3,Right x4" --smoke
  row BOOTS     = 'E TYPE'
  tuple A-A1-A-A-A, scene built 1 time(s)
```

A linha andou, a tupla não, e nenhuma cena nova foi montada.

## Root cause

A janela monta a figura a partir de `State.tuple_text()`, que é
`looks.format_tuple` — e a tupla é a do corpus, os cinco campos de
`TUPLE_ORDER` (pele, cabelo, cor, barba, cor da barba). `boots` não está nela,
então o valor se perdia entre a tela e o `Builder`, e a troca da linha nem
disparava o `redraw` (que compara o texto antes e depois). O gate
`looks_ui` repetia a mesma lista: `ui_check.TUPLE_ROWS` eram as cinco linhas
da tupla, e `BOOTS` nunca foi exigida chegar à figura.

## Fix

- `looks.TUPLE_EXTRA = ("boots",)`: `parse_tuple` aceita uma sexta parte
  opcional e `format_tuple` a escreve quando os valores a trazem. O corpus
  continua com cinco partes.
- `ui_check.TUPLE_ROWS` ganha `BOOTS`, então o gate agora pressiona a linha e
  exige uma cena nova.
- O controle `looks-tuple-any-length` passa a plantar sobre a guarda nova.

## Arquivos a criar ou modificar

- `tools/looks/looks.py`
- `tools/looks/screen.py` (docstring)
- `tools/looks/ui_check.py`
- `tools/looks/controls.py`

## Verificação

```text
$ python3 tools/looks/selftest.py
looks_selftest: 0 failure(s)          # 109 de 109 controles vermelhos
$ python3 tools/looks/ui_check.py
looks_ui: 21 of 21 negative control(s) red, and the window drew every tuple ...
$ python3 tools/looks/oracle.py --keys "Up x3,Right x4" 2
oracle --keys: 0 difference(s) after 7 press(es), across the game, screen.json and our window
```

Na captura do `--keys` o jogo e a janela desenham a chuteira E vermelha; com
`BOOTS` em A a janela desenha a preta (0,73% dos pixels diferem entre as duas).

## Log de Execução

- 2026-09-29: consertado e medido contra o jogo no slot 2.
- **Closed** — commit `533d16b` (2026-09-29): fix(looks): the BOOTS row reaches the figure
  - Files (`git show --name-status 533d16b`):
    - `A docs/tasks/looks/CORR-LOOKS-109.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/controls.py`
    - `M tools/looks/looks.py`
    - `M tools/looks/screen.py`
    - `M tools/looks/ui_check.py`
