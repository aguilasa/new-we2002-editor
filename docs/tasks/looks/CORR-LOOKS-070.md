---
id: CORR-LOOKS-070
title: "A caixa do cursor no valor do DEFAUL começa em x 396 no jogo, e a tabela a carrega da linha de carga em x 314"
origin: CORR-LOOKS-067
severity: low
files: [tools/looks/oracle.py, tools/looks/screen.py, tools/looks/screen.json]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-070 — A caixa do cursor no valor do DEFAUL começa em x 396 no jogo, e a tabela a carrega da linha de carga em x 314

Origin: [CORR-LOOKS-067](/docs/tasks/looks/CORR-LOOKS-067.md)

## Problema identificado

Com o cursor no **valor** do `DEFAUL` (um `Up` depois da carga), o jogo
desenha a caixa amarela em `(396, 41, 476, 52)`. O `screen.State.cursor_box()`
não mede a caixa por linha: carrega para baixo, pelo `pitch`, a caixa da linha
de carga (`cursor_box_on_load = [314, 53, 476, 64]`), e dá `[314, 41, 476, 52]`.
A janela desenha o que a tabela diz, então sai 82 px mais larga à esquerda. Nenhum
gate compara a caixa do cursor da janela com a do jogo, e o `--keys` compara
texto, ajuda e setas, não a caixa.

Apontado pelo worker da CORR-LOOKS-067 em 2026-09-21; anterior a ela.

## Evidência

```text
$ grep -n "396" docs/tasks/looks/CORR-LOOKS-067.md     # o que o walk da 067 leu da VRAM
116:    Up    -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'

$ python -c "import json,sys; sys.path.insert(0,'tools/looks'); import screen; \
    d=json.load(open('tools/looks/screen.json',encoding='utf-8')); s=screen.State(d,'2'); \
    print('load',s.row,s.cursor_box()); s.press('Up'); print('after Up',s.row,s.cursor_box())"
load NAT [314, 53, 476, 64]
after Up DEFAUL [314, 41, 476, 52]
```

## Causa raiz

(hipótese) `State.cursor_box()` (`tools/looks/screen.py`) supõe que a caixa
tem a mesma largura em toda linha e só desce pelo `pitch`. O walk do `--screen`
mede a caixa na chegada, mas grava só a da linha de carga
(`cursor_box_on_load`); a caixa por linha nunca entra na tabela. Falta saber se
só o `DEFAUL` difere ou se outras linhas também.

## Correção

- `tools/looks/oracle.py`, walk do `--screen --write`: gravar a caixa do cursor
  medida no valor de **cada** linha (como a 067 já faz para o rótulo).
- `tools/looks/screen.py`: `cursor_box()` lê a caixa da linha; `validate` recusa
  linha sem ela.
- Um confronto da caixa no `--keys` (jogo × tabela × janela), com controle
  plantado.
- Regenerar `tools/looks/screen.json` pelo gerador.

## Arquivos a criar ou modificar

- `tools/looks/oracle.py`
- `tools/looks/screen.py`
- `tools/looks/screen.json` (gerado)

## Verificação

O comando `python` da Evidência deve dar `after Up DEFAUL [396, 41, 476, 52]`,
e o `oracle.py --keys "Up" 2` deve confrontar a caixa e dar 0 diferença; com a
caixa do `DEFAUL` plantada em x 314, vermelho.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `18dcf753`: **reproduzida**.

```text
$ grep -n "396" docs/tasks/looks/CORR-LOOKS-067.md
116:    Up    -> row 0 box (396, 41, 476, 52) help 'Confirm' arrows <(384,43) DEFAUL 'O.K.'
(também 119, 120 e 202, com a mesma caixa)
$ python -c "... screen.State(d,'2') ... press('Up') ..."
load NAT [314, 53, 476, 64]
after Up DEFAUL [314, 41, 476, 52]
```

### Execução (2026-09-22, HEAD `18dcf753`)

**Medição antes do conserto: não é só o `DEFAUL`.** Sonda no emulador (script
de rascunho sobre `oracle.screen_frames`/`_cursor_row`, 1162 s), a caixa lida
da VRAM em toda linha dos dois slots — na chegada, na ponta esquerda, no valor
do meio e na ponta direita:

