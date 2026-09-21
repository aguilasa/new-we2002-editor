---
id: CORR-LOOKS-010
title: "Correção: o `EDT_MOD.BIN` tem 20 seções e duas listas de onze — a varredura começou a 15.704 e chamou o resto de EOF exato"
type: correção
category: engenharia-reversa
status: done
depends_on: []
origin: LOOKS-TASK-04
severity: high
done_on: 2026-09-14
done_commit: 727e00d
---

# CORR-LOOKS-010: o `EDT_MOD.BIN` tem 20 seções e duas listas de onze

## Problema identificado

O Log da task afirma, como resultado da varredura nova:

```
/BIN/EDT_MOD.BIN    11 secoes   690 vert   611 prim  grupos=[1]*11  termina em 36072 (EOF=36072) EXATO
```

Os números estão certos **para a varredura que foi feita** — e essa varredura
**começa no offset 15.704**, a 43% do arquivo. O Log não diz isso em lugar
nenhum, e "termina em 36.072 EXATO" lido sem o ponto de partida sugere que o
arquivo inteiro foi lido. Não foi: os 15.704 bytes anteriores nunca passaram
pelo `scan()`.

E eles **são seções**. Varrendo do offset 216 — que é o primeiro alvo da
**segunda lista de ponteiros**, aquela que a primeira palavra do cabeçalho do
próprio arquivo aponta (`0x8011C070` → 112) — o `section.py` desta mesma task
acha **20 seções, 1.218 vértices, 1.074 primitivas**, contíguas, pela regra da
corrida de zeros, terminando no mesmo EOF.

O arquivo tem **duas listas de onze registros, de forma idêntica**, e elas
compartilham duas peças:

| lista | onde | os onze alvos |
|---|---|---|
| A | offset 112 (`header[0]`) | 216, 2.608, 4.272, 3.440, 6.800, 9.328, 13.352, **15.704**, 11.340, 14.528, **17.572** |
| B | offset 8 (`header[1]`) | 19.440, 21.832, 24.136, 22.984, 26.920, 29.704, 33.720, **15.704**, 31.712, 34.896, **17.572** |

A união das duas é exatamente as 20 seções da varredura. **A task mediu a lista
B e escreveu o resultado como se fosse o arquivo.**

Três consequências, em ordem de custo:

1. **A §1.5 do plano diz que aquela região é textura, e ela é geometria.** O
   texto afirma *"Entre o offset 216 e o 15.704 há outra região, com nove alvos
   de ponteiro … e um cabeçalho TIM em 3.228. É material de textura, e é a
   §6(a)."* Os nove alvos são as nove seções que faltavam, e o "cabeçalho TIM"
   cai **dentro** da seção que vai de 2.608 a 3.432. A task tinha na mão a
   ferramenta que decide isso e não a apontou para lá — enquanto reescrevia a
   §1.4 e a §1.5 no lugar.
2. **A mesma §1.5 diz *"há dados não-geometria entre as seções"*.** Do 216 ao
   EOF não há: é seção, corrida de zeros, seção. O que não é geometria são os
   216 bytes iniciais, que são as duas listas.
3. **A [`LOOKS-TASK-05`](/docs/tasks/looks/05-arquivos-de-modelo.md) congela o
   número.** O critério dela manda o `EDT_MOD.BIN` dar *"11 seções, 690
   vértices, 611 primitivas"* **como asserção**. Executada assim, o gate
   `looks_image` passa a exigir para sempre a leitura parcial, e a segunda
   lista deixa de ser encontrável por um teste. E a
   [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) — a incógnita
   (a), de onde vem o boneco — vai escolher entre `EDT_MOD.BIN` e os TMDs de
   `0x00168xxx` sem saber que o `EDT_MOD.BIN` oferece **dois** bonecos.

O que **não** está errado: as onze peças da lista B são mesmo as que a §1.5
descreve — cinco pares de contagem idêntica mais a peça sozinha `84/71`. A task
não varreu as onze erradas; ela varreu onze de vinte e chamou o arquivo de
lido.

## Evidência

Medido nesta revisão, com o `section.py` e o `iso_source.py` da própria task,
sobre `roms/japanese-shift-jis.bin`:

```
scan(edt, 15704) ->  11 sec   690 vert   611 prim  groups=[1]*11  end=36072   (o que o Log diz)
scan(edt,   216) ->  20 sec  1218 vert  1074 prim  groups=[1]*20  end=36072
```

As vinte, com offset e contagem:

```
   216  84/71     2608  30/24     3440  30/24     4272  80/78     6800  80/78
  9328  72/59    11340  72/59    13352  40/35    14528  40/35
 15704  63/56    17572  63/56    19440  84/71    21832  40/34    22984  40/34
 24136  88/86    26920  88/86    29704  72/59    31712  72/59    33720  40/35    34896  40/35
```

