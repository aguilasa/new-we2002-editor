---
id: CORR-KITS-047
---

# CORR-KITS-047 — Fazer o oracle.py afirmar o conjunto que reporta, não só imprimir

Origin: [KITS-TASK-27](/docs/tasks/kits/27-titular-e-suplente-no-jogo.md)

## Problem

O veredito da §4.1 e o controle do critério 2 da KITS-TASK-27 (o time da largada mostra o 1º par) só são impressos pelo `tools/kits/oracle.py`. O `main()` devolve 0 seja qual for o conjunto que sair mais próximo: com o mapeamento de conjuntos plantado ao contrário, a ferramenta reporta Escócia no conjunto 2 e Dinamarca no 1, e sai 0. Veredito impresso e não afirmado não é gate. A ferramenta também não está no `selftest.py` nem no `controls.py` (a linha "oracle.py self-check" do `kits_selftest` é do módulo do `looks`).

## Evidência

```text
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C $S
$ sed -i 's/^IMAGE_SETS = ((0, 4), (1, 5))/IMAGE_SETS = ((4, 0), (5, 1))/; s/^SETS = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2}/SETS = {0: 2, 1: 2, 2: 2, 3: 2, 4: 1, 5: 1, 6: 1, 7: 1}/' $S/tools/kits/oracle.py
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --slot 3 --cue $PWD/work/we2002-english.cue --out $S/match-3
$ (cd $S && WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png $S/match-3/vram-0.png); echo rc=$?
  TEX_01  record  2 player palette     set 2  at (0,486), (0,490)
  TEX_13: exact records of set 1
  TEX_01 uniform  at (576,256): ... -- set 2 nearer
  TEX_13 uniform  at (640,256): ... -- set 1 nearer
rc=0
```

## Root cause

Hipótese: a ferramenta foi escrita como leitor de investigação, e a resposta esperada (que tag joga em que conjunto) nunca lhe foi dada como entrada.

## Fix

Em `tools/kits/oracle.py`, acrescentar `--expect TAG=SET` (por exemplo `--expect 01=1 --expect 13=2`), que falha quando a paleta de jogador exata ou a página mais próxima discorda. Em `tools/kits/controls.py`, um controle plantado para ela, sobre fixture de dump de VRAM ou VRAM sintética; registrar a corrida vermelha no Log.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `tools/kits/controls.py`

## Verificação

`python3 tools/kits/oracle.py --png <dump da partida> --expect 01=2` tem de sair diferente de zero. Hoje a opção não existe e a corrida sai 0 seja qual for o conjunto.

## Log de Execução
