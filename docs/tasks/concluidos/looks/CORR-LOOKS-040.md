---
id: CORR-LOOKS-040
title: "Correção: o `looks_ui` só julga a cabeça, e passa com a figura inteira apagada"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-16
severity: medium
done_on: 2026-09-16
done_commit: 3c65af4
---

# CORR-LOOKS-040: onze das doze peças estão fora do gate da UI

## Problema identificado

O `ui_check.PIECE = "head"`: as quatro corridas que o gate julga desenham
`--piece head`, e a razão está escrita — as tuplas mexem na cabeça, e a figura
inteira diluiria a diferença. A razão é boa e a consequência não foi olhada:
**nenhuma das outras onze peças entra em julgamento nenhum.**

A corrida de `--smoke` desenha a figura inteira e **imprime as contagens** —
593 primitivas, 356 texturizadas, 12 seções, 1.186 triângulos. O gate lê dessa
saída apenas `window up` e o `-32000`, e joga os números fora. O contexto da
própria LOOKS-TASK-16 diz por que eles existem:

> um quadro em branco e um boneco escrevem PNG do mesmo tamanho, e só os
> números separam os dois antes de alguém olhar

O gate trocou os números pelo PNG, que é mais forte — para a cabeça. Para o
resto da figura não sobrou nem uma coisa nem outra.

## Evidência

Apagando o corpo numa cópia da árvore — `sections_of` devolvendo `[]` para as
peças do `EDT_MOD.BIN`, de modo que a figura passa de 593 primitivas e 12
seções para 18 e 1:

```text
$ <venv>/python <cópia>/tools/looks/ui/app.py --smoke
  A-A1-A-A-A, figure 0: 18 primitive(s), 18 textured, 3 surface(s), 36 triangle(s)
  sections 1, shelf on, wireframe off, camera yaw 180 pitch 0

$ python <cópia>/tools/looks/ui_check.py
looks_ui: 3 of 3 negative control(s) red, and the window drew every tuple it
          was asked for
exit=0
```

**Verde, com onze peças de doze desaparecidas.**

O que segura a árvore hoje são dois gates que não são este: o mesmo plantio
deixa o `scene.py --check-image` vermelho —

```text
scene --check-image: 1 problem(s)
    the scene has no head or no boots, so up was not measured
```

— e o `looks_selftest` também (`1 failure(s)`). Então o repositório não está
exposto; o que está errado é o alcance **deste** alvo, que é o da fase 5 e o
único que põe a janela de pé.

## Causa raiz

`PIECE = "head"` foi escolhido para não diluir as diferenças de cor, e nada foi
posto no lugar para cobrir a figura que o `--smoke` desenha.

## Correção

### Arquivo: `tools/looks/ui_check.py`

Duas metades, e nenhuma delas é trocar o `--piece head`, que está certo pela
razão escrita:

1. **Ler os números que o `--smoke` imprime**, em vez de descartá-los: parsear
   a linha de contagens e exigir que a figura inteira traga mais de uma seção,
   mais primitivas do que a cabeça sozinha, e alguma texturizada. São as
   asserções que o próprio contexto da task chama de "o que separa os dois".
2. **Julgar um PNG da figura inteira**, uma vez, com os mesmos juízes de
   quadro: tamanho, não-branco e teto de fundo. Custa uma corrida a mais
   (~1 s) e põe as onze peças dentro do alvo.

E o controle negativo correspondente: apagar o corpo tem de deixar o gate
vermelho, como apagar os triângulos já deixa.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/ui_check.py` | modificar |
| `docs/tasks/looks/16-contratos-da-ui.md` | modificar (o critério e o Log) |

## Verificação

- [x] `python tools/looks/ui_check.py` verde, julgando também a figura inteira
- [x] o mesmo gate fica **vermelho** com `sections_of` devolvendo `[]` —
      `exit=1`, com as duas linhas dizendo qual piso caiu
- [x] as contagens do `--smoke` entram numa asserção, não só na impressão
- [x] `python tools/looks/selftest.py --quiet` verde, 41 de 41 controles
      vermelhos
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduz: com o corpo apagado, o `--smoke` cai de 593 primitivas em
doze seções para **18 em uma**, e o gate saía **0**.

As duas metades da CORR foram feitas, e nenhuma delas troca o `--piece head`,
que está certo pela razão escrita.

**1. As contagens viraram asserção.** O `_counted()` lê a linha que o app já
imprimia e o `judge_whole()` a julga contra `WHOLE = {primitives: 100,
sections: 2, textured: 1}` — o menor enunciado que separa uma figura de uma
peça dela. Não são os números do disco nem os da cabeça: a cabeça sozinha é 18
em uma seção, e é exatamente isso que um corpo que não desenhou produz.

**2. A figura inteira ganhou um PNG julgado**, pelas mesmas regras de quadro
dos outros:

```text
the whole figure: 640x640, 44 colour(s), the commonest covers 91.91%
```

### A prova de que agora cobre

Com o `sections_of` devolvendo `[]` na árvore:

```text
  A-A1-A-A-A, figure 0: 18 primitive(s), 18 textured, 3 surface(s), 36 triangle(s)
FAIL: the whole figure came out with primitives 18 and the floor is 100 …
FAIL: the whole figure came out with sections 1 and the floor is 2 …
exit=1
```

Antes deste conserto, a mesma árvore com o mesmo plantio saía **0**.

Controle novo `ui-whole-figure-unjudged`: as contagens lidas e **não**
julgadas. Vermelho — e este cabe no `controls.py`, ao contrário do da
CORR-LOOKS-039, porque o julgamento mora no `self_check()` e não precisa de
janela.

### Problemas encontrados

Nenhum no conserto. Vale registrar um limite que a medição mostrou: a figura
inteira cobre **91,91%** de uma cor só, contra os 95% do
`BACKGROUND_CEILING` — o boneco na prateleira ocupa pouco do quadro, então o
teto de fundo é uma guarda frouxa para ela. Quem a segura são as contagens, não
o teto; está dito aqui porque é o que alguém confundiria ao ler o gate passar.

### Arquivos criados/modificados

- `tools/looks/ui_check.py` — `WHOLE`, `_counted()`, `judge_whole()`, o PNG da
  figura inteira, o `piece` do `draw()` e as quatro asserções
- `tools/looks/controls.py` — o controle `ui-whole-figure-unjudged`
- `docs/tasks/looks/16-contratos-da-ui.md` — o contexto
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-040.md` — este arquivo
_Migrated on 2026-09-21: done_commit approximated from the last commit touching this file._
