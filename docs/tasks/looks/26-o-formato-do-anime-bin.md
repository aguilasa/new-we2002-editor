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

- [ ] `anime.py` com `self_check()` sem imagem, e `--check-image` que pula
      com 77 e está na lista do `cli.py check` (o self-check dele falha se não
      estiver).
- [ ] O cabeçalho lido e a estrutura varrida **até o EOF exato**, com o offset
      de partida ao lado de cada contagem.
- [ ] Qual entrada é a caminhada da tela, medido — não escolhido pelo tamanho.
- [ ] **As matrizes do quadro N da [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) reproduzidas exatamente**, nas onze
      peças e na cabeça, nos dois slots.
- [ ] Dois controles negativos — ordem de campo e escala —, vermelhos pela
      própria causa.
- [ ] §10.3 (l) com o formato medido.

---

## Log de Execução

*(preencher ao executar)*
