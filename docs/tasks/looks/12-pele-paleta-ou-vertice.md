---
id: LOOKS-TASK-12
title: "Incógnita (d) — pele é troca de paleta ou de cor de vértice?"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-11"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-12: Pele — paleta ou cor de vértice

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (d), e §1.6.
- A GPU responde **4-bit CLUT** com textura ligada; a primitiva de 24 bytes das
  seções carrega **cor por vértice e nenhum UV**. Os dois não podem valer para
  a mesma geometria.
- Na tela, `SKIN` de `A` para `D` mudou o tom **sem mexer em vértice nenhum** —
  o que é compatível com as duas hipóteses.
- **Decidir isto decide metade da Fase 3**, e a resposta depende da
  LOOKS-TASK-08.
- **Comece por `load_state`.** Os dois states de 2026-09-14 põem o jogo na tela
  de edição: **slot 1 goleiro, slot 2 jogador de linha**, os dois no disco
  inglês. Recarregar entre medições dá baseline byte a byte idêntico, e é o que
  faz o diff medir só o que você mudou.
- **A RAM se lê por MCP vivo.** O `savestate.py` não alcança a RAM nesta
  máquina: sem CLI `zstd` e sem o módulo `zstandard`, ele lê cabeçalho e para.


- **O terceiro controle negativo da §5.5 é desta fase, e está em aberto.**
  A [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md)
  entregou oito controles em 2026-09-14 e **não** o de paleta — *trocar uma
  paleta por outra* não tem o que derrubar enquanto nada lê paleta. Quando
  esta task decidir se a pele é troca de paleta ou de cor de vértice, o
  controle entra no `tools/looks/controls.py` como substituição literal, e
  o `looks_selftest` passa a exigi-lo vermelho como exige os outros oito.

---

- **A resposta já foi medida, e esta task começa com ela na mão.** Em
  2026-09-14 a [`LOOKS-TASK-08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md)
  mediu, por `python tools/looks/oracle.py --fields SKIN`, que **cada passo de
  `SKIN` soma `0x40` ao byte baixo do CLUT id** das primitivas da pele — quatro
  valores ao todo, que são as quatro peles do `kSkin[4]`. **É paleta.** Não há
  cor de vértice em jogo: a pergunta desta task nasceu da leitura errada da
  primitiva, que dizia "quatro cores, sem UV" e foi corrigida na §1.6.
- **O que continua sendo desta task** é o outro lado do critério: dizer o que o
  renderizador tem de implementar, com a paleta **lida do disco** e não
  deduzida, e o controle da §5.5 — trocar uma paleta por outra e exigir
  vermelho — que a
  [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md)
  encaminhou para cá por não ter o que derrubar ainda. O veredito adianta a
  direção; não substitui a medição da paleta.

---

## Objetivo

Saber como a cor chega ao boneco, e portanto o que o renderizador tem de fazer.

---

## Critério de conclusão

- [ ] Medido, a partir de `load_state` e com `diff_memory` ou leitura de VRAM,
      o que muda quando `SKIN` vai de `A` a `D`: a CLUT em VRAM, as cores de
      vértice na RAM, ou as duas.
- [ ] **Um passo de cada vez, recarregando o state entre eles.** `A→B→C→D`
      numa sessão só acumula quatro mudanças e uma câmera que se moveu;
      `A→D` a partir do mesmo baseline mede uma coisa.
- [ ] Mesma medição para `H.COL` e `H.F.COL.`, que são candidatos a paleta pela
      matriz do Superpack (`65892 + raça*512 + tipo*32`).
- [ ] **A matriz do Superpack é conferida** — quatro raças × oito tipos —, e
      confirmada ou desmentida contra o disco.
- [ ] O resultado diz, em uma frase, o que o `viewer.py` da Fase 5 precisa
      implementar: textura com CLUT, cor de vértice, ou os dois caminhos.

---

## Log de Execução

*(preencher ao executar)*
