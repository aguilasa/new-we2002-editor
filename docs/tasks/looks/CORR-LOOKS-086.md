---
id: CORR-LOOKS-086
title: Levar a ressalva da armadilha 96 ao docstring do HELP_UPLOAD
origin: LOOKS-TASK-39
severity: low
files: [tools/looks/layout.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-23
done_commit: 336aedce
---

# CORR-LOOKS-086 — Levar a ressalva da armadilha 96 ao docstring do HELP_UPLOAD

Origin: [LOOKS-TASK-39](/docs/tasks/looks/39-o-texto-da-ajuda.md)

## Problema identificado

O `HELP_UPLOAD = 0x8003A950` está documentado como "the instruction a VRAM
write watchpoint over the page stops at", sem ressalva — enquanto o **mesmo
commit** acrescenta a armadilha 96 e uma linha impressa-e-não-afirmada dizendo
que esse `pc` é artefato de DMA, e que duas de quatro sondas devolveram
`0x8003F2F4` e `0x8010A910`. Uma constante lida depois será tomada por
propriedade medida do jogo, que é justamente o que a task decidiu que ela não
é.

## Evidência

```text
$ python tools/looks/oracle.py --help-box 2
      (the pc at each: 0x8003A950 -- printed, not asserted: the copy is a DMA, and the watch reports one hit for the press, not one per tile)

$ sed -n '/^HELP_IMAGE_LOAD/,/^"""$/p' tools/looks/layout.py | head -4
"""The library routine that copies one tile into the page, and the instruction
a VRAM write watchpoint over the page stops at.
```

## Causa raiz

A ressalva entrou na lista de armadilhas do perfil e na linha impressa da
ferramenta, mas não na constante que carrega o endereço.

## Correção

Acrescentar a cláusula ao docstring de `HELP_IMAGE_LOAD`/`HELP_UPLOAD` em
`tools/looks/layout.py`: o `pc` é onde o watchpoint parou **nesta** corrida e
não é estável (armadilha 96); o que se afirma é o retângulo mais o
`lui a0,0xA000` lido do disco em `0x8003A884`/`0x8003A8B8`.

## Arquivos

- tools/looks/layout.py

## Verificação

`sed -n '/^HELP_IMAGE_LOAD/,/^"""$/p' tools/looks/layout.py | grep -c "96\|not
stable\|DMA"` tem de imprimir pelo menos `1` (imprime `0` hoje).

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-23, HEAD `dca4a96e`: **reproduzida** (o `--help-box` não rodou — emulador com outro agente).

```text
$ sed -n '/^HELP_IMAGE_LOAD/,/^"""$/p' tools/looks/layout.py | grep -c "96\|not stable\|DMA"
0
# o docstring (HELP_UPLOAD em layout.py:1881) segue sem ressalva
# a armadilha 96 existe, em perfil-looks.armadilhas.md:79-86, e diz o contrário:
#   0x8003A950 em duas corridas, 0x8003F2F4 e 0x8010A910 nas duas seguintes
```

Observação lateral da triagem: a numeração das armadilhas salta de `96.` para
`91.` na linha 87 daquele arquivo.

Corrigida em 2026-09-23, HEAD `420709ce`, sem emulador. O docstring de
`HELP_IMAGE_LOAD`/`HELP_UPLOAD` (`tools/looks/layout.py:1895`) passou a dizer
as duas coisas em ordem: o `pc` é onde o watchpoint parou **numa** corrida e
não é estável — a cópia é DMA, `0x8003A950` em duas corridas e `0x8003F2F4` /
`0x8010A910` nas duas seguintes (armadilha 96) —, e o que se afirma é o
retângulo mais o `lui a0,0xA000` lido do disco.

**Os dois endereços foram remedidos aqui, não copiados desta CORR.** Lendo o
`/SLPM_870.56` da imagem japonesa pelo `iso_source`, com a base tirada do
cabeçalho PS-EXE do próprio arquivo (`0x80010000`, igual ao
`layout.BOOT_BASE`; 335.872 bytes de texto):

```text
0x8003A884: 0x3C04A000  lui a0,0xA000
0x8003A8B8: 0x3C04A000  lui a0,0xA000
lui a0,0xA000 entre 0x8003A780 e 0x8003A980: ['0x8003a884', '0x8003a8b8']
```

São **os dois únicos** `lui a0,0xA000` da rotina, o que o docstring agora diz
— ninguém precisa procurar um terceiro. `a0` fica `0xA0000000`, cujo byte alto
é o `HELP_COPY_COMMAND`.

Verificação e portões, todos verdes:

```text
$ sed -n '/^HELP_IMAGE_LOAD/,/^"""$/p' tools/looks/layout.py | grep -c "96\|not stable\|DMA"
1

$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok

$ rite check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

Varredura: `HELP_UPLOAD` e `HELP_IMAGE_LOAD` não aparecem em mais nenhum
`.py` nem `.md` do repositório — são constantes **registradas, não lidas**,
como o bloco do `HELP_ICON_CODES` ao lado. Por isso a ressalva só cabia no
docstring: não há chamador para adverti-la.
- **Closed** — commit `336aedce` (2026-09-23): docs(looks): say the help-upload pc is a DMA artefact, not a measurement
  - Files (`git show --name-status 336aedce`):
    - `M docs/tasks/looks/CORR-LOOKS-086.md`
    - `M tools/looks/layout.py`
