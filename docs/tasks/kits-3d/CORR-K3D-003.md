---
id: CORR-K3D-003
---

# CORR-K3D-003 — G5 "Hoje" e api.numbered ainda dizem que a cópia das costas exige Number

Origin: [K3D-TASK-05](/docs/tasks/kits-3d/05-costas-sempre.md)

## Problem

A [K3D-TASK-05](/docs/tasks/kits-3d/05-costas-sempre.md) passou a aplicar a cópia das
costas (`BACK_COPY`) sempre, e acrescentou ao G5 do `KITS-AJUSTES-3D.md` um parágrafo
"Decisão nova" e uma seção "Feito". A lista "Hoje" logo acima continua dizendo, no
presente, que a cópia só acontece com Number marcado e que a dica da aba "explica o
vazado" — dica que o mesmo commit removeu. As referências de linha também ficaram
velhas: `BACK_COPY` está em `core/figure.py:357`, não `:351`, e `ui/i18n.py:79-82` não
traz mais dica de vazado. O docstring de `api.numbered` tem o mesmo defeito: descreve
acrescentar o painel das costas, que agora já vem de `figure()`. A regra "fechar um
veredito é varrer quem dizia o anterior" exige a mudança na mesma task.

## Evidência

```text
$ grep -n "só acontece \*\*com Number marcado\|core/figure.py:351\|explica o vazado" docs/KITS-AJUSTES-3D.md
137:  (44,6) no jogador e (108,6) no goleiro (`BACK_COPY`, `core/figure.py:351`; medido na §4.7). Aqui
138:  a cópia só acontece **com Number marcado** (`api.numbered`, `ui/app.py:619-625`). Na figura de
147:- **A dica da aba explica o vazado** (`ui/i18n.py:79-82`). Ela foi escrita sob a decisão de
$ grep -n "^BACK_COPY" tools/kits/core/figure.py
357:BACK_COPY = {0: (44, 6), 1: (108, 6)}
```

## Root cause

Hipótese: a task acrescentou "Decisão nova" e "Feito" ao G5 sem revisitar os itens de
"Hoje", que descrevem o estado anterior ao conserto.

## Fix

No G5 do `docs/KITS-AJUSTES-3D.md`, marcar os itens de "Hoje" que mudaram (a cópia só
com Number; a dica que explica o vazado) como o estado antes da K3D-TASK-05, ou
reescrevê-los, e corrigir as referências de linha. No `tools/kits/core/api.py`, dizer
no docstring de `numbered` que ele só pinta o número, porque a cópia das costas já vem
de `figure()`.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md
- tools/kits/core/api.py

## Verificação

```sh
grep -n "só acontece \*\*com Number marcado\|core/figure.py:351\|explica o vazado" docs/KITS-AJUSTES-3D.md
```

Imprime 3 linhas hoje; tem de não imprimir nada depois da correção.

## Log de Execução

- 2026-10-07 — triagem inline: **REPRODUCED**. O `grep` da Evidência imprimia as linhas
  137, 138 e 147 do `KITS-AJUSTES-3D.md`; `BACK_COPY` está em `core/figure.py:357`.
- G5 "Hoje" marcado como estado antes da K3D-TASK-05; os dois itens que ela mudou (cópia
  só com Number, dica do vazado) dizem o que mudou, com as linhas atuais
  (`core/figure.py:357`, `ui/app.py:629-632`, `ui/i18n.py:79-82`). Docstring de
  `api.numbered` diz que só pinta os dígitos.
- Verificação: o `grep` não imprime nada (exit 1). `python3 tools/kits/selftest.py`:
  `controls: 0 failure(s)`, `kits_selftest: 0 failure(s)`.
- **Closed** — commit `4a7952e` (2026-10-07): docs(kits): mark G5 'Hoje' as the state before K3D-TASK-05
  - Files (`git show --name-status 4a7952e`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-003.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/core/api.py`
