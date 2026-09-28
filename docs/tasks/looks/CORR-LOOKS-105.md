---
id: CORR-LOOKS-105
title: "H1, M1 e N1 não desenham cabeça nenhuma"
origin: LOOKS-TASK-14
severity: medium
files: [tools/looks/assembly.py, tools/looks/layout.py, tools/looks/ui_check.py, tools/looks/confront.py, tools/looks/ui/looks_set.py, docs/PLAN-LOOKS-PY.md]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-28
done_commit: 9696c38
---

# CORR-LOOKS-105 — H1, M1 e N1 não desenham cabeça nenhuma

Origin: [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md)

## Problem

Na linha HAIR, os estilos H1, M1 e N1 deixam o painel vazio: a janela não
desenha cabeça nenhuma. Achado em teste manual pelo usuário em 2026-09-28. No
jogo, os três têm cabelo próprio.

## Evidência

O `assembly.HAIR_MAP` tinha `None` nos três, e o `head_of` os recusava. O
`--patched HAIR` confirma que nenhum dos três grava nada:

```text
$ python3 tools/looks/oracle.py --patched HAIR 2
      19  changed: nothing   |   differs from the disc in: 24, 26, 28, 30, 32, 48, 52, 54
      28  changed: nothing   |   ...
      29  changed: nothing   |   ...
```

O que o jogo **desenha**, lido do ponteiro de modelo da carga de matriz da
cabeça (`oracle._pose_cycle`, o mesmo leitor da pose), com cada estilo na tela:

```text
slot 2 A1 ( 0): MODEL sections drawn [('MODEL.BIN', 24)]
slot 2 G1 (18): MODEL sections drawn [('MODEL.BIN', 28)]
slot 2 H1 (19): MODEL sections drawn [('MODEL.BIN', 42)]
slot 2 M1 (28): MODEL sections drawn [('MODEL.BIN', 38)]
slot 2 N1 (29): MODEL sections drawn [('MODEL.BIN', 40)]
slot 2 O1 (30): MODEL sections drawn [('MODEL.BIN', 44)]
slot 1: as mesmas seis linhas
```

A1, G1 e O1 são os controles, e caem nas seções que o mapa já tinha.

## Root cause

A [LOOKS-TASK-14](/docs/tasks/looks/14-tabela-de-montagem.md) mediu o mapa pelo
que cada passo **grava** em `MODEL.BIN`. H1, M1 e N1 não gravam nada porque a
janela do disco das seções 42, 38 e 40 já é a deles, e por isso o mapa ficou
sem resposta. O plano registrava o buraco e dizia o que o destravaria: ler o que
o jogo desenha. Faltava fazer essa leitura.

## Fix

- `HAIR_MAP` e `HAIR_MAP_GOALKEEPER`: H1 → (42, ()), M1 → (38, ()), N1 →
  (40, ()), sem faixa porque nada é gravado. `HAIR_MAP_SILENT` 3 → 0 e
  `HAIR_MAP_SECTIONS` 13 → 16, nas duas figuras.
- As cores das seis cabeças novas (38 a 43), medidas pelo `--colour` a partir
  de A-H1, A-M1 e A-N1, e das mesmas com barba F para as gêmeas:
  `layout.COLOUR_PRIMITIVES` de SKIN, H.COL, H.F.COL. e FACE.
- As gêmeas e os quads de barba, pelo `--patched FACE` a partir dos três:
  `FACE_TWINS` 38→39, 40→41 e 42→43, e `layout.FACE_TWIN_QUADS` 39 e 41 →
  (7, 10, 11) e 43 → (8, 13).
- A recusa continua testada. Nenhum valor da tela é recusado agora, então o
  self-check planta H1 de volta a `None` no `HAIR_MAPS`. O `ui_check` roda os
  dois julgamentos de recusa numa cópia da árvore com a mesma planta
  (`REFUSAL_PLANT`) e exige que, sem a planta, H1 desenhe.
- Textos: `confront.py`, `ui/looks_set.py` e os dois itens abertos da tabela
  de montagem no [plano](/docs/PLAN-LOOKS-PY.md), agora fechados.

## Arquivos a criar ou modificar

- [tools/looks/assembly.py](/tools/looks/assembly.py)
- [tools/looks/layout.py](/tools/looks/layout.py)
- [tools/looks/ui_check.py](/tools/looks/ui_check.py)
- [tools/looks/confront.py](/tools/looks/confront.py)
- [tools/looks/ui/looks_set.py](/tools/looks/ui/looks_set.py)
- [docs/PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)

## Verificação

```text
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
$ python3 tools/looks/cli.py check | tail -1
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
$ python3 tools/looks/ui_check.py | grep -E 'refus|H1|looks_ui'
  A-H1-A-A-A, planted back to a refusal, exits 2 and writes no picture
  H1 TYPE is refused on the screen: the row keeps the game's text, ...
  and unplanted, A-H1-A-A-A draws
looks_ui: 21 of 21 negative control(s) red, ...
$ for n in 19 28 29; do python3 tools/looks/oracle.py --keys "Down x2,Right x$n" 2; done
oracle --keys: 0 difference(s) ...   (três vezes)
```

As capturas de jogo e janela de H1, M1 e N1, lado a lado, estão em
`work/looks-corr105/h1grid.png`, fora do git. As três cabeças batem: H1 de topo
reto, M1 com o bico na testa, N1 com o cabelo comprido. O que sobra de
diferença é o giro do close-up (§10.3 (p) do plano).

## Log de Execução

- 2026-09-28 — lida a seção desenhada nos dois slots, com controles; medidas
  cores, gêmeas e quads de barba; corrigido; selftest, check-image, ui_check e
  a comparação de tela verdes.
- **Closed** — commit `9696c38` (2026-09-28): fix(looks): draw H1, M1 and N1 with the heads the game draws for them
  - Files (`git show --name-status 9696c38`):
    - `M docs/PLAN-LOOKS-PY.md`
    - `A docs/tasks/looks/CORR-LOOKS-105.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/assembly.py`
    - `M tools/looks/confront.py`
    - `M tools/looks/layout.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui_check.py`
