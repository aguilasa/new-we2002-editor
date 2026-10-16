---
id: KRP-TASK-23
---

# KRP-TASK-23 — Fechamento da fase 3a

## Goal

A fase 3a (os controles da cabeça na aba) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 3a do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no §3.3 (o resto só reroda e corrige escrituração)
- Out:
  - código novo

## Done criteria

- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`
- [x] uma captura da aba com o painel à vista, nas duas línguas, citada no Log
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **done** (2026-10-16): fechamento da fase 3a na HEAD `fb8934d3`, com as correções da fase fechadas (`rite status`: `open fixes: critical 0, high 0, medium 0, low 0`). O §3.3 já dizia o que a fase fez. O plano ganhou só a linha "Feito na fase 3a", no fim do [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3).

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  348.95 sec
2/5 Test #19: kits_image .......................   Passed   28.20 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  260.29 sec
5/5 Test #22: kits_replay ......................   Passed   12.31 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 81 of 81 red
$ sh rite check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

A aba com o painel à vista, nas duas línguas (Croácia TEX_22, a tupla do Bokšić). Mostram os cinco combos à direita da vista 3D, com os rótulos literais do §3.3: Skin Color … Beard Color, e Cor da Pele … Cor da Barba.

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --lang en-US --player-looks A-L3-H-A-A --screenshot work/krp-t23/panel-en-US.png
  wrote work/krp-t23/panel-en-US.png, 980x640
  Croatia — TEX_22 · image work bitmap, 1st set · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
exit=0
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --lang pt-BR --player-looks A-L3-H-A-A --screenshot work/krp-t23/panel-pt-BR.png
  wrote work/krp-t23/panel-pt-BR.png, 980x640
  Croatia — TEX_22 · image bitmap de trabalho, 1º conjunto · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
exit=0
$ sha256sum work/krp-t23/*.png
bc5176d231e7c96a81ef5bc7735f83ec0803d293cf7d06e19c73d9e885cb12c2  work/krp-t23/panel-en-US.png
8b15577a1550170bda33e1d84d9eb6846ce35f6e026e94a8c23d271dc91260d6  work/krp-t23/panel-pt-BR.png
```
- **Closed** — commit `61b1fa45` (2026-10-16): docs(kits): close phase 3a of kits-replay with the gates rerun at HEAD
  - Files (`git show --name-status 61b1fa45`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/23-fechamento-da-fase-3a.md`
- **Reviewed** (2026-10-16) at `1bf78cdb`: CORR-KRP-026
