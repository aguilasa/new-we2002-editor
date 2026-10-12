---
id: CORR-K3D-033
---

# CORR-K3D-033 — Linhas $ do --replay --focus no G8 sem --frame-json não produzem a saída colada

Origin: [K3D-TASK-19](/docs/tasks/kits-3d/19-medir-capitao-linha-replay.md)

## Problem

O G8 escreve `$ python3 tools/kits/oracle.py --replay 9 --focus 3` (e `10 --focus 3`,
`10 --focus 2`) com saída começando por `capture read from work/kits-oracle/replay-9-3.json,
no emulator`. O `run_replay` só lê a captura guardada quando recebe `--frame-json`
(`if cache and os.path.isfile(cache)`). Rodado como está escrito, o comando sobe o
emulador, captura de novo e imprime `capture kept at …`. A saída colada no G8 pela [K3D-TASK-19](/docs/tasks/kits-3d/19-medir-capitao-linha-replay.md) não
é a que o comando citado produz.

## Evidência

```text
$ grep -n '^\$ python3 tools/kits/oracle.py --replay [0-9]* --focus [0-9]*$' docs/KITS-AJUSTES-3D.md
1167:$ python3 tools/kits/oracle.py --replay 9 --focus 3
1223:$ python3 tools/kits/oracle.py --replay 10 --focus 3
1279:$ python3 tools/kits/oracle.py --replay 10 --focus 2
$ sed -n 3545,3561p tools/kits/oracle.py
    path = cache or os.path.join(ATTACH_DIR, name + ".json")
    if cache and os.path.isfile(cache):
        ...
        print("  capture read from %s, no emulator" % cache)
```

O revisor confirmou por `diff` que, com `--frame-json work/kits-oracle/replay-<slot>-<K>.json`,
as três saídas batem com o G8.

## Root cause

A corrida usou `--frame-json`, e a linha `$` foi escrita sem ele.

## Fix

No G8 de `docs/KITS-AJUSTES-3D.md` e nos itens do Log da task, escrever
`--frame-json work/kits-oracle/replay-<slot>-<K>.json` nas três linhas `$ … --replay … --focus`
— ou colar a saída da captura ao vivo.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md
- docs/tasks/kits-3d/19-medir-capitao-linha-replay.md

## Verificação

```sh
grep -n '^\$ python3 tools/kits/oracle.py --replay [0-9]* --focus [0-9]*$' docs/KITS-AJUSTES-3D.md
```

Hoje imprime três linhas; depois, nada.

## Log de Execução

### 2026-10-12 — `--frame-json` nas três linhas `$`

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `d348951`. O `grep`
achou as linhas 1167, 1223 e 1279 sem `--frame-json`, e o `sed` mostrou o `if cache and
os.path.isfile(cache)`.

Conserto: as três linhas `$` do G8 agora levam
`--frame-json work/kits-oracle/replay-<slot>-<K>.json`. Com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`,
rodei cada uma como está escrita e comparei, com `diff`, contra o bloco colado embaixo dela. As três
saídas são idênticas.

O Log da K3D-TASK-19 (itens 56 a 58) ficou como está. Ali estão as corridas ao vivo, que de fato
subiram o emulador, e o que o Log cita delas é a linha `ok`, que é a mesma com ou sem `--frame-json`.

Verificação: `grep -n '^\$ python3 tools/kits/oracle.py --replay [0-9]* --focus [0-9]*$' docs/KITS-AJUSTES-3D.md`
não imprime nada.
- **Closed** — commit `43810978` (2026-10-12): docs(kits): give the G8 --replay --focus commands the --frame-json they were run with
  - Files (`git show --name-status 43810978`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-033.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
