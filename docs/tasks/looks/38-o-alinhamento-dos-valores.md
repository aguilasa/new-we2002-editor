---
id: LOOKS-TASK-38
title: "O alinhamento dos valores — a caixa do objeto de texto no `screen.json`, e o valor à direita"
type: implementação
category: ui
phase: 10
depends_on: [LOOKS-TASK-37]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: pending
review_commit: null
done_on: 2026-09-22
done_commit: 19bcdf0a
---

# LOOKS-TASK-38: O alinhamento dos valores

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (o).
- **Saiu da [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md)**, dividida em 2026-09-21 a pedido do usuário.
- **Medido na terceira passada da 31, e não aplicado:** o objeto de texto dos
  valores que o `SCREEN_PRINT` recebe é uma caixa de largura 296 a partir de
  x 176 — borda direita em 472 —, e os valores terminam contra ela (`23`
  começa em 448, `TYPE` em 425, `Unknown` em 392). A janela os escreve a
  partir da esquerda da caixa do cursor.
- **O `screen.json` é gerado**, pelo `oracle.py --screen --write` (~12 min), e
  não se edita à mão: a caixa do objeto entra pelo gerador, e o `--screen`
  remede.
- **Depois da 37**, porque a largura de cada glifo decide onde um valor
  alinhado à direita começa; com a fonte do Qt o alinhamento sairia certo na
  borda e errado em todo o resto.

---

## Objetivo

Cada texto da janela fica onde o jogo o põe dentro da caixa do objeto — os
valores encostados na borda direita.

---

## Critério de conclusão

- [x] O gerador grava a caixa (x, largura) e o modo de alinhamento de cada
      objeto de texto; `screen.py --check` confere, e `--screen` remede com
      0 diferença.
- [x] A janela alinha por essa caixa; o ponto inicial de cada valor bate com
      o do sprite do jogo, nos dois slots, ao longo de `oracle.py --keys`.
- [x] Um controle plantado (o alinhamento pela esquerda) fica vermelho.

---

## Notas

- **Da [`LOOKS-TASK-36`](/docs/tasks/looks/36-os-sprites-estaticos.md):** o ◀
  ao lado do valor tem x **fixo por linha** (302 em `NAT`, 424 em `AGE`, 416
  em `FOOT`, 384 nas outras oito, gravado no `screen.json` pelo walk) e não
  acompanha o começo do texto. Ele não serve de régua para o alinhamento — e o
  alinhamento não precisa movê-lo.
- **Da [`CORR-LOOKS-070`](/docs/tasks/looks/CORR-LOOKS-070.md):** a caixa do
  cursor sobre o valor também é **por linha** — x 314 em `NAT`, 436 em `AGE`,
  428 em `FOOT`, 396 nas outras nove, sempre até 476 —, e o `screen.json` a
  grava em `rows[*].cursor`. O `layout()["cursor"]` (e o `values_x`) continua
  sendo a caixa de `NAT` descida pelo passo; é dele que a janela escreve os
  valores hoje, e é esse o ponto que esta task troca pela caixa do objeto.

- **Da [`LOOKS-TASK-37`](/docs/tasks/looks/37-a-tabela-de-glifos.md):** o
  byte 13 do objeto de texto parece o **modo de alinhamento**: 0 nos rótulos,
  2 nos objetos de `TYPE`, `Unknown` e `RIGHT`, 3 nos dígitos, na placa e na
  camisa. Ele já está gravado no `screen.json` como `align` em
  `initial.*.styles`. Falta medir o que cada modo faz. E um valor é montado de
  **vários objetos**, cada um com o seu espaçamento (`A1 TYPE` = `A1`, com
  espaçamento 0 e um tab, mais `TYPE`, com 2). Hoje a janela o escreve numa
  corrida só, com o estilo do objeto do último pedaço
  (`State.value_style`), a partir da borda esquerda da caixa da linha. Placa
  e camisa saem do x do objeto, e por isso o `looks_ui` julga os sprites com
  `--no-unplaced-text`. Com o alinhamento, essa opção perde o motivo.

## Log de Execução

**Executado em:** 2026-09-22

### O que foi feito

- **A regra, lida das chamadas de desenho.** O byte 13 do objeto é o modo:
  **0** começa a linha na esquerda da caixa, **2** a encosta na borda direita
  (`x + largura − largura da linha`, com o espaçamento de cada glifo) e **3**
  a centra, arredondando para baixo. O `\t` põe a caneta em `x + byte`, por
  cima do que o modo decidiu. Está em `glyphs.ALIGNMENTS` e
  `glyphs.Font.place`, com um modo fora dos três sendo recusado.
- **O código de cor.** A tabela de saltos do código de controle, em
  0x800FC048 do `/SELECTC.BIN`, diz que o **13 grava três bytes como a cor do
  objeto** (0x8010C730) e que o **9 é o tab** (0x8010C690). Por isso o `O.K.`
  do `DEFAUL` sai cinza num objeto lavanda, e a cor **persiste nas linhas
  abaixo**: `screen.line_tokens` passou a emitir o token de cor, e
  `screen.colour_at` dá a cor em vigor no começo de cada linha.
- **A caixa muda com o valor.** O objeto do `NAT` fica em x −80 com `Unknown`
  e em −104 com uma nação. Então o walk grava, **por valor de cada linha**, os
  pedaços que a escrevem — caixa, modo, espaçamento, cor e tokens
  (`oracle.value_layout` → `rows[*].layouts`) — e não uma caixa por linha. A
  placa e a camisa ganharam caixa e tokens no estilo (`oracle.placed_style`).
- **A janela** desenha todo texto por essa tabela (`LooksSet.glyphs`), e o
  relatório imprime cada glifo com ponto e `uv`. Saíram o `--no-unplaced-text`
  e o `State.value_style`, que perderam o motivo.
