---
id: KITS-TASK-33
---

# KITS-TASK-33 — Aba Diagnóstico: a lista de `kit.problems`

## Goal

A aba lista os problemas da guarda de forma registro a registro; TEX recusado aparece com o motivo, não desenhado torto.

## Arquivos a criar ou modificar

- `tools/kits/ui/*.py`
- `tools/kits/ui_check.py`
- `docs/PLAN-KITS-PY.md` — a §3.4 diz o que a aba lista e como o `kits_ui` a julga

## Done criteria

- [x] Captura com o `TEX_48` e o `TEX_70` da European Deluxe mostrando cada um o seu motivo, e com o `TEX_13` mostrando a nota de leitura além do tamanho ISO
- [x] Captura com um TEX sadio: lista vazia
- [x] `kits_ui` estendido, verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4). O plano liga a fase 9 à fase 1; a aba precisa da janela, então depende da 20. Decisão de 2026-09-30.

Da KITS-TASK-07: o `TEX_13` deixou de ser recusado — os "10 registros" eram o tamanho ISO desatualizado, e lido até onde o cabeçalho acaba ele tem os 11 (§2.1). O critério passou a pedir o `TEX_48` e o `TEX_70` (dois motivos de LZSS) e a nota do `TEX_13`; `python tools/kits/cli.py tex roms/golden-european-deluxe.bin` lista os 8 recusados.

## Log de Execução

### 2026-10-04

Terceira aba, **Diagnosis** / **Diagnóstico** (`ui/app.py`, `show_diagnosis`):
um resumo e uma lista, uma linha por problema da guarda (`Refused: …`) e uma
por nota de leitura (`Note: …`), com o texto do núcleo (em inglês nas duas
línguas, o limite da §3.4). Seis chaves novas no catálogo, nas duas línguas.
`--tab diag` abre nela; `--list-diagnosis` imprime o resumo e as linhas, que é
o que o `kits_ui` lê. Recusado não é desenhado: o plano fica vazio e a aba diz
o motivo.

**Critério 1** — `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin work/venv-looks/bin/python tools/kits/ui/app.py roms/golden-european-deluxe.bin --tag <T> --tab diag --screenshot work/kits-diag-ed-<T>.png`
(a variável entra no hash: sem ela a aba 3D sai cinza e a última linha diz "3D off", e com
caminho relativo o texto da linha muda; CORR-KITS-060)
(sha256 `9c1ec4f0a88a…` o 48, `fdde711d5d1c…` o 70, `cf7f3c54141e…` o 13), e
o mesmo com `--list-diagnosis`:

```
  diagnosis: /BIN/TEX_48.BIN on roms/golden-european-deluxe.bin: refused by the guard, 1 problem(s)
  row 0: Refused: record 0 (uniform, first set) has an LZSS stream that does not decode: stream at 48: distance 0 at 4810
  diagnosis: /BIN/TEX_70.BIN on roms/golden-european-deluxe.bin: refused by the guard, 1 problem(s)
  row 0: Refused: record 4 (uniform, second set) has an LZSS stream that does not decode: stream at 11948: distance 0 at 16938
  diagnosis: /BIN/TEX_13.BIN on roms/golden-european-deluxe.bin: read, with 2 note(s)
  row 0: Note: its ISO size is 31792 bytes and its own header ends at byte 32146, before the next file; read to 32146.
```

(Os dois recusados trazem também a nota de setor marcado Form 2, e o 70 a de
leitura além do tamanho ISO.)

**Critério 2** — `… roms/japanese-shift-jis.bin --tag 00 --tab diag --screenshot work/kits-diag-jp-00.png`
(sha256 `93b4f55112d6…`): lista vazia; `--list-diagnosis` dá só
`diagnosis: /BIN/TEX_00.BIN on roms/japanese-shift-jis.bin: read, nothing to report`.

**Critério 3** — juiz novo no `ui_check.py` (`diag_judge`): o `TEX_00`
avulso não tem linha nem pixel de texto na lista; a cópia com o byte que o
`cli.py tex --negative` planta (byte 48) tem a linha `Refused: record 0 (`; e,
com `WE2002_KITS_ED_IMAGE`, os três da European Deluxe têm cada um a sua linha.
Planta `diagnosis rows never added` (a linha de problema não entra na lista).
`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_KITS_ED_IMAGE=roms/golden-european-deluxe.bin python3 tools/kits/ui_check.py`:

```
  ok    the Diagnosis tab lists the guard's refusal and the reading notes, and nothing for a sound kit (sound 0 row(s), 0 text px in its list, planted 1 row(s), ED TEX_48 2 row(s), ED TEX_70 3 row(s), ED TEX_13 2 row(s))
  ok    plant 'diagnosis rows never added' fails the diagnosis judge
kits_ui: 0 failure(s)
```

Sem a variável da ED, a linha diz `ED not checked, WE2002_KITS_ED_IMAGE unset`
e o juiz imprime a nota de que os três não foram julgados.
- **Closed** — commit `84e5c6d` (2026-10-04): feat(kits): Diagnosis tab lists the guard's problems and the read notes
  - Files (`git show --name-status 84e5c6d`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/33-aba-diagnostico.md`
    - `M docs/tasks/kits/34-definicao-de-pronto.md`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-05) at `8901c5d`: CORR-KITS-060, CORR-KITS-061
