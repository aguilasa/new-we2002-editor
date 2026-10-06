---
id: KITS-TASK-43
---

# KITS-TASK-43 — Medir o encaixe da braçadeira e da manga longa do MODEL.BIN

## Goal

Medir, na partida do slot 5, como o jogo põe na figura as seções do `/BIN/MODEL.BIN` que a KITS-TASK-39 achou: a seção 93, que é a braçadeira, e as 95 a 102, que são a manga longa. A pergunta é que transformação cada seção recebe e a que peça do corpo ela se prende. A outra pergunta é se a figura de partida inteira é o `MODEL.BIN`, e não o `EDT_MOD.BIN` que a aba 3D desenha. Sem essa resposta, os checkboxes **Captain armband** e **Long sleeves** da KITS-TASK-40 não têm como desenhar sem inventar geometria (§0).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova, `--attach SLOT`. Ela casa cada primitiva da lista do GPU com a seção do `MODEL.BIN` de que sai, pelos texels, como a `--sleeves` já faz. Depois lê, como o `tools/looks/oracle.py --pose` faz na `LOOKS SET`, a matriz que o GTE carrega antes de cada seção
  - `tools/kits/selftest.py`, para a parte pura nova
  - `docs/PLAN-KITS-PY.md`: §4.3 com o resultado
- Out: desenhar a braçadeira e a manga longa na janela (KITS-TASK-40)

## Done criteria

- [x] `oracle.py --attach 5` colado no Log, com duas contagens. A primeira diz quantas primitivas da figura no quadro saem do `MODEL.BIN` e quantas do `EDT_MOD.BIN`, por seção. A segunda diz, para a seção 93 e para as 95 a 102, a seção do corpo cuja matriz elas compartilham, ou a matriz própria que recebem
- [x] A regra na §4.3: qual seção do `MODEL.BIN` substitui ou acompanha qual peça da figura, e se a manga curta e a longa são seções alternativas da mesma peça. O comando que mede vai junto
- [x] Um vermelho visto: a seção trocada (a 94, ou uma do tronco) e a ferramenta acusando
- [x] Se a figura de partida não for a do `EDT_MOD.BIN`, a §4.3 diz isso e diz o que a aba 3D precisaria ler para desenhar a braçadeira e a manga longa. Essa leitura é trabalho novo, decisão do usuário

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Criada em 2026-10-05, a pedido do usuário, quando a KITS-TASK-40 chegou sem regra para nenhum dos três checkboxes.

State: `work/kits-states/SLPM-87056_5.sav`, a mesma partida da KITS-TASK-42. A seção 94 do `MODEL.BIN` fica entre a braçadeira (93) e as mangas longas (95 a 102), e não apareceu no quadro. É a primeira candidata a manga curta ou a peça trocada.

O `looks` já mediu na `LOOKS SET` que a transformação por peça é absoluta e que o ponteiro de modelo numa parada nomeia a peça anterior. As duas armadilhas estão no `CLAUDE.md`, seção do visualizador de aparência. Elas valem aqui até prova em contrário.

## Log de Execução

