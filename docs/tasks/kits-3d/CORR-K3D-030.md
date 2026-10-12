---
id: CORR-K3D-030
---

# CORR-K3D-030 — Juiz do --replay-field aceita tabela curta: 3 focos dão ok

Origin: [CORR-K3D-026](/docs/tasks/kits-3d/CORR-K3D-026.md)

## Problem

O `replay_field_judge` não confere quantos jogadores a tabela andou. Uma corrida que sai do laço
cedo — um toque que leva a câmera a outra figura longe do eixo e é lida como "a volta à bola" —
passa com `ok`. A captura guardada de uma corrida do slot 10 com o controle físico do usuário
ligado ([CORR-K3D-031](/docs/tasks/kits-3d/CORR-K3D-031.md)) segue 3 jogadores, para no k = 5
numa figura da família 56 a 18174 de profundidade, e o juiz aprova. O G8 afirma 22 jogadores, dez
de linha e um goleiro por página, e nada disso é julgado.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay-field 10 --frame-json work/kits-oracle/replay-field-10-short-capture.json | grep -E '^ +5  |  ok  '
    5  0.0410      65    8  18174    0.2    4.8  17588    79   56 None    none    none             None    0  ball
  ok    3 focus(es) follow a player and the camera comes back to the ball; the outfield captain is focus 3, number 11 with armband 93; the goalkeeper draws 92
```

O mesmo vale para a captura `work/kits-oracle/replay-field-9-black-capture.json` (7 focos, um
deles num quadro preto), que também sai `ok`.

## Root cause

O juiz só pede "a câmera voltou à bola" no fim; o número de focos seguidos e a contagem por
página não entram em `REPLAY_FIELD_EXPECT`.

## Fix

Em `tools/kits/oracle.py`, pôr em `REPLAY_FIELD_EXPECT` os jogadores por página (dez de linha e
um goleiro em cada uma das duas, como o G8 mediu) e fazer o `replay_field_judge` falhar quando a
tabela tiver outro número, e quando a volta à bola vier antes de todos. Caso no `selftest.py`
com a tabela cortada e controle no `controls.py`.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- tools/kits/selftest.py
- tools/kits/controls.py

## Verificação

O comando da Evidência sai 1, com um `FAIL` que diz quantos jogadores a tabela tem contra os 22;
`--replay-field 9` e `10` limpos continuam `ok`.

## Log de Execução

### 2026-10-12 — o juiz pede 20 de linha, 2 goleiros e nenhuma outra figura

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `677e37d`. A
Evidência saiu igual: a linha do k = 5 e `ok    3 focus(es) …`.

Conserto (`tools/kits/oracle.py`):
- `REPLAY_FIELD_EXPECT` ganhou `"players": {"outfield": 20, "keepers": 2}` nos dois slots. O
  docstring diz de onde vem: a K3D-TASK-18 não mediu ninguém expulso.
- O `replay_field_judge` conta os focos seguidos de raiz 2, de raiz 13 e os de outra raiz, e falha com
  `the walk follows N outfield player(s), M goalkeeper(s) and O other figure(s), not 20, 2 and 0`.
- Casos novos no `selftest.py`:
  - `oracle --replay-field: the walk follows the expected players`;
  - `oracle --replay-field: a walk cut short or onto another figure fails`.
- Controle novo no `controls.py`: `oracle-replay-field-players-unasked`, visto `RED`.

Medido com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`:
- o comando da Evidência sai 1, com
  `FAIL  the walk follows 3 outfield player(s), 0 goalkeeper(s) and 0 other figure(s), not 20, 2 and 0`;
- `--replay-field 9 --frame-json work/kits-oracle/replay-field-9-black-capture.json` sai com
  `FAIL  the walk follows 6 outfield player(s), 0 goalkeeper(s) and 1 other figure(s), not 20, 2 and 0`;
- as capturas limpas da CORR-K3D-026 continuam `ok    22 focus(es) …`, tanto no
  `--replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json` quanto no `10`.

**G8:** a conclusão 3 diz que o juiz pede os 22. A planta inteira passou de 48 para 49 `FAIL` (a
contagem da caminhada entra), e o G8 foi corrigido.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 48 of 48 red`.
