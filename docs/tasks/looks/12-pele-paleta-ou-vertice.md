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

---

## Objetivo

Saber como a cor chega ao boneco, e portanto o que o renderizador tem de fazer.

---

## Critério de conclusão

- [ ] Medido, com `diff_memory` ou leitura de VRAM, o que muda quando `SKIN`
      vai de `A` a `D`: a CLUT em VRAM, as cores de vértice na RAM, ou as duas.
- [ ] Mesma medição para `H.COL` e `H.F.COL.`, que são candidatos a paleta pela
      matriz do Superpack (`65892 + raça*512 + tipo*32`).
- [ ] **A matriz do Superpack é conferida** — quatro raças × oito tipos —, e
      confirmada ou desmentida contra o disco.
- [ ] O resultado diz, em uma frase, o que o `viewer.py` da Fase 5 precisa
      implementar: textura com CLUT, cor de vértice, ou os dois caminhos.

---

## Log de Execução

*(preencher ao executar)*
