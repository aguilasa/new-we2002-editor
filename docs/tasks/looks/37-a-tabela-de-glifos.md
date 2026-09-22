---
id: LOOKS-TASK-37
title: "A tabela de glifos — o texto da tela desenhado com a fonte do `EDT_2D.BIN`"
type: implementação
category: render
phase: 10
depends_on: [LOOKS-TASK-31]
status: pending
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
---

# LOOKS-TASK-37: A tabela de glifos

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o).
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário.
- **A fonte está medida:** 121 sprites de altura 12 cortados da página
  (704,256) a 4 bits, CLUT (0,497), e os texels saem do `EDT_2D.BIN`, iguais à
  VRAM. A janela ainda escreve com uma fonte do Qt.
- **Foto de um quadro não basta:** o texto muda com a tecla. O que falta é a
  regra do jogo — de cada código de caractere para `u`, `v` e largura. Ela
  está na rotina de glifo (`layout.SCREEN_GLYPH`): faixas de código com
  aritmética própria e uma tabela de pares (`u`, largura) lida a partir de
  `0x8010D008`, na overlay. A rotina e a overlay são do **disco inglês**, que
  é o que o emulador roda; se a tabela difere no japonês, isso é achado, e a
  guarda do `/SELECT8.BIN` já recusa o inglês.
- **O avanço entre glifos** é a largura mais o espaçamento do objeto de texto
  (`+14` do objeto que o `SCREEN_PRINT` recebe), e os dois passes da rotina
  (medir e desenhar) usam a mesma largura.

---

## Objetivo

A janela escreve todo o texto da tela — rótulos, valores, `SHIRT N`, a placa —
com os glifos do `EDT_2D.BIN`, posicionados pela regra do jogo.

---

## Critério de conclusão

- [x] A regra código → (`u`, `v`, largura) lida do disco pela guarda, e de que
      disco ela vem, escrito.
- [x] Conferida contra os 121 sprites de fonte do quadro medido, nos dois
      slots: cada código dá o `uv`, o tamanho e o ponto que o jogo desenhou,
      com um controle plantado vermelho.
- [x] A janela desenha o texto com esses glifos; `oracle.py --keys` continua
      0 diferença nos dois slots.
- [x] `confront.py --outside` nas regiões de texto, com o jogo fotografado
      duas vezes de controle.

---

## Notas

- **Da [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md):** a
  janela tem `--no-stand-in-text`, que omite o texto da placa e da camisa
  escrito com a fonte do Qt, porque ele cobre texels de sprite que o jogo deixa
  à mostra (armadilha 93). Com os glifos do jogo, a opção e o `stand_in_text`
  do `looks_set.py` perdem o motivo — e o `looks_ui` pode voltar a fotografar
  a janela inteira.

## Log de Execução

**Executado em:** 2026-09-22

### O que foi feito

- **A rotina não está onde a task supunha.** A task fala de uma tabela "na
  overlay", e a overlay que o ciclo já lia é o `/SELECT8.BIN`, que termina em
  0x800E98F8. A rotina (0x8010BB04) e a tabela (0x8010D008) estão no
  **`/SELECTC.BIN`**, carregado em 0x800FC000. Achei-o por conteúdo: 64 bytes
  da RAM procurados nos 245 arquivos de cada disco (armadilha 94).
- **De que disco a regra vem:** o `/SELECTC.BIN` difere entre os discos
  (5.201 bytes entre 0x2B8 e 0x5A26, o texto traduzido). A rotina e a tabela
  são iguais byte a byte no japonês, no inglês e na RAM do jogo. A regra é
  lida do **japonês**, pela guarda: o arquivo entrou no `DIGEST` e em
  `CODE_FILES`, com LBA 1950 e 106.966 bytes.
- **`tools/looks/glyphs.py` (novo):** a tabela de pares (`u`, largura) vem do
  disco, e as faixas de `v` foram transcritas da rotina (`V_BANDS`). A regra
  é **recusada** se a rotina no disco não tiver o sha256 de onde a transcrição
  foi lida (`layout.GLYPH_ROUTINE_DIGEST`). Os códigos fora de 32..126 também
  são recusados: a rotina os trata por aritmética e por busca de Shift-JIS,
  e nenhuma string desta tela chega lá. `Font.run` dispõe o texto: largura
  mais o espaçamento do objeto, e o espaço anda sem desenhar.
- **`oracle.py`:**
  - o objeto de texto passa a ser lido em 20 bytes: o byte 14 é o espaçamento,
    os bytes 16 a 18 a cor, e o byte 13 o que parece o alinhamento;
  - o gerador grava `initial.*.styles` no `screen.json`;
  - `--glyphs` confere a regra contra o quadro.
