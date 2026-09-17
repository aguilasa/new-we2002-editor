---
id: LOOKS-TASK-29
title: "Incógnita (s) — `HEIG` e `BODY`: o que mudam no desenho, medido pela pose"
type: investigação
category: montagem
phase: 9
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-28"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (s)"
status: pendente
---

# LOOKS-TASK-29: Altura e corpo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.2 e §10.3 (s).
- **`BODY` não escreve em nenhum dos dois arquivos de modelo** (§6 (a)); se
  muda o desenho, muda na transformação — e a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) já lê a transformação.
- **`HEIG` vai de 148 a 211** (`looks.py`), e a tela dos dois states mostra
  `175 cm`. Escala linear em altura é o palpite óbvio, e palpite óbvio já foi
  medido errado neste ciclo mais de uma vez.
- **As linhas já existem na tela** ([`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md)); hoje elas trocam o texto e não o
  desenho.

---

## Objetivo

Medir o que `HEIG` e `BODY` fazem com as matrizes de cada peça, e aplicar no
desenho.

---

## Critério de conclusão

- [ ] A pose do mesmo quadro capturada em pelo menos três alturas (as duas
      pontas e uma do meio) e em todos os valores de `BODY`, nos dois slots.
- [ ] A regra medida — escala por eixo, por peça, ou outra coisa — com a
      diferença de inteiro para inteiro, e o que não muda dito.
- [ ] O `scene.py` aplica a regra, e as matrizes reproduzem as capturadas
      exatamente.
- [ ] Silhueta contra o emulador nas pontas de `HEIG` e em dois `BODY`,
      dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md).
- [ ] Controle negativo: altura aplicada no eixo errado fica vermelha.
- [ ] §10.3 (s) com o veredito e a data.

---

## Log de Execução

*(preencher ao executar)*
