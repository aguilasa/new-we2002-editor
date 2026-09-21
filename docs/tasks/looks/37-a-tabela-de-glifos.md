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

- [ ] A regra código → (`u`, `v`, largura) lida do disco pela guarda, e de que
      disco ela vem, escrito.
- [ ] Conferida contra os 121 sprites de fonte do quadro medido, nos dois
      slots: cada código dá o `uv`, o tamanho e o ponto que o jogo desenhou,
      com um controle plantado vermelho.
- [ ] A janela desenha o texto com esses glifos; `oracle.py --keys` continua
      0 diferença nos dois slots.
- [ ] `confront.py --outside` nas regiões de texto, com o jogo fotografado
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

*(preencher ao executar)*
