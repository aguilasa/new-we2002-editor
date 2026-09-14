---
id: LOOKS-TASK-19
title: "`cli.py` e os três alvos de `ctest`"
type: implementação
category: verificação
phase: 7
depends_on: ["LOOKS-TASK-18"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4.4"
status: pendente
---

# LOOKS-TASK-19: A linha de comando e os gates

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4.4 e §9.
- A convenção do repositório é **um alvo por faixa de custo**: um obrigatório
  que não precisa de nada e nunca pula; os dependentes de fixture com
  `SKIP_RETURN_CODE 77` e a variável nomeada na mensagem; os de display/venv
  sob `if(UNIX AND Python3_FOUND)`.

---

## Objetivo

`tools/looks/cli.py` responde pelas perguntas do projeto, e o `ctest` registra
os três alvos.

---

## Critério de conclusão

- [ ] `cli.py` com `sections`, `pieces`, `texture`, `looks` e `check`.
- [ ] `looks_selftest` registrado, sem dependência nenhuma, **nunca pula**.
- [ ] `looks_image` registrado, com `SKIP_RETURN_CODE 77` e
      `WE2002_LOOKS_IMAGE` nomeada na mensagem de skip.
- [ ] `looks_ui` registrado sob `if(UNIX AND Python3_FOUND)`, também com 77.
- [ ] Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped** — e o
      número aparece no Log, copiado da saída.
- [ ] Os alvos dos outros projetos continuam verdes: `ctest -R "pes2|mcr|tasks"`
      sem regressão, especialmente se a LOOKS-TASK-10 mexeu no
      `bin_archive.py`.

---

## Log de Execução

*(preencher ao executar)*
