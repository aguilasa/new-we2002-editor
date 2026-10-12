# Replays nos slots 9 e 10 — o jogador de perto, e o que a aba 3D pode aproveitar

Relatório das três investigações da fase 7 do ciclo `kits-3d`:
[K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md) (o goleiro capitão de perto,
fechada em 2026-10-09, commits `f020577` e `4cf6a39`),
[K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md) (os 22 em campo por L2/R2, 2026-10-10,
`27f2565` e `1a90142`) e
[K3D-TASK-19](/docs/tasks/kits-3d/19-medir-capitao-linha-replay.md) (o capitão de linha, manga curta e
longa, 2026-10-12, `d8f8e7df` e `23fb593e`). As revisões abriram treze correções, todas fechadas:
[CORR-K3D-023](/docs/tasks/kits-3d/CORR-K3D-023.md),
[024](/docs/tasks/kits-3d/CORR-K3D-024.md), [025](/docs/tasks/kits-3d/CORR-K3D-025.md),
[026](/docs/tasks/kits-3d/CORR-K3D-026.md), [027](/docs/tasks/kits-3d/CORR-K3D-027.md),
[028](/docs/tasks/kits-3d/CORR-K3D-028.md), [029](/docs/tasks/kits-3d/CORR-K3D-029.md),
[030](/docs/tasks/kits-3d/CORR-K3D-030.md), [031](/docs/tasks/kits-3d/CORR-K3D-031.md),
[032](/docs/tasks/kits-3d/CORR-K3D-032.md), [033](/docs/tasks/kits-3d/CORR-K3D-033.md),
[034](/docs/tasks/kits-3d/CORR-K3D-034.md) e [035](/docs/tasks/kits-3d/CORR-K3D-035.md). O retro do
ciclo está em [retro.md](/docs/tasks/kits-3d/retro.md). A saída completa das ferramentas, colada da
HEAD, está em
[G8 do KITS-AJUSTES-3D](/docs/KITS-AJUSTES-3D.md#g8--replays-nos-slots-9-e-10-braçadeira-e-manga-longa-de-perto-o-goleiro-capitão-e-os-22-em-campo).
Este documento resume o que foi medido e responde a uma pergunta: **o que dos replays muda o desenho
da aba 3D, e o que já está certo?** É o insumo do plano do próximo ciclo do kits.

## Os states e os controles do replay

O pedido que abriu a fase (usuário, 2026-10-09): melhorar o desenho do jogador na aba 3D como um todo,
e principalmente com a braçadeira de capitão — "meio estranha, não se parece muito com o jogo" — e
com manga longa — "um pouco diferente do jogo". Nenhum state anterior mostrava as duas coisas de
perto.

Os dois states são **replays parados** de Brasil × Croácia, câmera focada no **Marcos** (goleiro,
nº 1, capitão do Brasil), de frente, no zoom mais próximo:

- **slot 9**: jogadores de linha de manga curta;
- **slot 10**: jogadores de linha de manga longa;
- os goleiros usam manga longa sempre. O capitão da Croácia é o **nº 11, Bokšić**.

As cópias mestras são `work/kits-states/SLPM-87056_9.sav` (sha256
`54c7979296a6652118607973232b84f9e030f9edc7d7e8cd68bc95607dc0d6d6`) e `SLPM-87056_10.sav`
(`bdf47644500f39dc7be313f0bc5a142fd3af7cebfd1c2ffa3a325c5389503b6e`).

Controles do replay (relato do usuário, confirmados pelas corridas): **L2/R2** trocam o jogador
que a câmera segue, pelos 22 e pela bola; **L1/R1** giram a câmera em volta dele; **Up/Down** mudam
o zoom; **Right/Left** segurados andam o replay (fora do escopo das três tasks). **Sem comando por
390 quadros o replay termina** nos dois slots — medido por `--replay-idle` sobre a placa "SAVE"
(`REPLAY_HUD`), não sobre a tela inteira: as bandeiras da torcida mexem 0,0357 em 150 quadros do
replay parado. Cada toque reinicia a contagem, então toda captura recarrega o state e fica abaixo
dela.

## Como foi medido

Todo número abaixo sai de `tools/kits/oracle.py`, pelas opções criadas nas três tasks:

```sh
export WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin
export WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue
export DISPLAY=:98 XAUTHORITY=
python3 tools/kits/oracle.py --replay-idle 9              # quadros até o replay acabar sozinho (e 10)
python3 tools/kits/oracle.py --replay 9                   # o goleiro de frente, o giro por R1 e as costas (e 10)
python3 tools/kits/oracle.py --replay-field 9             # os 22 por L2, um foco por recarga (e 10)
python3 tools/kits/oracle.py --replay-field 9 --field-button R2   # o mesmo laço por R2
python3 tools/kits/oracle.py --replay 9 --focus 3         # o Bokšić: 3 toques de L2, costas, giro, frente
python3 tools/kits/oracle.py --replay 10 --focus 3        # idem, manga longa
python3 tools/kits/oracle.py --replay 10 --focus 2        # o Balaban (nº 20), manga longa sem faixa
python3 tools/kits/oracle.py --replay-confront 9 [--focus K]      # a aba contra o quadro do jogo
python3 tools/kits/oracle.py --replay 9 --plant-replay    # as plantas, vistas saindo 1
python3 tools/kits/oracle.py --replay-field 9 --plant-replay-field [focus|panel]
```

As capturas ficam em `work/kits-oracle/`: `replay-<slot>.json` (goleiro), `replay-<slot>-<K>.json`
(foco K), `replay-field-<slot>[-R2]-capture.json` (o laço) e a tabela `replay-field-<slot>.json`;
as poses em `work/kits-pose/slot<slot>-keeper-front.json` e `slot<slot>-focus<K>-first.json`; o
recorte do frame buffer do jogo em `replay-<slot>[-<K>]-frame.png` (4×) e a aba em
`-tab-front.png` e `-tab-back.png`. Toda leitura se refaz **sem emulador** com `--frame-json
<captura>`, e é assim que cada linha deste documento foi reconferida na HEAD. Custo de relógio
observado nesta sessão, que nenhuma opção imprime: `--replay-field` leva de 35 a 40 minutos por slot
(25 focos); `--replay --focus` de 10 a 20 minutos; reler uma captura leva segundos.

O que o juiz afirma mora em `REPLAY_EXPECT` (por slot e foco) e `REPLAY_FIELD_EXPECT` (por slot). As
linhas decisivas, da HEAD:

```text
$ python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json      # e 10, a mesma linha
  ok    the followed figure opens at section 13 with head 34, draws 92 in place of 15, holds still, and its back shows panel (576, 100, 104) with number 1
$ python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json
  ok    22 focus(es) follow a player and the camera comes back to the ball; the outfield captain is focus 3, number 11 with armband 90; the goalkeeper draws 92
$ python3 tools/kits/oracle.py --replay-field 10 --frame-json work/kits-oracle/replay-field-10-capture.json
  ok    22 focus(es) follow a player and the camera comes back to the ball; the outfield captain is focus 3, number 11 with armband 93; the goalkeeper draws 92
$ python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json
  ok    the followed figure opens at section 2 with head 46, draws 90 in place of 4, holds still, and its back shows panel (640, 60, 104) with number 11
$ python3 tools/kits/oracle.py --replay 10 --focus 3 --frame-json work/kits-oracle/replay-10-3.json
  ok    the followed figure opens at section 2 with head 46, draws 93 in place of 97, holds still, and its back shows panel (640, 60, 104) with number 11
$ python3 tools/kits/oracle.py --replay 10 --focus 2 --frame-json work/kits-oracle/replay-10-2.json
  ok    the followed figure opens at section 2 with head 46, draws no armband, holds still, and its back shows panel (640, 80, 104) with number 20
```

As plantas: `--plant-replay` sai 1 com quatro `FAIL` no goleiro e seis no Bokšić (`the followed
figure opens at 2, not at section 103`, a primeira vez que a conferência de raiz fica vermelha com
uma figura real no quadro); `--plant-replay-field` sai 1 com 49 `FAIL`, e cada metade sozinha
(`focus`, `panel`) derruba o seu. Os controles plantados do catálogo (`controls.py`) foram de 43 a
53, todos `RED`.

## O que foi encontrado

### 1. O jogo não sombreia: todo quad é plano (127,127,127), e o pixel do quadro é o texel puro

Em todas as figuras capturadas — o Marcos nos dois slots, o Bokšić nos dois, o Balaban — cada
primitiva vai à GPU com `0 shaded, 0 raw, 0 semi` e cor de canto `(127, 127, 127)`: nenhum Gouraud,
nenhuma textura crua, nenhuma semitransparência. A cor 127 é o neutro do console (texel × 127/128),
então o que aparece na tela é o próprio texel. O `colour_confront` mede isso lendo o frame buffer sob
cada seção e comparando com o texel puro e com o texel modulado pela cor de canto (`far`, distância
média por canal, cinco bits):

- goleiro, slot 9: puro 0,31–3,40 contra modulado 1,08–3,53; slot 10: 0,42–3,01 contra 0,99–3,28, o
  puro mais perto em toda seção com pixel próprio;
- Bokšić: faixa 90 2,27 contra 2,55; faixa 93 2,18 contra 2,59; o puro mais perto em todas;
- Balaban: o puro mais perto em todas menos duas, as de menos pixel: a manga 95 empata (30 px, 3,08
  contra 3,10) e a 96 vira (9 px, 8,07 contra 7,67).

As distâncias maiores do goleiro (16, 17, 92: 2,2 a 3,4) têm a rede do gol por cima na tela —
suspeita, não medida. **Consequência para a aba:** o `core/raster.py`, que pinta o texel mais próximo
sem luz nem cor de vértice, já faz o que o jogo faz. Sombreamento não é a diferença.

### 2. A paleta é a do disco, e a CLUT do jogador é a linha de paleta do kit carregado

A paleta do disco que a aba usa é a que o jogo tem na VRAM: `TEX_41` registro 3 (paleta de goleiro)
contra a CLUT (0,488), `256 entries, 0 differ`; `TEX_22` registro 2 (paleta de jogador) contra a
(0,487), `0 differ`. Na partida os dois kits ficam lado a lado: Brasil na página (576,256), paleta de
jogador em (0,486) e de goleiro em (0,488); Croácia na página (640,256), (0,487) e (0,489); as
bandeiras em (704,256) e (704,320), com paletas em (256,494) e (256,495).

Uma surpresa de instrumento: na VRAM do replay **não existem** os corpos de uniforme como o disco os
guarda — o `_edit_kit`, que acha o kit pela imagem (registros 0, 1, 4 e 5), não encontra nenhum, e as
tasks 17 e 18 ficaram com `tag None`. Quem identifica o kit de um jogador é a paleta que ele amostra
(`figure_tag`, K3D-TASK-19): o Bokšić amostra (0,487) → `TEX_22`. A página de uniforme está lá, mas
com outro conteúdo (o `read_panels` lê os números dela).

### 3. O goleiro do jogo é a família 13 inteira, com a 92 no lugar da 15

Nos dois slots a figura seguida abre em `34 13 14 16 92 17 18 20 11 19 21` (mais uma peça que o
atraso de desenho deixa sem nome), a 4681 e 4682 de profundidade. Cabeça 34, torso 13, braços 14 e
16 à direita, **92 e 17** à esquerda — a 92 é a braçadeira do goleiro, com os vértices da 15 —, pernas
18, 20, 19 e 21, e a 11. A família 56, com as braçadeiras 91 e 94, **não aparece**: nem no zoom
máximo do goleiro, nem em nenhum dos 22 jogadores dos dois laços (`--keeper-armband 9` sai 1 com
`0 whole and 49 cut figure(s)`, porque no zoom máximo o quadro só tem o goleiro e a última peça nunca
é nomeada; é o juiz do `--replay` que afirma a 92).

O painel do número do goleiro é **fixo na seção**: de frente nenhum quad do torso amostra painel
(`front: 0 primitive(s)`); de costas, quatro, e os quatro são os texels da própria seção 13 no disco
(`back: 4 primitive(s) of the figure sample panel (100,104) of page (576,256); 4 of them are torso
13's own texels on the disc`). O número lido é o 1, dígito em (7,7), 0 pixels sem explicação.

### 4. O capitão de linha: 90 no lugar da 4 (manga curta), 93 no lugar da 97 (manga longa)

Os três focos de perto, seção a seção:

| Foco | Ordem (cabeça primeiro) | Faixa | Quads da faixa, zona do bitmap de mangas |
|---|---|---|---|
| Bokšić, slot 9 | `46 2 3 5 90 6 7 9 11 8 10` | **90** no lugar da 4 | 2; "armband, short sleeve"; "short sleeve, left, captain"; "…under the armband" |
| Bokšić, slot 10 | `46 2 95 96 93 98 7 9 11 8 10` | **93** no lugar da 97 | 4; "armband, long sleeve"; "long sleeve, left, captain"; "…under the armband" |
| Balaban, slot 10 | `46 2 95 96 97 98 7 9 11 8 10` | nenhuma | — |

A faixa e as mangas amostram a CLUT (0,487) e a página (640,256); as mangas 95, 96 e 98 caem nas
zonas "long sleeve, right", "elbow, right; long sleeve, right forearm" e "elbow, left; long sleeve,
left forearm", a 97 em "long sleeve, left", a 3 em "short sleeve, right; shoulder, first". É
exatamente o que o `arm_dress` da aba já faz desde G3 (`ARM_PIECES`, `SLEEVE_LENGTHS`,
`LONG_TO_SHORT`).

O **encaixe** das seções com as matrizes do jogo (`mean pixels off the frame, by section`) fica em
torno de 1 px no Balaban, inclusive nas quatro mangas (`95:1.03 96:0.97 97:0.97 98:0.92`). No Bokšić
passa de 9 px em algumas seções (slot 9: 5, 7, 8, 10, 11; slot 10: 95 e 96), e isso **não é
geometria**: nos dois quadros dele há um brasileiro sobreposto na tela — slot 9, `depth 6802, 4.0 px
off the axis: 34 2 3 5 4 6 …`; slot 10, `depth 3907, 63.9 px off the axis`, à frente dele — e os
quads do vizinho entram na caixa da figura. É também por isso que a CLUT (0,486), a paleta do
Brasil, aparece nas seções dele; o Balaban, sozinho no quadro, só amostra a (0,487).

### 5. A aba já desenha a faixa e as mangas como o jogo; o que difere é corpo, pose e cabeça

O confronto por histograma de cor (`--replay-confront`, a figura da aba contra os pixels do jogo sob
os quads da figura) registra, sem afirmar limite:

| Figura | Aba de costas | Aba de frente | O que a aba desenhou |
|---|---|---|---|
| Marcos, slot 9 | 0,548 | 0,501 | `--figure 1 --armband --number 1` |
| Marcos, slot 10 | 0,544 | 0,499 | idem |
| Bokšić, slot 9 | 0,406 | 0,365 | `--figure 0 --armband --number 11` |
| Bokšić, slot 10 | 0,413 | 0,385 | `… --long-sleeves` |
| Balaban, slot 10 | 0,393 | 0,375 | `--figure 0 --long-sleeves --number 20` |

(Nos focos de linha as duas abas são comparadas com **as costas** do jogo, a primeira captura; a
frente do jogo nunca foi comparada com a frente da aba — [CORR-K3D-034](/docs/tasks/kits-3d/CORR-K3D-034.md).)

Lado a lado (`replay-<slot>[-<K>]-frame.png` contra `-tab-*.png`), o que difere:

- **no goleiro, o corpo**: o jogo desenha a família 13 inteira — torso largo, mangas e luvas dessa
  família, a faixa sobre o braço dela, parado —, e a aba desenha o corpo do `EDT_MOD.BIN` na
  caminhada da `LOOKS SET`, com só a 92 posta no `upper arm b`;
- **no capitão de linha, a pose e a cabeça**: a faixa, as mangas, a cor, a paleta e a sombra batem;
  a aba está na caminhada da `LOOKS SET` e o jogo na corrida do replay; a aba tem uma cabeça só, de
  cabelo escuro, e o jogo uma por jogador (item 8).

Nada nas cinco capturas pede mudar a faixa ou a manga em si: posição na lista, zona do bitmap, CLUT
e modo de desenho são os que a aba já usa.

### 6. Pose parada, medida: a do replay é a corrida, vista de costas

Em todos os focos as matrizes da figura seguida diferem por **0** entre dois quadros (`still pose:
… differ by 0 … (limit 0)`); é a primeira pose parada medida no jogo (G7, a tela EDIT PL. NUM, era
negativa). A projeção do GTE é a mesma em tudo: H 1376, OFX 0, OFY 0. Cinco poses ficaram gravadas
com a projeção, em `work/kits-pose/`: `slot9-keeper-front.json`, `slot10-keeper-front.json` (o
goleiro de frente, zoom máximo), `slot9-focus3-first.json`, `slot10-focus3-first.json` (o Bokšić de
costas) e `slot10-focus2-first.json` (o Balaban de costas). Até aqui a aba tinha uma pose de partida
só, a do slot 5 (`core/match_pose.json`, caminhando), e usa a caminhada da `LOOKS SET`.

### 7. Os 22: a ordem do L2/R2 e o mapa painel ↔ número das duas páginas

`--replay-field` recarrega o state, toca L2 k vezes (cada toque um `press` que tem de mexer a tela;
mexeram de 0,0687 a 0,1416) e captura dois quadros inteiros depois de 60 quadros de pouso. Os dois
slots dão a **mesma tabela**, mudando só a manga:

| k | Quem | Cabeça | Raiz | Faixa | Painel (página, x, y) | Número |
|---|---|---|---|---|---|---|
| 0 | Marcos, de frente, zoom máximo (4681) | 34 | 13 | 92 | — | — |
| 1 | a bola (o Marcos a 6059 no slot 9, 5012 no 10; fora do eixo) | 34 | 13 | 92 | — | — |
| 2 | Balaban | 46 | 2 | — | (640, 80, 104) | 20 |
| 3 | **Bokšić** | 46 | 2 | **90** / **93** | (640, 60, 104) | 11 |
| 4 | | 24 | 2 | — | (640, 40, 104) | 10 |
| 5 | | 47 | 2 | — | (640, 20, 104) | 8 |
| 6 | | 34 | 2 | — | (640, 0, 104) | 7 |
| 7 | | 24 | 2 | — | (640, 80, 80) | 3 |
| 8 | | 34 | 2 | — | (640, 60, 80) | 4 |
| 9 | | 24 | 2 | — | (640, 40, 80) | 14 |
| 10 | | 28 | 2 | — | (640, 20, 80) | 5 |
| 11 | | 46 | 2 | — | (640, 0, 80) | 2 |
| 12 | goleiro da Croácia | 24 | 13 | — | (640, 100, 104) | 1 |
| 13 | | 34 | 2 | — | (576, 80, 104) | 9 |
| 14 | | 34 | 2 | — | (576, 60, 104) | 11 |
| 15 | | 34 | 2 | — | (576, 40, 104) | 10 |
| 16 | | 34 | 2 | — | (576, 20, 104) | 2 |
| 17 | | 32 | 2 | — | (576, 0, 104) | 6 |
| 18 | | 34 | 2 | — | (576, 80, 80) | 16 |
| 19 | | 34 | 2 | — | (576, 60, 80) | 7 |
| 20 | | 34 | 2 | — | (576, 40, 80) | 4 |
| 21 | | 34 | 2 | — | (576, 20, 80) | 3 |
| 22 | | 24 | 2 | — | (576, 0, 80) | 5 |
| 23 | Marcos de novo, como no k = 0 | 34 | 13 | 92 | — | — |
| 24 | a bola | 34 | 13 | 92 | — | — |

O que a tabela diz:

- **A ordem do L2**: do Marcos à bola, depois os dez de linha da Croácia, o goleiro croata, os dez de
  linha do Brasil, o Marcos de novo e a bola. Dentro de cada time a grade de painéis anda **de trás
  para frente**: (80,104), (60,104) … (0,104), (80,80) … (0,80), e por fim o goleiro em (100,104).
  **R2 é o mesmo laço ao contrário** (`--field-button R2`): do Marcos direto ao Brasil de (0,80) a
  (80,104), o goleiro croata, a Croácia de (0,80) a (80,104), e só no fim a bola (k = 22). São 22
  jogadores, nenhum expulso; o juiz exige 20 de linha, 2 goleiros e 0 outras figuras
  ([CORR-K3D-030](/docs/tasks/kits-3d/CORR-K3D-030.md)).
- **Painel ↔ número**, pelas páginas de uniforme lidas da VRAM (`read_panels`): Brasil (576):
  `5 3 4 7 16` na linha 80, `6 2 10 11 9` na 104, e o 1 do goleiro em (100,104); Croácia (640):
  `2 5 14 4 3` na linha 80, `7 8 10 11 20` na 104, e o 1 em (100,104). A ordem da grade não é a dos
  números, como já se via no slot 5 (§4.7 do PLAN-KITS-PY).
- **Toda costa de jogador de linha amostra duas células**: a própria e a (0,80), compartilhada por
  todos os de linha da página (`the cell every outfield back of a page also samples: page 576
  0,0,80; page 640 0,0,80`); o painel de cada um é a que sobra — ou a (0,80) para quem a ocupa
  (k = 11 e k = 22).
- **A manga é por slot**: curta (3–6) nos 20 de linha do slot 9, longa (95–98) nos 20 do 10, sem
  divergência por jogador; os goleiros são família 13 nos dois.
- **O capitão de cada time**: o Bokšić é o k = 3 nos dois slots (90 no 9, 93 no 10, painel (60,104),
  número 11); o Marcos é o k = 0 (e o 23), família 13 com a 92. O goleiro croata (k = 12) é família
  13 **sem** faixa; nenhum jogador de linha do Brasil usa faixa.

### 8. A cabeça é por jogador: seis seções para 22, iguais nos dois slots

`heads: 24 on 640/10 640/3 640/14 640/1 576/5; 28 on 640/5; 32 on 576/6; 34 on 640/7 640/4 576/9
576/11 576/10 576/2 576/16 576/7 576/4 576/3 None/None; 46 on 640/20 640/11 640/2; 47 on 640/8`
(página/número): seis seções de cabeça — 24, 28, 32, 34, 46 e 47 — e cada jogador mantém a sua no
slot 10. A cabeça não é da figura nem do time: a 34 aparece nos dois times e no Marcos; o Balaban
(20) e o Bokšić (11) usam a 46; o goleiro croata a 24.

E a **mesma seção sai com CLUT diferente** por jogador: a 46 do Bokšić amostra (128,480) nos dois
slots (`46: 14 prim(s), … CLUT (128,480)`); a 46 do Balaban, (32,480) e (160,480); a 34 do Marcos,
(32,480) e (160,480). Na tela o Bokšić é loiro e o Balaban castanho. A aba desenha uma cabeça só,
de cabelo escuro, nas duas figuras.

### 9. A câmera do replay, medida

- De frente, no zoom máximo (k = 0), o goleiro está a 4681 (slot 9) e 4682 (slot 10) de profundidade,
  ~60 px de altura em 256×192.
- Com L2 a câmera vai para **as costas** do jogador seguido, a uma distância só (4676–4715 no slot 9,
  4685–4729 no 10), e o mantém **no eixo** (0,0–4,4 px de deslocamento). Por isso o painel do número
  sai sem girar, e é a frente que pede o giro.
- **R1/L1** giram de 8 a 12 graus por toque; o goleiro ficou de costas em 18 toques (slot 9) e 14
  (slot 10), o Bokšić de frente em 17 e 16, o Balaban em 15.
- **Quem é o seguido** atrás de um jogador é a figura no eixo, não a mais perto da câmera: no slot 9,
  k = 21, o vizinho está a 2584 e o seguido a 4692; no k = 9, o vizinho está a 1,9 px do eixo mas a
  20692. A margem do juiz pede a figura seguinte a 8 px a mais do eixo **ou** a 1000 de profundidade;
  o par mais apertado dos três laços é o próprio Bokšić no slot 9 (`closest next figure inside 8 px:
  focus 3, 3.46 px farther off the axis and 2108 apart in depth`).
- Cada foco corre de 64 a 67 quadros do último toque ao fim da captura, sob os 390 do timeout.

### 10. Negativas, com comando e saída

- família 56 e braçadeiras 91/94: não vistas em dois states e 22 jogadores (`--replay`, `--replay-field`);
- Gouraud, textura crua, semitransparência: `0 shaded, 0 raw, 0 semi` em toda seção de toda figura;
- `--keeper-armband 9`: sai 1 (`0 whole and 49 cut figure(s)`), porque o zoom máximo deixa uma figura
  só no quadro;
- a planta do `--replay` sem `--focus` nunca alcança a conferência de raiz com dado real (uma figura
  por quadro); só a do Bokšić alcançou;
- a frente do jogo nunca foi comparada com a frente da aba (os focos de linha só capturam as costas de
  primeira);
- a segunda corrida de cabeças do `MODEL.BIN` (seções 74 a 105) não apareceu em nenhum dos 22.

## O que as treze correções mudaram no instrumento

Os grupos de causa raiz estão no [retro](/docs/tasks/kits-3d/retro.md): 13 das 35 correções do
ciclo caíram na fase 7, e as três de severidade alta (020, 026, 030) nas investigações no emulador;
as armadilhas K1 a K5 que o retro gravou em
[perfil-kits-3d.armadilhas.md](/docs/prompts/perfil-kits-3d.armadilhas.md) e a quinta regra de
"Convenções da documentação" do [CLAUDE.md](../CLAUDE.md) saíram delas. Aqui fica só o que o ciclo
novo reaproveita como **método**:

- **Linhas que as opções passaram a imprimir** — cada uma era uma sonda ou um número de memória:
  `idle N` nas linhas `front:` e `turn:` (023); `front:`/`back:` de painel (025); `whole frames per
  capture` e a coluna `still` em todo foco (026: eram 7 submits e 23 dos 25 focos saíam com um quadro
  só — cada quadro manda três listas à GPU e só uma tem figuras; passaram a 9); `closest next figure
  inside 8 px…` e `frames from the last tap…` (029); a contagem de 20 de linha, 2 goleiros e 0
  outras figuras no juiz do laço (030: uma tabela de 3 focos dava `ok`); `every figure of the last
  frame, nearest the axis first` (035).
- **Regras de captura que ficaram**: o seguido atrás de um jogador é a figura no eixo, com margem
  (024, aplicada na 18); o painel é lido só nos quads dentro da caixa do próprio torso, e a célula
  compartilhada é descontada (18); as paradas do giro não leem o GTE, e emprestam a projeção da
  primeira captura (19); o kit se acha pela paleta amostrada (19); um **controle físico ligado**
  vaza no fork pelo `[Pad1] = SDL-0` e dá `still 282` sem toque — `fork.refuse_joysticks` recusa a
  corrida antes de subir o emulador (031).
- **O que o retro aponta e ainda vale para a ferramenta nova**: o esperado é constante por (slot,
  foco), não lido da captura (K1); a planta derruba a asserção que diz cobrir, com dado real (K2); a
  linha `$` traz toda flag, inclusive `--frame-json` (K3).
- Os controles plantados foram de 43 a 53 `red` ao longo das três tasks, com `ctest -R kits` 4/4 em
  todas.

## Descobertas novas para o desenho 3D

Cada item diz o que foi visto, a regra já medida em outro ciclo que o explica, o que a aba faria com
isso, e o que falta medir.

### (a) Cabelo, barba e pele do jogador vêm da CLUT da cabeça, pela regra da LOOKS SET

O ciclo `looks` mediu como a tela `LOOKS SET` pinta a cabeça
([layout.py](../tools/looks/layout.py)): as quatro paletas de pele são as linhas 480 a 483 da VRAM,
uma por valor de `skin_colour` (`SKIN_PALETTES`); dentro de cada linha, a coluna de 16 entradas é o
que o `skin.grid` chama de janela (x/16); a coluna 0 é a pele nua (`BARE_SKIN_COLUMN`), a coluna
`1 + hair_colour` é a cor do cabelo (`HAIR_COLUMN`, A–H) e a `9 + beard_colour` a da barba
(`BEARD_COLUMN`, sete valores).

As CLUTs que o `--replay --focus` imprimiu leem-se por essa regra:

| Jogador | Cabeça | CLUT impressa | Linha → pele | Coluna → cor |
|---|---|---|---|---|
| Bokšić (slots 9 e 10) | 46 | (128,480) | 480 → A | 8 → cabelo H |
| Balaban (slot 10) | 46 | (32,480), (160,480) | 480 → A | 2 → cabelo B; 10 → barba B |
| Marcos (slots 9 e 10) | 34 | (32,480), (160,480) | 480 → A | 2 → cabelo B; 10 → barba B |

**Hipótese:** essas são as três bits de `hair_colour`, `beard_colour` e as duas de `skin_colour` do
registro de 12 bytes do jogador — o que o [Player.cpp](../src/core/Player.cpp) decodifica
(`hair_colour = (raw_attributes[1]>>1)&0x07`, …) e o `tools/looks/looks.py decode()` lê do disco
(`layout.PLAYER_RECORD_OFFSET`, 1449 registros em `/SELECT.BIN`). Não foi medido: a task que confirma
lê o registro dos três jogadores no disco e bate com as colunas da tabela. Se bater, a aba ganha o
que hoje lhe falta: desenhar a cabeça de **qualquer jogador real** — o `core/figure.py:scene_of`
chama `scene.build(files, looks.parse_tuple(TUPLE), …)` com uma tupla fixa
(`TUPLE = assembly.CORPUS_REFERENCE`); a tupla do jogador no lugar dela é a mudança.

### (b) A seção da cabeça é o estilo de cabelo, e a tabela já existe

O `looks` mediu em que seção do `MODEL.BIN` cada estilo da linha HAIR desenha
(`assembly.HAIR_MAP`, [assembly.py](../tools/looks/assembly.py)): a letra do estilo é a seção —
A = 24, B = 26, C = 30, D = 48, E2 = 54, F = 52, G = 28, H = 42, I = 34, J = 36, K = 32, L = 46,
M = 38, N = 40, O = 44, P = 50 — e o dígito é a faixa da folha de cabelo. As seis cabeças vistas em
campo cabem nela: 24 = A, 28 = G, 32 = K, 34 = I (o Marcos), 46 = L (Bokšić e Balaban). A **47** é
a seção ímpar seguinte da 46, que o `looks` chama de *twin*: é a mesma cabeça desenhada quando a
barba é F ou G (`FACE_TWINS`). Ou seja, o jogador k = 5 da Croácia (nº 8) tem o estilo L e barba F ou
G — hipótese pela mesma regra, a medir junto com (a). A segunda corrida de cabeças (74–105), que o
`looks` nunca viu mover, não apareceu em campo.

### (c) A pose de corrida está gravada, e o `ANIME.BIN` pode ser a fonte dela

As cinco poses de `work/kits-pose/` são a corrida do replay, de costas (focos de linha) e de frente
(goleiro). O `ANIME.BIN` guarda 204 animações, e `tools/looks/anime.py --against-pose` liga uma
captura ao par que o jogo estava lendo (medido no `looks` para a caminhada: 408 de 408 peças). O
caminho para a aba posar o boneco "correndo" sem depender de uma captura congelada é esse: achar a
animação e o quadro da corrida no arquivo, e posar a família 2 por ele, como hoje se posa a caminhada
da `LOOKS SET`. Falta medir se as capturas de replay carregam o ponteiro do par (o `pose_capture`
não o lê; o `--pose` do `looks` lê).

### (d) O goleiro do jogo é a família 13 inteira

Torso 13, braços 14/16 e 15→92/17, pernas 18/20/19/21, cabeça por jogador. A aba desenha o goleiro
do `EDT_MOD.BIN` com só a 92 trocada, e é a maior diferença visível das três tasks (item 5).
Desenhar o goleiro pela família 13, com a pose `slot9-keeper-front.json` e a projeção medida, é a
mudança que aproxima o desenho do jogo — e reabre a decisão da
[K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md), que tirou a figura de partida do seletor. É
decisão do usuário, já registrada no G8.

### (e) Dois kits na VRAM ao mesmo tempo, e o kit pela paleta

Na partida as páginas (576,256) e (640,256) carregam os dois times, cada um com a sua paleta de
jogador e de goleiro, e as bandeiras ao lado. O `figure_tag` já resolve o kit de uma figura pela
CLUT que ela amostra. É a base para uma vista com os dois times — ou os 22 — na aba, sem nada novo
de formato.

### (f) O painel do número, fechado

Goleiro: painel fixo na seção 13, em (100,104). Jogador de linha: a célula própria e a (0,80)
compartilhada. O `numbered_scene` da aba já pinta a célula própria pela regra do §4.7; nada a mudar.
Saber da célula compartilhada evita contar quads "a mais" ao comparar a aba com o jogo.

### (g) A câmera "replay" como preset da aba

H 1376, OFX e OFY 0; o jogador a 4681 de frente (zoom máximo) e a ~4700 de costas; giro de 8 a 12
graus por toque. A aba hoje desenha em projeção ortográfica (`raster.draw`), então reproduzir a
vista do jogo pede projeção perspectiva com esses números — candidato, não pedido.

### (h) O que não muda

Faixa, mangas, cor, paleta e sombreamento: fechados pelas três tasks. Nenhuma task de conserto
precisa mexer neles.

## Diagnóstico: o que dos replays muda o desenho da aba 3D?

**Sombra, cor e faixa estão certos; o que falta é corpo, pose e cabeça.** As cinco capturas de perto
dizem que a aba já amostra os mesmos texels, pelas mesmas CLUTs, nas mesmas zonas e sem sombreamento
— como o jogo. O que a separa do jogo é geometria e pose (o goleiro inteiro; a corrida) e um dado por
jogador (a cabeça).

| Achado | Valor para a aba | Uso |
|---|---|---|
| Todo quad plano, pixel = texel, paleta 0 de 256 | **Confirmação.** O `core/raster.py` já faz o que o jogo faz | nenhuma mudança |
| 90 no lugar da 4, 93 no lugar da 97, 95–98 a 1 px | **Confirmação** de G3/`ARM_PIECES`, agora de perto e nas duas mangas | nenhuma mudança na faixa nem nas mangas |
| Goleiro = família 13 inteira, 92 no lugar da 15; 56/91/94 não vistas | **Novo, e muda o desenho.** A aba desenha outro corpo | desenhar o goleiro pela família 13 com a pose medida (reabre a K3D-TASK-10) |
| Cabeça por jogador, seis seções, CLUT por jogador | **Novo, e muda o desenho.** A aba tem uma cabeça só | cabeça pela tupla do jogador (`HAIR_MAP`, pele/cabelo/barba pela CLUT) — depois de confirmar (a) |
| Pose de corrida gravada, projeção H 1376 | **Novo.** Segunda pose de partida medida | posar pelo `ANIME.BIN` (c), ou pela captura |
| Ordem do L2/R2, mapa painel ↔ número das duas páginas, célula compartilhada | **Confirmação** do §4.7, agora nos 22 | nenhuma mudança; serve de regra ao leitor de replay |
| Dois kits lado a lado na VRAM, kit pela paleta | **Novo, mas de instrumento** | vista de dois times, se for pedida |
| Câmera do replay (4681/~4700, 8–12° por toque) | **Novo, cosmético** | preset de câmera, se a aba ganhar perspectiva |
| Família 56, Gouraud, semitransparência, frente contra frente | **Negativas** | nenhum |

**Recomendação.** Ordem sugerida de tasks para o ciclo novo, do que mais aproxima a aba do jogo ao
que menos:

1. **Cabeça por jogador.** Primeiro medir (a) e (b): ler o registro dos três jogadores no disco e bater
   com as CLUTs e seções do replay (uma task de investigação, barata: as capturas já existem). Depois
   desenhar a cabeça com a tupla do jogador no `scene_of`.
2. **Goleiro pela família 13**, com `slot9-keeper-front.json` e a projeção medida — decisão do
   usuário sobre a K3D-TASK-10, e implementação.
3. **Pose de corrida pelo `ANIME.BIN`** (c): ligar as capturas ao par do arquivo e posar a família 2.
4. **Jogador real no seletor**: time, número (`SquadNumbers`), capitão (`Team.captain`) e cabeça —
   o que faz as três de cima virarem uma vista do jogador que o usuário escolhe.
5. **Câmera "replay"** (g), opcional.
6. **A ferramenta de leitura** (abaixo), que serve de instrumento às quatro primeiras e barateia toda
   investigação seguinte.

## Uma ferramenta de leitura do jogador no replay

### O que existe, e onde aperta

Tudo o que as três tasks mediram passa por [oracle.py](../tools/kits/oracle.py): 4.769 linhas, das
quais cerca de 1.300 são o bloco G8 —

- **captura** (sobe o emulador): `replay_capture`, `replay_arrive`, `replay_field_capture`, sobre
  `pose_capture` e `matrix_stops` (breakpoints em `POSE_PIECE_MATRIX` e `GPU_LIST_SUBMIT`, leitura
  das listas da GPU da RAM, VRAM por `vram_region`);
- **análise** (pura, sobre a captura): `replay_figures`, `figure_depth`, `figure_off_axis`,
  `replay_focus`, `field_focus`, `pose_change`, `figure_group`, `piece_box`, `section_samples`,
  `shading_of`, `colour_confront`, `panel_samples`, `panel_cell`, `field_panels`, `field_number`,
  `sleeves_of`, `armband_of`, `figure_tag`;
- **juízes e plantas**: `replay_judge`, `replay_field_judge`, `REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`.

O que aperta, para um agente de IA e para quem lê na linha de comando:

- **tudo imprime prosa.** A única saída estruturada é o arquivo de captura (`replay-*.json`), cujo
  schema é implícito — chaves `focus/front/back/events/lists/offsets/buffer/texture/pages/hits/
  yaws/depths/turned/front_frames/back_frames/turn_frames` — e cujas tuplas viram listas no JSON
  (`_restore_samples` as repõe). Cada pergunta nova sobre uma figura é reler 300 linhas de saída ou
  escrever uma sonda — e sonda foi a origem das [CORR-K3D-029](/docs/tasks/kits-3d/CORR-K3D-029.md)
  e [035](/docs/tasks/kits-3d/CORR-K3D-035.md);
- **o custo está na captura, não na análise**: minutos de emulador por foco, segundos para reler.
  Uma ferramenta que separe as duas coisas deixa o agente perguntar quantas vezes quiser sobre uma
  captura já feita;
- **uma opção por pergunta** (`--replay`, `--replay-field`, `--replay-confront`, mais os `--plant-*`)
  num `argparse` de modos exclusivos; não há como pedir "a figura k do quadro, seção 93, em JSON".

Vale a pena: as quatro primeiras tasks recomendadas acima começam todas lendo uma captura de replay
(cabeça, CLUT, pose, família), e cada uma repetiria o mesmo trabalho de leitura.

### Projeto

Duas camadas, reaproveitando o código por **move**, não por cópia — o `oracle.py` passa a importar
a primeira e fica com o que é gate:

**1. `tools/kits/core/replay.py` — o leitor, puro.** Sem emulador, sem `tools/looks/oracle`; só
`layout`, `section`, `skin`, `assembly` e o `core` do kits. Entra no `selftest.py` com os casos
sintéticos que hoje estão no bloco `oracle --replay` e `--replay-field` (eles migram, não se
duplicam).

- `Capture.load(path)` — lê um `replay-*.json`, repõe as tuplas, valida o `schema` e as chaves;
  `Capture.frames()` → `Frame` (lista `figures`, `head` da lista da GPU, offset de desenho);
- `Figure` — `order` (cabeça primeiro), `root`, `head`, `family` (`outfield` 2, `goalkeeper` 13,
  `other`), `sleeves`, `armband`, `depth`, `off_axis`, `pieces` (seção, rotação, translação,
  projeção), `pose()` (o JSON de `work/kits-pose/`), `box(index)`;
- `Figure.sections(index)` → por seção: primitivas, `shaded/raw/semi`, CLUTs, páginas, zonas, erro de
  encaixe em pixels, e — com o frame buffer da captura — `far` puro e modulado;
- `Figure.panel(pages)` → células amostradas, célula própria (descontada a compartilhada), número;
- `Figure.head()` → estilo pela `HAIR_MAP` (e o *twin*), pele pela linha da CLUT, cabelo e barba
  pela coluna (`skin.grid`, `HAIR_COLUMN`, `BEARD_COLUMN`) — a regra de (a) e (b), marcada como
  hipótese até a task que a confirma;
- `Walk.load(path)` → a tabela dos 22 de um `replay-field-*-capture.json`, foco a foco, com a
  ordem e o mapa painel ↔ número;
- `judge(figure, expect)` e `judge_walk(rows, expect)` — os juízes de hoje, sobre esses objetos.

**2. `tools/kits/replay.py` — a linha de comando.** Subcomandos, na convenção do `cli.py`; **`--json`
em todo leitor**, com `"schema": "kits-replay/1"` e chaves fixas (é o contrato com o agente); saída
humana curta por padrão.

| Subcomando | O que responde | Emulador |
|---|---|---|
| `capture --slot 9 [--focus K] [--turn R1\|L1] [--walk L2\|R2] [--out DIR]` | faz a captura: recarga do state, toques, pouso, `pose_capture`, VRAM; guarda `replay-*.json` | sim |
| `figures <captura>` | toda figura do último quadro: profundidade, deslocamento do eixo, ordem, família, time pela paleta | não |
| `figure <captura> [--on-axis\|--nearest\|--nth N] [--section S]` | a figura seguida, seção a seção (ou uma seção só) | não |
| `head <captura> [--player <registro>]` | estilo, pele, cabelo e barba decodificados; com `--player`, contra o registro do disco | não |
| `pose <captura> [--write pose.json] [--against-anime]` | a pose com a projeção; o par do `ANIME.BIN` que a explica, se houver | não |
| `panel <captura>` | células amostradas, painel e número | não |
| `walk <captura-do-laço>` | a tabela dos 22, a ordem e o mapa painel ↔ número | não |
| `confront <captura> [--tab] [--section S]` | pixel do jogo contra texel puro e modulado; com `--tab`, a aba por histograma (sobe o `app.py`) | não (o `--tab` sobe a aba) |
| `show <captura> --png out.png [--section S \| --box]` | o recorte do frame buffer do jogo e a figura desenhada pelo `core/raster` na pose capturada, lado a lado — para **olhar**, sem Qt | não |
| `describe <captura>` | o resumo de uma tela: quem é seguido, família, faixa, manga, cabeça, painel, pose parada, o que a planta diria | não |

Guardas do `capture`, herdadas do que as tasks mediram: `fork.refuse_joysticks` antes de subir;
o timeout de 390 quadros como limite de toda sequência; 9 submits por captura (dois quadros inteiros);
foco pelo eixo com a margem (8 px ou 1000) atrás de um jogador, menor z no zoom máximo; projeção da
primeira captura emprestada ao giro; kit pela paleta.

**3. O `oracle.py` fica com os gates**: `REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`, as plantas e os
controles, chamando o `core/replay`. O `--frame-json` continua funcionando — é o mesmo arquivo.

### Custos e limites a escrever na task

- captura: 10 a 40 minutos por corrida (relógio observado), com `frame_step` a ~57 ms por chamada
  (armadilha 34 do PLAN-PES2-PSX); releitura: segundos;
- no zoom máximo há uma figura só por quadro; atrás de um jogador, de 1 a 17; a última peça de cada
  quadro fica sem nome (atraso de desenho);
- as capturas de hoje são o schema v0: o `Capture.load` as aceita e as migra para o v1 (chaves
  `schema`, `slot`, `focus`, `button`, `taps`, e as tuplas tipadas);
- a frente de um jogador de linha só existe depois do giro, e a frente da aba só se compara com ela se
  o `confront` ganhar a captura girada como entrada.

### Verificação da ferramenta, já sob as armadilhas do retro

- `selftest`: os leitores sobre as cinco capturas em `work/kits-oracle/` (o digest de cada uma no
  Log da task), e os casos sintéticos migrados do `oracle`;
- o `--json` de `figure` reproduz, campo a campo, o que a linha `ok` do `oracle.py --replay
  --frame-json` afirma, nas cinco capturas;
- o esperado por (slot, foco) é constante, nunca lido da captura (K1); cada asserção nova entra com
  uma planta que derruba **essa** asserção com dado real, e o Log mostra a linha (K2); toda linha `$`
  do Log traz as flags da corrida, inclusive `--frame-json` (K3);
- um controle por leitor novo no `controls.py`; `ctest -R kits` 4/4.

### O que muda para quem pergunta

| Pergunta de um agente | Hoje | Com a ferramenta |
|---|---|---|
| "Que seção é a faixa do jogador 3, e com que CLUT?" | `--replay 9 --focus 3 --frame-json …`, 60 linhas de saída, achar a linha `90:` | `replay figure replay-9-3.json --section 90 --json` |
| "Quem está no quadro além do seguido?" | a linha `every figure…` (só existe desde a CORR-035) | `replay figures replay-9-3.json --json` |
| "De que cor é o cabelo do seguido?" | sonda sobre a CLUT, à mão | `replay head replay-9-3.json --json` |
| "Como está a figura, vista de lado?" | abrir o `app.py` no `:98` e exportar | `replay show replay-9-3.json --png out.png` |
| "O que mudou entre duas corridas?" | `diff` de saídas de prosa | o mesmo `--json` nas duas, e um `diff` |