```text
linha      slot 1 e slot 2 (as quatro leituras iguais em cada linha)
DEFAUL     (396,  41, 476,  52)
NAT        (314,  53, 476,  64)
SKIN       (396,  65, 476,  76)
HAIR       (396,  77, 476,  88)
H.COL      (396,  89, 476, 100)
FACE       (396, 101, 476, 112)
H.F.COL.   (396, 113, 476, 124)
HEIG       (396, 125, 476, 136)
BODY       (396, 137, 476, 148)
AGE        (436, 149, 476, 160)
BOOTS      (396, 161, 476, 172)
FOOT       (428, 173, 476, 184)
```

A caixa é **por linha**, igual nos dois slots e em todo valor da linha; a
tabela, que descia a de `NAT` pelo passo, errava **onze** das doze linhas, não
só o `DEFAUL`. (O x de cada caixa fica 12 px à direita do ◀ que a
LOOKS-TASK-36 mediu por linha: 302, 384, 424, 416.) A hipótese da Causa raiz
se confirma, com o alcance maior.

**Conserto.**

- `oracle.py`: o `_walk_row` lê a caixa do valor na chegada e nas duas pontas
  (depois do rótulo, no `DEFAUL`) e recusa se ela se mover ao longo da linha;
  grava `rows[*].cursor`. O `measure_screen` confere cada uma contra a caixa
  que o `_walk_cursor` leu ao chegar à linha. O `--keys` passa a ler a caixa
  do jogo (VRAM, nas duas corridas do controle), a do `screen.State` e a da
  janela — esta **medida na captura que a janela grava** (`window_cursor`),
  não perguntada a ela. Self-check do `window_cursor` numa imagem sintética em
  escala 2.
- `screen.py`: `State.cursor_box()` lê a caixa da linha; `validate` recusa
  linha sem ela e caixa que não cubra a própria linha. Três checks novos no
  `--check` (a caixa é da linha e não a de outra descida pelo passo; linha sem
  caixa recusada; caixa fora da linha recusada) e um no estado medido.
- `screen.json` regravado por `oracle.py --screen --write` (1160 s): o diff é
  só as doze chaves `cursor`, 72 linhas acrescentadas.

**Verificação.**

```text
$ python -c "... screen.State(d,'2') ... press('Up') ..."
load NAT [314, 53, 476, 64]
after Up DEFAUL [396, 41, 476, 52]
$ python tools/looks/oracle.py --keys "Up" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows and the same cursor box
    cursor    [396, 41, 476, 52]
oracle --keys: 0 difference(s) after 1 press(es), across the game, screen.json and our window
```

Controle plantado (rascunho `plant.py`: a caixa do `DEFAUL` da tabela em
x 314, e a janela com o `cursor_box` antigo, descido pelo passo):

```text
  FAIL  the cursor box: the game draws [396, 41, 476, 52] and screen.json says [314, 41, 476, 52]
  FAIL  the cursor box: the game draws [396, 41, 476, 52] and our window draws [314, 41, 476, 52]
oracle --keys: 2 difference(s) after 1 press(es), across the game, screen.json and our window
```

Outras sequências, todas com 0 diferença entre jogo, tabela e janela:

```text
--keys (as 19 do KEY_SEQUENCE)        cursor [396, 125, 476, 136]   0 difference(s)
--keys "Up,Left" 2                    cursor [188, 41, 272, 52]     0 difference(s)
--keys "Up,Left,Right" 2              cursor [396, 41, 476, 52]     0 difference(s)
--keys "Up" 1                         cursor [396, 41, 476, 52]     0 difference(s)
--keys "Down" x8 1  (AGE)             cursor [436, 149, 476, 160]   0 difference(s)
--keys "Down" x10 2 (FOOT)            cursor [428, 173, 476, 184]   0 difference(s)
$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ python tools/looks/oracle.py --check
oracle.py: 0 failure(s)
$ python tools/looks/selftest.py
looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check
cli check: 11 module(s), 11 ok, 0 skipped, 0 failed -- ok
```
$ python tools/looks/oracle.py --screen
  screen measured in 1131s
oracle --screen: 0 difference(s) from screen.json
$ python tools/looks/ui_check.py
looks_ui: 16 of 16 negative control(s) red, and the window drew every tuple it was asked for and answered every key with what the game shows
```

A janela não mudou: ela já desenhava `state.cursor_box()`, e o conserto do
`screen.py` a corrigiu. O `layout()["cursor"]` (e o `values_x`), de onde a
janela escreve os valores, continua sendo a caixa de `NAT` descida pelo passo —
é o ponto que a [`LOOKS-TASK-38`](/docs/tasks/looks/38-o-alinhamento-dos-valores.md)
troca, e ganhou nota lá.
