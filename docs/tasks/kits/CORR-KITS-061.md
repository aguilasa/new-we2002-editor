---
id: CORR-KITS-061
---

# CORR-KITS-061 — Plantar um controle para as linhas de nota da aba Diagnóstico

Origin: [KITS-TASK-33](/docs/tasks/kits/33-aba-diagnostico.md)

## Problem

A única planta registrada da aba Diagnóstico, `diagnosis rows never added`, remove a linha `diag_problem`. Nada planta a perda das linhas `diag_note`. As linhas de nota só são afirmadas num lugar: a conferência do `TEX_13` do disco ED, que só roda com `WE2002_KITS_ED_IMAGE` definida — e o alvo `kits_ui` do `ctest` não a define. No gate registrado, uma janela que largue toda nota de leitura continua verde, e o Log não mostra vermelho dessa asserção. Plantado à mão, o juiz fica vermelho com a variável ED e verde sem ela.

## Evidência

```text
$ (cópia de rascunho; a linha `self.diag_list.addItem(tr("diag_note", text=text))` do app.py trocada por `pass`)
$ python3 - <<'PY'
import sys,os,tempfile; sys.path.insert(0,'tools/kits')
import ui_check as u
for ed in ('<repo>/roms/golden-european-deluxe.bin', None):
    if ed: os.environ['WE2002_KITS_ED_IMAGE']=ed
    else: os.environ.pop('WE2002_KITS_ED_IMAGE',None)
    with tempfile.TemporaryDirectory() as t:
        print(ed is not None, u.diag_judge('work/venv-looks/bin/python', os.environ['WE2002_LOOKS_IMAGE'], os.environ.copy(), t))
PY
True (["ED TEX_13: exit 0, no row starting 'Note: its ISO size is' in []"], [...])
False ([], ['sound 0 row(s)', '0 text px in its list', 'planted 1 row(s)', 'ED not checked, WE2002_KITS_ED_IMAGE unset'])
$ grep -n "WE2002_KITS_ED_IMAGE" tests/CMakeLists.txt
(sem saída)
```

## Root cause

A lista de plantas cobre só o caminho de problema; o caminho de nota tem testemunha só no disco ED e nenhum controle.

## Fix

Em `tools/kits/ui_check.py`: uma entrada em `PLANTS` que remove a linha `addItem` de `diag_note`, e uma testemunha de nota para o `diag_judge` que não dependa do disco ED (por exemplo um TEX avulso cuja leitura produza nota, extraído de um disco que o gate já tem). Não havendo, tornar o vermelho da planta condicional à variável ED e dizê-lo na saída.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`

## Verificação

```sh
WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin DISPLAY=:98 XAUTHORITY= python3 tools/kits/ui_check.py | grep "plant 'diagnosis note rows never added' fails"
```

Sem saída hoje; depois do conserto imprime uma linha `ok`.

## Log de Execução
