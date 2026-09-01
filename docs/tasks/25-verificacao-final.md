---
id: PES2-TASK-25
title: "Verificação final — o projeto contra a definição de pronto"
type: fechamento
category: verificação
phase: 6
depends_on: ["PES2-TASK-24"]
fonte_de_verdade: "/docs/PLAN-PES2-PSX.md §0 (definição de pronto)"
status: pendente
---

# PES2-TASK-25: Verificação final

## Contexto

- **Referência:** `docs/PLAN-PES2-PSX.md` §0 e §7 (entregáveis).
- **É a última task do pool.** Depois dela o projeto ou fecha e desce para
  `docs/tasks/concluidos/`, ou tem uma lista escrita do que falta.

---

## Objetivo

Medir o projeto inteiro contra o que ele prometeu, e escrever o veredito.

### Os sete entregáveis da §7

| Fase | Entregável | Estado |
|---|---|---|
| 0 | `iso.py` + round-trip + controle negativo + emulador | **feito e verde** (§5.1) |
| 1 | âncoras `OFS_*`; diff entre releases | **feito** |
| 2 | inventário de texto; contagem e ordem; **primeiro `poke` verificado** | PES2-TASK-04 |
| 3 | estrutura do registro de jogador | PES2-TASK-10 |
| 4 | estrutura de time, formação, uniforme, bandeira, ML | PES2-TASK-16 |
| 5 | `pes2_map.json` + gerador + round-trip headless | PES2-TASK-21 |
| 6 | editor | PES2-TASK-24 |

Preencher a coluna de estado com **medida**, não com "feito".

### O que fechar no repositório

- [ ] `docs/PES2-AJUSTES.md` — a §7 dele era o backlog enquanto não havia
      tasks. Com o pool cumprido, ele vira registro histórico: dizê-lo no
      cabeçalho, ou aposentar o arquivo.
- [ ] `CLAUDE.md` — a seção de PES2 diz que o projeto está **fora do pool**
      *por escolha*. Deixou de estar em 2026-09-01. Atualizar, e atualizar o
      inventário de ferramentas de `tools/pes2/` com o que as tasks
      acrescentaram.
- [ ] `docs/PLAN-PES2-PSX.md` — cabeçalho, §5 e §7, com o estado por fase.
- [ ] Mover as tasks e os dois arquivos de progresso para
      `docs/tasks/concluidos/`, **juntos** — a pasta é um conjunto fechado, e
      o `check_tasks.py` confere cada task contra o `progresso.md` que mora
      ao lado dela ([.claude/rules/tasks.md](../../.claude/rules/tasks.md)).

### O que **não** fechar sem dizer

Qualquer campo mapeado e não verificado por `poke`, qualquer lacuna
declarada no mapa, e qualquer coisa que a PES2-TASK-01 tenha deixado
bloqueada por falta de ferramenta. Projeto que fecha escondendo lacuna
custa mais caro do que projeto que fecha com a lista.

---

## Critério de conclusão

- [ ] A tabela dos sete entregáveis preenchida com medida.
- [ ] `ctest -R pes2` verde: `pes2_selftest`, `pes2_image`, `pes2_boot`.
- [ ] `python3 tools/check_tasks.py` verde.
- [ ] A conferência de links da [.claude/rules/links.md](../../.claude/rules/links.md)
      verde para o que as tasks acrescentaram.
- [ ] O que ficou aberto, listado, com o custo de cada item.

---

## Log de Execução

*(a preencher)*
