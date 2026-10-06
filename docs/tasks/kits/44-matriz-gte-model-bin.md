---
id: KITS-TASK-44
---

# KITS-TASK-44 — Ler a matriz do GTE por seção do MODEL.BIN na partida

## Goal

Responder com a matriz que o jogo entrega ao GTE o que a KITS-TASK-43 não conseguiu responder pela geometria (CORR-KITS-071): a que peça do corpo se prendem, na partida do slot 5, a seção 93 (braçadeira) e as 95 a 102 (manga longa). Cada uma divide a matriz de uma seção do corpo, ou recebe a sua própria? O ajuste projetivo do `--attach` não decide isso: são 9 ou 10 pontos por seção contra 11 incógnitas (§4.3, "Negativa medida").

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova (`--attach-matrix SLOT`, por exemplo) que acha no código da partida as instruções que escrevem a matriz do GTE. É o mesmo gesto do `tools/looks/oracle.py --pose` na `LOOKS SET` (`ctc2` no registrador de controle 0). Ela lê a matriz e a translação carregadas antes de cada seção do `MODEL.BIN`, e agrupa as seções por matriz idêntica
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.3, o encaixe medido
- Out: manga curta contra longa. Ela pede um save state de partida com manga curta, que é decisão do usuário (§4.3). Também fica fora desenhar na janela (KITS-TASK-40)

## Done criteria

- [ ] `oracle.py --attach-matrix 5` colado no Log, sem elisão: para a seção 93 e as 95 a 102 de cada jogador, a seção do corpo cuja matriz é a mesma, ou "própria"
- [ ] Um vermelho visto: a captura deslocada de uma seção (o atraso de ponteiro que o `looks` mediu) ou uma seção do corpo trocada, e a ferramenta acusando
- [ ] A §4.3 diz o encaixe medido, com o comando
- [ ] `ctest --test-dir build -R kits`: 4/4

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 pela [CORR-KITS-071](/docs/tasks/kits/CORR-KITS-071.md), por decisão do usuário: reabrir o critério 1 da KITS-TASK-43 (a segunda contagem) com trabalho de seguimento.

As duas armadilhas do `looks` valem aqui até prova em contrário. O ponteiro de modelo numa parada nomeia a peça **anterior**. E a transformação por peça é absoluta: o jogo entrega a câmera já composta. Ver a seção do visualizador de aparência no `CLAUDE.md` e o `tools/looks/oracle.py --pose-lag`.

Recursos: emulador e save-states. O slot 5 tem cópia mestra em `work/kits-states/`.

## Log de Execução
