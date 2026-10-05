---
id: KITS-TASK-38
---

# KITS-TASK-38 — Medir as costas e o número no jogo

## Goal

Responder com medição a pergunta da §4.7: o jogo preenche a lacuna do torso em tempo de execução, (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro, com as costas e o número? Se preenche, de onde vêm os texels e onde cai cada dígito. Se não preenche, a negativa fica medida.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova (`--back SLOT`) que lê a VRAM da imagem de uniforme (576,256) nos dois retângulos e diz, por pixel, se o índice ainda é 0. O controle é o mesmo retângulo lido do TEX do disco
  - `tools/kits/selftest.py`, se a opção ganhar parte pura testável sem emulador
  - `docs/PLAN-KITS-PY.md`: §4.7 com o resultado
- Out: desenhar o número na janela (KITS-TASK-40)

## Done criteria

- [ ] `oracle.py --back 1` e `--back 2` (os dois states da `LOOKS SET`) colados no Log, com a contagem de pixels de índice diferente de 0 em cada retângulo
- [ ] Um vermelho visto: o retângulo errado (a zona dos números, por exemplo) ou o TEX trocado, e a ferramenta acusando
- [ ] Se a `LOOKS SET` não escreve ali, a task fica **blocked**, com `--unblocked-by` nomeando o save state de partida que falta. Esse state é decisão do usuário, nunca improvisado
- [ ] Se escreve: a regra (origem dos texels, posição do dígito) na §4.7, com o comando que a mede

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.7).

Recursos: emulador e save-states (fixture em `work/looks-states/`). A zona "numbers 0-9" (64,68) 60×12 é a candidata a origem. Nenhuma primitiva da `LOOKS SET` a amostra (`WHY_NUMBERS` em `tools/kits/core/zones.py`).

## Log de Execução
