---
id: LOOKS-TASK-26
title: "`anime.py` — o formato do `ANIME.BIN`, medido contra a pose capturada"
type: implementação
category: formato
phase: 9
depends_on: ["LOOKS-TASK-25"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (l)"
status: pendente
---

# LOOKS-TASK-26: O formato do `ANIME.BIN`

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (l), e o rito da Fase 1 (§1.4).
- **Só começa se a [`LOOKS-TASK-24`](/docs/tasks/looks/24-de-onde-vem-a-pose.md) disse que a pose vem do `ANIME.BIN`.** Se disse outra
  coisa, esta task muda de arquivo e de título, e isso se registra aqui antes.
- **Ela disse que vem, em 2026-09-17, e deixou o começo do formato medido**
  (`oracle.py --pose`; §10.3 (j) do plano):
  - o arquivo está na RAM **byte a byte** em `layout.ANIME_BASE` = `0x8017EE00`,
    nos dois slots — 396.804 de 396.804;
  - **a base NÃO sai do `layout.derive_base()`**, e tentar é perder tempo: a
    regra lê "palavra com bit alto" e o payload deste arquivo abre com
    `0x9000040A`, então a corrida de ponteiros não fecha nas 204 palavras; e
    mesmo cortada ali, o ponteiro mais baixo mira o offset **912**, não o 816
    que a regra supõe. A base medida veio de **conteúdo** (uma corrida de 64
    bytes do offset 1.000 aparece uma vez só na RAM);
  - o cabeçalho é de **204 entradas**, uma por animação, e a tela toca a
    **entrada 5** — nenhuma outra é lida (watchpoint de leitura nas 204 de uma
    vez);
  - a entrada aponta uma **lista de quadros**; o estado em
    `layout.ANIME_STATE` guarda a lista (+0x18), o quadro corrente (+0x1C) e o
    índice (+0x329), que anda todo quadro e **volta a zero** quando a entrada
    ao lado marca o fim — é a passada se repetindo;
  - o quadro é lido por `0x80011E80`, `0x80011E94`, `0x80011EB0` e
    `0x80011ECC`, e o código logo antes (`0x80011D48`…) **desempacota ângulos
    de uma palavra** com `sll`/`sra` e os guarda no scratchpad (`0x1F800120`,
    `0x1F800122`, …). **Os nove números da matriz não estão no arquivo:** o
    que está são ângulos empacotados, e a matriz é calculada deles.
- **O gabarito é a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md).** Matriz de determinante 1 e boneco em pé é
  plausível, não certo.
- **Ela existe desde 2026-09-18**, em `work/looks-pose/slot<S>-frame<N>.json`,
  gravada por `oracle.py --pose <SLOT> <N> [N ...]`, e o que ela obriga:
  - **o que o jogo carrega por peça é ABSOLUTO** — a câmera já composta com a
    volta da peça (`M x Mt = C x Ct`, medido) —, então reproduzir o gabarito
    exige saber **a câmera daquele quadro**, que está no mesmo JSON (`camera`),
    e não só os ângulos do arquivo. Comparar a matriz crua do `ANIME.BIN`
    contra o JSON sem compor a câmera dá diferença em tudo e não é achado;
  - **são 12 cargas por passada, não 11**: as onze peças da figura mais uma
    raiz sem ponteiro de modelo;
  - **a comparação é exata** — meias-palavras 4.12 —, e o formato da struct do
    jogo é 9 rotações, 2 bytes de enchimento, 3 translações de 32 bits;
  - **o quadro N é contado a partir do `load_state`**, e duas capturas do mesmo
    N são idênticas número a número: é o controle do gabarito, e o leitor se
    mede contra ele no mesmo N.
- **As regras da Fase 1 valem inteiras:** endereço só no `layout.py`; contagem
  com o offset de partida; varredura que não chega ao EOF é errada; módulo novo
  com `self_check()` e caso vermelho.

---

## Objetivo

