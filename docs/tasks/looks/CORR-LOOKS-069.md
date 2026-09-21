---
id: CORR-LOOKS-069
title: "Dizer quantos sprites estáticos foram amostrados, não 14"
origin: LOOKS-TASK-36
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-069 — Dizer quantos sprites estáticos foram amostrados, não 14

Origin: [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md)

## Problema identificado

O `oracle.py --scenery --write` imprime "359 pixel(s) of 14 sprite(s)", e o
Log da task cita a frase. Só 13 sprites trazem amostra: a barra é inteira
transparente (armadilha 91) e não tem nenhuma. O número é o de sprites
estáticos achados, não o de amostrados.

## Evidência

Revisão da LOOKS-TASK-36 em 2026-09-21, contando os sprites com `samples` em
`work/looks-scenery/slot{1,2}.json`:

```text
$ python -c (conta sprites com "samples" em work/looks-scenery/slot{1,2}.json)
1 142 sprites; 13 with samples; 359 samples
2 142 sprites; 13 with samples; 359 samples
Counter: plate 4, shirt boxes 4, title 4, bar 1, icon 1  (= 14 static)
```

## Causa raiz

(hipótese) A mensagem em `tools/looks/oracle.py:2188` divide pelo número de
sprites estáticos, e não pelo dos que deram ao menos uma amostra.

## Correção

`tools/looks/oracle.py`, perto da linha 2188: imprimir os sprites que têm
amostra e nomear os que não têm (a barra).

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`

## Verificação

`python tools/looks/oracle.py --scenery --write` deve dizer "of 13 sprite(s)"
e nomear a barra como não amostrada, batendo com a recontagem acima.

## Log de Execução
