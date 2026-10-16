---
id: CORR-KRP-023
---

# CORR-KRP-023 — Linhas $ do Log da KRP-TASK-22 encurtadas e o lado antes (ca147a8e) não mostrado

Origin: [KRP-TASK-22](/docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

## Problem

A evidência de digest, PNG e `confront` do Log está escrita com linhas `$` encurtadas ou em prosa:
`…`, `(> digest-before.txt / digest-after.txt)`, a variável de laço `$f` com "(f = 0, 1)" e
`$ ... confront`.

Os comandos do lado antes, em ca147a8e (como saíram o `digest-before.txt` e os `before-fig*.png`),
não aparecem. As linhas de digest também não estão coladas, só o `SAME-DIGEST`.

Os resultados se reproduzem: o revisor remontou os dois lados, e a saída de digest dele é igual a
`work/krp22/digest-after.txt`. Mas o Log não diz a quem lê como chegar lá. É a armadilha "Linha `$`
diferente do que rodou".

## Evidência

```text
$ grep -nE '^\$ .*(…|\.\.\.|\$f)' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md
93:$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1   (> digest-before.txt / digest-after.txt)
96:$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure $f --export-3d work/krp22/after-fig$f.png   (f = 0, 1)
99:$ cmp work/krp22/before-fig$f.png work/krp22/after-fig$f.png && echo SAME-PNG-$f
120:$ ... confront work/kits-replay/tab/replay-9-3-R1.json --tab --player
123:$ ... confront work/kits-replay/tab/replay-10-2-R1.json --tab --player
126:$ ... confront work/kits-replay/tab/replay-9-R1.json --tab --player
```

## Root cause

Os comandos foram condensados à mão ao escrever o Log.

## Fix

No Log da task, escrever cada comando inteiro:

- `git archive ca147a8e | tar -x -C <tmp>` para o lado antes;
- as duas invocações de `cli.py figure`, com os redirecionamentos;
- uma linha `--export-3d` por figura;
- a linha completa do `confront`, com ambiente e `--out`.

Colar as linhas de digest, não só o `SAME-DIGEST`.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md`

## Verificação

```sh
grep -nE '^\$ .*(…|\.\.\.|\$f)' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md
```

Hoje imprime 6 linhas. Depois do conserto não pode imprimir nada.

## Log de Execução
