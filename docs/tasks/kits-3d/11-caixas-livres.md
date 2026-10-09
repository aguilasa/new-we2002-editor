---
id: K3D-TASK-11
---

# K3D-TASK-11 — Number, braçadeira e manga longa livres nas duas figuras

## Goal

Number, Captain armband e Long sleeves combinam livremente — nenhuma, uma, duas ou as três — no jogador e no goleiro.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`
  - `tools/kits/core/figure.py`, `tools/kits/core/api.py`
  - `tools/kits/ui_check.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G4: decisão reaberta da KITS-TASK-40, datada)
- Out: o que a K3D-TASK-08 não mediu: a caixa fica desligada com a frase, nas duas línguas

## Done criteria

- [x] `kits_ui` captura as 8 combinações × 2 figuras de costas e afirma que cada caixa muda a captura em todo contexto
- [x] uma planta por caixa (que a ignora) fica vermelha
- [x] nenhuma caixa é escondida ou desligada sem medida que justifique
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

**A fonte manda sobre o critério 1** ([G4](/docs/KITS-AJUSTES-3D.md#g4--number-captain-armband-e-long-sleeves-em-qualquer-combinação-nas-duas-figuras)):
o goleiro só usa manga longa (usuário, 2026-10-08). A caixa Long sleeves dele fica marcada e
desligada, com a frase; por isso são 8 combinações no jogador e 4 no goleiro.

## Log de Execução

### 2026-10-09 — caixas livres nas duas figuras

- **Regra de G3 estendida:** as seções 14 a 17 e a 92 entraram em `ARM_PIECES`.
  `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms`:
  `section  92 -> upper arm b (nearest EDT section 13 at 6.1, other part 8.5), frame offset 0.8`,
  `ok    every sleeve and armband section is in its EDT_MOD.BIN piece's frame (offset 1.9 at most, slack 3.0)`.
  Com `--plant-edt-arms`, a corrida sai 1, com 23 `FAIL`, todos `units out of`.
- **Combinações:** `kits_ui`, `ok    3D TEX_14 from the back: every combination of the boxes on both figures, and each box changes the view in every one (figure 0 Number at least 1197 px, figure 0 Captain armband at least 315 px, figure 0 Long sleeves at least 3293 px, figure 0: 8 combinations, figure 1 Number at least 1196 px, figure 1 Captain armband at least 477 px, figure 1: 4 combinations)`.
- **Braçadeira do goleiro:** `goalkeeper 740 px (3.0 % of the figure) in a 32x61 box, x 0.75-0.99 y 0.17-0.35 of the figure's box, ink 353 px` (TEX_A4).
- **Plantas, uma por caixa, todas vermelhas:**
  - `ok    plant 'Number ignored' fails the dressing judge`;
  - `ok    plant 'Long sleeves ignored' fails the dressing judge`;
  - `ok    plant 'armband never put on' fails the armband judge`;
  - `ok    plant 'goalkeeper's armband ignored' fails the dressing judge`;
  - `ok    plant 'goalkeeper's Long sleeves box left on' fails the dressing boxes judge`;
  - `ok    plant 'goalkeeper's Long sleeves box left unticked' fails the dressing boxes judge`.
- **Nenhuma caixa escondida:** `ok    the dressing boxes: all shown on both figures, the goalkeeper's Long sleeves ticked and off with the sentence; …`.
  A única caixa desligada é o Long sleeves do goleiro, justificado pela decisão do usuário em G4.
- **Correção de caminho:** o texto desligado da caixa do goleiro tem pixels antisserrilhados na
  cor do fundo da vista (0x8C), e o `view_box` do `ui_check.py` os tomava como parte da vista: a
  braçadeira aparecia como 407×211 px. Agora ele usa só as linhas e colunas majoritariamente de fundo.
- Selftest: os 5 casos novos `arm_dress: the goalkeeper …` dão `ok`. No catálogo, o controle
  `figure-keeper-armband-on-the-player-arm` dá `RED` (`python3 tools/kits/controls.py --only figure-keeper-armband-on-the-player-arm`).

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, `kits_ui: 0 failure(s)`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 37 of 37 red`.
- **Closed** — commit `1549f06` (2026-10-09): feat(kits): free the three dressing boxes on both figures
  - Files (`git show --name-status 1549f06`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits-3d/11-caixas-livres.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-09) at `c70d127`: CORR-K3D-018, CORR-K3D-019
