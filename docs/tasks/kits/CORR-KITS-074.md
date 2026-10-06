---
id: CORR-KITS-074
---

# CORR-KITS-074 — Colar no Log a saída inteira do --attach, não elidida

Origin: [KITS-TASK-43](/docs/tasks/kits/43-medir-encaixe-mangas.md)

## Problem

O critério 1 pede o `--attach 5` colado no Log com as duas contagens. O Log mostra 2 das 24 linhas de ajuste por seção e troca o resto por "...". A segunda contagem não pode ser conferida pelo Log.

## Evidência

```text
$ grep -c "point(s): alone" docs/tasks/kits/43-medir-encaixe-mangas.md
2
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --attach 5 --frame-json work/kits-oracle/attach-5.json | grep -c "point(s): alone"
24
$ grep -n "^    \.\.\.$" docs/tasks/kits/43-medir-encaixe-mangas.md
68:    ...
```

## Root cause

A transcrição foi encurtada por tamanho.

## Fix

No Log de `docs/tasks/kits/43-medir-encaixe-mangas.md`, colar a saída inteira. Ela reproduz byte a byte a partir de `work/kits-oracle/attach-5.json`, e uma corrida ao vivo do revisor deu quadro idêntico.

## Arquivos a criar ou modificar

- `docs/tasks/kits/43-medir-encaixe-mangas.md`

## Verificação

`test "$(grep -c 'point(s): alone' docs/tasks/kits/43-medir-encaixe-mangas.md)" -eq 24` falha hoje (2); passa depois.

## Log de Execução
