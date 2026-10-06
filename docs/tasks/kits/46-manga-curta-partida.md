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

- [x] Um save state de partida com pelo menos um time de manga curta e um capitão de manga curta na tela, dado pelo usuário, com cópia mestra em `work/kits-states/`
- [x] `oracle.py --attach-matrix <slot>` colado no Log: a ordem de desenho de um jogador de manga curta, a de um capitão de manga curta e a do goleiro
- [x] A regra na §4.3: qual seção de manga curta ocupa o lugar de qual seção de manga longa, e onde a braçadeira entra na manga curta
- [x] Um vermelho visto: a seção trocada e a ferramenta acusando

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
- **blocked** (2026-10-06): Slot 6 (saved as short sleeves) measures and shows long sleeves: --attach-matrix 6 gives slot 5's orders, --sleeves-image 6 equals slot 5, and the screenshot shows Norway in long sleeves. Needs the user to say how short sleeves appear in the game and a state that shows them. Partial work: the oracle commit before this one.

**Destravada em 2026-10-06.** O usuário refez o state: "Eu tinha feito
errado, mas agora está certo o state". A nova cópia mestra é
`work/kits-states/SLPM-87056_6.sav`, sha256 começando por `773aed606178d96a`.

**`--attach-matrix 6 --sleeve-length short`**, ao vivo, exit 0. As linhas por
figura saíram do trecho abaixo e estão todas `own`:

```
  stops kept at work/kits-oracle/matrix-6.json (--frame-json reads them back)
  /BIN/EDT_MOD.BIN against RAM at its LOOKS SET address: 30937 byte(s) differ
  /BIN/MODEL.BIN against RAM at its LOOKS SET address: 415 byte(s) differ
  600 stop(s), 585 distinct matrices (436 distinct rotations)
  600 stop(s); what the pointers name, by count:
    MODEL.BIN:2                    44
    MODEL.BIN:3                    43
    MODEL.BIN:5                    43
    MODEL.BIN:6                    43
    MODEL.BIN:7                    43
    MODEL.BIN:9                    43
    MODEL.BIN:11                   43
    MODEL.BIN:8                    43
    MODEL.BIN:10                   43
    MODEL.BIN:12                   35
    MODEL.BIN:4                    26
    MODEL.BIN:90                   17
    MODEL.BIN:62                   9
    MODEL.BIN:64                   9
    MODEL.BIN:30                   9
    MODEL.BIN:24                   9
    MODEL.BIN:52                   9
    MODEL.BIN:42                   9
    MODEL.BIN:34                   8
    none                           8
    MODEL.BIN:79                   8
    MODEL.BIN:56                   8
    MODEL.BIN:57                   8
    MODEL.BIN:58                   8
    MODEL.BIN:59                   8
    MODEL.BIN:60                   8
    MODEL.BIN:61                   8
    MODEL.BIN:63                   8
  51 whole figure(s), 8 of them with a last piece no stop names; the matrix of a stop goes to the piece named 1 stop(s) later.  The order each figure draws, head first:
    x9   30 2 3 5 90 6 7 9 11 8 10 12
    x9   24 2 3 5 4 6 7 9 11 8 10 12
    x9   52 2 3 5 4 6 7 9 11 8 10 12
    x8   42 2 3 5 4 6 7 9 11 8 10 12
    x8   79 56 57 58 59 60 61 63 62 64
  every figure's translations within 118 to 216 of its median (limit 500)
  the worn sections of every figure, each against every other piece of it:
    figure  0, head 30   3 own, 5 own, 90 own, 6 own
    figure  1, head 24   3 own, 5 own, 4 own, 6 own
    figure  5, head 79   57 own, 58 own, 59 own, 60 own
    ...
  ok    short sleeves: every worn section has its own matrix, and section 90 is drawn where 4 is
```

Ficaram de fora as 28 linhas de contagem por seção e 45 das 51 linhas por
figura; todas as 51 dizem `own`. A primeira corrida, antes de existir o
`--sleeve-length`, saiu 1 com `FAIL  no figure draws section 93`. A regra de
manga longa não vale aqui.

**`--sleeves 6`**, exit 0: `kit pages: uniform image 176, sleeves image 4`,
`long sleeve 0, armband 4, other 0`, nas zonas "armband, short sleeve" e nas
duas de capitão de manga curta. São 3 quads distintos no `MODEL.BIN` (3 de 3),
das seções 90 e 91, e os mesmos quads deslocados um texel não estão em arquivo
nenhum.

**A regra, na §4.3.** Por posição na ordem de desenho:

- as quatro peças de braço do jogador de linha são 95 96 97 98 de manga longa
  e 3 5 4 6 de manga curta;
- a braçadeira é a 93 no lugar da 97 de manga longa, e a 90 no lugar da 4 de
  manga curta;
- o goleiro tem 99 101 100 102 de manga longa e 57 58 59 60 de manga curta.

O código guarda isso em `oracle.SLEEVE_LENGTHS`.

**Vermelhos vistos.**

- `--attach-matrix 6 --frame-json work/kits-oracle/matrix-6.json
  --sleeve-length short --plant-matrix slot` sai 1, com `FAIL  a captain draws
  2 3 5 90 6 7 9 11 8 10 12, and no figure draws it with 6 where 90 is`.
- O mesmo arquivo com `--sleeve-length long` sai 1, com `FAIL  no figure draws
  section 93`.
- No `selftest.py`, duas checagens novas de manga curta. Plantando o
  julgamento preso à 93, a segunda falha com `FAIL  oracle --attach-matrix
  --sleeve-length short: and not where 6 is`. O código foi restaurado.

Regressão do slot 5: `--attach-matrix 5 --frame-json
work/kits-oracle/matrix-5.json` sai 0 com `ok    long sleeves: every worn
section has its own matrix, and section 93 is drawn where 97 is`.
- **pending** (2026-10-06): The user re-saved slot 6 with short sleeves; --attach-matrix 6 now draws 2 3 5 4 6.
