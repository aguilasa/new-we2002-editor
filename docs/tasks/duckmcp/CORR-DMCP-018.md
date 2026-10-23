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

2026-10-23 — reproduzido: o único controle `live` era `live-kills-on-skip` (`(live) 1/1`), e o selftest
só chamava `live.run` no check de morte do emulador.

Conserto, já sobre o veredito `failures()` da CORR-DMCP-019:
- **Check novo.** `check_live_read_back` roda `live.main` offline. Um `_FakeClient` grava um PNG de
  verdade (`png.encode`) no `dump_vram`, e o check afirma cinco coisas:
  - passa com RAM inteira, VRAM de 1024×512 e serial;
  - `FAIL (serial)` com serial vazio;
  - `FAIL (vram)` com VRAM de 1024×513;
  - linha FAIL com `PngError` quando o arquivo de VRAM não decodifica (CORR-DMCP-017);
  - linha FAIL com `ToolError` numa leitura curta de RAM.
- **RAM e quadros direto no `failures()`.** Pelo falso essas duas condições não falham: o `read_ram`
  recusa leitura curta antes, e o falso anda um quadro por chamada.
- **Controles.** Cinco controles `live-*` desligam uma condição cada (`if False:`) ou tiram o
  `ValueError` do `except`.

Verificação:

```text
$ python3 tools/duckmcp/selftest.py | grep -E "  (ok|FAIL) +live:|check\(s\)"
  ok    live: a skipped launch leaves another session's emulator alive
  ok    live: a launch that fails after its Popen stops the new pid
  ok    live: the read-back passes on RAM, a 1024x512 VRAM and a serial
  ok    live: an empty serial fails, named serial
  ok    live: a 1024x513 VRAM fails, named vram
  ok    live: a VRAM file that does not decode ends in a FAIL line
  ok    live: a short RAM read ends in a FAIL line
  ok    live: failures() is empty when all four hold
  ok    live: failures() names frames when frame_number moves wrong
  ok    live: failures() names ram when RAM is short
duckmcp_selftest: 369 check(s) ran, 0 failure(s)
$ for c in live-frames-unchecked live-ram-unchecked live-vram-unchecked live-serial-unchecked live-png-error-escapes; do python3 tools/duckmcp/controls.py --only $c | sed -n 2p | cut -c1-120; done
red    live-frames-unchecked (rule live): FAIL  live: failures() names frames when frame_number moves wrong
red    live-ram-unchecked (rule live): FAIL  live: failures() names ram when RAM is short
red    live-vram-unchecked (rule live): FAIL  live: a 1024x513 VRAM fails, named vram  (0, 'duckmcp_live:
red    live-serial-unchecked (rule live): FAIL  live: an empty serial fails, named serial  (0, 'duckmcp_l
red    live-png-error-escapes (rule live): FAIL  live: a VRAM file that does not decode ends in a FAIL l
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 31 control(s), 31 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (gpu) 2/2, (live) 6/6, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
```
