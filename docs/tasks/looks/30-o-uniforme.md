---
id: LOOKS-TASK-30
title: "Incógnita (n) — o uniforme: qual `TEX_*.BIN`, na guarda, e as primitivas vestidas"
type: implementação
category: textura
phase: 10
depends_on: ["LOOKS-TASK-20"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (n)"
status: pendente
---

# LOOKS-TASK-30: O uniforme

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (n) e §6 (f).
- **237 primitivas da figura 0 (429 da figura 1) saem cinza** porque amostram
  páginas dos `TEX_*.BIN` (`assembly.py --check-image`), e a guarda não lê o
  que não sabe conferir.
- **Toda leitura de textura sai do disco japonês** (Fase 3), com o digest no
  `layout.py` antes do primeiro byte. Na `golden-european-deluxe.bin`, 18 dos
  105 são form 2 (§8, item 5); no japonês, medir.
- **Qual arquivo a tela carrega se mede na VRAM**, não pelo nome.

---

## Objetivo

Vestir o boneco com o uniforme que a tela `LOOKS SET` mostra: o `TEX_*.BIN`
certo, pela guarda, com páginas e CLUTs resolvidos.

---

## Critério de conclusão

- [ ] Os digests dos `TEX_*.BIN` japoneses no `layout.py`, com a forma de
      cada um medida, e o `iso_source.py --check-discs` estendido.
- [ ] Qual `TEX_*.BIN` a tela dos dois states carrega, medido contra a VRAM.
- [ ] Zero `no image` no relatório do `ui/app.py`, ou o resto nomeado com o
      motivo.
- [ ] **O confronto de cor da §5.3 re-rodado com o uniforme:** as tuplas
      continuam em primeiro lugar.
- [ ] Controle negativo: o `TEX_*.BIN` de outro time fica vermelho.
- [ ] §6 (f) e §10.3 (n) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
