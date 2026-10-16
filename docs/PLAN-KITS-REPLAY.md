# Plano — o jogador 3D da aba, a partir dos replays, e uma ferramenta de leitura de replay

Plano do ciclo `kits-replay` (prefixo `KRP`). O insumo é o relatório
[KITS-REPLAYS-9-10](/docs/KITS-REPLAYS-9-10.md), que resume as três investigações de replay do
ciclo `kits-3d` (K3D-TASK-17, 18 e 19) e responde: **sombra, cor, faixa e manga da aba 3D já batem
com o jogo; o que falta é corpo, pose e cabeça.** Este plano decide o que fazer com isso e em que
ordem; os números ficam no relatório e em
[G8 do KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g8--replays-nos-slots-9-e-10-braçadeira-e-manga-longa-de-perto-o-goleiro-capitão-e-os-22-em-campo),
colados da ferramenta, e não se reescrevem aqui.

## 0. Escopo

### Objetivo

1. Uma **ferramenta de leitura do jogador no replay**, que separe a captura (minutos de emulador)
   da análise (segundos, sem emulador) e responda em `--json`. Vem primeiro: toda melhoria abaixo
   começa lendo uma captura de replay.
2. A aba 3D desenhar o jogador **mais perto do jogo**: cabeça por jogador, goleiro pela família 13,
   pose de corrida, jogador real escolhido no seletor, os dois times lado a lado e uma câmera
   "replay" em perspectiva.

### Não-objetivos

