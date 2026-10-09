---
id: K3D-TASK-12
---

# K3D-TASK-12 — Fechamento da fase 4

## Goal

A fase 4 e o ciclo conferidos na HEAD.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [x] as verificações da Fase 4 do perfil, cada uma com comando e saída no Log
- [x] `rite check --cycle kits-3d`: 0 erros
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

**Verificação 3 conforme G4, não ao pé da letra:** são 8 combinações no jogador e 4 no goleiro.
O goleiro só usa manga longa (usuário, 2026-10-08), então a caixa dele fica marcada e desligada
([G4](/docs/KITS-AJUSTES-3D.md#g4--number-captain-armband-e-long-sleeves-em-qualquer-combinação-nas-duas-figuras), K3D-TASK-11).

## Log de Execução

### 2026-10-09 — fase 4 conferida na HEAD

Verificações da Fase 4 do perfil:

1. **Nenhum UV remapeado à mão.** `git diff 07ed133..HEAD -- tools/kits/core/ | grep -nE "^\+.*\buvs?\b"`
   (de depois do fechamento da fase 3 até a HEAD) dá uma linha só:
   `+                                  scene.drawn_points(part.points, *place), part.uvs,`. O
   `dressed_scene` repassa os UVs da própria seção do `MODEL.BIN`, sem mudar nenhum; só os pontos
   são posicionados pela pose da peça.
2. **Decisões reabertas datadas no plano.** `grep -n "Reaberto em" docs/PLAN-KITS-PY.md`:
   - `379:  CORR-KITS-066, KITS-TASK-40). **Reaberto em 2026-10-07** (K3D-TASK-05, G5 do` (KITS-TASK-37);
   - `384:  medida no jogo (§4.3, KITS-TASK-47). **Reaberto em 2026-10-08** (K3D-TASK-10,` (KITS-TASK-47);
   - `398:  manga longa de jogador de linha. **Reaberto em 2026-10-09** (K3D-TASK-11, G4` (KITS-TASK-40).

   A da KITS-TASK-37 **faltava**: o §3.4 ainda dizia, no presente, que a dica fala das costas
   vazadas e que, sem a caixa, o desenho segue os dados. Esta task escreveu a reabertura, datada
   pela decisão de G5 (usuário, 2026-10-07), e declarou `docs/PLAN-KITS-PY.md` com `rite set`.
3. **O `kits_ui` cobre as combinações nas 2 figuras, com uma planta por caixa:**
   - `ok    3D TEX_14 from the back: every combination of the boxes on both figures, and each box changes the view in every one (figure 0 Number at least 1197 px, figure 0 Captain armband at least 315 px, figure 0 Long sleeves at least 3293 px, figure 0: 8 combinations, figure 1 Number at least 1196 px, figure 1 Captain armband at least 477 px, figure 1: 4 combinations)`;
   - plantas: `ok    plant 'Number ignored' fails the dressing judge`, `ok    plant 'Long sleeves ignored' fails the dressing judge`, `ok    plant 'armband never put on' fails the armband judge`, `ok    plant 'goalkeeper's armband ignored' fails the dressing judge`, `ok    plant 'goalkeeper's Long sleeves box left on' fails the dressing boxes judge`, `ok    plant 'goalkeeper's Long sleeves box left unticked' fails the dressing boxes judge`.
4. **ctest e controles:** abaixo.

Gates:
- `sh …/rite check --cycle kits-3d`: `check: 0 error(s), 0 warning(s) in 1 cycle(s)`.
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, `kits_ui: 0 failure(s)`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 37 of 37 red`.
