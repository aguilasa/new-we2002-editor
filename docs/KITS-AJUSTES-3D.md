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

**Hoje:**

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
matriz e o lugar que a figura dá a essa peça. A tabela é `ARM_PIECES` de `tools/kits/oracle.py`, e
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
  section  57 -> upper arm a (nearest EDT section  1 at 5.6, other part 7.9), frame offset 1.8 (+1.6,+0.8,+0.4)
  section  58 -> forearm a   (nearest EDT section  3 at 4.3, other part 13.5), frame offset 1.8 (-0.2,+1.8,+0.4)
  section  59 -> upper arm b (nearest EDT section  2 at 5.5, other part 8.2), frame offset 1.2 (+0.9,+0.8,-0.4)
  section  60 -> forearm b   (nearest EDT section  4 at 4.3, other part 13.5), frame offset 1.8 (-0.2,+1.8,-0.4)
  section  90 -> upper arm b (nearest EDT section  2 at 5.6, other part 8.2), frame offset 0.8 (+0.1,+0.8,+0.2)
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
seção continua com a mesma peça mais próxima, e a corrida sai 1 só pelo referencial: 18 linhas
`FAIL`, todas `units out of` (até a CORR-K3D-013 o controle era 20 em y, que trocava a peça mais
próxima e saía com 21 `FAIL`). No catálogo do `controls.py`, `oracle-arm-side-flipped` e
`oracle-arm-frame-blind` derrubam os casos sintéticos do `selftest.py`.

**O que fica para a K3D-TASK-10:** substituir a peça inteira pela seção do `MODEL.BIN` ou desenhar
a braçadeira por cima da malha do `EDT_MOD.BIN`. A regra diz onde a seção vai e com que matriz; ela
não diz qual das duas malhas aparece.

## G4 — Number, Captain armband e Long sleeves em qualquer combinação, nas duas figuras

**Pedido.** As três caixas valem para **player** e **goalkeeper** e combinam livremente: nenhuma,
uma, duas ou as três ao mesmo tempo.

**Hoje** (`dressings()`, `ui/app.py:583-601`):

| Caixa | Jogador | Goleiro |
|---|---|---|
| Number | recusado quando a figura de partida é desenhada (`number_off`, `ui/i18n.py:84`): o painel do torso de partida não foi medido (§4.7) | funciona |
| Captain armband | funciona, trocando para a figura de partida | desligado, com `armband_off` (`ui/i18n.py:86`) |
| Long sleeves | funciona, trocando para a figura de partida | escondido (`ui/app.py:589`) |

Hoje só a braçadeira e a manga longa combinam entre si.

**Em aberto:**

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
15.** Medido no slot 7 (`work/kits-states/SLPM-87056_7.sav`): Brasil x China, e Marcos, goleiro e
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
  not drawn here: section 91 has the mirrored vertices of goalkeeper arm 57; its texels touch: armband, short sleeve (player), short sleeve, left, captain (player), short sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 94 has the vertices of goalkeeper arm 59; its texels touch: armband, long sleeve (player), long sleeve, left, captain (player), long sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 91 has the mirrored vertices of goalkeeper arm 99; its texels touch: armband, short sleeve (player), short sleeve, left, captain (player), short sleeve, left, captain, under the armband (player), shoulder, second (player)
  not drawn here: section 94 has the vertices of goalkeeper arm 100; its texels touch: armband, long sleeve (player), long sleeve, left, captain (player), long sleeve, left, captain, under the armband (player), shoulder, second (player)
  ok    the goalkeeper opened at section 13 draws section 92 in place of 15
```

O que a saída diz:

- **A 92 entra no lugar da 15.** Nas 23 figuras inteiras, o goleiro desenha a 92 na quinta posição, onde
  fica o `upper arm b`, e nunca desenha a 15. A 92 tem os vértices da 15, vértice por vértice: é o
  mesmo braço com outros texels, como a 93 em relação à 97 e a 90 em relação à 4 (G3). Pela regra de
  G3, ela vai no `upper arm b` da figura do `EDT_MOD.BIN`.
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
