---
id: CORR-KITS-035
---

# CORR-KITS-035 — Reconciliar o "captura igual" da §0 e da §7 do plano com a diferença medida de 1,95 %

Origin: [KITS-TASK-20](/docs/tasks/kits/20-fechamento-fase-4.md)

## Problem

A entrega da fase 4 na §7 do `docs/PLAN-KITS-PY.md` (linha 608) ainda diz "captura igual no Windows e no Linux", e o item 5 da §0 (linha 48) diz que "a janela sai igual". As capturas dos dois sistemas diferem em 12.224 px (1,95 %), diferença que a KITS-TASK-19 atribuiu à rasterização de texto. A KITS-TASK-20 fechou a fase "conferida na HEAD" sem mudar esse texto, e nada afirma o tamanho aceitável da diferença: `ui_check.py --compare` só imprime a contagem. Viola "fechar um veredito é varrer quem dizia o anterior" e "veredito impresso e não afirmado não é gate".

## Evidência

```text
$ python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png <scratch>/head.png | tail -1
12224 of 627200 pixels differ (1.95 %)
$ grep -n -i 'captura igual\|sai igual' docs/PLAN-KITS-PY.md
48:   núcleo, e a janela sai igual no Windows e no Linux.
608:| 4 | **a janela mínima**: Abrir… (ROM ou TEX), combobox, aba "Plano", estilo Fusion fixo; captura igual no Windows e no Linux | 2, 3 |
```

(`<scratch>/head.png` sai de `DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot <scratch>/head.png`. Controle: o mesmo estado com `--tag A4` dá 300.383 px, 47,89 %.)

## Root cause

Hipótese: a KITS-TASK-19 aceitou a diferença de rasterização só no próprio Log; editou a §3.4 do plano, mas não a §0 nem a §7, e a task de fechamento conferiu a lista de critérios sem conferir o texto da §7.

## Fix

Em `docs/PLAN-KITS-PY.md`, reescrever o item 5 da §0 e a linha da fase 4 na §7 para dizer o que foi medido: mesma paleta e mesmo painel Fusion, com diferença só na rasterização de texto. Alternativa mais forte: `ui_check.py --compare` aceitar um limite declarado e sair diferente de zero acima dele (com planta que o derrube), e o plano citar esse limite.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`
- `tools/kits/ui_check.py` (se o limite for afirmado)

## Verificação

```sh
grep -n 'captura igual\|sai igual' docs/PLAN-KITS-PY.md
```

Acha as duas linhas hoje; depois do conserto, vazio ou qualificado.

## Log de Execução
