---
id: K3D-TASK-02
---

# K3D-TASK-02 — Combos do tamanho da opção mais longa

## Goal

Todo combo da janela mostra inteira a opção mais longa do idioma em uso e se reajusta quando o idioma troca ao vivo — o defeito que o `image_box` já corrigiu (`ui/app.py:326-327`) deixa de existir nos outros.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/ui/app.py`
  - `tools/kits/ui_check.py`, `tools/kits/controls.py`
- Out: mudar textos do catálogo (é a K3D-TASK-01)

## Done criteria

- [x] `kits_ui` afirma, para cada combo, abrindo em en-US e trocando para pt-BR ao vivo (e o inverso), que a largura do combo é ≥ a largura do texto mais longo dos seus itens; a saída cita o combo e as duas larguras
- [x] a planta que tira o ajuste de um combo (ex.: `set_box`) fica vermelha
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Combos hoje com a política default: `set_box`, `figure_box`, `language_box`, `palette_box`, `zoom_box` (G2).

**Como se mede.** `app.py --list-combos` imprime, para cada combo da janela, a largura do
campo de texto que o estilo dá (`SC_ComboBoxEditField`, seta e moldura fora) e a do item
mais longo. A lista de combos é achada (`Window.combos()`, por `vars`), não escrita, e o juiz
`combos_judge` do `ui_check.py` exige os sete nomes que ele mesmo escreve. Corre na aba 3D:
noutra aba os combos dela não estão dispostos e a largura sai 615. O `--switch-to` passou a
dar `settle` antes de trocar — sem isso a janela era medida já no idioma novo e o defeito não
aparecia (antes da correção: en→pt `set_box` 39/50, `figure_box` 81/108, `tag_box` 203/218).

Evidência (2026-10-07):

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py
  ok    every combo is as wide as its longest item after a live switch, both ways (field/longest px: en>pt tag_box 223/218, en>pt language_box 108/104, en>pt image_box 185/179, en>pt palette_box 162/156, en>pt zoom_box 20/15, en>pt set_box 55/50, en>pt figure_box 115/108, pt>en tag_box 203/198, ... pt>en set_box 55/35, pt>en figure_box 115/74)
        plant 'Kit combo keeps its first width': en-US to pt-BR: set_box field 39 px, its longest item 'Visitante' 50 px
  ok    plant 'Kit combo keeps its first width' fails the combo width judge
kits_ui: 0 failure(s)

$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4

$ python3 tools/kits/controls.py
controls: 29 of 29 red
```

A planta é do catálogo `PLANTS` do `ui_check.py`, não do `controls.py`: largura de widget só
se mede com janela, e o `controls.py` planta contra o `selftest.py`, que roda sem tela. Por
isso o `controls.py` não ganhou entrada nesta task.

Visto de passagem, fora do escopo: em pt-BR o `image_box` ainda diz "1º conjunto" /
"2º conjunto", e o `palette_box` mostra os nomes de registro do core em inglês
("goalkeeper palette, first set") — vocabulário que a G1 não alcançou.

## Log de Execução

- **Closed** — commit `f24ab93` (2026-10-07): feat(kits): fit every combo to its longest item across language switches
  - Files (`git show --name-status f24ab93`):
    - `M docs/tasks/kits-3d/02-combos-ajustados.md`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui_check.py`
