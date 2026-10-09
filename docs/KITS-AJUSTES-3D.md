# Ajustes da aba 3D do `kits`

O ciclo `kits` está arquivado em
[docs/tasks/concluidos/kits/](/docs/tasks/concluidos/kits/progresso.md). No teste manual da aba
3D, o usuário achou cinco lacunas, que estão listadas aqui (2026-10-07). Este documento é a entrada
do ciclo seguinte. Não é plano: diz o que se pede, como a aba está hoje e o que ainda precisa ser
decidido ou medido.

Os caminhos são relativos a `tools/kits/`, e as linhas são as da HEAD em que este arquivo entrou. As
fontes de verdade do ciclo anterior são as seções do
[PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md):

- [§0](/docs/PLAN-KITS-PY.md#0), com os Não-objetivos;
- [§3.4](/docs/PLAN-KITS-PY.md#3.4), a interface;
- [§4.3](/docs/PLAN-KITS-PY.md#4.3), manga longa e braçadeira;
- [§4.7](/docs/PLAN-KITS-PY.md#4.7), as costas e o número.

## G1 — "Set" vira "Kit": Home/Away, Uniforme: Casa/Visitante

**Pedido.** O campo "Set" passa a se chamar **Kit**, com as opções **Home** e **Away**. Em pt-BR, o
campo é **Uniforme**, com **Casa** e **Visitante**. Quando o idioma troca, os tamanhos se ajustam
(ver G2).

**Hoje:**

- `set_box` em `ui/app.py:390-392`, com os dados 1 e 2.
- Os rótulos saem de `ui/i18n.py`:

  | Chave | en-US | pt-BR |
  |---|---|---|
  | `kit_set` | "Set" (`:72`) | "Conjunto" (`:132`) |
  | `set_first` | "first" (`:73`) | "titular" (`:133`) |
  | `set_second` | "second" (`:74`) | "suplente" (`:134`) |

- `retranslate` aplica os rótulos (`ui/app.py:490-491`).

**Decidido (usuário, 2026-10-07).** Não há o que medir. No futebol, o primeiro uniforme é o de casa
(mandante) e o segundo, o de visitante, e uma coisa não exclui a outra. O conjunto 1 é Home/Casa e
o 2 é Away/Visitante. Isto é convenção do domínio, não medição, e o texto deve dizer assim.

**Decidido também (usuário, 2026-10-07): interface e CLI.** O CLI usa `--set 1|2` (`cli.py:1256`) e
ganha `--kit home|away` com o mesmo efeito; o help diz que 1 é home e 2 é away. Os documentos
históricos do ciclo `kits` continuam dizendo "primeiro e segundo conjunto", porque são registro.

## G2 — Combos do tamanho da opção mais longa

**Pedido.** Todo combo mostra inteira a opção de texto mais longo do idioma em uso, e volta a se
ajustar quando o idioma muda.

**Hoje:**

- `set_box`, `figure_box`, `language_box`, `palette_box` e `zoom_box` ficam na política padrão do
  Qt, que mede o combo uma vez só, quando ele aparece pela primeira vez.
- O `retranslate` (`ui/app.py:468`, chamado pelo `language_changed` em `:504`) só faz
  `setItemText`. Nada é medido de novo.
- O único combo com `AdjustToContents` é o `image_box` (`ui/app.py:325-331`). O comentário em
  `:326-327` já descreve exatamente esse defeito, que só foi corrigido ali.
- O `tag_box` usa `setMinimumContentsLength(18)`.

**A verificação deve prever:**

- uma captura nas duas línguas, com o rótulo mais longo de cada combo sem corte;
- uma planta que tira o ajuste e deixa o caso vermelho.

## G3 — Sem "match player": só "player" e "goalkeeper"

**Pedido.** O seletor de figura passa a ter só **player** e **goalkeeper**. A figura de partida
sai da interface. Do trabalho de "match player", só o **conhecimento medido** pode ser usado.

**Antes da K3D-TASK-10** (o estado que motivou o pedido):

- O `figure_box` tem três itens (`ui/app.py:393-398`), e o terceiro é `MATCH_FIGURE = 2` (`:68`).
- Jogador e goleiro vêm do `EDT_MOD.BIN`, montados por `scene_of` (`core/figure.py:84-104`).
- A figura de partida é o `MODEL.BIN` inteiro, na pose `core/match_pose.json`, montado por
  `match_scene` (`core/figure.py:250-333`).
- Marcar Captain armband ou Long sleeves no jogador **troca** o desenho para a figura de partida
  (`match_drawn`, `ui/app.py:576-581`).

**Medido no ciclo anterior, e que pode ser aproveitado** (§4.3; KITS-TASK-43 a 47):

- seção 93: a braçadeira de manga longa, no lugar da 97;
- seção 90: a braçadeira de manga curta, no lugar da 4;
- seções 95-98: braços de manga longa do jogador de linha;
- seções 3, 5, 4 e 6: braços de manga curta do jogador de linha (`LONG_TO_SHORT`,
  `core/figure.py:188`);
- seções 99-102 e 57-60: braços do goleiro, longos e curtos (`SLEEVE_LENGTHS`,
  `core/figure.py:177-182`);
- a matriz de GTE de cada peça e a pose medida.

**Era a decisão central do ciclo, e a K3D-TASK-07 a mediu (abaixo).** Como vestir a figura do `EDT_MOD.BIN` com geometria
medida do `MODEL.BIN` sem remapear UV à mão, o que o §0 proíbe. Há duas saídas:

- transplantar as seções do `MODEL.BIN` para a figura, com matriz medida;
- medir se o `EDT_MOD.BIN` tem peça equivalente.

As duas pedem medição antes de código. **Decidido (usuário, 2026-10-07): medir primeiro.** Uma
task de investigação compara as duas figuras e escreve a regra aqui; a implementação depende dela.

**Medido (K3D-TASK-07, 2026-10-08): transplante, sem peça equivalente.** Cada seção de manga e de
braçadeira do `MODEL.BIN` entra no lugar de uma peça de braço do `EDT_MOD.BIN` e é desenhada com a
matriz e o lugar que a figura dá a essa peça. A tabela é `ARM_PIECES` de `tools/kits/core/figure.py` (desde a K3D-TASK-10; o `oracle.py` a importa), e
quem a mede e afirma é:

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --edt-arms
```

```text
edt-arms: /BIN/MODEL.BIN and /BIN/EDT_MOD.BIN
  upper arm a EDT_MOD.BIN sections 1 12, posed alike by name
  upper arm b EDT_MOD.BIN sections 2 13, posed alike by name
  forearm a   EDT_MOD.BIN sections 3 14, posed alike by name
  forearm b   EDT_MOD.BIN sections 4 15, posed alike by name
  section   3 -> upper arm a (nearest EDT section  1 at 5.6, other part 8.2), frame offset 0.8 (+0.1,+0.8,-0.2)
  section   4 -> upper arm b (nearest EDT section  2 at 5.6, other part 8.2), frame offset 0.8 (+0.1,+0.8,+0.2)
  section   5 -> forearm a   (nearest EDT section 14 at 3.6, other part 10.9), frame offset 0.7 (-0.4,+0.6,+0.1)
  section   6 -> forearm b   (nearest EDT section 15 at 3.6, other part 10.9), frame offset 0.7 (-0.4,+0.6,-0.1)
  section  14 -> upper arm a (nearest EDT section 12 at 6.0, other part 8.5), frame offset 0.9 (+0.6,+0.3,+0.6)
  section  15 -> upper arm b (nearest EDT section 13 at 6.1, other part 8.5), frame offset 0.8 (+0.4,+0.3,-0.6)
  section  16 -> forearm a   (nearest EDT section 14 at 5.1, other part 12.6), frame offset 1.2 (+0.9,-0.6,-0.6)
  section  17 -> forearm b   (nearest EDT section 15 at 5.1, other part 12.6), frame offset 1.2 (+0.9,-0.6,+0.6)
  section  57 -> upper arm a (nearest EDT section  1 at 5.6, other part 7.9), frame offset 1.8 (+1.6,+0.8,+0.4)
  section  58 -> forearm a   (nearest EDT section  3 at 4.3, other part 13.5), frame offset 1.8 (-0.2,+1.8,+0.4)
  section  59 -> upper arm b (nearest EDT section  2 at 5.5, other part 8.2), frame offset 1.2 (+0.9,+0.8,-0.4)
  section  60 -> forearm b   (nearest EDT section  4 at 4.3, other part 13.5), frame offset 1.8 (-0.2,+1.8,-0.4)
  section  90 -> upper arm b (nearest EDT section  2 at 5.6, other part 8.2), frame offset 0.8 (+0.1,+0.8,+0.2)
  section  92 -> upper arm b (nearest EDT section 13 at 6.1, other part 8.5), frame offset 0.8 (+0.4,+0.3,-0.6)
  section  93 -> upper arm b (nearest EDT section 13 at 6.1, other part 8.5), frame offset 0.8 (+0.4,+0.3,-0.6)
  section  95 -> upper arm a (nearest EDT section 12 at 6.1, other part 8.5), frame offset 0.8 (+0.4,+0.3,+0.6)
  section  96 -> forearm a   (nearest EDT section 14 at 3.5, other part 11.1), frame offset 0.8 (+0.3,+0.7,-0.3)
  section  97 -> upper arm b (nearest EDT section 13 at 6.1, other part 8.5), frame offset 0.8 (+0.4,+0.3,-0.6)
  section  98 -> forearm b   (nearest EDT section 15 at 3.5, other part 11.1), frame offset 0.8 (+0.3,+0.7,+0.3)
  section  99 -> upper arm a (nearest EDT section  1 at 5.6, other part 7.9), frame offset 1.8 (+1.6,+0.8,+0.4)
  section 100 -> upper arm b (nearest EDT section  2 at 5.5, other part 8.2), frame offset 1.2 (+0.9,+0.8,-0.4)
  section 101 -> forearm a   (nearest EDT section 14 at 4.1, other part 12.8), frame offset 1.8 (-0.3,+1.8,+0.3)
  section 102 -> forearm b   (nearest EDT section 15 at 4.1, other part 13.1), frame offset 1.9 (-0.6,+1.8,-0.3)
  ok    every sleeve and armband section is in its EDT_MOD.BIN piece's frame (offset 1.9 at most, slack 3.0)
```

O que a saída diz:

- **Não há peça equivalente no `EDT_MOD.BIN`.** A distância média ao vértice mais próximo da peça
  mais perto fica entre 3,5 e 6,1, nunca 0: as peças de braço do `EDT_MOD.BIN` são outra malha. Nenhuma
  delas é a braçadeira, que só existe no `MODEL.BIN` (90 e 93).
- **A seção do `MODEL.BIN` está no referencial da peça.** A translação que melhor deita cada
  seção sobre a peça que a regra lhe dá (`ARM_PIECES`, não a mais próxima) fica entre 0,7 e 1,9
  unidade (`FRAME_SLACK` 3,0). Por isso a matriz certa para desenhá-la é a da própria peça, sem
  matriz nova. Até a [CORR-K3D-013](/docs/tasks/kits-3d/CORR-K3D-013.md) o ajuste corria contra a
  peça mais próxima, e aí um resíduo pequeno só dizia "está sobre alguma peça de braço": um braço
  movido 20 em y assentava na outra parte com 2,0 a 2,2 e passava.
- **A parte (braço ou antebraço) é a peça mais perto.** A outra parte fica sempre mais longe
  (coluna "other part"). **O lado (a ou b) é o sinal do z médio da seção.** As seções vêm em pares
  espelhados em z, e por isso a distância não decide o lado.
- **As duas figuras recebem a mesma pose por peça de braço — por construção, não por medição**
  ("posed alike by name"). As seções 1 e 12, 2 e 13, 3 e 14, 4 e 15 têm o mesmo nome em `pieces.py`,
  e o `scene.pose` dá a cada seção a transformação do nome dela (`tools/looks/scene.py`, o laço sobre
  `piece_names`). A conferência compara essa tabela com ela mesma e não pode imprimir "posed apart".
  Que o jogo pose a seção 12 do goleiro como a 1 do jogador é suposição herdada do ciclo `looks`, não
  medida aqui; medir pede a matriz do GTE por peça de cada figura, lida do jogo
  ([CORR-K3D-012](/docs/tasks/kits-3d/CORR-K3D-012.md)). O braço longo cabe melhor no braço do
  goleiro (12 e 13); no jogador, ele vai no slot de mesmo nome (1 e 2), com a mesma matriz.
- **Concorda com a ordem medida no jogo** (`SLEEVE_LENGTHS`, `LONG_TO_SHORT`). 95→3 e 97→4 caem nos
  mesmos `upper arm a` e `upper arm b`; 96→5 e 98→6 nos mesmos antebraços. A braçadeira (93 no lugar
  da 97, 90 no lugar da 4) cai em `upper arm b`, o braço que ela substitui. No goleiro, 99/101/100/102
  caem nas peças de 57/58/59/60.

O controle `--plant-edt-arms` move todo braço do `MODEL.BIN` 8 unidades em x antes de medir. Toda
seção continua com a mesma peça mais próxima, e a corrida sai 1 só pelo referencial: 23 linhas
`FAIL`, todas `units out of` (18 antes de a K3D-TASK-11 somar as cinco seções do goleiro; até a CORR-K3D-013 o controle era 20 em y, que trocava a peça mais
próxima e saía com 21 `FAIL`). No catálogo do `controls.py`, `oracle-arm-side-flipped` e
`oracle-arm-frame-blind` derrubam os casos sintéticos do `selftest.py`.

**O que ficou para a K3D-TASK-10:** substituir a peça inteira pela seção do `MODEL.BIN`, ou
desenhar a braçadeira por cima da malha do `EDT_MOD.BIN`. A regra diz onde a seção vai e com que
matriz; ela não diz qual das duas malhas aparece.

**Decidido e feito (K3D-TASK-10, 2026-10-08): a peça inteira é trocada, e a figura de partida sai
da interface.** Isto reabre a decisão da KITS-TASK-47, que tinha posto a figura de partida no
seletor e trocava o desenho para ela ao marcar Captain armband ou Long sleeves.

- **O seletor tem dois itens:** jogador e goleiro, os dois do `EDT_MOD.BIN`. O `match_scene`
  continua no núcleo, porque o `oracle.py --match-silhouette` o usa; a janela não o chama.
- **A troca da peça:** marcar as caixas faz o `figure.dressed_scene` tirar do jogador as peças de
  braço que o `figure.arm_dress` nomeia e pôr no lugar a seção do `MODEL.BIN`, com a matriz e o lugar
  que a pose dá àquela peça. O `arm_dress` lê só `ARM_PIECES`, `LONG_TO_SHORT` e `SLEEVE_LENGTHS`:
  - manga longa: 95, 96, 97 e 98 nos quatro braços;
  - braçadeira: 93 (manga longa) ou 90 (manga curta) no `upper arm b`;
  - manga curta sem braçadeira: o braço do próprio `EDT_MOD.BIN`.
- **Por que trocar, e não sobrepor:** a 90 e a 93 têm os vértices da 4 e da 97, ou seja, são o
  braço inteiro com outros texels, não uma faixa. Desenhada por cima da malha do `EDT_MOD.BIN`, a
  braçadeira brigaria com ela no z-buffer, as duas superfícies quase coincidentes.
- **Medido no `kits_ui`** (TEX_14, de costas):
  - a silhueta do jogador com braçadeira, com manga longa ou com as duas cobre a silhueta sem as
    caixas em 0,959 a 0,962 (`SAME_FIGURE` 0,90);
  - com a figura de partida no lugar (a planta), 0,745;
  - com manga longa, a braçadeira muda 369 px numa caixa de 30×19 no braço.
- **A cópia das costas vale só para a imagem do uniforme:** o `numbered_scene` deixa de pintar a
  imagem das mangas, que as seções do `MODEL.BIN` amostram.
- **O goleiro ficou para a K3D-TASK-11:** `DRESSED_FIGURES` tinha só o jogador. A braçadeira do
  goleiro (92, G4) entrou lá (abaixo).

**Estendido (K3D-TASK-11, 2026-10-09): o goleiro desenhado do torso 13.** As seções 14, 15, 16 e 17
e a braçadeira 92 (G4) entraram em `ARM_PIECES`, e o mesmo `--edt-arms` as mede (saída acima). As
cinco caem nas peças de braço do goleiro do `EDT_MOD.BIN` (12 a 15), com offset de 0,8 a 1,2:
14→`upper arm a`, 15 e 92→`upper arm b`, 16→`forearm a`, 17→`forearm b`. É a mesma ordem da 95 a
98, e a 92 cai onde a 15, cujos vértices ela tem.

## G4 — Number, Captain armband e Long sleeves em qualquer combinação, nas duas figuras

**Pedido.** As três caixas valem para **player** e **goalkeeper** e combinam livremente: nenhuma,
uma, duas ou as três ao mesmo tempo.

**Hoje** (`dressings()` em `ui/app.py`; desde a K3D-TASK-10 a figura é sempre a do `EDT_MOD.BIN`, G3;
o goleiro desde a K3D-TASK-11):

| Caixa | Jogador | Goleiro |
|---|---|---|
| Number | funciona, com as outras caixas ou sem elas | funciona, com a braçadeira ou sem ela |
| Captain armband | funciona: a 90 ou a 93 no `upper arm b` (`figure.arm_dress`) | funciona: a 92 no `upper arm b` |
| Long sleeves | funciona: 95-98 nos quatro braços | marcada e desligada, com `long_keeper`: ele só usa manga longa |

Antes da K3D-TASK-10, o Number era recusado no jogador quando a braçadeira ou a manga longa
trocavam o desenho para a figura de partida (`number_off`), e só essas duas combinavam entre si.
Antes da K3D-TASK-11, a braçadeira ficava desligada no goleiro (`armband_off`) e a manga longa,
escondida.

**Era o que estava em aberto** (os três itens foram fechados; ver o fim desta seção):

- A braçadeira do goleiro **foi medida pela K3D-TASK-08** (abaixo). Antes, não havia medida: `SLEEVE_LENGTHS` lista os braços do goleiro (99-102 e
  57-60), mas nenhuma braçadeira para ele. **Decidido (usuário, 2026-10-07): medir no emulador.** Se
  faltar um save state de goleiro capitão, a task fica blocked até o usuário gravar um.
- O pedido **reabre uma decisão** da KITS-TASK-40, a de esconder a manga longa no goleiro. A mudança
  precisa ser registrada como decisão nova, com data.
- O Number junto com a braçadeira ou a manga longa depende de G3: em qual torso o painel é
  montado.

**A verificação deve prever** as oito combinações nas duas figuras. Cada caixa tem de mudar a
captura, e cada uma precisa de uma planta que a ignore e fique vermelha.

**Medido (K3D-TASK-08, 2026-10-08): a braçadeira do goleiro de manga longa é a seção 92, no lugar da
15** (a 92 desenhada é medida; o "no lugar da 15" é inferido dos vértices e dos texels, ver abaixo). Medido no slot 7 (`work/kits-states/SLPM-87056_7.sav`): Brasil x China, e Marcos, goleiro e
capitão do Brasil, está com a bola nos pés e de manga longa. Nesse quadro, o jogo desenha o goleiro
com outra família de seções do `MODEL.BIN`, não a dos slots 5 e 6 (torso 56, braços 99-102 ou
57-60): torso 13, braços 14 16 15 17, pernas 18-21 e cabeça 34. A tabela é `KEEPER_ARMBANDS` de
`tools/kits/oracle.py`, e quem a mede e afirma é:

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= \
  python3 tools/kits/oracle.py --keeper-armband 7
```

Lida de volta das paradas que essa corrida guardou (`--frame-json work/kits-oracle/matrix-7.json`):

```text
  stops read from work/kits-oracle/matrix-7.json, no emulator
  600 stop(s); 23 whole and 4 cut figure(s) opened at section 13; the whole ones in the order:
    x23  34 13 14 16 92 17 18 20 11 19 21 12
  every whole figure's translations within 153 to 184 of its median (limit 500)
  section 92 has section 15's vertices; its texels touch: armband, short sleeve (goalkeeper), short sleeve, left, captain (goalkeeper), short sleeve, left, captain, under the armband (goalkeeper), shoulder, second (goalkeeper)
  section 15 is drawn by 0 of these 27 figure(s); its texels touch: shoulder, second (goalkeeper), sleeve, shoulder to elbow (goalkeeper)
  not drawn here: section 91 has the mirrored vertices of goalkeeper arm 57; its texels touch: armband, short sleeve (player), short sleeve, left, captain (player), short sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 94 has the vertices of goalkeeper arm 59; its texels touch: armband, long sleeve (player), long sleeve, left, captain (player), long sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 91 has the mirrored vertices of goalkeeper arm 99; its texels touch: armband, short sleeve (player), short sleeve, left, captain (player), short sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 94 has the vertices of goalkeeper arm 100; its texels touch: armband, long sleeve (player), long sleeve, left, captain (player), long sleeve, left, captain, under the armband (player), shoulder, second (player)
  ok    the goalkeeper opened at section 13 draws section 92 in place of 15
```

O que a saída diz:

- **A 92 entra no lugar da 15 — inferido, não visto trocar.** Nas 23 figuras inteiras, o goleiro
  desenha a 92 na quinta posição, onde fica o `upper arm b`, e nenhuma das 27 desenha a 15. A 92 tem os
  vértices da 15, vértice por vértice: é o mesmo braço com outros texels, como a 93 em relação à 97 e a
  90 em relação à 4 (G3). Os texels dizem o resto: a 92 toca as zonas de capitão do goleiro, a 15 só
  `shoulder, second` e `sleeve, shoulder to elbow`. O "no lugar da 15" se apoia nesses dois fatos;
  nenhum goleiro da família 13 desenhando a 15 foi visto, porque o slot 7 só tem o goleiro capitão
  nessa família, e por isso o `keeper_armband_judge` não exige a ordem simples como o
  `matrix_judge` faz ([CORR-K3D-015](/docs/tasks/kits-3d/CORR-K3D-015.md)). Pela regra de G3, a 92 vai
  no `upper arm b` da figura do `EDT_MOD.BIN`.
- **Os texels da 92 são as linhas de capitão do goleiro** na imagem das mangas, as zonas de
  `zones.py` marcadas como goleiro: `short sleeve, left, captain`, `armband, short sleeve` e
  `… under the armband`. Os nomes dessas zonas, que vêm do Superpack, dizem "short sleeve", mas o
  goleiro medido usa manga longa.
- **Cada peça tem matriz própria**, e as translações de cada figura inteira ficam entre 153 e 184 da
  mediana (limite 500). As 4 cortadas (a última peça de um quadro, sem parada que a nomeie) ficam fora
  da ordem e da faixa; até a [CORR-K3D-014](/docs/tasks/kits-3d/CORR-K3D-014.md) a saída as contava como
  inteiras ("27 whole") e a faixa ia a 196.

O controle `--plant-keeper-armband` espera a 103, que também tem os vértices da 15, e a corrida sai 1 com
`FAIL  no figure opened at section 13 draws section 103`: é o desenho que decide, não a geometria. No
catálogo do `controls.py`, `oracle-keeper-armband-unasked` derruba o caso sintético do `selftest.py`.

**O goleiro só tem manga longa neste jogo** (usuário, 2026-10-08). Por isso não há braçadeira de
manga curta para medir, e na figura do `EDT_MOD.BIN` a braçadeira do goleiro é a 92 no `upper arm b`,
com ou sem a caixa Long sleeves. As seções 57-60 de `SLEEVE_LENGTHS["short"]` são as que o slot 6
desenhou num goleiro de partida em que os jogadores de linha usavam manga curta (KITS-TASK-46). O
"short" ali é o comprimento da manga do jogador de linha, não do goleiro.

**Não visto, e fora da regra:** o goleiro capitão da família dos slots 5 e 6 (torso 56). No slot 7, o
goleiro com a bola é desenhado pela família 13. Pela geometria, a saída lista dois candidatos que
nenhum quadro mostrou desenhados (`not drawn here`):

- a 91, espelho da 57/99, cujos texels tocam as linhas de capitão de manga curta do jogador;
- a 94, com os vértices da 59/100, cujos texels tocam as linhas de capitão de manga longa do jogador.

A regra vale para o caso medido. Se um dia aparecer um state do goleiro capitão na família 56, ele é
medido pelo mesmo `--keeper-armband`, com uma entrada nova em `KEEPER_ARMBANDS`.

**Decidido e feito (K3D-TASK-11, 2026-10-09): as três caixas valem nas duas figuras.** Isto reabre a
decisão da KITS-TASK-40, que escondia a manga longa no goleiro e desligava a braçadeira nele.

- **A braçadeira do goleiro** é a 92 no `upper arm b` do goleiro do `EDT_MOD.BIN`, pela regra de G3
  (`--edt-arms` mede a 92 nessa peça com offset 0,8). O `figure.arm_dress` a lê de
  `KEEPER_ARMBAND`, e o `oracle.py` usa a mesma constante em `KEEPER_ARMBANDS`. Os outros braços do
  goleiro continuam os dele, que já são de manga longa.
- **O Long sleeves do goleiro aparece marcado e desligado,** com a frase `long_keeper` ("o goleiro
  não usa outra"). É a decisão do usuário de 2026-10-08 (acima): não há manga curta de goleiro para
  desenhar. O núcleo recusa `sleeves="short"` no goleiro, e `sleeves=None` quer dizer a manga própria
  da figura (curta no jogador, longa no goleiro). Voltando ao jogador, a caixa volta ao que estava.
- **Por isso as combinações são 8 no jogador e 4 no goleiro** (Number × braçadeira), não 8 × 2: a
  terceira caixa do goleiro não tem o que mudar. O `kits_ui` mede assim, de costas (TEX_14):

  ```text
  figure 0 Number at least 1197 px, figure 0 Captain armband at least 315 px, figure 0 Long sleeves at least 3293 px, figure 0: 8 combinations, figure 1 Number at least 1196 px, figure 1 Captain armband at least 477 px, figure 1: 4 combinations
  ```

  O número é o menor efeito da caixa entre as combinações das outras. Cada caixa tem uma planta
  vermelha: `Number ignored`, `Long sleeves ignored`, `armband never put on` e `goalkeeper's armband
  ignored`. As duas da caixa do goleiro, `goalkeeper's Long sleeves box left on` e `… left
  unticked`, também ficam vermelhas.
- **A braçadeira do goleiro muda só o braço:** 740 px numa caixa de 32×61, com 353 px da cor da
  faixa, medido em TEX_A4. Em TEX_14 a faixa do goleiro tem o cinza da camisa (57,57,57), e a tinta
  não teria o que separar.

## G5 — Figura inteira em qualquer giro

**Pedido.** Em qualquer posição de giro, o jogador aparece completo. Hoje as costas e outras partes
não aparecem.

**Hoje** (estado antes da K3D-TASK-05; os dois itens que ela mudou dizem o que mudou). O que se
sabia de por que falta pedaço:

- **Lacuna do torso.** O torso amostra (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro
  (`core/zones.py:194-196`). Essa área é transparente no TEX.
- **A cópia das costas é medida; antes da K3D-TASK-05 era condicional.** O jogo copia a "shirt
  back" para essa lacuna: (44,6) no jogador e (108,6) no goleiro (`BACK_COPY`,
  `core/figure.py:357`; medido na §4.7). Até a K3D-TASK-05 a cópia dependia de Number marcado e
  nunca acontecia na figura de partida; desde ela o `scene_of` a aplica sempre, e o
  `api.numbered` (`ui/app.py:629-632`) só pinta os dígitos.
- **Texel transparente deixa ver o fundo.** As superfícies são desenhadas em RGBA
  (`ui/figure_view.py:64-65`), então o que é transparente mostra o que está atrás.
- **Ordem de desenho.** O `figure_view` não descarta faces. Ele ordena os triângulos pela
  profundidade média de cada um (`ui/figure_view.py:97-100`), o que pode inverter peças que se
  cruzam.
- **Triângulos perdidos.** Um triângulo com transformação degenerada é pulado sem aviso
  (`ui/figure_view.py:119-121`).
- **A dica da aba explicava o vazado**, escrita sob a decisão de 2026-10-05 (KITS-TASK-37) de
  desenhar fiel aos dados. A K3D-TASK-05 a reescreveu: hoje (`figure_hint`, `ui/i18n.py:79-82`)
  ela diz que a lacuna do torso é desenhada com a cópia das costas que o jogo faz.

**Em aberto.** Aplicar sempre a cópia das costas é regra medida do jogo, não invenção. O resto
precisa de uma ferramenta que, por ângulo, conte o que falta na figura: texel transparente, ordem de
profundidade e triângulo pulado. Só depois disso se escolhe o conserto. **Decidido (usuário,
2026-10-07):** a cópia das costas passa a valer sempre, e uma ferramenta conta por ângulo o que
ainda falta; o ciclo conserta o que ela achar.

**Decisão nova, datada (usuário, 2026-10-07), que substitui a de 2026-10-05 (KITS-TASK-37).** As
costas deixam de sair vazadas: toda figura da `LOOKS SET` recebe a cópia das costas (`BACK_COPY`),
com ou sem Number, porque é o que o jogo faz (§4.7 do PLAN-KITS-PY). Nenhum outro texel foi
inventado.

**Feito (K3D-TASK-05, 2026-10-07).** O `scene_of` (`core/figure.py`) aplica a cópia sempre, e o
Number só pinta os dígitos por cima. A contagem é feita pelo comando abaixo, de 15 em 15 graus nas
duas figuras do TEX_00, kit 1, com Number desmarcado:

```
WE2002_LOOKS_IMAGE=<japonês> python3 tools/kits/cli.py holes <japonês> --tag 00 --top 60
```

Ela dá **0 px vindos da lacuna do torso em todo giro**. Antes eram 3.853 px no jogador e 3.857 no
goleiro, de costas. O `kits_ui` afirma isso, e a planta que tira a cópia sem Number deixa a lacuna
à vista em 42 dos 48 giros.

**O que ainda falta, com a causa:**

| Tipo | Jogador, px por giro | Goleiro, px por giro | Causa |
|---|---|---|---|
| `transparent` | 0 a 30 | 0 a 13 | Texel transparente do próprio TEX no colarinho. Nas zonas: `shirt front, collar` (só no jogador) e as duas `collar tip` (nas duas figuras). Nas lacunas da KITS-TASK-16: `collar, between its tips` (nas duas figuras) e `collar, the notch between the shoulders` (só no goleiro). É o decote, e é dado do TEX, não buraco do desenho. |
| `skipped` | 108 a 514 | 203 a 423 | O triângulo tem UV sem área: um canto repetido, ou os três colineares. A vista (`ui/figure_view.py:119-121`) não acha transformação afim e pula o triângulo. A definição do tipo é exatamente essa. |
| `misordered` | 124 a 427 | 146 a 418 | A vista pinta de trás para frente pela profundidade média de cada triângulo (`ui/figure_view.py:97-100`). Onde seções vizinhas se cruzam, o triângulo mais próximo é pintado antes de outro que fica atrás dele. |

`skipped` e `misordered` eram do desenho que o `ui/figure_view.py` fazia. **Consertados em G6**
(K3D-TASK-13 e 14, 2026-10-08): a vista passou a mostrar o desenho do núcleo (`core/raster.py`),
com profundidade por pixel e UV interpolado a partir da tela. Agora o mesmo `cli.py holes` dá
`skipped 0` e `misordered 0` nos 48 giros. Os números da tabela acima são de antes dessa troca, e
as linhas do `figure_view.py` que ela cita não existem mais.

## G6 — Desenho com profundidade por pixel

**Pedido (teste manual do usuário, 2026-10-08).** De costas, a bermuda do jogador fica incompleta
na perna direita, entre a nádega e a camiseta. Do lado esquerdo, na junção da bermuda com a
camiseta, há trechos sem textura.

**Medido (2026-10-08)** com o modelo do `cli.py holes` (TEX_00, kit 1, jogador, yaw 0). Os números
por seção saíram de uma sonda descartável que só lê; o total por tipo é o que o `cli.py holes`
imprime.

- **Nádega direita / camiseta:** são os `skipped` da seção 5 (bermuda). Os triângulos têm UV
  degenerado, com um canto repetido ou os três colineares, como `(56.5,30.5) (53.5,31.5)
  (56.5,30.5)`. A vista não acha a afim textura→tela (`ui/figure_view.py:119-121`), pula o
  triângulo, e o fundo aparece.
- **Cintura esquerda e joelho:** são os `misordered`. A vista ordena pela profundidade média de
  cada triângulo (`ui/figure_view.py:97-100`), e uma peça de trás sai pintada por cima de outra da
  frente: a seção 7 sobre a 5, e uma linha na cintura entre as seções 0, 1, 6 e 24.
- **Rachaduras de geometria** não são a causa: no jogador, nenhum pixel fechado dentro da silhueta
  fica sem triângulo.

**Decidido (usuário, 2026-10-08):**

- **Profundidade por pixel (z-buffer).** Em cada pixel vence o triângulo mais próximo. Isso diverge
  da ordem do jogo (a tabela de ordem do PS1), mas o jogo só mostra a figura de frente, e o pedido
  é a figura inteira em qualquer giro.
- **O rasterizador fica no núcleo.** O `core` desenha a figura com z-buffer, UV interpolado por
  pixel a partir da tela e texel mais próximo, sem suavização. A interpolação a partir da tela
  também cobre o triângulo de UV degenerado, como a GPU do PS1 faz. Texel transparente não escreve
  cor nem profundidade. A vista só mostra a imagem pronta por QPainter, e a contagem do
  `cli.py holes` usa o mesmo código, o que acaba com a diferença entre modelo e vista. Continua em
  software. Isto refina a decisão "3D em QPainter por software" (§3.4 do PLAN-KITS-PY).

**Pedido também (usuário, 2026-10-08):** este trabalho vem antes de G3 e G4.

## G7 — Tela EDIT PL. NUM: o jogo desenhando o número e o giro

**Relato (usuário, 2026-10-09).** Em EDIT MODE → EDIT PL. NUM → uma seleção, o jogo abre a tela
"背番号エディット" (captura do usuário em `/home/ingmar/Pictures/2026-10-09_14-34.png`): a lista
dos 23 do time à esquerda, um boneco 3D no painel central e a grade de números à direita. O
boneco abre **de frente**; ao confirmar um jogador ele **gira para as costas** e fica de costas com
o **número à mostra**. O state está no **slot 8** do DuckStation (Brasil; Marcos, GK nº 1,
selecionado e de frente). A cópia mestra vai para `work/kits-states/SLPM-87056_8.sav`.

**O que a tela pode responder, e que hoje vem de fonte pior:**

- **o número nas costas desenhado fora de partida**, com o painel 20×24. Hoje a regra do número
  vem só do slot 5, uma partida (§4.7 do PLAN-KITS-PY, KITS-TASK-42);
- **o giro frente→costas**, com matriz por quadro. A aba gira por conta própria; o jogo nunca foi
  medido girando uma figura parada;
- **uma pose parada**, de frente e de costas, das duas figuras. A `LOOKS SET` só dá a caminhada;
- **qual família de modelo** a tela usa — `EDT_MOD.BIN`, como a `LOOKS SET`, ou o `MODEL.BIN` de
  partida (torso 2, 56 ou 13) — e com que kit, paleta e mangas, no goleiro e no jogador de linha.
  Se for `MODEL.BIN` com o goleiro em 56, esta tela pode ser onde a 91 ou a 94 (G4, "não visto")
  aparecem.

**Decidido (usuário, 2026-10-09): investigar primeiro, numa task só.** A task mede e escreve o
que achou, inclusive as negativas; o que virar desenho na aba vira task nova, a partir do medido.

**O que a task mede.** Cada número sai de uma opção versionada do `oracle.py`,
`--edit-number SLOT [--player ROW]`, com `--plant-edit-number` como controle:

1. **Carga e captura** do slot 8 pela cópia mestra (`load_slot`), com captura da tela.
2. **Família do modelo e ordem das seções, de frente:** as paradas na carga de matriz
   (`matrix_stops`), cortadas nas raízes do `MODEL.BIN` (2, 56, 13) e nas do `EDT_MOD.BIN`, com a
   ordem `xN …` por figura, como o `--attach-matrix` imprime.
3. **Kit, paleta e mangas:** a página de uniforme em VRAM e a linha de CLUT (486 jogador, 488
   goleiro); as seções de braço na ordem dizem a manga e se há braçadeira (90, 93, 92 — ou 91, 94).
4. **Pose parada e câmera:** a matriz por peça da parada de frente, em `work/kits-pose/`, e a
   câmera por `camera_from_pieces`.
5. **O giro:** confirmar o jogador e colher as paradas quadro a quadro até a figura parar de
   costas — quantos quadros, o ângulo por quadro, e se a câmera muda. Em `work/kits-oracle/`.
6. **O número nas costas:** com a figura de costas, os painéis da página de uniforme pelo leitor
   de `--back … --panels` — o painel usado, os dígitos e as posições, contra `DIGIT_Y`,
   `DIGIT_STEP` e `BACK_COPY` do `core/figure.py`. O esperado é o do slot 5; divergência é
   resultado.
7. **Jogador de linha:** `--player ROW` desce a lista ROW vezes antes de confirmar (Marcos é a
   linha 0; Edmilson, CB 5, a linha 1) e repete os itens 2 a 6.

O que não der para medir fica escrito como negativa, com o comando e a saída.

**Medido (K3D-TASK-16, 2026-10-09).** A cópia mestra é `work/kits-states/SLPM-87056_8.sav`
(sha256 `ee349d74…b184`). Os dois comandos, com `WE2002_LOOKS_IMAGE` e `WE2002_LOOKS_DRIVE_IMAGE`,
guardam a captura em `work/kits-oracle/edit-8-<linha>.json`, e a mesma leitura sai de lá com
`--frame-json` (abaixo, colada da HEAD):

```sh
python3 tools/kits/oracle.py --edit-number 8            # Marcos, GK 1, a linha selecionada
python3 tools/kits/oracle.py --edit-number 8 --player 1 # Edmilson, CB 5, uma linha abaixo
```

```text
  capture read from work/kits-oracle/edit-8-0.json, no emulator
  front: 180 stop(s), 14 whole figure(s); the order each draws, head first:
    x14  MODEL.BIN:34 EDT_MOD.BIN:11 EDT_MOD.BIN:12 EDT_MOD.BIN:14 EDT_MOD.BIN:13 EDT_MOD.BIN:15 EDT_MOD.BIN:16 EDT_MOD.BIN:18 EDT_MOD.BIN:9 EDT_MOD.BIN:17 EDT_MOD.BIN:19 ?  (goalkeeper)
  front: every figure's translations within 145 to 178 of its median (limit 500); torso yaw -11.4 to -9.9 degrees, torso at (3, -54, 3778)
  turn: 1200 stop(s), 99 whole figure(s); the order each draws, head first:
    x99  MODEL.BIN:34 EDT_MOD.BIN:11 EDT_MOD.BIN:12 EDT_MOD.BIN:14 EDT_MOD.BIN:13 EDT_MOD.BIN:15 EDT_MOD.BIN:16 EDT_MOD.BIN:18 EDT_MOD.BIN:9 EDT_MOD.BIN:17 EDT_MOD.BIN:19 ?  (goalkeeper)
  turn: every figure's translations within 142 to 193 of its median (limit 500); torso yaw -179.9 to 180.0 degrees, torso at (-3, -53, 3779)
  kit: TEX_41 record 1 sleeves at (576,384), TEX_41 record 2 player palette at (0,486), TEX_41 record 3 goalkeeper palette at (0,488)
  the screen wears TEX_41 set 1, uniform page at (576,256)
  torso yaw per frame after the press: -12 -18 -24 -29 -35 -41 -45 -51 -56 -62 -67 -73 -80 -86 -91 -97 -101 -105 -111 -117 -122 -128 -134 -141 -146 -152 -157 -163 -169 -173 -178 -178 -178 -180 179 178 178 178 178 178 180 180 180 180 180 180 178 178 178 178 180 -179 -178 -178 -178 -178 -178 -180 -180 -180 -180 -180 -180 -178 -178 -178 -178 -180 179 178 178 178 178 178 180 180 180 180 180 180 178 178 178 178 180 -179 -178 -178 -178 -178 -178 -180 -180 -180 -180 -180 -180 -178 -178
  Circle turned the figure: torso yaw -12.0 to -178.5 in 30 frame(s) (frames 1 to 30 of 99), steps -6.2 -5.6 -5.7 -5.6 -5.6 -4.2 -5.6 -5.6 -5.6 -5.7 -5.6 -7.0 …
  page_front: 2 block(s) differ from the disc: (0,80)-(19,103) 480 px; (100,104)-(119,127) 480 px
    player     panel (  0, 80): number None digits none; 0 pixel(s) the rule does not explain
    goalkeeper panel (100,104): number 1    digits 1 at (7,7); 0 pixel(s) the rule does not explain
    picture: work/kits-oracle/edit-8-0-front.png
  page_back: 2 block(s) differ from the disc: (0,80)-(19,103) 480 px; (100,104)-(119,127) 480 px
    player     panel (  0, 80): number None digits none; 0 pixel(s) the rule does not explain
    goalkeeper panel (100,104): number 1    digits 1 at (7,7); 0 pixel(s) the rule does not explain
    picture: work/kits-oracle/edit-8-0-back.png
  front pose kept at work/kits-pose/slot8-row0-front.json (12 pieces)
  back pose kept at work/kits-pose/slot8-row0-back.json (12 pieces)
  ok    the goalkeeper opens at section 34, Circle turned it -166 degrees in 30 frame(s), and its back panel holds number 1
```

```text
  capture read from work/kits-oracle/edit-8-1.json, no emulator
  front: 180 stop(s), 14 whole figure(s); the order each draws, head first:
    x14  MODEL.BIN:24 EDT_MOD.BIN:0 EDT_MOD.BIN:1 EDT_MOD.BIN:3 EDT_MOD.BIN:2 EDT_MOD.BIN:4 EDT_MOD.BIN:5 EDT_MOD.BIN:7 EDT_MOD.BIN:9 EDT_MOD.BIN:6 EDT_MOD.BIN:8 ?  (player)
  front: every figure's translations within 137 to 162 of its median (limit 500); torso yaw -12.7 to -10.0 degrees, torso at (-1, -44, 3778)
  turn: 1200 stop(s), 99 whole figure(s); the order each draws, head first:
    x99  MODEL.BIN:24 EDT_MOD.BIN:0 EDT_MOD.BIN:1 EDT_MOD.BIN:3 EDT_MOD.BIN:2 EDT_MOD.BIN:4 EDT_MOD.BIN:5 EDT_MOD.BIN:7 EDT_MOD.BIN:9 EDT_MOD.BIN:6 EDT_MOD.BIN:8 ?  (player)
  turn: every figure's translations within 133 to 172 of its median (limit 500); torso yaw -179.9 to 180.0 degrees, torso at (-4, -47, 3778)
  kit: TEX_41 record 1 sleeves at (576,384), TEX_41 record 2 player palette at (0,486), TEX_41 record 3 goalkeeper palette at (0,488)
  the screen wears TEX_41 set 1, uniform page at (576,256)
  torso yaw per frame after the press: -13 -18 -24 -28 -32 -38 -44 -49 -55 -61 -68 -73 -79 -84 -90 -96 -100 -105 -111 -117 -124 -131 -136 -142 -148 -153 -159 -163 -169 -174 180 180 180 178 178 178 178 180 -179 -178 -178 -178 -178 -178 -180 -180 -180 -180 -180 -180 -178 -178 -178 -178 -180 179 178 178 178 178 178 180 180 180 180 180 180 178 178 178 178 180 -179 -178 -178 -178 -178 -178 -180 -180 -180 -180 -180 -180 -178 -178 -178 -178 -180 179 178 178 178 178 178 180 180 180 180
  Circle turned the figure: torso yaw -12.5 to 179.9 in 30 frame(s) (frames 1 to 30 of 99), steps -5.6 -5.6 -4.3 -4.3 -5.7 -5.6 -5.6 -5.6 -5.6 -7.0 -5.6 -5.6 …
  page_front: 2 block(s) differ from the disc: (0,80)-(19,103) 480 px; (100,104)-(119,127) 480 px
    player     panel (  0, 80): number 5    digits 5 at (7,7); 0 pixel(s) the rule does not explain
    goalkeeper panel (100,104): number 1    digits 1 at (7,7); 0 pixel(s) the rule does not explain
    picture: work/kits-oracle/edit-8-1-front.png
  page_back: 2 block(s) differ from the disc: (0,80)-(19,103) 480 px; (100,104)-(119,127) 480 px
    player     panel (  0, 80): number 5    digits 5 at (7,7); 0 pixel(s) the rule does not explain
    goalkeeper panel (100,104): number 1    digits 1 at (7,7); 0 pixel(s) the rule does not explain
    picture: work/kits-oracle/edit-8-1-back.png
  front pose kept at work/kits-pose/slot8-row1-front.json (12 pieces)
  back pose kept at work/kits-pose/slot8-row1-back.json (12 pieces)
  ok    the player opens at section 24, Circle turned it -168 degrees in 30 frame(s), and its back panel holds number 5
```

As duas corridas saem 0. O controle `--plant-edit-number` espera figuras abertas na 103 e lê cada painel uma linha acima, e sai 1:

```text
  PLANT  figures expected to open at section 103, and every panel read one row up
  FAIL  no figure opened at section 103
  FAIL  panel (100,103): 290 pixel(s) are neither the shirt back nor a digit
  FAIL  panel (100,103): digits at [(7, 8)], the rule puts them at [(7, 7)]
```

O que a saída diz, item por item:

1. **Carga e captura.** O state carrega pela cópia mestra; as capturas ficam em
   `work/looks-shots/edit-8-<linha>-front.png` e `-back.png` (de costas, com o número), e a página
   de uniforme pintada em `work/kits-oracle/edit-8-<linha>-front.png` e `-back.png`.
2. **Família do modelo: a da `LOOKS SET`, não a de partida.** As duas figuras são as do
   `EDT_MOD.BIN`: o goleiro desenha a lista 1 (seções 11 a 19, mais a chuteira 9 compartilhada e a
   outra, 10, que nenhuma parada nomeia — o `?`), o jogador de linha a lista 0 (0 a 9). Nenhuma seção
   de braço, manga ou braçadeira do `MODEL.BIN` entra: a tela não é onde a 91 ou a 94 aparecem
   (negativa). A única seção do `MODEL.BIN` é a cabeça, e ela **difere entre os dois**: 24 no
   jogador (a que a `LOOKS SET` desenha, `pieces.HEAD_SECTION`) e **34 no goleiro**. É plausível que
   a cabeça seja a do jogador, não a da figura — o `MODEL.BIN` tem várias cabeças e a `LOOKS SET`
   troca cabelo —, mas isso não foi medido aqui; a aba desenha a 24 nas duas figuras.
3. **Kit, paleta e mangas.** A tela veste o `TEX_41` (Brasil), conjunto 1, nas páginas da partida:
   uniforme em (576,256) e mangas em (576,384), paletas nas linhas 486 (jogador) e 488 (goleiro). O
   uniforme não é achado exato porque as duas lacunas do torso estão escritas (480 halfwords, item 6).
   As mangas são as peças de braço de cada lista do `EDT_MOD.BIN`: o goleiro de manga longa, o
   jogador de manga curta, como na `LOOKS SET`.
4. **Pose parada e câmera: negativa.** A figura **não está parada**: de frente, as matrizes mudam a
   cada quadro e a guinada do torso oscila entre −9,9° e −11,4° (a caminhada da `LOOKS SET`; na
   captura, a perna levantada). Os arquivos `work/kits-pose/slot8-row<linha>-front.json` e
   `-back.json` guardam a matriz por peça de um quadro dessa caminhada, não uma pose parada. A câmera
   não foi derivada: a leitura não captura o par do `ANIME.BIN` de cada peça, que o
   `camera_from_pieces` exige. O torso fica em (3, −54, 3778) no goleiro e (−1, −44, 3778) no
   jogador, e não muda com o giro.
5. **O giro.** Quem confirma é o **Circle**. A figura gira de −12° a −178° (goleiro) e de −12,5° a
   +179,9° (jogador) em **30 quadros**, a −5,6° por quadro (−4,2 e −7,0 uma vez cada), e fica de
   costas a ±180°, ainda caminhando (o balanço de ±2° por quadro que segue na linha "torso yaw per
   frame"). A translação não muda: a câmera é a mesma de frente e de costas. **O Cross não
   confirma**: a tela volta para a seleção de time (`Select Team`, captura
   `work/looks-shots/edit-8-0-Cross-back.png`) e a carga de matriz por peça para de disparar. Medido
   apertando só ele ([CORR-K3D-022](/docs/tasks/kits-3d/CORR-K3D-022.md)):

   ```sh
   WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin \
   WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= \
     python3 tools/kits/oracle.py --edit-number 8 --button Cross
   ```

   ```text
     Cross pressed: did not turn the figure; the per-piece matrix load gave 313 of 1200 stop(s) (12 whole figure(s)), then stopped firing for 20 s
   ```

   A corrida sai 1, com os `FAIL` do giro e do número que esse botão não produz. Por isso a ordem de
   `EDIT_BUTTONS` (Circle primeiro) e a recarga do state antes de cada botão.
6. **O número nas costas: a regra da partida, escrita ao selecionar a linha.** Na página de
   uniforme só diferem do disco os dois painéis do torso, (0,80) e (100,104). O da figura mostrada tem
   o número pela regra do §4.7: um dígito em (7,7) — `DIGIT_Y` 7, x 7 —, sobre as costas da camisa, e
   zero pixel que a regra não explique. O da outra figura tem as costas sem dígito. E a página é a
   **mesma antes e depois do giro**: o jogo escreve o painel quando a linha é selecionada, não ao
   virar. O Number da aba já faz isso.
7. **Jogador de linha.** `--player 1` desce para Edmilson (um `Down`, que move 0,0148 da tela) e
   repete tudo: lista 0, cabeça 24, giro de 30 quadros, painel (0,80) com o 5.

**O que isso dá à aba 3D.** Nada de geometria nova: a tela é a figura da `LOOKS SET`, com o mesmo
uniforme, a mesma caminhada e o mesmo painel de número da partida. O que ela acrescenta e a aba não
tem: o giro medido — 30 quadros a 5,6° por quadro, de frente para as costas, com a câmera parada —,
que serve de regra se a aba ganhar um "virar de costas" animado; e a dúvida da cabeça 34, que uma
task nova mede se quiser cabeça por jogador. Decisão de desenhar fica para o usuário.

## Para o ciclo

**Ordem sugerida:**

1. G1 e G2: texto e layout, baratos e independentes.
2. G5: a cópia das costas passa a ser sempre aplicada, e o resto se mede por ângulo.
3. G3 e G4: dependem da decisão de geometria da G3.

**Decisões do ciclo anterior que este pedido reabre.** Cada uma precisa entrar no plano novo como
decisão nova, datada:

- a figura "match player" no seletor (KITS-TASK-47);
- a manga longa escondida no goleiro e a braçadeira desligada nele (KITS-TASK-40);
- as costas vazadas por fidelidade aos dados (usuário, 2026-10-05; KITS-TASK-37).

**O que não muda:**

- o §0: nada de geometria inventada nem de UV remapeado à mão;
- o desenho por `QPainter` em software;
- o catálogo i18n como fonte única de texto da interface.
