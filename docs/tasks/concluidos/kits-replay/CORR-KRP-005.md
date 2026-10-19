---
id: CORR-KRP-005
---

# CORR-KRP-005 — Log da KRP-TASK-04 cola resumo de extrator não versionado e pasta placeholder

Origin: [KRP-TASK-04](/docs/tasks/concluidos/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md)

## Problem

Os blocos de saída do Log da KRP-TASK-04 não são o que os comandos `$` deles imprimem.

- `figure --json` imprime um objeto JSON, mas o Log mostra uma linha de resumo por captura, sob os
  cabeçalhos "(campos schema, figure.root, ...)", "(campo section)" e "(schema, foci, follows)". Esse
  resumo saiu de um extrator cujo corpo não está no Log.
- A corrida vermelha do `kits_replay` usou
  `WE2002_KITS_REPLAY_DIR=<pasta com replay-10-3.json no lugar de replay-10-2.json>`, um placeholder
  que ninguém consegue remontar a partir do Log.
- As cinco linhas `$ python3 tools/kits/replay.py figure ...` não trazem o `WE2002_LOOKS_IMAGE`, de
  que precisam. Ele aparece só na prosa acima delas.

Isso fere a K3 e a regra "número em Log é colado da ferramenta".

## Evidência

```text
$ grep -n "(campos\|(campo section\|(schema, foci\|<pasta com" docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md
61:(campos schema, figure.root, figure.head, figure.armband, figure.replaces, still, turned, panel.panel, panel.number)
76:(campo section) {'cluts': [[0, 487]], ...
84:(schema, foci, follows) kits-replay/1 25 {'goalkeeper': 2, 'other': 0, 'outfield': 20}
105:$ WE2002_KITS_REPLAY_DIR=<pasta com replay-10-3.json no lugar de replay-10-2.json> WE2002_LOOKS_IMAGE=... ctest --test-dir build -R kits_replay --output-on-failure
```

## Root cause

Sondas ad hoc (um extrator de campos JSON e uma pasta de symlinks montada à mão) rodaram e tiveram a
saída colada, sem que as sondas entrassem no Log ou numa ferramenta versionada.

## Fix

No Log da task:

- colar a saída dos próprios leitores sem `--json` (ela já é curta), ou escrever o extrator inteiro
  num heredoc;
- escrever a corrida da pasta trocada como os passos que a remontam: `mkdir`, symlink das seis
  capturas boas, symlink de `replay-10-3.json` como `replay-10-2.json`, e então
  `python3 tools/kits/replay.py check <dir>`;
- pôr `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin` em cada linha `$`.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md`

## Verificação

```sh
grep -n "<pasta\|(campos" docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md
```

Hoje imprime 2 linhas. Depois do conserto não pode imprimir nada.

## Log de Execução

### 2026-10-13

No Log da KRP-TASK-04, os blocos das cinco capturas de perto, da seção 90 e do `walk` foram trocados
pela saída humana dos próprios leitores (`replay.py figure`, `figure --section 90`, `walk`, sem
`--json`), rodada de novo e colada inteira, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`
em toda linha `$`. A corrida vermelha do `kits_replay` virou passos que a remontam: `mktemp -d`,
symlink das seis capturas boas de `work/kits-oracle/`, symlink de `replay-10-3.json` como
`replay-10-2.json`, `replay.py check <pasta>` (rc=1, `kits_replay: 1 failure(s)`, o `FAIL` de
sha256 `d362…6ace8` contra `e9b7…2a7b`) e o mesmo pelo `ctest` com `WE2002_KITS_REPLAY_DIR` na pasta
(`***Failed`). A corrida *skipped* também foi refeita e colada inteira. O Log diz que esses blocos são
desta CORR. A prosa em volta ficou com o mesmo sentido; a menção a `far 2.27 e 2.55` saiu da frase da
seção 90, porque a saída humana não imprime esses campos.

```
$ grep -n "<pasta\|(campos" docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md; echo "grep rc=$?"
grep rc=1
```
- **Closed** — commit `5ebdd3fd` (2026-10-13): docs(kits-replay): paste real replay.py output and a rebuildable red run in KRP-TASK-04 Log
  - Files (`git show --name-status 5ebdd3fd`):
    - `M docs/tasks/kits-replay/04-replay-py-de-leitura-figures-figure-panel-walk.md`
    - `M docs/tasks/kits-replay/CORR-KRP-005.md`
