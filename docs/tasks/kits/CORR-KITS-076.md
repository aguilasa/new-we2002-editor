---
id: CORR-KITS-076
---

# CORR-KITS-076 — Dar vermelho plantado à verificação de matriz compartilhada

Origin: [KITS-TASK-44](/docs/tasks/kits/44-matriz-gte-model-bin.md)

## Problem

A resposta inteira da KITS-TASK-44 é "própria": nenhuma seção vestida divide a matriz com outra peça da figura. Só a lista `same` de `matrix_report` decide isso. O selftest nunca monta uma figura em que uma seção vestida divida matriz, e nenhuma das duas plantas (`lag`, `slot`) passa por esse caminho. Trocando a comparação por `if False` — de modo que nunca ache divisão —, o selftest continua verde e a repetição das paradas ainda imprime "ok every worn section has its own matrix". O critério 2 (vermelho para captura deslocada ou seção trocada) foi cumprido, mas o veredito que a task existe para entregar nunca foi visto vermelho.

## Evidência

```text
$ S=<scratch>; git archive HEAD | tar -x -C $S/tree; cd $S/tree
$ sed -i 's/if q is not p and q\["matrix"\] == p\["matrix"\]\]/if False]/' tools/kits/oracle.py
1142:                        if False]
$ python3 tools/kits/selftest.py; echo $?
142:  ok    oracle --attach-matrix: every worn section has its own matrix, and 93 is where 97 is
kits_selftest: 0 failure(s)
planted exit 0
$ WE2002_LOOKS_IMAGE=<repo>/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach-matrix 5 --frame-json $S/matrix-5.json | tail -1
  ok    every worn section has its own matrix, and section 93 is drawn where 97 is
```

## Root cause

Hipótese: os controles foram escolhidos pelo texto do critério de pronto (atraso, seção trocada), não pela asserção que carrega o resultado.

## Fix

Em `tools/kits/selftest.py`, uma verificação que dá a uma seção vestida (por exemplo a 97) a mesma rotação e translação da seção 7 da mesma figura e exige que `oracle.matrix_judge` reporte "shares its matrix". Opcional: um terceiro `--plant-matrix share` em `tools/kits/oracle.py` que copia uma matriz do corpo para a 97 nas paradas guardadas e tem de sair 1.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/oracle.py`

## Verificação

Com a planta `if False` acima aplicada, `python3 tools/kits/selftest.py` tem de sair diferente de zero. Hoje sai 0.

## Log de Execução

Reproduzido em 2026-10-06 sobre `3b5c603`, numa cópia `git archive HEAD tools docs src data
CMakeLists.txt` no scratchpad, com a comparação do `matrix_report` trocada por `if False]`:

```text
$ python3 $S/tools/kits/selftest.py --no-plant | grep -E "own matrix|FAIL|kits_selftest:"
  ok    oracle --attach-matrix: every worn section has its own matrix, and 93 is where 97 is
kits_selftest: 0 failure(s)
```

Conserto:

- `tools/kits/selftest.py`: um caso que dá à seção 97 da segunda figura a matriz da seção 7 da
  mesma figura e exige que o `matrix_judge` diga `section 97 shares its matrix with [7]`.
- `tools/kits/controls.py`: o controle `oracle-matrix-share-blind`, que planta exatamente o
  `if False]` da Evidência.
- O `--plant-matrix share` opcional ficou de fora: o controle versionado já cobre o caminho.

```text
$ python3 tools/kits/selftest.py | grep -E "shares it|kits_selftest:"
  ok    oracle --attach-matrix: a long sleeve given section 7's matrix shares it
kits_selftest: 0 failure(s)
$ python3 tools/kits/controls.py --only oracle-matrix-share-blind
  RED    oracle-matrix-share-blind    kits/oracle.py :: matrix_report
controls: 1 of 1 red
$ python3 $S/tools/kits/selftest.py --no-plant      (cópia da árvore consertada, com o if False plantado)
  FAIL  oracle --attach-matrix: a long sleeve given section 7's matrix shares it
kits_selftest: 1 failure(s)
```
- **Closed** — commit `a190f34` (2026-10-06): test(kits): see the shared-matrix verdict red
  - Files (`git show --name-status a190f34`):
    - `M docs/tasks/kits/CORR-KITS-076.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/selftest.py`
