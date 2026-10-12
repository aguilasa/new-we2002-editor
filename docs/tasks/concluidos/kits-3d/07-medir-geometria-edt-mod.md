---
id: K3D-TASK-07
---

# K3D-TASK-07 — Medir como braçadeira e manga longa entram na figura do EDT_MOD.BIN

## Goal

Fica medido como a braçadeira (seção 93/90) e as mangas longas (95-102) do `MODEL.BIN` podem vestir a figura do `EDT_MOD.BIN`: peça equivalente no `EDT_MOD.BIN`, ou transplante com a matriz medida — ou a negativa medida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py` (opção nova)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G3: a regra)
- Out: desenhar na aba (é a K3D-TASK-10)

## Done criteria

- [x] a regra (ou a negativa) está em G3 com o comando versionado que a imprime, colado da HEAD
- [x] a opção nova tem controle plantado no catálogo, visto vermelho
- [x] se o resultado for negativo, a task vai a blocked com `--unblocked-by`, não a done
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Medido no ciclo anterior: `SLEEVE_LENGTHS`, `LONG_TO_SHORT`, `core/match_pose.json` (§4.3 do PLAN-KITS-PY).

## Log de Execução

### 2026-10-08 — medição na HEAD de trabalho

**Resultado positivo: transplante com a matriz da própria peça, sem peça equivalente.** A regra
está em [G3](/docs/KITS-AJUSTES-3D.md#g3--sem-match-player-só-player-e-goalkeeper), com a saída
inteira colada. A tabela é `ARM_PIECES` em `tools/kits/oracle.py`. Como o resultado não é negativo,
a task não vai a blocked.

- Opção nova: `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms`,
  que sai 0 com a última linha `ok    every sleeve and armband section is in its EDT_MOD.BIN piece's frame (offset 1.9 at most, slack 3.0)`.
  As quatro peças de braço aparecem como `posed alike` (1/12, 2/13, 3/14, 4/15).
- A planta da opção: `... oracle.py --edt-arms --plant-edt-arms` sai `rc=1`, com 21 linhas `FAIL`,
  por exemplo `FAIL  section 96: 16.0 units out of forearm a's frame, past 3.0` e
  `FAIL  section 97: on forearm b, the rule says upper arm b`.
- Casos sintéticos no `selftest.py`, os quatro `ok`:
  - `oracle --edt-arms: a sleeve goes on its own piece, in its frame`;
  - `… the mirrored sleeve goes on side b`;
  - `… a sleeve moved out of its frame fails`;
  - `… an arm the two figures pose apart fails`.
- Controles no catálogo, vistos vermelhos com `python3 tools/kits/controls.py --only <id>`:
  - `RED    oracle-arm-side-flipped      kits/oracle.py :: arm_side`;
  - `RED    oracle-arm-frame-blind       kits/oracle.py :: frame_offset`.
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 34 of 34 red`.

Fica para a K3D-TASK-10: substituir a peça do `EDT_MOD.BIN` pela seção do `MODEL.BIN` ou desenhar
por cima dela. Está registrado no fim da medição em G3.
- **Closed** — commit `08ab6a4` (2026-10-08): feat(kits): measure where MODEL.BIN sleeves and armband sit on the EDT_MOD.BIN figure
  - Files (`git show --name-status 08ab6a4`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/07-medir-geometria-edt-mod.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
- **Reviewed** (2026-10-08) at `cc4d26d`: CORR-K3D-011, CORR-K3D-012, CORR-K3D-013
