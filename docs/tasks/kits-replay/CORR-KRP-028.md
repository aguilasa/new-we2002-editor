---
id: CORR-KRP-028
---

# CORR-KRP-028 — Log da KRP-TASK-24 atribui 108094 px ao Log da 22 e encurta a linha de digest

Origin: [KRP-TASK-24](/docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md)

## Problem

Duas linhas do Log de Execução não se reproduzem a partir da HEAD como estão escritas.

- O Log diz que a comparação antiga referência × Croácia 11 "deu 108094 px no Log da 22". Esse número
  não aparece no Log de nenhuma task, em nenhuma revisão, salvo neste. Ele se reproduz, mas só rodando
  o `kits_ui` de antes da task.
- A linha de evidência de digest está encurtada com "…" e redireciona para arquivos sob `work/`
  (`work/krp24/digest-*.txt`).

## Evidência

```text
$ git log --all --oneline -S108094
a0bec3f8 feat(kits): the body's skin follows the player's skin colour
$ grep -c 108094 docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md
0
$ grep -n "digest-before" docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md
...python3 tools/kits/cli.py figure roms/japanese-shift-jis.bin --tag 22; … --tag 22 --match --set 1   (> digest-before.txt / digest-after.txt)
```

Remontando a árvore de antes da task e rodando o `kits_ui` dela:

```text
$ T=$(mktemp -d); git archive 34763c76 | tar -x -C "$T"; mkdir -p "$T/work"; ln -s "$PWD/work/venv-looks" "$T/work/venv-looks"; (cd "$T" && DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$OLDPWD/roms/japanese-shift-jis.bin python3 tools/kits/ui_check.py) | grep "reference against"
... (reference against Croatia 11 108094 px, Croatia 11 against Croatia 2 617 px)
```

A corrida do revisor extraiu só `tools data src` (`git archive 34763c76 tools data src`). O
`git archive` completo acima é a generalização dela e não foi rodado.

## Root cause

O Log foi escrito de memória de uma corrida local, em vez de colado de uma fonte versionada, e os
comandos de digest foram encurtados.

## Fix

No Log da KRP-TASK-24 (`docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md`):

- trocar "no Log da 22" pelos passos de remontagem da árvore de antes da task, acima;
- escrever a comparação de digest inteira: as duas invocações de `cli.py figure` (sem opção e com
  `--match --set 1`), cada uma contra `git archive 34763c76` e contra a HEAD, e depois o `diff`.

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md`

## Verificação

```sh
grep -n "Log da 22" docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md
```

Não pode imprimir nada, e o bloco de evidência não pode ter mais nenhum "…".

## Log de Execução

### 2026-10-17

Reprodução (`rite reproduce`, HEAD `364cc3a2`): `git log --all --oneline -S108094` só acha o
`a0bec3f8` e a revisão; `grep -c 108094` no arquivo da task 22 dá 0; e a linha de digest do Log da
task 24 é encurtada com `…`, com os redirecionamentos em prosa.

Conserto, no Log da KRP-TASK-24:

- "no Log da 22" virou "no `kits_ui` da árvore de antes desta task (`34763c76`)", com o script de
  remontagem e a linha que ele imprime. Rodado da raiz no `:98`, ele dá `reference against Croatia 11
  108094 px, Croatia 11 against Croatia 2 617 px`, o número do Log;
- a comparação de digest passou a ser um script inteiro (`git archive 34763c76`, as duas invocações
  de `cli.py figure`, a sem opção e a com `--match --set 1`, em cada lado, e o `diff`), com as sete
  linhas de digest coladas. Deu `SAME`, como antes.

Um tropeço no caminho: a primeira corrida do `kits_ui` antigo saiu 77, `skipped -- no display :98`.
O Xvfb do `:98` tinha caído, e foi subido de novo com a receita do `CLAUDE.md` antes da corrida acima.

Verificação:

```text
$ grep -n "Log da 22" docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md
$ sed -n '/^## Log/,$p' docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md | grep -c "…"
0
```

O primeiro não imprime nada (sai 1).
- **Closed** — commit `acb67846` (2026-10-17): docs(kits): KRP-TASK-24 Log rebuilds the 108094 px and spells out the digest run
  - Files (`git show --name-status acb67846`):
    - `M docs/tasks/kits-replay/24-pele-do-corpo-segue-a-da-cabeca.md`
    - `M docs/tasks/kits-replay/CORR-KRP-028.md`
