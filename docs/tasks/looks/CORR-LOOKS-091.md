---
id: CORR-LOOKS-091
title: "O bloco de evidência mistura prosa à transcrição do comando"
origin: LOOKS-TASK-40
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-091 — O bloco de evidência mistura prosa à transcrição do comando

Origin: [LOOKS-TASK-40](/docs/tasks/looks/40-a-camera-do-close-up.md)

## Problema identificado

O bloco `### Evidência` apresenta duas transcrições `$ python ...`, e nenhuma
das duas é o que o comando imprime:

- a do `--closeups` tira `NAT`, `BODY` e `AGE` das doze linhas sem reticência,
  e tira a corrida do slot 1 inteira;
- a do `--silhouette-closeups` elide o meio de cada linha com `...` e troca a
  tabela do slot 1 por uma glosa em português — `-- slot 1 (goalkeeper) --  (o
  pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)` — que a
  ferramenta nunca emite.

Todo número da glosa está certo, então nada está errado. O que se perde é o
leitor conseguir separar saída de ferramenta de comentário, num bloco que
existe para ser evidência.

## Evidência

```text
$ sed -n '118,126p' docs/tasks/looks/40-a-camera-do-close-up.md
    FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) ...,  1005 (3.9x)
  -- slot 1 (goalkeeper) --  (o pior caso dos dois slots: SKIN, 402 de 1922, 21%, controle 2,5x)

$ WE2002_LOOKS_IMAGE=... WE2002_LOOKS_DRIVE_IMAGE=... python tools/looks/confront.py --silhouette-closeups
  FACE      walk frame 12; band from row 35:  257 of 2505 ( 10%) with its own camera, 1005 with the full figure's (3.9x)
  -- slot 1 (goalkeeper), 6 row(s) with a camera of their own: BOOTS, FACE, H.COL, H.F.COL., HAIR, SKIN --
  SKIN      walk frame 12; band from row 35:  402 of 1922 ( 21%) with its own camera,  997 with the full figure's (2.5x)
```

## Causa raiz

A transcrição foi encurtada para leitura, e a frase de resumo foi escrita
**dentro** da cerca em vez de ao lado dela.

## Correção

Colar as seis linhas do slot 1 verbatim (são doze ao todo) e tirar a frase do
"pior caso" de dentro da cerca para a prosa acima. É o mesmo princípio da regra
do ciclo sobre transcrição em `CORR-*`: reescrever é falsificar a evidência.

## Arquivos

- docs/tasks/looks/40-a-camera-do-close-up.md

## Verificação

Toda linha dentro das duas cercas aparece verbatim na saída do comando nomeado
no topo do bloco — `diff` entre o trecho do arquivo e a saída filtrada do
`confront.py --silhouette-closeups` sai vazio.

## Log de Execução
