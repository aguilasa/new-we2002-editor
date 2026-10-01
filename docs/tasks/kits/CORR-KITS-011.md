---
id: CORR-KITS-011
title: "Fix the broken.tex fixture recipe: offset 5056 is not tag byte +14"
origin: KITS-TASK-06
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-10-01
done_commit: 5f0588e4
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

### Reprodução (HEAD `da8c435a`)

O `rite reproduce` não roda a Evidência (os caminhos são `<scratch>`); refeita à mão, com `<scratch>` = pasta da sessão:

```text
$ MSYS_NO_PATHCONV=1 python tools/pes2/iso.py extract roms/japanese-shift-jis.bin /BIN/TEX_00.BIN -o <scratch>/tex00.bin
$ (d[5056] ^= 0xFF) python tools/kits/cli.py open <scratch>/broken5056.tex
REFUSE broken5056.tex -> NotASource: <scratch>/broken5056.tex is neither a CD image nor a kit container (TEX): as a CD image, 29944 bytes is not a whole number of 2352-byte sectors; as a TEX, record 0 is kind 245 at (576,256) 64x128 where a kit container has image at (576,256) 64x128.
$ (d[5070] ^= 0xFF) python tools/kits/cli.py open <scratch>/broken5070.tex
REFUSE broken5070.tex -> NotASource: <scratch>/broken5070.tex is neither a CD image nor a kit container (TEX): as a CD image, 29944 bytes is not a whole number of 2352-byte sectors; as a TEX, it has 10 image/palette records where a kit container has 11.
$ cd tools/pes2 && python -c "...; print(d.find(b'\x0f\x80\xff\x00'))" <scratch>/tex00.bin
5070
```

REPRODUCED. Causa raiz confirmada: 5056 é o início do registro 0, e a tag fica em +14.

### O que foi feito

- `tools/kits/core/source.py`: `build_open_fixtures(imagem, pasta)` monta as fixtures do Log a partir do disco — `kit.bin` (o `TEX_00` extraído), `disc.tex` (hardlink, nada copiado), `disc.cue`, `broken-tag.tex` (byte = início do registro 0 + `TEX_TAG_FIELD`, **achado pela lista de registros**), `broken-kind.tex` (o byte 5056 da receita velha, como controle do outro veredito), `note.txt`, `empty.bin`, `zeros.iso`, `gone.cue`, `missing.bin` e uma pasta — e `open_controls` abre cada uma e confere tipo e frase (`OpenControl.ok`). Exportado em `core/api.py`, de modo que o `cli.py` continua só na fachada.
- `tools/kits/cli.py open --negative <imagem>`: monta numa pasta temporária, imprime cada desfecho, sai 1 se algum falhar.
- KITS-TASK-06: a receita passa a dizer 5070, e o Log ganhou a saída do comando.

### Verificação

```text
$ (receita do Log, d[5070] ^= 0xFF) python tools/kits/cli.py open <scratch>/broken.tex
REFUSE broken.tex -> NotASource: <scratch>/broken.tex is neither a CD image nor a kit container (TEX): as a CD image, 29944 bytes is not a whole number of 2352-byte sectors; as a TEX, it has 10 image/palette records where a kit container has 11.
$ python tools/kits/cli.py open --negative roms/japanese-shift-jis.bin | tail -1
11 of 11 expectations held
```

O verificador visto falhando — `TEX_TAG_FIELD` posto em 0, que é a receita velha:

```text
$ python -c "import sys; sys.path.insert(0,'tools/kits'); import cli; from core import source
source.TEX_TAG_FIELD = 0
raise SystemExit(cli.main(['open','--negative','roms/japanese-shift-jis.bin']))"
broken-tag.tex  kit.bin, byte 5056 (record 0 at 5056, +0: the tag) XOR 0xFF expect NotASource       got NotASource       FAILED
    <tmp>\broken-tag.tex is neither ... as a TEX, record 0 is kind 245 at (576,256) 64x128 where a kit container has image at (576,256) 64x128.
exit 1
$ grep -rnE 'print\(|sys\.exit|PySide|^[A-Z_]+ *= *\[\]' tools/kits/core/
(sem saída, exit 1)
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum
c2ec025a808afd4ffbe4c39fca0d991a *-
```
- **Closed** — commit `5f0588e4` (2026-10-01): fix(kits): build the source-recognition fixtures by command, with the tag byte found
  - Files (`git show --name-status 5f0588e4`):
    - `M docs/tasks/kits/06-fachada-e-origem.md`
    - `M docs/tasks/kits/CORR-KITS-011.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/source.py`
