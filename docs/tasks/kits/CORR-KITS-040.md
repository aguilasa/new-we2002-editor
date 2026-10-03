---
id: CORR-KITS-040
---

# CORR-KITS-040 — Versionar a sonda dos registros do TEX_00 no lugar do heredoc elidido

Origin: [KITS-TASK-22](/docs/tasks/kits/22-looks-kit-set.md)

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
