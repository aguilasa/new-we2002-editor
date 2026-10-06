---
id: CORR-KITS-082
---

# CORR-KITS-082 — Dar veredito ao --sleeves-image ou marcá-lo como só relatório

Origin: [KITS-TASK-46](/docs/tasks/kits/46-manga-curta-partida.md)

## Problem

O `--sleeves-image`, acrescentado no aa3c293 nesta task, sempre devolve 0: não tem valor esperado, planta nem selftest, e não é mencionado na §4.3 nem no perfil. Ainda assim o Log da fase bloqueada cita números dele como evidência ("5551 pixel(s) of 16384 differ").

## Evidência

```text
$ sed -n '1276,1301p' tools/kits/oracle.py | grep -n 'return'
  26:    return 0
$ grep -c 'sleeves-image\|sleeves_image' tools/kits/selftest.py docs/PLAN-KITS-PY.md
tools/kits/selftest.py:0
docs/PLAN-KITS-PY.md:0
```

## Root cause

Foi escrito como diagnóstico enquanto a task estava bloqueada num save state errado, e nunca virou gate.

## Fix

Em `tools/kits/oracle.py`, dar ao `--sleeves-image` um `--expect` e uma planta que o deixe vermelho; ou documentá-lo na §4.3 como sonda só de relatório, cujos números não são afirmados.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

`grep -n 'sleeves-image' docs/PLAN-KITS-PY.md tools/kits/selftest.py` devolve pelo menos uma linha (hoje nenhuma).

## Log de Execução
