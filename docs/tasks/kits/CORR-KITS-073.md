---
id: CORR-KITS-073
---

# CORR-KITS-073 — Remover ou afirmar FIT_PIXELS: a regra documentada nunca é aplicada

Origin: [KITS-TASK-43](/docs/tasks/kits/43-medir-encaixe-mangas.md)

## Problem

`tools/kits/oracle.py` declara `FIT_PIXELS = 2.0`, documentada como "A projection fits a section when its mean error is under this many screen pixels". Nada a lê. A segunda contagem (divisão de matriz) é impressa e nunca julgada, então a regra documentada não tem gate atrás dela — veredito impresso e não afirmado.

## Evidência

```text
$ grep -n "FIT_PIXELS" tools/kits/*.py
tools/kits/oracle.py:760:FIT_PIXELS = 2.0
```

## Root cause

Hipótese: o limiar foi planejado para um veredito de matriz compartilhada que a medida não sustentou, e ficou para trás quando o veredito caiu.

## Fix

Em `tools/kits/oracle.py`: apagar `FIT_PIXELS` e a docstring, ou usá-la no `attach_judge` com um vermelho plantado em `tools/kits/selftest.py`. Depende da decisão da CORR-KITS-071 sobre o que o critério 1b passa a pedir.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `tools/kits/selftest.py`

## Verificação

`test "$(grep -c FIT_PIXELS tools/kits/oracle.py)" -ne 1` falha hoje (a única ocorrência é a definição); passa depois, seja por remoção (0) ou por uso.

## Log de Execução
