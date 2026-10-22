---
id: CORR-DMCP-007
---

# CORR-DMCP-007 — Fazer os checks de janela mais larga e de PID próprio poderem falhar

Origin: [DMCP-TASK-08](/docs/tasks/duckmcp/08-fork.md)

## Problem

Dois checks do `fork.self_check` ficam verdes com o defeito que deviam pegar:

- (a) "with no match the widest non-dialog window wins": a lista de teste põe a janela mais larga que
  sobra ("Some Game", 800) antes de "Other" (400), então "pega a primeira" — o comportamento antigo do
  pes2 que o Log diz ter trocado — passa igual;
- (b) "running_pids never returns our own pid": o `pgrep -x duckstation-qt|AppRun|DuckStation-x64` nunca
  acha o python, então tirar o filtro `pid != os.getpid()` não muda nada.

## Evidência

```text
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C $S; cd $S; python3 - <<'PY'
p='tools/duckmcp/fork.py';s=open(p).read()
s=s.replace("return max(kept, key=lambda pair: pair[0])[1]","return kept[0][1]")
open(p,'w').write(s)
PY
$ python3 tools/duckmcp/selftest.py | grep -E 'FAIL|check\(s\)'
duckmcp_selftest: 194 check(s) ran, 0 failure(s)
$ S=$(mktemp -d); git -C /home/ingmar/desenvolvimento/github/new-we2002-editor archive HEAD tools | tar -x -C $S; cd $S; python3 - <<'PY'
p='tools/duckmcp/fork.py';s=open(p).read()
s=s.replace("if pid != os.getpid() and pid not in pids:","if pid not in pids:")
open(p,'w').write(s)
PY
$ python3 tools/duckmcp/selftest.py | grep -E 'FAIL|own pid|check\(s\)'
  ok    fork: running_pids never returns our own pid
duckmcp_selftest: 194 check(s) ran, 0 failure(s)
```

## Root cause

Os checks entraram sem defeito plantado que os derrubasse: a ordem da lista `seen` e a falta de um
`pgrep` injetável deixam os dois sem vermelho possível.

## Fix

Em `tools/duckmcp/fork.py` `self_check`: pôr uma janela mais estreita antes da mais larga na lista
`seen` (ex.: ("Other", 400) antes de ("Some Game", 800)); separar o parse da saída do `pgrep` numa
função pura que recebe as linhas e o PID próprio, e fazer o check sobre ela. Para cada caso, um
controle em `tools/duckmcp/controls.py` com o defeito plantado acima.

## Arquivos a criar ou modificar

- `tools/duckmcp/fork.py`
- `tools/duckmcp/controls.py`

## Verificação

As duas plantas da Evidência deixam `python3 tools/duckmcp/selftest.py` com pelo menos 1 falha cada, e
`python3 tools/duckmcp/controls.py` termina em "N red as required" com os dois controles novos
vermelhos. Na árvore real, o selftest sai 0.

## Log de Execução

2026-10-22 — reproduzido na HEAD `69910a9f`, e as duas plantas da Evidência dão
`duckmcp_selftest: 194 check(s) ran, 0 failure(s)`. Na (b) aparece
`ok    fork: running_pids never returns our own pid`.

Conserto:
- (a) Na lista `seen` do `self_check`, ("Other", 400) passou a vir antes de ("Some Game", 800).
- (b) O parse do `pgrep` já é a função pura `select_pids(found, own, cmdline)`, desde a CORR-DMCP-008. O
  check novo dá a ela o próprio PID na entrada e exige que ele saia; o check vivo antigo continua lá.
- Controles novos: `fork-first-window-wins` (`return kept[0][1]`) e `fork-own-pid-kept` (sem
  `pid == own`). O texto da planta (b) da Evidência mudou de lugar com a CORR-DMCP-008, e o controle
  planta onde o filtro mora agora.

Verificação:

```text
$ <planta (a) da Evidência numa cópia>; python3 tools/duckmcp/selftest.py | grep -E 'FAIL|check\(s\)'
  FAIL  fork: with no match the widest non-dialog window wins  o
  FAIL  fork: ANY_WINDOW is the same as no match
duckmcp_selftest: 196 check(s) ran, 2 failure(s)
$ python3 tools/duckmcp/controls.py --only fork-first-window-wins | tail -1
duckmcp_controls: 1 control(s), 1 red as required; per rule (fork) 1/1
$ python3 tools/duckmcp/controls.py --only fork-own-pid-kept | tail -2
red    fork-own-pid-kept (rule fork): FAIL  fork: select_pids drops our own pid even when pgrep lists it  [7, 8]
duckmcp_controls: 1 control(s), 1 red as required; per rule (fork) 1/1
$ python3 tools/duckmcp/controls.py | tail -1
duckmcp_controls: 19 control(s), 19 red as required; per rule (a) 2/2, (c) 8/8, (client) 2/2, (d) 4/4, (fork) 3/3
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 196 check(s) ran, 0 failure(s)
```
- **Closed** — commit `cc8d5a39` (2026-10-22): test(duckmcp): make the widest-window and own-pid checks able to fail
  - Files (`git show --name-status cc8d5a39`):
    - `M docs/tasks/duckmcp/CORR-DMCP-007.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/controls.py`
    - `M tools/duckmcp/fork.py`
