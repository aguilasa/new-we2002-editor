---
id: LOOKS-TASK-40
title: "A câmera do close-up — o painel aproxima nas seis linhas em que o jogo aproxima"
type: implementação
category: render
phase: 10
depends_on: [LOOKS-TASK-28]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-23
review_commit: e76d2740
done_on: 2026-09-23
done_commit: 45734fe1
---

# LOOKS-TASK-40: A câmera do close-up

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o) e a §10 sobre a câmera.
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário; o
  pedido vinha da [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md).
- **Medido pela [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md):** com o cursor numa linha de cabeça
  (`HAIR`, por exemplo) o jogo aproxima a câmera na cabeça e gira o boneco,
  um ângulo por captura que a carga de câmera do GTE **não** traz — a câmera
  que vale ali se deriva das próprias peças (`oracle.camera_from_pieces`), e
  o `oracle.py --camera SLOT LINHA` a mede.
- **A janela desenha sempre a câmera de corpo inteiro**, medida com o cursor
  em `NAT`.
- **Antes da [`LOOKS-TASK-33`](/docs/tasks/looks/33-a-janela-animada.md)**: as duas mexem na câmera do painel, e a
  janela animada precisa saber qual câmera vale em cada linha.

---

## Objetivo

O painel troca para a câmera do close-up quando o cursor está numa linha de
cabeça, e volta à de corpo inteiro nas outras, como o jogo.

---

## Critério de conclusão

- [x] Quais linhas aproximam, medido no jogo nos dois slots, e a câmera de
      cada uma escrita em `work/looks-camera/`.
- [x] A janela troca de câmera ao mover o cursor, e a troca é por linha, não
      por palpite.
- [x] `confront.py --silhouette` no close-up de cada linha que aproxima, nos
      dois slots, dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md), com o controle do
      jogo contra si mesmo.
- [x] Um controle plantado (a janela que não troca de câmera) fica vermelho.

---

## Log de Execução

**Executado em:** 2026-09-23

### O que foi feito

- **Quais linhas aproximam: seis das doze, e a sexta desmente o título desta
  task.** O `oracle.py --closeups` anda as **doze** linhas no jogo, nos dois
  slots, e lê a câmera em cada uma: `SKIN`, `HAIR`, `H.COL`, `FACE` e
  `H.F.COL.` aproximam na cabeça, com a mesma translação `[-120, 266, 999]`;
  **`BOOTS` aproxima nas chuteiras**, com translação própria
  `[-224, 90, 1934]`; as outras seis ficam com a câmera de corpo inteiro,
  **idêntica número a número** à da linha de carga. O `H` é 1376 nas doze — o
  zoom está na translação, não na projeção. Uma lista feita pelo nome ("linha
  de cabeça") perderia o `BOOTS`.
- **A janela troca por linha, e a troca sai do disco.** `scene.close_up_rows`
  lê quais linhas têm câmera medida em `work/looks-camera/`, e
  `scene.load_camera(slot, escala, linha)` escolhe o arquivo da linha quando
  existe. O `press` da janela reaponta a câmera quando **a linha** muda, não
  só quando a estatura muda, e o relatório passou a dizer com qual câmera o
  painel desenhou.
- **A mira do close-up é medida, não ajustada.** No close-up o eixo é o do
  jogo (`scene.panel_axis`: o meio do display visto de dentro do painel, já
  que os offsets do GTE são zero) e a translação é reassentada na peça de
  referência (`scene.rebased`), porque a nossa cena tem essa peça na origem e
  a câmera do jogo não. No corpo inteiro segue valendo o `ROOT_AT`, que é
  escolha declarada.
- **A cadeia da estatura ganhou a folga do giro** (`scene.CHAIN_TURN_SLACK`,
  128 de 4096): nas cinco linhas de cabeça o modelo gira, e a vista lida onde
  o jogo a constrói é um instante mais velha que a matriz da carga. Sem a
  folga o `HAIR` caía na órbita da v1 — e o relatório dizia "full figure",
  que era mentira; agora diz `refused` com o motivo.
- **O juiz:** `confront.py --silhouette-closeups`, uma foto por linha que
  aproxima, e o `looks_ui` andando o cursor até cada uma delas.
- **Os limiares são os da faixa da 28.** O critério pede "dentro do limiar da
  LOOKS-TASK-28", e o que vale aqui não é o `MATCH_SHARE` dela (0,25 sobre a
  máscara inteira): no close-up a máscara do jogo perde o corpo escuro sobre
  fundo escuro (armadilha 68/`HEAD_BAND`), então a conta é **na faixa** da
  tinta — a mesma conta do `--silhouette-styles`, que a 28 já limita com
  `CLOSEUP_SHARE` 0,25 e `CLOSEUP_MARGIN` 1,2x. `CLOSEUP_CAMERA_SHARE` **é** o
  `CLOSEUP_SHARE` (0,25, pior caso medido 21%), e `CLOSEUP_CAMERA_MARGIN` é
  1,5x, mais apertado que o 1,2x, com o pior controle em 2,5x. Este parágrafo
  dizia até a [CORR-LOOKS-088](/docs/tasks/looks/CORR-LOOKS-088.md) que as
  constantes da 28 "não servem aqui" e fixava o share em 0,35 — mais frouxo
  que o teto já medido do ciclo para a mesma contagem; com o defeito plantado
  (`camera_file` ignorando a linha) o `HAIR` passava 1 ponto acima de 0,35 e
  passa 11 acima de 0,25.

