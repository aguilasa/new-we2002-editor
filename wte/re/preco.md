# `re/preco.md` — a fórmula de preço

Produto da [WTE-TASK-32](../../docs/tasks/32-preco-do-jogador.md). A feature que
motivou o projeto, e a única das quatro que é **aritmética** em vez de formato.

## O que se recuperou

```text
s := soma das dezesseis barras de habilidade
preço := s⁴ div 3000000
       + s³ div   40000
       + s²   div     700
       + s    div       7
       + 5
se posição = 0 (goleiro):  preço := preço * 5 div 3
```

As quatro constantes são `0x2DC6C0`, `0x9C40`, `0x2BC` e `7`, e aparecem **duas
vezes** no `.exe` — uma por handler.

## As duas fontes concordam, e é isso que dá confiança

| Fonte | O que ela diz |
|---|---|
| disassembly, `0x004110e7`..`0x0041112a` (`base_teamClick`) | as quatro divisões, o `+ 5`, e o `× 5 div 3` em `0x00411142` |
| disassembly, `0x00408c3b`..`0x00408c83` (`etiqprecioClick`) | **as mesmas** quatro divisões e o mesmo `+ 5`, com o `× 5 div 3` em `0x00408c95` |
| tabela de verdade, 132 jogadores | 100% de acerto — ver abaixo |

Os dois handlers foram lidos instrução a instrução e são a mesma fórmula
compilada duas vezes. Isso não era garantido: o preço de **um** jogador e o
preço do **time** podiam divergir, e o enunciado da task alertava para isso
(*"pode haver desconto, teto, ou tratamento diferente do goleiro"*). Não há.

## De onde vem a soma — e por que as duas metades diferem

**`etiqprecioClick` soma o que está na TELA.** Ele faz
`FindComponent('barrhab' + N)` para N de 1 a 16 e acumula o campo `+0x20c` de
cada um, que num `TScrollBar` é a `Position`. Quem põe valor lá é a rotina de
encher a ficha, como `max(atributo − 12, 0)`.

**Consequência que vale saber:** mexer numa barrinha e clicar no rótulo dá o
preço do valor **mexido**, mesmo sem gravar nada. O port faz igual, lendo as
mesmas `Position` — ler o `TPlayer` daria o preço do disco e seria outra coisa.

**`base_teamClick` soma a partir da MEMÓRIA**, porque não há tela por jogador:
dezesseis chamadas a `0x00403278` sobre uma tabela de 16 registros de 12 bytes
em `0x00423648`, com os atributos crus em `0x0043364e`/`0x0043364f`.

**O port não porta a `0x00403278`.** Ela é o decodificador de atributo do
original, e este port tem o dele — transpilado do `we2002_core` e conferido
contra as duas ROMs desde a fase 3. Portá-la seria ter dois decodificadores e
duas verdades. A `SomaDasHabilidades` do
[`we2002_preco`](../src/we2002_preco.pas) calcula do `TPlayer` decodificado, e
a tabela de verdade abaixo prova que o número é o mesmo.

## Três coisas que a leitura ingênua erraria

### 1. O `s⁴` é de 32 bits, e transborda

O original faz `imul` de 32×32 — que produz 64 bits em `edx:eax` — e **logo em
seguida um `cdq`**, que reescreve `edx` com o sinal de `eax`. A metade alta é
jogada fora antes da divisão.

Em Pascal isso é `LongInt` **deliberado**, não `Int64`. Medido no
[`test_preco.pas`](../tests/test_preco.pas): a primeira soma em que as duas
versões divergem é **216** (215⁴ = 2.136.750.625 cabe em 31 bits; 216⁴ não), e a
partir dali o preço de 32 bits **cai** enquanto o de 64 bits sobe.

Jogador real não chega lá — a amostra medida vai de soma 36 a 77 —, mas nada no
formato impede uma soma de 216, e reproduzir o transbordo é reproduzir o
original.

### 2. A divisão trunca para zero, não para baixo

`idiv` do x86 e o `div` do Object Pascal fazem o mesmo; `Floor` faria outra
coisa em negativo. Soma negativa não acontece — a `Position` não é negativa —,
mas **o transbordo do item 1 produz valor negativo**, e aí a diferença aparece.

### 3. O `× 5 div 3` é do goleiro, e a condição mora em lugares diferentes

No `etiqprecioClick` é `flechasapa1.Position = 0` (`0x00408c90`), e o
`flechasapa1` é a seta de **posição**. No `base_teamClick` é a mesma pergunta
feita à memória. Posição 0 é goleiro.

