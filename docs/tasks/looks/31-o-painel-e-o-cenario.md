---
id: LOOKS-TASK-31
title: "Incógnita (o) — o painel e o cenário da tela: do disco ou da GPU"
type: implementação
category: render
phase: 10
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-28"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
---

# LOOKS-TASK-31: O painel e o cenário

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.3 (o).
- **A [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) desenha a tela com o arranjo medido, e o cenário por aproximação.**
  O degradê do painel, a borda, a barra de título, as faixas das linhas e a
  fonte podem ser imagem do `DAT2D.BIN` ou do `EDT_2D.BIN`, ou polígonos da
  GPU — e isso decide se a janela lê ou desenha.
- **A display list já é legível** (`oracle.walk_packets`, §6 (a)).

---

## Objetivo

Dizer de onde vem cada elemento do cenário da tela `LOOKS SET` e reproduzi-lo
na janela, lido do disco quando for do disco.

---

## Critério de conclusão

- [ ] A fonte de cada elemento — painel, borda, barra de título, faixas,
      caixa de ajuda, fonte dos textos — medida pela display list: pacote e
      cores, ou registro de imagem e página.
- [ ] A janela os desenha; o que é imagem sai do disco japonês pela guarda.
- [ ] Com a câmera da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), o nosso quadro e o do emulador comparados **fora
      da silhueta**, com o controle do emulador contra ele mesmo.
- [ ] §10.3 (o) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
