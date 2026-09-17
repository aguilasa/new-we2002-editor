---
id: LOOKS-TASK-19
title: "`cli.py` e os quatro alvos de `ctest`"
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

- **Existe um segundo gate de disco desde 2026-09-15**, e ele não está em
  `ctest` nenhum: `python tools/looks/texture.py --check-image`, da
  [`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md). Ele pula
  com 77 sem `WE2002_LOOKS_IMAGE`, como o `looks_image` já faz. **Decidir se o
  `looks_image` passa a rodar os dois `--check-image`** — o do `modelfile.py` e
  o do `texture.py` — ou se nasce um alvo terceiro é desta task; deixá-lo fora é
  um alvo verde que não roda metade do que existe.

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
- [x] `looks_ui` **já registrado**, pela
      [`LOOKS-TASK-16`](/docs/tasks/looks/16-contratos-da-ui.md) em 2026-09-16,
      com `SKIP_RETURN_CODE 77`. Esta task **confere**, não cria — e confere
      uma coisa a mais, porque o enunciado deste item dizia
      `if(UNIX AND Python3_FOUND)` e isso está **medido como errado**: a janela
      sobe nativa nesta máquina Windows, estacionada em −32000, sem Xvfb
      nenhum. Sob `if(UNIX …)` o alvo desapareceria justamente de onde ele
      roda, e `ctest -R looks_ui` responderia `No tests were found!!!`
      **saindo zero** — a armadilha 12 outra vez. Ele entrou no mesmo
      `if(Python3_FOUND)` dos outros dois.
- [ ] **Decidir o que fazer com o `oracle.py --check-live`, que existe desde a
      [`LOOKS-TASK-07`](/docs/tasks/looks/07-oraculo-e-rota-ate-a-tela.md)** e
      hoje não é alvo nenhum. Ele sobe o emulador, carrega os dois save states,
      confere a chegada pelo quadro e compara a RAM com o disco; **pula com 77**
      sem `WE2002_LOOKS_DRIVE_IMAGE`, sem `WE2002_LOOKS_IMAGE`, sem os `.sav`
      de `work/looks-states/` ou sem o fork — os quatro conferidos antes de o
      emulador subir, desde a
      [`CORR-LOOKS-017`](/docs/tasks/looks/CORR-LOOKS-017.md). Ou vira um
      quarto alvo — e aí o título desta task e a tabela
      de gates do [`perfil-looks.md`](/docs/prompts/perfil-looks.md) passam a
      dizer quatro —, ou fica como comando de mão, e **isso fica escrito**. O
      que não pode é continuar sendo um gate que só roda quem se lembra dele,
      que é exatamente o que a
      [`CORR-LOOKS-012`](/docs/tasks/looks/CORR-LOOKS-012.md) abriu.
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