### Evidência

As duas cercas abaixo são a saída inteira de cada comando, colada como ele a
imprimiu em 2026-09-25 na HEAD `b9ce47a9`, com o emulador de pé
(`WE2002_LOOKS_IMAGE` no disco japonês, `WE2002_LOOKS_DRIVE_IMAGE` no `.cue`
inglês), nada cortado: as linhas de navegação (`shot ...`, `slot N restored`,
`Down moved it by ...`) ficam junto com as de resultado. Cada corrida leva
alguns minutos por slot.

O `--closeups` dá, nos dois slots, as mesmas seis linhas que aproximam —
`BOOTS`, `FACE`, `H.COL`, `H.F.COL.`, `HAIR` e `SKIN` — e as mesmas seis que
ficam com a câmera da linha de carga, com a mesma translação por linha no
goleiro e no jogador de linha.

```text
$ python tools/looks/oracle.py --closeups
  fork 17604 on this desktop, log C:\games\ps1\work\duckstation-fork.log
  window 1246232
  duckstation-mcp 1.0.0 answering
  window moved off the visible desktop
  -- slot 2 (outfield player) --
  shot camera-2-0-  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-.png
  slot 2 restored: the outfield player, on LOOKS SET
  shot camera-2-0-  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-.png
  slot 2 restored: the outfield player, on LOOKS SET
    control: the loading row (NAT) read twice, camera identical: translation [-480, 192, 4125], H 1376
  shot camera-2-0-DEFAUL  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-DEFAUL.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  Down moved it by 0.011982
  Down moved it by 0.010089
    DEFAUL    translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-2-0-NAT  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-NAT.png
  slot 2 restored: the outfield player, on LOOKS SET
    NAT       translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-2-0-SKIN  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-SKIN.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
    SKIN      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-2-0-HAIR  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-HAIR.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
    HAIR      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-2-0-H.COL  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-H.COL.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
    H.COL     translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-2-0-FACE  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-FACE.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
    FACE      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-2-0-H.F.COL.  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-H.F.COL..png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
    H.F.COL.  translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-2-0-HEIG  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-HEIG.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
    HEIG      translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-2-0-BODY  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-BODY.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
    BODY      translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-2-0-AGE  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-AGE.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
    AGE       translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-2-0-BOOTS  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-BOOTS.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    BOOTS     translation [-224, 90, 1934]       H 1376  ZOOMS
  shot camera-2-0-FOOT  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-FOOT.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  Down moved it by 0.011982
    FOOT      translation [-480, 192, 4125]      H 1376  the loading row's camera
    6 row(s) zoom (BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN) and 6 keep the loading row's camera (DEFAUL, NAT, HEIG, BODY, AGE, FOOT)
  shot camera-2-0-BOOTS  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\camera-2-0-BOOTS.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    control: BOOTS read twice, camera identical
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-BOOTS.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-FACE.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-H.COL.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-H.F.COL..json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-HAIR.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot2-SKIN.json
  -- slot 1 (goalkeeper) --
  shot camera-1-0-  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  shot camera-1-0-  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-.png
  slot 1 restored: the goalkeeper, on LOOKS SET
    control: the loading row (NAT) read twice, camera identical: translation [-480, 192, 4125], H 1376
  shot camera-1-0-DEFAUL  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-DEFAUL.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  Down moved it by 0.011982
  Down moved it by 0.010089
    DEFAUL    translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-1-0-NAT  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-NAT.png
  slot 1 restored: the goalkeeper, on LOOKS SET
    NAT       translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-1-0-SKIN  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-SKIN.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
    SKIN      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-1-0-HAIR  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-HAIR.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
    HAIR      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-1-0-H.COL  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-H.COL.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
    H.COL     translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-1-0-FACE  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-FACE.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
    FACE      translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-1-0-H.F.COL.  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-H.F.COL..png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
    H.F.COL.  translation [-120, 266, 999]       H 1376  ZOOMS
  shot camera-1-0-HEIG  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-HEIG.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
    HEIG      translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-1-0-BODY  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-BODY.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
    BODY      translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-1-0-AGE  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-AGE.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
    AGE       translation [-480, 192, 4125]      H 1376  the loading row's camera
  shot camera-1-0-BOOTS  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-BOOTS.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    BOOTS     translation [-224, 90, 1934]       H 1376  ZOOMS
  shot camera-1-0-FOOT  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-FOOT.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  Down moved it by 0.011982
    FOOT      translation [-480, 192, 4125]      H 1376  the loading row's camera
    6 row(s) zoom (BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN) and 6 keep the loading row's camera (DEFAUL, NAT, HEIG, BODY, AGE, FOOT)
  shot camera-1-0-BOOTS  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\camera-1-0-BOOTS.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    control: BOOTS read twice, camera identical
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-BOOTS.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-FACE.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-H.COL.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-H.F.COL..json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-HAIR.json
    wrote C:\github\new-we2002-editor\work\looks-camera\slot1-SKIN.json
oracle --closeups: 0 problem(s) over 2 slot(s)
```

