---
id: LOOKS-TASK-07
title: "`oracle.py` — o emulador por MCP e a rota até a tela `LOOKS SET`"
type: implementação
category: oráculo
phase: 2
depends_on: ["LOOKS-TASK-06"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §1.11"
status: pendente
---

# LOOKS-TASK-07: O oráculo, e a rota que falta

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §1.11 e
  §5.2.
- **A rota da tela de título até o menu `EDIT` não existe.** A sessão que
  levantou o plano pegou o jogo já dentro dele; escrever a rota é esta task.
- Molde pronto: as rotas nomeadas de `tools/pes2/mcp_drive.py` (`route_title`,
  `route_main_menu`, `route_edit`), que esperam pela assinatura do quadro e não
  pelo relógio.
- **Bote o disco inglês** — menus legíveis, geometria idêntica (§1.3).

---

## Objetivo

`tools/looks/oracle.py`: subir o emulador, chegar à tela `LOOKS SET` sozinho, e
oferecer as operações que as tasks 08 e 09 vão usar — ler RAM, capturar quadro,
trocar o valor de um campo.

---

## Critério de conclusão

- [ ] `route_looks()` sai da carga do disco e chega à tela `LOOKS SET`, sem
      intervenção manual, e **espera pela assinatura do quadro**.
- [ ] A rota deixa um **save state** na tela alcançada, e reusa — é o que fez a
      tentativa de PES2 cair de 2,5 min para ~40 s.
- [ ] **Círculo confirma e precisa de pelo menos 8 frames.** Com 3 o jogo não
      registra e a tela fica igual, o que parece botão errado. Fica no código,
      não em comentário solto.
- [ ] **Uma tecla de cada vez.** Nada de laço de confirmação — a regra do
      [CLAUDE.md](../../../CLAUDE.md) custou uma corrida no ciclo `wte/`.
- [ ] `verify_load()` reconfere a §5.2: RAM em `0x8011C000` e `0x8016E800` byte
      a byte igual ao disco. É a amarra entre arquivo e tela.
- [ ] Sem emulador, **pula** (77) com a mensagem dizendo o que falta.

---

## Log de Execução

*(preencher ao executar)*
