---
id: CORR-LOOKS-082
title: "Dar ao parse_keys uma sintaxe de repetição, em vez de linhas de 317 caracteres"
origin: CORR-LOOKS-075
severity: low
files: [tools/looks/screen.py, docs/tasks/looks/38-o-alinhamento-dos-valores.md]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: in-progress
depends_on: []
done_on: null
done_commit: null
---

# CORR-LOOKS-082 — Dar ao parse_keys uma sintaxe de repetição, em vez de linhas de 317 caracteres

Origin: [CORR-LOOKS-075](/docs/tasks/looks/CORR-LOOKS-075.md)

## Problema identificado

A [CORR-LOOKS-075](/docs/tasks/looks/CORR-LOOKS-075.md) escolheu a metade menor
da correção: escreveu por extenso as três sequências abreviadas do log da
LOOKS-TASK-38. O resultado roda, e é longo — a linha de 47 teclas tem **317
caracteres** e a de 32 tem 232, contra 229 da maior linha que havia em
`docs/tasks/looks/`. A outra metade continua aberta: o `screen.parse_keys` não
tem sintaxe de repetição, e foi justamente por isso que quem escreveu o log
abreviou à mão.

## Evidência

```text
$ python tools/looks/oracle.py --keys "<Right x10>" 2
oracle FAILED: '<Right x10>' is not one of the four this screen answers to: Up, Down, Left, Right

$ grep -n 'oracle.py --keys' docs/tasks/looks/38-o-alinhamento-dos-valores.md | awk '{print length($0)}'
# a linha de 47 teclas tem 317 caracteres
```

## Causa raiz

`screen.parse_keys` aceita só os quatro nomes separados por vírgula
(`tools/looks/screen.py`, perto da linha 1084).

## Correção

Aceitar uma forma de repetição — `Right x41` ou `41*Right`, uma só, escolhida e
documentada —, com self-check dos dois sentidos e de entrada inválida, e
reescrever as três linhas do log da task 38 na forma nova. O controle é a
sequência longa por extenso e a abreviada darem a mesma lista de teclas.

## Arquivos a criar ou modificar

- `tools/looks/screen.py`
- `docs/tasks/looks/38-o-alinhamento-dos-valores.md`

## Verificação

`parse_keys("Right x41")` dá as mesmas 41 teclas que a forma por extenso, e
toda linha `$ python tools/looks/oracle.py --keys …` copiada do arquivo da task
sai com código 0.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `ae915dba`: **reproduzida**.

```text
$ python tools/looks/oracle.py --keys "<Right x10>" 2
oracle FAILED: '<Right x10>' is not one of the four this screen answers to: Up, Down, Left, Right
  (saída 1; falha no parse, sem subir emulador -- oracle.py:5643 chama parse_keys antes do preflight em 5648)

linha 151 do arquivo da task: 47 teclas, 317 caracteres de comando (335 com o comentário)
linha 153: 32 teclas, 232 (249 com o comentário)
maior linha nos outros arquivos numerados de docs/tasks/looks/: 229 (36-...:178)

tools/looks/screen.py:1093  def parse_keys(text)  -- split por vírgula contra BUTTONS (screen.py:856);
  nenhuma sintaxe de repetição. A Causa raiz desta CORR diz "perto da linha 1084": são 1093.
```

**Corrigida em 2026-09-22.**

### A forma escolhida

`Right x41` — **uma só**, e `41*Right` é **recusado**, não adivinhado: o valor
de ter sintaxe é uma sequência ter uma grafia, e quem lê um log não precisar
perguntar qual das duas está valendo. A escolha é a do exemplo da Verificação
desta CORR, e é também a que quem abreviou o log da task 38 à mão escreveu
sozinho (`<Right x10>`) — menos os sinais de maior e menor, que continuam
sendo recusa.

As regras, todas em `screen.REPETITION` e no docstring do `parse_keys`:

- o `x` é obrigatório e minúsculo; o branco antes dele é opcional (`Right x41`
  e `Rightx41` são a mesma sequência, como `Down, Right ,Up` já era);
- a contagem é decimal e **de pelo menos um** — `Right x0` é recusado, não
  lido como "nenhuma tecla"; sequência de nenhuma tecla é a string vazia, que
  o `--keys ""` já usa;
- contado e simples se misturam na mesma linha (`Down,Right x31`);
- a recusa **ensina a forma**: a mensagem passou a terminar em `(a repetition
  is written 'Right x41')`, para quem colar `41*Right` ou `<Right x10>` ler
  ali o que se aceita.

### O que mudou

```python
# tools/looks/screen.py, antes (1093)
def parse_keys(text: str) -> list:
    """`Down,Down,Right` to the three presses it names, refusing the rest."""
    buttons = [part.strip() for part in text.split(",") if part.strip()]
    for button in buttons:
        if button not in BUTTONS:
            raise BadScreen("%r is not one of the four this screen answers "
                            "to: %s" % (button, ", ".join(BUTTONS)))
    return buttons

# depois (1093-1146): REPETITION = re.compile(r"^([A-Za-z]+)\s*x([0-9]+)$"),
# REPETITION_EXAMPLE, _not_a_button(), e o laço que expande a contagem
    for part in text.split(","):
        ...
        found = REPETITION.match(part)
        if found is None:                      # parte simples, como antes
            ...
        button, count = found.group(1), int(found.group(2))
        if button not in BUTTONS:
            raise _not_a_button(button)
        if count < 1:
            raise BadScreen("%r counts no press; a repetition is at least "
                            "one, and a sequence of none is the empty string"
                            % part)
        buttons.extend([button] * count)
```

