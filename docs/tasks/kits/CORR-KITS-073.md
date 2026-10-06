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

Reproduzido em 2026-10-06 sobre `5a1f6e6`: `grep -n "FIT_PIXELS" tools/kits/*.py` casa só a
definição (`tools/kits/oracle.py:760`).

Conserto: pela decisão da CORR-KITS-071, o veredito de matriz compartilhada não vem do ajuste
projetivo. Ele passou à KITS-TASK-44, que lê a matriz do GTE. Por isso `FIT_PIXELS` e a docstring
dela saíram de `tools/kits/oracle.py`, em vez de virarem gate de uma regra que a medida não
sustenta. O `--attach` continua imprimindo os erros de ajuste como dado, sem julgá-los.

```text
$ test "$(grep -c FIT_PIXELS tools/kits/oracle.py)" -ne 1 && echo verif-ok
verif-ok
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach 5 --frame-json work/kits-oracle/attach-5.json | tail -1
  ok    the figure is MODEL.BIN's, and section 93 takes the place of 97
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py | tail -1
controls: 26 of 26 red
```
- **Closed** — commit `23f9866` (2026-10-06): refactor(kits): drop FIT_PIXELS, a threshold nothing judged
  - Files (`git show --name-status 23f9866`):
    - `M docs/tasks/kits/CORR-KITS-073.md`
    - `M tools/kits/oracle.py`