- Andar o replay com Right/Left segurados.
- Mudar faixa, manga, cor, paleta ou sombreamento: fechados pelas três investigações
  ([item (h)](/docs/KITS-REPLAYS-9-10.md#h-o-que-não-muda)).
- Geometria ou UV inventados ou remapeados à mão ([§0 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#0)):
  só o medido entra no desenho.
- Gravar na imagem ou no cartão.

### Decisões confirmadas

- **Ciclo `kits-replay`, prefixo `KRP`** (usuário, 2026-10-12).
- **A ferramenta vem antes das melhorias**, porque elas a usam (usuário, 2026-10-12).
- **O goleiro passa a ser desenhado pela família 13**, com a pose medida e a 92 no lugar da 15.
  Isto **reabre a [K3D-TASK-10](/docs/tasks/concluidos/kits-3d/10-duas-figuras.md)**, que tirou a
  figura de partida do seletor (usuário, 2026-10-12; [§4](#4)).
- **Entram no ciclo**: jogador real no seletor ([§6](#6)), vista dos dois times ([§7](#7)), câmera
  "replay" em perspectiva ([§8](#8)) e o `confront --tab` ([§2.4](#2.4)) (usuário, 2026-10-12).

### O que não muda

- O 3D é desenhado em software no núcleo (`tools/kits/core/raster.py`) e mostrado por `QPainter`
  ([§3.4 do PLAN-KITS-PY](/docs/PLAN-KITS-PY.md#3.4)).
- Texto da interface só sai do catálogo `tools/kits/ui/i18n.py`, nas duas línguas.
- O `oracle.py` continua sendo o dono dos gates de replay (`REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`,
  plantas); a ferramenta nova é o leitor que ele importa.

## 1. O que já está medido

Tudo no [relatório](/docs/KITS-REPLAYS-9-10.md#o-que-foi-encontrado), itens 1 a 10, e nas
[descobertas (a) a (h)](/docs/KITS-REPLAYS-9-10.md#descobertas-novas-para-o-desenho-3d). O que cada
fase deste plano usa:

| Fase | Usa | Estado |
|---|---|---|
| [§2](#2) ferramenta | o bloco G8 do `oracle.py`, as capturas em `work/kits-oracle/` e o [projeto](/docs/KITS-REPLAYS-9-10.md#projeto) | projeto pronto |
| [§3](#3) cabeça | itens [8](/docs/KITS-REPLAYS-9-10.md#8), [(a)](/docs/KITS-REPLAYS-9-10.md#a-cabelo-barba-e-pele-do-jogador-vêm-da-clut-da-cabeça-pela-regra-da-looks-set) e [(b)](/docs/KITS-REPLAYS-9-10.md#b-a-seção-da-cabeça-é-o-estilo-de-cabelo-e-a-tabela-já-existe) | **hipótese**, a medir |
| [§4](#4) goleiro | itens [3](/docs/KITS-REPLAYS-9-10.md#3) e [(d)](/docs/KITS-REPLAYS-9-10.md#d-o-goleiro-do-jogo-é-a-família-13-inteira) | medido |
| [§5](#5) corrida | itens [6](/docs/KITS-REPLAYS-9-10.md#6) e [(c)](/docs/KITS-REPLAYS-9-10.md#c-a-pose-de-corrida-está-gravada-e-o-animebin-pode-ser-a-fonte-dela) | pose capturada; par do `ANIME.BIN` a medir |
| [§6](#6) jogador real | item [7](/docs/KITS-REPLAYS-9-10.md#7) e o §4.7 do PLAN-KITS-PY | painel e número medidos |
| [§7](#7) dois times | item [(e)](/docs/KITS-REPLAYS-9-10.md#e-dois-kits-na-vram-ao-mesmo-tempo-e-o-kit-pela-paleta) | medido |
| [§8](#8) câmera | itens [9](/docs/KITS-REPLAYS-9-10.md#9) e [(g)](/docs/KITS-REPLAYS-9-10.md#g-a-câmera-replay-como-preset-da-aba) | medido |

## 2. A ferramenta de leitura

Projeto no [relatório](/docs/KITS-REPLAYS-9-10.md#uma-ferramenta-de-leitura-do-jogador-no-replay).
Duas camadas, com o código **movido** do `oracle.py`, não copiado.

### 2.1 O leitor puro: `tools/kits/core/replay.py`

Sem emulador e sem `tools/looks/oracle`; importa só `layout`, `section`, `skin`, `assembly` e o
`core` do kits.

- `Capture.load(path)` lê um `replay-*.json`, repõe as tuplas (o `_restore_samples` do oracle vem
  para cá), valida as chaves e migra o schema implícito de hoje (v0) para o **v1**: chaves
  `schema`, `slot`, `focus`, `button`, `taps` e tuplas tipadas. `Capture.frames()` devolve `Frame`
  (figuras, cabeça da lista da GPU, offset de desenho).
- `Figure`: `order` (cabeça primeiro), `root`, `head`, `family` (`outfield` 2, `goalkeeper` 13,
  `other`), `sleeves`, `armband`, `depth`, `off_axis`, `pieces`, `pose()` (o JSON de
  `work/kits-pose/`), `box(index)`.
- `Figure.sections(index)`: por seção, primitivas, `shaded/raw/semi`, CLUTs, páginas, zonas, erro de
  encaixe em pixels e, com o frame buffer, `far` puro e modulado.
- `Figure.panel(pages)`: células amostradas, célula própria (descontada a compartilhada (0,80)) e
  número.
- `Walk.load(path)`: a tabela dos 22 de um `replay-field-*-capture.json`.
- `judge(figure, expect)` e `judge_walk(rows, expect)`: os juízes de hoje sobre esses objetos.

Os casos sintéticos do `selftest.py` que hoje exercitam o bloco `oracle --replay` e
`--replay-field` **migram** para cá; não se duplicam.

### 2.2 O `oracle.py` passa a importar o leitor

Saem do `oracle.py`, por move, as funções de análise do bloco G8: `replay_figures`,
`figure_depth`, `figure_off_axis`, `replay_focus`, `field_focus`, `pose_change`, `figure_group`,
`piece_box`, `section_samples`, `shading_of`, `colour_confront`, `panel_samples`, `panel_cell`,
`field_panels`, `field_number`, `sleeves_of`, `armband_of`, `figure_tag` e `_restore_samples`. Ficam
no oracle `REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`, os juízes como gate, as plantas e a captura.

O critério do move é **saída idêntica**: `oracle.py --replay … --frame-json`,
`--replay-field … --frame-json` e `--replay-confront` dão o mesmo texto antes e depois, sobre as
capturas existentes.

**Feito na fase 1** ([KRP-TASK-01](/docs/tasks/kits-replay/01-leitor-puro-core-replay-py-capture-v0v1-frame.md),
[02](/docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md) e
[03](/docs/tasks/kits-replay/03-fechamento-da-fase-1.md)), e o que difere do texto acima:

- o leitor não lê o disco: o índice do MODEL.BIN (`oracle.model_index`) e a largura do registro do
  uniforme entram como parâmetro — `Figure.box(index)`, `Figure.sections(index, buffer, texture)`,
  `Figure.panel(index, pages, width, on_torso)`, `Walk.load(path, index, width)`,
  `field_number(pages, panel, width, shift)`;
- o v1 traz também `kind` (`close` ou `walk`); `Capture.frames(side)` lê a frente ou as costas de
  uma captura de perto, e a de laço se lê por `Walk`; uma chave que a análise lê e falta é
  `ReplayError` nomeando a chave;
- `judge(report, expect, plant_root=None)`: a planta passa a raiz plantada em vez de `plant=True`;
  no oracle o juiz entra como `replay_judge`, porque o `judge` dele é o do `--expect`;
- além das dezenove, saíram do oracle os auxiliares de que elas dependem (`pose_frames`,
  `matrix_pieces`, `pose_project`, `piece_error`, `kit_image_of`, `read_panels`, `field_row`…), os
  dois juízes e as constantes deles; o oracle os importa de `core.replay`. A regra `REPLAY_MOVED`
  do `selftest.py` recusa qualquer das dezenove definida de novo no oracle, com o controle
  `replay-copy-in-oracle`;
- os casos sintéticos de replay migraram (23 de 26; os 3 restantes testam a leitura da lista da GPU
  e o `replay_chooser`, que ficam no oracle). Onze controles que plantavam no oracle passaram a
  plantar no leitor — nove na KRP-TASK-01, renomeados sem o prefixo `oracle-`, e dois na
  KRP-TASK-02 (`oracle-back-byte-order`, `oracle-pose-texel-order`) — e dois novos plantam nele
  (`replay-key-check`, `replay-v0-slot`): 13 com alvo `kits/core/replay.py`, contados por
  `grep -cE '^\s*"[^"]+", "kits/core/replay.py"' tools/kits/controls.py`.

### 2.3 A linha de comando de leitura: `tools/kits/replay.py`

Subcomandos, na convenção do `tools/kits/cli.py`, todos sem emulador: `figures`, `figure
[--on-axis|--nearest|--nth N] [--section S]`, `panel`, `walk`, `describe` e, desde a
[§3.1](#3.1), `head [--player all|N]`. **`--json` em todo
leitor**, com `"schema": "kits-replay/1"` e chaves fixas — é o contrato com o agente; saída humana
curta por padrão.

O `figure --json` reproduz, campo a campo, o que a linha `ok` do `oracle.py --replay --frame-json`
afirma, nas cinco capturas de perto.

### 2.4 Olhar e confrontar: `show`, `confront` e `confront --tab`

- `show <captura> --png out.png [--section S | --box]`: o recorte do frame buffer do jogo ao lado
  da figura desenhada pelo `core/raster` na pose capturada — para olhar, sem Qt.
- `confront <captura> [--section S]`: pixel do jogo contra texel puro e modulado.
- `confront <captura> --tab`: sobe o `ui/app.py --export-3d` e compara a aba com o jogo por
  histograma, **frente com frente e costas com costas** — fecha a lacuna da
  [CORR-K3D-034](/docs/tasks/concluidos/kits-3d/CORR-K3D-034.md). A frente de um jogador de linha só
  existe na captura girada ([§2.5](#2.5), `--turn`).

O `confront --tab` **registra número, não afirma limite**. É o instrumento de "antes e depois" de
toda task de desenho das fases seguintes.

### 2.5 A captura: `replay.py capture`

`capture --slot S [--focus K] [--turn R1|L1] [--walk L2|R2] [--out DIR]`, a única que sobe o
emulador. Guardas, todas já medidas no ciclo `kits-3d`:

- `fork.refuse_joysticks` antes de subir (CORR-K3D-031);
- recarga do state antes de cada sequência, e toda sequência abaixo dos 390 quadros do timeout do
  replay;
- 9 submits por captura (dois quadros inteiros, CORR-K3D-026);
- o seguido é a figura no eixo, com margem de 8 px ou 1000 de profundidade, atrás de um jogador; a
  de menor z no zoom máximo (CORR-K3D-024);
- as paradas do giro emprestam a projeção da primeira captura; o kit se acha pela paleta amostrada.

O `oracle.py` passa a capturar por ela. Custo de relógio: 10 a 40 minutos por corrida; releitura em
segundos.

### 2.6 O gate: `kits_replay`

Alvo novo de `ctest`, **`kits_replay`**: roda os leitores sobre as capturas da pasta apontada por
`WE2002_KITS_REPLAY_DIR` (hoje `work/kits-oracle/`), confere o digest de cada uma contra o
registrado, e sai 77 (*skipped*) sem a variável ou sem `WE2002_LOOKS_IMAGE`. Não há pasta default:
o `ctest` roda de `build/tests`, e um default relativo pularia em silêncio
([KRP-TASK-04](/docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md)). A contagem de alvos `kits` mora só no [§9](#9).

**Feito na fase 2** ([KRP-TASK-04](/docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md)
a [08](/docs/tasks/kits-replay/08-fechamento-da-fase-2.md)), e o que difere do texto acima:

- o `check` confere cada captura contra a tabela `CAPTURES` do `replay.py` (nome e sha256) e julga
  com as constantes do oracle, importado **por caminho** — o `oracle.py` e o `confront.py` da looks
  têm o mesmo nome e vêm antes no `sys.path`;
- a captura de perto guarda o frame buffer das **duas** capturas (`buffer` e `back_buffer`): sem o
  segundo o `confront --tab` não tinha o jogo da captura girada para comparar;
- qual captura tem a frente do jogo é `game_side(side, focus)`: sem foco a primeira é a frente do
  goleiro; atrás de um jogador (`--focus K`) a primeira é as costas e a frente é a girada;
- `capture` grava em `work/kits-replay/` por padrão (`--out`), e o giro **não** é julgado contra os
  390: ele conta da recarga através de todos os toques, cada um reinicia o ocioso, e o que se julga
  é o maior intervalo entre dois toques (`turn gap`); sem `--turn` o campo `turned` sai `not asked`.

## 3. Cabeça por jogador

### 3.1 Medir a regra

Hipótese do relatório, (a) e (b): a seção da cabeça é o estilo de cabelo pela `assembly.HAIR_MAP`
(com o *twin* da `FACE_TWINS` para barba F ou G, a 47); a linha da CLUT dá a pele, e a coluna dá o
cabelo (`HAIR_COLUMN`) e a barba (`BEARD_COLUMN`), pela regra que o ciclo `looks` mediu
(`tools/looks/layout.py`, `tools/looks/skin.py`).

A medição: o subcomando `replay head <captura> [--player <registro>]` decodifica estilo, pele,
cabelo e barba da captura, e com `--player` confronta com o registro de 12 bytes do jogador no disco
(`tools/looks/looks.py`, `records` e `decode`). Confronta **os 22 do laço**
(`replay-field-9-capture.json` e `-10-`), não só os três de perto. Achar o registro de cada um dos 22
(time e número pelo painel, [item 7](/docs/KITS-REPLAYS-9-10.md#7)) faz parte da medição.

Resultado negativo é resultado: se a regra não fechar, a §3.2 desenha só o que fechou.

**Medido** ([KRP-TASK-09](/docs/tasks/kits-replay/09-medir-a-regra-da-cabeca-estilo-pele-cabelo-e.md)):
a regra **fecha nos 22 dos dois laços**, e nas três capturas de perto.
`replay.py head <captura> --player all` dá `22 of 22 distinct player(s) match their disc record` em
`replay-field-9-capture.json` e em `-10-`. O jogador se acha pela página e pelo número do painel:
página 576 é o Brasil (time 41) e 640 a Croácia (22), `HEAD_TEAMS`. O número de camisa sai de
`OFS_SQUAD_NUMBERS_NATIONAL` (cinco bits por vaga, gravado menos um), e o registro é o
`time * 23 + vaga` do `/SELECT.BIN`. O foco 0 não mostra painel: é o goleiro em que o replay abre,
e o painel dele é o da captura de perto do mesmo slot, (576, 100, 104) número 1.

O que a medição fixa:

- **seção = estilo**: a seção desenhada é a do `assembly.HAIR_MAP` para o `hair_style` do
  registro. Barba F ou G troca pela gêmea do `FACE_TWINS`: a 47 do número 8 da Croácia é
  `A-L3-H-F-C`. Aparecem seis seções: 24 (A), 28 (G), 32 (K), 34 (I), 46 (L) e 47 (L gêmea);
- **linha da CLUT = pele**, `480 + skin_colour`: aparecem as peles A, C e D (Brasil 10, 2, 6, 16,
  7, 3 em 482; 11 e 4 em 483);
- **coluna = cabelo ou barba**: a coluna `1 + hair_colour` está em toda cabeça. A coluna
  `9 + beard_colour` só aparece quando a vista mostra a barba. Nos dois slots aparece no Marcos e
  no 8 da Croácia; só no slot 10, no 20 e no 7 da Croácia e no 11, no 6, no 7 e no 5 do Brasil.
  Por isso a barba só se julga quando aparece;
- **a cabeça se lê dentro do box da própria peça** (`core/replay.py head_samples`): o box da figura
  inteira pega a cabeça de um vizinho. No slot 10 isso daria (16,482) no 4 da Croácia e (32,480) no
  10 do Brasil: o `replay.py head` lê os dois com as duas CLUTs, (16,482) e (32,480), e o
  `kits_replay` cai em 4 falhas. Esses números são de uma corrida remontável, com script e saída no
  Log da [CORR-KRP-016](/docs/tasks/kits-replay/CORR-KRP-016.md). O que fica no gate é o controle
  `replay-head-piece-box` do `controls.py`. Ele tira a condição e derruba uma asserção sintética do
  selftest, sem dado real: uma figura e um quad da cabeça de um vizinho, dentro do box da figura e fora do box
  da peça.

O esperado por jogador é a constante `HEAD_EXPECT` do `replay.py` (K1), e o `kits_replay` confere
duas coisas: que o disco ainda a diz, e que cada cabeça seguida a lê. A planta
`replay.py check --plant-hair-column`, que move toda CLUT uma coluna, derruba o gate com dado real
(saída no Log da task).
Dois slots medidos dizem "nos dois", não "sempre".

### 3.2 Desenhar

`core/figure.py:scene_of` e `match_scene` recebem a tupla do jogador no lugar de
`TUPLE = assembly.CORPUS_REFERENCE`. O CLI e a aba ganham a opção (a tupla, e depois o jogador real
pelo [§6](#6)). Confronto de antes e depois pelo `confront --tab` nos três de perto.

**Feito** ([KRP-TASK-10](/docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md)).
Os dois recebem `player` (uma tupla da looks, `A-L3-H-A-A`). Quem desenha a cabeça é a regra do
[§3.1](#3.1), em `core/figure.py`, e o `replay.py head` usa a mesma regra de seção:

- `player_head_section`: a seção do `HAIR_MAP`, e a gêmea do `FACE_TWINS` para barba F ou G;
- `player_head_clut`: aplicada sobre a CLUT que o **disco** dá a cada primitiva da cabeça. A linha
  vira `480 + skin_colour`, a coluna 1 vira `1 + hair_colour` e a coluna 9 vira
  `9 + beard_colour`. Qualquer outra CLUT fica como o disco a dá;
- os texels são os do disco, como o `match_scene` texturiza uma seção do MODEL.BIN.

Na figura da aba (`scene_of`), a cabeça da tupla de referência sai inteira e a do jogador entra no
lugar que a pose dá à cabeça (`scene.place_for`). A cena da looks com a tupla do jogador não serve:
ela deixa parte das primitivas da 46 na coluna do disco, e o jogo pinta todas. **O resto da figura
não muda**, inclusive a pele do corpo, que nenhum replay mediu. No `match_scene`, a seção da cabeça
troca na mesma matriz.

Sem a opção nada muda, e o digest de `cli.py figure` (as duas cenas) é o de antes. O CLI tem
`figure --player`; a aba tem a caixa "Cabeça do jogador" e o `--player-looks`; o
`confront --tab --player` repassa a tupla do jogador que o painel da captura nomeia
(`HEAD_EXPECT`). O confronto do desenho com o jogo, primitiva a primitiva, é o
`replay.py head --drawn`: as três capturas de perto e os 24 focos de cada laço amostram a CLUT do
jogo em toda primitiva.

## 4. Goleiro pela família 13

Medido ([item 3](/docs/KITS-REPLAYS-9-10.md#3)): o goleiro do jogo é a família 13 inteira — torso
13, braços 14 e 16 à direita, 92 (no lugar da 15) e 17 à esquerda, pernas 18, 20, 19 e 21, a 11 e a
cabeça do jogador. A aba hoje desenha o goleiro do `EDT_MOD.BIN` com só a 92 trocada, e é a maior
diferença visível das três investigações.

A mudança: desenhar o goleiro pela família 13 do `MODEL.BIN`, com a cabeça do [§3](#3), na pose de
`work/kits-pose/slot9-keeper-front.json` promovida a arquivo versionado do núcleo (como
`core/match_pose.json`), e a faixa 92 quando capitão. A decisão reaberta da K3D-TASK-10 fica escrita
no plano e no perfil, datada. Confronto de antes e depois pelo `confront --tab` no goleiro dos dois
slots.

## 5. Pose de corrida

### 5.1 Medir a corrida no `ANIME.BIN`

As cinco poses de `work/kits-pose/` são a corrida do replay. O `ANIME.BIN` guarda 204 animações, e
`tools/looks/anime.py --against-pose` liga uma captura ao par que o jogo lia — medido no `looks`
para a caminhada. A medição: a captura passa a gravar o ponteiro do par (como o `--pose` do `looks`;
o `pose_capture` hoje não o lê), e `replay pose <captura> --against-anime` imprime animação e quadro
que explicam cada uma das cinco poses — ou a negativa, com comando e saída.

### 5.2 Posar pela corrida

Famílias 2 e 13 posadas pela animação e quadro medidos, como hoje se posa a caminhada da
`LOOKS SET`; a aba ganha seletor de pose (caminhada ou corrida). Se a §5.1 der negativa, a pose
capturada versionada é o fallback, e isso fica escrito.

## 6. Jogador real no seletor

O que faz as fases 3 a 5 virarem a vista de um jogador escolhido: o seletor da aba ganha **time e
jogador**, e daí saem número (`SquadNumbers`), capitão (`Team.captain`), cabeça ([§3](#3)), figura
de linha ou goleiro ([§4](#4)) e a manga. O que ainda não se lê do disco no `tools/kits` (elenco,
número, capitão) sai dos `OFS_*` já mapeados para o `we2002_core`, pelo caminho que o
`gen_tables.py` já usa para os nomes de time — a forma exata se decide na task, sem tocar `src/`.

## 7. Vista dos dois times

Medido ([item (e)](/docs/KITS-REPLAYS-9-10.md#e-dois-kits-na-vram-ao-mesmo-tempo-e-o-kit-pela-paleta)):
na partida os dois kits ficam lado a lado na VRAM, cada um com a sua paleta de jogador e de goleiro.
A aba ganha a vista de dois jogadores, um de cada time, cada um com o seu kit. Nada novo de formato.

## 8. Câmera "replay"

Medido ([item 9](/docs/KITS-REPLAYS-9-10.md#9)): projeção do GTE com H 1376 e OFX, OFY 0; o jogador
a 4681–4682 de profundidade de frente no zoom máximo e a ~4700 de costas; giro de 8 a 12 graus por
toque. A aba hoje desenha em projeção ortográfica; a mudança é **projeção perspectiva no
`core/raster.py`** com esses números, e um preset "replay" na aba. Fica por último porque muda o
confronto de todas as anteriores: o `confront --tab` se refaz nas cinco capturas com a câmera nova.

## 9. Verificação

Gates de toda task:

- `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY=
  WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`:
  **4 alvos até o `kits_replay` existir, 5 depois** (`kits_selftest`, `kits_image`, `kits_gen`,
  `kits_ui`, `kits_replay`), todos passando e sem *skipped*. Este é o único lugar do plano com a
  contagem; o resto remete aqui.
- `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com um controle por leitor
  ou asserção nova.

As armadilhas do retro do `kits-3d` que valem aqui
([perfil-kits-3d.armadilhas](/docs/prompts/perfil-kits-3d.armadilhas.md)):

- **K1** — o esperado é constante por (slot, foco), nunca lido da captura;
- **K2** — toda asserção nova entra com uma planta que a derruba com dado real, e o Log mostra o
  vermelho;
- **K3** — toda linha `$` do Log traz as flags da corrida, inclusive `--frame-json`.

Toda task de desenho registra o `confront --tab` antes e depois, colado da HEAD. Toda task de
investigação: negativa é resultado e não bloqueia; só a cópia mestra ausente bloqueia
(`test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav`).

## 10. Fases e ordem

| Fase | Seções | O que entrega |
|---|---|---|
| 1 | [§2.1](#2.1), [§2.2](#2.2) | o leitor puro e o oracle sobre ele, com saída idêntica |
| 2 | [§2.3](#2.3)–[§2.6](#2.6) | a linha de comando, `show`, `confront` e `confront --tab`, a captura e o gate `kits_replay` |
| 3 | [§3](#3) | a regra da cabeça medida nos 22, e a cabeça por jogador desenhada |
| 4 | [§4](#4) | o goleiro pela família 13 |
| 5 | [§5](#5) | a corrida medida no `ANIME.BIN` e a pose de corrida na aba |
| 6 | [§6](#6), [§7](#7) | jogador real no seletor e a vista dos dois times |
| 7 | [§8](#8) | a câmera "replay" em perspectiva |

Por que esta ordem:

- **A ferramenta primeiro** (fases 1 e 2): as fases 3 a 5 começam lendo uma captura, e o
  `confront --tab` é a métrica de antes e depois de todas as tasks de desenho.
- **A cabeça antes do goleiro**: o goleiro da família 13 usa a cabeça do jogador.
- **A medição da corrida só depende da ferramenta** e pode correr cedo; posar pela corrida espera o
  goleiro, porque posa as duas famílias.
- **O jogador real junta as três** (cabeça, goleiro, pose) no seletor; os dois times vêm em cima
  dele.
- **A câmera por último**: é cosmética, e muda o confronto de todas as anteriores.
