---
id: LOOKS-TASK-40
title: "A câmera do close-up — o painel aproxima na cabeça quando a linha é de cabeça"
type: implementação
category: render
phase: 10
depends_on: [LOOKS-TASK-28]
status: in-progress
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: null
review_commit: null
done_on: null
done_commit: null
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
- **Os limiares são novos, e por quê.** O critério pedia "dentro do limiar da
  LOOKS-TASK-28", e os dela (`MATCH_SHARE` 0,25 sobre a máscara inteira) não
  servem aqui: no close-up a máscara do jogo perde o corpo escuro sobre fundo
  escuro (armadilha 68/`HEAD_BAND`), então a conta é **na faixa** da tinta,
  como no `--silhouette-styles`. `CLOSEUP_CAMERA_SHARE` é 0,35 com o pior caso
  medido em 21%, e `CLOSEUP_CAMERA_MARGIN` 1,5x com o pior controle em 2,5x —
  medidos nas doze comparações e escritos com folga acima do pior, que é a
  regra da 28.

### Evidência

```text
$ python tools/looks/oracle.py --closeups          # os dois slots, ~3 min cada
    control: the loading row (NAT) read twice, camera identical: translation [-480, 192, 4125], H 1376
    DEFAUL    translation [-480, 192, 4125]      H 1376  the loading row's camera
    SKIN      translation [-120, 266, 999]       H 1376  ZOOMS
    HAIR      translation [-120, 266, 999]       H 1376  ZOOMS
    H.COL     translation [-120, 266, 999]       H 1376  ZOOMS
    FACE      translation [-120, 266, 999]       H 1376  ZOOMS
    H.F.COL.  translation [-120, 266, 999]       H 1376  ZOOMS
    HEIG      translation [-480, 192, 4125]      H 1376  the loading row's camera
    BOOTS     translation [-224, 90, 1934]       H 1376  ZOOMS
    FOOT      translation [-480, 192, 4125]      H 1376  the loading row's camera
    6 row(s) zoom (BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN) and 6 keep the loading row's camera (DEFAUL, NAT, HEIG, BODY, AGE, FOOT)
    control: BOOTS read twice, camera identical
oracle --closeups: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-closeups
  the panel is 146x120 native pixels; the camera's axis falls at (240, 54) inside it
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) ...,   899 (3.0x)
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) ...,  1016 (3.8x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) ...,   716 (2.5x)
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) ...,   915 (3.1x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)
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
