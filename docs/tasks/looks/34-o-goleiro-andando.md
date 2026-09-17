---
id: LOOKS-TASK-34
title: "O goleiro — figura 1 montada e andando na tela, conferida no slot 1"
type: verificação
category: oráculo
phase: 11
depends_on: ["LOOKS-TASK-33"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: pendente
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
