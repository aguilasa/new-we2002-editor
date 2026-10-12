---
id: CORR-KRP-001
---

# CORR-KRP-001 — Figure sem o membro pieces de §2.1, e a ausência fora da lista de desvios

Origin: [KRP-TASK-01](/docs/tasks/kits-replay/01-leitor-puro-core-replay-py-capture-v0v1-frame.md)

## Problem

A §2.1 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#2.1) lista estes membros de `Figure`:
`order`, `root`, `head`, `family`, `sleeves`, `armband`, `depth`, `off_axis`, `pieces`, `pose()` e
`box(index)`. O [core/replay.py](/tools/kits/core/replay.py) define todos menos `pieces`, porque
`Figure` herda de `list`. O Log da KRP-TASK-01 lista os desvios da §2.1 (parâmetros extras,
`frames(side)`, `kind`) e não menciona este. A KRP-TASK-04 monta a linha de comando a partir da
§2.1, e código escrito contra a API do plano (`figure.pieces`) dá `AttributeError`.

## Evidência

```text
$ cd tools/kits && python3 -c "import sys; sys.path.insert(0,'.'); from core.replay import Figure; print([a for a in ('order','root','head','family','sleeves','armband','depth','off_axis','pieces','pose','box') if not hasattr(Figure,a)])"
['pieces']
$ sed -n 70,91p docs/PLAN-KITS-REPLAY.md | grep -n pieces
`other`), `sleeves`, `armband`, `depth`, `off_axis`, `pieces`, `pose()` (o JSON de
```

## Root cause

(Hipótese.) Como `Figure` virou subclasse de `list`, as peças passaram a ser o próprio objeto, o
membro explícito pareceu redundante e não foi adicionado.

## Fix

Escolha uma das duas:

- adicionar `@property def pieces(self): return list(self)` a `Figure` em
  `tools/kits/core/replay.py`, com um caso de selftest que o leia;
- ou registrar a omissão no parágrafo de desvios do Log da KRP-TASK-01 e na §2.1 do plano.

## Arquivos a criar ou modificar

- `tools/kits/core/replay.py`
- `tools/kits/selftest.py`
- `docs/PLAN-KITS-REPLAY.md` (só no segundo caminho)

## Verificação

```sh
cd tools/kits && python3 -c "import sys; sys.path.insert(0,'.'); from core.replay import Figure; assert hasattr(Figure,'pieces')"
```

Hoje dá vermelho (`AssertionError`). No caminho da documentação, a verificação passa a ser a §2.1
não listar mais `pieces`.

## Log de Execução

2026-10-12 — reproduzida (`rite reproduce CORR-KRP-001`): o primeiro comando da Evidência imprime
`['pieces']`, e a §2.1 do plano lista `pieces` (linha 11 do recorte 70-91).

Caminho escolhido: o primeiro. `Figure.pieces` em `tools/kits/core/replay.py` devolve
`list(self)` — as peças, cabeça primeiro, como lista simples; a §2.1 continua certa e não muda.
Caso novo em `_replay_checks` do `tools/kits/selftest.py`: as duas figuras do caso de família
devolvem `list` com `[46, 2, 95, 93]` e `[46, 13]`.

Verificação:

```text
$ cd tools/kits && python3 -c "import sys; sys.path.insert(0,'.'); from core.replay import Figure; assert hasattr(Figure,'pieces'); print('ok')"
ok
```

Controle: `harness.run("replay", selftest._replay_checks)` dá `replay: 0 failure(s)`; com
`del replay.Figure.pieces` plantado antes, dá 1 falha —
`AttributeError at selftest.py:1510 in _replay_checks  'Figure' object has no attribute 'pieces'`.

Gates (`rite gates --cycle kits-replay --id CORR-KRP-001`): `ctest --test-dir build -R kits` —
`100% tests passed, 0 tests failed out of 4` (`kits_image` e `kits_ui` *skipped*); `python3
tools/kits/controls.py` — `controls: 55 of 55 red`.
- **Closed** — commit `6bdf17d2` (2026-10-12): fix(kits): Figure.pieces, the §2.1 member the replay reader left out
  - Files (`git show --name-status 6bdf17d2`):
    - `M docs/tasks/kits-replay/CORR-KRP-001.md`
    - `M tools/kits/core/replay.py`
    - `M tools/kits/selftest.py`
