---
id: MCR-TASK-03
title: "A fixture nomeada, o venv e o binding Qt"
type: ferramenta
category: ferramental
phase: 0
depends_on: ["MCR-TASK-01"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §4"
status: pendente
---

# MCR-TASK-03: Fixture, venv e Qt

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §4.
- **O Python desta máquina é duplo, e isso já é armadilha medida:** `python3`
  do `PATH` é o mise 3.13.13, `/usr/bin/python3` é 3.12.3, e o
  `build/CMakeCache.txt` fixou o mise. `apt install python3-pyqt6` instalaria
  para o 3.12 e ficaria **invisível** — o apt termina em verde e o `import`
  continua falhando.
- A fixture existe: `work/entrada.mcr`, 131.072 B, `BISLPM-86600WEW-OPT`, fora
  do git. Cartão de jogo é dado do jogo: **não se versiona**.

---

## Objetivo

Deixar o ambiente reproduzível e registrado, e a fixture nomeada por variável
em vez de por caminho cravado.

---

## Critério de conclusão

- [ ] `work/venv-mcr/` com **PySide6** instalado, e no Log: a versão resolvida,
      o `python -VV` do venv e o `pip freeze`. "Instalei PySide6" não é medição.
- [ ] A escolha de PySide6 sobre PyQt6 registrada com as duas razões — o Python
      duplo e a licença (LGPL × GPL, num repositório que não pode ser
      licenciado).
- [ ] `WE2002_MCR_CARD` é a variável que nomeia a fixture, e nada no código
      cravou `work/entrada.mcr`.
- [ ] Alvos `mcr` e `mcr-98` no `Makefile` da raiz, o segundo com a receita de
      `XAUTHORITY` do `:98` que os outros alvos já usam.
- [ ] Confirmado que `make fresh` **não** apaga o venv (ele remove quatro
      caminhos nomeados) e que `work/` continua no `.gitignore`.
- [ ] Uma corrida de fumaça: `work/venv-mcr/bin/python -c "import PySide6; print(PySide6.__version__)"`.

---

## Armadilhas

- **Não instale nada por `apt` para isto.** Ver o Contexto.
- **A UI roda no `:98`.** `:1` só a pedido explícito do usuário.

---

## Log de Execução

*(a preencher)*
