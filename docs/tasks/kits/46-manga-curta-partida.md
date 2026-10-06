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

2026-10-06. O usuário salvou o slot 6: "Noruega x Equador, mangas curtas,
início da partida, jogador 10 da Noruega é o capitão e está com a bola". A
cópia mestra está em `work/kits-states/SLPM-87056_6.sav` (sha256 começando por
`a2788f6a24cd39d9`). Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP.

**O slot 6 mede igual ao slot 5, de manga longa.**

- `--attach-matrix 6` sai 0 com as mesmas ordens do slot 5:
  `24 2 95 96 97 98 7 9 11 8 10 12`, `30 2 95 96 93 98 7 9 11 8 10 12` e
  `79 56 99 101 100 102 61 63 62 64`, e `every figure's translations within
  117 to 216 of its median (limit 500)`.
- `--sleeves 6` sai 0: `kit pages: uniform image 132, sleeves image 77`, e
  `long sleeve 64, armband 8, other 5`. Os 45 quads distintos estão no
  `/BIN/MODEL.BIN` (45 de 45), nas seções 93 e 95 a 102.
- `--attach 6` sai 0, com os jogadores desenhando
  `2 7 8 9 10 95 96 97 98` e `2 7 8 9 10 93 95 96 98`.
- A opção nova `--sleeves-image SLOT --page 576 --tag 14` lê a imagem de
  mangas da VRAM. Nos dois slots ela dá o mesmo resultado, `5551 pixel(s) of
  16384 differ from the disc, in 3 block(s)`, nos blocos (128,0)-(159,127),
  (192,0)-(251,35) e (220,25)-(228,35), e nenhum deles está nas zonas de manga
  longa (x 160 a 191).
- **A captura de tela confirma:** em `work/kits-oracle/sleeves/slots-5-6-players.png`
  (recortes de `work/looks-shots/sleeves-5.png` e `sleeves-6.png`), os
  jogadores da Noruega estão de **manga longa** nos dois states, e o capitão
  aparece com a braçadeira.

A medição não acha manga curta no slot 6, e a tela também não mostra. Pela
regra da task, o save state é decisão do usuário e não se improvisa. A task
fica **blocked** até o usuário dizer como a manga curta aparece no jogo. Pode
ser opção de tempo ou estação, pode ser uniforme de outro time, e pode ser que
o state tenha sido salvo antes de a escolha valer.

