---
id: CORR-LOOKS-108
---

# CORR-LOOKS-108 — O mapa de cabelo guarda quatro faixas para o K1, e o K1 não grava nenhuma

Origin: [LOOKS-TASK-14](/docs/tasks/concluidos/looks/14-tabela-de-montagem.md)

## Problem

O `assembly.HAIR_MAP` guarda para o K1 as faixas (0, 1, 3, 4) da seção 32, e a
CORR-LOOKS-104 o deixou como o único estilo de faixa múltipla, "cuja reescrita
não é passo de faixa". Conferido contra o jogo em 2026-09-29, o K1 não grava
cabelo nenhum: as quatro faixas não descrevem nada que o jogo desenhe.

## Evidência

A seção 32 lida assentada no K1 (duas leituras 300 quadros apartadas iguais,
o método do `--colour`), nas duas figuras e com duas tuplas de cor, comparada
com o disco:

```text
2 A-K1-A-A-A {10: 9}
2 C-K1-D-A-A {10: 9}
1 A-K1-A-A-A {10: 9}
1 C-K1-D-A-A {10: 9}
all equal: True
```

Só a primitiva 10 difere do disco, e ela é da coluna 9: um quad de barba, que o
FACE cuida. Nenhum quad de cabelo foi reescrito. No `--patched HAIR`, a seção 32
já "differs from the disc" no valor 0, antes de qualquer K1: os save states a
trazem alterada, e o que o passo 24 grava é a volta ao disco.

Com o jogo capturado no mesmo ângulo de giro que a janela usa parada (−240),
J1 e K1 saem iguais nos dois lados:
`work/looks-corr108/k1same.png`, fora do git.

## Root cause

A [LOOKS-TASK-14](/docs/tasks/concluidos/looks/14-tabela-de-montagem.md) tirou as faixas
do que cada passo **grava**, e comparou contra o estado anterior, não contra o
disco. Um passo que restaura bytes alterados pelo save state aparece como
escrita. No K1 isso produziu quatro faixas de algo que o jogo só devolve.

## Fix

Em `tools/looks/assembly.py`: K1 → (32, ()) nos dois mapas, e
`HAIR_MAP_MULTI_BAND` 1 → 0. Os casos do self-check que exigiam "K1 é o único
de faixa múltipla" passam a exigir nenhum. No
[plano](/docs/PLAN-LOOKS-PY.md), o fechamento dos quads deixa de dizer que o K1
resta. O desenho não muda: a seção 32 não está em `layout.HAIR_QUADS`, então as
quatro faixas nunca eram aplicadas.

## Arquivos a criar ou modificar

- [tools/looks/assembly.py](/tools/looks/assembly.py)
- [docs/PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)

## Verificação

```text
$ python3 tools/looks/assembly.py --check | tail -1
assembly.py: 0 failure(s)
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
$ python3 tools/looks/cli.py check | tail -1
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```

## Log de Execução

- 2026-09-29 — K1 lido assentado nos dois slots; comparado com o jogo no mesmo
  giro; mapa corrigido.
- **Closed** — commit `14442eb` (2026-09-29): fix(looks): K1 writes no hair band, so the map keeps none
  - Files (`git show --name-status 14442eb`):
    - `M docs/PLAN-LOOKS-PY.md`
    - `A docs/tasks/looks/CORR-LOOKS-108.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/assembly.py`
