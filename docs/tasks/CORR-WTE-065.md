---
id: CORR-WTE-065
title: "Correção: \"o maior b0 medido é 43\" — é 111 na europeia e 116 na japonesa"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-WTE-065: o maior `b0` medido não é 43

## Problema identificado

Três sítios da WTE-TASK-33 justificam **não modelar** `b0 >= 120` com o mesmo
número, e o número está errado:

| arquivo | linha | frase |
|---|---|---|
| `wte/tools/conta_ml.py` | 185 | `Nenhuma das duas ROMs chega la (o maior `b0` medido e 43)` |
| `wte/src/we2002_ml.pas` | 129 | `Nenhuma das duas ROMs chega la -- o maior `b0` medido e 43.` |
| `docs/tasks/33-slots-de-master-league.md` | 179 | `Nenhuma das duas ROMs chega lá — o maior `b0` medido é 43 —` |

O `43` é o maior `b0` entre os **pares que caem fora do vetor** — sai da linha
`fora: indice 488 -> 0x004335f4 pares [(267, 43, 121)]` que o `--medir`
imprime. O maior `b0` **medido** nas imagens é outro, e nenhum dos três sítios
o mediu.

A conclusão (`b0 >= 120` não é alcançado, e por isso não precisa de regra)
**continua de pé**. O que cai é a margem: ela não é 77, é 4.

## Evidência

Varredura dos 760 pares das duas cópias, a mesma leitura que a
`conta_ml.conta()` faz (salto de fronteira de setor incluído):

```text
work/ml-eu.bin  max b0 contados 111   max b0 em todos os pares 111
work/ml-jp.bin  max b0 contados 116   max b0 em todos os pares 116
```

Contra o afirmado:

| fonte | valor |
|---|---|
| `conta_ml.py:185`, `we2002_ml.pas:129`, `33-slots-de-master-league.md:179` | 43 |
| varredura dos 760 pares de `work/ml-eu.bin` | **111** |
| varredura dos 760 pares de `work/ml-jp.bin` | **116** |
| o teto da tabela (`ML_NC_POR_TIME`, 120 entradas) | 120 |

A saída do `--medir` que originou o engano, recortada:

```text
  ml-eu.bin: livres=13 proprios=453 distintos=449 fora=8
      fora: indice 488 -> 0x004335f4 pares [(267, 43, 121)]
```

## Causa raiz

O número foi tirado da lista de pares **fora do vetor**, que é um recorte, e
escrito como se fosse o máximo sobre todos os pares — e como ele mora só em
comentário e em markdown de task, nenhum `--check` o vê.

## Correção

### Arquivo: `wte/tools/conta_ml.py`

Medir o maior `b0` em vez de afirmá-lo. `conta()` já percorre os 760 pares:
devolver `max_b0` no dicionário, imprimi-lo no `--medir` e gravá-lo como
coluna nova de `wte/re/ml-slots-medido.tsv`. O `gera_md()` passa a compor a
frase a partir dessa coluna — assim o número entra no perímetro do
`--check` e não pode envelhecer sozinho.

### Arquivo: `wte/src/we2002_ml.pas`

Trocar a frase do comentário da linha 129 pela medida — os dois valores, com a
imagem de cada um, e a folga real até 120.

### Arquivo: `docs/tasks/33-slots-de-master-league.md`

Idem na linha 179, preservando a conclusão (não modelar) e trocando a
justificativa pela medida.

### Arquivo: `wte/tools/test_conta_ml.py`

Caso novo: `conta()` sobre imagem sintética com `b0` conhecido devolve esse
`b0` como máximo. Sem ele a coluna nova é mais um número sem guarda.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/conta_ml.py` | modificar |
| `wte/tools/test_conta_ml.py` | modificar |
| `wte/re/ml-slots-medido.tsv` | modificar (via `--medir`) |
| `wte/re/ml-slots.md` | modificar (via gerador) |
| `wte/src/we2002_ml.pas` | modificar |
| `docs/tasks/33-slots-de-master-league.md` | modificar |

## Verificação

- [x] `python3 wte/tools/conta_ml.py --medir work/ml-eu.bin work/ml-jp.bin`
      imprime `max b0` 111 e 116
- [x] `grep -rn 'maior .b0. medido' wte docs` não devolve mais `43`
- [x] `python3 wte/tools/conta_ml.py --check` verde
- [x] `cd wte/tools && python3 -m unittest test_conta_ml` verde
- [x] `lazbuild wte/wte.lpi` compila
- [x] `make -C wte check` rc 0
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-19

**Resumo do que foi feito:**

O `conta()` passou a medir o maior `b0` **entre os pares que chegam à
fórmula** — os que o enchimento e o `b1 < 23` descartam nunca a alcançam — e a
devolvê-lo como `max_b0`. O `--medir` grava o número na coluna nova `max_b0` do
`ml-slots-medido.tsv` e o imprime; o `gera_md()` compõe dali a seção "O ramo
`b0 >= 120`, que nenhuma das duas alcança", com os valores por imagem e a folga
real. Assim o número entra no perímetro do `--check` e não pode envelhecer
sozinho: medido **116** na japonesa, **111** na europeia, 4 de folga até 120 —
não 43, que era o maior `b0` da lista de pares *fora do vetor*, um recorte.

O comentário do `indice_do_bloco` deixou de afirmar número e passou a apontar
para a coluna. O `we2002_ml.pas` e a WTE-TASK-33, que não são gerados, ficaram
com os dois valores medidos e a origem deles.

**Problemas encontrados:**

O `textwrap.fill` quebrou `` `ml-eu.bin` `` no hífen e partiu o code span em
duas linhas — `break_on_hyphens=False` e `break_long_words=False`. Nome de
arquivo dentro de crase é o caso em que o wrap default estraga markdown.

O `linhas_medidas()` leria `r[8]` de um TSV medido antes desta coluna e
estouraria com `IndexError` a três frames de distância; ganhou guarda que
recusa com a mensagem certa e manda refazer o `--medir` em vez de completar a
mão — as duas últimas colunas são leitura de tela e não se inventam.

**Arquivos criados/modificados:**

- `wte/tools/conta_ml.py`
- `wte/tools/test_conta_ml.py`
- `wte/re/ml-slots-medido.tsv` (via `--medir`)
- `wte/re/ml-slots.md` (via gerador)
- `wte/src/we2002_ml.pas`
- `docs/tasks/33-slots-de-master-league.md`