**A ordem importa:** o fator vem *depois* do `+ 5`, sobre o preço inteiro.
Testado — `13 × 5 div 3 = 21`, e não `13 + 5` nem `(13 div 3) × 5`.

### E um quarto: o fator de exibição

O que aparece no `casilla_precio` é o preço **vezes 10.000**
(`imul` de 64 bits por `0x2710`, `0x00408cb3`). O byte gravado na imagem é o
preço **sem** o fator. Confundir os dois poria 210000 num byte.

## A tabela de verdade

O método é o que a task pede, com uma troca que a torna mais forte: em vez de
ler o preço de **um** jogador na tela, deixa-se o `base_teamClick` do oráculo
**gravar** o preço de 22 jogadores na imagem, e leem-se os bytes.

Cada time é uma corrida do oráculo. O
[`dump_preco`](../tests/dump_preco.pas) imprime, por jogador, o preço que o
port prevê **e** o byte que ficou na imagem; o
[`check_preco.py`](../tools/check_preco.py) compara as colunas e guarda o
resultado em [`preco.tsv`](preco.tsv).

**132 jogadores, 6 times da ROM japonesa, 100% de acerto.** Somas de 36 a 77,
12 goleiros entre eles.

### A ROM europeia não hospeda este oráculo

A corrida sobre ela gravou **zero** bytes — o `wte.exe` morre na troca de time
com aquela imagem, medido na
[CORR-WTE-044](../../docs/tasks/CORR-WTE-044.md). As linhas dela estão no TSV
**sem** `medido`, e o coletor diz isso em voz alta.

**Isso já enganou uma vez, e a guarda nasceu daí.** A primeira versão do coletor
creditou ao oráculo os preços **de fábrica** daquela imagem e acusou 21
divergências que não existiam. Hoje ele exige prova de que o oráculo escreveu:
compara a faixa de preço do time contra a ROM virgem antes de marcar qualquer
linha como medida.

## O achado que ninguém procurava: o original preça 22 slots, não 23

O laço do `base_teamClick` vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em
`0x00411178`), mas cada volta começa com

```text
call 0x4046e8                        ' carrega_jogador(time, slot, buffer 2)
cmp  DWORD PTR ds:0x43366c,0x0       ' a terceira coluna do buffer
je   0x411175                        ' pula o slot
```

e **para o slot 22 a coluna sai zero**. Medido em seis times: os bytes gravados
vão de `CONDICIONAL_BASE + 23·t` até `+ 21`, e o do slot 22 fica com o valor de
fábrica em todos.

**O conteúdo do jogador não explica.** No time 9 o slot 21 e o slot 22 têm a
mesma soma (36) e a mesma posição (0), e só o 21 é gravado.

**A causa está aberta**, e é a [CORR-WTE-095](../../docs/tasks/CORR-WTE-095.md).
Duas medições dela, de 2026-08-24, estreitaram o que ainda falta:

**1. O salto é real, e não byte que já estava certo.** Plantados `0xFF` nos
slots 20, 21 e 22 do time 2 e rodado o oráculo pelo
[`golden-22-precos`](../tests/roteiros/golden-22-precos.txt): os slots 20 e 21
voltaram com **26** e **21**, que são exatamente o `previsto` do
[`preco.tsv`](preco.tsv), e o slot 22 continuou **255**. A alternativa barata —
"o oráculo grava e o byte não muda porque já valia o preço" — está descartada.

**2. A conta de offset do oráculo não tem caso especial de slot.** Lida
inteira, a `0x00404374` decide por **time**, nunca por slot: `cmp ecx,0x3f`
separa seleção de clube de ML, e `cmp ecx,0x35` / `cmp ecx,0x38` zeram a
terceira coluna só para os times **54 e 55** — os mesmos 46 jogadores que o
`Database.cpp:756-764` pula. Para todo time de seleção fora desses dois, ela
escreve `0x2ece0c + 23·time + 2·(time div 56) + slot` em `[esi+ecx*4+0x28]`, que
é o `0x43366c` que o laço testa, **sem nenhum ramo dependente do slot**.

Isso fecha o ramo grande da correção: **a conta de offset deste port não está
errada para o slot 22** — ela é a mesma do oráculo, e o oráculo a calcula igual
para os 23. O que sobra em aberto é uma contradição estreita e nomeada: o laço
observa zero num campo que a rotina que acabou de rodar sempre preenche com
valor não nulo.

O port reproduz o que o **oráculo** faz, porque é contra ele que o gate mede — e
a divergência fica escrita em vez de silenciosa. O `check_preco.py` recusa
qualquer linha de slot 22 marcada como medida: se a regra cair, o
`ULTIMO_SLOT_PRECADO` do handler está errado e o `--check` diz isso.
