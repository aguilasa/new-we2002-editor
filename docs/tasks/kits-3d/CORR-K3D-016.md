---
id: CORR-K3D-016
---

# CORR-K3D-016 — Braçadeira de manga curta sem juiz no desenho

Origin: [K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md)

## Problem

Na [K3D-TASK-10](/docs/tasks/kits-3d/10-duas-figuras.md), com manga curta (o padrão) a braçadeira é a seção 90 do `MODEL.BIN` no lugar do
`upper arm b` do jogador, e nenhum juiz do `kits_ui` olha esse desenho. O `match_judge` só
roda com `--long-sleeves`; o `same_judge` confere só a silhueta; e o `dress_judge` só pede
"> 0 px mudados", o que aqui é sempre verdade: o `raster.py` ajusta a vista aos limites
da cena (`MARGIN`, linhas 83-85), então trocar uma seção de limites diferentes desloca a
figura inteira. A diferença entre sem e com braçadeira é o contorno do corpo todo
(6178 px, da cabeça às chuteiras), não a faixa. Numa cópia que desenha o braço simples
(seção 4) no lugar da 90, a braçadeira some da tela e todo juiz fica verde; o caso
`arm_dress` do selftest também, porque a tabela não muda. O mesmo reenquadramento faz a
figura pular ao marcar a caixa, e deixaria passar de graça o "cada caixa muda a captura
em todo contexto" da K3D-TASK-11.

## Evidência

```text
$ D=$(mktemp -d); git archive HEAD tools | tar -x -C $D
$ python3 - "$D/tools/kits/core/figure.py" <<'PY'
import sys; p=sys.argv[1]; s=open(p).read()
old="        one = sections[number]\n        place = places.get((layout.EDT_MOD, index))"
assert s.count(old)==1
open(p,'w').write(s.replace(old,"        one = sections[4 if number == 90 else number]  # planted\n        place = places.get((layout.EDT_MOD, index))"))
PY
$ cd $D/tools/kits && DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 - <repo> $D <<'PY'
import sys; sys.path.insert(0,'.'); import ui_check as u
R,D=sys.argv[1],sys.argv[2]; env=u.environment(); py=R+'/work/venv-looks/bin/python'; img=R+'/roms/japanese-shift-jis.bin'
print('dress', u.dress_judge(py,img,env,D)); print('same', u.same_judge(py,img,env,D)); print('match', u.match_judge(py,img,env,D))
PY
dress ([], 'Number 1197 px, Captain armband 5957 px, Long sleeves 5270 px')
same ([], 'Captain armband 0.959, Long sleeves 0.962, both 0.962')
match ([], "369 px (1.5 % of the figure) in a 30x19 box, x 0.74-0.97 y 0.26-0.32 of the figure's box")
```

Uma captura da cópia plantada (`app.py ... --figure 0 --yaw 0 --armband`) não mostra a
faixa amarela no braço; na HEAD a mesma captura mostra.

## Root cause

O juiz da braçadeira veio da figura de partida, onde só rodava com manga longa (93 e 97
dividem a caixa de vértices, então não havia reenquadramento). O caso de manga curta
ficou só com o selftest no nível da tabela, e o "> 0 px" do `dress_judge` não distingue
o vestir do reenquadramento da vista (provado pela planta acima).

## Fix

Em `tools/kits/ui_check.py`, fazer o juiz da braçadeira rodar também sem
`--long-sleeves` e afirmar a faixa dentro de `ARM_SIDE`/`ARM_ROWS`, com uma planta como a
de cima vista vermelha. Um caminho é, em `tools/kits/core/raster.py` ou
`tools/kits/ui/figure_view.py`, ajustar a vista aos limites da figura sem vestir, para
marcar uma caixa não reenquadrar; se o reenquadramento ficar, julgar a faixa de manga
curta pela cor ou região própria, não por diferença crua de pixel.

## Arquivos a criar ou modificar

- tools/kits/ui_check.py
- tools/kits/core/raster.py (ou tools/kits/ui/figure_view.py)
- tools/kits/controls.py

## Verificação

Refazer os comandos da cópia plantada acima: ao menos um juiz tem de devolver lista de
falhas não vazia para "Captain armband" com manga curta, e
`ctest --test-dir build -R kits_ui` tem de listar uma planta nova que derruba esse juiz.

## Log de Execução

- 2026-10-09 — triagem: **REPRODUCED**, à mão (a Evidência tem marcadores `<repo>` e escreve
  arquivos). Na cópia do scratchpad com a 90 trocada pela 4, os três juízes ficavam verdes:
  `dress ([], 'Number 1197 px, Captain armband 5957 px, …')`, `same ([], …)`, `match ([], …)`.
- `core/figure.py` + `core/raster.py`: o `dressed_scene` guarda os pontos da figura sem vestir em
  `notes["fit"]`, e o `raster.draw` enquadra por eles. Marcar uma caixa não reenquadra mais: a
  diferença da braçadeira no `dress_judge` caiu de 5957 px para 626.
- `ui_check.py`: o juiz da braçadeira roda nas duas mangas (`ARMBAND_SLEEVES`), com caixa própria
  para a curta (`ARMBAND_BOX_SHORT`: a 90 toma o braço inteiro, 36x63) e uma asserção nova: as cores
  da zona da faixa no work bitmap que a figura sem braçadeira não mostra têm de aparecer em ao menos
  `ARMBAND_INK` px. Planta nova "short-sleeve armband drawn as the plain arm" no `PLANTS`. O
  `controls.py` ficou como estava: a planta mora no catálogo do `kits_ui`, que é onde o juiz roda.
- Verificação:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits -V
21:   ok    3D TEX_14: the player in long and in short sleeves is drawn, and the captain's armband changes only a box on its arm (long sleeves 367 px (1.5 % of the figure) in a 31x19 box, x 0.73-0.97 y 0.26-0.32 of the figure's box, ink 367 px; short sleeves 771 px (3.1 % of the figure) in a 36x63 box, x 0.74-1.00 y 0.17-0.36 of the figure's box, ink 336 px)
21:         plant 'short-sleeve armband drawn as the plain arm': short sleeves: the band's own colours show on 0 px, under 100: the arm changed, the armband is not on it
21:   ok    plant 'short-sleeve armband drawn as the plain arm' fails the armband judge
21: kits_ui: 0 failure(s)
The following tests passed:
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py | tail -1
controls: 36 of 36 red
```
