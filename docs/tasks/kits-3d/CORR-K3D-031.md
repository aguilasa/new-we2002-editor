---
id: CORR-K3D-031
---

# CORR-K3D-031 — Controle físico ligado entra no emulador do oráculo e suja as corridas ao vivo

Origin: [CORR-K3D-026](/docs/tasks/kits-3d/CORR-K3D-026.md)

## Problem

O fork do DuckStation que o `oracle.py` sobe no `:98` usa a configuração da máquina, e o `[Pad1]`
dela é `SDL-0`. O SDL lê o controle físico qualquer que seja o display, então um controle ligado —
em 2026-10-11 um `Wireless Controller` em uso no RetroArch — manda botões e analógico para o jogo
sob teste. Em quatro corridas de `--replay-field` seguidas saíram quatro tabelas diferentes: quadro
preto no k = 8 do slot 9, MCP sem resposta no slot 10, câmera ainda voando no k = 4 do R2
(`still 188`) e o k = 0 do slot 9 se mexendo (`still 282`) sem toque nenhum. Desligado o controle,
as corridas voltaram ao que a K3D-TASK-18 mediu. Nenhuma ferramenta confere isso antes de correr.

## Evidência

```text
$ grep -n '^Up = \|^L2 = ' ~/.local/share/duckstation/settings.ini
L2 = SDL-0/+LeftTrigger
Up = SDL-0/DPadUp
$ grep -rln 'js0\|/dev/input\|joystick' tools/looks/oracle.py tools/pes2/fork.py tools/kits/oracle.py
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-moving-capture.json | grep -E '^ +0  '
    0  -           65    1   5197    1.3      -      -    34   13 None    92      none             None    282  
```

O `grep -rln` não acha nada: nenhuma guarda. A captura `replay-field-9-moving-capture.json` é a do
k = 0 se mexendo; o mesmo state, sem controle, dá `4681` e `still 0`.

## Root cause

O SDL entrega o controle a todo processo que o abre, e o oráculo herda os bindings do usuário por
decisão (CLAUDE.md, 2026-09-02: nenhum lançador configura o DuckStation).

## Fix

Uma guarda no lançamento do fork (`tools/pes2/fork.py` ou no `Oracle.__enter__` de
`tools/looks/oracle.py`), do jeito da guarda de janela grande do `golden_check.sh`: com um
joystick presente (`/dev/input/js*`), recusar a corrida ao vivo com a mensagem do que fazer, sem
mexer na configuração do DuckStation. Planta e controle no padrão do ciclo.

## Arquivos a criar ou modificar

- tools/pes2/fork.py (ou tools/looks/oracle.py)
- tools/kits/controls.py

## Verificação

Com `/dev/input/js0` presente, `python3 tools/kits/oracle.py --replay-field 9` sai sem subir o
emulador e diz por quê; sem ele, corre.

## Log de Execução
