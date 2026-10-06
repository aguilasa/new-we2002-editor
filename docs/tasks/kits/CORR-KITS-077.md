---
id: CORR-KITS-077
---

# CORR-KITS-077 — Imprimir pelo --attach-matrix a contagem de matrizes distintas

Origin: [KITS-TASK-44](/docs/tasks/kits/44-matriz-gte-model-bin.md)

## Problem

A §4.3 (`docs/PLAN-KITS-PY.md:647`) diz "As 600 matrizes são todas diferentes". Nenhuma ferramenta versionada imprime esse número: o `--attach-matrix` só reporta divisão e dispersão por figura. A afirmação vale — recontada por um script avulso do revisor sobre as paradas guardadas, 600 de 600 pares (rotação, translação) são distintos —, mas só 452 rotações são distintas; as 148 repetições são entre figuras, nunca dentro de uma. Número em documento é colado de ferramenta versionada.

## Evidência

```text
$ grep -n "600 matrizes" docs/PLAN-KITS-PY.md
647:- **Toda peça tem matriz própria.** As 600 matrizes são todas diferentes, e
$ python3 -c "import json;s=json.load(open('<scratch>/matrix-5.json'))['stops'];m=[(tuple(x['rotation']),tuple(x['translation'])) for x in s];print(len(m),len(set(m)),len(set(r for r,t in m)))"
600 600 452
$ python3 tools/kits/oracle.py --attach-matrix 5 --frame-json work/kits-oracle/matrix-5.json | grep -c distinct
0
```

## Root cause

Hipótese: a contagem saiu de uma sonda descartável durante a execução e nunca virou opção nem linha de saída.

## Fix

Em `run_attach_matrix` (`tools/kits/oracle.py`), imprimir "N stop(s), M distinct matrices (R distinct rotations)", e colar essa linha na §4.3 — ou tirar a frase.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`
- `docs/PLAN-KITS-PY.md`

## Verificação

`python3 tools/kits/oracle.py --attach-matrix 5 --frame-json work/kits-oracle/matrix-5.json | grep -c distinct` imprime 0 hoje; pelo menos 1 depois.

## Log de Execução

Reproduzido em 2026-10-06 sobre `e5c54b1`. A ferramenta não imprimia a contagem, e a §4.3 a
afirmava:

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach-matrix 5 --frame-json work/kits-oracle/matrix-5.json | grep -c distinct
0
$ grep -n "600 matrizes" docs/PLAN-KITS-PY.md
647:- **Toda peça tem matriz própria.** As 600 matrizes são todas diferentes, e
```

Conserto: o `run_attach_matrix` imprime `N stop(s), M distinct matrices (R distinct rotations)`.
A §4.3 cola essa linha ao lado da frase.

Só a linha impressa entra no plano. Que as rotações repetidas caem entre figuras e nunca dentro
de uma é contagem da sonda do revisor, sem ferramenta versionada, e por isso ficou fora.

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach-matrix 5 --frame-json work/kits-oracle/matrix-5.json | grep -E "distinct|ok "
  600 stop(s), 600 distinct matrices (452 distinct rotations)
  ok    every worn section has its own matrix, and section 93 is drawn where 97 is
```
