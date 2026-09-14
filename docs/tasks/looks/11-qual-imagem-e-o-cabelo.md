---
id: LOOKS-TASK-11
title: "A contradição 8 × 3.568 — qual imagem do `DAT2D.BIN` é o cabelo"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-10"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.8"
status: pendente
---

# LOOKS-TASK-11: Qual imagem é o cabelo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.8 e
  §1.7.
- **Dois documentos da cena se contradizem.** A tabela do CARP rotula o offset
  **8** como *"Pelos Cuerpos y botines"* e o **3.568** como *"Caras"*; o
  tutorial do `zeta` manda abrir o **3.568** para achar os cabelos.
- Os dois não podem estar certos, e **o disco decide**. É barato: exportar as
  duas imagens e olhar.
- Enquanto não estiver decidido, **nenhum código pode cravar nenhum dos dois**.

---

## Objetivo

Resolver a contradição por exportação, e deixar o rótulo de cada uma das 23
imagens conferido ou marcado como não conferido.

---

## Critério de conclusão

- [ ] As imagens de offset 8 e 3.568 exportadas para PNG e **olhadas**.
- [ ] O veredito registrado com a evidência, e o documento da cena que errou
      fica nomeado — não para culpar, para que ninguém volte a ele.
- [ ] Cross-check barato disponível: o Superpack traz
      `Caras - zeta\cabellowe2002.bmp` (8,1 KB, folha de cabelo 4 bpp) e dois
      `.tim` do mesmo conteúdo; comparar contra a nossa exportação decide sem
      depender de julgamento visual.
- [ ] Os 23 rótulos ficam numa tabela, cada um marcado **conferido** ou
      **opinião de terceiro**.

---

## Log de Execução

*(preencher ao executar)*
