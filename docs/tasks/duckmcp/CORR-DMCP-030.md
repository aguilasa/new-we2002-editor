---
id: CORR-DMCP-030
---

# CORR-DMCP-030 — Desfazer no Log da 23 a causa atribuída aos 435 s do --screen

Origin: [DMCP-TASK-23](/docs/tasks/duckmcp/23-looks-breakpoints.md)

## Problem

O Log diz que o `--screen` levou 3137 s depois contra 2702 s antes, e atribui os 435 s a mais, "ao que
parece", à sonda de vida (`pgrep`) que o `debug.wait_for_pause` roda a cada volta. Na HEAD entregue o
mesmo comando mediu 2685 s, menos que o "antes" citado: a lentidão não reproduz e a causa sugerida não
se sustenta. Quem ler o Log pode concluir que a sonda de vida custa ~16% e escolher um `HIT_POLL` com
base nisso.

## Evidência

```text
$ J=<cópia de roms/japanese-shift-jis.bin>; WE2002_LOOKS_IMAGE=$J WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/looks/oracle.py --screen
  screen measured in 2685s
oracle --screen: 0 difference(s) from screen.json
$ grep -n '3137s\|435 s' docs/tasks/duckmcp/23-looks-breakpoints.md
(a linha do `--screen`: "screen measured in 3137s" … "Os 435 s a mais vêm, ao que parece, da sonda de vida")
```

## Root cause

Hipótese, não provada: a duração do `--screen` varia de uma corrida para outra (máquina e emulador), e
uma corrida de cada lado foi lida como efeito do código.

## Fix

Na `docs/tasks/duckmcp/23-looks-breakpoints.md`, registrar que a duração não reproduz (2685 s na HEAD) e
retirar a atribuição à sonda de vida, ou trocá-la por uma medida com mais de uma corrida por lado. O Log
é histórico: acrescentar nota, não reescrever.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/23-looks-breakpoints.md`

## Verificação

`grep -n 'ao que parece, da sonda de vida' docs/tasks/duckmcp/23-looks-breakpoints.md` acha a linha
hoje; depois da correção, ou não acha mais, ou a linha vem seguida de nota que a desfaz com a medida de
2685 s.

## Log de Execução
