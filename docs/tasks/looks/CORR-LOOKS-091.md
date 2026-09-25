---
id: CORR-LOOKS-091
title: "O bloco de evidência mistura prosa à transcrição do comando"
origin: LOOKS-TASK-40
severity: low
files: [docs/tasks/looks/40-a-camera-do-close-up.md]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
unblocked_by: null
---

# CORR-LOOKS-091 — O bloco de evidência mistura prosa à transcrição do comando

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

O bloco `### Evidência` apresenta duas transcrições `$ python ...`, e nenhuma
das duas é o que o comando imprime:

- a do `--closeups` tira `NAT`, `BODY` e `AGE` das doze linhas sem reticência,
  e tira a corrida do slot 1 inteira;
- a do `--silhouette-closeups` elide o meio de cada linha com `...` e troca a
  tabela do slot 1 por uma glosa em português — `-- slot 1 (goalkeeper) --  (o
  pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)` — que a
  ferramenta nunca emite.

Todo número da glosa está certo, então nada está errado. O que se perde é o
leitor conseguir separar saída de ferramenta de comentário, num bloco que
existe para ser evidência.

## Evidência

```text
$ sed -n '118,126p' docs/tasks/looks/40-a-camera-do-close-up.md
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
  FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
  SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
```

## Causa raiz

A transcrição foi encurtada para leitura, e a frase de resumo foi escrita
**dentro** da cerca em vez de ao lado dela.

## Correção

Colar as seis linhas do slot 1 verbatim (são doze ao todo) e tirar a frase do
"pior caso" de dentro da cerca para a prosa acima. É o mesmo princípio da regra
do ciclo sobre transcrição em `CORR-*`: reescrever é falsificar a evidência.

## Arquivos

- docs/tasks/looks/40-a-camera-do-close-up.md

## Verificação

Toda linha dentro das duas cercas aparece verbatim na saída do comando nomeado
no topo do bloco — `diff` entre o trecho do arquivo e a saída filtrada do
`confront.py --silhouette-closeups` sai vazio.

## Log de Execução

### 2026-09-25 — triagem inline (`/rite:fix-all looks --plan`, Rite 0.8.0)

**REPRODUCED**, decidido inline por `rite reproduce --all --cycle looks --json` na HEAD `de066fd5`.

O `sed` devolve a mesma cerca com a frase do "pior caso" dentro dela: o sintoma. O `confront` não roda aqui pelo mesmo motivo da CORR-LOOKS-088 e não decide.

```text
$ sed -n '118,126p' docs/tasks/looks/40-a-camera-do-close-up.md
  -- slot 2 (outfield player), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
    control: the BOOTS close-up twice, walk frame 0 and 0, 0 pixel(s) apart
    BOOTS     walk frame  0; band from row  3:  160 of 2682 (  6%) with its own camera, 2452 with the full figure's (15.3x)
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
    H.COL     walk frame 12; band from row 35:  299 of 2373 ( 13%) ...,   899 (3.0x)
    H.F.COL.  walk frame 12; band from row 35:  266 of 2516 ( 11%) ...,  1016 (3.8x)
    HAIR      walk frame 12; band from row 35:  286 of 1972 ( 15%) ...,   716 (2.5x)
    SKIN      walk frame 12; band from row 35:  297 of 1897 ( 16%) ...,   915 (3.1x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)
$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
confront FAILED: SLPM-87056_1.sav was recorded on 'C:\\games\\ps1\\work\\we2002-english.cue', and this cycle drives '...'.  The file name cannot tell you this: both releases boot the serial SLPM-87056, so a state made on the Japanese disc carries the same name and brings unreadable menus with it.
[exit 1]
```

### 2026-09-25 — triagem inline (`/rite:fix-all looks CORR-LOOKS-091 CORR-LOOKS-093`, Rite 0.9.3)

**REPRODUCED**, decidido inline por `rite reproduce CORR-LOOKS-091 --cycle looks --json` na HEAD `a3e6809b`: `sed -n '118,126p'` ainda mostra a glosa `-- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)` e as linhas elididas com `...`. O `confront.py` do emulador não rodou (placeholder `...` nas variáveis) e não é preciso para decidir.

### 2026-09-25 — execução (`/rite:fix-all looks CORR-LOOKS-091 CORR-LOOKS-093`, Rite 0.9.3)

**Correção parcial.** A glosa saiu da cerca e as linhas elididas também, mas as
seis linhas do slot 1 **não** foram coladas, porque nenhuma cópia literal delas
existe e a ferramenta não pôde rodar.

- O `confront.py --silhouette-closeups` abre `oracle.Oracle(...)` dentro do
  `check_closeup_cameras`, ou seja, sobe o emulador, e este worker não tinha o
  recurso `duckstation`. O `oracle.py --closeups` idem.
- Não há transcrição completa guardada: `grep -rl "with its own camera" docs`
  acha só a task 40, a CORR-LOOKS-088 e esta CORR, e `git log -S "402 of 1922"`
  só o commit de revisão `7717326c`. A linha `SKIN` do slot 1 aparece ali com
  recuo de 0 e de 2 espaços, e a ferramenta imprime 4 (`"    %-9s walk frame
  ..."`): foi reescrita, não capturada, e não conta como literal. Nada em
  `work/` guarda a saída.

O que mudou em `/docs/tasks/looks/40-a-camera-do-close-up.md`:

- a frase do "pior caso" saiu da cerca e virou prosa acima dela;
- as cinco linhas do slot 2 com `...` saíram da cerca e os números delas
  viraram prosa; na cerca ficaram só as quatro linhas guardadas inteiras
  (cabeça, slot 2, controle, `BOOTS`);
- a linha final `confront --silhouette-closeups: 0 problem(s) over 2 slot(s)`
  saiu da cerca junto com o slot 1, porque abaixo do `BOOTS` do slot 2 ela
  esconderia as linhas que faltam, e virou prosa;
- a prosa acima da cerca do `--closeups` diz agora o que falta nela (`NAT`,
  `BODY`, `AGE` e o slot 1 inteiro).

```text
$ python - (as cercas do bloco `### Evidência`, procurando `...` ou a glosa)
2 fences; lines with elision or gloss: []
$ python tools/looks/selftest.py --quiet | tail -3
  ..... 108 of 108 controls red
controls: 0 failure(s)
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py | tail -1
check: 0 error(s), 13 warning(s) in 4 cycle(s)
```

**Falta**, e só com o emulador: rodar `python tools/looks/confront.py
--silhouette-closeups` (e o `oracle.py --closeups`, para as linhas que faltam
na outra cerca) e colar as doze linhas literais. Só então a Verificação desta
CORR — `diff` vazio contra a saída do comando — se cumpre por inteiro; hoje ela
vale para as linhas que ficaram nas cercas, que aparecem literais no commit
`45734fe1`, e não foi rodada contra uma corrida nova.
- **pending** (2026-09-25): the literal slot-1 lines require confront.py --silhouette-closeups, which starts the emulator; rerun on a machine with duckstation and paste the tool's own output; partial work in 214af796
- **blocked** (2026-09-25): the literal slot-1 lines need the tool's own output; partial work in 214af796 — unblocked by `python tools/looks/oracle.py --check-live`
- **pending** (2026-09-25): python tools/looks/oracle.py --check-live now passes (0 failures) with WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue
