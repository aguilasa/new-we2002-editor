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
