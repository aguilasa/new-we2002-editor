---
id: CORR-KRP-002
---

# CORR-KRP-002 — Comparação antes/depois do Log depende de work/krp02/run.sh, não versionado

Origin: [KRP-TASK-02](/docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md)

## Problem

O Log da KRP-TASK-02 traz 14 linhas `$ python3 tools/kits/oracle.py …` soltas e, depois, um laço
`diff -q` sobre `work/krp02/before/*.txt` e `work/krp02/after/*.txt`. Quem escreveu esses `.txt` foi
`work/krp02/run.sh`, um script fora do git. Ele exporta o ambiente e redireciona stdout e stderr de
cada comando para o arquivo, com uma linha `exit N` no fim.

O Log não mostra o script nem diz como a árvore "antes" (fffa211a) foi montada. Do jeito que estão
escritas, as linhas `$` não geram `.txt` nenhum, e a comparação não se repete a partir do Log. O
critério pedia "as linhas `$` completas no Log".

A afirmação em si se sustenta: o revisor refez a comparação inteira e deu 14/14 idênticos.

## Evidência

```text
$ ls work/krp02/
after
before
run.sh
$ git ls-files work/krp02 | wc -l
0
$ sed -n '6p' work/krp02/run.sh
o() { name=$1; shift; python3 tools/kits/oracle.py "$@" > "$out/$name.txt" 2>&1; echo "exit $?" >> "$out/$name.txt"; }
$ grep -c 'git archive fffa211a' docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md
0
```

Reprodução do revisor: `git archive fffa211a | tar -x -C <tmp>`, links de `work/` e `roms/` para
dentro dela, os mesmos 14 comandos nas duas árvores — "same" nos 14.

## Root cause

O executor guardou o harness de captura como arquivo descartável em `work/` e colou no Log só os
argumentos dos comandos, sem o corpo do script.

## Fix

Duas saídas:

- acrescentar ao Log de Execução da KRP-TASK-02 um adendo com o corpo inteiro de `run.sh` num
  heredoc e os passos que remontam a árvore "antes" (`git archive fffa211a | tar -x -C <tmp>` e os
  links de `work/` e `roms/`);
- ou versionar o harness como opção do oracle.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md`

## Verificação

```sh
grep -c 'git archive fffa211a' docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md
```

Hoje dá 0. Depois do conserto dá ≥1, e o heredoc com a função `o()` aparece junto.

## Log de Execução

2026-10-12 — reproduzida (`rite reproduce CORR-KRP-002`): `git ls-files work/krp02 | wc -l` dá
`0`, e `grep -c 'git archive fffa211a'` no arquivo da KRP-TASK-02 dá `0`.

Caminho escolhido: o primeiro, sem versionar o harness. Adendo "Adendo (CORR-KRP-002): como a
comparação se refaz" no Log da KRP-TASK-02, antes da linha `Closed`, com o corpo do `run.sh` num
heredoc e os passos que montam as duas árvores (`git archive fffa211a` e `git archive 09203255`,
com `work/` e `roms/` ligados para dentro).

Antes de escrever, refiz a comparação no scratchpad: o `run.sh` reescrito é idêntico ao de
`work/krp02/` (`cmp` sem saída), e as duas árvores rodaram com ele, saindo `same` nos 14. `grep -c
FAIL` dá 4 (`plant-9`), 6 (`plant-9-3`), 49 (`plant-field-9`), 47 (`focus`) e 1 (`panel`), com
`exit 1`; as nove leituras saem `exit 0`, sem `FAIL`. Os passos dessa corrida usavam um laço sobre
`before:fffa211a after:09203255`; no adendo eles aparecem como duas linhas de `git archive`
explícitas, que dão a mesma árvore (o `oracle.py` de `09203255` é igual ao da HEAD, por `cmp`; o
`--stat` entre as duas árvores dá `22 insertions(+), 749 deletions(-)`, o mesmo do Log).
Controle do laço de `diff`: acrescentar um `x` a uma cópia de `out-after/replay-9.txt` dá uma linha
`DIFF`, a de `replay-9.txt`.

Verificação:

```text
$ grep -c 'git archive fffa211a' docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md
1
$ grep -c 'o() {' docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md
1
```

Gates (`rite gates --cycle kits-replay --id CORR-KRP-002`): `ctest --test-dir build -R kits` —
`100% tests passed, 0 tests failed out of 4` (`kits_image` e `kits_ui` *skipped*); `python3
tools/kits/controls.py` — `controls: 56 of 56 red`.
- **Closed** — commit `98853b84` (2026-10-12): docs(kits): the KRP-TASK-02 before/after comparison, runnable from its Log
  - Files (`git show --name-status 98853b84`):
    - `M docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md`
    - `M docs/tasks/kits-replay/CORR-KRP-002.md`
