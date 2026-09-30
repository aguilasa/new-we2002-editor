---
id: KITS-TASK-27
title: "§4.1 no emulador: suplente em campo e a VRAM lida"
type: "investigação"
phase: 7
depends_on: [KITS-TASK-26]
source_of_truth: "/docs/PLAN-KITS-PY.md#4.1"
files: ["tools/kits/oracle.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["emulador", "save-states"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-27 — §4.1 no emulador: suplente em campo e a VRAM lida

## Goal

A §4.1 respondida pelo jogo: com um time de pares diferentes jogando de suplente, os retângulos enviados à VRAM são o 2º par do TEX (ou não são), lido pelo `oracle.py --kit` do `looks` ou por opção versionada.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Comando versionado sobe o fork, chega à partida e compara retângulo por retângulo; saída colada
- [ ] Controle: o mesmo comando com o time de titular mostra o 1º par
- [ ] A §4.1 do plano tem veredito; se o par não for o 2º, uma CORR é aberta contra a fase 5

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.1). É a fase que não pode ser pulada (§7). Começa de save state, não da rota manual.

## Log de Execução
