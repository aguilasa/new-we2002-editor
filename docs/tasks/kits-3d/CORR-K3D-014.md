---
id: CORR-K3D-014
---

# CORR-K3D-014 — --keeper-armband conta figuras cortadas como inteiras (27 contra 23)

Origin: [K3D-TASK-08](/docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md)

## Problem

O `run_keeper_armband` da [K3D-TASK-08](/docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md) imprime `len(report["figures"])` como "whole figure(s)",
mas o `matrix_report` guarda em `figures` também as figuras cortadas (última peça `None`)
e só as deixa fora de `orders`. A saída diz 27 figuras inteiras enquanto a única linha de
ordem é x23; o G4 cola essa linha e logo abaixo diz "Nas 23 figuras inteiras", e o
documento se contradiz. A linha de dispersão "153 to 196" também inclui as 4 cortadas, e
`report["cut"]` nunca é impresso.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --keeper-armband 7 --frame-json work/kits-oracle/matrix-7.json | grep -E "whole|x23"
  600 stop(s); 27 whole figure(s) opened at section 13, in the order:
    x23  34 13 14 16 92 17 18 20 11 19 21 12
$ grep -n "23 figuras inteiras" docs/KITS-AJUSTES-3D.md
230:- **A 92 entra no lugar da 15.** Nas 23 figuras inteiras, o goleiro desenha ...
```

Pelo revisor, chamando `matrix_report` direto na HEAD: `figures 27`, `cut 4`, as quatro
cortadas `[34, 13, 14, 16, 92, 17, 18, 20, 11, 19, 21, None]`.

## Root cause

O rótulo foi copiado sem levar em conta que `matrix_report` mantém as cortadas em
`figures`.

## Fix

No `run_keeper_armband` de `tools/kits/oracle.py`, imprimir as inteiras e as cortadas em
separado (`len(figures) - cut` e `cut`), e a dispersão só das inteiras. Recolar o bloco
de saída do G4 em `docs/KITS-AJUSTES-3D.md` a partir da HEAD e atualizar o Log da task.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md
- docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --keeper-armband 7 --frame-json work/kits-oracle/matrix-7.json | grep -c "27 whole"
```

Hoje imprime 1; depois, 0, com "23 whole … 4 cut" na saída.

## Log de Execução

- 2026-10-08 — triagem inline: **REPRODUCED**. `--keeper-armband 7 --frame-json …` imprimia
  `27 whole figure(s)` com uma só linha de ordem, `x23`.
- `oracle.py`: `matrix_report` marca cada figura com `cut`; o `run_keeper_armband` imprime inteiras e
  cortadas em separado e a faixa de translação só das inteiras. G4 recolado da HEAD e Log da
  K3D-TASK-08 com a nota.
- Verificação:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --keeper-armband 7 --frame-json work/kits-oracle/matrix-7.json | grep -E "whole|x23"
  600 stop(s); 23 whole and 4 cut figure(s) opened at section 13; the whole ones in the order:
    x23  34 13 14 16 92 17 18 20 11 19 21 12
  every whole figure's translations within 153 to 184 of its median (limit 500)
```

  `grep -c "27 whole"` → 0. `selftest.py`: `kits_selftest: 0 failure(s)`.
- **Closed** — commit `062b552` (2026-10-08): fix(kits): count whole and cut goalkeeper figures apart in --keeper-armband
  - Files (`git show --name-status 062b552`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md`
    - `M docs/tasks/kits-3d/CORR-K3D-014.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`
