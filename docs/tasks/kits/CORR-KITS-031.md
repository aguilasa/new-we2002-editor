---
id: CORR-KITS-031
---

# CORR-KITS-031 — Plant controls for the three other 4.6 failure branches

Origin: [KITS-TASK-16](/docs/tasks/kits/16-zonas.md)

## Problem

O `Confrontation.ok` reprova em quatro condições: `outside`, `unsampled_unexplained`, `sampled_but_excused` e `gaps_unused`. Só a primeira (`--negative`) e a sobreposição de zonas (`zones-front-moved`) têm vermelho plantado versionado. As outras três são asserções novas sem vermelho no Log nem no `controls.py`, embora as Notas da task afirmem que "lacuna que ninguém amostra também reprova". O revisor plantou cada uma numa cópia e todas ficaram vermelhas — a lógica funciona hoje —, mas nenhum gate a protege.

## Evidência

```text
$ grep -n "zones" tools/kits/controls.py
151:        "zones-front-moved", "kits/core/zones.py", "ZONES",
154:        "FAIL  zones.self_check() reports no failure",
156:        "overlap its neighbour (section 5, control 4 on the disc is `cli.py zones "
```

Sondas do revisor, sem versão (cópia `git archive HEAD tools`, um `sed` por cópia nova de `tools/kits/core/zones.py`, e depois `python tools/kits/cli.py zones roms/japanese-shift-jis.bin`):

```text
sed 's/_z("numbers 0-9", SHARED, 64, 68, 60, 12, WHY_NUMBERS)/_z("numbers 0-9", SHARED, 64, 68, 60, 12)/'
  -> "1 zone(s): NO REASON GIVEN" / "verdict: section 4.6 FAILS", exit 1
sed 's/_z("socks", PLAYER, 0, 48, 32, 18)/_z("socks", PLAYER, 0, 48, 32, 18, WHY_NUMBERS)/'
  -> "EXCUSED BUT SAMPLED  figure 0  (0,48) 32x18  socks", exit 1
sed 's/^GAPS = (/GAPS = (\n    Gap("planted", PLAYER, 0, 120, 2, 2, "x"),/'
  -> "GAP NOBODY SAMPLES  figure 0  (0,120) 2x2  planted", exit 1
```

## Root cause

Hipótese: os controles plantados cobriram só o controle 4 do §5, e os outros ramos do veredito do confronto foram tomados como cobertos por ele.

## Fix

Acrescentar três entradas a `tools/kits/controls.py` (ou casos puros no bloco do `kits_selftest` que monta um `UvReport` sintético, perto da linha 285), uma por ramo, usando os três plantios acima.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`
- `tools/kits/selftest.py`

## Verificação

```text
$ python tools/kits/controls.py | tail -1
```

Hoje dá "13 of 13"; depois tem de listar os três controles novos vermelhos.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `eaeb6838`)

```text
$ grep -n "zones" tools/kits/controls.py
151:        "zones-front-moved", "kits/core/zones.py", "ZONES",
154:        "FAIL  zones.self_check() reports no failure",
156:        "overlap its neighbour (section 5, control 4 on the disc is `cli.py zones "
```

REPRODUCED: só o `zones-front-moved`; nenhum controle nem check toca `unsampled_unexplained`, `sampled_but_excused` ou `gaps_unused`.

### O que foi feito

- `tools/kits/selftest.py`: casos puros no bloco do mapa, sobre um mapa de três zonas e uma lacuna montados ali — uma zona sem amostra e sem motivo, uma com motivo e amostrada, uma lacuna que ninguém amostra —, cada um exigindo que o seu ramo do `Confrontation` a nomeie, e o veredito `ok` falso. Rodam no `kits_selftest`, sem disco.
- `tools/kits/controls.py`: três controles, um por ramo, que trocam o corpo da propriedade por `return ()` e exigem a linha FAIL do caso correspondente. Plantam a lógica, não os dados do `ZONES`/`GAPS` — os plantios de dados da revisão só ficam vermelhos com o disco, e o `controls.py` roda o `kits_selftest`, sem disco.

### Verificação

```text
$ env -u WE2002_LOOKS_IMAGE python tools/kits/selftest.py --no-plant | grep -E "section 4.6|verdict says|kits_selftest"
  ok    a zone nobody samples, with no reason, fails section 4.6
  ok    a zone excused from sampling, and sampled, fails section 4.6
  ok    a declared gap nobody samples fails section 4.6
  ok    and the verdict says so
kits_selftest: 0 failure(s)
$ python tools/kits/controls.py | tail -4
  RED    zones-quiet-unexplained      kits/core/zones.py :: Confrontation.unsampled_unexplained
  RED    zones-excused-sampled        kits/core/zones.py :: Confrontation.sampled_but_excused
  RED    zones-gap-unused             kits/core/zones.py :: Confrontation.gaps_unused
controls: 16 of 16 red
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | tail -1
verdict: section 4.6 holds
```
