---
id: K3D-TASK-09
---

# K3D-TASK-09 — Fechamento da fase 3

## Goal

A fase 3 conferida na HEAD.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [x] as verificações da Fase 3 do perfil, cada uma com comando e saída no Log
- [x] `rite check --cycle kits-3d`: 0 erros
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

### 2026-10-08 — conferência na HEAD `aca5cea`

**Verificações da Fase 3 do perfil:**

1. **Número da regra sai de opção versionada.** As saídas de hoje, `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms`
   (`rc=0`) e `… --keeper-armband 7 --frame-json work/kits-oracle/matrix-7.json` (`rc=0`), foram
   comparadas com os blocos `text` colados em G3 e G4, e são iguais nos dois casos (`g3 pasted == HEAD output: True`,
   `g4 pasted == HEAD output: True`). Os números do texto também batem com a saída:
   - G3: distância de 3,5 a 6,1 (`at 3.5,` … `at 6.1,`), offset de 0,7 a 1,9 e `slack 3.0`;
   - G3: a planta `--plant-edt-arms` dá 18 `FAIL`, todas `units out of` (`grep -vc "units out of"` dá `0`);
   - G4: `23 whole and 4 cut figure(s)` e `within 153 to 184`;
   - G4: a planta `--plant-keeper-armband` dá `FAIL  no figure opened at section 13 draws section 103`.
2. **Resultado negativo não fecha critério.** As duas medições da fase deram resultado positivo
   (K3D-TASK-07 e 08 em done). A K3D-TASK-08 tinha save state de goleiro capitão (slot 7), e o caso de
   manga curta não existe para o goleiro (usuário, 2026-10-08, registrado em G4).
3. **`controls.py` todo vermelho, com o controle novo de cada medição:** `controls: 35 of 35 red`, entre eles
   `RED    oracle-arm-side-flipped`, `RED    oracle-arm-frame-blind` (G3) e
   `RED    oracle-keeper-armband-unasked` (G4).

**`rite check --cycle kits-3d`:** `check: 0 error(s), 0 warning(s) in 1 cycle(s)`.

**`DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:**
`100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- **Closed** — commit `07ed133` (2026-10-08): docs(kits): verify phase 3 at HEAD
  - Files (`git show --name-status 07ed133`):
    - `M docs/tasks/kits-3d/09-fechamento-fase-3.md`
- **Reviewed** (2026-10-08) at `24bc15b`: no finding
