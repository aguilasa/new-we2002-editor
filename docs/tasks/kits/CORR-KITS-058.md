---
id: CORR-KITS-058
---

# CORR-KITS-058 — Fazer o kits_ui conferir que o seletor de kit mostra os times

Origin: [KITS-TASK-31](/docs/tasks/kits/31-combobox-de-times.md)

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
