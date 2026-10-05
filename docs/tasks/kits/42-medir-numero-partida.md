---
id: KITS-TASK-42
---

# KITS-TASK-42 — Medir o número de camisa numa partida

## Goal

Responder ao passo 2 da §4.7 na partida do slot 5. A pergunta é se a lacuna do torso, ou outro lugar da página de kit, recebe o número de camisa. Se recebe, a task diz de onde vêm os texels de cada dígito e onde cada um cai. Na `LOOKS SET` o jogo copia as costas e não desenha número (KITS-TASK-38). Nada se sabe ainda da partida, e é essa regra que o checkbox **Number** da KITS-TASK-40 espera.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: o `--back` passa a aceitar slot de partida (`load_slot`) e uma página de kit escolhida (`--page 576|640`), com o TEX de cada página dado pelo `--slot` (Noruega `TEX_14` em (576,256), Equador `TEX_47` em (640,256)). Se o número não estiver na lacuna, ele procura na página inteira os pixels que diferem do disco
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.7 com o resultado
- Out: desenhar o número na janela (KITS-TASK-40)

## Done criteria

- [ ] `oracle.py --back 5 --page 576` e `--page 640` colados no Log: os pixels que diferem do disco na lacuna e no resto da página, e a origem de cada bloco escrito
- [ ] Se há número: a regra na §4.7, com a zona de origem de cada dígito, o retângulo onde ele cai e o comando que mede isso. O camisa 10 da Noruega dá dois dígitos, "1" e "0", e a regra tem que dizer onde cai cada um
- [ ] Se não há número na página de kit: a negativa medida na §4.7. Se o número estiver em outra página, a task diz qual, pela lista do GPU (`--sleeves` já anda essa lista)
- [ ] Um vermelho visto: o TEX trocado entre as duas páginas, ou a zona errada, e a ferramenta acusando

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

Criada em 2026-10-05, a pedido do usuário, quando a KITS-TASK-40 chegou sem regra para nenhum dos três checkboxes.

State: `work/kits-states/SLPM-87056_5.sav`, salvo pelo usuário em 2026-10-05. É Noruega × Equador, os dois de manga longa, e o state abre com o camisa 10 da Noruega, que é o capitão, com a bola. O `--slot 5` acha a Noruega (`TEX_14`) em (576,256) e o Equador (`TEX_47`) em (640,256). As páginas da partida batem só em parte com o disco: o uniforme diferiu em 2.640 de 8.192 halfwords contra o conjunto 1. Então a partida reescreve a página, e o número é o primeiro suspeito.

Um caso medido não é a regra: um número (10) e um time. Outro número, se for preciso, pede outro state, e isso é decisão do usuário.

## Log de Execução
