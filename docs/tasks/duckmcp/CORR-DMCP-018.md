---
id: CORR-DMCP-018
---

# CORR-DMCP-018 — Versionar controles para os checks de RAM, VRAM e serial do live.py

Origin: [DMCP-TASK-15](/docs/tasks/duckmcp/15-fechamento-fase-3.md)

## Problem

A task acrescenta três condições ao veredito `passed` e uma função `read_back` nova. Nenhum check do
selftest chama `read_back` ou `run` por esse caminho, e o único controle `live` do `controls.py` é o
`live-kills-on-skip`. O vermelho que o Log mostra veio de editar o `live.py` à mão e restaurá-lo; nada
na HEAD o refaz. E a condição de RAM nunca pode ser falsa, porque `Session.read_ram` já levanta
`ToolError` numa leitura curta.

## Evidência

```text
$ grep -n -i "live" tools/duckmcp/controls.py
187:        "live-kills-on-skip", "live", "live.py",
$ python3 tools/duckmcp/controls.py | tail -1
... (live) 1/1 ...
$ grep -n "read_back\|live.run" tools/duckmcp/selftest.py
470:                live.run("/x/a.cue", 1)
```

## Root cause

As condições novas só foram exercitadas contra o emulador real. O `_FakeClient` do `session.py` as
deixaria rodar offline (como o heredoc da CORR-DMCP-017), mas nada o usa para isso.

## Fix

No `tools/duckmcp/selftest.py`, um check que roda `live.run` com `fork.launch` trocado por um
`_FakeClient` que grava um PNG real de 1024x512 no `dump_vram`; afirmar `passed` verdadeiro, e falso
com serial vazio ou PNG de 1024x513. Depois, controles no `tools/duckmcp/controls.py` que quebram cada
condição e têm de ficar vermelhos.

## Arquivos a criar ou modificar

- `tools/duckmcp/selftest.py`
- `tools/duckmcp/controls.py`

## Verificação

`python3 tools/duckmcp/controls.py | tail -1` mostra `(live) 2/2` ou mais (hoje `(live) 1/1`), e
`python3 tools/duckmcp/selftest.py` lista uma linha `live:` do `read_back`.

## Log de Execução
