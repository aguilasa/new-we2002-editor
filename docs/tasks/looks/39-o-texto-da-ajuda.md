---
id: LOOKS-TASK-39
title: "O texto da ajuda — quem escreve a página (832,256) na VRAM, e de onde"
type: investigação
category: render
phase: 10
depends_on: [LOOKS-TASK-37]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: pending
review_commit: null
done_on: 2026-09-22
done_commit: 42c4ebfa
---

# LOOKS-TASK-39: O texto da ajuda

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o).
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário.
- **Medido:** o texto da caixa de ajuda (`Visual` com o cursor em `NAT`) são
  seis sprites 16×16 da página (832,256), CLUT (64,496), e **nenhuma imagem do
  disco cobre esses texels** — o `DATSEL3.BIN` tem um registro ali e bate só
  em parte. A CLUT é do `DAT2D.BIN`. O jogo escreve os texels na VRAM em tempo
  de execução (armadilha 90 do perfil).
- **A ajuda muda com a linha** (`layout.SCREEN_HELP` aponta o texto em
  Shift-JIS), então o jogo renderiza cada texto numa página e desenha a página.
  Candidatos: uma fonte de outra página copiada glifo a glifo, ou uma fonte em
  outro arquivo. A cópia passa pelo GPU (comando de cópia de VRAM ou de carga
  na lista) ou pela CPU; a lista do quadro já é legível (`oracle.commands_of`).
- **Depois da 37**, porque se a ajuda é montada a partir da mesma fonte, a
  tabela de glifos já estará lida.

---

## Objetivo

Dizer de onde vêm os texels da ajuda e, se forem do disco, a janela desenhá-la
com eles.

---

## Critério de conclusão

- [x] Quem escreve a página (832,256), medido: o comando ou a instrução, e a
      origem dos texels.
- [x] Se a origem é o disco: a janela desenha a ajuda de cada linha com ela,
      conferida contra o jogo em `oracle.py --keys` nos dois slots. Se não é:
      o resultado negativo escrito na §10.3 (o), com a razão, e a janela
      mantém o texto medido do `screen.json`.
- [x] `confront.py --outside` na caixa de ajuda, com o controle do jogo.

---

## Log de Execução

**Executado em:** 2026-09-22

### O que foi feito

- **A resposta é negativa para o disco, e definitiva: os texels são da ROM do
  console.** Para cada caractere de dois bytes da string, o jogo chama
  `0x8003BEEC`, que cai numa **chamada de BIOS** (`0x8003873C`: `t2` =
  `0xB0`, `t1` = `0x51` — a busca na ROM de caracteres) e devolve o endereço
  de um bitmap **16×15**, 30 bytes, uma linha por meia-palavra **big-endian**.
  Todo endereço devolvido cai em `0xBFC00000+0x80000`.
- **Quem escreve a página (832,256):** o jogo, por **cópia de memória para a
  VRAM** — o comando GP0 `0xA0` — de um retângulo de 4 meias-palavras por 16
  linhas, que a 4 bits é um ladrilho 16×16. A página é uma **tira**, um
  ladrilho por caractere que desenha, escrita só quando o texto muda.
- **A cadeia se lê do disco, e é recusada se não for ela.** O
  `/SLPM_870.56` entrou na guarda (digest japonês, LBA 24, 337.920 bytes,
  `CODE_FILES`), com a base lida do próprio cabeçalho PS-EXE e conferida
  contra `layout.BOOT_BASE`. O `oracle.help_chain` decodifica o `jal`, o
  alcance do stub e as três instruções da chamada de BIOS, e cada uma tem um
  caso vermelho no self-check.
- **A janela não muda.** A ROM do console não está no disco, não é deste
  repositório e a regra do ciclo é ler do disco pela guarda; a caixa continua
  escrita com o texto medido do `screen.json` numa fonte de apoio do Qt. O
  `confront.py --outside` passou a medir a caixa pixel a pixel e a **não
  afirmá-la**, com a linha dizendo por quê.
- **O `oracle.py --help-box` é quem remede tudo isso**, nos dois slots, com
  três controles: a tira parada com nada apertado, a mesma tecla duas vezes, e
  o bitmap do caractere seguinte.

### Evidência

