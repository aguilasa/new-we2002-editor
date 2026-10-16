---
id: KRP-TASK-22
---

# KRP-TASK-22 — Painel de controles da cabeça na aba 3D, no lugar da tupla em texto

## Goal

A aba 3D não tem mais o campo de texto da tupla: com "Cabeça do jogador" marcada, um painel à direita da vista mostra um `QComboBox` por campo da tupla (pele, estilo e cor do cabelo, estilo e cor da barba), com os rótulos do [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3) nas duas línguas e a largura reajustada a cada troca de idioma; a cabeça desenhada sai dos combos.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/api.py` (`PLAYER_FIELDS`, `player_tuple`, `player_fields`: a UI fala só com o `api`)
  - `tools/kits/ui/app.py` (o painel, o `--player-looks` posicionando os combos, o `--list-3d`)
  - `tools/kits/ui/i18n.py` (título do painel e os cinco rótulos)
  - `tools/kits/ui_check.py` (juiz do painel e das larguras, e as plantas)
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.3: o 940×409 → 786×409 medido e os números de confronto inalterados; declarado pela [CORR-KRP-022](/docs/tasks/kits-replay/CORR-KRP-022.md))
- Out:
  - o sexto campo (`boots`), altura e corpo (§3.3)
  - o seletor de jogador real (KRP-TASK-17)
  - a regra da cabeça (§3.1, §3.2): não muda

## Done criteria

- [x] nenhum `QLineEdit` na aba 3D (`grep -n player_edit tools/kits/ui/app.py` vazio)
- [x] `app.py … --list-3d` imprime o painel oculto sem a caixa e visível com ela, e os cinco combos com 4, 32, 8, 7 e 7 itens, com os rótulos do §3.3 em en-US e pt-BR
- [x] trocar de idioma ao vivo (`--switch-to`) muda a largura do painel e nenhum rótulo corta, julgado pelo `kits_ui`, com a planta de largura fixa vista vermelha
- [x] sem a caixa marcada, o digest de `cli.py figure` e o PNG de `--export-3d` são os de antes da task
- [x] `replay.py confront <captura> --tab --player` antes e depois, nas três capturas de perto, colado da HEAD no Log (registra número, não afirma limite)
- [x] o `kits_ui` cobre o painel com plantas: painel nunca mostrado, combo de cor do cabelo ignorado, largura fixa
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Decisão do usuário (2026-10-16), com imagem: o painel à direita da vista, os rótulos literais do §3.3. Os combos ficam como atributos da janela, para o `combos()` do `app.py` (que acha combo por `vars(self)`) lhes dar `AdjustToContents` e o juiz de largura de combo existente os alcançar.

## Log de Execução

- **done** (2026-10-16): o campo de texto da tupla saiu da aba 3D. Com "Cabeça do jogador" marcada, um `QGroupBox` à direita da vista mostra um `QComboBox` por campo (`api.PLAYER_FIELDS`), com os rótulos do §3.3; os combos são atributos da janela (`head_<campo>_box`), então o `combos()` lhes dá `AdjustToContents` e o juiz de largura de combo os alcança (`COMBO_NAMES` ganhou os cinco). `retranslate()` reescreve os rótulos e chama `fit_head_panel()`, que refaz a largura fixa do painel. O `--player-looks` posiciona os combos e recusa tupla inválida com saída 2. Arquivo além dos de início, declarado por `rite set --files`: `docs/PLAN-KITS-REPLAY.md`, porque o §3.3 previa que o `confront --tab --player` mudaria de número, e a medição abaixo mostrou que não muda.

```
$ grep -n player_edit tools/kits/ui/app.py; echo "grep exit $?"
grep exit 1
```

O painel e os combos, nas duas línguas, sem e com a caixa (`--player-looks` marca a caixa):

```
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang en-US  --list-3d
  box player head: shown True, enabled True, ticked False, text Player's head (looks)
  line edits: 0
  head panel: Player's head, shown False, width 148, looks A-A1-A-A-A
  head skin_colour: Skin Color, label width 61, combo width 40, 4 items, current A
  head hair_style: Hair Style, label width 57, combo width 47, 32 items, current A1
  head hair_colour: Hair Color, label width 60, combo width 40, 8 items, current A
  head beard_style: Beard Style, label width 68, combo width 40, 7 items, current A
  head beard_colour: Beard Color, label width 71, combo width 40, 7 items, current A
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang en-US --player-looks A-L3-H-A-A --list-3d
  box player head: shown True, enabled True, ticked True, text Player's head (looks)
  line edits: 0
  head panel: Player's head, shown True, width 148, looks A-L3-H-A-A
  head skin_colour: Skin Color, label width 61, combo width 40, 4 items, current A
  head hair_style: Hair Style, label width 57, combo width 47, 32 items, current L3
  head hair_colour: Hair Color, label width 60, combo width 40, 8 items, current H
  head beard_style: Beard Style, label width 68, combo width 40, 7 items, current A
  head beard_colour: Beard Color, label width 71, combo width 40, 7 items, current A
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang pt-BR  --list-3d
  line edits: 0
  head panel: Cabeça do jogador, shown False, width 172, looks A-A1-A-A-A
  head skin_colour: Cor da Pele, label width 69, combo width 40, 4 items, current A
  head hair_style: Estilo do Cabelo, label width 95, combo width 47, 32 items, current A1
  head hair_colour: Cor do Cabelo, label width 84, combo width 40, 8 items, current A
  head beard_style: Estilo da Barba, label width 89, combo width 40, 7 items, current A
  head beard_colour: Cor da Barba, label width 78, combo width 40, 7 items, current A
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 14 --tab 3d --lang pt-BR --player-looks A-L3-H-A-A --list-3d
  line edits: 0
  head panel: Cabeça do jogador, shown True, width 172, looks A-L3-H-A-A
  head skin_colour: Cor da Pele, label width 69, combo width 40, 4 items, current A
  head hair_style: Estilo do Cabelo, label width 95, combo width 47, 32 items, current L3
  head hair_colour: Cor do Cabelo, label width 84, combo width 40, 8 items, current H
  head beard_style: Estilo da Barba, label width 89, combo width 40, 7 items, current A
  head beard_colour: Cor da Barba, label width 78, combo width 40, 7 items, current A