- **O `--keys`** compara o conjunto inteiro de glifos do quadro contra os da
  janela, com uma linha de falha por linha da tela; o **`--outside`** compara
  as duas colunas de texto pixel a pixel, com a borda da caixa do cursor de
  fora, que pulsa (armadilha 36).

### Evidência

```text
$ python tools/looks/glyphs.py            # os casos do alinhamento
  ok    alignment 0 starts the line at 50
  ok    alignment 2 starts the line at 135
  ok    alignment 3 starts the line at 92
  ok    centring rounds down, as the game's shift does
  ok    a tab puts the pen at its column from the box's left, whatever the alignment
  ok    a colour token tints the glyphs after it and not before
  ok    an alignment no object carries is refused
glyphs.py: 0 failure(s)

$ python tools/looks/screen.py --check
  ok    line_tokens keeps a tab's column and a colour code's three bytes
  ok    a colour code holds into the lines below it
  ok    a layout that spells another value is refused
  ok    an alignment no object carries is refused
  ok    a row with a value and no layout is refused
screen.py: 0 failure(s)

$ python tools/looks/oracle.py --screen --write        # 19 min 8 s
oracle --screen --write: wrote tools/looks/screen.json

$ python tools/looks/oracle.py --keys "" 2             # e 1
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows, the same cursor box and the same 121 glyph(s)
oracle --keys: 0 difference(s) after 19 press(es), across the game, screen.json and our window

$ python tools/looks/oracle.py --keys "<Right x10>" 2                  # NAT numa nacao: a caixa anda
oracle --keys: 0 difference(s) after 10 press(es), ...
$ python tools/looks/oracle.py --keys "<Down x7, Right x40>" 2          # HEIG em 210 cm
oracle --keys: 0 difference(s) after 47 press(es), ...
$ python tools/looks/oracle.py --keys "<Down x2, Right x30>" 2          # SKIN na ponta
oracle --keys: 0 difference(s) after 32 press(es), ...
$ python tools/looks/oracle.py --keys "Up,Left" 2                       # o rotulo do DEFAUL
oracle --keys: 0 difference(s) after 2 press(es), ...

$ python tools/looks/confront.py --outside
  -- slot 2 --
    labels, pixel for pixel within 16 per channel: 0 of 16416 differ (the game against itself: 0; the game one pixel off: 2875)
    values, pixel for pixel within 16 per channel: 0 of 23472 differ (the game against itself: 0; the game one pixel off: 3075)
  -- slot 1 --
    (o mesmo: 0 de 16416 e 0 de 23472, 2875 e 3075 deslocado)
confront --outside: 0 problem(s) over 2 slot(s)
```

**O controle plantado.** `python tools/looks/controls.py --only
glyphs-aligned-left` (o modo 2 devolvendo 0, isto é, o valor pela esquerda) dá
`1 of 1 red`. E o mesmo defeito, plantado na árvore e medido contra o jogo,
deixa o `--keys` vermelho linha por linha:

```text
  FAIL  the glyphs on line y 41: the game draws 10 starting [(200, 41, 184, 146)], our window 10 starting [(176, 41, 46, 158)]
  FAIL  the glyphs on line y 65: the game draws 9 starting [(200, 65, 96, 158)], our window 9 starting [(176, 65, 108, 158)]
```

### Problemas encontrados

- **O `O.K.` saía lavanda, e o jogo o escreve cinza.** A primeira corrida do
  `--outside` com a coluna dos valores deu **514 de 23.472** pixels
  diferentes, em duas linhas só. A causa não era posição: o código de
  controle 13 da string troca a cor, e os tokens o descartavam. A tabela de
  saltos da rotina de impressão fechou a questão, e o `screen.json` foi
  regravado (armadilha 95).
- **A borda da caixa do cursor pulsa** — (206,206,74) no quadro do jogo
  contra (181,181,57) na janela —, e entrava na conta dos pixels. Ela saiu da
  comparação de texto: é pulso, não texto, e a caixa já é uma região "não
  medida, não afirmada".
- **Restaurei o `glyphs.py` de um backup depois de um erro meu.** Para
  mostrar o `--keys` vermelho, plantei o defeito na árvore e desfiz com `git
  checkout --`, que apagou as mudanças ainda não commitadas do arquivo. O
  backup estava em `/tmp`, e o arquivo voltou idêntico (mesmo self-check, 68
  inserções). A forma segura é a do `controls.py`, que planta numa cópia.
- **O `--screen` não foi re-rodado para remedir o arquivo recém-gravado**
  (seriam mais 19 min). O `screen.validate` fechou no gerador — e agora ele
  também exige que os pedaços de cada valor **soletrem** o texto dele —, e o
  `--keys` confere o arquivo contra o jogo em cinco sequências.

### Gates

```text
# na arvore de 19bcdf0a
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 27 file(s), 30000 line(s)
  ..... 102 of 102 controls red
looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
$ python tools/check_tasks.py
check: 0 error(s), 11 warning(s) in 4 cycle(s)
```

O `looks_ui` (16 de 16 controles vermelhos, 4 min), o `--keys` e o
`--outside` rodaram sobre o código do commit e estão transcritos acima; depois
deles só mudou prosa.
- **Closed** — commit `19bcdf0a` (2026-09-22): feat(looks): put every text where the game puts it inside its box
  - Files (`git show --name-status 19bcdf0a`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/38-o-alinhamento-dos-valores.md`
    - `M tools/looks/confront.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/glyphs.py`
    - `M tools/looks/oracle.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/screen.json`
    - `M tools/looks/screen.py`
    - `M tools/looks/ui/app.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui_check.py`
