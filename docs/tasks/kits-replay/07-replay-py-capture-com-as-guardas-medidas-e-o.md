---
id: KRP-TASK-07
---

# KRP-TASK-07 — replay.py capture com as guardas medidas, e o oracle capturando por ela

## Goal

`replay.py capture --slot S [--focus K] [--turn R1|L1] [--walk L2|R2] [--out DIR]` faz a captura que hoje mora no `oracle.py` (`replay_capture`, `replay_arrive`, `replay_field_capture` sobre `pose_capture`), grava no schema v1 e aplica as guardas do [§2.5](/docs/PLAN-KITS-REPLAY.md#2.5); o `oracle.py` passa a capturar por ela.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/replay.py`
  - `tools/kits/oracle.py`
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - andar o replay com Right/Left
  - ponteiro do par do `ANIME.BIN` (KRP-TASK-14)

## Done criteria

- [x] `replay.py capture --slot 9 --focus 3` grava uma captura v1 cuja leitura por `replay.py figure --json` dá os mesmos campos da linha `ok` do [relatório](/docs/KITS-REPLAYS-9-10.md#como-foi-medido) para o foco 3 do slot 9
- [x] `replay.py capture --slot 9 --focus 3 --turn R1` e `--slot 10 --focus 3|2 --turn R1` gravam a frente dos focos de linha, para a KRP-TASK-06
- [x] com um joystick plantado em `fork.JOYSTICK_DIR`, `capture` recusa antes de subir o emulador (planta no `controls.py`)
- [x] a saída imprime, por sequência, os quadros corridos e o timeout de 390, e nenhuma passa dele
- [x] (não se aplicou: as duas cópias mestras existem — `test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav` sai 0) sem uma das cópias mestras: `rite mark KRP-TASK-07 blocked --unblocked-by "test -f work/kits-states/SLPM-87056_9.sav -a -f work/kits-states/SLPM-87056_10.sav"` e o pedido ao usuário
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Custo de relógio: 10 a 40 minutos por corrida. `frame_step` a ~57 ms. O seguido atrás de um jogador é a figura no eixo com margem (CORR-K3D-024).

## Log de Execução

### 2026-10-14

As três funções de captura — `replay_arrive`, `replay_capture` e `replay_field_capture` — saíram
do `oracle.py` para `tools/kits/replay.py`, chamando as primitivas do oracle (`pose_capture`,
`matrix_stops`, `load_slot`, `_edit_kit`, `_edit_page`…) pelo módulo carregado por caminho, com o
oracle registrado como `kits_oracle` quando é ele quem roda. O `oracle.py --replay`/`--replay-field`
captura por elas (`_kits_replay()`). `replay_capture` aceita `rotate=None`: só a primeira captura,
`turned` `"not asked"`. O subcomando novo `capture --slot S [--focus K] [--turn R1|L1] [--walk
L2|R2] [--out DIR] [--cue CUE]` chama `fork.refuse_joysticks()` **antes** de ler o disco ou subir o
fork, grava em `work/kits-replay/` (não em `work/kits-oracle/`, cujas capturas o `kits_replay`
prende ao digest) no schema v1 (`schema`, `kind`, `slot`, `focus`, `button`, `taps`), e imprime
cada sequência com os quadros e o timeout, saindo 1 se uma julgada chega a ele.

O giro não é julgado contra os 390: `turn_frames` conta da recarga ao fim da captura girada,
atravessando os ~15 toques de R1, e cada toque recomeça o ocioso do replay. A primeira versão o
julgava e acusou `FAIL  turn: 610 frame(s), not under the timeout 390` na 9-3-R1 e `581` na
10-3-R1 — falso vermelho, porque o juiz do oracle (`replay_judge`) sempre olhou só
`front_frames` e `back_frames`. Corrigido (`sequences` marca o que é julgado) e as duas refeitas;
os dois arquivos saíram com o **mesmo sha256** nas duas corridas.

Corridas, todas com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin
WE2002_LOOKS_DRIVE_IMAGE=$PWD/work/looks-disc/we2002-english.cue DISPLAY=:98 XAUTHORITY=`:

```
$ python3 tools/kits/replay.py capture --slot 9 --focus 3 --out work/kits-replay
  front     65 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-9-3.json (schema v1, sha256 ac1d591a2cde7bcdcd7e36b48a29f5f36f4a6516afee1aa427de2ae8d51adf4e)
(11:31:56 a 11:32:12)
$ python3 tools/kits/replay.py capture --slot 9 --focus 3 --turn R1 --out work/kits-replay
  front     65 frame(s) from its last tap to the end of its capture; timeout 390
  turn      610 frame(s) from the reload, across its taps (each starts the idle again): not judged
  back      44 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-9-3-R1.json (schema v1, sha256 81f278d156d9f3ce58d1e4209eb4c1f7c1335b7cacd817a83a08ed8929e52cdd)
(11:45:09 a 11:49:03)
$ python3 tools/kits/replay.py capture --slot 10 --focus 3 --turn R1 --out work/kits-replay
  front     64 frame(s) from its last tap to the end of its capture; timeout 390
  turn      581 frame(s) from the reload, across its taps (each starts the idle again): not judged
  back      45 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-10-3-R1.json (schema v1, sha256 b9dd37e385e912168c9973b65f319c470297f4a5a1d60f0895b21f80261f6ac5)
(11:49:03 a 11:53:56)
$ python3 tools/kits/replay.py capture --slot 10 --focus 2 --turn R1 --out work/kits-replay
  front     65 frame(s) from its last tap to the end of its capture; timeout 390
  turn      601 frame(s) from the reload, across its taps (each starts the idle again): not judged
  back      35 frame(s) from its last tap to the end of its capture; timeout 390
  capture kept at work/kits-replay/replay-10-2-R1.json (schema v1, sha256 8c14251394bc337a2db9f0301bc102b4a59040ab786682da76637c507f930cf0)
(11:41:57 a 11:45:01)
```

As quatro saem 0; nenhuma sequência julgada passa de 65 quadros. Custo de relógio bem abaixo dos
10 a 40 minutos previstos: 16 s sem giro, 3 a 5 min com giro.

A captura sem giro, lida:

```
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-replay/replay-9-3.json --json
(capture.kind slot focus button taps | schema, figure, still, panel)
close 9 3 L2 3 | kits-replay/1 root 2 head 46 armband 90 replaces 4 still 0 panel [640, 60, 104] number 11 turned not asked
```

É a linha `ok` do relatório para o foco 3 do slot 9: `opens at section 2 with head 46, draws 90
in place of 4, holds still, and its back shows panel (640, 60, 104) with number 11`.

As três giradas, lidas por `core.replay.Capture.load` (lado `back`, a frente do jogador):
`replay-9-3-R1: schema 1, slot 9 focus 3, turned back, rotate R1, figure root 2 head 46 armband 90`;
`replay-10-3-R1: … root 2 head 46 armband 93`; `replay-10-2-R1: … root 2 head 46 armband None`.
São a entrada da KRP-TASK-06.

O oracle, agora capturando pela `replay.py`, dá a mesma saída sobre as capturas guardadas: o
`run.sh` da [KRP-TASK-02](/docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md)
na HEAD de trabalho, comparado com `work/krp02/before/`: `14 same`.

Plantas (cópia do `tools/`, `selftest.py --no-plant`, sai 1):

```
$ python3 tools/kits/controls.py --only replay-capture-joystick-late
  RED    replay-capture-joystick-late kits/replay.py :: run_capture
  FAIL  replay.py capture refuses a plugged-in controller before it reads or boots anything  KeyError: 'WE2002_LOOKS_IMAGE'
$ python3 tools/kits/controls.py --only replay-capture-timeout-unasked
  RED    replay-capture-timeout-unasked kits/replay.py :: timeout_failures
  FAIL  replay.py capture: a sequence that reaches the replay's timeout fails  []
```

O caso da guarda põe um `js0` em `fork.joysticks` e faz `looks_oracle.model_maps` e `fork.launch`
levantarem: sem o `refuse_joysticks` no começo, a captura avança e cai lendo o disco.

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/5 Test #18: kits_selftest ....................   Passed  274.65 sec
2/5 Test #19: kits_image .......................   Passed   27.20 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  207.88 sec
5/5 Test #22: kits_replay ......................   Passed    7.63 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 67 of 67 red
```
- **Closed** — commit `9bc2d8ee` (2026-10-14): feat(kits): replay.py capture, and the oracle capturing through it
  - Files (`git show --name-status 9bc2d8ee`):
    - `M docs/tasks/kits-replay/07-replay-py-capture-com-as-guardas-medidas-e-o.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/replay.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/replay.py`, `tools/kits/oracle.py`, `tools/kits/core/replay.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`
