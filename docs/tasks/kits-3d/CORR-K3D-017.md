---
id: CORR-K3D-017
---

# CORR-K3D-017 — Documentos e docstrings ainda descrevem a figura de partida e o ARM_PIECES antigo

Origin: [K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md)

## Problem

A [K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md) fechou o veredito "a figura de partida sai da janela; o `ARM_PIECES` mora no
núcleo", mas texto que dizia o anterior ficou como estava:

- o G3 (`docs/KITS-AJUSTES-3D.md:101`) ainda diz "A tabela é `ARM_PIECES` de
  `tools/kits/oracle.py`";
- a §4.3 do `docs/PLAN-KITS-PY.md` ainda tem o parágrafo "A figura de partida na aba 3D,
  desde 2026-10-06" e diz "Na aba a figura é vista no referencial do próprio torso", sem
  nota de que a janela não a mostra mais;
- os docstrings de módulo com o contrato dão a assinatura antiga, sem `armband`/`sleeves`:
  `tools/kits/core/api.py:23` e `tools/kits/core/figure.py:10`.

## Evidência

```text
$ grep -n "ARM_PIECES. de .tools/kits/oracle.py" docs/KITS-AJUSTES-3D.md
101:matriz e o lugar que a figura dá a essa peça. A tabela é `ARM_PIECES` de `tools/kits/oracle.py`, e
$ grep -n "A figura de partida na aba 3D" docs/PLAN-KITS-PY.md
793:**A figura de partida na aba 3D, desde 2026-10-06 (...).**
$ grep -n "frame=None)$" tools/kits/core/api.py tools/kits/core/figure.py
tools/kits/core/api.py:23:    api.figure(kit, kit_set, figure, geometry_path=None, frame=None)
tools/kits/core/figure.py:10:    scene = figure.scene_of(kit, kit_set, figure, geometry_path=None, frame=None)
```

## Root cause

A varredura passou pelo G3/G4 e pela §3.4 do plano, as seções que a task nomeou, mas não
por todo lugar que repete a decisão (regra "fechar um veredito é varrer quem dizia o
anterior").

## Fix

No G3 de `docs/KITS-AJUSTES-3D.md`, apontar `ARM_PIECES` para `tools/kits/core/figure.py`
(que o `oracle.py` importa). Na §4.3 de `docs/PLAN-KITS-PY.md`, acrescentar a nota datada
de que desde a K3D-TASK-10 a janela não desenha a figura de partida (o núcleo e o
`--match-silhouette` continuam). Nos docstrings de `tools/kits/core/api.py` e
`tools/kits/core/figure.py`, acrescentar `armband=False, sleeves="short"`. Os quatro
arquivos estão no `files` declarado da task.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md
- docs/PLAN-KITS-PY.md
- tools/kits/core/api.py
- tools/kits/core/figure.py

## Verificação

```sh
grep -n "ARM_PIECES. de .tools/kits/oracle.py" docs/KITS-AJUSTES-3D.md
grep -n "frame=None)$" tools/kits/core/api.py tools/kits/core/figure.py
```

Os dois têm de não imprimir nada, e a §4.3 do plano (perto da linha 793) tem de trazer a
nota da K3D-TASK-10.

## Log de Execução
