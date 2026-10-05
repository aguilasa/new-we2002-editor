---
id: CORR-KITS-050
---

# CORR-KITS-050 — Corrigir a docstring do report() que promete filtro de conjunto compartilhado

Origin: [KITS-TASK-27](/docs/tasks/kits/27-titular-e-suplente-no-jogo.md)

## Problem

A docstring de `report()` em `tools/kits/oracle.py` diz que conta um registro "not shared byte for byte with the other set of the same kit", mas o código não tem esse filtro: todo registro não plano de índice 0-7 é contado. É por isso que o `TEX_A4` (conjuntos idênticos) sai como "exact records of set 1 and 2", como o Log anota.

## Evidência

```text
$ sed -n '/^def report(hits/,/^    return/p' tools/kits/oracle.py
  """... not flat, and
  not shared byte for byte with the other set of the same kit."""
  ...
      if not flat and index in SETS:
          worn.setdefault(tag, set()).add(SETS[index])
$ grep -n "shared byte for byte" tools/kits/oracle.py
187:    shared byte for byte with the other set of the same kit."""
```

## Root cause

A docstring foi escrita antes do código, ou o filtro caiu.

## Fix

Em `tools/kits/oracle.py`, implementar o filtro (pular o índice i quando `payload(i) == payload(i±4)`) ou tirar a cláusula da docstring.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`

## Verificação

`grep -n "shared byte for byte" tools/kits/oracle.py` não acha nada; ou, com o filtro, `--png` sobre o dump do LOOKS SET (`work/kits-oracle/looks-2`) deixa de imprimir "TEX_A4: exact records of set 1 and 2".

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `5023982`, sobre o dump gravado da tela LOOKS SET (sem emulador):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/looks-2/vram-0.png | grep -v ' record '
  105 kit container(s) read from /home/ingmar/desenvolvimento/github/new-we2002-editor/roms/japanese-shift-jis.bin
  TEX_A4: exact records of set 1 and 2
  TEX_A4 uniform  at (576,256): set 1 differs in  480 of 8192 halfwords, set 2 in  480 -- a tie
  TEX_A4 sleeves  at (576,384): set 1 differs in    0 of 8192 halfwords, set 2 in    0 -- a tie
```

Conserto: o filtro implementado, não a cláusula tirada. `search` devolve um quinto campo, `shared` — o registro é byte a byte o do outro conjunto (índice ±4) —, e `report` não conta registro compartilhado para nomear conjunto: marca a linha com `the same in both sets, names neither` e, se o kit não nomeou conjunto nenhum, diz isso. Assim a docstring passa a ser verdade.

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/looks-2/vram-0.png | grep -v ' record '
  105 kit container(s) read from /home/ingmar/desenvolvimento/github/new-we2002-editor/roms/japanese-shift-jis.bin
  TEX_A4: its set records are found, but both sets are the same: no set named
  TEX_A4 uniform  at (576,256): set 1 differs in  480 of 8192 halfwords, set 2 in  480 -- a tie
  TEX_A4 sleeves  at (576,384): set 1 differs in    0 of 8192 halfwords, set 2 in    0 -- a tie
```

Controle de que o filtro não apaga achado verdadeiro: no dump da partida (`TEX_01` e `TEX_13`, nenhum registro compartilhado) o veredito é o mesmo de antes:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png | grep 'TEX_.*:'
  TEX_01: exact records of set 1 and 2
  TEX_13: exact records of set 2
```

A linha 45 do Log da KITS-TASK-27 (`TEX_A4 wears set 1 and 2`) é transcrição de uma versão anterior da ferramenta, e fica.
- **Closed** — commit `b35975a` (2026-10-04): fix(kits): oracle.py stops naming a set from records both sets share
  - Files (`git show --name-status b35975a`):
    - `M docs/tasks/kits/CORR-KITS-050.md`
    - `M tools/kits/oracle.py`
