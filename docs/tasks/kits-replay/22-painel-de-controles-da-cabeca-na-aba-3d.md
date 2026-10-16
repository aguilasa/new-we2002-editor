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

Sem a caixa, o digest e o PNG são os de antes. Mesmos comandos na HEAD `ca147a8e` e na árvore da task:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1   (> digest-before.txt / digest-after.txt)
$ diff work/krp22/digest-before.txt work/krp22/digest-after.txt && echo SAME-DIGEST
SAME-DIGEST
$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure $f --export-3d work/krp22/after-fig$f.png   (f = 0, 1)
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 213 ms
  3d view: at 20,169, 940x409, yaw 180, pitch 0, frame 119 ms
$ cmp work/krp22/before-fig$f.png work/krp22/after-fig$f.png && echo SAME-PNG-$f
SAME-PNG-0
SAME-PNG-1
```

`confront --tab --player` antes (HEAD `ca147a8e`) e depois, nas três de perto, com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/<captura>.json --tab --player --out work/krp22/<antes|depois>`. Os números são os mesmos: com o painel a vista fica 786×409 em vez de 940×409 (`--export-3d … --player-looks A-L3-H-A-A` imprime `3d view: at 20,169, 786x409`), mas a altura é a mesma e a figura sai igual. Registra número, não afirma limite.

Antes:

```
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.442, 0.668 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.439, 0.748 over the colours the tab draws
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.335, 0.521 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.424, 0.636 over the colours the tab draws
  tab front (yaw 180) against the game's front capture: 4440 px, histogram intersection 0.500, 0.666 over the colours the tab draws
  tab back (yaw 0) against the game's back capture: 7381 px, histogram intersection 0.414, 0.730 over the colours the tab draws
```

Depois:

```
$ ... confront work/kits-replay/tab/replay-9-3-R1.json --tab --player
  tab front (yaw 180) against the game's back capture: 3200 px, histogram intersection 0.442, 0.668 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 3520 px, histogram intersection 0.439, 0.748 over the colours the tab draws
$ ... confront work/kits-replay/tab/replay-10-2-R1.json --tab --player
  tab front (yaw 180) against the game's back capture: 3401 px, histogram intersection 0.335, 0.521 over the colours the tab draws
  tab back (yaw 0) against the game's front capture: 2777 px, histogram intersection 0.424, 0.636 over the colours the tab draws
$ ... confront work/kits-replay/tab/replay-9-R1.json --tab --player
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
