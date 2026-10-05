---
id: CORR-KITS-064
---

# CORR-KITS-064 — Cobrir o reset por duplo clique com juiz e planta

Origin: [KITS-TASK-37](/docs/tasks/kits/37-reset-e-dica-das-costas.md)

## Problem

A §3.4 diz que o duplo clique na vista desfaz o giro como o botão, e o commit cdf41c5 acrescenta `FigureView.mouseDoubleClickEvent`. Nenhum gate o exercita: o `reset_judge` do `kits_ui` só dirige `--reset`, que chama `reset_button.click()`. Se o `mouseDoubleClickEvent` fosse apagado, os gates continuariam verdes. O comportamento funciona hoje — uma sonda do revisor (`QTest.mouseDClick` numa `FigureView` girada a 0/30) a trouxe de volta a 180,0/0,0 —, mas a sonda não é versionada.

## Evidência

```text
$ grep -nE "DoubleClick|dclick|mouseDClick" tools/kits/ui_check.py tools/kits/selftest.py
(sem saída)
$ grep -n mouseDoubleClickEvent tools/kits/ui/figure_view.py
157:    def mouseDoubleClickEvent(self, _event) -> None:
$ git show cdf41c5 -- tools/kits/ui/figure_view.py | grep -A3 mouseDoubleClickEvent
+    def mouseDoubleClickEvent(self, _event) -> None:
+        self.drag = None
+        self.reset()
```

## Root cause

Hipótese: os critérios de pronto só nomearam o caminho `--reset`, e só ele ganhou juiz.

## Fix

Em `tools/kits/ui_check.py`, um juiz de duplo clique — uma opção do `app.py` que mande `QTest.mouseDClick` à `figure_view` depois de `--yaw`/`--pitch`, ou uma verificação headless da `FigureView` — e uma planta que torna `mouseDoubleClickEvent` um no-op em `figure_view.py`.

## Arquivos a criar ou modificar

- `tools/kits/ui_check.py`
- `tools/kits/ui/app.py` (se for por opção de linha de comando)

## Verificação

`WE2002_LOOKS_IMAGE=<.bin japonês absoluto> python3 tools/kits/ui_check.py` não mostra hoje nenhuma linha de duplo clique; depois do conserto mostra uma linha `ok` de duplo clique e a planta 'double-click does nothing' vermelha.

## Log de Execução
