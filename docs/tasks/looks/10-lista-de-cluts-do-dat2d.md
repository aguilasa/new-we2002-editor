---
id: LOOKS-TASK-10
title: "A lista de CLUTs do `DAT2D.BIN` que o `bin_archive.py` não acha"
type: engenharia-reversa
category: textura
phase: 3
depends_on: ["LOOKS-TASK-08"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.7"
status: pendente
---

# LOOKS-TASK-10: A lista de paletas que falta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.7.
- Medido: `bin_archive.py ls` sobre o `DAT2D.BIN` japonês responde
  **`23 image(s), 0 clut(s)`**. As imagens saem inteiras; as paletas, não.
- Que a lista existe, a tabela do CARP diz: as paletas começam em **65.892**,
  logo depois do fim da lista de imagens (65.508 + 23×16 = 65.876).
- **Ler `0 clut(s)` como "não tem paleta" é o erro** — armadilha 6 do plano.
- **Só no disco japonês.** O `DAT2D.BIN` difere no inglês (§1.3).

---

## Objetivo

Achar e decodificar a segunda lista, e decidir se o conserto vai em
`tools/looks/texture.py` ou no próprio `tools/pes2/bin_archive.py`.

---

## Critério de conclusão

- [ ] A lista de CLUTs é localizada por **marcador**, no método que o
      `bin_archive.entries()` já usa, e não por offset constante.
- [ ] A contagem de paletas é medida e registrada, com as de 256 e as de 16
      cores separadas.
- [ ] As **quatro "Pieles"** (65.892 / 66.404 / 66.916 / 67.428) e o bloco de
      **"Botines"** (67.940) que o CARP nomeia são conferidos contra o disco —
      opinião de terceiro vira medição ou cai.
- [ ] Fica decidido e justificado **onde o conserto mora**: se `bin_archive.py`
      ganhar a segunda lista, o `pes2_selftest` tem de continuar verde.
- [ ] Controle negativo: trocar uma paleta por outra fica vermelho.

---

## Log de Execução

*(preencher ao executar)*