No `--silhouette-closeups` o pior caso dos dois slots é o `SKIN` do slot 1,
402 de 1922 pixels da faixa (21%) com a própria câmera contra 997 com a do
corpo inteiro (2,5x), o número que a
[`CORR-LOOKS-088`](/docs/tasks/looks/CORR-LOOKS-088.md) também registra, e
abaixo do `CLOSEUP_CAMERA_SHARE` de 0,25. A corrida termina com `0 problem(s)
over 2 slot(s)`.

```text
$ python tools/looks/confront.py --silhouette-closeups
  the panel is 146x120 native pixels; the camera's axis falls at (240, 54) inside it
  fork 17044 on this desktop, log C:\games\ps1\work\duckstation-fork.log
  window 4262030
  duckstation-mcp 1.0.0 answering
  window moved off the visible desktop
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) with its own camera,  899 with the full figure's (3.0x)
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) with its own camera, 1016 with the full figure's (3.8x)
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  716 with the full figure's (2.5x)
  shot silhouette-2-0  mean=0.183158 sd=0.190350  C:\github\new-we2002-editor\work\looks-shots\silhouette-2-0.png
  slot 2 restored: the outfield player, on LOOKS SET
  Down moved it by 0.030911
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) with its own camera,  915 with the full figure's (3.1x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
  Down moved it by 0.035889
  Down moved it by 0.011406
  Down moved it by 0.008597
  Down moved it by 0.018978
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  146 of 2699 (  5%) with its own camera, 2471 with the full figure's (16.9x)
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1002 with the full figure's (3.9x)
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
    H.COL     walk frame 12; band from row 35:  297 of 2379 ( 12%) with its own camera,  910 with the full figure's (3.1x)
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
  Down moved it by 0.041667
  Down moved it by 0.049728
  Down moved it by 0.054816
    H.F.COL.  walk frame 12; band from row 35:  256 of 2506 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
  Down moved it by 0.041630
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  703 with the full figure's (2.5x)
  shot silhouette-1-0  mean=0.182425 sd=0.189376  C:\github\new-we2002-editor\work\looks-shots\silhouette-1-0.png
  slot 1 restored: the goalkeeper, on LOOKS SET
  Down moved it by 0.030911
    SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
confront --silhouette-closeups: 0 problem(s) over 2 slot(s)
```

