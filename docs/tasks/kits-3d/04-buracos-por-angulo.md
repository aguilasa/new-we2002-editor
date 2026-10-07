---
id: K3D-TASK-04
---

# K3D-TASK-04 — Ferramenta que conta o que falta na figura por ângulo

## Goal

Uma ferramenta versionada conta, por giro e por figura, os pixels do boneco por onde se vê o fundo (texel transparente, triângulo pulado, ordem de profundidade), e diz de qual peça e zona do TEX cada falta vem.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/cli.py` (ou `tools/kits/oracle.py`): a opção nova
  - `tools/kits/core/` se a contagem pedir apoio no núcleo
  - `tools/kits/selftest.py`, `tools/kits/controls.py`
- Out: consertar o que a contagem achar (é a K3D-TASK-05)

## Done criteria

- [x] o comando imprime uma linha por (figura, yaw) de 0 a 345 em passos de 15, com os pixels vazados e as peças/zonas responsáveis; transcrição inteira no Log
- [x] controle plantado: uma lacuna nova no TEX aumenta a contagem e fica vermelha no `controls.py`
- [x] a contagem de hoje mostra a lacuna do torso (0,80) 20×24 no jogador e (100,104) 20×24 no goleiro com Number desmarcado
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

Causas candidatas em G5: lacuna do torso, RGBA, ordem por profundidade média, triângulo degenerado pulado.

## Log de Execução

**A ferramenta.** `python3 tools/kits/cli.py holes <disco> --tag TAG [--set|--kit] [--figure]
[--step 15] [--top N] [--negative]`, sobre `api.count_holes` (`core/figure.py`). Ela rasteriza em
software a mesma câmera do `ui/figure_view.py` (`rotate()` e `MARGIN`, que o selftest confere
iguais), num quadrado de 320 px (o mínimo da vista), com a mesma ordem de pintura (profundidade
média do triângulo) e a textura amostrada no centro do pixel. Por pixel, o triângulo **mais
próximo** é o que uma figura inteira mostraria, e a falta se conta em três tipos:

- `transparent`: o mais próximo amostra um texel transparente. Pelo buraco se vê o que está atrás
  (o peito por dentro, ou o fundo); `backdrop` é quantos desses mostram o fundo;
- `skipped`: o mais próximo é um triângulo que a vista não mapeia (UV sem área);
- `misordered`: o mais próximo é opaco, mas a vista pinta outro por cima dele.

Primeira versão contava só "fundo visível" e deu **0** na lacuna do torso: pelo buraco das costas
aparece o peito por dentro, não o fundo. Por isso a definição é pelo triângulo mais próximo.

É modelo da pintura da vista, não captura: conta, não compara pixel com screenshot.

**Controle.** `controls.py`: `holes-alpha-ignored` (todo texel opaco) derruba "hole count: a
transparent texel in the uniform raises the count", num caso sintético do `selftest.py` (dois quads,
um bloco transparente no da frente). No disco, `holes --negative` torna a zona `shirt front`
transparente e exige que a contagem suba a partir dela.

```
$ python3 tools/kits/selftest.py --no-plant
  ..... whole: missing 0; holed: transparent 676 (backdrop 0) from [('transparent', 'near section 0')]; flat UV: skipped 2916
  ok    hole count: a transparent texel in the uniform raises the count, from that part
  ok    hole count: its camera is ui/figure_view.py's rotate() and MARGIN
$ python3 tools/kits/controls.py --only holes-alpha-ignored
  RED    holes-alpha-ignored          kits/core/figure.py :: count_holes
