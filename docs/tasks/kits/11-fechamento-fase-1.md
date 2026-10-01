---
id: KITS-TASK-11
---

# KITS-TASK-11 — Fechamento da fase 1 — núcleo, lado TEX

## Goal

A fase 1 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R kits` na HEAD, saída colada com os nomes dos alvos
- [ ] `python tools/kits/controls.py` na HEAD, todos vermelhos
- [ ] Confrontos 1 e 2 refeitos, números colados
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

Da KITS-TASK-09: o confronto 1 roda dentro do `kits_image` (`cli.py export --confront` e o `--negative`, ~31 s cada). Continua aberta, sem dono, a discordância da KITS-TASK-02 entre `texture.tables` (do `looks`) e `bin_archive.entries` sobre `/BIN/DATSEL2.BIN` — não é TEX, e o confronto 1 não a toca.

## Log de Execução
