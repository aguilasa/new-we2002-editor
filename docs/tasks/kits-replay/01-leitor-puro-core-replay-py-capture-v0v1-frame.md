---
id: KRP-TASK-01
---

# KRP-TASK-01 — Leitor puro core/replay.py: Capture v0→v1, Frame, Figure e Walk, com os casos sintéticos migrados

## Goal

Existe `tools/kits/core/replay.py`, o leitor puro de captura de replay: `Capture.load` (com migração do schema v0 das capturas de hoje para o v1), `Frame`, `Figure` (com `sections`, `panel`, `pose`, `box`), `Walk.load` e os juízes `judge`/`judge_walk`, sem emulador e sem `tools/looks/oracle`. É o código que o `oracle.py` passa a importar na KRP-TASK-02.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/replay.py` (novo)
  - `tools/kits/selftest.py` (os casos sintéticos de `oracle --replay` e `--replay-field` migram para o leitor)
  - `tools/kits/controls.py`
  - `docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md` (nota de passagem: os auxiliares copiados que o move tem de tirar do oracle)
- Out:
  - `tools/kits/oracle.py` (o move é a KRP-TASK-02)
  - a linha de comando (KRP-TASK-04)

## Done criteria

- [x] `grep -nE '^(from|import) ' tools/kits/core/replay.py` não lista `tools.looks.oracle` nem `oracle`, nem `fork`/`mcp`
- [x] `python3 tools/kits/selftest.py`: os casos sintéticos de replay passam a nomear `core/replay` e saem `ok`; nenhum caso existe duplicado (contagem de casos de replay igual antes e depois, colada no Log)
- [x] `Capture.load` lido sobre as sete capturas de `work/kits-oracle/` (cinco de perto, dois laços) devolve `schema` 1 e as chaves fixas do [§2.1](/docs/PLAN-KITS-REPLAY.md#2.1); o sha256 de cada captura vai no Log
- [x] uma planta (captura com chave faltando) faz o `Capture.load` recusar com mensagem que nomeia a chave, vista vermelha no `controls.py`
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Pontos de partida no `oracle.py`: `_restore_samples`, `replay_figures`, `replay_focus`, `field_focus`, `section_samples`, `panel_samples`, `figure_tag`, `replay_judge`, `replay_field_judge`. Nesta task o código pode ser escrito a partir delas; a remoção do oracle é a 02, e as duas juntas não podem deixar cópia. Armadilha K1: o esperado é constante por (slot, foco).

## Log de Execução

### 2026-10-12

Criado `tools/kits/core/replay.py`: `Capture.load`/`from_dict` (v0→v1, recusa por chave com
`ReplayError`), `Frame`, `Figure` (subclasse de `list`: os juízes e funções que recebiam a figura
como lista de peças continuam recebendo), `Walk.load`/`of`, `judge`, `judge_walk`. Diferenças de
assinatura em relação ao texto do [§2.1](/docs/PLAN-KITS-REPLAY.md#2.1), todas por o leitor ser
puro: o índice do MODEL.BIN e a largura do registro do uniforme entram como parâmetro
(`Figure.panel(index, pages, width, on_torso)`, `Figure.sections(index, buffer, texture)`,
`Walk.load(path, index, width)`); `Capture.frames(side)` escolhe frente ou costas; o v1 traz
também `kind` (`close`/`walk`). A nota da KRP-TASK-02 lista os auxiliares copiados que o move tem
de tirar do oracle.

Imports, sem `oracle`, `fork` nem `mcp`:

```
$ grep -nE '^(from|import) ' tools/kits/core/replay.py
24:from __future__ import annotations
26:import json
27:import os
28:import re
30:from . import tex  # noqa: F401  (tex puts tools/pes2 and tools/looks on sys.path)
31:from .errors import KitsError
32:from .figure import BACK_COPY, GLYPH_W
33:from .zones import GAPS, ZONES
35:import layout  # noqa: E402  (tools/looks)
```

Casos de replay do selftest: antes, 26 linhas `--replay` (`python3 tools/kits/selftest.py`,
`grep -c -- '--replay'` da saída). Depois (`python3 tools/kits/selftest.py --no-plant`, bloco
`replay self-check`): 23 nomeiam `core/replay`, 3 continuam `oracle --replay` porque testam a
leitura da lista da GPU e o `replay_chooser`, que ficam no oracle (`textured_samples`,
`draw_offset`); 26 = 23 + 3, nenhum duplicado. Mais 4 casos novos (`Capture` v0→v1, walk v1,
chave faltando, `Figure`). `replay: 0 failure(s)`.

As sete capturas, checagem versionada no `kits_image` (`REPLAY_CAPTURES`, esperado constante por
arquivo):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle python3 tools/kits/selftest.py --image
replay captures self-check
  ok    Capture.load(replay-9.json): schema 1, close 9 0 None 0
  ..... replay-9.json sha256 125ff69bf1fedc188a12ee933ec431c6d9fbd4f79c7488966c08304b87551b1d
  ok    Capture.load(replay-9-3.json): schema 1, close 9 3 L2 3
  ..... replay-9-3.json sha256 f34717387cc1f706ad9921c65fc5473fa9cd7ab53cecdfa938c2de680bddb5a8
  ok    Capture.load(replay-10.json): schema 1, close 10 0 None 0
  ..... replay-10.json sha256 8dde786284f499c52ef58480a2dea963fa982259f320a7ad50bcf3229009811a
  ok    Capture.load(replay-10-2.json): schema 1, close 10 2 L2 2
  ..... replay-10-2.json sha256 e9b785b2a6cf80029293fbbd20fc873eeeeebe919d6e08cc11ef03e0928d2a7b
  ok    Capture.load(replay-10-3.json): schema 1, close 10 3 L2 3
  ..... replay-10-3.json sha256 d362901327da8d5efba910f6f456cbb357fb19eb53807751751a401c1fe6ace8
  ok    Capture.load(replay-field-9-capture.json): schema 1, walk 9 None L2 24
  ..... replay-field-9-capture.json sha256 efb8e1e4b1b7e62411faf5224eb80265843af43a5e3290bc39c9ba74d9426971
  ok    Capture.load(replay-field-10-capture.json): schema 1, walk 10 None L2 24
  ..... replay-field-10-capture.json sha256 57e8f52326f6e9f03503223bd38874a58314b6754f5d0825cae082956341d8f4
replay captures: 0 failure(s)
```

