---
id: KITS-TASK-46
---

# KITS-TASK-46 — Medir a manga curta da figura de partida

## Goal

Medir quais seções do `MODEL.BIN` um jogador de linha de **manga curta** desenha numa partida, e em que lugar da ordem de desenho cada uma entra. A comparação é com a ordem de manga longa da KITS-TASK-44 (`cabeça 2 95 96 97 98 7 9 11 8 10 12`). A pergunta é se a manga curta são seções alternativas das mesmas peças, com as candidatas 91 e 94 (§4.3). Sem isso, o checkbox **Long sleeves** não tem o que desligar.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: o `--attach-matrix` e o `--attach` rodam num slot novo, de manga curta. Se precisar, ganham a ordem de manga curta no julgamento
  - `docs/PLAN-KITS-PY.md`: §4.3, "Manga curta contra longa"
- Out: desenhar (KITS-TASK-47)

## Done criteria

- [ ] Um save state de partida com pelo menos um time de manga curta e um capitão de manga curta na tela, dado pelo usuário, com cópia mestra em `work/kits-states/`
- [ ] `oracle.py --attach-matrix <slot>` colado no Log: a ordem de desenho de um jogador de manga curta, a de um capitão de manga curta e a do goleiro
- [ ] A regra na §4.3: qual seção de manga curta ocupa o lugar de qual seção de manga longa, e onde a braçadeira entra na manga curta
- [ ] Um vermelho visto: a seção trocada e a ferramenta acusando

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 por decisão do usuário, junto com a KITS-TASK-45. **O save state é decisão do usuário e não se improvisa** (perfil, fase 10). Sem ele, esta task fica blocked.

## Log de Execução
