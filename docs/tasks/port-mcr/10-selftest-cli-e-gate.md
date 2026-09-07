---
id: MCR-TASK-10
title: "`selftest.py`, o CLI e os três alvos de `ctest` — fecha a Fase 1"
type: ferramenta
category: ferramental
phase: 2
depends_on: ["MCR-TASK-09"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §5.2"
status: pendente
---

# MCR-TASK-10: O gate

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §4.4 e §5.2.
- O padrão do repositório: `self_check()` importável, agregado num `selftest`, e
  registro no `ctest` com `SKIP_RETURN_CODE 77` quando depende de fixture ou de
  ambiente. `tools/pes2/selftest.py` é o modelo; `savestate.py` é o exemplar do
  controle negativo.
- **A partir daqui a regressão fica vermelha sozinha**, e é a partir daqui que a
  UI pode começar sem risco.

---

## Objetivo

Fechar a Fase 1 com gate: um selftest que roda em qualquer máquina, um CLI
utilizável, e três alvos de `ctest` com faixas de custo distintas.

---

## Critério de conclusão

- [ ] `tools/mcr/selftest.py` monta um cartão sintético em memória e agrega os
      `self_check()` dos módulos — **sem depender da fixture e sem Qt**.
- [ ] As duas guardas da Regra 3: `ui/*.py` não importa `layout`/`card`/`io`, e
      `"PySide6" not in sys.modules` depois de importar o núcleo inteiro.
- [ ] `cli.py` com `info`, `dump`, `get`, `set`, `roundtrip`, `negative` e
      `check`, saída determinística.
- [ ] Três alvos em `tests/CMakeLists.txt`: `mcr_selftest` (obrigatório),
      `mcr_card` (`WE2002_MCR_CARD`, skip 77) e `mcr_ui` (venv + `:98`, skip 77).
- [ ] **Numa máquina sem venv e sem fixture**, `ctest -R mcr` reporta
      **1 passed, 2 skipped** — nunca `0 tests`, nunca erro.
- [ ] `make test` continua verde.

---

## Log de Execução

*(a preencher)*
