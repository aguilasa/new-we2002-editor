---
id: K3D-TASK-10
---

# K3D-TASK-10 — Seletor só com player e goalkeeper, vestidos pela regra medida

## Goal

O seletor de figura tem só **player** e **goalkeeper**; a figura de partida sai da interface, e a braçadeira e a manga longa passam a vestir as duas figuras pela regra da K3D-TASK-07.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G3: decisão reaberta da KITS-TASK-47, datada; a tabela "Hoje" de G4)
  - `docs/PLAN-KITS-PY.md` (§3.4: a nota de que a decisão da KITS-TASK-47 foi reaberta)
  - `tools/kits/oracle.py` (o `ARM_PIECES` passa a ser importado do núcleo)
- Out: remapear UV à mão (§0)

## Done criteria

- [x] `figure_box` tem 2 itens; `kits_ui` afirma, e a planta que devolve o terceiro fica vermelha
- [x] com braçadeira ou manga longa marcadas, a figura continua a do `EDT_MOD.BIN` (o `kits_ui` compara a silhueta sem as caixas)
- [x] a regra da K3D-TASK-07 é a única fonte da geometria nova (citada no código pela constante e em G3)
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

### 2026-10-08 — duas figuras, vestidas pela regra de G3

**Feito:**

- **Seletor:** o `figure_box` ficou com jogador e goleiro, e o `MATCH_FIGURE` saiu do `ui/app.py`,
  junto com as chaves `figure_match` e `number_off` do `ui/i18n.py`. O `--list-3d` passou a imprimir
  a linha `figure selector:`.
- **Núcleo, em `core/figure.py`:**
  - `ARM_PIECES` saiu do `oracle.py` e veio para cá, e o `oracle.py` passou a importá-la, como já
    fazia com o `SLEEVE_LENGTHS`;
  - `arm_dress` diz que seção do `MODEL.BIN` vai em que peça;
  - `dressed_scene` troca as peças com a pose da peça de mesmo nome;
  - `_model_banks` e `_model_part` são o texturizador do `match_scene`, separado para os dois usarem;
  - o `numbered_scene` passou a pintar só a imagem do uniforme.
- **API:** o `api.figure` ganhou `armband=` e `sleeves=`.
- **Decisão:** registrada em G3 com data, reabrindo a KITS-TASK-47.

**Verificação:**

- `figure_box` com 2 itens: `boxes_judge` dá `[]`. A planta `a third figure in the selector`
  fica vermelha: `figure 0 en-US: the figure selector says 'Figure: player | goalkeeper |', not 'Figure: player | goalkeeper'`.
- Figura do `EDT_MOD.BIN` com as caixas: `same_judge` dá
  `Captain armband 0.959, Long sleeves 0.962, both 0.962` (`SAME_FIGURE` 0,90). A planta
  `the match figure back for the dressings` dá
  `Captain armband: the silhouette overlaps the bare figure's by 0.745, under 0.90 -- not the EDT_MOD.BIN figure`.
- O juiz da braçadeira, agora no jogador: `369 px (1.5 % of the figure) in a 30x19 box, x 0.74-0.97 y 0.26-0.32 of the figure's box`.
  As plantas `armband never put on` (`the armband changes nothing`) e `armband drawn on the torso`
  (`… spans 79x104, over 40 …`) ficam vermelhas.

  Os valores dos juízes vieram de uma chamada direta de `same_judge`, `match_judge` e
  `boxes_judge` do `ui_check.py`, na árvore de trabalho final. As linhas das plantas vieram do
  `ui_check.py` rodado antes de corrigir o literal da planta `back copy only with Number`, que
  mirava a linha de `scene_of` que esta task mudou. O ctest final, depois dessa correção,
  imprime `kits_ui: 0 failure(s)`, o que quer dizer que toda planta ficou vermelha.
- **A regra como única fonte:**
  - o `arm_dress` lê só `ARM_PIECES`, `LONG_TO_SHORT` e `SLEEVE_LENGTHS`;
  - os quatro casos `arm_dress: …` do `selftest.py` dão `ok`;
  - o controle `RED    figure-long-sleeves-short-arms kits/core/figure.py :: arm_dress` fica vermelho;
  - G3 cita `figure.arm_dress` e `ARM_PIECES`.
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*; `kits_ui: 0 failure(s)`.
- `python3 tools/kits/controls.py`: `controls: 36 of 36 red`.
- Captura do núcleo para conferir de olho: `work/k3d-10/dress.png`, com o TEX_00 jogador de costas,
  de lado e de frente. As colunas são: sem caixas, braçadeira, manga longa, as duas.
- **Closed** — commit `dbc021c` (2026-10-08): feat(kits): dress the EDT_MOD.BIN player with MODEL.BIN arms, drop the match figure
  - Files (`git show --name-status dbc021c`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits-3d/10-duas-figuras.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
