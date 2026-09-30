---
id: KITS-TASK-13
title: "`teams.py` e `cli.py teams`: nome da ROM ou tabela inglesa, decidido pelo disco"
type: "implementação"
phase: 2
depends_on: [KITS-TASK-12]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.3"
files: ["tools/kits/core/teams.py", "tools/kits/core/source.py", "tools/kits/core/api.py", "tools/kits/cli.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-13 — `teams.py` e `cli.py teams`: nome da ROM ou tabela inglesa, decidido pelo disco

## Goal

`source.teams()` devolve `TeamEntry(index, name, name_origin, tag)`; o disco japonês (boot `SLPM_870.56`) dá nomes da tabela, os outros dão o nome da ROM, disco desconhecido cai no nome da ROM com `name_origin` dizendo isso.

## Arquivos a criar ou modificar

- `tools/kits/core/teams.py`
- `tools/kits/core/source.py`
- `tools/kits/core/api.py`
- `tools/kits/cli.py`

## Done criteria

- [ ] `cli.py teams roms/japanese-shift-jis.bin` sai com `name_origin` `table` em todas as linhas; primeiras linhas coladas
- [ ] `cli.py teams roms/golden-european-deluxe.bin` sai com `rom`, e os nomes batem com os que o `we2002_core` lê (comando de conferência e contagem no Log)
- [ ] Nenhum nome vazio na japonesa (contagem da ferramenta)
- [ ] `tag` é `None` em toda linha enquanto a §4.2 não fechar

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.3).

## Log de Execução
