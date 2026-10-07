---
id: CORR-KITS-052
---

# CORR-KITS-052 — Colar inteira a saída do controle de conjuntos trocados, ou marcar o corte

Origin: [KITS-TASK-29](/docs/tasks/concluidos/kits/29-fechamento-fase-7.md)

## Problem

O Log da KITS-TASK-29 mostra três linhas FAIL do controle de conjuntos trocados, todas do `TEX_13`. O comando imprime seis. As três omitidas, sem marca, são as do `TEX_01` — justamente a metade do controle da fase 7 que diz respeito ao time da largada ("o time titular mostra o 1º par"). Quem lê o Log vê só o kit suplente sendo recusado.

## Evidência

```text
$ S=<scratch>; WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --slot 3 --cue $PWD/work/we2002-english.cue --out $S/f7 --lines --flags --expect 01=1 --expect 13=2
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png $S/f7/vram-0.png --expect 01=2 --expect 13=1 | grep -E 'FAIL|ok'
  FAIL  TEX_01: exact player palette of set 1, expected set 2
  FAIL  TEX_01: the uniform page is nearer to set 1, expected set 2
  FAIL  TEX_01: the sleeves page is nearer to set 1, expected set 2
  FAIL  TEX_13: exact player palette of set 2, expected set 1
  FAIL  TEX_13: the uniform page is nearer to set 2, expected set 1
  FAIL  TEX_13: the sleeves page is nearer to set 2, expected set 1
exit=1
$ grep -c 'FAIL  TEX_01' docs/tasks/kits/29-fechamento-fase-7.md
0
```

## Root cause

Hipótese: as linhas foram escolhidas à mão ao colar, e o corte não foi marcado.

## Fix

No Log de `docs/tasks/kits/29-fechamento-fase-7.md`, colar as seis linhas FAIL (ou acrescentar um "(…)" explícito com a contagem omitida). Só o Log muda; nenhum código.

## Arquivos a criar ou modificar

- `docs/tasks/kits/29-fechamento-fase-7.md`

## Verificação

```sh
grep -c 'FAIL  TEX_01' docs/tasks/kits/29-fechamento-fase-7.md
```

Dá 0 hoje; 3 depois do conserto.

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `a023979`: `grep -c 'FAIL  TEX_01' docs/tasks/kits/29-fechamento-fase-7.md` dá `0`.

O dump da corrida da KITS-TASK-29 ainda está no scratchpad daquela sessão, e é byte a byte o `work/kits-oracle/match-3/vram-0.png` (`cmp` igual, `screen.png` com o sha256 `ee1bfba6e7dc…` nos dois). O controle de conjuntos trocados sobre ele imprime as seis linhas, com saída 1:

```
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --expect 01=2 --expect 13=1 | grep -E 'FAIL|ok'
  FAIL  TEX_01: exact player palette of set 1, expected set 2
  FAIL  TEX_01: the uniform page is nearer to set 1, expected set 2
  FAIL  TEX_01: the sleeves page is nearer to set 1, expected set 2
  FAIL  TEX_13: exact player palette of set 2, expected set 1
  FAIL  TEX_13: the uniform page is nearer to set 2, expected set 1
  FAIL  TEX_13: the sleeves page is nearer to set 2, expected set 1
exit=1
```

Conserto: as seis linhas coladas no Log da KITS-TASK-29, no lugar das três do `TEX_13`.

```
$ grep -c 'FAIL  TEX_01' docs/tasks/kits/29-fechamento-fase-7.md
3
```
- **Closed** — commit `ea9bc76` (2026-10-04): docs(kits): paste all six lines of the swapped-sets control in the KITS-TASK-29 log
  - Files (`git show --name-status ea9bc76`):
    - `M docs/tasks/kits/29-fechamento-fase-7.md`
    - `M docs/tasks/kits/CORR-KITS-052.md`