```text
$ python tools/looks/oracle.py --help-box
  the chain, decoded from /SLPM_870.56 (335872 bytes of code):
    0x800331B8 jal 0x8003BEEC, which calls 0x8003873C at 0x8003BF2C, 0x8003BF4C, 0x8003BF7C -- the BIOS vector 0x000000B0, function 0x51
    and 4 code(s) the dispatch draws from VRAM instead: 0x819a, 0x819c, 0x81a1, 0x81a3
  -- slot 2 (outfield player) --   (o slot 1 deu as mesmas linhas)
    control: with nothing pressed, nothing wrote the page in 6s: still
    one Down wrote the page: 1 hit(s), 4x16, tile(s) 14 of the strip
      (the pc at each: 0x8003A950 -- printed, not asserted: the copy is a DMA, and the watch reports one hit for the press, not one per tile)
    control: the same press twice asks for the same 14 glyph(s)
    the box now shows the SKIN help, 'Skin Colour   # Turn': 15 character(s) that draw, 14 of them asked of the ROM and 1 drawn from VRAM (0x81a1)
    14 lookup(s), 0 answer(s) outside the console's ROM at 0xBFC00000+0x80000; the first 0x800FCF50 -> 0xBFC67482, the last 0x800FCF71 -> 0xBFC676F8
    the frame cuts 15 sprite(s) from the page, 14 of them on the CLUT [64, 496]
    14 of 14 tile(s) are the ROM's bitmap plus its one-pixel outline; control: the NEXT character's tile takes 0 of those bitmaps
oracle --help-box: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --outside
  -- slot 2 --   (e o mesmo no slot 1)
    help, pixel for pixel within 16 per channel: 323 of 14787 differ (the game against itself: 0; the game one pixel off: 316)  (the console's font, not ours to draw: not asserted)
    labels, pixel for pixel within 16 per channel: 0 of 16416 differ (...)
    values, pixel for pixel within 16 per channel: 0 of 23472 differ (...)
confront --outside: 0 problem(s) over 2 slot(s)
```

Os casos vermelhos da cadeia, no `oracle.py --check`: a chamada que não é
`jal`, a chamada que vai para outro lugar, a rotina que não alcança o stub, o
stub que não carrega `0xB0`, o stub que não salta por `t2`, e o stub que pede
outra função — seis, mais o glifo de menos de 30 bytes e os dois casos do
bitmap que não cabe no ladrilho.

### Problemas encontrados

- **O `pc` do watchpoint de VRAM não é quem escreveu, e isso quase virou
  medida.** Duas sondas seguidas deram `0x8003A950` para o acerto sobre a
  tira, e a terceira e a quarta deram `0x8003F2F4` e `0x8010A910`: a cópia é
  por DMA, então o programa já andou quando o GPU toca a VRAM. A asserção
  sobre o `pc` saiu da ferramenta (fica impressa, dizendo por quê), e quem
  afirma quem escreve é o retângulo mais o código lido do disco
  (armadilha 96). Ele também reporta **um** acerto por tecla, o último do
  lote: contar ladrilhos por ali dá 1 de 15.
- **Um ladrilho de quinze não vem da ROM.** A ajuda do `SKIN` tem 15
  caracteres que desenham e 14 chamadas; o que falta é o `■`. O despacho
  nomeia **quatro** códigos (`0x819A`, `0x819C`, `0x81A1`, `0x81A3`) que
  desenha de um lugar fixo da VRAM, e é por isso que o `■` é o único sprite
  da caixa na CLUT (32,498). **De onde saem os texels desse ladrilho não foi
  medido** — está na §10.3 (o) como aberto.
- **A busca na RAM pelos texels não achou nada, e a razão era o instrumento.**
  A tira decodificada da VRAM não aparece na RAM porque o jogo monta cada
  ladrilho no scratchpad (`0x1F800360`), que não está nos dois megabytes; e a
  leitura de VRAM vem por PNG, sem o bit 15 de cada meia-palavra
  (`COLOUR_BITS`), o que estraga toda busca por bytes exatos. A comparação que
  vale é de **tinta** — texel zero ou não —, que sobrevive à viagem.
- **Um achado para outra hora:** 22 códigos (kanji e área privada) têm bitmap
  próprio no `/SELECT.BIN`, nos offsets 253.728 (os códigos) e 253.772 (os
  bitmaps de 32 bytes), achados por conteúdo a partir da RAM. Nenhum deles
  aparece nesta tela.

### Gates

Todos verdes sobre esta árvore; depois deles só mudou prosa.

```text
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 27 file(s), 30891 line(s)
  ..... 104 of 104 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 16 of 16 negative control(s) red, and the window drew every tuple it was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --help-box
oracle --help-box: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --outside
confront --outside: 0 problem(s) over 2 slot(s)

$ python tools/check_tasks.py
check: 0 error(s), 11 warning(s) in 4 cycle(s)
```
- **Closed** — commit `42c4ebfa` (2026-09-22): feat(looks): measure where the help box's text comes from
  - Files (`git show --name-status 42c4ebfa`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/39-o-texto-da-ajuda.md`
    - `M tools/looks/confront.py`
    - `M tools/looks/layout.py`
    - `M tools/looks/oracle.py`
