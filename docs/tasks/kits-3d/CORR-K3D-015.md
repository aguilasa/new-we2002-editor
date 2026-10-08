---
id: CORR-K3D-015
---

# CORR-K3D-015 — "No lugar da 15" do G4 é inferido da geometria, não visto desenhado

Origin: [K3D-TASK-08](/docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md)

## Problem

O título do G4, da [K3D-TASK-08](/docs/tasks/kits-3d/08-medir-bracadeira-goleiro.md), diz que a seção 92 é desenhada "no lugar da 15", mas nenhuma
figura do slot 7 desenha a seção 15. Só os vértices em comum (`same_vertices`) e a
posição na ordem sustentam o "no lugar de". Ao contrário do `matrix_judge`, o juiz do
goleiro não exige uma figura sem braçadeira da mesma família com a 15 naquela vaga, então
a troca em si nunca foi vista. O corpo do G4 traz o argumento dos vértices, mas o título
em negrito e `KEEPER_ARMBANDS["replaced"]` soam como observação.

## Evidência

```text
$ grep -n "nenhum goleiro da família 13 desenhando a 15\|inferid" docs/KITS-AJUSTES-3D.md
(nada; exit 1)
```

Pelo revisor, sobre `work/kits-oracle/matrix-7.json` na HEAD: a seção 15 aparece 0 vezes
nas peças, a 92 aparece 27; `armband_zones` dá à 15 só `shoulder, second` e `sleeve,
shoulder to elbow`, e à 92 as zonas de capitão.

## Root cause

Hipótese: o slot 7 só tem o goleiro capitão na família da seção 13, então não há
contraparte sem braçadeira para comparar.

## Fix

No G4 de `docs/KITS-AJUSTES-3D.md`, dizer que o "no lugar da 15" se apoia nos vértices
idênticos mais os texels de capitão, e que nenhum goleiro da família 13 desenhando a 15
foi visto. Opcional: o `--keeper-armband` imprimir as zonas de texel da seção substituída
ao lado das da braçadeira. Se algum dia existir state com goleiro sem braçadeira da
família 13, estender o `keeper_armband_judge` para exigir a ordem simples, como o
`matrix_judge` faz.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md
- tools/kits/oracle.py

## Verificação

```sh
grep -n "nenhum goleiro da família 13 desenhando a 15\|inferid" docs/KITS-AJUSTES-3D.md
```

Hoje vazio; depois tem de casar.

## Log de Execução
