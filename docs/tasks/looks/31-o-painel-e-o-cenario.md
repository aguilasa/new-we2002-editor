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
- **O que a [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md) deixou
  para cá, olhando a dupla de capturas que ela pôs no Log** — a janela ao lado
  do quadro do emulador, com os mesmos doze textos:
  - **as duas setas `◀ ▶` ao lado do valor da linha selecionada.** O jogo as
    desenha coladas na caixa do cursor e elas **somem na ponta do alcance** —
    é o que a armadilha 28 do perfil já media pelo outro lado, contando valor
    pela célula. A janela não as desenha, porque o `screen.json` guarda a
    caixa do cursor e não elas. Medir de onde saem (objeto de texto, glifo ou
    polígono) responde de quebra se a seta que some é a testemunha barata de
    "esta ponta travou";
  - **o valor é alinhado à DIREITA dentro da caixa do cursor** no jogo, e a
    janela o escreve a partir da esquerda dela. A caixa está medida; a posição
    do texto dentro dela, não;
  - **a placa (`GK`/`CB`) e o nome da camisa têm caixa própria**, com uma
    barra vazia ao lado da camisa e um ícone à esquerda dela;
  - as cores, o degradê e a fonte, que é o objeto desta task.

- **O painel aproxima a câmera na CABEÇA quando a linha sob o cursor é de
  cabeça** — medido pela [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md)
  em 2026-09-18: com o cursor em `HAIR` a foto é um close-up, com `Kind of Hair`
  na caixa de ajuda e o dobro da tinta da figura inteira. A janela não faz isso:
  ela desenha sempre a câmera de corpo inteiro que o `oracle.py --camera` mediu
  com o cursor em `NAT`. Medir a câmera do close-up e trocá-la por linha é
  desta task, junto com o resto do painel.

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
