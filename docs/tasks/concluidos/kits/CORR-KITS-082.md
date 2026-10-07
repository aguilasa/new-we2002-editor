---
id: CORR-KITS-082
---

# CORR-KITS-082 — Dar veredito ao --sleeves-image ou marcá-lo como só relatório

Origin: [KITS-TASK-46](/docs/tasks/concluidos/kits/46-manga-curta-partida.md)

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

Reproduzido em 2026-10-06 sobre `f4fa94c`: o `run_sleeves_image` sempre devolve 0, e
`grep -c 'sleeves-image\|sleeves_image' tools/kits/selftest.py docs/PLAN-KITS-PY.md` dá 0 nos dois.

Conserto, pela segunda opção da Correção: o `--sleeves-image` fica como sonda só de relatório,
e isso está dito em três lugares.

- A docstring do `run_sleeves_image` diz que ele não afirma nada e sai sempre 0.
- O help da opção diz "a report, always exits 0".
- A §4.3 diz que os números dele são pista, não veredito, e que nenhuma regra da seção se apoia
  neles.

Não ganhou `--expect` nem planta: nenhuma regra medida depende dele.

```text
$ grep -n 'sleeves-image' docs/PLAN-KITS-PY.md tools/kits/selftest.py
docs/PLAN-KITS-PY.md:…:O `oracle.py --sleeves-image SLOT --page X --tag T`, que compara a imagem de
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
```
- **Closed** — commit `328528c` (2026-10-06): docs(kits): --sleeves-image is a report, and section 4.3 says so
  - Files (`git show --name-status 328528c`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-082.md`
    - `M tools/kits/oracle.py`
