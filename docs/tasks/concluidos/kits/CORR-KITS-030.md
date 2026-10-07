---
id: CORR-KITS-030
---

# CORR-KITS-030 — Make the 4.6 gap count match the tool's six gaps

Origin: [KITS-TASK-16](/docs/tasks/concluidos/kits/16-zonas.md)

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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `eaeb6838`)

```text
$ grep -n "quatro lacunas" docs/PLAN-KITS-PY.md
495:§4.6 vale, com quatro lacunas declaradas.** O mapa é o `ZONES` do
$ python tools/kits/cli.py zones roms/japanese-shift-jis.bin | grep "^gaps"
gaps: what the game samples and the map leaves without a zone (6)
```

REPRODUCED.

### O que foi feito

§4.6 do plano: "seis lacunas declaradas", com o que são (tronco nas duas figuras; gola nas duas, em dois retângulos cada — a fresta entre os ombros e o vão entre as pontas) e a remissão à linha `gaps: (...)` do `cli.py zones`. Varredura: nenhum outro documento do ciclo dizia "quatro lacunas".

### Verificação

```text
$ grep -c "quatro lacunas" docs/PLAN-KITS-PY.md
0
```
- **Closed** — commit `6779dafd` (2026-10-02): docs(kits): six declared gaps in plan 4.6, as cli.py zones counts them
  - Files (`git show --name-status 6779dafd`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/CORR-KITS-030.md`