Um `tools/looks/anime.py` que lê o `ANIME.BIN` do disco japonês, diz o que cada
entrada do cabeçalho nomeia, e devolve, para a animação da tela e um quadro,
**as mesmas matrizes que o jogo carregou**.

---

## Critério de conclusão

- [x] `anime.py` com `self_check()` sem imagem, e `--check-image` que pula
      com 77 e está na lista do `cli.py check` (o self-check dele falha se não
      estiver). O `cli check` passou de 8 para **9 módulos**.
- [x] O cabeçalho lido e a estrutura varrida **até o EOF exato**, com o offset
      de partida ao lado de cada contagem: **a partir de 816, 197 blocos,
      3.952 quadros, terminando em 396.804 = EOF, 0 buraco**.
- [x] Qual entrada é a caminhada da tela, medido — não escolhido pelo tamanho:
      `layout.ANIME_SCREEN_ENTRY = 5`, do watchpoint de leitura sobre as 204
      entradas de uma vez (LOOKS-TASK-24), e não do tamanho do bloco.
- [ ] **As matrizes do quadro N da [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) reproduzidas exatamente**, nas onze
      peças e na cabeça, nos dois slots. **NÃO FEITO — é o único critério que
      falta**, e o estado está medido: os **ângulos** saem exatos, **96 de
      96**, nos dois slots; das matrizes, **32 saem exatas e 90 ficam dentro
      de uma unidade de 4.096**, que é o arredondamento do GTE; e **seis** —
      um passe só do goleiro, com ângulos certos e a mesma câmera — ficam de
      92 a 188, sem explicação.
- [x] Dois controles negativos — ordem de campo e escala —, vermelhos pela
      própria causa. São **três**: a ordem dos campos, a escala do ângulo e a
      tabela de seno truncada em vez de arredondada. 81 de 81 vermelhos.
- [x] §10.3 (l) com o formato medido, e com os dois pontos abertos escritos ao
      lado.

---

## Log de Execução

**Executado em:** 2026-09-18 — **PARCIAL** (duas sessões no mesmo dia)

**Resumo do que foi aprendido**

O formato está medido inteiro e o leitor existe: cabeçalho de 204 ponteiros
**absolutos**, payload que se divide em 197 blocos `[quadros][lista][0x0B]` e
**fecha no EOF exato sem um buraco**, quadro de doze pares — um par por peça
desenhada, na ordem em que a tela as desenha —, e três ângulos de 10 bits com
sinal por par, deslocados quatro.

