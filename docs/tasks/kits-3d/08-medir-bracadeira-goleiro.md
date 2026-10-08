---
id: K3D-TASK-08
---

# K3D-TASK-08 — Medir a braçadeira do goleiro no emulador

## Goal

Fica medido se, e como, o jogo desenha a braçadeira de capitão no goleiro (seção, peça trocada, mangas curta e longa).

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
  - `docs/KITS-AJUSTES-3D.md` (G4)
- Out: desenhar na aba (é a K3D-TASK-11)

## Done criteria

- [x] a regra (ou a negativa) está em G4 com o comando do `oracle.py` colado da HEAD
- [x] controle plantado no catálogo, visto vermelho
- [x] sem save state de goleiro capitão: `rite mark K3D-TASK-08 blocked --unblocked-by "test -f work/kits-states/<slot do goleiro>.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Recursos: emulador e save-states. Como na KITS-TASK-43, o `oracle.py --attach` serve de ponto de partida.

**Save state do goleiro capitão: slot 7** (usuário, 2026-10-08). A partida é Brasil x China, e o
goleiro do Brasil é o capitão. No momento do save, ele está com a bola. Hoje o arquivo está em
`~/.local/share/duckstation/savestates/SLPM-87056_7.sav`, e a cópia mestra fica em
`work/kits-states/SLPM-87056_7.sav`, ao lado dos slots 3 a 6 (copiada em 2026-10-08, ver o Log).

## Log de Execução

### 2026-10-08 — slot 7: braçadeira do goleiro medida

O state do slot 7 foi copiado para `work/kits-states/SLPM-87056_7.sav` (sha256 `91c8e2b4…cc1e`), a
cópia mestra que o `load_slot` restaura.

**Medido:** o goleiro de manga longa desenha a braçadeira como seção 92, no lugar da 15. A regra está
em [G4](/docs/KITS-AJUSTES-3D.md#g4--number-captain-armband-e-long-sleeves-em-qualquer-combinação-nas-duas-figuras),
com a saída colada.

- Ao vivo, `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY= python3 tools/kits/oracle.py --keeper-armband 7`:
  - `x23  34 13 14 16 92 17 18 20 11 19 21 12`;
  - `ok    the goalkeeper opened at section 13 draws section 92 in place of 15`, `rc=0`.

  A captura `work/looks-shots/matrix-7.png` mostra Marcos (GK nº 1, Brasil) com a bola nos pés.
- A planta `--plant-keeper-armband` sai `rc=1`, com
  `FAIL  no figure opened at section 13 draws section 103`.
- Os quatro casos `oracle --keeper-armband: …` do `selftest.py` dão `ok`.
- Controle `RED    oracle-keeper-armband-unasked kits/oracle.py :: keeper_armband_judge`
  (`python3 tools/kits/controls.py --only oracle-keeper-armband-unasked`).
- `--attach-matrix 7` não serve aqui. Ele corta as figuras só nas raízes 2 e 56, e esse goleiro abre na
  13. O resultado é `FAIL  figure 0: a translation 1889 …` em todas as 22 figuras. O `--keeper-armband`
  corta em `KEEPER_ROOTS` (2, 56 e 13) e passa a raiz ao `matrix_passes`.

**Manga curta não existe para o goleiro** (usuário, 2026-10-08: "nesse jogo o goleiro só tem mangas
longas"). Por isso o caso medido cobre a braçadeira do goleiro, e a task não vai a blocked. Fica fora
da regra, registrado em G4: o goleiro capitão da família 56 (slots 5 e 6), nunca visto com a braçadeira.
Os candidatos por geometria, 91 e 94, aparecem na saída como `not drawn here`.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 35 of 35 red`.
- O critério de blocked não se aplica: há save state de goleiro capitão (slot 7).
- **Closed** — commit `8b73f96` (2026-10-08): feat(kits): measure the goalkeeper captain's armband in a match
  - Files (`git show --name-status 8b73f96`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
