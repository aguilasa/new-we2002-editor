---
id: CORR-DMCP-005
---

# CORR-DMCP-005 — kits_selftest vermelho: o sandbox dos controles não copia tools/duckmcp, e o shim pes2/mcp.py não importa

Origin: [DMCP-TASK-06](/docs/tasks/duckmcp/06-cli-e-shim-mcp.md)

## Problem

`python3 tools/kits/selftest.py` sai 1 desde o commit `4de49640` (DMCP-TASK-06): o `controls.py` do
`kits` monta o sandbox com `COPIED = ("tools/kits", "tools/looks", "tools/pes2", "src/core", "data")`
(`tools/kits/controls.py:31`), e o `tools/pes2/mcp.py`, agora shim, importa `duckmcp` a partir de
`tools/` — que na cópia não tem `duckmcp`. A cópia limpa já sai vermelha, nenhum controle chega a ser
plantado, e o `kits_selftest` inteiro fica vermelho. A revisão da 06 não rodou o `kits_selftest`.

O mesmo buraco existe em mais três sandboxes que copiam `tools/pes2` sem `tools/duckmcp`:
`tools/kits/ui_check.py:93` (`COPIED = ("kits", "looks", "pes2")`), `tools/looks/controls.py`
(`_sandbox`, ~1115) e `tools/looks/ui_check.py` (~1144). Os do `looks` passam hoje só porque nada que
eles rodam importa o shim ainda; a DMCP-TASK-22 os quebra.

## Evidência

<!-- The exact command and its output that shows the problem. Whoever fixes this reproduces it first. -->

```text
$ python3 tools/kits/selftest.py --quiet; echo exit=$?
  FAIL  plant every control: raised RuntimeError: the unplanted sandbox is not green (exit 1):   FAIL  the self-check itself raised ModuleNotFoundError at mcp.py:27 in <module>  No module named 'duckmcp' -- checks after this point did not run;   FAIL  looks oracle.self_check() reports no failure  failures=1;   FAIL  the self-check itself raised ModuleNotFoundError at mcp.py:27 in <module>  No module named 'duckmcp' -- checks after this point did not run
  FAIL  there is at least one control
  FAIL  every planted control turns the gate red  []
controls: 3 failure(s)
kits_selftest: 3 failure(s)
exit=1
```

Medido em 2026-10-22 na HEAD `499569e4`.

## Root cause

A 06 trocou um módulo autocontido de `tools/pes2/` por um que depende de `tools/duckmcp/`, e as cópias
de árvore que os projetos fazem para plantar defeito listam os diretórios à mão. O §4.1 do plano previa
o `COPIED` do `kits` ganhando `tools/duckmcp`, mas só na Fase 7 — tarde, porque o shim nasceu na Fase 1.

## Fix

Os quatro sandboxes passam a copiar `tools/duckmcp` junto com `tools/pes2`, com a mesma regra de
`ignore` (`__pycache__`) que já usam. Nada de código da lib muda.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`
- `tools/kits/ui_check.py`
- `tools/looks/controls.py`
- `tools/looks/ui_check.py`

## Verificação

- `python3 tools/kits/selftest.py --quiet; echo exit=$?` → antes `kits_selftest: 3 failure(s)`, `exit=1`; depois 0 falhas, `exit=0`, e a linha dos controles diz quantos ficaram vermelhos.
- `python3 tools/looks/selftest.py --quiet; echo exit=$?` → continua `0 failure(s)`.
- `grep -n duckmcp tools/kits/controls.py tools/kits/ui_check.py tools/looks/controls.py tools/looks/ui_check.py` acha a cópia nos quatro.

## Log de Execução
