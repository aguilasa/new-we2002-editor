---
id: CORR-DMCP-019
---

# CORR-DMCP-019 — Atualizar o docstring e a linha FAIL do live.py para os checks novos

Origin: [DMCP-TASK-15](/docs/tasks/duckmcp/15-fechamento-fase-3.md)

## Problem

O Log diz "O docstring dele foi atualizado", mas duas frases antigas sobreviveram: uma ainda diz que o
gate "asks only ... the tools the server declares, and that `frame_step` moves `frame_number`"; a outra
diz que a saída 1 é "when the fork failed or the frame count is wrong", embora agora também falhe por
RAM, VRAM ou serial. A linha FAIL também não diz qual condição falhou: com só o serial quebrado, todo
valor impresso batia com o pedido e a linha ainda dizia FAIL.

## Evidência

```text
$ sed -n 7,9p tools/duckmcp/live.py; sed -n 24,26p tools/duckmcp/live.py
knows which game it is: the gate asks only what every disc answers -- the
tools the server declares, and that `frame_step` moves `frame_number`.
...
fork failed or the frame count is wrong. The last line is always
```

Numa cópia `git archive HEAD tools` com `reads["game"].serial is not None` trocado por `is None` via
`sed`, rodada no `:98`:

```text
duckmcp_live: FAIL -- frame_number moved 5 for 5 frame_step (want 5); tools=95 frames 45->50; ram=2097152 vram=1024x512 serial=SLPM-87056
```

## Root cause

A edição acrescentou um parágrafo mas não voltou às frases que enunciavam o contrato antigo.

## Fix

No `tools/duckmcp/live.py`, reescrever as linhas 7-9 e o parágrafo do código de saída para cobrir RAM,
VRAM e `game()`, e fazer a linha FAIL nomear a(s) condição(ões) que falharam.

## Arquivos a criar ou modificar

- `tools/duckmcp/live.py`

## Verificação

`grep -n "asks only what every disc answers -- the$" tools/duckmcp/live.py` não imprime nada, e
`grep -n "frame count is wrong" tools/duckmcp/live.py` também não.

## Log de Execução
