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
