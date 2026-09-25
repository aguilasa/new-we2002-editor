---
id: LOOKS-TASK-34
title: "O goleiro — figura 1 montada e andando na tela, conferida no slot 1"
type: verificação
category: oráculo
phase: 11
depends_on: [LOOKS-TASK-33]
status: pending
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.4"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
---

# LOOKS-TASK-34: O goleiro

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.4, e §6 (b).
- **O goleiro é o mesmo esqueleto com duas peças remodeladas** (§1.5), na
  lista 1 do `EDT_MOD.BIN`. Se a animação é a mesma, a pose se aplica às seções
  da lista 1; se não for, é outra entrada.
- **As tasks anteriores medem os dois slots**, mas o que implementam pode ter
  sido exercitado só na figura 0. Resultado negativo é resultado.

---

- **Da [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md):** o
  `confront.py --silhouette 1` já julga **oito passadas** do ciclo no slot 1,
  as duas metades incluídas, sem `N` na linha de comando — medido em
  2026-09-25, a melhor passada a 13–15% da tinta do jogo e a 1–3 passadas da
  nomeada. E o `oracle.py --rhythm` mostrou o goleiro lendo os pares da
  **mesma entrada 5** que o jogador de linha em todas as linhas menos `FOOT`,
  onde o jogo toca a entrada 147 nos dois slots. O que sobra para esta task é
  olhar a janela, e o que for só da figura 1.

---

## Objetivo

Conferir que o slot 1 sai com a placa `GK`, a figura 1 montada, vestida e
andando igual ao jogo, e corrigir o que só funcionava na figura 0.

---

## Critério de conclusão

- [ ] `.\make.ps1 looks -State 1` olhado, com captura no Log.
- [ ] Qual animação a figura 1 usa, medido.
- [ ] `confront.py --silhouette 1 <N>` em pelo menos oito N, dentro do limiar.
- [ ] O que diferia entre as figuras corrigido, ou aberto como CORR com a
      tupla nomeada.

---

## Log de Execução

*(preencher ao executar)*
