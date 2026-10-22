---
id: CORR-DMCP-013
---

# CORR-DMCP-013 — Versionar como controles as plantas dos checks novos de gpu, png, vram e psx

Origin: [DMCP-TASK-13](/docs/tasks/duckmcp/13-hardware-e-pixels.md)

## Problem

O vermelho visto dos checks novos — `GpuListLoop` trocado por `GpuListTooLong`, a ordem de desempate
do Paeth trocada, `to_rgb` com `b << 2`, o marcador de fim ignorado, `HARDWARE_RANGES` plantado no
`selftest.py` e no `psx.py` — foi feito uma vez numa cópia de rascunho e está no Log só em prosa. O
`controls.py` não mudou no commit e continua com 21 controles, nenhum de psx/gpu/png/vram. As outras
asserções do ciclo ganharam controle versionado (`press-without-duration`, `client-*`, `fork-*`); estas
ficaram ad hoc e não se refazem a partir da HEAD.

## Evidência

```text
$ git diff --stat 87987d9d^ 87987d9d -- tools/duckmcp/controls.py
(vazio)
$ python3 tools/duckmcp/controls.py --list | grep -cE 'gpu|png|vram|psx|ranges'
0
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 21 control(s), 21 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (live) 1/1, (session) 1/1
```

## Root cause

Hipótese: os critérios só pediam o vermelho "visto no Log", então as plantas não viraram controles.

## Fix

Um controle por planta no `tools/duckmcp/controls.py`, cada um uma substituição literal que exige a
linha FAIL da sua asserção: o walk levantando `GpuListTooLong` em vez de `GpuListLoop`; a ordem de
desempate do `_paeth` trocada; `to_rgb` com `b << 2`; o teste do marcador de fim desligado; um
`HARDWARE_RANGES` plantado no `psx.py` deixando o sentinela vermelho. A planta local ao `selftest.py`,
que tem de ficar verde, pode virar asserção positiva no selftest.

## Arquivos a criar ou modificar

- `tools/duckmcp/controls.py`

## Verificação

`python3 tools/duckmcp/controls.py --list | grep -cE 'gpu|png|vram|psx'` dá 0 hoje e tem de dar ≥ 4;
`python3 tools/duckmcp/controls.py` termina em "N red as required".

## Log de Execução

2026-10-22 — reproduzido: `python3 tools/duckmcp/controls.py --list | grep -cE 'gpu|png|vram|psx|ranges'`
dava `0`.

Conserto: cinco controles no `controls.py`, cada um uma substituição literal única que exige a linha
FAIL da sua asserção. São as plantas que o Log da DMCP-TASK-13 fez à mão: `gpu-loop-as-too-long`,
`gpu-end-marker-ignored`, `png-paeth-tie-upleft-first`, `vram-blue-shift` e `psx-range-planted`, este
com a faixa plantada no `psx.py`, o que deixa vermelha a sentinela da regra (c). A planta que tem de
ficar verde, a faixa local no `selftest.py`, **não** virou asserção; a CORR a deixava opcional.

Verificação:

```text
$ for c in gpu-loop-as-too-long gpu-end-marker-ignored png-paeth-tie-upleft-first vram-blue-shift psx-range-planted; do python3 tools/duckmcp/controls.py --only $c | sed -n 2p | cut -c1-200; done
red    gpu-loop-as-too-long (rule gpu): FAIL  gpu: walk refuses a list looping back to its head as a loop  GpuListTooLong: the GPU list from 0x80000100 loops: node 0x800001a0 points back to node 0x800
red    gpu-end-marker-ignored (rule gpu): FAIL  gpu.self_check() raised ValueError: 4 byte(s) at 0x80ffffff are outside the 65536-byte dump
red    png-paeth-tie-upleft-first (rule png): FAIL  png: Paeth breaks its ties left, then up, then upper-left, as Pillow did  [10, 12, 20, 16, 6, 44, 26, 54]
red    vram-blue-shift (rule vram): FAIL  vram: to_halfword(to_rgb(h)) == h for all 32768 values  [1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031]
red    psx-range-planted (rule psx): FAIL  rule (c): the address judge refuses the gaps between ranges
$ python3 tools/duckmcp/controls.py --list | grep -cE 'gpu|png|vram|psx'
5
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 26 control(s), 26 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3, (gpu) 2/2, (live) 1/1, (png) 1/1, (psx) 1/1, (session) 1/1, (vram) 1/1
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
```
