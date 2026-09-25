---
id: CORR-LOOKS-088
title: "O gate do close-up afrouxa um limiar que a LOOKS-TASK-28 já mediu mais apertado"
origin: LOOKS-TASK-40
severity: medium
files: [tools/looks/confront.py, docs/tasks/looks/40-a-camera-do-close-up.md, docs/PLAN-LOOKS-PY.md, docs/prompts/perfil-looks.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
unblocked_by: null
---

# CORR-LOOKS-088 — O gate do close-up afrouxa um limiar que a LOOKS-TASK-28 já mediu mais apertado

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

O terceiro critério de conclusão da LOOKS-TASK-40 pede que o close-up caia
"dentro do limiar da [LOOKS-TASK-28](/docs/tasks/looks/28-a-camera-do-jogo.md)",
e o log justifica constantes novas dizendo que as dela "não servem aqui
(`MATCH_SHARE` 0,25 sobre a máscara inteira)". Mas a 28 **também** tem
constantes de close-up por faixa — `CLOSEUP_SHARE` 0,25 e `CLOSEUP_MARGIN`
1,2, as duas calculadas sobre o `HEAD_BAND`, exatamente a faixa que esta task
conta —, e **as doze medições passam nelas** (pior share 21% < 25%; pior
margem 2,5x > 1,2x).

O `CLOSEUP_CAMERA_SHARE` 0,35 é, portanto, mais **frouxo** que o teto já
medido do ciclo para a mesma espécie de contagem, e a razão declarada para
criá-lo não se sustenta.

## Evidência

```text
$ grep -n "^HEAD_BAND = \|^CLOSEUP_MARGIN = \|^CLOSEUP_SHARE = \|^CLOSEUP_CAMERA_SHARE = \|^CLOSEUP_CAMERA_MARGIN = " tools/looks/confront.py
1472:HEAD_BAND = 40
1485:CLOSEUP_MARGIN = 1.2
1502:CLOSEUP_SHARE = 0.25
1694:CLOSEUP_CAMERA_SHARE = 0.35
1703:CLOSEUP_CAMERA_MARGIN = 1.5

$ grep -n "os dela" docs/tasks/looks/40-a-camera-do-close-up.md
90:  LOOKS-TASK-28", e os dela (`MATCH_SHARE` 0,25 sobre a máscara inteira) não

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
confront --silhouette-closeups: 0 problem(s) over 2 slot(s)
# todos os shares de 5 a 21%, todas as margens de 2,5 a 16,9x — dentro do
# CLOSEUP_SHARE 0,25 e do CLOSEUP_MARGIN 1,2 também

# o defeito plantado (cópia de 45734fe1 fora do repo, camera_file ignorando a linha):
FAIL  slot 2, HAIR: our close-up differs in 716 of the 1972 band pixel(s) (36%), over the 35% a matching aim takes
```

O termo de share por si quase não pega o defeito plantado — 36% contra um teto
de 35% —, e quem decide é o `CLOSEUP_CAMERA_MARGIN` (1,0x contra 1,5x).

## Causa raiz

(hipótese) O log leu a constante de máscara inteira da 28 (`MATCH_SHARE`) como
"o limiar da 28" e não notou que o `--silhouette-styles`, citado pelo nome duas
linhas depois, já carrega constantes de faixa com a mesma forma 0,25/1,2.

## Correção

Uma das duas:

- apertar o `CLOSEUP_CAMERA_SHARE` para o 0,25 que o ciclo já mediu para
  contagem sobre a faixa da cabeça — as doze medições passam nele; ou
- manter 0,35 e reescrever o docstring e o parágrafo do log dizendo **por que**
  uma contagem de mira de câmera precisa de mais folga que uma de estilo,
  nomeando `CLOSEUP_SHARE`/`CLOSEUP_MARGIN` e não só o `MATCH_SHARE`.

A mesma frase aparece na §10.3 do plano e na linha do gate no perfil.

## Arquivos

- tools/looks/confront.py (`CLOSEUP_CAMERA_SHARE`, `CLOSEUP_CAMERA_MARGIN`)
- docs/tasks/looks/40-a-camera-do-close-up.md
- docs/PLAN-LOOKS-PY.md
- docs/prompts/perfil-looks.md

## Verificação

Com `CLOSEUP_CAMERA_SHARE = 0.25`, `python tools/looks/confront.py
--silhouette-closeups` segue imprimindo `0 problem(s) over 2 slot(s)`, e o
defeito plantado do `camera_file` continua vermelho nas seis linhas dos dois
slots.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

As duas primeiras saídas são as registradas, byte a byte: as constantes e a frase "os dela" continuam no lugar, e é isso o defeito. A terceira não roda aqui: `WE2002_LOOKS_*=...` é marcador, não caminho, e o `confront` recusa o save state antes de subir o emulador. Não decide nada contra a Evidência — a medição do close-up é suporte, não sintoma.

```text
$ grep -n "^HEAD_BAND = \|^CLOSEUP_MARGIN = \|^CLOSEUP_SHARE = \|^CLOSEUP_CAMERA_SHARE = \|^CLOSEUP_CAMERA_MARGIN = " tools/looks/confront.py
1472:HEAD_BAND = 40
1485:CLOSEUP_MARGIN = 1.2
1502:CLOSEUP_SHARE = 0.25
1694:CLOSEUP_CAMERA_SHARE = 0.35
1703:CLOSEUP_CAMERA_MARGIN = 1.5
$ grep -n "os dela" docs/tasks/looks/40-a-camera-do-close-up.md
90:  LOOKS-TASK-28", e os dela (`MATCH_SHARE` 0,25 sobre a máscara inteira) não
$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
confront FAILED: SLPM-87056_1.sav was recorded on 'C:\\games\\ps1\\work\\we2002-english.cue', and this cycle drives '...'.  The file name cannot tell you this: both releases boot the serial SLPM-87056, so a state made on the Japanese disc carries the same name and brings unreadable menus with it.
[exit 1]
```
- **pending** (2026-09-25): plan-only run claimed it before the D1 fix
- **blocked** (2026-09-25): the Verificação needs confront.py --silhouette-closeups rerun with CLOSEUP_CAMERA_SHARE 0.25, and that command starts the emulator; no work started — unblocked by `python tools/looks/oracle.py --check-live`
- **pending** (2026-09-25): python tools/looks/oracle.py --check-live now passes (0 failures) with WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue

### 2026-09-25 — correção (`/rite:fix looks CORR-LOOKS-088`, emulador disponível)

**Triagem: REPRODUCED** inline na HEAD `4db5928d`: o grep ainda imprime `HEAD_BAND = 40`, `CLOSEUP_MARGIN = 1.2`, `CLOSEUP_SHARE = 0.25`, `CLOSEUP_CAMERA_SHARE = 0.35`, `CLOSEUP_CAMERA_MARGIN = 1.5`, e a frase "os dela" continua na linha 90 da LOOKS-TASK-40.

```text
$ grep -n "^HEAD_BAND = \|^CLOSEUP_MARGIN = \|^CLOSEUP_SHARE = \|^CLOSEUP_CAMERA_SHARE = \|^CLOSEUP_CAMERA_MARGIN = " tools/looks/confront.py
1472:HEAD_BAND = 40
1485:CLOSEUP_MARGIN = 1.2
1502:CLOSEUP_SHARE = 0.25
1694:CLOSEUP_CAMERA_SHARE = 0.35
1703:CLOSEUP_CAMERA_MARGIN = 1.5
$ grep -n "os dela" docs/tasks/looks/40-a-camera-do-close-up.md
90:  LOOKS-TASK-28", e os dela (`MATCH_SHARE` 0,25 sobre a máscara inteira) não
```

**Causa raiz confirmada:** a hipótese vale. As doze medições (abaixo, na HEAD) ficam entre 5% e 21% de share e 2,5x a 16,9x de margem, dentro do `CLOSEUP_SHARE` 0,25 e do `CLOSEUP_MARGIN` 1,2 que a 28 já aplica à mesma contagem sobre o `HEAD_BAND`; o 0,35 não tinha razão medida.

**O que mudou** — a primeira opção da Correção:

- `tools/looks/confront.py`: `CLOSEUP_CAMERA_SHARE = CLOSEUP_SHARE` (0,25), com o docstring dizendo por que é a mesma constante; `CLOSEUP_CAMERA_MARGIN` fica 1,5 (mais apertado que o 1,2), e o docstring diz isso.
- `docs/tasks/looks/40-a-camera-do-close-up.md`: o parágrafo "Os limiares são novos" virou "Os limiares são os da faixa da 28", nomeando `CLOSEUP_SHARE`/`CLOSEUP_MARGIN` e registrando o 0,35 antigo.
- `docs/PLAN-LOOKS-PY.md` §10.3 e `docs/prompts/perfil-looks.md` (linha do gate): os dois limiares nomeados com valor.

Variáveis de todas as corridas: `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue`. Transcrições sem as linhas de navegação (`Down moved`, `shot`, `restored`).

Na HEAD (0,35):

```text
$ python tools/looks/confront.py --silhouette-closeups
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) with its own camera,  899 with the full figure's (3.0x)
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) with its own camera, 1016 with the full figure's (3.8x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  716 with the full figure's (2.5x)
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) with its own camera,  915 with the full figure's (3.1x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  146 of 2699 (  5%) with its own camera, 2471 with the full figure's (16.9x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1002 with the full figure's (3.9x)
    H.COL     walk frame 12; band from row 35:  297 of 2379 ( 12%) with its own camera,  910 with the full figure's (3.1x)
    H.F.COL.  walk frame 12; band from row 35:  256 of 2506 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  703 with the full figure's (2.5x)
    SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
confront --silhouette-closeups: 0 problem(s) over 2 slot(s)
exit 0
```

Com a correção (0,25):

```text
$ grep -n "^CLOSEUP_CAMERA_SHARE = \|^CLOSEUP_CAMERA_MARGIN = " tools/looks/confront.py
1694:CLOSEUP_CAMERA_SHARE = CLOSEUP_SHARE
1708:CLOSEUP_CAMERA_MARGIN = 1.5
$ python tools/looks/confront.py --silhouette-closeups
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) with its own camera,  899 with the full figure's (3.0x)
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) with its own camera, 1016 with the full figure's (3.8x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  716 with the full figure's (2.5x)
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) with its own camera,  915 with the full figure's (3.1x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  146 of 2699 (  5%) with its own camera, 2471 with the full figure's (16.9x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1002 with the full figure's (3.9x)
    H.COL     walk frame 12; band from row 35:  297 of 2379 ( 12%) with its own camera,  910 with the full figure's (3.1x)
    H.F.COL.  walk frame 12; band from row 35:  256 of 2506 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) with its own camera,  703 with the full figure's (2.5x)
    SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
confront --silhouette-closeups: 0 problem(s) over 2 slot(s)
exit 0
```

**Controle plantado**, com a correção: `scene.camera_file` devolvendo sempre o `slotN.json` (a janela que não troca de câmera com a linha), por um wrapper no scratchpad que troca a função antes de importar o `confront` — nada no repositório tocado. Vermelho nas seis linhas dos dois slots, pelos **dois** termos: o share vai de 36% (`HAIR`) a 92% (`BOOTS`), 11 pontos acima de 0,25 no pior caso contra 1 ponto acima do 0,35 antigo, e a margem lê 1,0x em todas.

```text
$ python <scratchpad>/planted.py --silhouette-closeups
PLANTED: scene.camera_file ignores the row; CLOSEUP_CAMERA_SHARE=0.25 CLOSEUP_CAMERA_MARGIN=1.5
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3: 2452 of 2682 ( 91%) with its own camera, 2452 with the full figure's (1.0x)
    FACE      walk frame 12; band from row 35: 1005 of 2505 ( 40%) with its own camera, 1005 with the full figure's (1.0x)
    H.COL     walk frame 12; band from row 35:  899 of 2373 ( 38%) with its own camera,  899 with the full figure's (1.0x)
    H.F.COL.  walk frame 12; band from row 35: 1016 of 2516 ( 40%) with its own camera, 1016 with the full figure's (1.0x)
    HAIR      walk frame 12; band from row 35:  716 of 1972 ( 36%) with its own camera,  716 with the full figure's (1.0x)
    SKIN      walk frame 12; band from row 35:  915 of 1897 ( 48%) with its own camera,  915 with the full figure's (1.0x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3: 2471 of 2699 ( 92%) with its own camera, 2471 with the full figure's (1.0x)
    FACE      walk frame 12; band from row 35: 1002 of 2505 ( 40%) with its own camera, 1002 with the full figure's (1.0x)
    H.COL     walk frame 12; band from row 35:  910 of 2379 ( 38%) with its own camera,  910 with the full figure's (1.0x)
    H.F.COL.  walk frame 12; band from row 35: 1005 of 2506 ( 40%) with its own camera, 1005 with the full figure's (1.0x)
    HAIR      walk frame 12; band from row 35:  703 of 1972 ( 36%) with its own camera,  703 with the full figure's (1.0x)
    SKIN      walk frame 12; band from row 35:  997 of 1922 ( 52%) with its own camera,  997 with the full figure's (1.0x)
  FAIL  slot 2, BOOTS: our close-up differs in 2452 of the 2682 band pixel(s) (91%), over the 25% a matching aim takes
  FAIL  slot 2, BOOTS: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 2, FACE: our close-up differs in 1005 of the 2505 band pixel(s) (40%), over the 25% a matching aim takes
  FAIL  slot 2, FACE: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 2, H.COL: our close-up differs in 899 of the 2373 band pixel(s) (38%), over the 25% a matching aim takes
  FAIL  slot 2, H.COL: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 2, H.F.COL.: our close-up differs in 1016 of the 2516 band pixel(s) (40%), over the 25% a matching aim takes
  FAIL  slot 2, H.F.COL.: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 2, HAIR: our close-up differs in 716 of the 1972 band pixel(s) (36%), over the 25% a matching aim takes
  FAIL  slot 2, HAIR: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 2, SKIN: our close-up differs in 915 of the 1897 band pixel(s) (48%), over the 25% a matching aim takes
  FAIL  slot 2, SKIN: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, BOOTS: our close-up differs in 2471 of the 2699 band pixel(s) (92%), over the 25% a matching aim takes
  FAIL  slot 1, BOOTS: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, FACE: our close-up differs in 1002 of the 2505 band pixel(s) (40%), over the 25% a matching aim takes
  FAIL  slot 1, FACE: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, H.COL: our close-up differs in 910 of the 2379 band pixel(s) (38%), over the 25% a matching aim takes
  FAIL  slot 1, H.COL: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, H.F.COL.: our close-up differs in 1005 of the 2506 band pixel(s) (40%), over the 25% a matching aim takes
  FAIL  slot 1, H.F.COL.: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, HAIR: our close-up differs in 703 of the 1972 band pixel(s) (36%), over the 25% a matching aim takes
  FAIL  slot 1, HAIR: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
  FAIL  slot 1, SKIN: our close-up differs in 997 of the 1922 band pixel(s) (52%), over the 25% a matching aim takes
  FAIL  slot 1, SKIN: the full figure's camera scores 1.0x this row's, under the 1.5x that tells a close-up from a window that did not change camera
confront --silhouette-closeups: 24 problem(s) over 2 slot(s)
exit 1
```

Gates:

```text
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)
$ python tools/looks/confront.py --check
confront.py: 0 failure(s)
$ python tools/check_tasks.py
check: 0 error(s), 13 warning(s) in 4 cycle(s)
$ python tools/pes2/fork.py status
no DuckStation is running
```
