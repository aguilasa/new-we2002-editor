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

- [ ] G7 tem a saída de `oracle.py --edit-number 8` e de `--edit-number 8 --player 1` coladas da HEAD, com os sete itens de G7 respondidos um a um (família e ordem das seções; kit, paleta e mangas; pose e câmera; o giro; o número nas costas; o jogador de linha), e toda negativa escrita como negativa, com comando e saída
- [ ] `--edit-number 8 --plant-edit-number` sai 1, com `FAIL` no juiz da família e no dos painéis; o controle novo do catálogo dá `RED` em `python3 tools/kits/controls.py --only <nome>`
- [ ] sem a cópia mestra: `rite mark K3D-TASK-16 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_8.sav"` e o pedido ao usuário
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

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
