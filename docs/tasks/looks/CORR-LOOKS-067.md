---
id: CORR-LOOKS-067
title: "Correção: o DEFAUL tem uma segunda posição — Left leva o cursor ao rótulo, com a ajuda \"Undo\" —, e o screen.json a registra como trava"
origin: LOOKS-TASK-36
severity: medium
files: [tools/looks/oracle.py, tools/looks/screen.py, tools/looks/screen.json, tools/looks/ui/looks_set.py, tools/looks/ui/app.py]
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
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

Triagem do `/rite:fix-all looks` em 2026-09-21, HEAD `36d1aaed`: **reproduzida**.

```text
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin WE2002_LOOKS_DRIVE_IMAGE=C:/games/ps1/work/we2002-english.cue     python tools/looks/oracle.py --keys "Up,Left" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help and the same arrows
  FAIL  the help: the game shows 'Undo' and screen.json says 'Confirm'
  FAIL  the help: the game shows 'Undo' and our window shows 'Confirm'
  FAIL  the arrows: the game draws >(276,43) and screen.json says <(384,43)
  FAIL  the arrows: the game draws >(276,43) and our window draws <(384,43)
oracle --keys: 4 difference(s) after 2 press(es), across the game, screen.json and our window
```

### Execução (2026-09-21, HEAD `2cc989db`)

**Reproduzida de novo e causa raiz confirmada** por sonda no emulador, uma
leitura por tecla (cursor lido da VRAM, ajuda, setas, texto do `DEFAUL`):

```text
Up,Left,Left,Right,Right
    Up    -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'
    Left  -> row 0 box (188, 41, 272, 52) help 'Undo' arrows >(276,43) DEFAUL 'O.K.'
    Left  -> row 0 box (188, 41, 272, 52) help 'Undo' arrows >(276,43) DEFAUL 'O.K.'
    Right -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'
    Right -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'
Up,Left,Down,Down,Up,Up
    (no rótulo, Up e Down não mexem em nada: caixa, ajuda e setas ficam)
```

No rótulo, `Left`, `Up` e `Down` **travam** — o cursor não sai da linha pela
vertical —, e só `Right` volta ao valor. O texto nunca muda; o walk, que
julgava trava só por texto, gravou o `Left` como trava e as setas do rótulo
como `left_end`.

**Conserto.**

- `oracle.py`: o `_walk_row` julga trava por texto, ajuda **e** setas; um
  `Left` que mantém o texto e move o resto é a entrada no rótulo, e o novo
  `_walk_label` mede a ajuda, as setas, a caixa do cursor (VRAM) e cada uma de
  `Left`/`Up`/`Down` duas vezes, recusando o que não for trava, e exige que
  `Right` devolva a ajuda e as setas do valor. O `left_end` passa a ser o do
  valor. Um `Right` que mova ajuda ou setas sem mudar o texto é recusado.
- `screen.py`: toda linha declara `label` (`null` ou a posição medida);
  `validate` recusa linha sem a chave, forma fora de `LABEL_MOVES` e ajuda de
  rótulo repetida. O `State` ganha `on_label` e `cursor_box()`; `help_text` e
  `arrows` o leem.
- `ui/looks_set.py`: a caixa do cursor vem de `state.cursor_box()`.
- `screen.json` regravado por `oracle.py --screen --write` (939 s). O diff:
  `"label": null` em onze linhas, a posição do rótulo no `DEFAUL`, e o
  `left_end` dele de ▶(276,43) para ◀(384,43).

```text
label: Left from the first value, help 'Undo', arrows >(276,43), cursor [188, 41, 272, 52]; there Left locks, Up locks, Down locks, and Right back
```

**Verificação.**

```text
$ python tools/looks/oracle.py --keys "Up,Left" 2
oracle --keys: 0 difference(s) after 2 press(es), across the game, screen.json and our window
$ python tools/looks/oracle.py --keys "Up,Left,Right" 2
oracle --keys: 0 difference(s) after 3 press(es), across the game, screen.json and our window
$ python tools/looks/oracle.py --keys "Up,Left,Down" 2
oracle --keys: 0 difference(s) after 3 press(es), across the game, screen.json and our window
$ python tools/looks/oracle.py --keys
oracle --keys: 0 difference(s) after 19 press(es), across the game, screen.json and our window
$ python tools/looks/screen.py --check
  ok    a label position that moves where the walk measured a lock is refused
  ok    a row that does not say whether it has a label is refused, which is the table the walk wrote before CORR-LOOKS-067
  ok    Up, Left from the load puts the cursor on DEFAUL's name, with its help, arrows and box (CORR-LOOKS-067)
screen.py: 0 failure(s)
$ python tools/looks/oracle.py --screen
oracle --screen: 0 difference(s) from screen.json
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check
cli check: 11 module(s), 11 ok, 0 skipped, 0 failed -- ok
$ python tools/looks/ui_check.py
FAIL: slot 2, DEFAUL to both ends: the window says presses '+++++++++++..' and screen.py says '+++++++++++++'
FAIL: slot 1, DEFAUL to both ends: the window says presses '+++++++++++..' and screen.py says '+++++++++++++'
```

O par de capturas do `Up,Left` (`work/looks-shots/keys-slot2.png` e
`keys-slot2-window.png`) mostra a caixa sobre `DEFAUL`, o ▶ à direita do
rótulo e `Undo` nos dois.

**Pendente: o `ui_check.py` fica vermelho por um arquivo fora da lista.** O
`ui/app.py` (`_send_keys`) decide que uma tecla "moveu" comparando
`(state.texts(), state.row)` antes e depois — o mesmo julgamento só por texto
que esta correção tirou do walk. Entrar e sair do rótulo não muda nenhum dos
dois, então a janela relata `..` onde o `State` diz `++`. Todo o resto do gate
passa. O conserto é acrescentar `window.state.on_label` à tupla de antes e
depois, em `tools/looks/ui/app.py`, que não está nos arquivos deste item.

**Pendência fechada (mesma data).** O `tools/looks/ui/app.py` entrou nos
arquivos do item. O `_send_keys` passa a comparar
`(texts, row, on_label)` antes e depois da tecla, e não só o texto e a linha.

```text
$ python tools/looks/ui_check.py
looks_ui: 14 of 14 negative control(s) red, and the window drew every tuple it was asked for and answered every key with what the game shows
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)
```

Fica de fora, e vai para uma correção nova: com o cursor no valor, a caixa da
janela é carregada da linha de carga (x 314), e o jogo a desenha em x 396 no
`DEFAUL`. Nenhum gate compara a caixa do cursor da janela com a do jogo, e o
problema vem de antes desta correção.
