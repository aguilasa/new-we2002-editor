---
id: KITS-TASK-33
---

# KITS-TASK-33 — Aba Diagnóstico: a lista de `kit.problems`

## Goal

A aba lista os problemas da guarda de forma registro a registro; TEX recusado aparece com o motivo, não desenhado torto.

## Arquivos a criar ou modificar

- `tools/kits/ui/*.py`
- `tools/kits/ui_check.py`

## Done criteria

- [ ] Captura com o `TEX_48` e o `TEX_70` da European Deluxe mostrando cada um o seu motivo, e com o `TEX_13` mostrando a nota de leitura além do tamanho ISO
- [ ] Captura com um TEX sadio: lista vazia
- [ ] `kits_ui` estendido, verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4). O plano liga a fase 9 à fase 1; a aba precisa da janela, então depende da 20. Decisão de 2026-09-30.

Da KITS-TASK-07: o `TEX_13` deixou de ser recusado — os "10 registros" eram o tamanho ISO desatualizado, e lido até onde o cabeçalho acaba ele tem os 11 (§2.1). O critério passou a pedir o `TEX_48` e o `TEX_70` (dois motivos de LZSS) e a nota do `TEX_13`; `python tools/kits/cli.py tex roms/golden-european-deluxe.bin` lista os 8 recusados.

## Log de Execução
