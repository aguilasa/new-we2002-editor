---
id: LOOKS-TASK-05
title: "`modelfile.py` — as 106 seções do `MODEL.BIN` e as 11 do `EDT_MOD.BIN`"
type: implementação
category: formato
phase: 1
depends_on: ["LOOKS-TASK-04"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.5"
status: pendente
---

# LOOKS-TASK-05: Os dois arquivos de modelo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.4 e
  §1.5.
- **Os dois arquivos não se percorrem do mesmo jeito**, e é a armadilha 2 do
  plano: o `MODEL.BIN` é contíguo a partir de 1816; o `EDT_MOD.BIN` é dirigido
  pela lista de ponteiros do cabeçalho, com dados não-geometria no meio.
- **A ordem da lista não é a ordem do arquivo** (armadilha 3). Assumir a do
  arquivo embaralha peça sem sintoma visível.

---

## Objetivo

`tools/looks/modelfile.py`: percorrer os dois arquivos e entregar a lista de
seções, preservando a ordem que a lista de montagem declara.

---

## Critério de conclusão

- [ ] `MODEL.BIN` percorrido a partir de 1816 dá **106 seções, 2.461 vértices,
      1.767 primitivas**, terminando **exatamente em 64.800 = EOF**.
- [ ] Os **6 grupos** do `MODEL.BIN` aparecem com os tamanhos
      `[55, 1, 34, 7, 5, 4]`.
- [ ] O cabeçalho do `EDT_MOD.BIN` é lido como **lista de registros
      `(contagem, ponteiro)` terminada por `0x000000FF`**.
- [ ] `EDT_MOD.BIN` dá **11 seções, 690 vértices, 611 primitivas**, e a última
      termina em 36.064, com o separador fechando em **36.072 = EOF**.
- [ ] As **cinco duplas de contagem idêntica** (`63/56`, `40/34`, `88/86`,
      `72/59`, `40/35`) e a **peça sozinha** (`84/71`) são identificadas como
      tal — sem ainda dizer qual parte do corpo é qual, que é a Fase 2.
- [ ] A ordem entregue é a **da lista**, e um controle negativo que a inverta
      fica vermelho.
- [ ] As contagens acima valem como asserção, não como comentário.

---

## Log de Execução

*(preencher ao executar)*
