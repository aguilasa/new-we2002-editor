---
id: CORR-DMCP-016
---

# CORR-DMCP-016 — Escrever as conferências de equivalência pré-mudança como passos refeitos do git

Origin: [DMCP-TASK-14](/docs/tasks/duckmcp/14-savestate.md)

## Problem

As linhas `$` do Log para "mesma saída que a HEAD anterior" não se refazem como estão escritas: fazem
`cmp` contra `sav_info_before_1.txt`, que não existe em repositório nenhum; o caso vermelho aponta para
uma `<cópia>` sem nome, com o patch só em prosa; a igualdade do `diff` de 8715 runs e a do `scan`
contra a versão numpy não têm comando nenhum. Todos os números reproduziram quando a versão antiga foi
refeita a partir do `74cfe939` — o achado é sobre como a evidência está escrita, não sobre os valores.

## Evidência

```text
$ S=$(mktemp -d); git archive 74cfe939 tools | tar -x -C "$S"; python3 "$S"/tools/pes2/savestate.py diff work/looks-states/SLPM-87056_1.sav work/looks-states/SLPM-87056_2.sav > "$S"/olddiff.txt; python3 tools/duckmcp/savestate.py diff work/looks-states/SLPM-87056_1.sav work/looks-states/SLPM-87056_2.sav > "$S"/newdiff.txt; cmp "$S"/olddiff.txt "$S"/newdiff.txt && echo diffsame; head -1 "$S"/newdiff.txt
diffsame
8715 run(s), 25769 byte(s) differ (1.23% of RAM)
$ grep -n 'sav_info_before\|<cópia>' docs/tasks/duckmcp/14-savestate.md
(as linhas $ do Log nomeiam sav_info_before_N.txt e <cópia>; nenhum arquivo versionado nem passo de reconstrução os produz)
```

## Root cause

Hipótese: as saídas de referência foram capturadas da árvore antes da edição, e só os resultados foram
colados no Log, não os comandos que as refazem do git.

## Fix

Acrescentar ao Log da `docs/tasks/duckmcp/14-savestate.md` uma entrada com o passo
`git archive 74cfe939 tools | tar -x -C <tmp>` e as comparações de `info`, `diff`, `scan` e `shot`
contra `<tmp>/tools/pes2/savestate.py`; escrever o patch do caso vermelho como as linhas `sed` exatas
rodadas numa cópia `git archive HEAD`.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/14-savestate.md`

## Verificação

`grep -n 'sav_info_before\|<cópia>' docs/tasks/duckmcp/14-savestate.md` não acha mais linha `$` que
dependa deles, e toda linha `$` nova roda a partir de um clone limpo mais `work/looks-states/` e dá a
saída colada.

## Log de Execução
