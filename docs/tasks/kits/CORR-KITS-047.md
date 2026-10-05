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

### 2026-10-04

Reproduzido na HEAD `5023982`, sem emulador: o dump `work/kits-oracle/match-3/vram-0.png` da corrida `--slot 3` da KITS-TASK-27 já estava no disco, e a planta da Evidência numa cópia `git archive HEAD tools` lida por `--png` dá o veredito invertido com saída 0:

```
$ sed -i 's/^IMAGE_SETS = ((0, 4), (1, 5))/IMAGE_SETS = ((4, 0), (5, 1))/; s/^SETS = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2}/SETS = {0: 2, 1: 2, 2: 2, 3: 2, 4: 1, 5: 1, 6: 1, 7: 1}/' $S/tools/kits/oracle.py
$ python3 $S/tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png | grep -v 'record '; echo rc=$?
  TEX_01: exact records of set 1 and 2
  TEX_13: exact records of set 1
  TEX_01 uniform  at (576,256): set 1 differs in 5050 of 8192 halfwords, set 2 in 4746 -- set 2 nearer
  TEX_01 sleeves  at (576,384): set 1 differs in 4211 of 8192 halfwords, set 2 in 2995 -- set 2 nearer
  TEX_13 uniform  at (640,256): set 1 differs in 2640 of 8192 halfwords, set 2 in 7198 -- set 1 nearer
  TEX_13 sleeves  at (640,384): set 1 differs in 4093 of 8192 halfwords, set 2 in 7693 -- set 1 nearer
rc=0
```

Conserto (depois da CORR-KITS-050, na mesma ferramenta):

- `--expect TAG=SET`, repetível. Falha quando a paleta de jogador exata achada não é só a do conjunto esperado (registro compartilhado ou plano não conta) ou quando uniforme ou mangas saem mais perto do outro conjunto. A paleta de goleiro fica de fora de propósito: na partida medida o goleiro da Escócia usa a do conjunto 2 (§4.1). `TAG=3` é recusado pelo `argparse`.
- No `kits_selftest`, `_oracle_checks`: uma VRAM sintética com a paleta de jogador e as duas páginas do conjunto 1 do contêiner do selftest escritas onde a partida as põe; `00=1` tem de passar, e `00=2` tem de dar três falhas (paleta e as duas páginas).
- Controle `oracle-sets-swapped` em `tools/kits/controls.py`: troca o `SETS`.

Verde e vermelho sobre o dump real:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --expect 01=1 --expect 13=2 | tail -1
  ok    TEX_01 in set 1, TEX_13 in set 2
(exit 0)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --expect 01=2 | tail -3
  FAIL  TEX_01: exact player palette of set 1, expected set 2
  FAIL  TEX_01: the uniform page is nearer to set 1, expected set 2
  FAIL  TEX_01: the sleeves page is nearer to set 1, expected set 2
(exit 1)
$ (a cópia plantada acima, com o oracle.py novo) python3 $S/tools/kits/oracle.py --png work/kits-oracle/match-3/vram-0.png --expect 01=1 --expect 13=2 | grep FAIL
  FAIL  TEX_01: exact player palette of set 2, expected set 1
  FAIL  TEX_01: the uniform page is nearer to set 2, expected set 1
  FAIL  TEX_01: the sleeves page is nearer to set 2, expected set 1
  FAIL  TEX_13: exact player palette of set 1, expected set 2
  FAIL  TEX_13: the uniform page is nearer to set 1, expected set 2
  FAIL  TEX_13: the sleeves page is nearer to set 1, expected set 2
(exit 1)
$ python3 tools/kits/selftest.py --no-plant | grep -E 'oracle --expect'
  ok    oracle --expect: set 1 written, 00=1 holds
  ok    oracle --expect: and 00=2 fails on the palette and both pages
$ python3 tools/kits/controls.py --only oracle-sets-swapped | tail -2
  RED    oracle-sets-swapped          kits/oracle.py :: SETS
controls: 1 of 1 red
$ python3 tools/kits/selftest.py | grep -E 'controls red|kits_selftest:'
  ..... 24 of 24 controls red
kits_selftest: 0 failure(s)
```
