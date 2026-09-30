---
id: KITS-TASK-07
title: Ler o TEX com guarda de forma e a cauda marcada Form 2 no leiaute Form 1
type: "implementação"
phase: 1
depends_on: [KITS-TASK-06]
source_of_truth: "/docs/PLAN-KITS-PY.md#2.1"
files: ["tools/kits/core/tex.py", "tools/kits/core/source.py", "tools/kits/core/api.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-07 — Ler o TEX com guarda de forma e a cauda marcada Form 2 no leiaute Form 1

## Goal

`tex.py` lê um TEX, nomeia as 6 imagens e as 5 paletas e preenche `kit.problems` registro a registro; a cauda marcada Form 2 com dado no leiaute Form 1 é lida como Form 1 e o diagnóstico diz que leu assim.

## Arquivos a criar ou modificar

- `tools/kits/core/tex.py`
- `tools/kits/core/source.py`
- `tools/kits/core/api.py`

## Done criteria

- [ ] Os 105 TEX do disco japonês abrem com `problems` vazio (número da ferramenta no Log)
- [ ] Na `golden-european-deluxe.bin`: dos 18 com cauda Form 2, 16 abrem com a nota de leitura Form 1; `TEX_13` é recusado por ter 10 registros; `TEX_48` é recusado pelo LZSS da primeira imagem (distance 0 no byte 4.810) — saída colada
- [ ] Controle: um byte trocado no fluxo LZSS de um TEX sadio é recusado com a frase do registro (§5, controle 4)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2.1).

Da KITS-TASK-01: os 11 retângulos do TEX (`EXPECTED_SHAPE`) estão em `tools/kits/core/survey.py`; pelo §3.1 endereço mora no `layout.py` do `looks` — mover para lá (ou justificar) quando o `tex.py` os usar, e o `survey.py` passar a importar de um lugar só.

Da KITS-TASK-06: o `core/source.py` reconhece TEX por `survey._shape_of` e `survey.EXPECTED_SHAPE` — quando os retângulos saírem do `survey.py`, o `source.py` passa a usar a função pública do módulo novo. E `survey.SurveyError` deriva de `Exception`; trazê-la para baixo de `errors.KitsError` junto, para `except KitsError` pegar tudo o que o núcleo levanta.

## Log de Execução
