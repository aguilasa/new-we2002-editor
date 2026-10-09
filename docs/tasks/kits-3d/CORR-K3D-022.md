---
id: CORR-K3D-022
---

# CORR-K3D-022 — Negativa do Cross no G7 sem comando que a meça

Origin: [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md)

## Problem

O item 5 do G7 e a linha do Log da [K3D-TASK-16](/docs/tasks/kits-3d/16-medir-tela-edit-pl-num.md) "o Cross sai da tela" afirmam como negativa que o
Cross não confirma: a tela volta à lista do time e a carga de matriz para. O critério de
pronto exige toda negativa "com comando e saída". O código da HEAD só aperta Cross se o
Circle falhar, e o Circle sempre gira a figura, então nenhum comando na HEAD produz essa
saída. As capturas guardadas não registram botão ignorado, e a corrida ao vivo refeita
pelo revisor também não. A afirmação vem de uma primeira corrida avulsa que a HEAD não
reconstrói.

## Evidência

```text
$ python3 -c "import json;k=json.load(open('work/kits-oracle/edit-8-0.json'));print(k['button'],k.get('ignored'))"
Circle None
$ python3 tools/kits/oracle.py --edit-number 8 --button Cross 2>&1 | tail -1
oracle.py: error: unrecognized arguments: --button Cross
```

Na corrida ao vivo do revisor na HEAD (`--edit-number 8`, no `:98`), a saída só traz
"Circle turned the figure: …", sem menção ao Cross.

## Root cause

`EDIT_BUTTONS` foi reordenado para Circle primeiro depois da medição, e a observação do
Cross ficou só na prosa.

## Fix

Acrescentar a `tools/kits/oracle.py` uma opção — por exemplo
`--edit-number 8 --button Cross` — que aperte só aquele botão e diga o que acontece: a
troca de tela e a carga de matriz parando depois de N paradas. Colar a saída no item 5 do
G7 em `docs/KITS-AJUSTES-3D.md`. Senão, marcar a frase do Cross no G7 como avulsa e não
medida na HEAD.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md

## Verificação

`python3 tools/kits/oracle.py --edit-number 8 --button Cross` (com o mesmo ambiente do
emulador) imprime que o Cross não girou a figura e que a carga parou. Hoje a opção não
existe (erro do argparse).

## Log de Execução
