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

2026-10-23 — reproduzido: `grep -n "asks only what every disc answers -- the$"` achava a linha 8, e o
parágrafo do código de saída dizia "1 when the fork failed or the frame count is wrong" (quebrado entre
as linhas 24 e 25, por isso a segunda grep da Verificação não o achava literalmente).

Conserto:
- O parágrafo de abertura passou a nomear as quatro coisas que o gate pergunta: ferramentas e quadros,
  RAM e VRAM nos tamanhos do console, e serial.
- O código de saída 1 cobre leitura que levanta e qualquer das quatro condições.
- O veredito saiu para `failures(steps, before, after, reads)`, que devolve os nomes do que falhou.
  `run` devolve essa lista no lugar de `passed`, e a linha final diz `FAIL (serial)`, `FAIL (frames,
  vram)` e assim por diante.

Verificação:

```text
$ grep -n "asks only what every disc answers -- the$" tools/duckmcp/live.py; echo g1=$?
g1=1
$ grep -n "frame count is wrong" tools/duckmcp/live.py; echo g2=$?
g2=1
$ python3 -c "…live.failures(5,0,5,ok), …(game=Game(None,None)), …(5,0,4, vram=(1024,513))"
[] ['serial'] ['frames', 'vram']
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
```

A linha FAIL nomeando a condição é afirmada pelo check offline da CORR-DMCP-018, e vista na corrida
viva da CORR-DMCP-020.
- **Closed** — commit `fededb1c` (2026-10-23): fix(duckmcp): name the failed conditions in live.py's FAIL line, and its docstring
  - Files (`git show --name-status fededb1c`):
    - `M docs/tasks/duckmcp/CORR-DMCP-019.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/live.py`
