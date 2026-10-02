---
id: CORR-KITS-030
---

# CORR-KITS-030 — Make the 4.6 gap count match the tool's six gaps

Origin: [KITS-TASK-16](/docs/tasks/kits/16-zonas.md)

## Problem

O §4.6 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) diz que o veredito vale "com quatro lacunas declaradas". A ferramenta, e o `GAPS` que ela lê, declaram 6: tronco ×2 e gola ×4.

## Evidência

```text
$ grep -n "quatro lacunas" docs/PLAN-KITS-PY.md
§4.6 vale, com quatro lacunas declaradas.** O mapa é o `ZONES` do
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | grep "^gaps"
gaps: what the game samples and the map leaves without a zone (6)
```

## Root cause

Hipótese: o número saiu de 2 tipos × 2 figuras, não da saída da ferramenta.

## Fix

No §4.6 do plano, escrever "seis lacunas" (dois tipos, nas duas figuras), ou remeter à linha `gaps: (...)` do comando.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Verificação

```text
$ grep -c "quatro lacunas" docs/PLAN-KITS-PY.md
```

Hoje dá 1; depois, 0.

## Log de Execução
