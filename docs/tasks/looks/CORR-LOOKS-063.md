---
id: CORR-LOOKS-063
title: "Correção: o `--silhouette-styles` decide por mínimo, sem controle e sem margem, e o \"estilo trocado discorda\" não é asserção"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-28
severity: high
done_on: 2026-09-18
done_commit: 50bb614
---

# CORR-LOOKS-063: o gate dos estilos no close-up não tem controle nem margem

## Problema identificado

O critério 5 da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md)
foi fechado assim:

```text
- [x] Três estilos de cabelo diferentes, dois slots: a silhueta concorda, e um
      estilo trocado de propósito discorda — **no close-up**, onde o estilo é
      grande: cada foto do jogo escolhe o próprio estilo entre os três, 6 de 6,
      por 1,4x a 4,4x (`--silhouette-styles`).
```

O gate que sustenta isso é o `confront.check_closeup_styles`, e ele faz **uma**
pergunta por foto: se o menor dos três escores é o do estilo que a tela mostra.

```python
tools/looks/confront.py:1415
                best = min(scores, key=scores.get)
                ...
                if best != shown:
                    problems.append(...)
```

Faltam três coisas que o próprio ciclo exige de silhueta, e que o
`--silhouette` da mesma task tem:

1. **Nenhum controle fecha antes.** O perfil, Fase 9: *"Silhueta só se compara
   com a câmera do jogo, e o limiar sai do controle — emulador contra emulador
   no mesmo quadro dá zero, em quadro deslocado dá diferença —, escrito depois
   de medido e dito que foi."* O `--silhouette` imprime *"control: frame 60
   captured twice … identical"* antes de qualquer comparação; o
   `--silhouette-styles` não captura nada duas vezes.
2. **Nenhuma margem.** "Um estilo trocado de propósito discorda" é, no código,
   *"pontua mais que o certo por qualquer quantia"*. A razão 1,4x a 4,4x do
   critério não é conferida nem impressa — sai de conta à mão sobre a tabela.
   E o `STYLE_MARGIN = 1.5` que o `_judged` aplica à mesma pergunta no corpo
   inteiro **reprovaria** esta corrida: a foto `A1` do slot 2 separa o nosso
   `I3` por **1,36x**.
3. **Nenhum limite para o escore certo.** O `_judged` recusa um casamento acima
   de `MATCH_SHARE` da tinta; aqui um escore certo de qualquer tamanho passa,
   desde que os outros dois sejam maiores.

Com três candidatos e só o mínimo, a asserção pega uma troca de estilo, e só
isso. Foto que muda de corrida para corrida, cabeça quase igual às outras, ou
câmera derivada errada passam verdes enquanto a ordem não se inverter.

## Evidência

Recorrido hoje, na árvore de `54c4888`, com as duas imagens e os dois states:

```text
$ python tools/looks/confront.py --silhouette-styles
    game A-A1-A-A-A: camera spread 3.7 / 0.51, walk frame 12; head band A1 202*  C1 357  I3 274
    game A-C1-A-A-A: camera spread 3.7 / 0.53, walk frame 12; head band A1 488  C1 119*  I3 563
    game A-I3-A-A-A: camera spread 3.7 / 0.54, walk frame 12; head band A1 385  C1 559  I3 155*
    game A-A1-A-A-A: camera spread 3.9 / 0.52, walk frame 12; head band A1 178*  C1 323  I3 284
    game A-C1-A-A-A: camera spread 74.1 / 0.89, walk frame 12; head band A1 469  C1 127*  I3 561
    game A-I3-A-A-A: camera spread 3.7 / 0.51, walk frame 12; head band A1 373  C1 542  I3 176*
confront --silhouette-styles: 0 problem(s) over 2 slot(s)
```

Não há linha de controle na saída. As razões, calculadas sobre ela: a menor é
274/202 = **1,36x** (slot 2, foto `A1`, contra o nosso `I3`), e a maior é
563/119 = **4,73x** (slot 2, foto `C1`, contra o nosso `I3`).

O controle é barato, porque o close-up é determinístico. Medido hoje com o
próprio `confront.closeup_at_tuple`, duas vezes seguidas, slot 2:

```text
A-A1-A-A-A walk 12 12 ink 4895 4895 mask diff 0 head-band diff 0 rot equal True
A-I3-A-A-A walk 12 12 ink 4698 4698 mask diff 0 head-band diff 0 rot equal True
```

E o contraste com o gate irmão, que tem os dois controles:

```text
$ python tools/looks/confront.py --silhouette
    control: frame 60 captured twice, 2383 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [603, 1483] pixel(s)
```

## Causa raiz

O `--silhouette-styles` foi reescrito na quinta sessão como pergunta de
classificação (qual dos três?), e os controles e limiares do `_judged` ficaram
no caminho do corpo inteiro, que foi removido.

## Correção

### Arquivo: `tools/looks/confront.py`

1. **Controle antes do teste:** o primeiro close-up de cada slot capturado
   duas vezes, e o gate recusa se a máscara ou a câmera derivada diferirem.
   O zero medido hoje entra como o esperado.
2. **Margem medida e impressa:** a razão entre o segundo melhor e o certo
   impressa por foto e conferida contra um limiar escrito **abaixo** do mínimo
   medido (1,36x), com o valor e a data no docstring, como o `MATCH_MARGIN`.
   Se o limiar ficar diferente do `STYLE_MARGIN` do corpo inteiro, o docstring
   diz por quê.
3. **Teto para o escore certo**, como o `MATCH_SHARE`: uma fração da tinta da
   faixa da cabeça, medida.

