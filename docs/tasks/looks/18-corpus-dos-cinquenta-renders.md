---
id: LOOKS-TASK-18
title: "Os 50 renders do Superpack como corpus independente"
type: verificação
category: oráculo
phase: 6
depends_on: ["LOOKS-TASK-17"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.4"
status: pendente
---

# LOOKS-TASK-18: O corpus dos cinquenta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.4.
- `MCR\We DB - polipoli\Faces\` tem **50 JPGs**, dos quais **49 nomeados
  pela tupla exata**: `A-I3-A-F-A` é pele A, cabelo I3, cor A, barba F, cor de
  barba A. O quinquagésimo é o `0.jpg` do terceiro bullet.
- **O caminho é relativo a `Superpackv6\We2002\`, não à raiz da coletânea** —
  `Superpackv6\MCR` não existe. Medido na
  [`LOOKS-TASK-01`](/docs/tasks/looks/01-base-legal-e-linhagem.md) em
  2026-09-14, junto com a correção dos números da §2 do plano.
- **São 50 arquivos, mas 49 tuplas.** O quinquagésimo se chama `0.jpg` e não
  tem tupla no nome — conferido na mesma data, `50 .jpg`, o primeiro em ordem
  sendo `0.jpg` e o segundo `A-A1-A-A-A.jpg`. Quem executar esta task decide o
  que ele é (referência do default? descarte?) antes de contar cobertura: um
  parser que exija tupla no nome **quebra** nele, e um que o ignore em silêncio
  reporta 50 onde mediu 49.
- **O valor deles é serem de outra pessoa.** O confronto da LOOKS-TASK-17 usa o
  mesmo caminho de código dos dois lados em parte do percurso; um corpus
  externo pega erro sistemático que ele não pegaria.
- **Não entram no git** (§2). Ficam apontados por variável de ambiente, como as
  outras fixtures do repositório.

---

- **As 49 tuplas já foram parseadas, e a cobertura medida — por comando.**
  `python tools/looks/looks.py --corpus <pasta>`, ou com a pasta em
  `WE2002_LOOKS_CORPUS`. **Não copie os números daqui: rode.** Esta
  transcrição é de 2026-09-15
  ([`CORR-LOOKS-027`](/docs/tasks/looks/CORR-LOOKS-027.md)), e a cobertura
  muda com a pasta que a variável apontar.

  ```text
  refused: 0.jpg -- '0' has 1 part(s) and a tuple has 5: skin_colour, ...
  50 .jpg   parsed: 49   refused: 1   round-trip to its own name: 49
     skin_colour    4 of  4 value(s) covered
     hair_style     9 of 32 value(s) covered
     hair_colour    4 of  8 value(s) covered
     beard_style    6 of  8 value(s) covered
     beard_colour   2 of  8 value(s) covered
  ```

  As 49 formatam de volta para o próprio nome, e o `0.jpg` **recusa com a
  mensagem certa** em vez de virar índice zero — que é o caso que o terceiro
  bullet deste Contexto pedia para não passar em silêncio. A cobertura está
  medida e é baixa onde importa: **9 dos 32 cabelos**, e duas das oito cores de
  barba. Conclusão de cobertura sobre o corpus inteiro é conclusão sobre esse
  pedaço.

---

## Objetivo

Usar o corpus para procurar erro sistemático, não para produzir um número
bonito.

---

## Critério de conclusão

- [ ] As tuplas parseadas do nome do arquivo, e a cobertura medida: quantos
      dos 32 cabelos, das 4 peles e das 7 barbas o corpus toca. **O `0.jpg` tem
      veredito escrito** — o que ele é, e se entra ou fica de fora da conta.
- [ ] Nosso render comparado contra os 50, com a mesma métrica da
      LOOKS-TASK-17.
- [ ] **Os piores casos são olhados um a um**, não só tabulados — é onde erro
      sistemático aparece.
- [ ] Divergência que não se explique por pose ou câmera vira **CORR**, com a
      tupla nomeada.
- [ ] O gate pula (77) sem a variável que aponta o corpus.

---

## Log de Execução

*(preencher ao executar)*
