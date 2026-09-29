---
id: CORR-LOOKS-107
title: "O close-up não gira o modelo, e no jogo ele gira"
origin: LOOKS-TASK-35
severity: medium
files: [tools/looks/layout.py, tools/looks/scene.py, tools/looks/oracle.py, tools/looks/ui/looks_set.py, tools/looks/ui/app.py, tools/looks/ui_check.py, docs/PLAN-LOOKS-PY.md, CLAUDE.md]  # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-29
done_commit: ac4d250
---

# CORR-LOOKS-107 — O close-up não gira o modelo, e no jogo ele gira

Origin: [LOOKS-TASK-35](/docs/tasks/looks/35-fechamento-da-v2.md)

## Problem

Nas cinco linhas de cabeça (SKIN, HAIR, H.COL, FACE, H.F.COL.) o jogo gira o
modelo no close-up, e a janela o mostra parado num ângulo só. Era aberto
conhecido da §10.3 (p) do [plano](/docs/PLAN-LOOKS-PY.md), e o usuário pediu o
conserto em 2026-09-29.

## Evidência

A câmera derivada das peças (`oracle.camera_from_pieces`), passada a passada,
com HAIR segurado: uma onda triangular de 1,40625° por passada entre −56,25° e
+39,375°.

```text
13005:-23.9 13007:-25.3 13010:-26.72 ... 13057:-56.26 13060:-54.84 ... 13148:0.0 ... 13212:39.37 13214:37.97 ...
```

O ângulo mora em RAM, em `0x80075CD6`, e é o mesmo que o `--camera` guarda
como ângulo y da *chain* (128 nos arquivos de corpo inteiro e de `BOOTS`, o
valor do momento nos cinco de cabeça). Lido quadro a quadro:

```text
slot2 load 128 | NAT+100 128 | SKIN 4032 | SKIN+100 3584 | back NAT 128 | NAT+100 128 | SKIN again 336 | HEIG 128 | BOOTS 128
slot 2 down: first [128, 112, 96, 80, 64, 48]  min -640 max 448  steps [-16, 0, 16]  changes 168
slot 1 down: first [128, 112, 96, 80, 64, 48]  min -640 max 448  steps [-16, 0, 16]  changes 168
```

## Root cause

A v2 fechou sem a curva do giro: o que se tinha eram ângulos de paradas
soltas, e girar sem a curva seria inventar velocidade e sentido. Faltava achar
de onde o jogo tira o ângulo.

## Fix

- `layout.TURN_ANGLE` e as constantes medidas: repouso `TURN_REST` (128), passo
  `TURN_STEP` (16 de 4096 por passada), `TURN_BOUNDS` (−640, +448) e
  `TURN_FIRST_DIRECTION` (−1 depois do `load_state`).
- `scene.turn_after(passes, direction)`: a forma fechada da onda, que devolve
  também o sentido depois da última passada.
- `WalkClock`: o giro começa no `hold()`, quando o cursor entra numa linha
  segurada (são as mesmas cinco), e termina no `release()`, que guarda o
  sentido. As passadas são contadas num relógio próprio (`free_frames`), porque
  a trava da linha segurada para a pose e não pode parar o giro; pausar congela
  o giro, e `.` o anda uma passada.
- `load_camera` e `panel_camera` recebem o ângulo e recompõem a câmera pela
  *chain* com o ângulo y trocado. A janela re-mira a cada passada que muda o
  giro, sem remontar a figura. Captura parada continua com o ângulo do próprio
  arquivo.
- `oracle.py --turn`: lê o ângulo quadro a quadro e confere o modelo nas duas
  figuras. Controles: a mesma entrada duas vezes, o repouso em NAT, uma passada
  de deslocamento como caso negativo, e a reentrada depois do rebote, que só
  passa se o sentido for mesmo guardado.

## Arquivos a criar ou modificar

- [tools/looks/layout.py](/tools/looks/layout.py)
- [tools/looks/scene.py](/tools/looks/scene.py)
- [tools/looks/oracle.py](/tools/looks/oracle.py)
- [tools/looks/ui/looks_set.py](/tools/looks/ui/looks_set.py)
- [tools/looks/ui/app.py](/tools/looks/ui/app.py)
- [tools/looks/ui_check.py](/tools/looks/ui_check.py)
- [docs/PLAN-LOOKS-PY.md](/docs/PLAN-LOOKS-PY.md)
- [CLAUDE.md](/CLAUDE.md)

## Verificação

```text
$ python3 tools/looks/oracle.py --turn
    control: the entry read twice from load_state, 380 frame(s), identical
    control: on NAT it rests at 128
    168 value(s) in 380 frame(s), from -640 to 448
    every value is scene.turn_after's, both ends reached once each; one pass along it is not
    left and entered again: rest 128, then [128, 144, 160, 176] -- the way it was going when it left (+1)
  (e o mesmo no outro slot)
oracle --turn: 0 problem(s) over 2 slot(s)
$ python3 tools/looks/selftest.py | tail -1
looks_selftest: 0 failure(s)
$ python3 tools/looks/ui_check.py | tail -1
looks_ui: 21 of 21 negative control(s) red, ...
```

Nos limites, a câmera recomposta tem o yaw do jogo: −56,25° e +39,375° nas
cinco linhas das duas figuras. Com o ângulo do próprio arquivo, ela fica a 61–80
de 4096 da câmera carregada, que é a folga `CHAIN_TURN_SLACK` já medida (o jogo
carrega a câmera uma passada depois de montá-la).

A janela animada chega a −80, −368 e −352 em 0,5 s, 1,2 s e 2,5 s. O jogo,
capturado nos mesmos ângulos e no mesmo sentido, mostra a mesma cabeça girada:
`work/looks-corr107/turngrid.png`, fora do git.

## Log de Execução

- 2026-09-29 — medida a curva pela câmera das peças; achado o ângulo em RAM;
  medido repouso, passo, pontas e reentrada; implementado; `--turn`, selftest,
  `ui_check` e a comparação de tela verdes.
- **Closed** — commit `ac4d250` (2026-09-29): feat(looks): turn the model in the close-up as the game does
  - Files (`git show --name-status ac4d250`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `A docs/tasks/looks/CORR-LOOKS-107.md`
    - `M docs/tasks/looks/correcoes-progresso.md`
    - `M tools/looks/layout.py`
    - `M tools/looks/oracle.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/ui/app.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui_check.py`
