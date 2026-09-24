---
id: LOOKS-TASK-35
title: "Fechamento da v2 — gates, `make.ps1 looks` e reconciliação do plano"
type: documentação
category: fechamento
phase: 11
depends_on: [LOOKS-TASK-23, LOOKS-TASK-29, LOOKS-TASK-30, LOOKS-TASK-31, LOOKS-TASK-34, LOOKS-TASK-36, LOOKS-TASK-37, LOOKS-TASK-38, LOOKS-TASK-39, LOOKS-TASK-40]
status: pending
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.5"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
resources: [emulador, tela]
---

# LOOKS-TASK-35: Fechamento da v2

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10 inteira, e a regra da [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md): o que a
  execução muda no plano muda na seção que mudou.
- **O `.\make.ps1 looks` existe desde 2026-09-17** e abre a v1. É o alvo que o
  usuário usa, e é aqui que ele passa a abrir o que a gravação e os save
  states mostram.

---

## Objetivo

Fechar a v2: gates novos alcançáveis pelo `ctest`, o alvo do usuário abrindo a
tela `LOOKS SET` com o boneco montado, vestido e andando, e plano, perfil e
`CLAUDE.md` batendo com o disco.

---

## Critério de conclusão

- [ ] `.\make.ps1 looks` abre a tela com o boneco montado, vestido e
      andando; o `help` diz os controles.
- [ ] Os comandos novos que precisam do emulador dentro de um alvo de `ctest`
      ou decididos como comando de mão, **e isso escrito** — a pergunta que a
      [`LOOKS-TASK-19`](/docs/tasks/looks/19-alvos-de-ctest-e-cli.md) respondeu para o `--check-live`.
- [ ] `ctest -R looks` com o número copiado de uma corrida que listou os alvos
      pelo nome, numa máquina limpa e com tudo apontado.
- [ ] Cada incógnita da §10.3 com veredito: respondida com a medição, ou
      aberta com a razão e o que a destravaria.
- [ ] §0, §6 (e), (f) e (h), perfil e `CLAUDE.md` reconciliados.
- [ ] `check_tasks.py` verde e a conferência de links sem linha nova.

---

## Log de Execução

*(preencher ao executar)*
