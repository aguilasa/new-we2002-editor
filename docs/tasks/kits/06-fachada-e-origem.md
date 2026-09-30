---
id: KITS-TASK-06
title: "Criar a fachada `api.py` e o `source.py` que reconhece ROM ou TEX pelo conteúdo"
type: "implementação"
phase: 1
depends_on: [KITS-TASK-05]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.1"
files: ["tools/kits/core/api.py", "tools/kits/core/source.py", "tools/kits/core/errors.py", "NOTICE.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-06 — Criar a fachada `api.py` e o `source.py` que reconhece ROM ou TEX pelo conteúdo

## Goal

`api.open_source(path)` devolve uma origem com `kind` `"rom"` ou `"tex"`, decidido pelo conteúdo; erros são exceções tipadas cuja mensagem é a frase que a interface mostra.

## Arquivos a criar ou modificar

- `tools/kits/core/api.py`
- `tools/kits/core/source.py`
- `tools/kits/core/errors.py`

## Done criteria

- [x] Um `.bin` do disco japonês renomeado para `.tex` abre como `rom`, e um TEX extraído renomeado para `.bin` abre como `tex` — comando e saída no Log
- [x] Arquivo que não é nenhum dos dois é recusado com exceção tipada e frase — comando e saída no Log
- [x] `grep -rnE 'print\(|sys\.exit|PySide|^[A-Z_]+ *= *\[\]' tools/kits/core/` vazio (sem saída, sem Qt, sem estado global mutável)
- [x] `NOTICE.md` ganha a seção "Lineage of the kit viewer (`tools/kits/`)" no mesmo commit, citando **todo código de terceiro que o `kits` alcança**, inclusive por import indireto: o LZSS e o formato `.BIN` da suíte CARP (Maximiliano Ducoli, via `tools/pes2/lzss.py` e `bin_archive.py`) e o `we3d` (Darkensses, MIT, via a geometria do `tools/looks/`). O Superpack não é citado como fonte (regra de 2026-09-30)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1).

Da KITS-TASK-01: a seção do `tools/kits/` no `NOTICE.md` já existe, com a linha do CARP (o `survey.py` importa `lzss.py`/`bin_archive.py`). Esta task a completa com o `we3d` quando a geometria do `looks` for alcançada.

## Log de Execução

### O que foi feito

- `core/errors.py`: `KitsError` → `SourceError` → `SourceMissing`, `SourceUnreadable`, `SourceEmpty`, `NotASource`.
- `core/source.py`: reconhece **pelo conteúdo**, nesta ordem — trilha de dados (tamanho múltiplo de 2.352 e `iso.Image` abre e lista arquivo), folha `.cue` (texto de até 64 KiB sem NUL, primeira linha `FILE … BINARY` com `TRACK nn MODE…`, resolvida contra a pasta do `.cue`), TEX (forma de `bin_archive.entries` igual à `survey.EXPECTED_SHAPE`), e recusa. A recusa diz o que falhou em cada uma das duas leituras.
- `core/api.py`: `open_source`, `RomSource` (`kit_tags()`, `image_path`, `cue_path`) e `TexSource` (`data`, `size`), `KIND_ROM`/`KIND_TEX` e as exceções. Sem `teams`, `kit`, `flat`, `figure`: são das tasks 07, 13, 15 e 24.
- `cli.py open <path> ...`: o que a fachada faz de cada arquivo. Entrou para a evidência sair de comando versionado e não de sonda; só usa `core.api`. Sai 1 se algum for recusado.
- `NOTICE.md`: a linha do `we3d` (Darkensses, MIT) na seção do `tools/kits/` — alcançado desde a KITS-TASK-03, pelo `section.py`/`modelfile.py`/`assembly.py` do `looks`. A do CARP já estava (KITS-TASK-01). Nenhuma linha da seção cita o Superpack.

### Evidência

Fixtures no scratchpad (`<scratch>`), feitas assim:

```
$ MSYS_NO_PATHCONV=1 python tools/pes2/iso.py extract roms/japanese-shift-jis.bin /BIN/TEX_00.BIN -o <scratch>/tex00.bin   # 29944 bytes
kit.bin    = cópia de tex00.bin
disc.tex   = os.link(roms/japanese-shift-jis.bin)   (hardlink, nada copiado)
broken.tex = tex00.bin com o byte +14 do registro 0 (offset 5056) em XOR 0xFF
note.txt (22 bytes de texto), empty.bin (0 bytes), zeros.iso (20 setores zerados),
gone.cue (aponta nothere.bin), missing.bin (não existe), e a própria pasta
```

Critério 1:

```
$ python tools/kits/cli.py open <scratch>/disc.tex <scratch>/kit.bin roms/golden-european-deluxe.cue      # exit 0
OPEN   disc.tex -> rom (kit tags 105, data track <scratch>/disc.tex)
OPEN   kit.bin -> tex (29944 bytes)
OPEN   golden-european-deluxe.cue -> rom (kit tags 105, data track C:\github\new-we2002-editor\roms\golden-european-deluxe.bin)
```

Critério 2 (caminhos do scratchpad encurtados para `<scratch>`):

```
$ python tools/kits/cli.py open note.txt empty.bin missing.bin broken.tex zeros.iso gone.cue k6      # exit 1
REFUSE note.txt -> NotASource: <scratch>/note.txt is neither a CD image nor a kit container (TEX): as a CD image, 22 bytes is not a whole number of 2352-byte sectors; as a TEX, it holds no image or palette record list.
REFUSE empty.bin -> SourceEmpty: <scratch>/empty.bin is empty (0 bytes).
REFUSE missing.bin -> SourceMissing: <scratch>/missing.bin does not exist.
REFUSE broken.tex -> NotASource: <scratch>/broken.tex is neither a CD image nor a kit container (TEX): as a CD image, 29944 bytes is not a whole number of 2352-byte sectors; as a TEX, it has 10 image/palette records where a kit container has 11.
REFUSE zeros.iso -> NotASource: <scratch>/zeros.iso is neither a CD image nor a kit container (TEX): as a CD image, no ISO 9660 filesystem on it (no CD001 at sector 16); as a TEX, it holds no image or palette record list.
REFUSE gone.cue -> SourceMissing: The cue sheet <scratch>/gone.cue names nothere.bin, and <scratch>\nothere.bin does not exist.
REFUSE k6 -> SourceUnreadable: <scratch> is a folder, not a file.
```

O `broken.tex` é o controle do lado TEX: um byte de tag trocado e o reconhecimento cai de 11 para 10 registros.

Critério 3:

```
$ grep -rnE 'print\(|sys\.exit|PySide|^[A-Z_]+ *= *\[\]' tools/kits/core/            # exit 1, sem saída
$ grep -rnE '^[A-Za-z_]+ *= *(\[|\{|dict\(|list\(|set\()' tools/kits/core/api.py tools/kits/core/source.py tools/kits/core/errors.py   # exit 1, sem saída
```

`python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum` → `c2ec025a808afd4ffbe4c39fca0d991a`, o mesmo das tasks anteriores.

### Problemas encontrados

- O `source.py` usa `survey._shape_of` e `survey.EXPECTED_SHAPE` (privado e fora do módulo de endereço). Nota na KITS-TASK-07, que é quem move os retângulos.
- `survey.SurveyError` deriva de `Exception`, não de `KitsError`: `except KitsError` não pega falha do `survey`. Nota na KITS-TASK-07.
- `RomSource.image_path` sai com barra invertida no Windows (`os.path.normpath`), como mostra a linha do `.cue`.
