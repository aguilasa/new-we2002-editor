---
id: KRP-TASK-07
---

# KRP-TASK-07 — replay.py capture com as guardas medidas, e o oracle capturando por ela

## Goal

`replay.py capture --slot S [--focus K] [--turn R1|L1] [--walk L2|R2] [--out DIR]` faz a captura que hoje mora no `oracle.py` (`replay_capture`, `replay_arrive`, `replay_field_capture` sobre `pose_capture`), grava no schema v1 e aplica as guardas do [§2.5](/docs/PLAN-KITS-REPLAY.md#2.5); o `oracle.py` passa a capturar por ela.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/oracle.py`
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - andar o replay com Right/Left
  - ponteiro do par do `ANIME.BIN` (KRP-TASK-14)

## Done criteria

- [ ] `replay.py capture --slot 9 --focus 3` grava uma captura v1 cuja leitura por `replay.py figure --json` dá os mesmos campos da linha `ok` do [relatório](/docs/KITS-REPLAYS-9-10.md#como-foi-medido) para o foco 3 do slot 9
- [ ] `replay.py capture --slot 9 --focus 3 --turn R1` e `--slot 10 --focus 3|2 --turn R1` gravam a frente dos focos de linha, para a KRP-TASK-06
- [ ] com um joystick plantado em `fork.JOYSTICK_DIR`, `capture` recusa antes de subir o emulador (planta no `controls.py`)
- [ ] a saída imprime, por sequência, os quadros corridos e o timeout de 390, e nenhuma passa dele
- [ ] sem uma das cópias mestras: `rite mark KRP-TASK-07 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Custo de relógio: 10 a 40 minutos por corrida. `frame_step` a ~57 ms. O seguido atrás de um jogador é a figura no eixo com margem (CORR-K3D-024).

## Log de Execução
