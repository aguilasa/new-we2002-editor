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
      peças e na cabeça, nos dois slots. **NÃO FEITO — é o que falta**, e o
      estado está medido em dois números: das 192 peças capturadas, **96
      trazem ângulos que o arquivo guarda inteiro por inteiro** e **96 trazem
      ângulos que quadro nenhum do arquivo guarda**; e das 96 que ele guarda,
      **32 matrizes saem exatas**, com a pior entrada **188** de 4.096 — todas
      as que erram são membros do goleiro.
- [x] Dois controles negativos — ordem de campo e escala —, vermelhos pela
      própria causa. São **três**: a ordem dos campos, a escala do ângulo e a
      tabela de seno truncada em vez de arredondada. 81 de 81 vermelhos.
- [x] §10.3 (l) com o formato medido, e com os dois pontos abertos escritos ao
      lado.

---

## Log de Execução

**Executado em:** 2026-09-18 — **PARCIAL**

**Resumo do que foi aprendido**

O formato está medido inteiro e o leitor existe: cabeçalho de 204 ponteiros
**absolutos**, payload que se divide em 197 blocos `[quadros][lista][0x0B]` e
**fecha no EOF exato sem um buraco**, quadro de doze pares — um par por peça
desenhada, na ordem em que a tela as desenha —, e três ângulos de 10 bits com
sinal por par, deslocados quatro. A ponte com o gabarito é a captura da pose,
que agora grava **o ângulo e o quadro tocado ao lado de cada peça**: os ângulos
do scratchpad são, par por par, os do quadro do arquivo.

**O que falta, e é por isso que a task não está concluída:** metade dos quadros
que o jogo mostra não está no arquivo — são construídos entre quadros-chave —, e
seis membros do goleiro recebem uma matriz que os ângulos do quadro nomeado não
explicam.

**Arquivos criados/modificados**

- `tools/looks/anime.py` — **novo**: o formato, o decode dos ângulos, a tabela
  de seno gerada, a rotação, `--check`, `--check-image`, `--report` e
  `--against-pose`
- `tools/looks/layout.py` — `ANIME_SCREEN_ENTRY` e `POSE_ANGLES`
- `tools/looks/oracle.py` — a captura passa a gravar, por peça, os três ângulos
  do scratchpad e **o quadro da animação que estava tocando naquela parada**
- `tools/looks/cli.py` e `tools/looks/selftest.py` — o módulo novo nas duas
  listas
- `tools/looks/controls.py` — três controles plantados, e o
  `cli-check-forgets-a-module` repontado para o último da lista
- `docs/PLAN-LOOKS-PY.md` — §10.3 (l) com o formato e o que ficou aberto
- `docs/tasks/looks/32-o-ciclo-da-caminhada.md` — a interpolação medida pela
  metade, encaminhada com os números e o endereço do código que mistura
- `docs/tasks/looks/progresso.md` — a task segue `⬜ Pendente`, de propósito

**Gates, na árvore de `caefe1b`**

```text
$ python tools/looks/selftest.py
  ..... 81 of 81 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
  ok    anime      exit 0   anime --check-image: 0 failure(s)
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/anime.py --check-image
  ok    the header names 204 animation(s), 197 of them distinct
  ok    the walk from offset 816 covers 197 block(s) and 3952 frame(s) and
        ends at 396804   EOF 396804, 0 hole(s)
  ok    every block closes with the same marker
  ok    every frame is 96 byte(s), twelve pairs of words
  ok    the entry the screen plays has a frame for each drawn piece
  ok    and its matrices are rotations

$ python tools/looks/anime.py --against-pose      # 16 capturas de --poses
  96 of 192 carry angles the file holds, integer for integer
  0 carry angles the file holds at that pair but NOT in the frame the state named
  96 carry angles NO frame of the file holds -- the in-between frames, still open
  of the 96 the file holds, 32 matrices are exact and the worst entry is 188 of 4096

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**Os controles, plantados e rodados** — os três novos, cada um numa cópia da
árvore:

```text
  RED    anime-angle-fields-in-the-wrong-order  anime.py :: angles
  RED    anime-angle-loses-its-scale            anime.py :: module constant
  RED    anime-sine-table-truncates             anime.py :: sine_table
```

**Problemas encontrados**

1. **A animação avança NO MEIO de uma passada de desenho.** Ler o ponteiro do
   quadro uma vez por captura nomeia os bytes errados para metade das peças —
   as cinco primeiras de uma passada vieram de um quadro e as sete seguintes do
   seguinte. A captura passou a ler o ponteiro **em cada parada**, e aí os
   ângulos batem 24 de 24 no slot 2.
2. **Casar ângulo por "existe no arquivo" produz falso positivo.** Procurando o
   trio em todos os 3.952 quadros, seis membros do goleiro "acharam" um par que
   não era o deles e a distância da matriz foi de 1 para 188. A comparação de
   matriz só vale onde o trio é o do quadro **que o estado nomeou**.
3. **A tabela de seno não precisa ser versionada, e isso é medição.** Despejada
   da RAM (16 KB) e comparada com `round(sin·4096)`: 0 divergência em 4.096.
   Truncar dá 3.080 — o controle plantado usa exatamente essa troca.
4. **O controle `cli-check-forgets-a-module` casava com o último nome da lista
   do `cli.py`.** Acrescentar `anime` no fim fez o literal dele parar de casar,
   e o gate acusou *"matched 0 times"*, não *"green"*. Controle que cita a
   borda de uma lista envelhece quando a lista cresce.
