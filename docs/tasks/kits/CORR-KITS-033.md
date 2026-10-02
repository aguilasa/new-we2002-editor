---
id: CORR-KITS-033
---

# CORR-KITS-033 — Levar a troca da planta "no Fusion" à docstring, ao comentário do ctest e às Notas

Origin: [KITS-TASK-19](/docs/tasks/kits/19-kits-ui-e-captura.md)

## Problem

A f85aa85 (metade Linux da KITS-TASK-19) trocou a planta "no Fusion" de *remover* `app.setStyle("Fusion")` para *trocar por* `app.setStyle("Windows")`, porque no Linux remover a linha não muda nada: o painel continua em 18,7 % e o juiz de estilo passa. Três lugares continuam afirmando o veredito antigo, que só vale no Windows: a docstring do módulo e as de `FUSION_PANE`/`STYLE_SHARE` em `tools/kits/ui_check.py` ("the native style paints it white", "white without Fusion", "0 when its line is removed"), o comentário de `tests/CMakeLists.txt:325` ("each planted out in a copy") e as Notas da task ("tira uma das duas linhas do `app.py`"). Viola "fechar um veredito é varrer quem dizia o anterior".

## Evidência

```text
$ (cópia por git archive HEAD tools; sed -i 's/^    app.setStyle("Fusion")$/    pass/' tools/kits/ui/app.py; WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py)
ok    the look is the fixed one: palette window colour 22.2 %, Fusion pane 18.7 %
$ grep -nE 'white without Fusion|0 when its line is removed|native style paints it white|planted out in a copy|tira uma das duas linhas' tools/kits/ui_check.py tests/CMakeLists.txt docs/tasks/kits/19-kits-ui-e-captura.md
tests/CMakeLists.txt:325:    # (Fusion and the fixed palette, each planted out in a copy and required to
docs/tasks/kits/19-kits-ui-e-captura.md:29:- **Os dois controles moram no próprio gate:** o `ui_check.py` copia `tools/{kits,looks,pes2}` para um temporário, tira uma das duas linhas do `app.py` e exige que o juiz de estilo reprove a cópia. Planta que não casa uma vez só é falha, não vermelho.
tools/kits/ui_check.py:26:      pane is gone (the native style paints it white);
tools/kits/ui_check.py:85:state's picture; white without Fusion)."""
tools/kits/ui_check.py:88:22.8 % and 18.8 %; 0 when its line is removed)."""
```

## Root cause

A metade Linux acrescentou um parágrafo à docstring (linhas 36-40) e editou a §3.4 do plano, mas não voltou às frases anteriores que afirmavam o veredito medido só no Windows.

## Fix

Reescrever cada frase como "trocar pelo estilo `Windows`" ou qualificá-la como medida no Windows: docstring do módulo, de `FUSION_PANE` e de `STYLE_SHARE` em `tools/kits/ui_check.py`; o comentário em `tests/CMakeLists.txt`; a nota correspondente da task.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tests/CMakeLists.txt`
- `docs/tasks/kits/19-kits-ui-e-captura.md`

## Verificação

```sh
grep -nE 'white without Fusion|0 when its line is removed|native style paints it white|planted out in a copy|tira uma das duas linhas' tools/kits/ui_check.py tests/CMakeLists.txt docs/tasks/kits/19-kits-ui-e-captura.md
```

Imprime 5 linhas hoje; vazio depois do conserto. E `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits_ui` continua verde.

## Log de Execução
