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

### 2026-10-02

Reproduzido na HEAD `ebb9e67`, com `$S` o scratchpad da sessão e a captura do Windows lida pelo `/media/ingmar/win`:

```
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 00 --image work1 --palette 2 --zoom 3 --zones --screenshot $S/head.png
$ python3 tools/kits/ui_check.py --compare /media/ingmar/win/github/new-we2002-editor/work/kits-ui-windows.png $S/head.png
kits-ui-windows.png: 980x640, window colour 23.1 %, Fusion pane 18.8 %
head.png: 980x640, window colour 22.9 %, Fusion pane 18.7 %
12224 of 627200 pixels differ (1.95 %)
$ grep -n -i 'captura igual\|sai igual' docs/PLAN-KITS-PY.md
48:   núcleo, e a janela sai igual no Windows e no Linux.
608:| 4 | **a janela mínima**: [...] captura igual no Windows e no Linux | 2, 3 |
```

Conserto, a alternativa mais forte: `--compare` agora **afirma**. Reprova acima de `CROSS_LIMIT = 5.0` % de pixels diferentes, ou quando uma das capturas perde a aparência fixa (o mesmo `judge_style` do gate), e sai 1. O plano cita o limite no item 5 da §0, no fim da §3.4 e na linha da fase 4 da §7.

Verde e os dois vermelhos, na mesma corrida (`nofusion.png` sai de uma cópia `git archive HEAD tools` com `setStyle("Windows")` no lugar do Fusion, rodada da cópia — a árvore viva não foi tocada):

```
$ python3 tools/kits/ui_check.py --compare $W $S/head.png
12224 of 627200 pixels differ (1.95 %)
ok    within 5.0 %, both with the fixed look
exit 0
$ python3 tools/kits/ui_check.py --compare $W $S/a4.png        # --tag A4
310271 of 627200 pixels differ (49.47 %)
FAIL  49.47 % differ, above the 5.0 % limit
exit 1
$ python3 tools/kits/ui_check.py --compare $W $S/nofusion.png
nofusion.png: 980x640, window colour 41.7 %, Fusion pane 0.0 %
249122 of 627200 pixels differ (39.72 %)
FAIL  nofusion.png loses the fixed look: Fusion's tab pane #ebebeb covers 0.0 %, under 10 %
FAIL  39.72 % differ, above the 5.0 % limit
exit 1
$ grep -n 'captura igual\|sai igual' docs/PLAN-KITS-PY.md
(vazio, exit 1)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `fc1879b` (2026-10-02): test(kits): make ui_check --compare assert a declared cross-platform limit
  - Files (`git show --name-status fc1879b`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-035.md`
    - `M tools/kits/ui_check.py`
