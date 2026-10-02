---
id: CORR-KITS-034
---

# CORR-KITS-034 — Desinverter a afirmação de caminho relativo/absoluto nas Notas da task

Origin: [KITS-TASK-19](/docs/tasks/kits/19-kits-ui-e-captura.md)

## Problem

As Notas da KITS-TASK-19 dizem que abrir o disco por caminho absoluto em vez de relativo leva a cor de janela "de 22,8 % para 23,1 %" — absoluto = 23,1 %. As medições dizem o contrário: a captura relativa do Windows dá 23,1 %, e o gate, que abre por caminho absoluto (`os.path.abspath(image)` em `ui_check.py:480`), registrou 22,8 % no Windows. No Linux, mesmo sentido: relativo 22,9 %, absoluto 22,2 % (caminho mais longo na barra cobre mais cor de janela). E o "22,8 %" solto nas Notas e nas docstrings só vale no Windows; no Linux o gate mede 22,2 %.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot <scratch>/linux.png
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot <scratch>/linux-abs.png
$ python3 tools/kits/ui_check.py --compare <scratch>/linux.png <scratch>/linux-abs.png
linux.png: 980x640, window colour 22.9 %, Fusion pane 18.7 %
linux-abs.png: 980x640, window colour 22.2 %, Fusion pane 18.7 %
7712 of 627200 pixels differ (1.23 %)
$ grep -n "de 22,8 % para 23,1 %" docs/tasks/kits/19-kits-ui-e-captura.md
31:- **`--compare A B`** é o comando versionado do critério 3. [...] muda a cor de janela de 22,8 % para 23,1 %.
```

## Root cause

Hipótese: os dois números foram transpostos ao escrever a nota — o 22,8 % do gate já era uma corrida por caminho absoluto.

## Fix

Na nota do `--compare A B`, dizer "relativo 23,1 % → absoluto 22,8 % (Windows)". Marcar o 22,8 % da nota do juiz de aparência e as docstrings "measured: 22.8 %" de `tools/kits/ui_check.py` como Windows, com o Linux em 22,2 %.

## Arquivos a criar ou modificar

- `docs/tasks/kits/19-kits-ui-e-captura.md`
- `tools/kits/ui_check.py`

## Verificação

```sh
grep -n "de 22,8 % para 23,1 %" docs/tasks/kits/19-kits-ui-e-captura.md
```

Casa hoje; vazio depois do conserto.

## Log de Execução

### 2026-10-02

Reproduzido, no Linux (`:98`), antes do conserto:

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot $S/linux.png
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py $PWD/roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot $S/linux-abs.png
$ python3 tools/kits/ui_check.py --compare $S/linux.png $S/linux-abs.png
linux.png: 980x640, window colour 22.9 %, Fusion pane 18.7 %
linux-abs.png: 980x640, window colour 22.2 %, Fusion pane 18.7 %
7712 of 627200 pixels differ (1.23 %)
$ grep -n "de 22,8 % para 23,1 %" docs/tasks/kits/19-kits-ui-e-captura.md
31:- **`--compare A B`** [...] muda a cor de janela de 22,8 % para 23,1 %.
```

Absoluto dá menos que relativo; a nota dizia o inverso. Os números do Windows (relativo 23,1 %, gate absoluto 22,8 %) são os do Log da própria task (linhas `kits-ui-windows.png: ... 23.1 %` e `ok the look is the fixed one: palette window colour 22.8 %`), não remedidos aqui — o Windows não está nesta máquina.

Conserto: a nota do `--compare` diz relativo → absoluto, 23,1 → 22,8 % no Windows e 22,9 → 22,2 % no Linux; a nota do juiz de aparência marca 22,8 % e 18,8 % como Windows, com 22,2 % e 18,7 % no Linux. As docstrings de `tools/kits/ui_check.py` já saíram por sistema na f51ec4f (CORR-KITS-033).

```
$ grep -n "de 22,8 % para 23,1 %" docs/tasks/kits/19-kits-ui-e-captura.md
(vazio, exit 1)
```
- **Closed** — commit `5ea909c` (2026-10-02): docs(kits): un-invert the relative/absolute path numbers in the KITS-TASK-19 notes
  - Files (`git show --name-status 5ea909c`):
    - `M docs/tasks/kits/19-kits-ui-e-captura.md`
    - `M docs/tasks/kits/CORR-KITS-034.md`
