---
id: KRP-TASK-03
---

# KRP-TASK-03 — Fechamento da fase 1

## Goal

A fase 1 (o leitor puro e o oracle sobre ele) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 1 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md` (o que a fase 1 entregou diferente do texto do §2.1 e do §2.2)
- Out:
  - código novo

## Done criteria

- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [x] `grep` das dezenove funções no `oracle.py`: `0`, de novo na HEAD
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

### 2026-10-13

Tudo na HEAD `489e17e7`.

Gates. A primeira corrida deu `kits_ui ... ***Skipped` com `kits_ui: skipped -- no display :98`
(`LastTest.log`): o Xvfb `:98` tinha caído durante a corrida. Subido de novo pela linha do
CLAUDE.md (`Xvfb :98 -screen 0 1280x1024x24 -nolisten tcp &`) e rerodado:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed  222.75 sec
2/4 Test #19: kits_image .......................   Passed   27.45 sec
3/4 Test #20: kits_gen .........................   Passed    0.03 sec
4/4 Test #21: kits_ui ..........................   Passed  208.98 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 56 of 56 red
```

Nenhum controle novo nesta task: ela não implementa.

```
$ grep -cE '^def (replay_figures|figure_depth|figure_off_axis|replay_focus|field_focus|pose_change|figure_group|piece_box|section_samples|shading_of|colour_confront|panel_samples|panel_cell|field_panels|field_number|sleeves_of|armband_of|figure_tag|_restore_samples)\b' tools/kits/oracle.py
0
$ grep -nE '^(from|import) ' tools/kits/core/replay.py | grep -cE 'oracle|fork|mcp'
0
$ rite check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

Verificação de fase "byte-idêntica antes e depois do move", refeita pela receita do adendo da
[KRP-TASK-02](/docs/tasks/concluidos/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md)
(`git archive` de `fffa211a` e da HEAD, `work/` e `roms/` ligados, o mesmo `run.sh`): `same` nos
14 arquivos; plantas `exit 1` com 4, 6, 49, 47 e 1 `FAIL` (`plant-9`, `plant-9-3`,
`plant-field-9`, `-focus`, `-panel`). Casos sintéticos migrados sem duplicata: conferido na
KRP-TASK-01 (26 = 23 + 3) e coberto pelo `kits_selftest` acima.

Escrituração: o plano não dizia o que a fase entregou diferente do texto; entrou um parágrafo
"Feito na fase 1" no fim do [§2.2](/docs/PLAN-KITS-REPLAY.md#2.2), com o plano declarado nos
arquivos desta task.
- **Closed** — commit `74018c42` (2026-10-13): docs(kits): close phase 1 of kits-replay
  - Files (`git show --name-status 74018c42`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/03-fechamento-da-fase-1.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
  - **Outside declared files** (`docs/PLAN-KITS-REPLAY.md`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-13) at `ef0133f2`: CORR-KRP-003
