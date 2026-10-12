---
id: KRP-TASK-06
---

# KRP-TASK-06 — confront --tab: a aba contra o jogo, frente com frente e costas com costas

## Goal

`replay.py confront <captura> --tab` sobe o `ui/app.py --export-3d` com a figura que a captura diz (figura, faixa, manga, número) e compara a aba com o jogo por histograma, frente com frente e costas com costas, fechando a lacuna da [CORR-K3D-034](/docs/tasks/concluidos/kits-3d/CORR-K3D-034.md). É a métrica de antes e depois das fases 3 a 7.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/confront.py` (reuso de `histogram`/`intersection`)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - fora do git: as capturas giradas de frente dos focos de linha, feitas com `replay.py capture --turn` (KRP-TASK-07)
- Out:
  - afirmar limite de histograma
  - mudar o desenho da aba

## Done criteria

- [ ] `replay.py confront <captura> --tab --json` nas cinco figuras de perto (Marcos 9 e 10, Bokšić 9 e 10, Balaban 10) dá `front` e `back` comparados com a mesma vista do jogo; os dez números colados no Log, ao lado dos do [item 5](/docs/KITS-REPLAYS-9-10.md#5)
- [ ] planta: comparar a frente da aba com as costas do jogo fica vermelha no `controls.py`
- [ ] sem uma das cópias mestras: `rite mark KRP-TASK-06 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Depende da 07 porque a frente de um jogador de linha só existe na captura girada. A aba sobe no `:98`.

## Log de Execução
