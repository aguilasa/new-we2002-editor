---
id: K3D-TASK-08
---

# K3D-TASK-08 — Medir a braçadeira do goleiro no emulador

## Goal

Fica medido se, e como, o jogo desenha a braçadeira de capitão no goleiro (seção, peça trocada, mangas curta e longa).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G4)
- Out: desenhar na aba (é a K3D-TASK-11)

## Done criteria

- [ ] a regra (ou a negativa) está em G4 com o comando do `oracle.py` colado da HEAD
- [ ] controle plantado no catálogo, visto vermelho
- [ ] sem save state de goleiro capitão: `rite mark K3D-TASK-08 blocked --unblocked-by "test -f work/kits-states/<slot do goleiro>.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Como na KITS-TASK-43, o `oracle.py --attach` serve de ponto de partida.

## Log de Execução
