---
id: KITS-TASK-16
title: "`zones.py` com proveniência, e a §4.6 fechada contra a geometria"
type: "verificação"
phase: 3
depends_on: [KITS-TASK-15, KITS-TASK-04]
source_of_truth: "/docs/PLAN-KITS-PY.md#4.6"
files: ["tools/kits/core/zones.py", "tools/kits/core/api.py", "tools/kits/controls.py", "docs/PLAN-KITS-PY.md", "NOTICE.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-16 — `zones.py` com proveniência, e a §4.6 fechada contra a geometria

## Goal

O mapa de zonas como dados, cada linha com o autor da medição (polipoli ou ramonpsx, transcritos no SUPERPACK-UNIFORMES §1.3/§2), `api.zone_at(x, y)`, e a conferência mecânica da §4.6: toda UV amostrada cai numa zona, e a zona que nenhuma primitiva amostra está listada com o motivo.

## Arquivos a criar ou modificar

- `tools/kits/core/zones.py`
- `tools/kits/core/api.py`
- `tools/kits/controls.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] O confronto imprime quantas primitivas caem em zona e quantas fora; o número que fica fora é 0 ou cada uma está listada
- [ ] Controle: o mapa deslocado 1 px reprova (§5, controle 4) — vermelho no Log
- [ ] A §4.6 do plano tem veredito e a lista das zonas sem primitiva
- [ ] A seção do `kits` no `NOTICE.md` credita, no mesmo commit, os autores do mapa e das medidas usados — polipoli (`Zonas kits y tex - polipoli/`) e ramonpsx (`Medidas TEX we2002.txt`) —, e cada linha do `zones.py` diz de qual dos dois veio. O Superpack não é citado

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.6).

## Log de Execução
