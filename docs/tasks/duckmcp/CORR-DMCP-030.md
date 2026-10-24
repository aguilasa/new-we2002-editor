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

**Reprodução (2026-10-24, HEAD `690a8474`, `rite reproduce CORR-DMCP-030 --cycle duckmcp`):** REPRODUCED
pelo segundo comando; o primeiro tem placeholder (`J=<cópia …>`) e saiu `shell_error`, sem decidir.

```text
$ grep -n '3137s\|435 s' docs/tasks/duckmcp/23-looks-breakpoints.md
47:**`--screen`.** Antes: a corrida da DMCP-TASK-22, `screen measured in 2702s` / … Depois: … `screen measured in 3137s` / … Os 435 s a mais vêm, ao que parece, da sonda de vida que a espera da lib roda a cada volta não pausada (`pgrep`). A contagem de paradas não muda.
```

O `--screen` (~45 min de emulador) não foi corrido de novo aqui: a correção é de texto, e a medida que
a desfaz é a da revisão (2685 s na HEAD entregue), citada como dela.

**Conserto:** nota logo depois da linha 47 da `23-looks-breakpoints.md`, sem reescrever o Log: a
atribuição à sonda de vida não se sustenta, os 435 s não reproduzem (2685 s na HEAD, contra 2702 s do
"antes"), uma corrida por lado não mede o custo, e a linha não serve para escolher `HIT_POLL`.

**Verificação:**

```text
$ grep -n 'ao que parece, da sonda de vida' docs/tasks/duckmcp/23-looks-breakpoints.md | cut -c1-60
47:**`--screen`.** Antes: a corrida da DMCP-TASK-22, `screen
$ grep -n 'CORR-DMCP-030' docs/tasks/duckmcp/23-looks-breakpoints.md
49:> **Nota (CORR-DMCP-030, 2026-10-24):** a atribuição acima não se sustenta. A revisão desta task rodou
128:- **Reviewed** (2026-10-24) at `19e27adf`: CORR-DMCP-030
$ rite check --cycle duckmcp --json      # errors, warnings
0 0
```

A linha 47 continua achada e vem seguida (linha 49) da nota que a desfaz com a medida de 2685 s.
- **Closed** — commit `edc90412` (2026-10-24): docs(duckmcp): note that the 435 s of --screen in task 23 do not reproduce
  - Files (`git show --name-status edc90412`):
    - `M docs/tasks/duckmcp/23-looks-breakpoints.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-030.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
