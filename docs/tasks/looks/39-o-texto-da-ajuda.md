---
id: LOOKS-TASK-39
title: "O texto da ajuda — quem escreve a página (832,256) na VRAM, e de onde"
type: investigação
category: render
phase: 10
depends_on: ["LOOKS-TASK-37"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (o)"
status: pendente
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

- [ ] Quem escreve a página (832,256), medido: o comando ou a instrução, e a
      origem dos texels.
- [ ] Se a origem é o disco: a janela desenha a ajuda de cada linha com ela,
      conferida contra o jogo em `oracle.py --keys` nos dois slots. Se não é:
      o resultado negativo escrito na §10.3 (o), com a razão, e a janela
      mantém o texto medido do `screen.json`.
- [ ] `confront.py --outside` na caixa de ajuda, com o controle do jogo.

---

## Log de Execução

*(preencher ao executar)*
