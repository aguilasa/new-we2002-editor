---
id: LOOKS-TASK-03
title: "`iso_source.py` e `layout.py` — a fachada de disco e o monopólio de endereço"
type: implementação
category: núcleo
phase: 1
depends_on: ["LOOKS-TASK-02"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.1"
status: pendente
---

# LOOKS-TASK-03: A fachada de disco e o monopólio de endereço

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.1, §3.2
  e §3.3 (regra 1).
- **Nada de leitor de ISO é escrito aqui.** `tools/pes2/iso.py` já lê a imagem
  japonesa nesta máquina, inclusive no Windows; esta task o **embrulha**, não o
  duplica.
- A regra 1 do ciclo — só `layout.py` carrega endereço — é o que permite mover
  um offset depois sem caçá-lo pela árvore.

---

## Objetivo

`tools/looks/iso_source.py` entrega bytes de arquivo do disco;
`tools/looks/layout.py` é o **único** módulo que sabe LBA, `BASE` e offset.

---

## Critério de conclusão

- [ ] `iso_source.py` abre a imagem por `tools/pes2/iso.py` e entrega
      `/BIN/EDT_MOD.BIN`, `/BIN/MODEL.BIN` e `/BIN/DAT2D.BIN`.
- [ ] `layout.py` carrega, e é o único a carregar: os LBAs (5000, 8100, 5300),
      os dois `BASE` (`0x8011C000`, `0x8016E800`), o início de geometria do
      `MODEL.BIN` (1816) e o offset dos registros de jogador (157.164).
- [ ] Os dois `BASE` são **derivados do cabeçalho e conferidos** contra a
      constante, não apenas cravados — é o método que a §1.2 usa.
- [ ] Varredura mecânica: nenhum endereço fora de `layout.py`.
- [ ] `self_check()` em cada um, com caso vermelho.

---

## Log de Execução

*(preencher ao executar)*
