---
id: K3D-TASK-16
---

# K3D-TASK-16 — Medir a tela EDIT PL. NUM no slot 8: modelo, número nas costas e giro

## Goal

Fica medido o que a tela EDIT PL. NUM desenha — família de modelo, kit e paleta, pose e câmera, o giro frente→costas e o número nas costas — no goleiro e num jogador de linha, ou a negativa de cada item. Só investigação: nada muda na aba 3D.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py` (`--edit-number SLOT [--player ROW]`, `--plant-edit-number`)
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G7: o medido, colado da HEAD)
  - fora do git: `work/kits-states/SLPM-87056_8.sav`, a cópia mestra do slot 8
- Out: desenhar qualquer coisa na aba (task nova, a partir do medido)

## Done criteria

- [x] G7 tem a saída de `oracle.py --edit-number 8` e de `--edit-number 8 --player 1` coladas da HEAD, com os sete itens de G7 respondidos um a um (família e ordem das seções; kit, paleta e mangas; pose e câmera; o giro; o número nas costas; o jogador de linha), e toda negativa escrita como negativa, com comando e saída
- [x] `--edit-number 8 --plant-edit-number` sai 1, com `FAIL` no juiz da família e no dos painéis; o controle novo do catálogo dá `RED` em `python3 tools/kits/controls.py --only <nome>`
- [x] sem a cópia mestra: `rite mark K3D-TASK-16 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_8.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Pontos de partida no `oracle.py`: `load_slot`, `matrix_stops` /
`matrix_pieces` / `matrix_passes` / `matrix_report` (`--attach-matrix`, `--keeper-armband`),
`read_back` / `read_panels` / `panels_judge` (`--back … --panels`), `run_match_pose`; no
`tools/looks/oracle.py`, `Oracle.press`, `camera_from_pieces`, `model_maps`,
`pointers_into_models`.

**Save state da tela: slot 8** (usuário, 2026-10-09). EDIT MODE → EDIT PL. NUM → seleção; o time é
o Brasil, e Marcos (GK nº 1) está selecionado, de frente. Ao confirmar um jogador, o boneco gira
para as costas e mostra o número. Captura do usuário em
`/home/ingmar/Pictures/2026-10-09_14-34.png`. Hoje o arquivo está em
`~/.local/share/duckstation/savestates/SLPM-87056_8.sav`; a cópia mestra vai para
`work/kits-states/SLPM-87056_8.sav`, ao lado dos slots 3 a 7, com o sha256 no Log.

Para o jogador de linha, `--player 1` desce uma linha (Edmilson, CB 5). Qual botão confirma
(Cross ou Circle) é medido com `Oracle.press`, que recusa um aperto que não muda a tela.

## Log de Execução

### 2026-10-09 — a tela medida nas duas figuras

A cópia mestra: `cp ~/.local/share/duckstation/savestates/SLPM-87056_8.sav work/kits-states/`, sha256
`ee349d74e26eef2cdb9f459ff2360dd15c4e0bdcf36677a9df242bf5b601a184` nos dois arquivos. O critério de
blocked não se aplica.

**Medido**, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`
e colado em [G7](/docs/KITS-AJUSTES-3D.md#g7--tela-edit-pl-num-o-jogo-desenhando-o-número-e-o-giro):

- `python3 tools/kits/oracle.py --edit-number 8`: `ok    the goalkeeper opens at section 34, Circle turned it -166 degrees in 30 frame(s), and its back panel holds number 1`, saída 0;
- `python3 tools/kits/oracle.py --edit-number 8 --player 1`: `ok    the player opens at section 24, Circle turned it -168 degrees in 30 frame(s), and its back panel holds number 5`, saída 0;
- os sete itens de G7 respondidos: família (`EDT_MOD.BIN`, listas 1 e 0; cabeças 34 e 24), kit (`TEX_41` conjunto 1 em (576,256), paletas 486/488), pose e câmera (**negativa**: a figura caminha; câmera não derivada), giro (Circle, 30 quadros a −5,6°), painel (regra do §4.7, escrito ao selecionar a linha, igual antes e depois do giro), jogador de linha (linha 1, número 5).
- Negativas também escritas: nenhuma seção 91/94; o Cross sai da tela.

**Controle:** `python3 tools/kits/oracle.py --edit-number 8 --frame-json work/kits-oracle/edit-8-0.json --plant-edit-number`
sai 1 com `FAIL  no figure opened at section 103`, `FAIL  panel (100,103): 290 pixel(s) are neither the shirt back nor a digit` e
`FAIL  panel (100,103): digits at [(7, 8)], the rule puts them at [(7, 7)]`. No catálogo:
`python3 tools/kits/controls.py --only oracle-edit-number-head-unasked` dá
`RED    oracle-edit-number-head-unasked kits/oracle.py :: edit_number_judge`. No `selftest.py`, os dez
casos `oracle --edit-number: …` dão `ok`.

Duas correções de instrumento no caminho, as duas na opção nova: o contador de giro contava o
balanço da caminhada (até 2° por quadro) como giro — o limiar é 3° e o giro é a primeira sequência
sem quebra; e o `Down` move só 0,0148 da tela, abaixo do 0,02 que o `press` do `looks` exige por
padrão (`EDIT_ROW_MOVED`).

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, `kits_ui: 0 failure(s)`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 38 of 38 red`.
- Varredura (`rite sweep`): só texto desta task e o `STATES_DIR` do `oracle.py`, que dizia "slots 3 to 5" e agora diz 3 a 7 e o 8.
