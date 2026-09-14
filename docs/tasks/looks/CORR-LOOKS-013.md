---
id: CORR-LOOKS-013
title: "Correção: o cabeçalho do `MODEL.BIN` foi descrito por metade — são duas corridas de ponteiros, e a primeira lista declara o 1816"
type: correção
category: engenharia-reversa
status: concluído
depends_on: []
---

# CORR-LOOKS-013: o cabeçalho do `MODEL.BIN` foi descrito por metade

## Problema identificado

A task fecha justificando por que o `MODEL.BIN` mantém
`MODEL_GEOMETRY_START` como constante em vez de derivar o início como o
`EDT_MOD.BIN` faz. **A decisão está certa** — `min(alvos)` sobre as listas do
`MODEL.BIN` responde 104, que não é seção. O que está errado é a **evidência**,
em dois pontos, e os dois estão escritos tanto no critério da task quanto no
docstring do `layout.geometry_start()`:

**1. "16 das 18 listas abrem com uma entrada de tag `0x80` mirando o offset
104."** São 16 que abrem com tag `0x80`, sim — mas só **12** miram o 104. As
outras **4** miram o **232**, que é uma **segunda** corrida de ponteiros crus,
de 32 ponteiros contra os 64 do 104. O docstring do `layout.py` diz coisa ainda
mais forte e ainda menos verdadeira: *"**Every one** of those lists opens with
an entry tagged 0x80 aiming at offset 104"* — duas listas abrem com tag `0x02`.

**2. "`MODEL_GEOMETRY_START` stays a constant because 1816 is a measured fact
the lists do not state."** As listas **declaram** o 1816. A primeira lista do
cabeçalho, em 72, tem **uma entrada só**, tag `0x02`, mirando exatamente
**1816** — que é o valor da constante. A segunda, em 88, tem uma entrada só
mirando **4792**, que é a segunda seção do arquivo. As duas são seções de
verdade.

Por que isso importa, além da precisão:

- **A segunda corrida de ponteiros não está registrada em lugar nenhum.** O
  Log e a §1.5 falam de "uma terceira forma de tabela" no singular, em 104. São
  duas, com tamanhos diferentes, e alvos diferentes. A
  [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) recebeu a
  linha de que a corrida de 104 é onde a hipótese do `we3d` — 14 jogadores de 11
  peças — se confere; ela vai procurar **uma** tabela e encontrar duas, e a
  segunda pode ser justamente o que distingue os agrupamentos.
- **"As listas não declaram o 1816" fechou uma porta que está aberta.** Existe
  derivação possível e ela é de uma linha: o menor alvo de entrada com tag
  `0x02` — as entradas que apontam seção — é **1816**, medido. A constante pode
  continuar (é barata e é fato), mas o motivo escrito hoje é falso, e um motivo
  falso é o que impede alguém de reabrir a questão com dado na mão.

## Evidência

Medido nesta revisão sobre `roms/japanese-shift-jis.bin`, com o
`layout.read_pointer_entries()` da própria task e com um parser independente,
que concordam:

```
header pointers: 18   distinct lists: 16
open with tag 0x80        : 16 of 18
open with (0x80 -> 104)   : 12 of 18
name 104 anywhere         : 12
```

As dezoito, com a primeira entrada de cada:

```
  list@72    n=1   first=(0x02 -> 1816)      <- declara a constante
  list@88    n=1   first=(0x02 -> 4792)
  list@360   n=12  first=(0x80 -> 104)
  list@360   n=12  first=(0x80 -> 104)
  list@568   n=12  first=(0x80 -> 104)
  list@672   n=10  first=(0x80 -> 104)
  list@776   n=12  first=(0x80 -> 104)
  list@880   n=10  first=(0x80 -> 232)       <- a segunda corrida
  list@1400  n=12  first=(0x80 -> 104)
  list@1504  n=10  first=(0x80 -> 232)
  list@984   n=12  first=(0x80 -> 104)
  list@1088  n=10  first=(0x80 -> 104)
  list@1192  n=12  first=(0x80 -> 104)
  list@1296  n=10  first=(0x80 -> 232)
  list@1608  n=12  first=(0x80 -> 104)
  list@1712  n=10  first=(0x80 -> 232)
  list@464   n=12  first=(0x80 -> 104)
  list@464   n=12  first=(0x80 -> 104)
```

