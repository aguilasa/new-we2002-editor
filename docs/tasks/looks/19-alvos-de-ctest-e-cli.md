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
- [x] `looks_selftest` **já registrado**, pela
      [`LOOKS-TASK-06`](/docs/tasks/looks/06-harness-controles-e-selftest.md).
      Esta task **confere**: sem dependência nenhuma e **nunca pula**.
- [x] `looks_image` **já registrado** — entrou na
      [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) em 2026-09-14,
      porque o perfil o prometia desde a LOOKS-TASK-05 e `ctest -R looks`
      respondia `No tests were found!!!` **saindo zero**, que se lê como
      verde. Esta task **confere**, não cria: `SKIP_RETURN_CODE 77`,
      `WE2002_LOOKS_IMAGE` nomeada na mensagem de skip, e o disco inglês
      recusado em vez de aceito em silêncio.
- [ ] `looks_ui` registrado sob `if(UNIX AND Python3_FOUND)`, também com 77.
- [ ] Numa máquina limpa, `ctest -R looks` dá **1 passed, 2 skipped** — e o
      número aparece no Log, **copiado da saída de uma corrida de verdade**.
      Até esta task são **1 passed, 1 skipped**: o `looks_selftest` passa e o
      `looks_image` pula sem a variável.
- [ ] **O número sai de uma corrida que listou os alvos pelo nome.**
      `ctest -R looks` que responde `No tests were found!!!` **sai 0**, e já
      passou por verde duas vezes neste ciclo
      ([`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md),
      [`CORR-LOOKS-015`](/docs/tasks/looks/CORR-LOOKS-015.md)). Nenhum
      diretório de build do worktree lista os alvos; nesta máquina a corrida
      sai de um build **fora da árvore**, configurado com o toolchain do
      vcpkg — a receita está na tabela de gates do
      [`perfil-looks.md`](/docs/prompts/perfil-looks.md).
- [ ] Os alvos dos outros projetos continuam verdes: `ctest -R "pes2|mcr|tasks"`
      sem regressão, especialmente se a LOOKS-TASK-10 mexeu no
      `bin_archive.py`.

---

## Log de Execução

*(preencher ao executar)*