**A lição da segunda sessão é sobre a ponte.** A primeira ligou captura e
arquivo pelo **quadro que o estado de animação nomeia**, e isso está certo para
o jogador de linha e **errado para o goleiro** — metade das peças não casava
com nada em 3.952 quadros, e a conclusão pronta era *"o jogo interpola metade
dos quadros"*, que chegou a ser escrita no plano e encaminhada para a
[`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md). A ponte que
vale é o **ponteiro que o jogo está lendo**: `s0` na instrução `0x80011D48`,
que anda o arquivo de oito em oito, um par por peça, nos dois slots. Com ela,
**96 de 96** peças trazem os ângulos do par, inteiro por inteiro, e a
interpolação deixa de ser um achado.

**O que falta, e é por isso que a task não está concluída:** a matriz não sai
exata — 32 de 96 saem, 90 ficam dentro de uma unidade de 4.096 (o GTE, que a
`RotMatrix` usa e este leitor não emula), e seis ficam mais longe sem
explicação.

**Arquivos criados/modificados** *(conferidos contra os dois commits)*

- `tools/looks/anime.py` — **novo**: o formato, o decode dos ângulos, a tabela
  de seno gerada, a rotação, `--check`, `--check-image`, `--report` e
  `--against-pose`
- `tools/looks/layout.py` — `ANIME_SCREEN_ENTRY`, `POSE_ANGLES`, e
  `ANIME_UNPACK` / `ANIME_UNPACK_BASE`, que é a ponte que vale
- `tools/looks/oracle.py` — a captura grava, por peça, os três ângulos do
  scratchpad, o quadro que a animação tocava e **o par que o jogo leu**, com o
  par consumido a cada peça
- `tools/looks/cli.py` e `tools/looks/selftest.py` — o módulo novo nas duas
  listas
- `tools/looks/controls.py` — três controles plantados, e o
  `cli-check-forgets-a-module` repontado para o último da lista
- `docs/PLAN-LOOKS-PY.md` — §10.3 (l) com o formato, e a correção no lugar do
  que ela dizia sobre interpolação
- `docs/tasks/looks/32-o-ciclo-da-caminhada.md` — o encaminhamento **corrigido**:
  o que foi mandado para lá de manhã era artefato, e a linha diz isso
- `docs/prompts/perfil-looks.md` — a linha de gate e as armadilhas
- `CLAUDE.md` — a linha do comando novo na tabela do ciclo
- `docs/tasks/looks/progresso.md` — a task segue `⬜ Pendente`, de propósito

**Gates, na árvore de `e5be774`**

```text
$ python tools/looks/selftest.py
  ..... 81 of 81 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/anime.py --check-image
  ok    the header names 204 animation(s), 197 of them distinct
  ok    the walk from offset 816 covers 197 block(s) and 3952 frame(s) and
        ends at 396804   EOF 396804, 0 hole(s)
  ok    every block closes with the same marker
  ok    every frame is 96 byte(s), twelve pairs of words
  ok    the entry the screen plays has a frame for each drawn piece
  ok    and its matrices are rotations
anime --check-image: 0 failure(s)

$ python tools/looks/anime.py --against-pose      # capturas de --poses, 2 slots
  96 of 96 carry the angles the file holds at the pair the game read,
      integer for integer
  0 piece(s) drew before any unpack stop, so no pair names them
  32 matrices of 96 are exact, and the worst entry is 188 apart of 4096
  open  ... six limbs of ONE pass of the goalkeeper ... everything else lands
      within one unit, which is the GTE's own rounding

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**Os controles, plantados e rodados** — cada um numa cópia da árvore:

```text
  RED    anime-angle-fields-in-the-wrong-order  anime.py :: angles
  RED    anime-angle-loses-its-scale            anime.py :: module constant
  RED    anime-sine-table-truncates             anime.py :: sine_table
```

**Problemas encontrados**

1. **O quadro que o estado nomeia não é o quadro que o jogo está lendo.**
   Ligar captura e arquivo por `layout.ANIME_STATE` funciona no slot 2 e falha
   inteiro no slot 1, e o sintoma é tentador: metade dos ângulos "não está no
   arquivo", o que se lê como interpolação. Foi escrito como achado no plano e
   na task 32 antes de ser remedido. **Ponteiro que diz onde o jogo ESTÁ lendo
   ganha de ponteiro que diz o que ele está tocando.**
2. **A animação avança NO MEIO de uma passada de desenho** — as cinco
   primeiras peças de uma passada vieram de um quadro e as sete seguintes do
   seguinte. É o que motivou ler por parada, e continua valendo.
3. **Dez variantes de desempacotamento dividem o mesmo dispatch**
   (`0x80011DA0`), e só uma para na instrução vigiada. Herdar o par da peça
   anterior nomeia bytes errados com cara de certo: doze peças de 108 casaram
   assim antes de o par ser **consumido** por peça.
4. **Casar ângulo por "existe no arquivo" produz falso positivo.** Procurando o
   trio nos 3.952 quadros, seis membros do goleiro acharam um par que não era o
   deles e a distância da matriz foi de 1 para 188.
5. **A tabela de seno não precisa ser versionada, e isso é medição.** Despejada
   da RAM (16 KB) e comparada com `round(sin·4096)`: 0 divergência em 4.096.
   Truncar dá 3.080 — o controle plantado usa exatamente essa troca.
6. **O controle `cli-check-forgets-a-module` casava com o último nome da lista
   do `cli.py`.** Acrescentar `anime` no fim fez o literal parar de casar, e o
   gate acusou *"matched 0 times"* — nem verde nem vermelho: um controle que
   deixou de existir.