2026-10-06. Ambiente: `DISPLAY=:98`, `XAUTHORITY` vazio,
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`,
`WE2002_LOOKS_DRIVE_IMAGE=work/looks-disc/we2002-english.cue`, fork MCP, slot 5
restaurado de `work/kits-states/`.

**O método mudou em relação ao que a task previa.** A leitura da matriz do
GTE, como faz o `looks --pose`, pediria endereços do código de partida, que
ninguém mediu. O `--attach` mede pela geometria. Cada primitiva de kit do
quadro (8 bits, CLUT de kit) é casada com a primitiva de modelo que tem os
mesmos quatro cantos de texel, os jogadores são separados por contato de caixa
de tela, e uma câmera projetiva é ajustada aos vértices do disco contra os
pontos de tela.

**`--attach 5`**, ao vivo, exit 0:

```
  250 figure primitive(s); by the file their texels are in: MODEL.BIN only 244, EDT_MOD.BIN only 0, both 0, neither 6
  19 primitive(s) whose texels sections 2 56 all hold: left out
  6 primitive(s) whose texels sections 59 91 93 94 97 100 all hold: left out
  4 primitive(s) whose texels sections 57 95 99 all hold: left out
  MODEL.BIN sections each player draws (texels one section holds only):
    player  0 ( 47 prims, CLUT (0,487)): 2 7 8 9 10 95 96 97 98
    player  1 ( 44 prims, CLUT (0,486)): 2 7 8 9 10 93 95 96 98
    player  2 ( 44 prims, CLUT (0,486)): 2 7 8 9 10 95 96 97 98
    player  3 ( 44 prims, CLUT (0,487)): 2 7 8 9 10 95 96 97 98
    player  4 ( 43 prims, CLUT (0,487)): 2 7 8 9 10 93 95 96 98
    player  5 ( 28 prims, CLUT (0,486)): 56 61 62 63 64 99 100 101 102
  one camera fitted to a worn section alone, and to it with each other section:
    player  1 ( 44 prims) section  93,  9 point(s): alone 1.28 px; one camera with section 2 2.13 px, 98 2.67 px, 95 4.54 px
    player  4 ( 43 prims) section  93,  9 point(s): alone 0.92 px; one camera with section 2 1.99 px, 98 2.31 px, 8 3.96 px
    ...
  ok    the figure is MODEL.BIN's, and section 93 takes the place of 97
```

As linhas de grupo compartilhado vêm da mesma corrida relida com
`--frame-json work/kits-oracle/attach-5.json`, depois que essa contagem entrou
na ferramenta. A linha de origem dá o mesmo.

**As duas contagens do primeiro critério.**

- Por arquivo: 244 primitivas do `MODEL.BIN`, 0 do `EDT_MOD.BIN`, 6 de nenhum.
  Por seção, a lista acima.
- Por matriz: cada seção vestida, ajustada sozinha, erra de 0,56 a 2,18 px. A
  exceção é a 99 do goleiro, com 16,69 px. Ajustada junto com outra seção, erra
  de 1,28 a 9,00 px.
- **Nenhum par decide matriz compartilhada.** O caso mais perto é a 95 com a 2
  no jogador 1, 1,28 px contra 1,09 px sozinha, e no jogador 3 o mesmo par dá
  4,76 px. Com 9 ou 10 pontos contra 11 incógnitas, o ajuste é frouxo demais.
  É uma negativa medida, registrada na §4.3. Decidir isso pede a matriz do
  GTE.

**A regra.** A 93 entra no lugar da 97: os dois capitães, um por time
(CLUTs (0,486) e (0,487)), desenham o conjunto de um jogador comum com a 93 em
vez da 97. O `attach_judge` afirma isso. Manga curta contra longa não foi
medida, porque os dois times estão de manga longa; está na §4.3 com as
candidatas 91 e 94.

**Vermelhos vistos.**

- `--attach 5 --frame-json work/kits-oracle/attach-5.json --plant-attach` sai
  1, com `FAIL  no player draws section 94`.
- O `selftest.py` traz quatro checagens `oracle --attach`. Plantando o
  `attach_judge` sem tirar a braçadeira do conjunto, a primeira falha com
  `FAIL  oracle --attach: 93 in place of 97 holds`. O código foi restaurado.

**A figura de partida não é a do `EDT_MOD.BIN`.** A §4.3 diz isso e diz o que
a aba 3D precisaria: as seções do `MODEL.BIN` e uma pose para elas. Isso é
trabalho novo, decisão do usuário. A nota foi para a KITS-TASK-40.
- **Closed** — commit `da80383` (2026-10-06): feat(kits): oracle.py --attach: the match figure is MODEL.BIN, the armband replaces section 97
  - Files (`git show --name-status da80383`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`
    - `M docs/tasks/kits/43-medir-encaixe-mangas.md`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
