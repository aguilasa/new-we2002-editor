---
id: K3D-TASK-17
---

# K3D-TASK-17 — Medir o goleiro capitão de perto nos replays dos slots 9 e 10: a braçadeira como o jogo a desenha, família, painel e pose parada

## Goal

Fica medido, nos dois replays, como o jogo desenha o Marcos (goleiro, nº 1, capitão do Brasil) de perto: a família de seções e a braçadeira (92 na família 13, ou 91/94 na 56), a faixa e os braços primitiva a primitiva na lista do jogo (página, CLUT, zona, cor de vértice, modo), a pose parada com a projeção da câmera, o painel que o torso amostra e o número nas costas, e o confronto da nossa figura — `match_scene` com a pose do jogo, e a aba — contra o quadro do jogo nas caixas da faixa e dos braços. É investigação: a aba não muda; as diferenças que o confronto listar são a entrada da task de conserto.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py` (`--replay SLOT [--rotate L1|R1] [--frame-json]`, `--replay-idle SLOT`, `--replay-confront SLOT`, `--plant-replay`; `textured_samples` guardando cor de vértice e modo; entrada nova em `KEEPER_ARMBANDS` se a família for 56)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G8: o medido dos dois slots, colado da HEAD)
  - fora do git: `work/kits-states/SLPM-87056_9.sav` e `SLPM-87056_10.sav`, as cópias mestras
- Out: `tools/kits/core/*`, `tools/kits/ui/*` (o conserto é task nova); os 22 por L2/R2 (K3D-TASK-18); o Bokšić (K3D-TASK-19); andar o replay com Right/Left

## Done criteria

- [x] G8 tem a saída de `oracle.py --replay 9`, `--replay 10`, `--replay-idle 9`, `--replay-idle 10`, `--replay-confront 9` e `--replay-confront 10` coladas da HEAD, com os sete itens da K3D-TASK-17 em G8 respondidos um a um nos dois slots (família, ordem, cabeça e braçadeira; a faixa e os braços na lista; pose parada; costas, painel e número; o confronto), toda negativa escrita como negativa com comando e saída, e a lista das diferenças que o confronto apontou (texel/paleta, sombra, pose), para a task de conserto
- [x] se a família for 56: `KEEPER_ARMBANDS` ganha a entrada medida e a seção da faixa (91 ou 94) e a substituída saem impressas; se for 13: o juiz do `--replay` afirma a 92 no lugar da 15 (`REPLAY_EXPECT`), e a corrida de `--keeper-armband 9` fica colada em G8 — como negativa, se não cortar o quadro
- [x] `--replay 9 --plant-replay` (a segunda figura mais perto seguida, de frente e de costas, esperada na raiz 103) sai 1 com os `FAIL` da figura, da pose, do painel e do número; os controles novos do catálogo dão `RED` em `python3 tools/kits/controls.py --only <nome>`, e os casos novos do `selftest.py` dão `ok`
- [x] cada captura recarrega o state antes do aperto e corre menos quadros que o timeout medido por `--replay-idle`, e a saída diz os dois números
- [x] sem uma das cópias mestras (não se aplicou: as duas existem, sha256 no Log): `rite mark K3D-TASK-17 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Pontos de partida no `oracle.py`: `load_slot`, `matrix_stops` /
`matrix_pieces` / `matrix_passes` / `matrix_report` e `KEEPER_ROOTS` (`--attach-matrix`,
`--keeper-armband`), `run_keeper_armband` / `keeper_armband_judge` / `KEEPER_ARMBANDS` /
`same_vertices`, `pose_capture` / `textured_samples` / `walk_gpu_list` (`--match-pose`),
`run_match_silhouette` / `game_silhouette` / `drawn_silhouette` / `raster` (`--match-silhouette`),
`read_back` / `read_panels` / `panels_judge` (`--back … --panels`), `_edit_kit`, `edit_capture`
(recarga do state antes de cada aperto, `--frame-json`), `piece_yaw`, `figure_torso`, `edit_turn`;
no `confront.py`, `histogram` / `intersection` / `restrict` / `box_pixels`; no `core/figure.py`,
`match_scene` (aceita a pose de outro slot) e `screen_points`; no `ui/app.py`, `--export-3d` com
`--figure 1 --armband --number 1 --tag <Brasil> --yaw`.

**Os states: slots 9 e 10** (usuário, 2026-10-09). Replays parados de Brasil × Croácia, câmera no
Marcos, de frente, zoom máximo; no 9 os jogadores de linha estão de manga curta, no 10 de manga
longa; os goleiros, sempre longa. Hoje os arquivos estão em `~/.local/share/duckstation/savestates/`;
as cópias mestras vão para `work/kits-states/`, ao lado dos slots 3 a 8, com o sha256 de cada uma
no Log. O quadro de cada state se vê sem emulador com `python3 tools/pes2/savestate.py shot`.

Controles do replay: L2/R2 trocam o focado, L1/R1 giram a câmera, Up/Down zoom, Right/Left
segurados andam o replay (fora), e sem comando ele termina. Os apertos são toques
(`press_button` com `duration_frames`); sem a duração o botão fica preso. O focado é a figura de
menor z nas paradas (espaço da vista).

## Log de Execução

### 2026-10-09 — o goleiro capitão de perto nos dois replays

As cópias mestras: `cp ~/.local/share/duckstation/savestates/SLPM-87056_{9,10}.sav work/kits-states/`,
sha256 `54c7979296a6652118607973232b84f9e030f9edc7d7e8cd68bc95607dc0d6d6` (9) e
`bdf47644500f39dc7be313f0bc5a142fd3af7cebfd1c2ffa3a325c5389503b6e` (10), iguais nos dois lugares. O
critério de blocked não se aplica.

**Medido**, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`
e colado em [G8](/docs/KITS-AJUSTES-3D.md#g8--replays-nos-slots-9-e-10-braçadeira-e-manga-longa-de-perto-o-goleiro-capitão-e-os-22-em-campo):

- `python3 tools/kits/oracle.py --replay-idle 9` e `10`: `left after 390 frame(s) with no input`, saída 0 nos dois;
- `python3 tools/kits/oracle.py --replay 9` e `10`: `ok    the followed figure opens at section 13 with head 34, draws 92 in place of 15, holds still, and its back shows panel (576, 100, 104) with number 1`, saída 0 nos dois;
- `python3 tools/kits/oracle.py --replay-confront 9` e `10`: paleta `256 entries, 0 differ`; histograma da aba contra o jogo 0,50 de frente e 0,54 a 0,55 de costas;
- todo quad do goleiro sai plano com a cor (127,127,127), e o pixel do jogo é o texel puro: **cor, paleta e sombreamento não são a diferença; o corpo e a pose são** (a família 13 do `MODEL.BIN` no jogo, o `EDT_MOD.BIN` caminhando na aba). A pose parada da família 13 fica em `work/kits-pose/slot<slot>-keeper-front.json`.
- Negativa: `--keeper-armband 9` sai 1 (`0 whole and 49 cut figure(s)`), porque o quadro do replay tem só o goleiro e a última peça nunca é nomeada; o juiz do `--replay` é quem afirma a 92.

**Controle:** `python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json --plant-replay`
sai 1 com `FAIL  no second figure in the frame`, `FAIL  the pose changed by None between two frames, over 0`,
`FAIL  the back samples panel None, not (576, 100, 104)` e `FAIL  the panel holds None, not 1`. No catálogo,
`controls.py --only` dá `RED` em `oracle-replay-focus-unasked`, `oracle-replay-colour-unread` e
`oracle-replay-modulation-ignored`. No `selftest.py`, os dez casos `oracle --replay: …` dão `ok`.

Correções de instrumento no caminho, todas na opção nova:

- a tela inteira não serve para medir o timeout, porque as bandeiras da torcida mexem 0,0357 em 150 quadros. Quem mede é a placa "SAVE" (`REPLAY_HUD`);
- o agrupamento por primitiva de kit (`players`) partia o goleiro desenhado de perto, e o grupo passou a ser a caixa da própria figura projetada (`figure_group`);
- o offset de desenho vem na lista de um nó, não na tabela de ordenação;
- um pixel conta para a última primitiva que o cobre na ordem da lista;
- no giro, o foco fica preso à raiz do goleiro, e a leitura é de 36 paradas, ou 300 só se o goleiro não estiver nelas. Com 300 a cada toque, o slot 10 recuou a câmera para 12636 no 14º toque e o R1 parou de mexer.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 43 of 43 red`.

