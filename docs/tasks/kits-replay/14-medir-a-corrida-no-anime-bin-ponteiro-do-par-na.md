---
id: KRP-TASK-14
---

# KRP-TASK-14 — Medir a corrida no ANIME.BIN: ponteiro do par na captura e pose --against-anime

## Goal

Fica medido que animação e quadro do `ANIME.BIN` explicam a pose de corrida do replay: a captura passa a gravar o ponteiro do par (como o `--pose` do `looks`), e `replay.py pose <captura> --against-anime` imprime animação e quadro das cinco poses — ou a negativa, com comando e saída. O resultado vai no §5.1 do plano.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py` (`pose`)
  - `tools/kits/core/replay.py`
  - `tools/kits/oracle.py` (o `pose_capture` lê o ponteiro)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§5.1: o resultado)
- Out:
  - posar a aba (KRP-TASK-15)

## Done criteria

- [ ] `replay.py pose <captura> --against-anime --json` nas cinco poses de perto recapturadas com o ponteiro: animação, quadro e quantas peças o par explica, colados no Log
- [ ] o esperado (animação e quadro) é constante por (slot, foco) no código (K1); uma planta que aponta outra animação fica vermelha com dado real (K2)
- [ ] negativa é resultado: se nenhum par explicar, o §5.1 diz isso com comando e saída, e a 15 usa a pose capturada
- [ ] sem uma das cópias mestras: `rite mark KRP-TASK-14 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Leitura do arquivo por `tools/looks/anime.py` (`no_pair_explains`, `pose`, `compose`, `against_walk`). O atraso de desenho do `looks` vale aqui: o ponteiro vivo numa parada nomeia a peça anterior.

## Log de Execução
