---
id: LOOKS-TASK-05
title: "`modelfile.py` — as 106 seções do `MODEL.BIN` e as 11 do `EDT_MOD.BIN`"
type: implementação
category: formato
phase: 1
depends_on: ["LOOKS-TASK-04"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.5"
status: concluído
---

# LOOKS-TASK-05: Os dois arquivos de modelo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.4 e
  §1.5.
- **Os dois arquivos não se percorrem do mesmo jeito** no que diz respeito ao
  **início**: o do `MODEL.BIN` é constante (1816, ver o último critério), e o do
  `EDT_MOD.BIN` é **derivado** pelo `layout.geometry_start()`. A partir do
  início certo, os dois varrem **contíguos** pela regra da corrida de zeros da
  §1.4 — inclusive o `EDT_MOD.BIN`, ao contrário do que a armadilha 3 do perfil
  diz ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md), e o
  encaminhamento está na
  [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md)).
- **A ordem da lista não é a ordem do arquivo.** É por isso que a lista é
  necessária, e não porque a varredura não alcance as seções. Assumir a do
  arquivo embaralha peça sem sintoma visível.

---

## Objetivo

`tools/looks/modelfile.py`: percorrer os dois arquivos e entregar a lista de
seções, preservando a ordem que a lista de montagem declara.

---

## Critério de conclusão

- [x] `MODEL.BIN` percorrido a partir de 1816 dá **106 seções, 2.461 vértices,
      1.767 primitivas**, terminando **exatamente em 64.800 = EOF**.
- [x] Os **6 grupos** do `MODEL.BIN` aparecem com os tamanhos
      `[55, 1, 34, 7, 5, 4]`.
- [x] O cabeçalho do `EDT_MOD.BIN` é lido como **duas** listas de registros
      `(contagem, ponteiro)` terminadas por `0x000000FF`, de **onze registros
      cada** — não uma. Elas compartilham 15.704 e 17.572, nas mesmas posições.
- [x] `EDT_MOD.BIN` percorrido **a partir de 216** dá **20 seções, 1.218
      vértices, 1.074 primitivas**, e a última termina em 36.064, com o
      separador fechando em **36.072 = EOF**. O 216 vem do
      `layout.geometry_start()`, **derivado** do menor alvo das listas, e não
      de um número escolhido à mão.