- **`screen.py`:** `State.style`, `value_style`, `value_box`, e a validação
  dos estilos, com dois casos vermelhos no toy.
- **Janela:** rótulos, valores, placa e camisa são escritos com os glifos do
  disco, na cor e no espaçamento medidos. O título continua sendo o sprite da
  36. Os valores partem da borda esquerda da caixa da linha, e a placa e a
  camisa do x do objeto: onde o jogo os põe é a 38. A opção
  `--no-stand-in-text` virou `--no-unplaced-text`.
- **`confront.py --outside`:** entraram as regiões `labels` e `values` e a
  comparação dos rótulos **pixel a pixel**.

### Evidência

```text
$ python tools/looks/glyphs.py --check-image
glyphs: the routine at 0xfb04-0x100d8 of /SELECTC.BIN is the one V_BANDS were read from; the table at 0x11008 holds 95 pairs
  v 146: '0123456789'               widths [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
  v 146: 'ABCDEFGHIJ'               widths [11, 10, 9, 11, 9, 9, 11, 11, 5, 10]
  v 158: 'KLMNOPQRSTUVWXYZ'         widths [10, 9, 12, 11, 11, 11, 11, 11, 9, 9, 11, 11, 14, 11, 10, 11]
  no glyph (width 0): @ ^ ~
glyphs --check-image: 0 problem(s)

$ python tools/looks/controls.py --only <cada um dos três>
controls: 1 of 1 red (1 substitution)     # glyphs-band-shifted
controls: 1 of 1 red (1 substitution)     # glyphs-table-one-pair-on
controls: 1 of 1 red (1 substitution)     # glyphs-routine-unchecked

$ python tools/looks/oracle.py --glyphs
  -- slot 2 --
    134 glyph(s) drawn, 13 space(s); 121 of 121 font sprite(s) equal to the rule in uv, size and CLUT, 0 unclaimed
    control: the table read 1 pair(s) off matches 0 of them
  -- slot 1 --
    134 glyph(s) drawn, 13 space(s); 121 of 121 font sprite(s) equal to the rule in uv, size and CLUT, 0 unclaimed
    control: the table read 1 pair(s) off matches 0 of them
oracle --glyphs: 0 problem(s) over 2 slot(s)
```

O ponto de cada sprite é o `(x, y)` que a passada de desenho reporta mais o
centro do display (256, 120): o `--glyphs` acha o sprite **nesse ponto**. O
avanço entre dois glifos de um objeto é a largura mais o byte 14. Medido em
todas as corridas das linhas: 2 nos rótulos e nos `TYPE`, 1 em `Unknown`, 0
em `SHIRT N` e nos dígitos.

```text
$ python tools/looks/oracle.py --screen --write      # 20 min 30 s
oracle --screen --write: wrote tools/looks/screen.json
  (git diff --stat: 278 inserções, 0 remoções)

$ python tools/looks/oracle.py --keys "" 2          # e 1: a sequência padrão
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows and the same cursor box
oracle --keys: 0 difference(s) after 19 press(es), across the game, screen.json and our window

$ python tools/looks/confront.py --outside
  -- slot 2 --
    control: the game photographed twice, the same ground in all 13 region(s)
    labels, pixel for pixel: 0 of 16416 differ (the game against itself: 0; the game one pixel off: 2875)
    labels       game (0, 49, 49)     ours (0, 53, 55)       6 apart
    values       game (0, 41, 49)     ours (0, 42, 55)       6 apart
  -- slot 1 --
    (o mesmo: 0 de 16416, 2875 deslocado, 6 e 6)
confront --outside: 0 problem(s) over 2 slot(s)

$ python tools/looks/ui_check.py                                               # 3 min 45 s
looks_ui: 16 of 16 negative control(s) red, ...

$ python tools/looks/oracle.py --check-live
oracle --check-live: 0 failure(s)
```

### Problemas encontrados

- **A mediana de uma região de texto mede o fundo, não as letras.** Os 6 de
  `labels` e `values` são a faixa, e sairiam iguais com o texto errado. Por
  isso entrou a comparação pixel a pixel. Ela só vale para os rótulos, que o
  jogo alinha à esquerda no x do objeto. Os valores, a placa e a camisa
  dependem do alinhamento da 38, e a nota foi para lá.
- **Um valor sai de mais de um objeto.** A janela o escreve numa corrida só,
  com o estilo do último pedaço. A nota está na 38.
- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado**
  (seriam mais 20 min). O `screen.validate` fechou no gerador, e o `--keys`
  nos dois slots confere o arquivo contra o jogo.

### Gates

Transcritos depois do commit de trabalho.