$ python3 tools/kits/selftest.py --image
  ok    cli.py holes: from the back the torso gap shows through on both figures, and its --negative sees a planted gap
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 30 of 30 red
```

**Transcrição inteira**, TEX_00, kit 1, Number desmarcado (2026-10-07):

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py holes roms/japanese-shift-jis.bin --tag 00 --negative
figure 0 yaw   0: silhouette 15161, missing 4512 (transparent 3853, backdrop 0; skipped 514; misordered 145)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 3853; skipped /BIN/EDT_MOD.BIN section 5 - 221; skipped /BIN/EDT_MOD.BIN section 2 - 79; skipped /BIN/EDT_MOD.BIN section 0 - 78
figure 0 yaw  15: silhouette 15274, missing 4311 (transparent 3653, backdrop 0; skipped 492; misordered 166)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 3653; skipped /BIN/EDT_MOD.BIN section 5 - 240; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 7 64; skipped /BIN/EDT_MOD.BIN section 2 - 63
figure 0 yaw  30: silhouette 15007, missing 3751 (transparent 3153, backdrop 0; skipped 381; misordered 217)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 3153; skipped /BIN/EDT_MOD.BIN section 5 - 220; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 7 54; skipped /BIN/EDT_MOD.BIN section 3 - 52
figure 0 yaw  45: silhouette 14785, missing 2786 (transparent 2263, backdrop 0; skipped 282; misordered 241)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 2263; skipped /BIN/EDT_MOD.BIN section 5 - 137; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 6 61; skipped /BIN/EDT_MOD.BIN section 3 - 52
figure 0 yaw  60: silhouette 14768, missing 1828 (transparent 1357, backdrop 183; skipped 245; misordered 226)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 1357; skipped /BIN/EDT_MOD.BIN section 5 - 119; skipped /BIN/EDT_MOD.BIN section 8 - 60; misordered /BIN/EDT_MOD.BIN section 0 over /BIN/MODEL.BIN section 24 49
figure 0 yaw  75: silhouette 14617, missing 1105 (transparent 614, backdrop 313; skipped 324; misordered 167)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 614; skipped /BIN/EDT_MOD.BIN section 5 - 174; skipped /BIN/EDT_MOD.BIN section 8 - 63; skipped /BIN/EDT_MOD.BIN section 3 - 40
figure 0 yaw  90: silhouette 14960, missing 744 (transparent 334, backdrop 280; skipped 286; misordered 124)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 334; skipped /BIN/EDT_MOD.BIN section 5 - 129; skipped /BIN/EDT_MOD.BIN section 8 - 60; misordered /BIN/EDT_MOD.BIN section 7 over /BIN/EDT_MOD.BIN section 5 35
figure 0 yaw 105: silhouette 15322, missing 596 (transparent 200, backdrop 185; skipped 232; misordered 164)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 193; skipped /BIN/EDT_MOD.BIN section 5 - 86; skipped /BIN/EDT_MOD.BIN section 8 - 58; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 51
figure 0 yaw 120: silhouette 15518, missing 543 (transparent 70, backdrop 56; skipped 202; misordered 271)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 98; skipped /BIN/EDT_MOD.BIN section 5 - 68; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 56; transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 56
figure 0 yaw 135: silhouette 15306, missing 567 (transparent 26, backdrop 3; skipped 150; misordered 391)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 162; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 61; skipped /BIN/EDT_MOD.BIN section 5 - 53; misordered /BIN/EDT_MOD.BIN section 1 over /BIN/EDT_MOD.BIN section 0 48
figure 0 yaw 150: silhouette 14786, missing 544 (transparent 26, backdrop 0; skipped 108; misordered 410)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 169; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 64; skipped /BIN/EDT_MOD.BIN section 5 - 58; misordered /BIN/EDT_MOD.BIN section 1 over /BIN/EDT_MOD.BIN section 0 45
figure 0 yaw 165: silhouette 14274, missing 442 (transparent 30, backdrop 0; skipped 131; misordered 281)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 106; skipped /BIN/EDT_MOD.BIN section 5 - 59; misordered /BIN/EDT_MOD.BIN section 2 over /BIN/EDT_MOD.BIN section 0 32; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 0 26
figure 0 yaw 180: silhouette 15161, missing 499 (transparent 30, backdrop 0; skipped 144; misordered 325)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 77; skipped /BIN/EDT_MOD.BIN section 5 - 63; misordered /BIN/EDT_MOD.BIN section 2 over /BIN/EDT_MOD.BIN section 0 61; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 6 51
figure 0 yaw 195: silhouette 15274, missing 549 (transparent 28, backdrop 0; skipped 139; misordered 382)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 92; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 6 80; misordered /BIN/EDT_MOD.BIN section 2 over /BIN/EDT_MOD.BIN section 0 72; skipped /BIN/EDT_MOD.BIN section 5 - 57
figure 0 yaw 210: silhouette 15007, missing 620 (transparent 27, backdrop 0; skipped 166; misordered 427)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 111; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 6 75; skipped /BIN/EDT_MOD.BIN section 6 - 58; misordered /BIN/EDT_MOD.BIN section 2 over /BIN/EDT_MOD.BIN section 0 56
figure 0 yaw 225: silhouette 14785, missing 599 (transparent 21, backdrop 0; skipped 187; misordered 391)  misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 125; skipped /BIN/EDT_MOD.BIN section 6 - 75; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 56; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 6 48
figure 0 yaw 240: silhouette 14768, missing 719 (transparent 206, backdrop 183; skipped 190; misordered 323)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 192; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 5 106; skipped /BIN/EDT_MOD.BIN section 6 - 82; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 57
figure 0 yaw 255: silhouette 14617, missing 890 (transparent 551, backdrop 312; skipped 204; misordered 135)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 546; skipped /BIN/EDT_MOD.BIN section 6 - 86; skipped /BIN/EDT_MOD.BIN section 7 - 54; misordered /BIN/EDT_MOD.BIN section 8 over /BIN/EDT_MOD.BIN section 10 49
figure 0 yaw 270: silhouette 14960, missing 1294 (transparent 935, backdrop 303; skipped 214; misordered 145)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 935; skipped /BIN/EDT_MOD.BIN section 6 - 83; skipped /BIN/EDT_MOD.BIN section 7 - 56; skipped /BIN/EDT_MOD.BIN section 4 - 39
figure 0 yaw 285: silhouette 15322, missing 1953 (transparent 1608, backdrop 205; skipped 218; misordered 127)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 1608; skipped /BIN/EDT_MOD.BIN section 6 - 73; skipped /BIN/EDT_MOD.BIN section 7 - 58; misordered /BIN/EDT_MOD.BIN section 7 over /BIN/EDT_MOD.BIN section 9 46
figure 0 yaw 300: silhouette 15518, missing 2648 (transparent 2242, backdrop 73; skipped 254; misordered 152)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 2242; skipped /BIN/EDT_MOD.BIN section 6 - 67; skipped /BIN/EDT_MOD.BIN section 7 - 54; skipped /BIN/EDT_MOD.BIN section 4 - 43
figure 0 yaw 315: silhouette 15306, missing 3365 (transparent 2926, backdrop 5; skipped 286; misordered 153)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 2926; skipped /BIN/EDT_MOD.BIN section 6 - 55; skipped /BIN/EDT_MOD.BIN section 2 - 52; skipped /BIN/EDT_MOD.BIN section 7 - 48
figure 0 yaw 330: silhouette 14786, missing 3964 (transparent 3474, backdrop 0; skipped 363; misordered 127)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 3474; skipped /BIN/EDT_MOD.BIN section 5 - 98; skipped /BIN/EDT_MOD.BIN section 2 - 63; skipped /BIN/EDT_MOD.BIN section 4 - 41
figure 0 yaw 345: silhouette 14274, missing 4310 (transparent 3795, backdrop 0; skipped 391; misordered 124)  transparent /BIN/EDT_MOD.BIN section 0 gap torso, under the map (0,80) 20x24 3795; skipped /BIN/EDT_MOD.BIN section 5 - 165; misordered /BIN/EDT_MOD.BIN section 5 over /BIN/EDT_MOD.BIN section 7 70; skipped /BIN/EDT_MOD.BIN section 2 - 68
negative: figure 0, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
figure 1 yaw   0: silhouette 15254, missing 4447 (transparent 3857, backdrop 1; skipped 410; misordered 180)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 3857; skipped /BIN/EDT_MOD.BIN section 16 - 182; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 18 73; skipped /BIN/EDT_MOD.BIN section 11 - 62
figure 1 yaw  15: silhouette 15217, missing 4285 (transparent 3658, backdrop 1; skipped 423; misordered 204)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 3658; skipped /BIN/EDT_MOD.BIN section 16 - 210; skipped /BIN/EDT_MOD.BIN section 14 - 71; skipped /BIN/EDT_MOD.BIN section 11 - 68
figure 1 yaw  30: silhouette 14911, missing 3773 (transparent 3171, backdrop 2; skipped 341; misordered 261)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 3171; skipped /BIN/EDT_MOD.BIN section 16 - 176; skipped /BIN/EDT_MOD.BIN section 14 - 77; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 18 54
figure 1 yaw  45: silhouette 14773, missing 2862 (transparent 2292, backdrop 4; skipped 268; misordered 302)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 2292; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 17 90; skipped /BIN/EDT_MOD.BIN section 16 - 87; skipped /BIN/EDT_MOD.BIN section 14 - 83
figure 1 yaw  60: silhouette 14887, missing 1940 (transparent 1392, backdrop 186; skipped 313; misordered 235)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 1392; skipped /BIN/EDT_MOD.BIN section 16 - 115; skipped /BIN/EDT_MOD.BIN section 14 - 87; skipped /BIN/EDT_MOD.BIN section 19 - 60
figure 1 yaw  75: silhouette 14821, missing 1245 (transparent 646, backdrop 344; skipped 419; misordered 180)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 646; skipped /BIN/EDT_MOD.BIN section 16 - 155; skipped /BIN/EDT_MOD.BIN section 14 - 94; skipped /BIN/EDT_MOD.BIN section 19 - 63
figure 1 yaw  90: silhouette 15188, missing 902 (transparent 352, backdrop 295; skipped 393; misordered 157)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 352; skipped /BIN/EDT_MOD.BIN section 16 - 120; skipped /BIN/EDT_MOD.BIN section 14 - 89; skipped /BIN/EDT_MOD.BIN section 19 - 60
figure 1 yaw 105: silhouette 15490, missing 746 (transparent 208, backdrop 198; skipped 348; misordered 190)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 206; skipped /BIN/EDT_MOD.BIN section 14 - 87; skipped /BIN/EDT_MOD.BIN section 16 - 86; skipped /BIN/EDT_MOD.BIN section 19 - 58
figure 1 yaw 120: silhouette 15641, missing 673 (transparent 64, backdrop 59; skipped 325; misordered 284)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 89; skipped /BIN/EDT_MOD.BIN section 14 - 81; skipped /BIN/EDT_MOD.BIN section 16 - 70; transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 59
figure 1 yaw 135: silhouette 15385, missing 691 (transparent 14, backdrop 5; skipped 264; misordered 413)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 160; skipped /BIN/EDT_MOD.BIN section 14 - 72; misordered /BIN/EDT_MOD.BIN section 19 over /BIN/EDT_MOD.BIN section 10 61; skipped /BIN/EDT_MOD.BIN section 15 - 56
figure 1 yaw 150: silhouette 14842, missing 648 (transparent 14, backdrop 3; skipped 216; misordered 418)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 175; misordered /BIN/EDT_MOD.BIN section 19 over /BIN/EDT_MOD.BIN section 10 62; skipped /BIN/EDT_MOD.BIN section 14 - 59; skipped /BIN/EDT_MOD.BIN section 15 - 59
figure 1 yaw 165: silhouette 14361, missing 538 (transparent 12, backdrop 1; skipped 237; misordered 289)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 109; skipped /BIN/EDT_MOD.BIN section 16 - 64; skipped /BIN/EDT_MOD.BIN section 14 - 59; skipped /BIN/EDT_MOD.BIN section 15 - 55
figure 1 yaw 180: silhouette 15254, missing 547 (transparent 14, backdrop 1; skipped 244; misordered 289)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 77; skipped /BIN/EDT_MOD.BIN section 16 - 59; skipped /BIN/EDT_MOD.BIN section 14 - 55; skipped /BIN/EDT_MOD.BIN section 15 - 54
figure 1 yaw 195: silhouette 15217, missing 605 (transparent 12, backdrop 1; skipped 203; misordered 390)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 94; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 17 81; skipped /BIN/EDT_MOD.BIN section 15 - 60; skipped /BIN/EDT_MOD.BIN section 16 - 57
figure 1 yaw 210: silhouette 14911, missing 650 (transparent 12, backdrop 2; skipped 227; misordered 411)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 111; skipped /BIN/EDT_MOD.BIN section 15 - 67; skipped /BIN/EDT_MOD.BIN section 17 - 58; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 17 57
figure 1 yaw 225: silhouette 14773, missing 670 (transparent 12, backdrop 4; skipped 251; misordered 407)  misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 131; skipped /BIN/EDT_MOD.BIN section 15 - 84; skipped /BIN/EDT_MOD.BIN section 17 - 75; misordered /BIN/EDT_MOD.BIN section 19 over /BIN/EDT_MOD.BIN section 10 56
figure 1 yaw 240: silhouette 14887, missing 797 (transparent 199, backdrop 185; skipped 255; misordered 343)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 194; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 16 107; skipped /BIN/EDT_MOD.BIN section 15 - 91; skipped /BIN/EDT_MOD.BIN section 17 - 82
figure 1 yaw 255: silhouette 14821, missing 977 (transparent 549, backdrop 343; skipped 282; misordered 146)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 547; skipped /BIN/EDT_MOD.BIN section 15 - 97; skipped /BIN/EDT_MOD.BIN section 17 - 86; skipped /BIN/EDT_MOD.BIN section 18 - 54
figure 1 yaw 270: silhouette 15188, missing 1401 (transparent 935, backdrop 329; skipped 307; misordered 159)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 935; skipped /BIN/EDT_MOD.BIN section 15 - 101; skipped /BIN/EDT_MOD.BIN section 17 - 83; skipped /BIN/EDT_MOD.BIN section 18 - 56
figure 1 yaw 285: silhouette 15490, missing 2066 (transparent 1608, backdrop 221; skipped 301; misordered 157)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 1608; skipped /BIN/EDT_MOD.BIN section 15 - 101; skipped /BIN/EDT_MOD.BIN section 17 - 73; skipped /BIN/EDT_MOD.BIN section 18 - 58
figure 1 yaw 300: silhouette 15641, missing 2736 (transparent 2243, backdrop 81; skipped 306; misordered 187)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 2243; skipped /BIN/EDT_MOD.BIN section 15 - 97; skipped /BIN/EDT_MOD.BIN section 17 - 67; skipped /BIN/EDT_MOD.BIN section 18 - 52
figure 1 yaw 315: silhouette 15385, missing 3434 (transparent 2927, backdrop 6; skipped 301; misordered 206)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 2927; skipped /BIN/EDT_MOD.BIN section 15 - 80; skipped /BIN/EDT_MOD.BIN section 17 - 53; skipped /BIN/EDT_MOD.BIN section 18 - 47
figure 1 yaw 330: silhouette 14842, missing 3971 (transparent 3475, backdrop 3; skipped 333; misordered 163)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 3475; skipped /BIN/EDT_MOD.BIN section 16 - 89; skipped /BIN/EDT_MOD.BIN section 15 - 65; skipped /BIN/EDT_MOD.BIN section 11 - 39
figure 1 yaw 345: silhouette 14361, missing 4340 (transparent 3790, backdrop 1; skipped 364; misordered 186)  transparent /BIN/EDT_MOD.BIN section 11 gap torso, under the map (100,104) 20x24 3790; skipped /BIN/EDT_MOD.BIN section 16 - 141; misordered /BIN/EDT_MOD.BIN section 16 over /BIN/EDT_MOD.BIN section 18 71; skipped /BIN/EDT_MOD.BIN section 11 - 58
negative: figure 1, shirt front made transparent: the count rises from it at 18 of 24 turn(s) -- ok
```

Leitura: de costas (yaw 0) a lacuna do torso responde por 3.853 px no jogador
(`gap torso, under the map (0,80) 20x24`, seção 0) e 3.857 no goleiro (`(100,104) 20x24`,
seção 11). Ao lado dela, de todo ângulo, aparecem triângulos pulados (UV sem área) e ordem
de pintura invertida entre seções vizinhas. O conserto é da K3D-TASK-05.

