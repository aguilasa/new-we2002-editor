---
id: KRP-TASK-24
---

# KRP-TASK-24 — A pele do corpo segue a Cor da Pele do painel da cabeça

## Goal

Na figura da aba, trocar a Cor da Pele no painel da cabeça muda também a pele do corpo (braços, pernas, mãos), pela regra que o ciclo `looks` mediu na `LOOKS SET`, como o [§3.3](/docs/PLAN-KITS-REPLAY.md#3.3) decide.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/core/figure.py` (`scene_of` monta a figura com o `skin_colour` do jogador)
  - `tools/kits/ui_check.py` (o `player_judge` exige o corpo diferente entre duas peles, com planta)
  - `tools/kits/selftest.py`
  - `docs/PLAN-KITS-REPLAY.md` (§3.3: a decisão)
- Out:
  - o `match_scene` (a aba não o desenha; §3.3)
  - cabelo e barba: só a cabeça os tem

## Done criteria

- [x] sem a opção, o digest de `cli.py figure` é o de antes da task
- [x] `cli.py figure … --player D-L3-H-A-A` contra `--player A-L3-H-A-A`: toda primitiva fora da cabeça que muda de CLUT desce 3 linhas, e alguma muda, impresso por comando versionado
- [x] o `kits_ui` exige o corpo (abaixo da cabeça) diferente entre as duas peles, e a planta que monta o corpo na pele de referência fica vermelha
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Decisão do usuário (2026-10-16), vendo o painel da KRP-TASK-22: "se mudar a cor da cabeça, tem que mudar a cor do corpo". Revoga, na aba, o "inclusive a pele do corpo" do §3.2.

## Log de Execução

- **done** (2026-10-16): o `scene_of` monta a figura com o `skin_colour` do jogador no lugar do da tupla de referência, e a cabeça entra depois pela regra do §3.1. A pele do corpo segue a regra da `LOOKS SET` (CORR-LOOKS-103). O `match_scene` não muda (§3.3).

Achado ao mexer no `player_judge`: desde a KRP-TASK-22, a comparação "reference × Croatia 11" media o painel aparecendo, não a cabeça. A captura de referência saía sem a caixa marcada (painel oculto, vista de 940 px), e deu 108094 px no `kits_ui` da árvore de antes desta task (`34763c76`; remontagem abaixo, refeita pela [CORR-KRP-028](/docs/tasks/kits-replay/CORR-KRP-028.md) em 2026-10-17). Agora a referência é capturada com a caixa marcada e a tupla `A-A1-A-A-A` (`REFERENCE_LOOKS`), e a diferença volta a ser da cabeça: 7449 px. Com isso a planta `Player's head ignored` derruba as três comparações, não só duas.

Sem a opção, o digest é o de antes (`34763c76` contra a HEAD; refeito pela CORR-KRP-028 em
2026-10-17, com a HEAD `4460419b`). O script, rodado da raiz do repositório:

```sh
#!/bin/bash
# CORR-KRP-028: digest of cli.py figure before (34763c76) and at HEAD, from the repository root.
set -e
R=$PWD
T=$(mktemp -d)
git archive 34763c76 | tar -x -C "$T"
mkdir -p work/krp28
for side in before after; do
  if [ $side = before ]; then D=$T; else D=$R; fi
  out=$R/work/krp28/digest-$side.txt
  (cd "$D" && WE2002_LOOKS_IMAGE=$R/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure $R/roms/japanese-shift-jis.bin --tag 22) > $out
  (cd "$D" && WE2002_LOOKS_IMAGE=$R/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure $R/roms/japanese-shift-jis.bin --tag 22 --match --set 1) >> $out
done
cat work/krp28/digest-before.txt
diff work/krp28/digest-before.txt work/krp28/digest-after.txt && echo SAME
```

```text
$ bash krp028.sh
set 1 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  9b136766e64f5bc1ae1b961002014bdc5e1e2bbf3f7fa39cb9fbf338afaa96ec
set 1 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  aab125ff5eb9f7d40d8498fb4c4aec868d86745a2d53ba9301ca83477794726c
set 2 figure 0  593 parts, 593 textured, 6 surfaces, bounds (-113,-33,-281)..(65,419,27)  e32b14c8e91bed5efa8d0c514780689f4e7f049b647182e27265faa9ed6a8ca6
set 2 figure 1  629 parts, 629 textured, 6 surfaces, bounds (-113,-33,-281)..(60,419,27)  c3d349fdd92419692989e849617d158465f656e6e65b721e77c442901a24a6dd
figure 0: set 1 and set 2 differ
figure 1: set 1 and set 2 differ
set 1 match figure, long sleeves: order 24 2 95 96 97 98 7 9 11 8 10 12  140 parts, 140 textured, 7 surfaces  a68ac8aca6428b0d2fdb5daa6f2c066bbe383e853dc562d85347f57ee01fa97b
SAME
```

A remontagem do 108094, também da raiz do repositório e com o `:98` de pé:

```sh
#!/bin/bash
# CORR-KRP-028: the kits_ui of the tree before the task (34763c76), for the reference against Croatia 11 line.
R=$PWD
T=$(mktemp -d)
git archive 34763c76 | tar -x -C "$T"
mkdir -p "$T/work"; ln -s "$R/work/venv-looks" "$T/work/venv-looks"
(cd "$T" && DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$R/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py) | grep "reference against"
```

```text
$ bash krp028-ui.sh
  ok    3D TEX_14: Player's head draws the looks tuple's head, and two players apart only in hair colour are drawn apart (reference against Croatia 11 108094 px, Croatia 11 against Croatia 2 617 px)
```

O corpo entre peles A e D sai do `kits_image` (`selftest.py --image`, `_player_skin_image_checks`); a planta `the body's skin not moved` derruba o `kits_ui`:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits -V
1/5 Test #18: kits_selftest ....................   Passed  310.73 sec
19:   ..... figure 0, skin A to D: 226 of 575 body primitive(s) move, by [3] row(s)
19:   ..... figure 1, skin A to D: 70 of 611 body primitive(s) move, by [3] row(s)
2/5 Test #19: kits_image .......................   Passed   26.93 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
21:   ok    3D TEX_14: Player's head draws the looks tuple's head, and two players apart only in hair colour are drawn apart (reference against Croatia 11 7449 px, Croatia 11 against Croatia 2 617 px, Croatia 11 against Croatia 11 skin D 4238 px below the head)
21:         plant 'Player's head ignored': reference and Croatia 11 draw the same 3D view; Croatia 11 and Croatia 2 draw the same 3D view; Croatia 11 and Croatia 11 skin D draw the same body: the skin stayed on the head
21:   ok    plant 'Player's head ignored' fails the player head judge
21:         plant 'the body's skin not moved': Croatia 11 and Croatia 11 skin D draw the same body: the skin stayed on the head
21:   ok    plant 'the body's skin not moved' fails the player head judge
21: kits_ui: 0 failure(s)
4/5 Test #21: kits_ui ..........................   Passed  240.25 sec
5/5 Test #22: kits_replay ......................   Passed   11.25 sec
The following tests passed:
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 81 of 81 red
```

A planta do `kits_ui` não tem par no `controls.py`: a regra está no `scene_of`, que só roda com o disco, e o sandbox dos controles corre sem ele (mesma razão do §3.2 para o `head --drawn`).
- **Closed** — commit `a0bec3f8` (2026-10-16): feat(kits): the body's skin follows the player's skin colour
  - Files (`git show --name-status a0bec3f8`):
    - `M docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md`
    - `M tools/kits/core/figure.py`
    - `M tools/kits/selftest.py`
    - `M tools/kits/ui_check.py`
- **Reviewed** (2026-10-17) at `212e579c`: CORR-KRP-027, CORR-KRP-028
