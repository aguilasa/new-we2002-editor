---
id: CORR-DMCP-034
---

# CORR-DMCP-034 — Apontar a linha do kits_replay no Log da 27 para um caminho de imagem que dure

Origin: [DMCP-TASK-27](/docs/tasks/duckmcp/27-fechamento-fase-7.md)

## Problem

A linha `$` do `kits_replay` no Log aponta `WE2002_LOOKS_IMAGE` para o scratchpad de outra sessão
(`/tmp/claude-1000/.../471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin`).
O arquivo existe hoje e tem o mesmo digest de `roms/japanese-shift-jis.bin`, mas é temporário: some
quando aquele scratchpad for limpo, e a linha deixa de rodar como está escrita. O veredito se mantém
numa cópia da mesma imagem (Passed, `kits_replay: 0 failure(s)`); o problema é só como a evidência foi
registrada.

## Evidência

```text
$ grep -n 'WE2002_LOOKS_IMAGE=' docs/tasks/duckmcp/27-fechamento-fase-7.md
...WE2002_LOOKS_IMAGE=/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin ...
$ sha1sum <esse caminho> roms/japanese-shift-jis.bin
93d16f10527fb116e48dfceae21ceb4b773c4aac (os dois)
```

## Root cause

Hipótese, não provada: a linha foi copiada do shell da corrida em vez de ser escrita com um caminho que
dure.

## Fix

No Log da `docs/tasks/duckmcp/27-fechamento-fase-7.md`, escrever a linha `$` com um caminho de cópia
genérico, como a receita do `CLAUDE.md` faz (`WE2002_LOOKS_IMAGE=<cópia de roms/japanese-shift-jis.bin>`),
ou com uma cópia em `work/`. O veredito colado continua o mesmo.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/27-fechamento-fase-7.md`

## Verificação

`grep -c '/tmp/claude-1000/.*/scratchpad' docs/tasks/duckmcp/27-fechamento-fase-7.md` dá 1 hoje e 0
depois.

## Log de Execução