As duas corridas, e o que há em cada:

```
  104: nao e secao; corrida de 64 ponteiros KSEG0 crus
       80172330 80172598 80172800 80172b30 -> 15152 15768 16384 17200
  232: nao e secao; corrida de 32 ponteiros KSEG0 crus
       8017aac0 8017aac0 8017ac40 8017ac40 -> 49856 49856 50240 50240
```

Os alvos das duas listas de uma entrada **são** seções:

```
 1816: SECTION 107 vert 88 prim, ends 4792
 4792: SECTION  50 vert 48 prim, ends 6352
```

E a derivação que o texto dá como impossível:

```
min target with tag 0x02: 1816   (144 entradas, 58 alvos distintos)
min de todos os alvos   : 104     <- por isso a decisao de nao usar min() esta certa
```

O que **não** mudou: as 18 listas, os tamanhos
`[1, 1, 12, 12, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10, 12, 12]`, o par
`(0, 0)` como slot vazio no 736/740 (e outro no 760/764) com o
`LIST_TERMINATOR` em 768 — tudo isso reproduz exatamente, e o achado central da
task, o slot vazio, está certo.

## Causa raiz

A primeira entrada de algumas listas foi tomada pela de todas, e o "1816 não é
declarado" veio de olhar as listas de doze e de dez sem olhar as duas de uma.

## Correção

### Arquivo: `tools/looks/layout.py`, docstring de `geometry_start()`

Trocar a frase de "every one of those lists … aiming at offset 104" pelo que se
mede: 16 das 18 abrem com tag `0x80`, **12** mirando 104 e **4** mirando 232;
as duas restantes são listas de uma entrada com tag `0x02`, que nomeiam seção.
A conclusão fica igual e passa a se apoiar no número certo: `min` sobre
**todos** os alvos dá 104, que não é seção, e por isso o `MODEL.BIN` não usa
`geometry_start()`.

E trocar "1816 is a measured fact the lists do not state" por: a primeira lista
declara 1816; a constante fica porque é barata e porque a derivação por tag
`0x02` ainda não foi exercitada em nenhum outro arquivo — não porque a
informação não esteja lá.

### Arquivo: `docs/tasks/looks/05-arquivos-de-modelo.md`

O último item do critério repete os dois erros; corrigir no lugar, com a data,
como o próprio critério já fez uma vez nesta task.

### Arquivo: `docs/PLAN-LOOKS-PY.md` §1.5

A seção *"O cabeçalho do `MODEL.BIN`: 18 listas, o slot vazio, e uma terceira
forma"* passa a registrar **duas** corridas — 104 com 64 ponteiros, 232 com 32
— e as duas listas de uma entrada que nomeiam seção.

### Arquivo: `docs/tasks/looks/08-de-onde-vem-o-boneco.md`

A linha encaminhada fala de uma corrida; passa a falar de duas, com os dois
tamanhos. Quem for conferir a hipótese dos 14 jogadores precisa saber que há
dois agrupamentos candidatos, não um.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |
| `docs/tasks/looks/05-arquivos-de-modelo.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/08-de-onde-vem-o-boneco.md` | modificar |

## Verificação

- [x] nenhum texto afirma que todas — ou 16 — as listas miram 104
- [x] as duas corridas (104, 64 ponteiros; 232, 32 ponteiros) estão registradas
- [x] está escrito que a lista de 72 declara 1816, e a de 88 declara 4792
- [x] `python tools/looks/layout.py --check`, `section.py --check`,
      `modelfile.py --check` e `layout.py --sweep` verdes
