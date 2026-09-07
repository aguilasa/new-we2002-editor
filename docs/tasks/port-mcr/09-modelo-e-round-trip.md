---
id: MCR-TASK-09
title: "`model.py`, `io.py` e o round-trip byte-idêntico"
type: implementação
category: núcleo
phase: 1
depends_on: ["MCR-TASK-06", "MCR-TASK-07", "MCR-TASK-08"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.1"
status: pendente
---

# MCR-TASK-09: O modelo e o round-trip

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §5.1 e §3.3
  (Regra 2).
- **Os bytes crus são normativos.** `model.Card` guarda os 131.072 bytes e edita
  por read-modify-write no campo; nada mais é tocado. É o que faz os 10 bytes
  finais de cada registro, a folga do bloco, o diretório e os seis campos de
  tática atravessarem intactos.
- O contraexemplo é o upstream, que remonta o arquivo — e é por isso que ele
  consegue escrever no cabeçalho.

---

## Objetivo

O modelo em `dataclasses` sem Qt e sem endereço, o I/O que valida e recusa, e o
round-trip que prova os dois.

---

## Critério de conclusão

- [ ] `Card`, `Player` e `Formation` como `dataclasses`; nenhum endereço fora de
      `layout.py`; nenhum `import` de Qt.
- [ ] **Round-trip forma 1** — ler → gravar: `cmp` = **0 bytes**.
- [ ] **Round-trip forma 2** — ler → decodificar os 23 → re-codificar todos →
      gravar: `cmp` = **0 bytes**. É esta que pega bug de encoder.
- [ ] O **controle negativo** completo, 5/5 vermelhos (§5.2 do plano).
- [ ] Gravação **sempre sobre cópia**; a ferramenta recusa escrever no arquivo
      apontado por `WE2002_MCR_CARD` sem `--force`.
- [ ] Uma edição de ponta a ponta medida no Log: mudar um atributo de um
      jogador muda **exatamente** os bytes esperados, e nada mais.

---

## Log de Execução

*(a preencher)*
