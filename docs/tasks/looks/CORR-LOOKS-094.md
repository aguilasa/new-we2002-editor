---
id: CORR-LOOKS-094
title: "Tirar das docstrings do ritmo o timer de HBlank que o código não lê"
origin: LOOKS-TASK-33
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-094 — Tirar das docstrings do ritmo o timer de HBlank que o código não lê

Origin: [LOOKS-TASK-33](/docs/tasks/looks/33-a-janela-animada.md)

## Problem

Duas docstrings dizem que o timer de HBlank conta 263 linhas por quadro: a do
`layout.FRAME_TICKS` diz que foi medido assim, e a do `oracle.check_rhythm`
diz que a conferência o exige. Nenhuma das duas é verdade: o `judge_clock`
não lê timer nenhum, e a armadilha 102, a docstring do `NTSC_LINES` e o log
da LOOKS-TASK-33 dizem que os timers raiz foram **recusados** como
testemunha (523 contra 65.463 HBlanks no mesmo ciclo). Os docs se
contradizem sobre o que sustenta o `FRAME_TICKS`.

## Evidência

```text
$ grep -n "HBlank" tools/looks/layout.py tools/looks/oracle.py docs/prompts/perfil-looks.armadilhas.md
tools/looks/layout.py:2137:566,203.8 a frame.  The HBlank timer counts 263 lines a frame over the same
tools/looks/oracle.py:7975:cycle timer 1 came back 523 HBlanks on one state and 65,463 on the other.
tools/looks/oracle.py:8250:          the HBlank timer has to count 263 lines a frame and timer 2 the
docs/prompts/perfil-looks.armadilhas.md:168:    ciclo o timer 1 contou 523 HBlanks num state e 65.463 no outro —, e o
$ sed -n 8115,8156p tools/looks/oracle.py | grep -ci "timer\|hblank"
0
```

## Root cause

Hipótese: as docstrings foram escritas para um primeiro plano que usava os
contadores raiz como testemunha; quando os timers se mostraram programados
pelo jogo, a conferência passou a ser a conta do padrão NTSC e as duas
docstrings não acompanharam.

## Fix

Em `tools/looks/layout.py`, reescrever a docstring do `FRAME_TICKS` dizendo
que a testemunha é o padrão NTSC (`oracle.ntsc_frame_ticks()`), conferido
contra o `get_gpu_state`. Em `tools/looks/oracle.py`, tirar da docstring do
`check_rhythm` a oração "HBlank timer … timer 2".

## Arquivos a criar ou modificar

- tools/looks/layout.py
- tools/looks/oracle.py

## Verificação

`grep -n "HBlank timer counts\|HBlank timer has to" tools/looks/layout.py tools/looks/oracle.py`
imprime 2 linhas hoje e não pode imprimir nada depois do conserto.

## Log de Execução