Planta com dado real: pasta com `replay-10-3.json` no lugar de `replay-10-2.json`
(`WE2002_KITS_REPLAY_DIR=<pasta plantada> python3 tools/kits/selftest.py --image --quiet`, sai 1):

```
  FAIL  Capture.load(replay-10-2.json): schema 1, close 10 2 L2 2  schema 1, ('close', 10, 3, 'L2', 3)
replay captures: 1 failure(s)
```

Controles novos (`replay-key-check`, `replay-v0-slot`), e a linha `FAIL` de cada um na cópia
plantada (`selftest.py --no-plant`, sai 1):

```
replay-key-check exit 1
  FAIL  core/replay: a capture lacking a key is refused, naming the key: did NOT refuse
replay-v0-slot exit 1
  FAIL  core/replay: a v0 close capture comes back as v1, slot and focus off its name  (1, 'close', 9, 3, 'L2', 3)
```

Nove controles que plantavam nas funções de análise do `oracle.py` ficaram verdes depois da
migração dos casos (a primeira corrida deu `controls: 46 of 55 red`); foram migrados para
`kits/core/replay.py` com o prefixo `oracle-` tirado do id: `replay-focus-unasked`,
`replay-modulation-ignored`, `replay-field-margin-unasked`, `replay-field-still-unasked`,
`replay-field-players-unasked`, `replay-field-shared-panel`, `replay-field-nearest-followed`,
`replay-shared-cell-kept`, `replay-sleeves-unjudged` — os nove `RED` em `--only`. Os ids antigos
só aparecem em tasks arquivadas do `kits-3d`, como registro.

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed  221.92 sec
2/4 Test #19: kits_image .......................   Passed   28.26 sec
3/4 Test #20: kits_gen .........................   Passed    0.03 sec
4/4 Test #21: kits_ui ..........................   Passed  214.98 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 55 of 55 red
```
- **Closed** — commit `a51525f0` (2026-10-12): feat(kits): pure replay reader core/replay.py
  - Files (`git show --name-status a51525f0`):
    - `M docs/tasks/kits-replay/01-leitor-puro-core-replay-py-capture-v0v1-frame.md`
    - `M docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tools/kits/controls.py`
    - `A tools/kits/core/replay.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/core/replay.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`, `docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-12) at `edd0dfb2`: CORR-KRP-001
