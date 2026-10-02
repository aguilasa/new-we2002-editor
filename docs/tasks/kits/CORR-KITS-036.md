---
id: CORR-KITS-036
---

# CORR-KITS-036 — Repor no Log a linha de saída do app.py cortada sem marca

Origin: [KITS-TASK-20](/docs/tasks/kits/20-fechamento-fase-4.md)

## Problem

O Log da KITS-TASK-20 transcreve a saída do comando de captura em duas linhas. Na HEAD o comando imprime três: a do meio (`TEX_00 · imagem bitmap de trabalho, 1º conjunto · paleta … · /BIN/TEX_00.BIN on roms/japanese-shift-jis.bin, 29944 bytes`) foi cortada sem marca de elisão, então a transcrição não é o que a ferramenta imprimiu.

## Evidência

```text
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot <scratch>/head.png
wrote <scratch>/head.png, 980x640
TEX_00 · imagem bitmap de trabalho, 1º conjunto · paleta player palette, first set · /BIN/TEX_00.BIN on roms/japanese-shift-jis.bin, 29944 bytes
window up, at -32000,-32000
$ grep -c '29944 bytes' docs/tasks/kits/20-fechamento-fase-4.md
0
```

## Root cause

Hipótese: a saída foi aparada à mão ao ser colada no Log.

## Fix

Colar a saída completa no Log de `docs/tasks/kits/20-fechamento-fase-4.md`, ou marcar o corte com "…".

## Arquivos a criar ou modificar

- `docs/tasks/kits/20-fechamento-fase-4.md`

## Verificação

```sh
grep -c '29944 bytes' docs/tasks/kits/20-fechamento-fase-4.md
```

Dá 0 hoje; 1 depois do conserto (ou a linha de "…" no lugar do corte).

## Log de Execução

### 2026-10-02

Reproduzido na HEAD `ebb76eb`, rodando o comando exato do Log (que regrava `work/kits-ui-linux-head.png`; a cópia anterior guardada no scratchpad dá `0 of 627200 pixels differ (0.00 %)` contra a nova):

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot work/kits-ui-linux-head.png
  wrote work/kits-ui-linux-head.png, 980x640
  TEX_00 · imagem bitmap de trabalho, 1º conjunto · paleta player palette, first set · /BIN/TEX_00.BIN on roms/japanese-shift-jis.bin, 29944 bytes
  window up, at -32000,-32000
$ grep -c '29944 bytes' docs/tasks/kits/20-fechamento-fase-4.md
0
```

Conserto: a linha do meio colada no Log, como a ferramenta imprime. Depois:

```
$ grep -c '29944 bytes' docs/tasks/kits/20-fechamento-fase-4.md
1
```

O mesmo corte está no Log da KITS-TASK-19 (a captura do Linux, e a do Windows): varrido em commit próprio.
- **Closed** — commit `7544e13` (2026-10-02): docs(kits): restore the app.py output line cut from the KITS-TASK-20 log
  - Files (`git show --name-status 7544e13`):
    - `M docs/tasks/kits/20-fechamento-fase-4.md`
    - `M docs/tasks/kits/CORR-KITS-036.md`
