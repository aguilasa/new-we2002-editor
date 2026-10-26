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

**Reprodução (2026-10-26, HEAD `e8890dd1`, `rite reproduce CORR-DMCP-034 --cycle duckmcp`):** REPRODUCED
pelo `grep` (o `sha1sum <esse caminho>` tem marcador e não roda):

```text
$ grep -n 'WE2002_LOOKS_IMAGE=' docs/tasks/duckmcp/27-fechamento-fase-7.md
61:$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/471f5f13-0bad-4499-8e65-753e81531194/scratchpad/dmcp22/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R 'kits_replay|tasks'
```

**Conserto.** Em vez de um marcador na linha `$` (que deixaria de rodar como escrita), uma cópia que
dura em `work/`, ignorada pelo git, com o digest do original:

```text
$ sha1sum roms/japanese-shift-jis.bin work/looks-japanese-shift-jis.bin
93d16f10527fb116e48dfceae21ceb4b773c4aac  roms/japanese-shift-jis.bin
93d16f10527fb116e48dfceae21ceb4b773c4aac  work/looks-japanese-shift-jis.bin
$ git check-ignore -q work/looks-japanese-shift-jis.bin && echo ignored
ignored
```

A corrida foi refeita com ela, e o bloco do Log da 27 passou a trazer a linha nova, a saída nova e uma
nota dizendo o que foi trocado e por quê (o `Passed 11.83 sec` original fica citado na nota):

```text
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/work/looks-japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R 'kits_replay|tasks' 2>&1 | grep -E "Test #|tests passed"
2/2 Test #22: kits_replay ......................   Passed   12.19 sec
100% tests passed, 0 tests failed out of 2
```

**Verificação:**

```text
$ grep -c '/tmp/claude-1000/.*/scratchpad' docs/tasks/duckmcp/27-fechamento-fase-7.md
0
$ rite check --cycle duckmcp --json      # errors, warnings
0 0
```
- **Closed** — commit `dd51cbed` (2026-10-26): docs(duckmcp): kits_replay line of task 27 runs against a copy in work/
  - Files (`git show --name-status dd51cbed`):
    - `M docs/tasks/duckmcp/27-fechamento-fase-7.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-034.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
