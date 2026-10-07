---
id: K3D-TASK-01
---

# K3D-TASK-01 — Kit Home/Away na aba e --kit home|away no CLI

## Goal

O seletor "Set" da aba 3D vira **Kit** (pt-BR **Uniforme**) com **Home**/**Away** (**Casa**/**Visitante**), e o CLI ganha `--kit home|away` ao lado de `--set 1|2`, com o mesmo efeito.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/i18n.py`, `tools/kits/ui/app.py`
  - `tools/kits/cli.py`
  - `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`
- Out: trocar `--set` (continua aceito); os Logs e CORRs do ciclo `kits` arquivado

## Done criteria

- [ ] `kits_ui` lê nas capturas `Kit` com `Home`/`Away` em en-US e `Uniforme` com `Casa`/`Visitante` em pt-BR; a planta que devolve `set_first` = "first" fica vermelha
- [ ] `python3 tools/kits/cli.py figure --kit away <args>` imprime o mesmo `_scene_digest` que `--set 2`, e `--kit home` o de `--set 1` (caso no `selftest.py`, com planta vermelha)
- [ ] `cli.py figure --help` diz que 1 é home e 2 é away
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Convenção do futebol, não medição (usuário, 2026-10-07).

## Log de Execução
