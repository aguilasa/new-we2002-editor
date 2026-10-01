---
id: CORR-KITS-024
---

# CORR-KITS-024 — Keep cross-task notes out of the task's commit or declare them

Origin: [KITS-TASK-10](/docs/tasks/kits/10-confronto-2-superpack.md)

## Problem

O commit c05f012b muda `docs/tasks/kits/28-confronto-3.md`, que não está na lista de arquivos da KITS-TASK-10: acrescenta um parágrafo dizendo à KITS-TASK-28 como estender o `confront.py`. O Log lista o arquivo, então dá para rastrear, mas a mudança fica fora do Escopo da task.

## Evidência

```text
$ git show --stat c05f012b | grep 28-confronto
 docs/tasks/kits/28-confronto-3.md           |   2 +
$ grep -n "28-confronto-3" docs/tasks/kits/10-confronto-2-superpack.md
100:    - `M docs/tasks/kits/28-confronto-3.md`
```

O arquivo só aparece no Log (linha 100), não em "Arquivos a criar ou modificar".

## Root cause

Hipótese: uma consequência de desenho para uma task posterior foi escrita na hora, sem acrescentar o arquivo ao Escopo desta task.

## Fix

Acrescentar `docs/tasks/kits/28-confronto-3.md` ao "Arquivos a criar ou modificar" da KITS-TASK-10, com o motivo (o `confront.py` passou a ser o lugar do `--score`). No resto do ciclo, deixar esse tipo de nota para a task posterior.

## Arquivos a criar ou modificar

- `docs/tasks/kits/10-confronto-2-superpack.md`

## Verificação

```text
$ grep -n "28-confronto-3" docs/tasks/kits/10-confronto-2-superpack.md
```

Hoje só a linha do Log; depois também uma linha na lista do Escopo.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `f66559ad`)

```text
$ git show --stat c05f012b | grep 28-confronto
 docs/tasks/kits/28-confronto-3.md           |   2 +
$ grep -n "28-confronto-3" docs/tasks/kits/10-confronto-2-superpack.md
100:    - `M docs/tasks/kits/28-confronto-3.md`
```

REPRODUCED.

### O que foi feito

`docs/tasks/kits/28-confronto-3.md` entrou no "Arquivos a criar ou modificar" da KITS-TASK-10, com o motivo: a nota diz à KITS-TASK-28 que o `confront.py` já existe e é onde o `--score` entra.

### Verificação

```text
$ grep -n "28-confronto-3" docs/tasks/kits/10-confronto-2-superpack.md | cut -c1-90
18:- `docs/tasks/kits/28-confronto-3.md` — uma nota: o `confront.py` passou a existir aq
119:    - `M docs/tasks/kits/28-confronto-3.md`
```

Duas linhas: a do Escopo e a do Log.
