---
id: CORR-LOOKS-088
title: "O gate do close-up afrouxa um limiar que a LOOKS-TASK-28 já mediu mais apertado"
origin: LOOKS-TASK-40
severity: medium
files: [tools/looks/confront.py, docs/tasks/looks/40-a-camera-do-close-up.md, docs/PLAN-LOOKS-PY.md, docs/prompts/perfil-looks.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: blocked
depends_on: []
done_on: null
done_commit: null
unblocked_by: python tools/looks/oracle.py --check-live
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