```

Troca ao vivo (`--switch-to`), julgada pelo `head_judge` do `kits_ui`: depois da troca, painel en-US 148 px e pt-BR 172 px, e todo rótulo com a largura que o texto pede. A planta `head panel width fixed` (o `fit_head_panel()` só na primeira vez) corta dois rótulos, e fica vermelha (linhas do `ctest` abaixo).

Sem a caixa, o digest e o PNG são os de antes. Lado antes: as `tools/` da HEAD `ca147a8e` extraídas fora do repositório. Lado depois: a árvore do repositório. Os dois rodam com o repositório como diretório corrente, porque o `confront` acha o venv por `work/venv-looks/…` relativo a ele.

Este bloco e os dois `confront` abaixo foram **refeitos em 2026-10-16 pela [CORR-KRP-023](/docs/tasks/kits-replay/CORR-KRP-023.md)**, com cada comando inteiro. O lado depois agora é a HEAD `17b1d791`, não a árvore da task. Desde a task o `app.py` mudou em dois pontos: a CORR-KRP-024 pôs `fits` no `--list-combos`, e a CORR-KRP-025 deixou status e nota de geometria numa linha só, o que só pesa com caminho de imagem longo. Nenhum número mudou: digest, PNG e as seis interseções são os da corrida original, e `work/krp22/digest-after.txt` e `work/krp22/after-fig{0,1}.png` batem byte a byte com os refeitos. O `app.py` imprime as linhas de status e `window up`, que a transcrição original cortava, e o `frame` (ms) é tempo de relógio.

```
$ git rev-parse HEAD
17b1d7910304351f63a0e218e9977e0635afc610
$ mkdir -p /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before work/krp23
$ git archive ca147a8e tools | tar -x -C /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 > work/krp23/digest-before.txt
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --match --set 1 >> work/krp23/digest-before.txt
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 > work/krp23/digest-after.txt
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --match --set 1 >> work/krp23/digest-after.txt
$ cat work/krp23/digest-before.txt
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  9b136766e64f5bc1ae1b961002014bdc5e1e2bbf3f7fa39cb9fbf338afaa96ec
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  aab125ff5eb9f7d40d8498fb4c4aec868d86745a2d53ba9301ca83477794726c
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  e32b14c8e91bed5efa8d0c514780689f4e7f049b647182e27265faa9ed6a8ca6
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  c3d349fdd92419692989e849617d158465f656e6e65b721e77c442901a24a6dd
figure 0: set 1 and set 2 differ
figure 1: set 1 and set 2 differ
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  a68ac8aca6428b0d2fdb5daa6f2c066bbe383e853dc562d85347f57ee01fa97b
$ cat work/krp23/digest-after.txt
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  9b136766e64f5bc1ae1b961002014bdc5e1e2bbf3f7fa39cb9fbf338afaa96ec
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  aab125ff5eb9f7d40d8498fb4c4aec868d86745a2d53ba9301ca83477794726c
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  e32b14c8e91bed5efa8d0c514780689f4e7f049b647182e27265faa9ed6a8ca6
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  c3d349fdd92419692989e849617d158465f656e6e65b721e77c442901a24a6dd
figure 0: set 1 and set 2 differ
figure 1: set 1 and set 2 differ
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  a68ac8aca6428b0d2fdb5daa6f2c066bbe383e853dc562d85347f57ee01fa97b
$ diff work/krp23/digest-before.txt work/krp23/digest-after.txt && echo SAME-DIGEST
SAME-DIGEST
$ diff work/krp22/digest-after.txt work/krp23/digest-after.txt && echo SAME-AS-TASK22-DIGEST
SAME-AS-TASK22-DIGEST
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 0 --export-3d work/krp23/before-fig0.png
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 107 ms
  Croatia — TEX_22 · image work bitmap, 1st set · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 1 --export-3d work/krp23/before-fig1.png
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 105 ms
  Croatia — TEX_22 · image work bitmap, 1st set · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 0 --export-3d work/krp23/after-fig0.png
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 106 ms
  Croatia — TEX_22 · image work bitmap, 1st set · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
$ DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 1 --export-3d work/krp23/after-fig1.png
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 109 ms
  Croatia — TEX_22 · image work bitmap, 1st set · palette player palette, first set · /BIN/TEX_22.BIN on roms/japanese-shift-jis.bin, 30772 bytes
  window up, at -32000,-32000
$ cmp work/krp23/before-fig0.png work/krp23/after-fig0.png && echo SAME-PNG-0
SAME-PNG-0
$ cmp work/krp23/before-fig1.png work/krp23/after-fig1.png && echo SAME-PNG-1
SAME-PNG-1
$ cmp work/krp22/after-fig0.png work/krp23/after-fig0.png && echo SAME-AS-TASK22-PNG-0
SAME-AS-TASK22-PNG-0
$ cmp work/krp22/after-fig1.png work/krp23/after-fig1.png && echo SAME-AS-TASK22-PNG-1
SAME-AS-TASK22-PNG-1
```

`confront --tab --player` antes e depois, nas três de perto. Os números são os mesmos: com o painel a vista fica 786×409 em vez de 940×409 (`--export-3d` com `--player-looks A-L3-H-A-A` imprime `3d view: at 20,169, 786x409`), mas a altura é a mesma e a figura sai igual. Registra número, não afirma limite.

Antes (`ca147a8e`):

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab --player --out work/krp23/before
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.442, 0.668 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.439, 0.748 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab --player --out work/krp23/before
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.335, 0.521 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.424, 0.636 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 /tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before/tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out work/krp23/before
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
```

Depois (HEAD `17b1d791`):

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab --player --out work/krp23/after
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.442, 0.668 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.439, 0.748 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab --player --out work/krp23/after
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.335, 0.521 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.424, 0.636 over the colours the tab draws
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out work/krp23/after
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
```

Plantas novas: no `kits_ui`, `head panel never shown`, `head panel width fixed` (juiz `head_judge`) e `hair colour combo ignored` (juiz `player_judge`); no `controls.py`, `api-player-tuple-drops-a-field`, contra a asserção do `selftest.py` que faz ida e volta de `player_fields`/`player_tuple`. A planta `Player's head ignored` continua casando a linha de antes.

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits -V
1/5 Test #18: kits_selftest ....................   Passed  341.92 sec
2/5 Test #19: kits_image .......................   Passed   27.66 sec
3/5 Test #20: kits_gen .........................   Passed    0.02 sec
21:   ok    the head panel: no text field on the 3D tab, hidden unticked and shown ticked with the five combos and their labels in en-US and pt-BR, and refitted on a live switch (panel width after the switch en-US 148, pt-BR 172)
21:         plant 'hair colour combo ignored': Croatia 11 and Croatia 2 draw the same 3D view
21:   ok    plant 'hair colour combo ignored' fails the player head judge
21:         plant 'head panel never shown': en-US ticked True: ["head panel: Player's head, shown False, width 148, looks A-L3-H-A-A"], not "head panel: Player's head, shown True,"...; pt-BR ticked True: ['head panel: Cabeça do jogador, shown False, width 172,
21:   ok    plant 'head panel never shown' fails the head panel judge
21:         plant 'head panel width fixed': en-US to pt-BR: the label of hair_style is 84 px and its text needs 95; en-US to pt-BR: the label of beard_style is 84 px and its text needs 89
21:   ok    plant 'head panel width fixed' fails the head panel judge
21: kits_ui: 0 failure(s)
4/5 Test #21: kits_ui ..........................   Passed  239.92 sec
5/5 Test #22: kits_replay ......................   Passed   12.04 sec
The following tests passed:
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
  RED    api-player-tuple-drops-a-field kits/core/api.py :: player_tuple
controls: 81 of 81 red
```
- **Closed** — commit `c74ba1cb` (2026-10-16): feat(kits): head panel of combos in place of the looks tuple text field
  - Files (`git show --name-status c74ba1cb`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui/app.py`
    - `M tools/kits/ui/i18n.py`
    - `M tools/kits/ui_check.py`
  - **Outside declared files** (`tools/kits/core/api.py`, `tools/kits/ui/app.py`, `tools/kits/ui/i18n.py`, `tools/kits/ui_check.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`, `docs/PLAN-KITS-REPLAY.md`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
- **Reviewed** (2026-10-16) at `34809e3f`: CORR-KRP-022, CORR-KRP-023, CORR-KRP-024, CORR-KRP-025
