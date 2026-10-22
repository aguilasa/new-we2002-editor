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
