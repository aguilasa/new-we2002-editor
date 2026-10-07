---
id: CORR-KITS-066
---

# CORR-KITS-066 — Atualizar figure_hint: as costas agora são medidas

Origin: [KITS-TASK-38](/docs/tasks/concluidos/kits/38-medir-costas-numero.md)

## Problem

A KITS-TASK-38 mudou o veredito sobre as costas: o jogo preenche o vão do torso com as costas da camisa. A dica da janela (`figure_hint`) ainda diz que as costas do jogo não foram medidas. A própria nota da task 38 na task 40 diz que a dica "passa a estar errada", mas o conserto foi passado adiante em vez de feito na task que mudou o veredito, o que a regra "fechar um veredito é varrer quem dizia o anterior" pede.

## Evidência

```text
$ grep -n -A2 '"figure_hint"' tools/kits/ui/i18n.py
78:        "figure_hint": "Drag to turn, double-click to reset. The back shows through: "
79:                       "the area the torso samples is empty in the TEX, and the game's "
80:                       "back and number are not measured yet.",
$ grep -n "passa a estar errada" docs/tasks/kits/40-checkboxes-numero-bracadeira.md
35:Da KITS-TASK-38 ... a dica da aba (`figure_hint` em `ui/i18n.py`, da KITS-TASK-37) diz que as costas "not measured yet" e passa a estar errada. ...
```

## Root cause

Hipótese: `i18n.py` estava fora dos arquivos declarados da task, e o texto vencido foi delegado à KITS-TASK-40 em vez de consertado aqui.

## Fix

Em `tools/kits/ui/i18n.py`, reescrever `figure_hint` nos dois idiomas (en-US e pt-BR) para que só o número fique "não medido". Conferir a §3.4 do `docs/PLAN-KITS-PY.md` (perto da linha 375), que dá o mesmo motivo para a dica. Se a KITS-TASK-40 (pendente) fizer isso antes, esta CORR fecha por ela.

## Arquivos a criar ou modificar

- `tools/kits/ui/i18n.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

```sh
grep -n "back and number are not measured" tools/kits/ui/i18n.py
```

Casa a linha 80 hoje; nada depois do conserto. O selftest de idioma (`language: 0 failure(s)`) continua verde.

## Log de Execução

Reproduzido em 2026-10-05 sobre `2886711`: `grep -n "back and number are not measured"
tools/kits/ui/i18n.py` casa a linha 80.

Conserto: `figure_hint`, nas duas línguas, diz que a área do torso está vazia no TEX, que o jogo
copia as costas da camisa para ela (medido) e que o número não foi medido. A §3.4 do
`PLAN-KITS-PY.md` dá o mesmo motivo. A KITS-TASK-40 ainda não tinha feito isso.

```text
$ grep -n "back and number are not measured" tools/kits/ui/i18n.py
(sem saída)
$ python3 tools/kits/selftest.py | grep -E "language:|kits_selftest:"
language: 0 failure(s)
kits_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `a6d1807` (2026-10-05): fix(kits): the 3D hint says the back is measured, the number is not
  - Files (`git show --name-status a6d1807`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-066.md`
    - `M tools/kits/ui/i18n.py`
