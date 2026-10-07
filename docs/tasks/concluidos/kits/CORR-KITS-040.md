---
id: CORR-KITS-040
---

# CORR-KITS-040 — Versionar a sonda dos registros do TEX_00 no lugar do heredoc elidido

Origin: [KITS-TASK-22](/docs/tasks/concluidos/kits/22-looks-kit-set.md)

## Problem

O bloco "O banco, medido antes de mexer" do Log da KITS-TASK-22 mostra `$ python3 - <<'X'   # texture.images/palettes sobre /BIN/TEX_00.BIN` e, no lugar do corpo do script, a saída dele. Os offsets reproduzem (o revisor os refez com heredoc próprio), mas a medição é sonda descartável que o Log não deixa refazer. A regra do repositório pede que sonda que produziu número vire opção de ferramenta versionada.

## Evidência

```text
$ grep -c "python3 - <<'X'" docs/tasks/kits/22-looks-kit-set.md
1
$ cd tools/looks && python3 - <<'X'
import iso_source, layout, texture
with iso_source.open_disc("../../roms/japanese-shift-jis.bin") as d:
    b = d.read(layout.kit_path("00"))
for r in texture.images(b): print("img", r.offset, (r.x, r.y, r.w, r.h))
for r in texture.palettes(b): print("clut", r.offset, (r.x, r.y, r.w, r.h))
X
img 48 (576, 256, 64, 128)
img 10556 (576, 256, 64, 128)
...
clut 23848 (256, 480, 256, 1)
```

(bate com o Log)

## Root cause

Sonda descartável colada no Log só como saída.

## Fix

Acrescentar a uma ferramenta versionada uma opção que liste os registros de um TEX — por exemplo `cli.py texture --records <tag>` ou uma opção do `texture.py` — e trocar o bloco do Log por esse comando e a saída dele.

## Arquivos a criar ou modificar

- `tools/looks/cli.py` (ou `tools/looks/texture.py`)
- `docs/tasks/kits/22-looks-kit-set.md`

## Verificação

```sh
grep -c "python3 - <<'X'" docs/tasks/kits/22-looks-kit-set.md
```

Imprime 1 hoje; 0 depois do conserto, e o comando novo reproduz os 11 registros.

## Log de Execução

### 2026-10-03

Reproduzido: `grep -c "python3 - <<'X'" docs/tasks/kits/22-looks-kit-set.md` dá `1`, e o heredoc da Evidência imprime os 11 registros.

Conserto: `cli.py texture --records TAG [image]` lista as imagens e as paletas de um `TEX_<TAG>.BIN` (offset e retângulo), pela leitura do `texture.py`; tag não medida é recusada (`exit 2`). O bloco do Log da KITS-TASK-22 agora mostra esse comando e a saída dele, que bate registro a registro com o heredoc:

```
$ python3 tools/looks/cli.py texture --records 00 roms/japanese-shift-jis.bin
  /BIN/TEX_00.BIN
  img      48 (576, 256, 64, 128)
  img    5088 (576, 384, 64, 128)
  img   10556 (576, 256, 64, 128)
  img   15908 (576, 384, 64, 128)
  img   21420 (704, 256, 64, 64)
  img   24392 (768, 384, 64, 128)
  clut   9468 (0, 486, 256, 1)
  clut  10012 (0, 488, 256, 1)
  clut  20332 (0, 486, 256, 1)
  clut  20876 (0, 488, 256, 1)
  clut  23848 (256, 480, 256, 1)
$ python3 tools/looks/cli.py texture --records ZZ roms/japanese-shift-jis.bin
cli texture: refused -- 'ZZ' is not one of the 105 kit tags measured on this disc
$ python3 tools/looks/cli.py --check | tail -1
cli.py: 0 failure(s)
$ grep -c "python3 - <<'X'" docs/tasks/kits/22-looks-kit-set.md
0
```

Uma diferença de forma: o Log antigo arrumava os registros em duas colunas (pares do mesmo retângulo lado a lado); a ferramenta imprime em ordem de arquivo, uma por linha.
- **Closed** — commit `d33fece` (2026-10-03): feat(looks): cli.py texture --records lists a kit's TEX records
  - Files (`git show --name-status d33fece`):
    - `M docs/tasks/kits/22-looks-kit-set.md`
    - `M docs/tasks/kits/CORR-KITS-040.md`
    - `M tools/looks/cli.py`
