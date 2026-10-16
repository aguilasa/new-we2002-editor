---
id: CORR-KRP-018
---

# CORR-KRP-018 — Coluna de barba, match_scene com player e head --drawn sem controle plantado

Origin: [KRP-TASK-10](/docs/tasks/kits-replay/10-cabeca-pela-tupla-do-jogador-no-scene-of-e-no.md)

## Problem

A K2 da §9 do [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#9) pede que toda asserção nova venha
com um plant que a derrube, e que o Log mostre esse vermelho. Três veredictos ou caminhos de código
novos não têm controle no catálogo:

1. A asserção do selftest "the player's beard column moves to his beard colour". Ela fica vermelha
   quando plantada (abaixo), mas o `controls.py` não tem entrada para ela, então esse vermelho nunca
   apareceu no catálogo. A asserção "off the skin records … is the disc's" também não tem controle.
2. O caminho de jogador do `match_scene` (troca de seção mais `player_head_clut` no `order[0]`).
   Nenhum selftest, `kits_ui` ou checagem do oracle chama `match_figure` com `player=`, então quebrá-lo
   não deixa nenhum gate vermelho.
3. O `replay.py head --drawn` sai 1 quando há divergência, mas não tem plant, e nenhum gate nem o
   `check` o roda. O vermelho dele só foi visto na corrida ad hoc do revisor.

## Evidência

```text
$ python3 tools/kits/controls.py --list | grep player_head_clut
  figure-player-hair-unmoved   kits/core/figure.py :: player_head_clut
  figure-player-skin-unmoved   kits/core/figure.py :: player_head_clut
$ grep -n "player=" tools/kits/selftest.py tools/kits/oracle.py tools/kits/ui_check.py
(sem saída)
$ grep -n "drawn_head\|--drawn" tools/kits/*.py tools/kits/core/*.py
tools/kits/replay.py:18 / 1135   (só o uso e o argparse; nenhum gate chama)
```

Não há controle de coluna de barba.

Plants ad hoc, numa cópia de rascunho montada a partir da HEAD (`git archive HEAD tools | tar -x -C <tmp>`).

Trocando `        column += values["beard_colour"]\n` por `        column += 0\n` em
`tools/kits/core/figure.py`, dentro de `<tmp>/tools/kits`:

```text
$ python3 -c "import selftest
class C:
    def ok(self,n,c,d=''): print('PASS' if c else 'FAIL',n)
selftest._player_head_checks(C())"
FAIL figure.py: the player's beard column moves to his beard colour
```

Pelo mesmo método, trocando `        column += values["hair_colour"]\n` por `        column += 0\n`:

```text
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/replay.py head <repo>/work/kits-oracle/replay-10-2.json --drawn
... 17 differ: [[1, [32, 480], [16, 480]], ...]
0 of 1 drawn head(s) sample the game's CLUT on every primitive
```

## Root cause

A task catalogou plants só para a coluna de cabelo, a linha de pele e o gêmeo redirecionado; os
outros caminhos novos ficaram sem controle.

## Fix

Em `CONTROLS`, no `tools/kits/controls.py`:

- `figure-player-beard-unmoved`, plantando a linha de barba de `player_head_clut`;
- uma asserção de selftest ou de `kits_image` de que `match_figure(..., player="A-L3-B-A-B")` desenha
  a seção 46 com as CLUTs (32,480)/(160,480), mais um controle que plante a troca de CLUT de
  `number == order[0][0]` no `match_scene`;
- para o `head --drawn`, uma de duas: ligá-lo ao `replay.py check` (o gate `kits_replay`) com um
  controle em `drawn_head`, ou dizer na §3.2 que ele é relatório, não gate.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`
- `tools/kits/selftest.py`
- `tools/kits/core/figure.py` (alvo dos plants)
- `tools/kits/replay.py`

## Verificação

```sh
python3 tools/kits/controls.py --list | grep -c "figure-player-beard-unmoved"
```

Hoje dá 0. Depois do conserto tem de dar 1, e `python3 tools/kits/controls.py` tem de continuar
terminando em `controls: N of N red`.

## Log de Execução

**Reprodução na HEAD `f6a0cf7a`.** Os dois plants ad hoc da Evidência, num só script
(`repro018.sh`, no scratchpad da sessão): cópia por `git archive HEAD tools src/core data`, troca
literal de uma linha de `player_head_clut`, e a corrida.

O script inteiro (rodado da raiz do repositório; `S` e `REPO` aqui com a forma genérica do que a corrida usou):

```sh
#!/bin/bash
# CORR-KRP-018: the two ad hoc plants of the Evidence, on a scratch copy of HEAD.
REPO=$PWD
S=$(mktemp -d)
for plant in beard hair; do
  T=$S/repro018-$plant; rm -rf $T; mkdir -p $T
  git -C $REPO archive HEAD tools src/core data | tar -x -C $T
  python3 - "$T/tools/kits/core/figure.py" "$plant" <<'PY'
import sys
p, which = sys.argv[1], sys.argv[2]
old = '        column += values["%s_colour"]\n' % which
t = open(p).read(); assert t.count(old) == 1, t.count(old)
open(p, "w").write(t.replace(old, "        column += 0\n"))
PY
  echo "== plant: column += values[\"${plant}_colour\"] -> column += 0"
  if [ $plant = beard ]; then
    (cd $T/tools/kits && python3 -c "import selftest
class C:
    def ok(self,n,c,d=''): print('PASS' if c else 'FAIL',n)
selftest._player_head_checks(C())")
  else
    WE2002_LOOKS_IMAGE=$REPO/roms/japanese-shift-jis.bin python3 $T/tools/kits/replay.py head \
      $REPO/work/kits-oracle/replay-10-2.json --drawn | tail -2 | cut -c1-120
    echo "exit ${PIPESTATUS[0]}"
  fi
done
```

```text
$ bash repro018.sh
== plant: column += values["beard_colour"] -> column += 0
PASS figure.py: the player's hair column moves to his hair colour
FAIL figure.py: the player's beard column moves to his beard colour
PASS figure.py: the player's skin is the CLUT row 480 + skin_colour
PASS figure.py: a head CLUT in no hair or beard column, or off the skin records, is the disc's
PASS figure.py: the player's head is his HAIR style's section, the twin for beard F
PASS figure.py: a player that is not a looks tuple is refused in a sentence
== plant: column += values["hair_colour"] -> column += 0
           drawn A-L3-B-A-B: section 46 (the game's 46), 18 primitive(s) the game samples, 17 differ: [[1, [32, 480], [1
0 of 1 drawn head(s) sample the game's CLUT on every primitive
exit 1
```

(a linha do `drawn` sai cortada em 120 colunas pelo `cut` do script.)

**Conserto.**

1. `controls.py` ganha quatro controles, todos em `tools/kits/core/figure.py`:
   - `figure-player-beard-unmoved`: `column += values["beard_colour"]` vira `column += 0`;
     derruba "the player's beard column moves to his beard colour";
   - `figure-player-off-skin-moved`: a guarda de linha de pele de `player_head_clut` vira
     `if False:`; derruba "a head CLUT in no hair or beard column, or off the skin records, is the
     disc's" (a CLUT da linha 486 passa a ser movida para a linha de pele);
   - `figure-match-player-clut`: no `match_scene`, `number == order[0][0]` vira `number == -1`;
   - `figure-match-player-section`: no `match_scene`, a troca de `order[0]` pela seção do jogador
     vira `order = list(order)`.
2. `selftest.py` ganha `_player_match_checks`, no caminho **sem** imagem, que é o que o
   `controls.py` roda: o `match_scene` de verdade, com a pose versionada e o `match_order` de
   verdade, sobre um disco de faz-de-conta (toda seção com uma primitiva na coluna 1 e uma na
   coluna 9 da linha 480; `section.scan`, `_model_banks` e `_model_part` trocados dentro de um
   `try/finally`). Duas asserções: com `player="A-L3-B-A-B"` a ordem abre na 46 no lugar da 24 da
   pose e o resto é o mesmo; a 46 sai com (32,480) e (160,480) e toda outra seção com (16,480) e
   (144,480), as do disco. Os dois controles do `match_scene` ficam vermelhos por elas.
3. `selftest.py --image` (`kits_image`) ganha `_player_match_image_checks`: `api.match_figure` no
   TEX_00 do disco japonês, jogador `A-L3-B-A-B`, desenha a 46 com as CLUTs (32,480) e (160,480).
   O `controls.py` não alcança esta (o sandbox corre sem `WE2002_LOOKS_IMAGE`), então o vermelho
   dela no disco foi visto à parte (`red018-image.sh`, cópia da árvore de trabalho com o plant de
   `figure-match-player-clut`):

```sh
#!/bin/bash
# CORR-KRP-018: the kits_image assertion on match_figure(player=...) seen red on
# the disc, planting the CLUT swap of match_scene in a copy of the working tree.
REPO=$PWD
S=$(mktemp -d)
for plant in none clut; do
  T=$S/red018-$plant; rm -rf $T; mkdir -p $T/tools
  cp -r $REPO/tools/kits $REPO/tools/looks $REPO/tools/pes2 $T/tools/
  if [ $plant = clut ]; then
    python3 - "$T/tools/kits/core/figure.py" <<'PY'
import sys
p = sys.argv[1]
old = "            if values is not None and number == order[0][0]:\n"
t = open(p).read(); assert t.count(old) == 1, t.count(old)
open(p, "w").write(t.replace(old, "            if values is not None and number == -1:\n"))
PY
  fi
  echo "== plant: $plant"
  (cd $T/tools/kits && python3 -c "
import selftest
from core import api
class C:
    def ok(self, n, c, d=''): print('PASS' if c else 'FAIL', n, '' if c else '-- ' + d)
    def attempt(self, n, f, default=None): return f()
img = '$REPO/roms/japanese-shift-jis.bin'
selftest._player_match_image_checks(C(), api.open_source(img).kit('00'), api.read_geometry(img))")
done
```

```text
$ bash red018-image.sh
== plant: none
PASS match_figure, player A-L3-B-A-B on the disc: section 46 drawn, with CLUTs (32,480) and (160,480) 
== plant: clut
FAIL match_figure, player A-L3-B-A-B on the disc: section 46 drawn, with CLUTs (32,480) and (160,480) -- sections [2, 7, 8, 9, 10, 11, 12, 46, 95, 96, 97, 98], CLUTs of 46 [(16, 480), (144, 480)]
```

4. `head --drawn`: **relatório, não gate**, dito na §3.2 do
   [PLAN-KITS-REPLAY.md](/docs/PLAN-KITS-REPLAY.md#3.2). Uma linha de motivo: um controle em
   `drawn_head` nunca ficaria vermelho no `controls.py`, que roda sem disco e sem capturas, e a regra
   que ele confronta já é segura pelas asserções acima, cada uma com controle; ligá-lo ao `check`
   seria um gate sem vermelho visto no catálogo. O `replay.py` não mudou.

**Verificação.**

```text
$ python3 tools/kits/controls.py --list | grep -c "figure-player-beard-unmoved"
1
$ python3 tools/kits/controls.py --list | tail -1
controls: 80 catalogued
$ python3 tools/kits/controls.py --only figure-player-beard-unmoved
  base   unplanted sandbox            selftest exit 0
  RED    figure-player-beard-unmoved  kits/core/figure.py :: player_head_clut
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only figure-player-off-skin-moved
  base   unplanted sandbox            selftest exit 0
  RED    figure-player-off-skin-moved kits/core/figure.py :: player_head_clut
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only figure-match-player-clut
  base   unplanted sandbox            selftest exit 0
  RED    figure-match-player-clut     kits/core/figure.py :: match_scene
controls: 1 of 1 red
$ python3 tools/kits/controls.py --only figure-match-player-section
  base   unplanted sandbox            selftest exit 0
  RED    figure-match-player-section  kits/core/figure.py :: match_scene
controls: 1 of 1 red
$ python3 tools/kits/controls.py | tail -1
controls: 80 of 80 red
$ python3 tools/kits/selftest.py | grep match_scene; python3 tools/kits/selftest.py | tail -1
  ok    figure.py: match_scene with a player draws his section where the head was, the rest of the order kept
  ok    figure.py: match_scene with a player draws his head with his CLUTs, (32,480) and (160,480), and every other section with the disc's
kits_selftest: 0 failure(s)
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/selftest.py --image | grep "A-L3-B-A-B\|failure"
kits_image: 0 failure(s)
  ok    match_figure, player A-L3-B-A-B on the disc: section 46 drawn, with CLUTs (32,480) and (160,480)
figure: 0 failure(s)
```

O `--image` acima correu sem `WE2002_KITS_REPLAY_DIR` (última linha `replay captures: not read`);
o conserto não toca no `replay.py`.
- **Closed** — commit `34430857` (2026-10-16): test(kits): plant the beard column and match_scene's player head; head --drawn is a report
  - Files (`git show --name-status 34430857`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/CORR-KRP-018.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