**Os controles plantados.** No `looks_ui`, os dois jeitos de a janela parar de
aproximar, cada um vermelho pela razão certa:

```text
the row reaching the camera                RED :: slot 2, cursor on BOOTS: the panel drew with 'full figure' and the measured camera for that row is 'BOOTS'
the cursor moving re-aiming the panel      RED :: slot 2, cursor on BOOTS: the panel drew with 'full figure' and the measured camera for that row is 'BOOTS'
```

E offline, no `controls.py`: `scene-camera-row-ignored` (o arquivo da linha
ignorado) dá `1 of 1 red`.

### Problemas encontrados

- **O título desta task supõe "linha de cabeça", e o jogo aproxima em seis
  linhas.** A `BOOTS` aproxima nas chuteiras, com translação própria. A medição
  ganha da suposição: o critério pedia "quais linhas aproximam, medido", e é o
  que está escrito na §10.3 (o).
- **A primeira comparação ficou vermelha por culpa do juiz, não da câmera.**
  Com o `fit_centre` do `--silhouette`, a nossa figura na câmera de `HAIR`
  marcou 11.995 pixels contra 2.116 da câmera de corpo inteiro: o ajuste centra
  o **corpo inteiro** no painel e mostra a barriga onde o jogo mostra a cabeça.
  O que um close-up erra é a mira, e por isso este confronto não ajusta nada
  (armadilha 97).
- **O `capture_camera` não alcançava a `DEFAUL`.** Ele andava
  `índice(linha) − índice(NAT)` Downs, que é negativo para a única linha acima
  da de carga: zero pressões, a câmera de `NAT` lida e atribuída à `DEFAUL`.
  Agora anda o resto da volta, que é o que o cursor faz.
- **O relatório da janela mentia quando a câmera era recusada.** Dizia
  `full figure` com o painel na órbita da v1; passou a dizer `refused` e a
  imprimir o motivo, e é isso que o `looks_ui` lê.
- **Mexer numa linha que um controle plantado cita quebra o controle.** O
  `press` da janela ganhou a condição da linha, e o `STATURE_BREAKS` citava a
  linha antiga: o `looks_ui` saiu com
  `FAIL: the substitution for the stature reaching the camera matched 0
  time(s), not once` — que é o desenho certo (substituição que não casa é
  controle **quebrado**, não verde). Atualizado o literal, o controle volta a
  ficar vermelho pelo motivo dele.
- **A folga da cadeia foi medida, não escolhida:** 61 a 80 de 4096 nas cinco
  linhas de cabeça, 0 no corpo inteiro e na `BOOTS`, translação exata nos
  catorze arquivos.

### Gates

Todos verdes sobre esta árvore; depois deles só mudou prosa.

```text
$ python tools/looks/selftest.py --quiet
  ..... 105 of 105 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 18 of 18 negative control(s) red, and the window drew every tuple it was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --closeups
oracle --closeups: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-closeups
confront --silhouette-closeups: 0 problem(s) over 2 slot(s)

$ python tools/check_tasks.py
check: 0 error(s), 11 warning(s) in 4 cycle(s)
```
- **Closed** — commit `45734fe1` (2026-09-23): feat(looks): zoom the panel on the six rows the game zooms on
  - Files (`git show --name-status 45734fe1`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/33-a-janela-animada.md`
    - `M docs/tasks/looks/40-a-camera-do-close-up.md`
    - `M tools/looks/confront.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/oracle.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/ui/app.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui_check.py`
- **Reviewed** (2026-09-23) at `e76d2740`: CORR-LOOKS-088, CORR-LOOKS-089, CORR-LOOKS-090, CORR-LOOKS-091