### Arquivos: `docs/tasks/looks/28-a-camera-do-jogo.md`, `docs/PLAN-LOOKS-PY.md` (§6 (h), §10.3 (m)), `docs/prompts/perfil-looks.md` (a linha do gate)

A razão citada passa a ser a que o gate imprime (a
[`CORR-LOOKS-064`](/docs/tasks/looks/CORR-LOOKS-064.md) corrige o número), e a
linha do gate no perfil diz que o controle fecha antes.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/confront.py` | modificar |
| `tools/looks/controls.py` | modificar (controle plantado: a margem ignorada) |
| `docs/tasks/looks/28-a-camera-do-jogo.md` | modificar |
| `docs/PLAN-LOOKS-PY.md` | modificar |
| `docs/prompts/perfil-looks.md` | modificar |

## Verificação

- [x] `confront.py --silhouette-styles` imprime a linha de controle (mesmo
      close-up duas vezes, 0 pixel) antes das seis comparações
- [x] cada foto imprime a razão contra o segundo melhor, e uma razão abaixo do
      limiar reprova
- [x] controle plantado em `controls.py` que tira a margem fica vermelho
- [x] `python tools/looks/selftest.py --quiet` verde
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-18

**Resumo do que foi feito**

A evidência bate número a número — as seis linhas da tabela, `0 problem(s)`, e
nenhuma linha de controle. O `--silhouette-styles` agora pergunta como o
`--silhouette` pergunta:

1. **Controle antes.** Em cada slot, o close-up de `A-A1-A-A-A` capturado duas
   vezes; o gate recusa o slot inteiro se a máscara, o quadro da caminhada ou a
   câmera derivada diferirem. A segunda captura é reaproveitada como a foto
   desse estilo, então o controle custa um close-up por slot.
2. **Margem, contra o estilo errado mais próximo.** Impressa por foto e
   conferida contra `CLOSEUP_MARGIN = 1.2`, abaixo do mínimo medido de
   **1,36x**. Não é o `STYLE_MARGIN = 1.5` do corpo inteiro, e o docstring diz
   por quê: com 1,5 a corrida correta de hoje reprovaria na foto mais apertada.
3. **Teto para o escore certo**, `CLOSEUP_SHARE = 0.25` da tinta da faixa da
   cabeça — medido **6% a 8%**, o mesmo espaço que o `MATCH_SHARE` deixa sobre
   os seus 8% a 17%.

O julgamento saiu para uma função pura, `closeup_verdict()`, porque o
controle plantado precisa de caminho sem emulador: o `self_check` do
`confront.py` a alimenta com os números da foto `A1` do slot 2 e com três casos
vermelhos que um mínimo simples deixa passar (vitória por um fio, estilo
trocado, escore certo longe da cabeça do jogo).

A corrida, depois do conserto:

```text
$ python tools/looks/confront.py --silhouette-styles
  -- slot 2 (outfield player) --
    control: A-A1-A-A-A close-up captured twice, walk frame 12 and 12, 0 pixel(s) apart, camera identical
    game A-A1-A-A-A: ... head band A1 202*  C1 357  I3 274; nearest wrong 1.36x, right 202 of 2379 (8%)
    game A-C1-A-A-A: ... head band A1 488  C1 119*  I3 563; nearest wrong 4.10x, right 119 of 2120 (6%)
    game A-I3-A-A-A: ... head band A1 385  C1 559  I3 155*; nearest wrong 2.48x, right 155 of 2059 (8%)
  -- slot 1 (goalkeeper) --
    control: A-A1-A-A-A close-up captured twice, walk frame 12 and 12, 0 pixel(s) apart, camera identical
    game A-A1-A-A-A: ... head band A1 178*  C1 323  I3 284; nearest wrong 1.60x, right 178 of 2440 (7%)
    game A-C1-A-A-A: ... head band A1 469  C1 127*  I3 561; nearest wrong 3.69x, right 127 of 2124 (6%)
    game A-I3-A-A-A: ... head band A1 373  C1 542  I3 176*; nearest wrong 2.12x, right 176 of 2097 (8%)
confront --silhouette-styles: 0 problem(s) over 2 slot(s)
```

**Problemas encontrados**

1. **A razão que interessa é contra o mais próximo, e ela não é a da CORR.**
   A evidência calcula 1,36x a **4,73x**, e o 4,73x é 563/119 — contra o estilo
   errado **mais distante**. Um veredito só é tão seguro quanto o estilo que
   ele quase escolheu, então o gate imprime a razão contra o mais próximo, e a
   maior dela é **4,10x** (488/119). É esse o número que a
   [`CORR-LOOKS-064`](/docs/tasks/looks/CORR-LOOKS-064.md) tem de escrever.
2. **A regra 1 pegou os casos do self check**: 2379 e 2200 soltos parecem
   endereço. O número da tinta virou um local com `# not-an-address:`, e os
   outros saíram dele.

**Arquivos criados/modificados**

- `tools/looks/confront.py` — `CLOSEUP_MARGIN`, `CLOSEUP_SHARE`,
  `closeup_verdict()`, o controle e a linha impressa no
  `check_closeup_styles()`, quatro casos no `self_check`
- `tools/looks/controls.py` — controle `confront-closeup-minimum-only`
- `docs/tasks/looks/28-a-camera-do-jogo.md` (critério 5),
  `docs/PLAN-LOOKS-PY.md` (§6 (h)), `docs/prompts/perfil-looks.md` (a linha do
  gate)
