---
id: CORR-KITS-058
---

# CORR-KITS-058 — Fazer o kits_ui conferir que o seletor de kit mostra os times

Origin: [KITS-TASK-31](/docs/tasks/concluidos/kits/31-combobox-de-times.md)

## Problem

Nenhum gate confere o que o combobox da janela mostra. O `kits_selftest` confere só `api.kit_order` no core, e o `tools/kits/ui_check.py` (`kits_ui`) nunca lê o texto dos itens do seletor. Se `relabel_tags` voltasse a rótulos `TEX_xx` crus, todo gate continuaria verde; o critério 2 se apoia hoje só numa captura feita à mão em `work/`, fora do versionamento.

## Evidência

```text
$ grep -n "tag_box\|combo\|kit_team" tools/kits/ui_check.py
(sem saída)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
4/4 Test #21: kits_ui ... Passed 26.28 sec
```

## Root cause

Os critérios da task pedem "uma captura" e "`kits_ui` verde", mas nada transforma a captura em verificação.

## Fix

Em `tools/kits/ui_check.py`, fazer o app reportar o texto dos itens do seletor (por exemplo uma opção do `app.py` que os imprima) e afirmar: item 0 == "Ireland — TEX_00", item 95 == "Master League default — TEX_A4", último == "TEX_A3", 105 itens no total. Plantar um vermelho revertendo os rótulos à tag crua numa cópia de caixa de areia.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tools/kits/ui/app.py`

## Verificação

`python3 tools/kits/ui_check.py | grep -q "kit selector lists teams"` falha hoje; passa depois do conserto, e a planta dos rótulos crus aparece como vermelho segurado.

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `ad4a3c0`: `grep -n "tag_box\|combo\|kit_team" tools/kits/ui_check.py` não acha nada, e o `kits_ui` passa sem olhar o seletor.

Conserto:

- `app.py --list-kits`: abre o disco, imprime os itens do seletor de kit (`  kit N: texto`) e sai 0.
- `ui_check.py`: o juiz `selector_judge` exige 105 itens, "Ireland — TEX_00" no 0, "Master League default — TEX_A4" no 95 e "TEX_A3" no 104 (`KIT_ITEM_WANT`); entra no `kits_ui` como "the kit selector lists teams in game order".
- Planta `kit labels bare tags`: numa cópia, o rótulo de time vira a tag crua; o juiz tem de reprovar.
- A docstring do módulo nomeia o juiz e a planta.

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --list-kits | sed -n '1,2p;95,98p;$p'
  kit 0: Ireland — TEX_00
  kit 1: Scotland — TEX_01
  kit 94: Basilea — TEX_94
  kit 95: Master League default — TEX_A4
  kit 96: TEX_95
  kit 97: TEX_96
  kit 104: TEX_A3
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep -E 'selector|bare|kits_ui:'
  ok    pt-BR picked in the window's selector is the window opened in pt-BR (0 px differ), and another picture than en-US (19319 px)
  ok    the kit selector lists teams in game order: 105 items, 0 'Ireland — TEX_00'; 95 'Master League default — TEX_A4'; 104 'TEX_A3'
        plant 'kit labels bare tags': item 0 is 'TEX_00', not 'Ireland — TEX_00'
  ok    plant 'kit labels bare tags' fails the selector judge
kits_ui: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `e9f8fbf` (2026-10-04): test(kits): kits_ui checks the kit selector lists teams in game order
  - Files (`git show --name-status e9f8fbf`):
    - `M docs/tasks/kits/CORR-KITS-058.md`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui_check.py`
