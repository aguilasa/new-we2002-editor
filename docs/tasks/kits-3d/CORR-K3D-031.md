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

### 2026-10-12 — o oráculo recusa correr com controle ligado

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `677e37d`:
- as duas linhas `SDL-0` do `settings.ini`;
- o `grep -rln` sem nada;
- o k = 0 com `5197` e `282`.

Conserto:
- `tools/pes2/fork.py` ganhou `joysticks(root)`, que lista os nós `js<N>` de `/dev/input`, e
  `refuse_joysticks(root)`, que levanta `Fail` (não `Skip`: corrida que não mede não passa) com a
  mensagem do que fazer.
- O `self_check` do `fork.py` ganhou dois casos: diretório sem joystick passa, e `js0` recusa.
- `tools/looks/oracle.py` chama `fork.refuse_joysticks()` no `Oracle.__enter__`, antes do
  `fork.launch`. É por ali que entra toda medição ao vivo do `kits` e do `looks`.
- A configuração do DuckStation continua intocada.
- O `make pes2-play` e o `pad.py`, que o usuário dirige com o próprio controle, não passam pelo
  `Oracle` e não são afetados.

Selftest e controles:
- Casos novos no `tools/kits/selftest.py` (bloco `live guard`):
  - `live runs: a plugged-in controller refuses the run`;
  - `live runs: the oracle refuses before it boots the fork`, com `fork.joysticks` trocado por um que
    devolve `js0` e `fork.launch` por um que acusa ter sido chamado.
- Dois controles no `controls.py`, ambos `RED` com `--only`:
  - `fork-joystick-let-through`;
  - `looks-oracle-joystick-unasked`.

Verificação:
- O vermelho com o controle de verdade não pôde ser visto: o usuário o desligou a pedido
  (2026-10-11), e `ls /dev/input/js*` não acha nada. Quem o cobre é o caso do selftest, que passa
  pelo mesmo `Oracle.__enter__`.
- Sem controle, a corrida passa da guarda e sobe o fork:
  `timeout 40 python3 tools/kits/oracle.py --replay-field 9 …` imprimiu `fork 939827 on :98` e
  `duckstation-mcp 1.0.0 answering`. Depois o fork foi derrubado com `tools/pes2/fork.py kill`.
- `python3 tools/pes2/fork.py --self-check`: `SELF-CHECK OK`.
- `ctest --test-dir build -R 'pes2_selftest|looks_selftest|tasks'`:
  `100% tests passed, 0 tests failed out of 3`.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 50 of 50 red`.
- **Closed** — commit `bfda5b23` (2026-10-12): fix(kits): refuse a live oracle run while a game controller is plugged in
  - Files (`git show --name-status bfda5b23`):
    - `M docs/tasks/kits-3d/CORR-K3D-031.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
    - `M tools/looks/oracle.py`
    - `M tools/pes2/fork.py`
