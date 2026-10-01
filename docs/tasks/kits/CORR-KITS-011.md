---
id: CORR-KITS-011
title: "Fix the broken.tex fixture recipe: offset 5056 is not tag byte +14"
origin: KITS-TASK-06
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-011 — Fix the broken.tex fixture recipe: offset 5056 is not tag byte +14

Origin: [KITS-TASK-06](/docs/tasks/kits/06-fachada-e-origem.md)

## Problem

O Log da KITS-TASK-06 monta o `broken.tex` com "o byte +14 do registro 0 (offset 5056) em XOR 0xFF" e cola a recusa "it has 10 image/palette records where a kit container has 11". No `TEX_00`, a varredura de tag acha o registro 0 em 5056, então o byte +14 (a tag) fica em **5070**. Trocar o 5056, como está escrito, muda o byte de tipo e dá outra recusa; trocar o 5070 dá a saída colada. Além disso, todas as fixtures estão descritas só em prosa (comandos `python -c` de uma linha e um `os.link` para `roms/`), então nenhuma ferramenta versionada as reconstrói, e o número do Log não sai da receita que está ao lado dele.

## Evidência

```text
$ grep -n '5056' docs/tasks/kits/06-fachada-e-origem.md
60:broken.tex = tex00.bin com o byte +14 do registro 0 (offset 5056) em XOR 0xFF
$ python -c "d=bytearray(open('tex00.bin','rb').read()); d[5056]^=0xFF; open('broken.tex','wb').write(d)"
$ python tools/kits/cli.py open <scratch>/broken.tex
REFUSE broken.tex -> NotASource: ... as a TEX, record 0 is kind 245 at (576,256) 64x128 where a kit container has image at (576,256) 64x128.
$ (o mesmo com d[5070]) python tools/kits/cli.py open <scratch>/broken2.tex
... as a TEX, it has 10 image/palette records where a kit container has 11.
$ cd tools/pes2 && python -c "import bin_archive as b; d=open('<scratch>/tex00.bin','rb').read(); print(hex(d.find(b'\x0f\x80\xff\x00')))"
0x13ce
```

`0x13ce` = 5070: a tag do registro que começa em 5070 − 14 = 5056.

## Root cause

Hipótese: o autor confundiu o offset de início do registro (5056) com o do byte trocado (5056 + 14 = 5070).

## Fix

Corrigir a receita em `docs/tasks/kits/06-fachada-e-origem.md` para o offset 5070. Melhor ainda: levar a montagem das fixtures e o controle da tag plantada para uma sonda versionada (o `selftest`/`controls.py` da KITS-TASK-08, ou um `cli.py open --negative`), para que a linha "10 de 11" saia de um comando que qualquer um reexecuta.

## Arquivos a criar ou modificar

- `docs/tasks/kits/06-fachada-e-origem.md`
- `tools/kits/controls.py` ou `tools/kits/cli.py`, se virar sonda

## Verificação

Montar o `broken.tex` pela receita do Log, como ela estiver escrita, e rodar `python tools/kits/cli.py open <scratch>/broken.tex`. Hoje a saída diz "record 0 is kind 245"; depois tem de dizer "it has 10 image/palette records where a kit container has 11".

## Log de Execução
