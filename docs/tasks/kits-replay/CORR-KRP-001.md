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
