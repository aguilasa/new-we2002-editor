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

- [ ] G8 tem a saída de `oracle.py --replay 9`, `--replay 10`, `--replay-idle 9`, `--replay-idle 10`, `--replay-confront 9` e `--replay-confront 10` coladas da HEAD, com os sete itens da K3D-TASK-17 em G8 respondidos um a um nos dois slots (família, ordem, cabeça e braçadeira; a faixa e os braços na lista; pose parada; costas, painel e número; o confronto), toda negativa escrita como negativa com comando e saída, e a lista das diferenças que o confronto apontou (texel/paleta, sombra, pose), para a task de conserto
- [ ] se a família for 56: `KEEPER_ARMBANDS` ganha a entrada medida e `--keeper-armband 9` sai 0 com a seção da faixa (91 ou 94) e a substituída impressas; se for 13: `--keeper-armband 9` sai 0 confirmando a 92, e a saída está colada em G8
- [ ] `--replay 9 --plant-replay` sai 1 com três `FAIL` (foco na raiz 103; painel lido uma linha acima; foco trocado pela segunda menor z); os controles novos do catálogo dão `RED` em `python3 tools/kits/controls.py --only <nome>`, e os casos novos do `selftest.py` dão `ok`
- [ ] cada captura recarrega o state antes do aperto e corre menos quadros que o timeout medido por `--replay-idle`, e a saída diz os dois números
- [ ] sem uma das cópias mestras: `rite mark K3D-TASK-17 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

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
