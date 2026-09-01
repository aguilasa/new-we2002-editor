# `re/preco.md` — a fórmula de preço

Produto da [WTE-TASK-32](../../docs/tasks/concluidos/32-preco-do-jogador.md). A feature que
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
[CORR-WTE-044](../../docs/tasks/concluidos/CORR-WTE-044.md). As linhas dela estão no TSV
**sem** `medido`, e o coletor diz isso em voz alta.

**Isso já enganou uma vez, e a guarda nasceu daí.** A primeira versão do coletor
creditou ao oráculo os preços **de fábrica** daquela imagem e acusou 21
divergências que não existiam. Hoje ele exige prova de que o oráculo escreveu:
compara a faixa de preço do time contra a ROM virgem antes de marcar qualquer
linha como medida.

## O achado que ninguém procurava: o original preça 22 slots, não 23

O laço do `base_teamClick` vai de 0 a 22 (`cmp DWORD PTR [ebp-0x2c],0x17` em
`0x00411178`), e cada volta começa com

```text
call 0x4046e8                        ' carrega_jogador(time, slot, buffer 2)
cmp  DWORD PTR ds:0x43366c,0x0       ' a terceira coluna do buffer
je   0x411175                        ' pula o slot
```

Medido em seis times: os bytes gravados vão de `CONDICIONAL_BASE + 23·t` até
`+ 21`, e o do slot 22 fica com o valor de fábrica em todos.

**O conteúdo do jogador não explica.** No time 9 o slot 21 e o slot 22 têm a
mesma soma (36) e a mesma posição (0), e só o 21 é gravado.

### O `je` não é a causa, e essa linha já foi escrita errada

Este documento afirmou, até 2026-08-24, que *"para o slot 22 a coluna sai
zero"*. **Está medido que não sai.** A
[CORR-WTE-095](../../docs/tasks/concluidos/CORR-WTE-095.md) instrumentou a corrida com o
[`diff_dirigido.sh`](../tools/diff_dirigido.sh) — `strace` sobre o oráculo, que
é a régua que enxerga **leitura**, coisa que `cmp` nenhum alcança:

```text
seeks SEEK_SET por offset, faixa 3067450..3067472 (os 23 slots do time 2)
  3067450  3  |  3067458  3  |  3067466  3
  ...         |  ...         |  3067471  3
  3067472  3     <- o slot 22, o MESMO numero de seeks dos outros 22
```

E a `0x004046e8` só lê o byte condicional **na rota de coluna não nula**: o
`cmp DWORD PTR [esi*4+0x433614],0x0` de `0x00404748` desvia para `0x0040477e`
quando ela é zero, e ali não há I/O nenhum — o que ele faz é pôr `0x32` no
buffer. Uma leitura em 3067472 prova, portanto, que **a coluna do slot 22 não é
zero**.

### Onde o byte se perde: abaixo do `fputc`, e está medido

No lado da **escrita**. Slot 21 e slot 22, lado a lado, na mesma corrida:

```text
slot 21                              slot 22
  _llseek 3067471 SET                  _llseek 3067472 SET
  read 512                             read 512
  _llseek 0 CUR -> 3067983             _llseek 0 CUR -> 3067984
  _llseek 3067983 SET                  _llseek 3067984 SET
  _llseek 3067471 SET                  _llseek 3067472 SET
  _llseek 0 CUR -> 3067471             _llseek 0 CUR -> 3067472
  _llseek 3067471 SET                  _llseek 3067472 SET
  write "\25" 1                       (nada)
```

Idênticas até o `fseek` da escrita, inclusive. Contadas as syscalls do laço
inteiro: **22** `write` de 1 byte para 23 voltas.

E o depurador fecha a conta. `winedbg` anexado ao PID Wine, dois breakpoints:

| Endereço | O que é | Paradas |
|---|---|---|
| `0x00411170` | o `call 0x403400` do laço | **23** |
| `0x0040342a` | o `fputc` dentro da `0x403400` | **23** |

Os 23 `fputc` **têm sucesso** — o retorno é o caractere gravado, não `EOF` —, e
o da 23ª volta é **20**, exatamente o `previsto` do [`preco.tsv`](preco.tsv)
para o slot 22 do time 2. Os 23 retornos batem, um a um, com a coluna
`previsto` daquele time.

**Ou seja: o preço do 23º jogador é calculado certo, aceito pelo runtime C e
jogado fora.** A perda é na saída bufferizada da Borland, abaixo do `fputc` —
código do runtime, não do editor. E não é pendência descarregável: o roteiro faz
descarga depois do clique (troca de time, com I/O de sobra) e o byte continua
não chegando.

A `0x00403388`, chamada depois de cada byte, não tem parte nisso: é o caminhador
de setor MODE2/2352, `ftell % 2352 == 2072` → `fseek(+304)`, que pula os 280 de
EDC/ECC mais os 24 do cabeçalho seguinte.

### O que está fechado, e o que fica fora de alcance

**Fechado — a conta de offset do port não está errada.** A `0x00404374` decide
por **time**, nunca por slot: `cmp ecx,0x3f` separa seleção de clube de ML, e
`cmp ecx,0x35` / `cmp ecx,0x38` zeram a terceira coluna só para os times **54 e
55** — os mesmos 46 jogadores que o `Database.cpp:756-764` pula. Para todo time
de seleção fora desses dois ela escreve
`0x2ece0c + 23·time + 2·(time div 56) + slot`, linear no slot, para os 23.

**Fechado — o slot 22 é endereçável, e o próprio editor o grava por outro
caminho.** A evidência já estava versionada e ninguém tinha cruzado: o
[`io-medido.tsv`](io-medido.tsv), sessão `27-mcr2iso`, traz
`W 3067473 3067495 23` — o import de `.mcr` escreve os **23** bytes
condicionais do time 3, slot 22 incluído. Não é propriedade do formato nem do
time; é deste handler.

**Fechado — é bug do original, e o port reproduz.** Não é propriedade do
formato, não é do time, não é do slot, e não é do port: é o editor do Obocaman
perdendo o último byte do laço na saída bufferizada. Está registrado como
divergência deliberada na
[WTE-TASK-35](../../docs/tasks/concluidos/35-divergencias-deliberadas.md), com as três
réguas que o sustentam.

**Fora de alcance, e por decisão:** *por que* o runtime da Borland larga
exatamente o último byte. Isso é interno ao CRT, não ao aplicativo — e este
projeto faz engenharia reversa do aplicativo. O comportamento observável está
medido, reproduzido e gateado; a víscera do runtime não muda nenhuma decisão do
port.

O port reproduz o que o **oráculo** faz, porque é contra ele que o gate mede — e
a divergência fica escrita em vez de silenciosa. O `check_preco.py` recusa
qualquer linha de slot 22 marcada como medida: se a regra cair, o
`ULTIMO_SLOT_PRECADO` do handler está errado e o `--check` diz isso.
