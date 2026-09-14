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
- [ ] O cabeçalho do `EDT_MOD.BIN` é lido como **duas** listas de registros
      `(contagem, ponteiro)` terminadas por `0x000000FF`, de **onze registros
      cada** — não uma. Elas compartilham 15.704 e 17.572, nas mesmas posições.
- [ ] `EDT_MOD.BIN` percorrido **a partir de 216** dá **20 seções, 1.218
      vértices, 1.074 primitivas**, e a última termina em 36.064, com o
      separador fechando em **36.072 = EOF**. O 216 vem do
      `layout.geometry_start()`, **derivado** do menor alvo das listas, e não
      de um número escolhido à mão.
- [ ] **Toda contagem de seção afirmada vem com o offset de onde a varredura
      começou.** Foi a metade que faltou na
      [`LOOKS-TASK-04`](/docs/tasks/looks/04-formato-de-secao.md): começar em
      15.704 dá 11/690/611 fechando no EOF exato, o que parece leitura completa
      e é metade do arquivo
      ([`CORR-LOOKS-010`](/docs/tasks/looks/CORR-LOOKS-010.md)).
- [ ] O `modelfile.py` entrega **modelo por lista**, não "as onze do
      `EDT_MOD.BIN`". Cada lista é uma peça sozinha (`84/71`) mais **cinco
      pares de contagem idêntica** — `30/24`, `80/78`, `72/59`, `40/35`,
      `63/56` na lista A; `40/34`, `88/86`, `72/59`, `40/35`, `63/56` na B —,
      identificados como tal, sem ainda dizer qual parte do corpo é qual, que
      é a Fase 2. **O critério diz de qual lista cada contagem é.**
- [ ] A ordem entregue é a **da lista**, e um controle negativo que a inverta
      fica vermelho.
- [ ] As contagens acima valem como asserção, não como comentário.
- [ ] **O `MODEL.BIN` continua com `MODEL_GEOMETRY_START` constante**, e a task
      diz por quê: o `read_pointer_list()` recusa as listas dele — a de 672
      abre com tag `0x80` e fecha com `0x00000000` em 736, e não com o
      terminador. Medir essa variante, ou registrar que ela fica aberta, é
      desta task.

---

## Log de Execução

*(preencher ao executar)*
