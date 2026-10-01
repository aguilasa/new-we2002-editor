---
id: CORR-KITS-013
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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `bc81d3ab`)

```text
$ python tools/kits/cli.py tex --iso-size roms/golden-european-deluxe.bin > i.txt; grep "^REFUSE" i.txt | grep -o "it has [0-9]* image" | sort | uniq -c; grep "^REFUSE" i.txt | grep -v "it has" | cut -c1-60
     54 it has 10 image
      4 it has 8 image
      6 it has 9 image
REFUSE TEX_48 (31464 bytes): record 0 (uniform, first set)
```

REPRODUCED: 64 com 8 a 10 registros, e o `TEX_48` recusado pelo LZSS (`stream at 48: distance 0 at 4810`), na leitura antiga e na nova.

### O que foi feito

§2.1 do plano:

- "65 TEX saem com 8 a 10 registros" virou as 65 recusas separadas: 64 por lista curta (54/6/4) e o `TEX_48` pelo LZSS.
- "Cada TEX ocupa um espaço de 20 setores" saiu — é um caso medido (104 de 105, por sonda) e nenhuma ferramenta o imprime. No lugar, o que a ferramenta afirma: nos 64, o que o cabeçalho aponta cabe antes do arquivo seguinte, que é a condição do `tex` para ler além do tamanho, e o "64 read past the ISO size" do resumo conta os que a cumpriram. Sem opção nova no `cli.py`.
- "lido até onde o cabeçalho diz, eles têm os 11" ganhou a ressalva medida: 7 dos 64 (`TEX_03`, `06`, `28`, `70`, `84`, `92`, `A2`) caem depois no LZSS ou no tamanho descomprimido e estão entre os 8 recusados.

Conferido sobre as duas saídas do `tex` (com e sem `--iso-size`): os 64 que a leitura nova lê além do tamanho são **o mesmo conjunto** dos 64 recusados por lista curta na antiga, e nenhuma recusa da leitura nova é por lista curta (`grep -c "it has [0-9]* image"` → 0, de 8 `REFUSE`).

### Verificação

```text
$ grep -n "65 TEX" docs/PLAN-KITS-PY.md
(sem saída, exit 1)
$ grep -n "20 setores" docs/PLAN-KITS-PY.md
(sem saída, exit 1)
```
- **Closed** — commit `b71d9cef` (2026-10-01): docs(kits): split the 65 ISO-size refusals in plan 2.1 and drop the 20-sector rule
  - Files (`git show --name-status b71d9cef`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-013.md`
