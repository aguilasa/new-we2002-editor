---
id: CORR-LOOKS-071
title: "Hold the rule's pen advance against the game, not only the uv"
origin: LOOKS-TASK-37
severity: high
files: [tools/looks/oracle.py, tools/looks/glyphs.py, tools/looks/controls.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-22
done_commit: 6a4944fc
---

# CORR-LOOKS-071 — Hold the rule's pen advance against the game, not only the uv

Origin: [LOOKS-TASK-37](/docs/tasks/looks/37-a-tabela-de-glifos.md)

## Problema identificado

O critério 2 da LOOKS-TASK-37 pede que cada código dê o `uv`, o tamanho **e o
ponto** que o jogo desenhou. O `oracle.py --glyphs` monta o ponto a partir da
própria chamada de desenho do jogo (`(x, y)` lido em `SCREEN_GLYPH` somado a
`SCENERY_CENTRE`) e procura um sprite ali. `glyphs.Font.run` nunca roda nesse
check, então nada confere "avanço = largura + espaçamento do byte 14" contra o
jogo. A frase do log — espaçamento "Medido em todas as corridas das linhas: 2
nos rótulos…, 1 em Unknown, 0 em SHIRT N e nos dígitos" — não tem comando
atrás. O único confronto indireto é o dos rótulos no `confront --outside`, e
todos os rótulos usam espaçamento 2: uma regra que ignora o espaçamento passa
todos os gates.

## Evidência

```text
$ sed -n 5140,5160p tools/looks/oracle.py   # check_glyphs
draws = [(code, x, y) for code, x, y, passing in calls if not passing]
point = (x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1])   # o ponto do jogo, não o da regra

# estilos iniciais do screen.json
labels spacing 2; values: AGE 0, NAT 1, o resto 2; shirt 0; plate 2

# plantado numa cópia de 0297ea1c: glyphs.py `x += width + spacing` -> `x += width + 2`
$ python glyphs.py        -> glyphs.py: 0 failure(s)
$ python selftest.py      -> controls: 0 failure(s)
```

O self-check do `glyphs.py` fica verde porque o único teste de avanço usa
espaçamento 2; o `confront --outside` compara só os rótulos (espaçamento 2).

## Causa raiz

(hipótese) O check `--glyphs` foi escrito para testar a tabela (uv, tamanho,
CLUT) e reusa as coordenadas da chamada do jogo como chave de busca. As
posições ficaram para a LOOKS-TASK-38 sem separar "onde a string começa"
(alinhamento, task 38) de "como a caneta anda" (espaçamento, esta task).

## Correção

- `tools/looks/oracle.py`, `check_glyphs`: agrupar as chamadas de desenho por
  objeto de texto; para cada objeto, dispor `Font.run(texto, primeiro_ponto,
  espaçamento_do_objeto, cor)` e exigir cada glifo seguinte no ponto que o jogo
  informou. Controle: espaçamento forçado a 0 tem de falhar.
- `tools/looks/glyphs.py`: caso de self-check com espaçamento 0 ou 1.
- `tools/looks/controls.py`: controle que planta `x += width + 2` no
  `Font.run`.

## Arquivos

- tools/looks/oracle.py
- tools/looks/glyphs.py
- tools/looks/controls.py

## Verificação

- Com `x += width + 2` plantado no `Font.run`, `python tools/looks/controls.py
  --only <id novo>` sai **vermelho** e `python tools/looks/oracle.py --glyphs`
  acusa o avanço errado em NAT/AGE/SHIRT nos dois slots.
- Sem o plantio, `python tools/looks/oracle.py --glyphs` imprime `0 problem(s)`.

## Log de Execução

Triagem do `/rite:fix-all looks` em 2026-09-22, HEAD `16550b53`: **reproduzida**.

```text
oracle.py:5149-5151  draws = [(code, x, y) for code, x, y, passing in calls if not passing]
                     point = (x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1])   # glyphs.Font.run nunca chamado
# cópia plantada (git archive HEAD tools), glyphs.py:147 `x += width + spacing` -> `x += width + 2`
$ python glyphs.py    -> glyphs.py: 0 failure(s)
$ python selftest.py  -> controls: 0 failure(s), 100 of 100 controls red; glyphs e screen sem falha
  (a 1 falha do looks_selftest é da cópia sem src/ e data/, não do plantio)
```

Correção em 2026-09-22, sobre `898f54f0`. **Causa raiz confirmada**: `check_glyphs`
só lia `SCREEN_GLYPH`, então não sabia a que objeto (e a que byte 14) cada glifo
pertencia, e nunca chamava `Font.run`; o self-check do `glyphs.py` testava o avanço
só com espaçamento 2.

- `oracle.py`: `_stops` aceita uma tupla de endereços (o `pc` separa as paradas);
  `check_glyphs` arma `SCREEN_PRINT` e `SCREEN_GLYPH` juntos, e `glyph_objects`
  atribui cada glifo ao objeto da última parada de impressão, com o byte 14 e a
  string dele. A passada de desenho é cortada nas **corridas da própria string**
  (`pen_runs`: nova corrida em `\n` e em `\t`), não por onde a caneta foi.
  `pen_problems` dispõe cada corrida com `Font.run` a partir do primeiro glifo e
  exige cada glifo seguinte no ponto do jogo. Controles: espaçamento forçado a 0 e
  a 2 para todo objeto (`PEN_CONTROLS`) tem de falhar.
- Achado da primeira corrida: cortando por linha, `A1` (espaçamento 0) saía com
  1 px de folga entre `A` e `1`. Não é espaçamento: a string é `\t\x12A\t\x1e1`, e
  o `\t` põe a caneta na coluna dele (onde a corrida **começa** é da task 38).
- `glyphs.py`: casos de self-check com espaçamento 0 e 1.
- `controls.py`: `glyphs-pen-ignores-spacing` planta `x += width + 2` no `Font.run`.

```text
# antes (controle novo, glyphs.py sem os casos novos)
$ python tools/looks/controls.py --only glyphs-pen-ignores-spacing
  GREEN  glyphs-pen-ignores-spacing glyphs.py :: Font.run  -- did NOT go red: glyphs
# depois
$ python tools/looks/controls.py --only glyphs-pen-ignores-spacing
  RED    glyphs-pen-ignores-spacing glyphs.py :: Font.run
controls: 1 of 1 red (1 substitution)

# sem plantio (os dois slots dão o mesmo; o slot 1 mostra GK no lugar de CB)
$ python tools/looks/oracle.py --glyphs
    pen: 8 object(s), 86 advance(s) laid by Font.run from each run's first glyph, 0 run(s) off
      object 0x800C7B00  spacing byte 2  gaps drawn [2]  'DEFAUL' (+11 run(s))
      object 0x800C7B14  spacing byte 2  gaps drawn [2]  'O.K.  ' (+8 run(s))
      object 0x800C7B28  spacing byte 1  gaps drawn [1]  'Unknown'
      object 0x800C7B3C  spacing byte 0  gaps drawn [0]  'A' (+9 run(s))
      object 0x800C7B50  spacing byte 2  gaps drawn [2]  '  RIGHT'
      object 0x800C7BA0  spacing byte 0  gaps drawn [0]  'SHIRT N'
      object 0x800C7BB4  spacing byte 2  gaps drawn [2]  'CB'
      object 0x800C7C2C  spacing byte 1  gaps drawn []  ''
    control: every object at spacing 0 puts 24 run(s) off
    control: every object at spacing 2 puts 4 run(s) off
oracle --glyphs: 0 problem(s) over 2 slot(s)

# com `x += width + 2` plantado no Font.run (revertido depois)
  FAIL  slot 2: pen: object 0x800C7B28, 'Unknown' at spacing 1: glyph 1 laid at (149, -67), the game drew it at (148, -67)
  FAIL  slot 2: pen: object 0x800C7B3C, '175' at spacing 0: glyph 1 laid at (159, 5), the game drew it at (157, 5)
  FAIL  slot 2: pen: object 0x800C7B3C, '23' at spacing 0: glyph 1 laid at (204, 29), the game drew it at (202, 29)
  FAIL  slot 2: pen: object 0x800C7BA0, 'SHIRT N' at spacing 0: glyph 1 laid at (-172, -82), the game drew it at (-174, -82)
  (as mesmas quatro no slot 1)
oracle --glyphs: 8 problem(s) over 2 slot(s)

$ python tools/looks/glyphs.py      -> glyphs.py: 0 failure(s)
$ python tools/looks/selftest.py    -> 101 of 101 controls red; looks_selftest: 0 failure(s)
$ python tools/looks/cli.py check   -> 12 module(s), 12 ok, 0 skipped, 0 failed -- ok
```
- **Closed** — commit `6a4944fc` (2026-09-22): fix(looks): hold Font.run's pen advance against the game's draw calls per text object
  - Files (`git show --name-status 6a4944fc`):
    - `M docs/tasks/looks/CORR-LOOKS-071.md`
    - `M tools/looks/controls.py`
    - `M tools/looks/glyphs.py`
    - `M tools/looks/oracle.py`
