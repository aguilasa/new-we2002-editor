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

Reproduzido na HEAD `17b1d791`, antes da edição:

```text
$ grep -nE '^\$ .*(…|\.\.\.|\$f)' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md
94:$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1   (> digest-before.txt / digest-after.txt)
97:$ work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure $f --export-3d work/krp22/after-fig$f.png   (f = 0, 1)
100:$ cmp work/krp22/before-fig$f.png work/krp22/after-fig$f.png && echo SAME-PNG-$f
121:$ ... confront work/kits-replay/tab/replay-9-3-R1.json --tab --player
124:$ ... confront work/kits-replay/tab/replay-10-2-R1.json --tab --player
127:$ ... confront work/kits-replay/tab/replay-9-R1.json --tab --player
```

São seis linhas, as mesmas da Evidência deslocadas uma linha para baixo (93 → 94).

O bloco de digest, PNG e `confront` do Log da KRP-TASK-22 foi reescrito com cada comando inteiro e rodado de novo, agora com saída em `work/krp23/`. O lado antes são as `tools/` de `ca147a8e`, extraídas por `git archive ca147a8e tools | tar -x` num diretório fora do repositório. O lado depois é a HEAD `17b1d791`, não a árvore da task: desde a task o `app.py` ganhou o `fits` do `--list-combos` (CORR-KRP-024) e o status de uma linha (CORR-KRP-025). As linhas de digest estão coladas inteiras.

Os comandos foram rodados por um script de scratchpad. O Log da task transcreve os mesmos comandos, um por linha. O corpo do script:

```sh
#!/bin/bash
# CORR-KRP-023: redo the before/after evidence of KRP-TASK-22, each command whole.
# Before = ca147a8e tools extracted into $B; after = the repo tree at HEAD.
set -x
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
B=/tmp/claude-1000/-home-ingmar-desenvolvimento-github-new-we2002-editor/19ade030-e44d-4060-8aef-84fed13cb062/scratchpad/k23/before
O=work/krp23
rm -rf $B $O; mkdir -p $B $O
git rev-parse HEAD
git archive ca147a8e tools | tar -x -C $B
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $B/tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 > $O/digest-before.txt
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $B/tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --match --set 1 >> $O/digest-before.txt
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 > $O/digest-after.txt
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22 --match --set 1 >> $O/digest-after.txt
cat $O/digest-before.txt
cat $O/digest-after.txt
diff $O/digest-before.txt $O/digest-after.txt && echo SAME-DIGEST
diff work/krp22/digest-after.txt $O/digest-after.txt && echo SAME-AS-TASK22-DIGEST
DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python $B/tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 0 --export-3d $O/before-fig0.png
DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python $B/tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 1 --export-3d $O/before-fig1.png
DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 0 --export-3d $O/after-fig0.png
DISPLAY=:98 XAUTHORITY= work/venv-looks/bin/python tools/kits/ui/app.py roms/japanese-shift-jis.bin --tag 22 --tab 3d --figure 1 --export-3d $O/after-fig1.png
cmp $O/before-fig0.png $O/after-fig0.png && echo SAME-PNG-0
cmp $O/before-fig1.png $O/after-fig1.png && echo SAME-PNG-1
cmp work/krp22/after-fig0.png $O/after-fig0.png && echo SAME-AS-TASK22-PNG-0
cmp work/krp22/after-fig1.png $O/after-fig1.png && echo SAME-AS-TASK22-PNG-1
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $B/tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab --player --out $O/before
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $B/tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab --player --out $O/before
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 $B/tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out $O/before
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-3-R1.json --tab --player --out $O/after
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-10-2-R1.json --tab --player --out $O/after
DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py confront work/kits-replay/tab/replay-9-R1.json --tab --player --out $O/after
```

Antigo contra novo: **nenhum número mudou.**

- Os sete digests são iguais nos dois lados. O `digest-after.txt` refeito é idêntico ao `work/krp22/digest-after.txt` da task (`SAME-AS-TASK22-DIGEST`).
- Os dois PNG de `--export-3d` são iguais entre antes e depois, e iguais aos `work/krp22/after-fig{0,1}.png` da task.
- As doze interseções de `confront` são as que o Log já mostrava: as seis do antes e as seis do depois.
- O que muda na transcrição não é número. O `app.py` imprime a linha de status e `window up`, que o Log original cortava. O `frame` em ms é tempo de relógio: era 213/119 e agora é 107/105/106/109.

Verificação, depois da edição:

```text
$ grep -nE '^\$ .*(…|\.\.\.|\$f)' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md; echo "grep exit $?"
grep exit 1
```
- **Closed** — commit `d13e1b1e` (2026-10-16): docs(kits): KRP-TASK-22 Log spells out the digest, PNG and confront commands
  - Files (`git show --name-status d13e1b1e`):
    - `M docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md`
    - `M docs/tasks/kits-replay/CORR-KRP-023.md`