### Os self-checks (`screen.py --check`)

O **controle** é o par: a sequência abreviada e a escrita por extenso têm de
dar a mesma lista — senão a linha curta de um log mede outra coisa que a longa
que ela substituiu.

```text
$ python tools/looks/screen.py --check
  ok    a key sequence with a stranger in it is refused whole
  ok    a key sequence parses to the presses it names
  ok    the abbreviated sequence and the written-out one are the same presses -- the control of the repetition form
  ok    a count repeats its own button and nothing else
  ok    counted and plain parts mix, and the blank before the x is optional
  ok    a count of one is the button alone
  ok    a stranger with a count is refused like a stranger without one
  ok    the other spelling of a repetition is refused, not guessed at
  ok    and so is the hand abbreviation a log once carried
  ok    a count with no number is not a button either
  ok    a count of zero is refused, not read as no press
screen.py: 0 failure(s)
```

Os dois sentidos são o terceiro (`Down x6,Right x41` == as 47 por extenso) e o
quarto (`Right x41` == `["Right"] * 41`); a entrada inválida são as cinco
recusas, entre elas `41*Right` e o `<Right x10>` que o log carregava.

### As três linhas da task 38, rodadas na forma nova

As sequências são **as mesmas** da [`CORR-LOOKS-075`](/docs/tasks/looks/CORR-LOOKS-075.md)
(`e04a0b05`) — `Right` ×10; `Down` ×6 + `Right` ×41; `Down` ×1 + `Right` ×31 —,
e as transcrições debaixo delas ficaram como estavam, que é evidência daquela
corrida. O que mudou é a grafia do comando, e cada uma foi rodada de novo no
jogo para mostrar que a grafia curta mede o mesmo (cada corrida imprime as doze
linhas da tela; abaixo, delas, só a que a sequência move):

```text
$ python tools/looks/oracle.py --keys "Right x10" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows, the same cursor box and the same 121 glyph(s)
  the window answered the same 10 press(es)
    help      'Nation'
    cursor    [314, 53, 476, 64]
oracle --keys: 0 difference(s) after 10 press(es), across the game, screen.json and our window

$ python tools/looks/oracle.py --keys "Down x6,Right x41" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows, the same cursor box and the same 121 glyph(s)
  the window answered the same 47 press(es)
    HEIG      '210 cm'
    help      'Height'
    cursor    [396, 125, 476, 136]
oracle --keys: 0 difference(s) after 47 press(es), across the game, screen.json and our window

$ python tools/looks/oracle.py --keys "Down,Right x31" 2
  control: the same sequence twice in the game gives the same twelve rows, the same help, the same arrows, the same cursor box and the same 121 glyph(s)
  the window answered the same 32 press(es)
    SKIN      'D TYPE'
    help      'Skin Colour   ■ Turn'
    cursor    [396, 65, 476, 76]
oracle --keys: 0 difference(s) after 32 press(es), across the game, screen.json and our window
```

As contagens (10, 47, 32) e onde cada sequência para — o cursor em `NAT`, com a
ajuda `Nation` e a caixa dele; `HEIG` em `210 cm`; `SKIN` em `D TYPE` — são as
da corrida da CORR-LOOKS-075.
E toda linha `--keys` do arquivo da task, lida do markdown e passada ao
`parse_keys`, dá a contagem que a transcrição debaixo dela diz — o `''` é a
sequência default do `--keys` sem argumento (`oracle.KEY_SEQUENCE`, 19 teclas):

```text
''                     -> 0 press(es)
'Right x10'            -> 10 press(es)
'Down x6,Right x41'    -> 47 press(es)
'Down,Right x31'       -> 32 press(es)
'Up,Left'              -> 2 press(es)
```

O comando de 317 caracteres tem agora **57**, e o de 232 tem 54; com o
comentário ao lado, as linhas do arquivo caíram de 335 e 249 para **88 e 87** —
abaixo da maior linha dos outros arquivos numerados de `docs/tasks/looks/`
(229), que era o que esta CORR mediu na triagem.

### Gates

```text
$ python tools/looks/screen.py --check
screen.py: 0 failure(s)
$ python tools/looks/selftest.py --quiet
  ..... rule 1 swept 27 file(s), 30181 line(s)
  ..... 103 of 103 controls red
looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
$ sh <rite> check --quick --cycle looks
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

### O que ficou de fora, e por quê

- **Sem controle plantado novo.** O `controls.py` estava com outro worker nesta
  leva; a forma nova é recusa pura e os cinco casos negativos do `--check`
  cobrem os dois sentidos. Fica o encaminhamento: um controle que faça o
  `parse_keys` **ignorar** a contagem (devolver uma tecla só) tem de ficar
  vermelho no `--check`.
- **A sintaxe não está escrita fora do `screen.py`.** O uso do `oracle.py`
  (linha 46), a ajuda do `--keys` do `ui/app.py` (31 e 301) e o docstring do
  `scene.screen_keys` continuam dizendo `Down,Right,Right`. São arquivos fora
  desta correção; encaminhados.
