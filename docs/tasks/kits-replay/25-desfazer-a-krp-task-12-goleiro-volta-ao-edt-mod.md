---
id: KRP-TASK-25
---

# KRP-TASK-25 — Desfazer a KRP-TASK-12: o goleiro volta ao do EDT_MOD.BIN, com a 92 trocada

## Goal

A figura 1 da aba e do CLI volta a ser o goleiro de antes da [KRP-TASK-12](/docs/tasks/kits-replay/12-goleiro-pela-familia-13-com-a-pose-medida-e-a-92.md): o do `EDT_MOD.BIN`, com só a 92 trocada quando capitão, vestido pelo `arm_dress`. O código que o commit `e4b2535e` trouxe sai — `keeper_scene`, `keeper_order`, `core/keeper_pose.json`, a linha `order` do `cli.py figure`, o juízo `family_judge` e a planta dele, o controle `figure-keeper-armband-always` —, e o §4 do plano diz, datado, que a família 13 foi desfeita.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py`
  - `tools/kits/core/keeper_pose.json` (removido)
  - `tools/kits/cli.py`
  - `tools/kits/ui_check.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§4: a reversão datada; o texto do "Feito" da KRP-TASK-12 fica, marcado como desfeito)
- Out:
  - a linha "Feito na fase 4" do §4 e o fechamento da fase (KRP-TASK-26)
  - o link `#3.3` da CORR-KRP-027, que a KRP-TASK-13 consertou: o conserto fica
  - a regra da cabeça e a pele do corpo da KRP-TASK-24 no goleiro do `EDT_MOD.BIN`: voltam ao que eram antes da KRP-TASK-12, não mudam

## Done criteria

- [ ] `git diff e4b2535e^ -- tools/kits/core/figure.py tools/kits/cli.py tools/kits/ui_check.py` vazio, ou cada linha que sobra justificada no Log (por exemplo um conserto de uma task posterior que toca o mesmo trecho)
- [ ] `test ! -e tools/kits/core/keeper_pose.json` e `grep -rn "keeper_scene\|keeper_order\|keeper_pose" tools/kits` vazio
- [ ] `cli.py figure roms/japanese-shift-jis.bin --tag 41 --set 1 --figure 1 --player A-I1-B-A-B`, com e sem `--armband`: digest igual ao da árvore de `e4b2535e^`, as duas corridas coladas no Log
- [ ] `cli.py figure --tag 22` e `--tag 22 --match --set 1`: digest igual antes e depois desta task (o `match_scene` não muda)
- [ ] `replay.py confront <captura> --tab` e `--tab --player`, no Marcos dos slots 9 e 10 (`work/kits-replay/tab/replay-{9,10}-R1.json`), colados da HEAD no Log: os números do lado "antes" do Log da KRP-TASK-12 (registra número, não afirma limite)
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, sem `figure-keeper-armband-always` no catálogo
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] o §4 do plano diz, datado, que a família 13 foi desfeita por decisão do usuário

## Notes

Decisão do usuário (2026-10-18): desfazer as KRP-TASK-12 e 13, numa fase 4a depois da 4.

O ponto de partida é `git revert e4b2535e` — o único commit de código da KRP-TASK-12; depois dele, só `87dc98a6` (KRP-TASK-13) tocou o plano. O revert não pode levar o arquivo da task 12 nem o `progress.json`: tasks fechadas ficam como estão, e o estado só muda pelo `rite`. Ao rodar, confira o que a KRP-TASK-14 mudou nos mesmos arquivos (`controls.py`, `selftest.py`), que estava em andamento quando esta task foi criada.
## Log de Execução
