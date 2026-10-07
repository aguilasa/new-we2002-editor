---
id: CORR-KITS-014
---

# CORR-KITS-014 — Add a planted control for the Form 2 and extent refusals

Origin: [KITS-TASK-07](/docs/tasks/concluidos/kits/07-tex-e-guarda-de-forma.md)

## Problem

Duas asserções novas da KITS-TASK-07 não têm controle versionado nem vermelho no Log. Uma é o `source._sector_data`, que lança `KitUnreadable` quando um setor marcado como Form 2 tem dados nos bytes 2072–2347. A outra é a regra da extensão do cabeçalho: ler além do tamanho ISO só até o arquivo seguinte. O único controle é o do byte do LZSS (`tex --negative`), e nada em `tools/kits` exercita o `KitUnreadable`. Vale a regra "verificador sem vermelho visto não é gate". O caminho funciona, mas só se viu vermelho por sonda descartável.

## Evidência

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
0
$ grep -rn "KitUnreadable" tools/kits --include=*.py | grep -v "errors.py\|api.py"
tools/kits/core/source.py:34:from .errors import (KitMissing, KitUnreadable, NotASource, SourceEmpty,
tools/kits/core/source.py:80:        no such tag, `KitUnreadable` if a sector of it is Form 2 for real.
tools/kits/core/source.py:150:        raise KitUnreadable(
tools/kits/core/source.py:176:        raise KitUnreadable("%s on %s runs past the end of the data track."
```

Sonda do revisor, sem versão (leitor de setor em memória que põe `0x55` no byte 2100 do setor 8675 do `TEX_13`):

```text
KitUnreadable /BIN/TEX_13.BIN on ../../roms/golden-european-deluxe.bin: sector 8675 (16 of 16) is Form 2 with data past byte 2048, so it is not a Form 1 sector with a wrong bit.
```

## Root cause

Hipótese: a lista de controles da task saiu do item 4 do §5 do plano, que é anterior às decisões sobre Form 2 e extensão, e as recusas novas nunca entraram nela.

## Fix

Acrescentar a `tools/kits` um controle plantado (no `cli.py tex --negative` ou no futuro `controls.py`) que ponha um byte não nulo nos bytes 2072–2347 de um setor marcado e espere `KitUnreadable`, usando um leitor de setor em memória como o da sonda, não uma cópia de 474 MB. Opcionalmente, um segundo plantio que limite o espaço abaixo da extensão e espere o `TEX_13` recusado. Nomear o controle no §5 do plano.

## Arquivos a criar ou modificar

- `tools/kits/core/source.py`
- `tools/kits/cli.py` ou `tools/kits/controls.py`
- `docs/PLAN-KITS-PY.md` (§5)

## Verificação

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
```

Hoje dá 0; depois, pelo menos 1.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `bc81d3ab`)

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
0
$ grep -rn "KitUnreadable" tools/kits --include=*.py | grep -v "errors.py\|api.py"
tools/kits/core/source.py:34:from .errors import (KitMissing, KitUnreadable, NotASource, SourceEmpty,
tools/kits/core/source.py:80:        no such tag, `KitUnreadable` if a sector of it is Form 2 for real.
tools/kits/core/source.py:150:        raise KitUnreadable(
tools/kits/core/source.py:176:        raise KitUnreadable("%s on %s runs past the end of the data track."
```

REPRODUCED.

### O que foi feito

- `tools/kits/core/source.py`: `disc_controls(imagem, tags)` planta as duas regras do `read_disc_file` por um **proxy** da imagem aberta (`_PlantedImage`), sem copiar nem gravar o disco:
  - **cauda Form 2**: `_PlantedFile` faz o byte 2100 do primeiro setor marcado Form 2 do primeiro kit que o tem ler `0x55`; tem de dar `KitUnreadable`;
  - **até o arquivo seguinte**: um arquivo falso no diretório, logo depois dos setores ISO do primeiro kit cujo cabeçalho acaba **além do último setor ISO**; a leitura tem de parar no tamanho ISO e o kit tem de sair recusado, sem a nota `past-iso-size`.
  - Disco sem kit a que as regras se apliquem (o japonês) → `NotASource` com a frase.
- `core/api.py`: `disc_controls(source)` e `DiscControl`. `cli.py tex --negative` roda, num disco e sem `--tag`, o controle do LZSS de antes e os dois novos; no japonês diz "not run" com o motivo.
- §5 item 4 do plano nomeia os dois controles.

### Verificação

```text
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin; echo "exit $?"
control: TEX_00, byte 48 (record 0 stream +0) 0x8a -> 0x75
  clean:   passes
  planted: record 0 (uniform, first set) decompresses to 0 bytes where its rectangle asks for 16384
control held: the planted kit is refused on record 0
control: Form 2 tail with data -- /BIN/TEX_00.BIN, sector 8415, byte 2100 = 0x55
  clean:   passes (32496 bytes; form2-tail)
  planted: KitUnreadable: /BIN/TEX_00.BIN on roms/golden-european-deluxe.bin: sector 8415 (16 of 16) is Form 2 with data past byte 2048, so it is not a Form 1 sector with a wrong bit.
control held
control: next file at the ISO size -- /BIN/TEX_07.BIN, a file placed at sector 8555 (its ISO end)
  clean:   passes (33110 bytes; past-iso-size, form2-tail)
  planted: refused: it has 10 image/palette records where a kit container has 11 (30016 bytes; no note)
control held
exit 0
$ python tools/kits/cli.py tex --negative roms/golden-european-deluxe.bin | grep -c KitUnreadable
1
```

O verificador visto falhando — a primeira versão escolhia o primeiro kit lido além do tamanho ISO, o `TEX_04`, cujo cabeçalho acaba **dentro** da sobra do último setor ISO; a cerca não o alcança, e o controle acusou:

```text
control: next file at the ISO size -- /BIN/TEX_04.BIN, a file placed at sector 8495 (its ISO end)
  clean:   passes (30602 bytes; past-iso-size)
  planted: passes (30602 bytes; past-iso-size)
control FAILED
exit 1
```

Regressões:

```text
$ python tools/kits/cli.py tex --negative roms/japanese-shift-jis.bin | tail -1
disc controls: not run: roms/japanese-shift-jis.bin has no kit read through a wrong Form 2 bit and past its ISO size, so the two read controls have nothing to plant.
$ python tools/kits/cli.py tex roms/<imagem>.bin | cmp - <saída antes>      # japonesa e European Deluxe: idênticas
$ python tools/kits/cli.py open --negative roms/japanese-shift-jis.bin | tail -1
11 of 11 expectations held
$ grep -rnE 'print\(|sys\.exit|PySide|^[A-Z_]+ *= *\[\]' tools/kits/core/
(sem saída, exit 1)
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin | md5sum
c2ec025a808afd4ffbe4c39fca0d991a *-
```

`tools/kits/controls.py` não foi criado: é da KITS-TASK-08, que o define como plantio numa cópia da árvore.
- **Closed** — commit `a4943bd5` (2026-10-01): fix(kits): plant the Form 2 tail and next-file rules in tex --negative
  - Files (`git show --name-status a4943bd5`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-014.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/core/source.py`
