---
id: CORR-LOOKS-071
title: "Hold the rule's pen advance against the game, not only the uv"
origin: LOOKS-TASK-37
severity: high
files: [tools/looks/oracle.py, tools/looks/glyphs.py, tools/looks/controls.py]   # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
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