- [x] **Toda contagem de seção afirmada vem com o offset de onde a varredura
      começou.** Foi a metade que faltou na
      [`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md): começar em
      15.704 dá 11/690/611 fechando no EOF exato, o que parece leitura completa
      e é metade do arquivo
      ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)).
- [x] O `modelfile.py` entrega **modelo por lista**, não "as onze do
      `EDT_MOD.BIN`". Cada lista é uma peça sozinha (`84/71`) mais **cinco
      pares de contagem idêntica** — `30/24`, `80/78`, `72/59`, `40/35`,
      `63/56` na lista A; `40/34`, `88/86`, `72/59`, `40/35`, `63/56` na B —,
      identificados como tal, sem ainda dizer qual parte do corpo é qual, que
      é a Fase 2. **O critério diz de qual lista cada contagem é.**
- [x] A ordem entregue é a **da lista**, e um controle negativo que a inverta
      fica vermelho.
- [x] As contagens acima valem como asserção, não como comentário.
- [x] **O `MODEL.BIN` continua com `MODEL_GEOMETRY_START` constante**, e a task
      diz por quê. **A variante foi medida, e a descrição acima estava errada**
      — corrigida em 2026-09-14 pela execução desta task: o `0x00000000` de 736
      não fecha a lista de 672, é a **entrada 8 de um par cujo tag também é
      zero**, e a lista segue até fechar com `LIST_TERMINATOR` em 768 como
      todas. Um par `(0, 0)` é **slot vazio**, não fim; entendido isso, as seis
      listas recusadas leem, e o `MODEL.BIN` tem **18 listas** de tamanhos
      `[1, 1, 12, 12, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 12]`.
      **O motivo de a constante ficar passou a ser outro, e é medido** — e esta
      frase também foi remedida, em 2026-09-14, pela
      [`CORR-LOOKS-013`](/docs/tasks/looks/CORR-LOOKS-013.md), que achou dois
      erros nela. São **16 das 18** listas que abrem com tag `0x80`, mas elas
      miram **duas** corridas de ponteiros KSEG0 crus, não uma: **12** miram o
      offset **104** (64 ponteiros) e **4** miram o **232** (32 ponteiros).
      Nenhuma das duas é seção, e `min` sobre **todos** os alvos responde 104 —
      um início dentro da tabela de ponteiros, que é exatamente o que derivar o
      início existe para evitar. A decisão de manter a constante continua certa;
      o número que a sustentava, não.
- [x] **E as listas declaram o 1816.** As outras duas do cabeçalho têm **uma
      entrada só**, tag `0x02`, mirando **1816** e **4792** — as duas primeiras
      seções do arquivo. O critério dizia que *"1816 é fato medido que as listas
      não declaram"*, e declaram: o menor alvo de entrada com tag `0x02` é
      **1816** (144 entradas nas 16 listas distintas, 58 alvos distintos). A
      constante fica por ser barata e porque essa derivação não foi exercitada
      em nenhum segundo arquivo — não por a informação faltar.

---

## Log de Execução

**Executado em:** 2026-09-14

### Resumo do que foi feito

`tools/looks/modelfile.py` responde as **duas** perguntas que se confundiam: o
que está no arquivo (todas as seções, em ordem de arquivo, fechando no EOF) e o
que o jogo monta (as seções que uma lista nomeia, **na ordem dela**). O módulo é
desenhado para que confundi-las dê trabalho: quem quer o segundo chama
`read_models()`, e quem chama `scan()` **não escolhe o início** — ele vem do
`layout`, que é a metade que faltou na LOOKS-TASK-04.

Medido contra o disco japonês:

```
/BIN/MODEL.BIN   from 1816: 106 sections, 2461 vertices, 1767 primitives, end 64800 = EOF
/BIN/EDT_MOD.BIN from  216:  20 sections, 1218 vertices, 1074 primitives, end 36072 = EOF
/BIN/EDT_MOD.BIN: 2 models
  list 0: 11 sections, 654 vertices, 575 primitives
    pairs [(30, 24), (40, 35), (63, 56), (72, 59), (80, 78)]  alone [(84, 71)]
  list 1: 11 sections, 690 vertices, 611 primitives
    pairs [(40, 34), (40, 35), (63, 56), (72, 59), (88, 86)]  alone [(84, 71)]
  shared by both lists: [15704, 17572]
```

As duas listas têm a mesma forma — **uma peça sozinha e cinco pares** —, que é
o que sustenta "cada lista é uma figura" sem dizer qual peça é qual, que é da
Fase 2. E os totais fecham: 654 + 690 = 1.344, menos as duas seções
compartilhadas contadas duas vezes (63 + 63) = **1.218**, que é o total do
arquivo.

### O achado: a descrição da variante do `MODEL.BIN` estava errada

O critério desta task dizia que a lista de 672 *"abre com tag `0x80` e fecha
com `0x00000000` em 736, e não com o terminador"*. **A segunda metade é
falsa.** O `0x00000000` de 736 é a **entrada 8 de um par cujo tag também é
zero**, e a lista segue até fechar com `LIST_TERMINATOR` em 768, como todas as
outras:

```
+ 60  80172070 -> 14448
+ 64  00000000      <- tag zero
+ 68  00000000      <- ponteiro zero   (o par vazio)
+ 72  00000002
+ 76  80171c10 -> 13328
...
+ 96  000000ff      <- o terminador, onde sempre esteve
```

**Um par `(0, 0)` é slot vazio.** Pulando-o, as seis listas recusadas leem, e o
`MODEL.BIN` tem **18 listas**, de tamanhos
`[1, 1, 12, 12, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 12]` — as
de 10 são justamente as que têm pares vazios. O ponteiro zero é **pulado e não
guardado**: guardá-lo poria o offset 0 — o cabeçalho — numa lista de inícios de
seção.

### E o motivo de o `MODEL.BIN` manter constante mudou de natureza

Antes era *"o parser não lê as listas dele"*. Agora lê, e a constante fica por
um motivo **medido**: 16 das 18 listas abrem com uma entrada de tag `0x80`
mirando o offset **104**, e 104 **não é seção**:

```
secao em 104?  nao -> claims 2148999984 vertices and 2149000600 primitives
words em 104:  80172330 80172598 80172800 80172b30 ... -> 15152 15768 16384 17200 ...
```

É uma **corrida de ponteiros KSEG0 crus**, sem tag e sem terminador — uma
terceira forma de tabela neste arquivo. `min(alvos)` responderia 104, e o
`geometry_start()` entregaria a uma varredura um início **dentro da tabela de
ponteiros**: exatamente a falha que derivar o início existe para impedir. Daí o
`layout.is_derivable()`, que recusa o arquivo, e o `MODEL_GEOMETRY_START`, que
guarda o 1816 porque ele é fato medido e não algo que as listas declarem.

**O que essa corrida agrupa ninguém mediu**, e é onde a hipótese do `we3d` — 14
jogadores de 11 peças — se confere. A linha está escrita **na**
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), que é quem
escolhe a origem do boneco, e não só aqui no Log.

> **Dois números destes três parágrafos foram remedidos em 2026-09-14 pela
> [`CORR-LOOKS-013`](/docs/tasks/looks/CORR-LOOKS-013.md)**, e ficam aqui como
> registro do que esta corrida concluiu. São **duas** corridas de ponteiros, não
> uma: das 16 listas que abrem com tag `0x80`, **12** miram o 104 (64 ponteiros)
> e **4** miram o **232** (32 ponteiros). E as listas **declaram** o 1816: as
> duas restantes têm uma entrada só, tag `0x02`, mirando 1816 e 4792, que são
> seções. A conclusão — constante em vez de `geometry_start()` — continua
> valendo, porque `min` sobre **todos** os alvos ainda responde 104.

### Um defeito latente que só o sintético pegou

O `is_derivable()` nasceu lendo **a palavra em que o ponteiro de cabeçalho
cai**. Isso é o tag da primeira entrada no `MODEL.BIN`, cujas listas abrem
direto em pares — e é a **contagem** no `EDT_MOD.BIN`, cujas listas trazem um
preâmbulo `[contagem][pad]`. Ou seja: respondia certo nos dois arquivos reais
**lendo duas coisas diferentes**, e um arquivo com preâmbulo *e* entrada
marcada passava batido. Foi o que o caso vermelho 3 do `self_check()`
sintético mostrou, com o arquivo construído justamente assim.

O conserto foi ler as **entradas**: o `read_pointer_entries()` devolve
`(tag, offset)`, o `read_pointer_list()` virou um invólucro fino dele, e o
`is_derivable()` percorre os tags. Guarda que acerta por coincidência é guarda
que ainda não foi testada.

### O controle negativo da ordem

Inverter a lista tem de ficar vermelho — e a asserção é sobre a **sequência**,
porque o conjunto não muda: `sorted(forward) == sorted(backward)`, e os totais
de vértice e primitiva são idênticos. O que muda é o `shape`. O `--check-image`
faz o equivalente contra o disco real, exigindo que **nenhuma** das duas listas
esteja em ordem de arquivo — sem isso, a distinção que o módulo inteiro existe
para manter ficaria sem teste.

### Arquivos criados/modificados

- `tools/looks/modelfile.py` — **novo**. `Model` (com `shape` e `pairs()`),
  `scan()`, `read_models()`, `verify()`, `_build_file()`, `self_check()` com
  três casos vermelhos e o `--check-image` vivo
- `tools/looks/layout.py` — o par `(0, 0)` como slot vazio;
  `read_pointer_entries()` e o `read_pointer_list()` como invólucro;
  `is_derivable()` lendo tags; `SUBLIST_TAG`, `GEOMETRY_START` e
  `GEOMETRY_EXPECTED`; o `geometry_start()` recusando arquivo não-derivável
- `docs/PLAN-LOOKS-PY.md` — §1.5 ganhou *"O cabeçalho do `MODEL.BIN`: 18
  listas, o slot vazio, e uma terceira forma"*
- `docs/tasks/looks/08-de-onde-vem-o-boneco.md` — a corrida de ponteiros de 104
  como terceira candidata
- `docs/tasks/looks/progresso.md` — tabela e checklist da Fase 1
- `docs/tasks/looks/05-arquivos-de-modelo.md` — este arquivo, com o critério da
  variante corrigido

### Problemas encontrados

Nenhum bloqueou. Dois registros:

- O critério desta task descrevia a variante do `MODEL.BIN` errado, e a
  correção está no próprio critério, com a data — divergência entre doc e
  ferramenta é achado.
- **`tools/pes2/selftest.py` continua sem rodar nesta máquina** (lê
  `/proc/self/fd`), como as tasks 03 e 04 registraram. Nada aqui tocou aquele
  projeto.