As nove primeiras somam 528 vértices e 463 primitivas — 1.218 − 690 e
1.074 − 611.

A segunda lista, byte a byte, na mesma forma da primeira (`3, 0`, onze pares
`(2, ponteiro)`, terminador `0x000000FF`):

```
 112: 0x00000003    116: 0x00000000
 120: 0x00000002    124: 0x8011C0D8 -> 216
 ...
 204: 0x801204A4 -> 17572
 208: 0x000000FF
 216: 0x00000054  0x00000047      <- 84 vertices, 71 primitivas: um cabecalho de secao
```

E o "cabeçalho TIM" de 3.228:

```
e[3228:3244] = 1000000007002700110000000300e6ff
palavra em 3228 == 0x10: True
secao que contem 3228: 2608 .. 3432   (30 vert / 24 prim)
palavras iguais a 0x00000010 no arquivo inteiro: 3
```

`0x10` é a magia de um TIM, e é também um inteiro comum. Aqui ele cai dentro do
corpo de uma seção que varre limpo.

O ponto de partida 15.704 também aparece, sem querer, no controle 24→20 que o
Log transcreve: `section at 17336` só faz sentido se a primeira seção lida foi a
de 15.704 (`15704 + 8 + 56×20 + 63×8 = 17336`). Reproduzido nesta revisão, com
o mesmo offset.

## Causa raiz

A varredura foi apontada para o offset onde as onze peças que o plano já
descrevia estavam, e o resultado — que fecha no EOF por começar perto dele —
foi lido como leitura do arquivo.

## Correção

### Arquivo: `docs/PLAN-LOOKS-PY.md` §1.5

Reescrever no lugar, com a data e o que a seção dizia antes, como manda o
perfil:

- o `EDT_MOD.BIN` tem **20 seções** e **duas** listas de onze registros, com
  `15.704` e `17.572` em ambas;
- a região 216–15.704 é **geometria**, não material de textura; o `0x10` de
  3.228 é falso positivo de magia TIM dentro de uma seção;
- a frase *"há dados não-geometria entre as seções"* sai: do 216 ao EOF é
  seção e corrida de zeros;
- **a pergunta que isso abre fica escrita**: dois modelos de onze peças, com
  duas peças em comum — dois bonecos (jogador de linha e goleiro?), duas
  qualidades do mesmo, ou um modelo e um conjunto de variações? Quem responde é
  a [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md), com o
  emulador, e o perfil já registra que **os dois save states do usuário são
  exatamente goleiro e jogador de linha** — o estímulo para decidir isso já
  está no disco.

### Arquivo: `docs/tasks/looks/05-arquivos-de-modelo.md`

O critério passa a exigir a varredura **do arquivo**, não de um pedaço:

- do offset 216 até o EOF: **20 seções, 1.218 vértices, 1.074 primitivas**,
  terminando em 36.072;
- as **duas** listas lidas, cada uma com onze registros, e o `modelfile.py`
  entregando **modelo por lista** em vez de "as onze do `EDT_MOD.BIN`";
- as cinco duplas mais o `84/71` continuam valendo — **para a lista B**, e o
  critério diz qual lista;
- toda contagem afirmada vem acompanhada do **offset de início**, que é a
  metade que faltou aqui.

### Arquivo: `docs/tasks/looks/08-de-onde-vem-o-boneco.md`

Uma linha de contexto: são dois modelos candidatos **dentro** do
`EDT_MOD.BIN`, além dos TMDs de `0x00168xxx`. A incógnita (a) ficou com três
respostas possíveis, não duas.

### Arquivo: `tools/looks/layout.py`

