---
id: MCR-TASK-11
title: "A casca Qt: janela, elenco e ficha em leitura"
type: implementação
category: ui
phase: 3
depends_on: ["MCR-TASK-10"]
fonte_de_verdade: "/docs/PLAN-MCR-PY.md §3"
status: pendente
---

# MCR-TASK-11: A UI em leitura

## Contexto

- **Referência:** [`/docs/PLAN-MCR-PY.md`](/docs/PLAN-MCR-PY.md) §3 (Regra 3) e
  §4.3.
- O upstream tem duas abas — `PLAYERS` e `FORMATION` — e uma terceira janela de
  opções que é do raspador dele, fora do escopo.
- **A UI não conhece endereço.** Ela importa `model`, `domains` e `glossary`, e
  mais nada; o `selftest` recusa o contrário.
- **Roda no `:98`.** `make mcr-98`.

---

- **Três campos têm mais valores do que o upstream deu nomes**, medido na
  MCR-TASK-08: `beard_style` e `beard_colour` guardam 3 bits (8 valores) e ele
  nomeia 7; `foot` guarda 2 bits (4) e ele nomeia 3. O índice extra **não é
  ilegal** — é anônimo. O `domains.label()` devolve `domains.UNNAMED` (`"?"`)
  nesse caso e **levanta** só quando o valor está fora da faixa do campo; a
  tela precisa distinguir as duas coisas, senão um cartão legítimo vira erro.

---

## Objetivo

Abrir um cartão e mostrar o que o núcleo já lê, sem gravar nada.

---

## Critério de conclusão

- [ ] Janela com a lista dos 23 jogadores, rotulada como o upstream (`[GK] Nome`).
- [ ] Ficha do jogador em leitura: posição, aparência, físico, os 16 atributos
      (exibidos 12..19), dorsal, pé e chuteira.
- [ ] Aba de formação desenhando os 10 de linha por X e Y — com os fatores de
      tela (`X*7`, `Y*2`) **na UI**, nunca no núcleo — e o papel de cada um.
- [ ] Nome em cp932 aparecendo correto na tela, inclusive o katakana.
- [ ] **Nenhum caminho de gravação ligado** nesta task: abrir é seguro por
      construção.
- [ ] **Toda a UI em en-US** — título de janela, aba, rótulo, cabeçalho de
      coluna, tooltip e mensagem. A regra é a §3.5 do plano e vale para o texto
      que o usuário lê, não só para o identificador.
- [ ] Captura de tela no `:98` anexada ao Log.

---

## Log de Execução

*(a preencher)*
