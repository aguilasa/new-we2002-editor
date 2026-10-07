---
id: CORR-KITS-090
---

# CORR-KITS-090 — Atualizar a dica do plano e a nota de ARM_SIDE que a task 40 deixou velhas

Origin: [KITS-TASK-40](/docs/tasks/concluidos/kits/40-checkboxes-numero-bracadeira.md)

## Problem

A KITS-TASK-40 mudou duas coisas que outros textos ainda descrevem do jeito antigo:

- A dica da aba (`figure_hint` em `tools/kits/ui/i18n.py`) agora manda marcar Number para pintar o painel das costas. O §3.4 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) ainda diz que a dica avisa "que o número não foi medido".
- A vista deixou de ser espelhada, e a mudança da braçadeira saiu de x 0,01–0,20 para x 0,80–0,99 da caixa da figura. A docstring de `ARM_SIDE` em `tools/kits/ui_check.py` ainda diz "measured at x 0.01-0.20". O `ARMBAND_BOX`, poucas linhas acima, a task atualizou.

## Evidência

```text
$ grep -n "que o número não foi medido" docs/PLAN-KITS-PY.md
377:  que o número não foi medido — o desenho segue os dados (decisão do usuário,
$ grep -n "measured at x 0.01-0.20" tools/kits/ui_check.py
120:either side: measured at x 0.01-0.20 of it (KITS-TASK-47, CORR-KITS-087)."""
$ grep -n "tick Number" tools/kits/ui/i18n.py
"copies the shirt back into it (measured); tick Number to paint "
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py | grep "match player is drawn"
ok 3D TEX_14: ... (291 px (1.3 % of the figure) in a 24x17 box, x 0.80-0.99 y 0.28-0.33 of the figure's box)
```

## Root cause

Dois vereditos fecharam (o número agora é desenhado; a vista deixou de ser espelhada) sem varrer os lugares que diziam o anterior.

## Fix

- No §3.4 do `docs/PLAN-KITS-PY.md` (por volta da linha 377), reescrever a frase da dica para bater com o `figure_hint`.
- Em `tools/kits/ui_check.py`, atualizar a docstring de `ARM_SIDE` para a medida pós-task 40 (x 0,80–0,99), citando o valor espelhado anterior e de onde ele vem.
- Antes de fechar, varrer `docs/` e `tools/kits/` atrás de outras menções a `0.01-0.20` e a "número não foi medido".

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`
- `tools/kits/ui_check.py`

## Verificação

```sh
grep -n "que o número não foi medido" docs/PLAN-KITS-PY.md; grep -n "measured at x 0.01-0.20" tools/kits/ui_check.py
```

Hoje imprime as duas linhas. Depois da correção não imprime nada.

## Log de Execução

- **Closed** — commit `46984e5` (2026-10-07): docs(kits): sweep the 3D hint and ARM_SIDE after KITS-TASK-40
  - Files (`git show --name-status 46984e5`):
    - `M docs/PLAN-KITS-PY.md`
    - `M tools/kits/ui_check.py`
