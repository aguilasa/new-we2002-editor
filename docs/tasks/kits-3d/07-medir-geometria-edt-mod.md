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

- [ ] a regra (ou a negativa) está em G3 com o comando versionado que a imprime, colado da HEAD
- [ ] a opção nova tem controle plantado no catálogo, visto vermelho
- [ ] se o resultado for negativo, a task vai a blocked com `--unblocked-by`, não a done
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Medido no ciclo anterior: `SLEEVE_LENGTHS`, `LONG_TO_SHORT`, `core/match_pose.json` (§4.3 do PLAN-KITS-PY).

## Log de Execução
