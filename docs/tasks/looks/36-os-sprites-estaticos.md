---
id: LOOKS-TASK-36
title: "Os sprites estáticos da tela — placa, caixas, ícone, barra, título e setas, lidos do disco"
type: implementação
category: render
phase: 10
depends_on: ["LOOKS-TASK-31"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
---

# LOOKS-TASK-36: Os sprites estáticos da tela

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o), a tabela dos sprites da quinta passada.
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário. A 31
  mediu de onde vem cada sprite da tela; esta os desenha.
- **O que já está medido:** o `oracle.py --scenery` anda a lista do quadro,
  parte cada nó em comandos e deixa os sprites em `work/looks-scenery/slotN.json`
  (ponto, tamanho, `uv`, CLUT, página, cor, blend). Os texels de cada grupo
  saem do `EDT_2D.BIN` ou do `DAT2D.BIN` e batem com a VRAM; as oito CLUTs
  saem do `DAT2D.BIN`.
- **Os estáticos:** o título `S SET`, o ícone à esquerda da camisa, as caixas
  verdes da camisa, a barra vazia ao lado da placa e a placa `CB`/`GK` — cuja
  **CLUT muda com a posição** ((208,499) no jogador de linha, (192,499) no
  goleiro), o que diz que a janela precisa saber a posição do jogador, não só
  copiar o quadro de um slot.
- **As setas `◀ ▶` não são estáticas:** seguem o cursor e somem na ponta do
  alcance (armadilha 28 do perfil). A `▶` está medida (página (704,0), CLUT
  (80,497), `DAT2D.BIN`); a `◀` não apareceu no quadro medido, com o cursor
  em `NAT`. Medir quando cada uma aparece é desta task.
- **O texto não é desta task** — é a [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md). A ajuda também
  não — é a [`LOOKS-TASK-39`](/docs/tasks/looks/39-o-texto-da-ajuda.md).

---

## Objetivo

A janela desenha os sprites estáticos da tela e as setas com texels e paletas
lidos do disco japonês pela guarda, no lugar e na ordem em que o jogo os
desenha.

---

## Critério de conclusão

- [ ] Um núcleo que monta a imagem de um sprite a partir do disco (texels
      LZSS, página, CLUT, cor e blend), com self-check e controle plantado —
      o texel 0 transparente e a modulação pela cor do sprite inclusos.
- [ ] A janela desenha título, ícone, caixas, barra e placa; a CLUT da placa
      vem da posição do jogador, conferida nos dois slots.
- [ ] As setas: quando cada uma aparece medido no jogo, e a janela as
      desenha igual ao longo de `oracle.py --keys`, com o controle fechando
      antes.
- [ ] O `looks_ui` amostra os sprites contra a tabela medida, com um controle
      plantado vermelho.
- [ ] `confront.py --outside` ganha as regiões desses sprites, com o jogo
      fotografado duas vezes de controle.

---

## Log de Execução

*(preencher ao executar)*