O offset de início do `EDT_MOD.BIN` não existe em lugar nenhum — a medição do
Log usou um número solto, o que a regra 1 não admite. Ou entra uma constante ao
lado de `MODEL_GEOMETRY_START`, ou entra a **derivação**: o menor alvo das duas
listas. A segunda é melhor, e é o método que a
[`CORR-LOOKS-008`](/docs/tasks/looks/CORR-LOOKS-008.md) já adotou para o `BASE`.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/tasks/looks/05-arquivos-de-modelo.md` | modificar |
| `docs/tasks/looks/08-de-onde-vem-o-boneco.md` | modificar |
| `tools/looks/layout.py` | modificar |

## Verificação

- [x] a §1.5 diz 20 seções e duas listas, com o que ela dizia antes e a data
- [x] nenhuma contagem de seção no plano ou nas tasks aparece sem o offset de
      onde a varredura começou
- [x] o critério da 05 pede 20/1.218/1.074 a partir de 216, e modelo por lista
- [x] o início do `EDT_MOD.BIN` é derivado ou é constante do `layout.py`, e o
      `--sweep` continua verde
- [x] `python tools/looks/section.py --check` e `layout.py --check` verdes
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

O início do `EDT_MOD.BIN` deixou de ser um número escolhido à mão e passou a ser
**derivado** — que é a parte que impede isso de acontecer de novo. Três funções
novas no `layout.py`:

- `read_pointer_list(data, offset, base)` — lê uma lista `(tag, ponteiro)`
  fechada por `0x000000FF`, com ou sem o `[contagem][pad]` na frente (se a
  segunda palavra é ponteiro, os pares já começaram), conferindo **cada alvo**
  contra o tamanho do arquivo;
- `record_lists(data)` — as listas que o cabeçalho nomeia, em ordem;
- `geometry_start(data)` — o menor alvo de qualquer lista. Para o
  `EDT_MOD.BIN` dá **216**, e a varredura a partir dele dá o arquivo inteiro.

```
geometry_start(EDT_MOD) = 216
scan a partir dele: 20 sec  1218 vert  1074 prim  end=36072 (EOF=36072)
listas: [11, 11]
```

Documentação, no lugar e com a data, como manda o perfil:

- **§1.5 reescrita.** Título novo, o bloco de ressalva dizendo o que ela afirmava
  antes e por quê (a varredura começou a 43% do arquivo e fechou no EOF exato),
  a tabela das duas listas lado a lado, as quatro leituras, e o `0x10` de 3.228
  desmontado como falso positivo de TIM dentro do corpo de uma seção.
- **§1 "Definição de pronto" e a tabela da §1.4** — 20 seções. A tabela ganhou a
  **linha antiga de propósito**, marcada, porque é ela que mostra que terminar
  no EOF não diz nada sobre o começo.
- **§8, armadilha 2** — dizia que o arquivo "não é contíguo". É: do 216 ao EOF.
  O que quebra é começar em 0 ou em 8, medido: `BadSection` com contagens na
  casa dos bilhões.
- **`05-arquivos-de-modelo.md`** — critério pede 20/1.218/1.074 a partir de 216,
  duas listas, `modelfile.py` entregando **modelo por lista**, as contagens
  ditas por lista, e a regra nova: toda contagem vem com o offset de partida.
- **`08-de-onde-vem-o-boneco.md`** — a incógnita (a) passou a ter **três**
  candidatos: lista A, lista B e os TMDs de `0x00168xxx`.

Casos vermelhos novos (9 e 10), sobre um modelo sintético na forma do
`EDT_MOD.BIN` — duas listas, uma com `[contagem][pad]` e outra sem:

| controle (nada commitado) | resultado |
|---|---|
| desligar a conferência de alvo **dentro do `read_pointer_list`** | `AssertionError: a pointer list aiming past the file was accepted`, exit 1 |
| aceitar `2` como terminador | `AssertionError: [[], []]` |

Gates: `layout --check`, `section --check`, `iso_source --check` verdes, e
`layout --sweep` → `no address outside layout.py (3 file(s), 981 line(s) swept)`.

**Problemas encontrados:**

**1. O `MODEL.BIN` não entra nessa derivação, e isso é achado novo.** O
`read_pointer_list()` **recusa** as listas dele: a de 672 abre com tag `0x80` e
fecha com `0x00000000` em 736, não com o terminador. Recusar é a resposta certa
até alguém medir a variante — afrouxar seria adivinhar formato —, então o
`MODEL_GEOMETRY_START` continua constante, o docstring diz por quê, e a
LOOKS-TASK-05 ganhou o item de medir ou registrar como aberto.

**2. O perfil do ciclo estava errado em dois lugares**, e é o arquivo pelo qual
o `/revisar` julga a fase: a verificação da Fase 1 exigia `EDT_MOD.BIN
11/690/611` — agora `20/1.218/1.074`, com o offset de partida junto —, e a
armadilha 3 dizia que o arquivo não é contíguo. Sem esse conserto a próxima
revisão cobraria o número errado.

**3. A transcrição do Log da LOOKS-TASK-04 fica como está**, com uma nota de
bloco ao lado dizendo de que offset ela saiu e qual é o número do arquivo. É
registro da corrida que a produziu.

**Arquivos criados/modificados:**

- `tools/looks/layout.py` — `BadPointerList`, `LIST_TERMINATOR`,
  `read_pointer_list()`, `record_lists()`, `geometry_start()`, casos 9 e 10
- `docs/PLAN-LOOKS-PY.md` — §1.5 reescrita, §1 (definição de pronto), a tabela
  da §1.4 e a armadilha 2 da §8
- `docs/tasks/looks/05-arquivos-de-modelo.md` — o critério
- `docs/tasks/looks/08-de-onde-vem-o-boneco.md` — os três candidatos
- `docs/tasks/looks/04-formato-de-secao.md` — a nota ao lado da transcrição
- `docs/prompts/perfil-looks.md` — Fase 1 e armadilha 3
- `docs/tasks/looks/CORR-LOOKS-010.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
