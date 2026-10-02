---
id: CORR-KITS-038
---

# CORR-KITS-038 — Trocar a linha narrativa "$ (a mesma troca...)" do Log por um comando

Origin: [KITS-TASK-21](/docs/tasks/kits/21-looks-builder-kit.md)

## Problem

O Log da KITS-TASK-21 mostra evidência sob `$ (a mesma troca numa cópia da árvore, e o self-check do scene nela)`. A linha é descrição, não comando: as duas linhas `FAIL` abaixo dela não se reproduzem a partir da HEAD como estão escritas. O revisor só as reproduziu escrevendo a própria planta com `sed`.

## Evidência

```text
$ grep -n 'a mesma troca' docs/tasks/kits/21-looks-builder-kit.md
67:$ (a mesma troca numa cópia da árvore, e o self-check do scene nela)
$ S=$(mktemp -d); git archive HEAD | tar -x -C $S; cd $S; sed -i 's/frame: int = None, kit: str = layout.KIT_ON_SCREEN):/frame: int = None, kit: str = "00"):/' tools/looks/scene.py; python3 tools/looks/scene.py --check | grep -E 'FAIL|failure'
  FAIL  with no kit named, the Builder wears TEX_A4, the screen's kit  '00'
  FAIL  and builds with the tag it was given  ['00', '00']
scene.py: 2 failure(s)
```

## Root cause

O passo da cópia de rascunho foi resumido em vez de transcrito.

## Fix

Em `docs/tasks/kits/21-looks-builder-kit.md`, trocar a linha entre parênteses pelos passos `git archive` + `sed` + `scene.py --check` acima, ou citar só `controls.py --only scene-builder-default-kit`, que é versionado.

## Arquivos a criar ou modificar

- `docs/tasks/kits/21-looks-builder-kit.md`

## Verificação

```sh
grep -n 'a mesma troca' docs/tasks/kits/21-looks-builder-kit.md
```

Imprime a linha 67 hoje; vazio depois do conserto.

## Log de Execução
