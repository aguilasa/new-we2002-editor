---
id: CORR-LOOKS-067
title: "Correção: o DEFAUL tem uma segunda posição — Left leva o cursor ao rótulo, com a ajuda \"Undo\" —, e o screen.json a registra como trava"
origin: LOOKS-TASK-36
severity: medium
files: [tools/looks/oracle.py, tools/looks/screen.py, tools/looks/screen.json, tools/looks/ui/looks_set.py]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-067 — Correção: o DEFAUL tem uma segunda posição — Left leva o cursor ao rótulo, com a ajuda "Undo" —, e o screen.json a registra como trava

Origin: [LOOKS-TASK-36](/docs/tasks/looks/36-os-sprites-estaticos.md)

## Problema identificado

A linha `DEFAUL` tem **duas** posições na tela, e o `screen.json` conhece uma.
Com o cursor em `DEFAUL`, `Left` não trava: leva a caixa do cursor do valor
`O.K.` para o **rótulo** `DEFAUL`, a ajuda troca de `Confirm` para `Undo`, e o
◀ ao lado de `O.K.` dá lugar a um ▶ em x 276, à direita do rótulo. `Right` volta.
O texto da linha não muda — `O.K.` nas duas —, e é por isso que o walk do
`--screen`, que julga a trava pelo texto, gravou `"left": "locks"`.

Consequência: a janela, que só sabe o que o `screen.json` diz, ignora o `Left`
no `DEFAUL` e continua mostrando `Confirm` e o ◀. O `KEY_SEQUENCE` padrão do
`--keys` não passa por ali, então o gate nunca viu.

## Evidência

Medido na execução da
[`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md), com o
`screen.json` que ela regravou (as setas do `DEFAUL` já gravadas: na chegada
◀(384,43), e depois de `Left` ▶(276,43)):

```text
$ python tools/looks/oracle.py --keys "Up,Left" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help and the same arrows
  FAIL  the help: the game shows 'Undo' and screen.json says 'Confirm'
  FAIL  the help: the game shows 'Undo' and our window shows 'Confirm'
  FAIL  the arrows: the game draws >(276,43) and screen.json says <(384,43)
  FAIL  the arrows: the game draws >(276,43) and our window draws <(384,43)
oracle --keys: 4 difference(s) after 2 press(es), across the game, screen.json and our window
```

O controle fecha antes — a sequência duas vezes no jogo dá a mesma tela —, então
as quatro diferenças são da tabela, não do jogo.

## Causa raiz

O `_walk_row` do `oracle.py` decide trava por **texto**: se duas teclas
seguidas deixam o texto da linha igual, a ponta travou. No `DEFAUL` o texto
nunca muda, mas o cursor, a ajuda e as setas mudam. O modelo do `screen.State`
tem um cursor por linha (qual linha) e um índice por linha (qual valor); a
posição "no rótulo" não cabe em nenhum dos dois.

## Correção

### Arquivo: `tools/looks/oracle.py`

O walk passa a julgar a trava também pela ajuda e pelas setas, e o `DEFAUL`
ganha a posição do rótulo medida: a ajuda (`Undo`), as setas e onde a caixa do
cursor fica.

### Arquivo: `tools/looks/screen.py`

O `State` modela a posição do rótulo no `DEFAUL` (`Left` entra, `Right` sai, e
o que `Up`/`Down` fazem a partir dali medido), e `help_text` e `arrows` a leem.
O `screen.json` se regrava pelo gerador, nunca à mão.

### Arquivo: `tools/looks/ui/looks_set.py`

A caixa do cursor sobre o rótulo quando o `State` diz que ele está lá.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/oracle.py` | modificar |
| `tools/looks/screen.py` | modificar |
| `tools/looks/screen.json` | regravar pelo `--screen --write` |
| `tools/looks/ui/looks_set.py` | modificar |

## Verificação

- [ ] `python tools/looks/oracle.py --keys "Up,Left" 2` sai com 0 diferença,
      e também `"Up,Left,Right"` e `"Up,Left,Down"`
- [ ] `python tools/looks/screen.py --check` verde, com um caso vermelho para a
      posição do rótulo
- [ ] `python tools/looks/ui_check.py` verde
- [ ] `python tools/looks/oracle.py --screen` com 0 diferença do `screen.json`

## Log de Execução *(preenchido após execução)*
