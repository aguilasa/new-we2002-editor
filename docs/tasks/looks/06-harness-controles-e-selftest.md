---
id: LOOKS-TASK-06
title: "`harness.py`, `controls.py` e `selftest.py` — o gate e os primeiros casos vermelhos"
type: implementação
category: verificação
phase: 1
depends_on: ["LOOKS-TASK-05"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.5"
status: pendente
---

# LOOKS-TASK-06: O gate e o controle negativo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.5 e
  §3.3.
- Molde pronto em `tools/mcr/`: `harness.Checker` e o `controls.Control` que
  planta **substituição literal no fonte** numa cópia da árvore e exige
  vermelho.
- *Guarda que nunca ficou vermelha é decoração.*

---

## Objetivo

`tools/looks/selftest.py` roda sem imagem, sem venv e sem display, e é o alvo
`looks_selftest`.

---

## Critério de conclusão

- [ ] `harness.py` com `Checker`: `ok` / `attempt` / `refuses` / `skip` /
      `report`.
- [ ] **O harness não se confere com ele mesmo.** O ramo de falha do `ok` é
      exercitado por um caminho que não passa pelo próprio `ok` — foi assim que
      o ciclo do `.mcr` pegou o `harness-counts-nothing`.
- [ ] `controls.py` com, no mínimo, os três controles da §5.5: trocar 24 por 20
      no tamanho de primitiva; inverter a ordem da lista de montagem; e
      (quando a Fase 3 existir) trocar uma paleta por outra.
- [ ] Substituição que casa 0 ou mais de 1 vez é control **quebrado**, não
      vermelho, e o relatório diz isso.
- [ ] As três regras de desenho da §3.3 varridas mecanicamente, com
      `os.walk` — e não `os.listdir`, que não enxerga `ui/`.
- [ ] **A regra 1 reusa o `layout.sweep_addresses()`**, que já existe desde a
      [`LOOKS-TASK-03`](/docs/tasks/looks/03-fonte-de-disco-e-layout.md) — o
      agregador não escreve um segundo varredor de endereço. Dois varredores
      da mesma regra divergem em silêncio, e o que ficar sem chamador vira
      código morto que ninguém percebe apodrecer
      ([`CORR-LOOKS-009`](/docs/tasks/looks/CORR-LOOKS-009.md)).
- [ ] O `looks_selftest` **falha** se a varredura da regra 1 achar alguma
      coisa, e o Log copia a linha com a contagem que ela imprime — `(N
      file(s), M line(s) swept)`. Varredura que não abriu arquivo nenhum tem
      de ser visível na saída, não dedutível.
- [ ] A contagem de controles é **impressa pela ferramenta**, nunca escrita em
      prosa.

---

## Log de Execução

*(preencher ao executar)*
