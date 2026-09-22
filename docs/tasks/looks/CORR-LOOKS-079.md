---
id: CORR-LOOKS-079
title: "A seta esquerda está em x 384 em nove linhas, não oito"
origin: LOOKS-TASK-38
severity: low
files: [docs/tasks/looks/38-o-alinhamento-dos-valores.md, docs/PLAN-LOOKS-PY.md, docs/tasks/looks/36-os-sprites-estaticos.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-079 — A seta esquerda está em x 384 em nove linhas, não oito

Origin: [LOOKS-TASK-38](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)

## Problema identificado

As Notas da LOOKS-TASK-38 e o plano dizem que a `◀` fica em "384 nas outras
**oito**" linhas. Contadas no `screen.json`, são **nove** as linhas que a têm em
384 — o `DEFAUL` incluído, desde que a
[CORR-LOOKS-067](/docs/tasks/looks/CORR-LOOKS-067.md) lhe deu seta de valor.

## Evidência

```text
$ python -c "import json;d=json.load(open('tools/looks/screen.json'));from collections import Counter;\
c=Counter(a['point'][0] for r in d['rows'].values() for v in r['arrows'].values() if v for a in v if a['side']=='left');print(c)"
Counter({384: 9, 424: 1, 416: 1, 302: 1})

$ python -c "import json;print(json.load(open('tools/looks/screen.json'))['rows']['DEFAUL']['arrows']['arrival'])"
[{'point': [384, 43], 'side': 'left'}]
```

## Causa raiz

Herdado da [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md), que
listou as oito linhas pelo nome antes de se saber que o `DEFAUL` tinha setas;
nunca revisto depois da CORR-LOOKS-067. A nota irmã do cursor ("396 nas outras
nove") está certa, e é o que torna a divergência visível.

## Correção

Dizer "nove" nos dois lugares. Sem mudança de código.

## Arquivos

- docs/tasks/looks/38-o-alinhamento-dos-valores.md (linha 58)
- docs/PLAN-LOOKS-PY.md (linha 3177)
- docs/tasks/looks/36-os-sprites-estaticos.md (linha 147, a lista de oito)

## Verificação

O comando `Counter` acima e a prosa concordam em nove.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `edb4dbfa`: **reproduzida**.

```text
$ python -c "... Counter(a['point'][0] ...)"
Counter({384: 20, 424: 3, 416: 2, 302: 2})   # o screen.json de 19bcdf0a guarda uma entrada por chave de valor
# por LINHA distinta: AGE 424, FOOT 416, NAT 302; BODY, BOOTS, DEFAUL, FACE, H.COL, H.F.COL., HAIR, HEIG, SKIN em 384 -> nove
$ python -c "... ['rows']['DEFAUL']['arrows']['arrival']"
[{'point': [384, 43], 'side': 'left'}]
# a prosa ainda diz "oito": 38-...:58, PLAN-LOOKS-PY.md:3177, 36-...:147
```
