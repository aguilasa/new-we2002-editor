---
id: CORR-KITS-083
---

# CORR-KITS-083 — Corrigir ou remedir a afirmação de que o pareamento por corners erra 2 a 4 px

Origin: [KITS-TASK-45](/docs/tasks/kits/45-pose-figura-partida.md)

## Problem

A afirmação aparece em quatro lugares: a §4.3 do plano ("Pareado por `corners`, cada peça erra de 2 a 4 px"), o comentário em `tools/kits/oracle.py:1389` ("every piece is off by 2 to 4 px"), o Log da KITS-TASK-45 ("2 a 4 px por peça (primeira corrida, worst 3.96 px)") e a nota acrescentada à task 47. Na própria captura do executor, parear por `corners` dá 1,48 a 4,05 px: três peças ficam abaixo do limite de 2,0, então "toda peça" é falso e o pior não é 3,96. A HEAD não tem opção que meça esse pareamento; o número saiu de sonda descartável.

## Evidência

```text
$ D=$(mktemp -d); git archive HEAD | tar -x -C $D; sed -i 's/zip(prim.indices, prim.texcoords)/zip(prim.corners, prim.texcoords)/' $D/tools/kits/oracle.py; (cd $D && WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python tools/kits/oracle.py --match-pose 5 --frame-json <cópia de work/kits-oracle/pose-5.json> | grep -E '^      section|worst' | awk '$3<2.0 || /worst/')
      section 96     1.86 px over 7 primitive(s)
      section 98     1.48 px over 7 primitive(s)
      section 98     1.63 px over 7 primitive(s)
  worst piece 4.05 px, limit 2.00
$ grep -rn "2 a 4 px\|2 to 4 px" docs/PLAN-KITS-PY.md docs/tasks/kits/4[57]*.md tools/kits/oracle.py
docs/PLAN-KITS-PY.md:733: … Pareado por `corners`, cada peça erra de 2 a 4 px.
tools/kits/oracle.py:1389:        # `corners` every piece is off by 2 to 4 px, by `indices` under 1
docs/tasks/kits/45-pose-figura-partida.md:91: …
docs/tasks/kits/47-figura-partida-aba-3d.md:37: …
```

(A captura em `work/kits-oracle/pose-5.json` veio de corrida ao vivo; a do revisor saiu byte a byte igual.)

## Root cause

Hipótese: o número saiu de uma corrida avulsa, provavelmente sobre código anterior ao commit (o Log diz "primeira corrida"), e foi escrito sem remedição na HEAD.

## Fix

Uma opção versionada, por exemplo `--pair-by corners`, no `oracle.py --match-pose` (em `piece_error`) que imprima a tabela por peça sob esse pareamento; colar a saída real (1,48 a 4,05 px, três peças abaixo do limite) na §4.3, no comentário do `oracle.py`, no Log da task 45 e na nota da task 47.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`
- `docs/tasks/kits/45-pose-figura-partida.md`
- `docs/tasks/kits/47-figura-partida-aba-3d.md`

## Verificação

`python tools/kits/oracle.py --match-pose 5 --frame-json work/kits-oracle/pose-5.json --pair-by corners` existe e imprime a faixa que a §4.3 cita; e `grep -rn "2 a 4 px\|2 to 4 px" docs/PLAN-KITS-PY.md docs/tasks/kits/4[57]*.md tools/kits/oracle.py` não acha nada. Hoje a opção não existe e a grep acha 4 linhas.

## Log de Execução

Reproduzido em 2026-10-06 sobre `7be3178`. A frase aparecia em quatro lugares e nenhuma opção a
media:

```text
$ grep -rn "2 a 4 px\|2 to 4 px" docs/PLAN-KITS-PY.md docs/tasks/kits/4[57]*.md tools/kits/oracle.py | cut -c1-60
docs/tasks/kits/47-figura-partida-aba-3d.md:37:Da KITS-TASK-45 (2026-10-06, §4.3): a pose
docs/tasks/kits/45-pose-figura-partida.md:91:O texel de cada canto segue `Primitive.indice
docs/PLAN-KITS-PY.md:733:oferece como desembaraçada. Pareado por `corners`, cada peça er
tools/kits/oracle.py:1389:        # `corners` every piece is off by 2 to 4 px, by `indices
```

Conserto:

- `tools/kits/oracle.py`: `--pair-by indices|corners` no `--match-pose`. O `piece_error` recebe o
  pareamento; `PAIRINGS` documenta os dois. Com `corners` a corrida é relatório: imprime a tabela
  e o julgamento e não grava pose.
- O comentário do `piece_error` não cita mais número.
- A §4.3, o Log da task 45 e a nota da task 47 citam a faixa medida.
- O controle `oracle-pose-texel-order` (CORR-KITS-084) passou a plantar a linha nova,
  `order = prim.corners`.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --match-pose 5 --frame-json work/kits-oracle/pose-5.json --pair-by corners
  PAIR   texels paired with the vertices in `corners` order, not the stored one
      section 96     1.86 px over 7 primitive(s)
      section 98     1.48 px over 7 primitive(s)
      section 98     1.63 px over 7 primitive(s)
      (… 24 linhas por peça, as outras 21 acima de 2,00 …)
  worst piece 4.05 px, limit 2.00
  (--pair-by corners is a report: nothing is written)
$ … --match-pose 5 --frame-json work/kits-oracle/pose-5.json
  worst piece 1.01 px, limit 2.00
  ok    every piece of both figures lands within 2.00 px of its frame
$ grep -rn "2 a 4 px\|2 to 4 px" docs/PLAN-KITS-PY.md docs/tasks/kits/4[57]*.md tools/kits/oracle.py
(sem saída)
$ python3 tools/kits/controls.py --only oracle-pose-texel-order
  RED    oracle-pose-texel-order      kits/oracle.py :: piece_error
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
```
