---
id: CORR-LOOKS-076
title: "O primeiro critério marca um --screen que não foi rodado"
origin: LOOKS-TASK-38
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-076 — O primeiro critério marca um --screen que não foi rodado

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

O primeiro critério de conclusão da LOOKS-TASK-38 termina em "`--screen` remede
com 0 diferença" e está marcado `[x]`, enquanto os "Problemas encontrados" da
própria task dizem que a remedição não foi rodada ("seriam mais 19 min"). O
critério foi marcado com base no `--write` mais o `--keys`, não no check que ele
nomeia.

O revisor rodou o `--screen`: dá **0 diferença**, o que também descarta edição à
mão da tabela gerada. Falta a transcrição no arquivo.

## Evidência

```text
$ sed -n '45,47p;184,187p' docs/tasks/looks/38-o-alinhamento-dos-valores.md
- [x] O gerador grava a caixa (x, largura) e o modo de alinhamento de cada
      objeto de texto; `screen.py --check` confere, e `--screen` remede com 0 diferença.
- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado** (seriam mais 19 min).

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/oracle.py --screen
  screen measured in 1197s
oracle --screen: 0 difference(s) from screen.json
```

## Causa raiz

O custo da corrida (~20 min) foi trocado pela marcação. O critério está de fato
satisfeito.

## Correção

Colar a transcrição do `--screen` no bloco de Evidência e tirar o terceiro
marcador de "Problemas encontrados". Sem mudança de código.

## Arquivos

- docs/tasks/looks/38-o-alinhamento-dos-valores.md

## Verificação

`python tools/looks/oracle.py --screen` imprime `0 difference(s) from
screen.json`, e a linha aparece na Evidência da task.

## Log de Execução