- [x] `python tools/looks/modelfile.py --check-image roms/japanese-shift-jis.bin`
      continua dando as mesmas contagens
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

A decisão ficou (constante em vez de `geometry_start()`, porque `min` sobre
**todos** os alvos ainda responde 104, que não é seção); o que mudou foi a
evidência, nos quatro lugares onde ela estava escrita.

**Erro 1 — uma corrida virou duas.** São 16 das 18 listas abrindo com tag
`0x80`, mas elas miram **duas** corridas de ponteiros KSEG0 crus:

```
open with tag 0x80        : 16 of 18
open with (0x80 -> 104)   : 12 of 18      corrida de 64 ponteiros
open with (0x80 -> 232)   :  4 of 18      corrida de 32 ponteiros

words em 104: 80172330 80172598 80172800 80172b30 -> 15152 15768 16384 17200
words em 232: 8017aac0 8017aac0 8017ac40 8017ac40 -> 49856 49856 50240 50240
```

O docstring do `geometry_start()` dizia *"**every one** of those lists opens
with an entry tagged 0x80 aiming at offset 104"* — duas coisas erradas na mesma
frase, já que duas listas abrem com tag `0x02`.

**Erro 2 — "as listas não declaram o 1816".** Declaram. As duas listas de uma
entrada nomeiam seção:

```
  list@72  n=1  first=(0x02 -> 1816)     1816: SECTION 107 vert  88 prim, ends 4792
  list@88  n=1  first=(0x02 -> 4792)     4792: SECTION  50 vert  48 prim, ends 6352

min target with tag 0x02: 1816
min de todos os alvos   : 104
```

A constante continua, com o motivo certo: é barata, e a derivação por tag
`0x02` não foi exercitada em nenhum segundo arquivo. Motivo falso é o que
impede alguém de reabrir a questão com dado na mão.

Corrigidos: o docstring do `layout.geometry_start()`, o critério da
[`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) (mais um item
novo sobre o 1816), a §1.5 do plano — que ganhou título novo, *"18 listas, o
slot vazio, e **duas** corridas"* — e a linha encaminhada à
[`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), que agora
manda procurar **duas** tabelas e registra que as duas listas de uma entrada
nomeiam seção.

Gates: `layout --check`, `section --check`, `modelfile --check` verdes;
`--sweep` → `no address outside layout.py (4 file(s), 1358 line(s) swept)`; e o
`--check-image` com as mesmas contagens de antes.

**Problemas encontrados:**

**1. O "144 entradas" da CORR é a contagem sobre as 16 listas distintas.** Sobre
os **18** ponteiros do cabeçalho são **166** — duas listas (360 e 464) são
apontadas duas vezes. O `min` e os 58 alvos distintos são os mesmos nas duas
leituras, então o número da CORR está certo; faltava dizer sobre qual conjunto.
Ficou escrito como "144 entradas nas 16 listas distintas".

**2. Um achado de graça, dentro da corrida de 232:** os alvos vêm **em pares
repetidos** (`49856 49856 50240 50240 …`), o que a de 104 não faz. Registrado
na LOOKS-TASK-08, que é quem vai medir o que elas agrupam.

**3. O Log da LOOKS-TASK-05 repete os dois erros em prosa**, e fica como está,
com uma nota de bloco ao lado dando os números certos — é registro do que
aquela execução concluiu, e a conclusão dela (a constante) continua valendo.

**Arquivos criados/modificados:**

- `tools/looks/layout.py` — o docstring de `geometry_start()`
- `docs/tasks/looks/05-arquivos-de-modelo.md` — o critério, mais a nota ao lado
  do Log
- `docs/PLAN-LOOKS-PY.md` — a §1.5, subseção do cabeçalho do `MODEL.BIN`
- `docs/tasks/looks/08-de-onde-vem-o-boneco.md` — as duas corridas
- `docs/tasks/looks/CORR-LOOKS-013.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
