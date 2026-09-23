---
id: CORR-LOOKS-086
title: Levar a ressalva da armadilha 96 ao docstring do HELP_UPLOAD
origin: LOOKS-TASK-39
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
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
