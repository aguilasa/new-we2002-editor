---
id: LOOKS-TASK-16
title: "`ui_check.py` — a UI julgada de fora, e o alvo `looks_ui`"
type: implementação
category: verificação
phase: 5
depends_on: ["LOOKS-TASK-15"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §4.4"
status: pendente
---

# LOOKS-TASK-16: Os contratos da UI

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §4.4 e
  §3.3.
- Molde pronto: o `tools/mcr/ui_check.py` julga a UI **de fora**, por contrato
  legível por máquina, e substitui os pontos que abririam modal.
- **A armadilha do ciclo do `.mcr` vale aqui inteira:** o `mcr_ui` passava com
  a janela sozinha quando faltava a fixture, e imprimia um `note:` que ninguém
  lia. Alvo que passa sem medir é pior do que alvo que pula.

---

## Objetivo

`tools/looks/ui_check.py` mede o que a janela realmente fez, e pula quando não
pode medir.

---

## Critério de conclusão

- [ ] O gate roda `--smoke` e `--screenshot`, e **julga o PNG**: tamanho, e que
      ele não é quadro em branco.
- [ ] Duas tuplas visivelmente diferentes produzem **imagens diferentes** — é o
      que impede o gate de passar desenhando sempre o mesmo boneco.
- [ ] Sem venv ou sem display, **pula com 77** e a mensagem nomeia o que falta.
- [ ] **Não existe caminho em que o alvo passe sem ter medido.** Se faltar
      imagem, ele pula; não passa com `note:`.
- [ ] Achado o venv por busca para cima, como o `mcr/ui_check.py` faz.

---

## Log de Execução

*(preencher ao executar)*
