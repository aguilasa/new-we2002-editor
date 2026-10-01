---
id: CORR-KITS-013
title: "Correct the §2.1 counts that no tool prints"
origin: KITS-TASK-07
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-013 — Correct the §2.1 counts that no tool prints

Origin: [KITS-TASK-07](/docs/tasks/kits/07-tex-e-guarda-de-forma.md)

## Problem

O §2.1 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md), escrito pela KITS-TASK-07, diz "Lido pelo tamanho ISO, 65 TEX saem com 8 a 10 registros". A ferramenta dá **64** com 8 a 10 registros (54×10, 6×9, 4×8); a 65ª recusa é o `TEX_48`, que tem 11 registros e é recusado pelo LZSS. O mesmo parágrafo diz "Cada TEX ocupa um espaço de 20 setores até o arquivo seguinte", o que vale para 104 dos 105, e nenhum comando versionado imprime o tamanho do espaço.

## Evidência

```text
$ sed -n 175,177p docs/PLAN-KITS-PY.md
estava. Cada TEX ocupa um espaço de 20 setores até o arquivo seguinte, e o
que o cabeçalho aponta está dentro dele. Lido pelo tamanho ISO, 65 TEX
saem com 8 a 10 registros; lido até onde o cabeçalho diz que o contêiner
$ python tools/kits/cli.py tex --iso-size roms/golden-european-deluxe.bin > i.txt; grep "^REFUSE" i.txt | grep -o "it has [0-9]* image" | sort | uniq -c; grep "^REFUSE" i.txt | grep -v "it has" | cut -c1-60
     54 it has 10 image
      4 it has 8 image
      6 it has 9 image
REFUSE TEX_48 (31464 bytes): record 0 (uniform, first set)
```

Sonda do revisor, sem versão (`source._slot_end(img, e) - e.lba` sobre os `TEX_*` da European Deluxe):

```text
slot Counter({20: 104, 380: 1})
```

## Root cause

Hipótese: o 65 é o total de recusas da linha de resumo, rotulado como "8 a 10 registros" sem separar o `TEX_48`; o 20 é um caso medido escrito como regra.

## Fix

No §2.1 do plano, dizer "64 saem com 8 a 10 registros (e o `TEX_48`, com 11, é recusado pelo LZSS)" e "104 dos 105 têm 20 setores até o arquivo seguinte", ou tirar essa afirmação. Se a contagem de setores ficar no texto, dar antes ao `cli.py tex` uma opção que imprima o espaço de cada TEX.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`
- `tools/kits/cli.py` (só se a afirmação dos setores ficar)

## Verificação

```text
$ grep -n "65 TEX" docs/PLAN-KITS-PY.md
```

Hoje imprime a linha 176; depois do conserto, não imprime nada.

## Log de Execução
