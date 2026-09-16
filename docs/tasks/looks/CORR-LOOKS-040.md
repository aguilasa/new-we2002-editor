---
id: CORR-LOOKS-040
title: "Correção: o `looks_ui` só julga a cabeça, e passa com a figura inteira apagada"
type: correção
category: verificação
status: pendente
depends_on: []
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

- [ ] `python tools/looks/ui_check.py` verde, julgando também a figura inteira
- [ ] o mesmo gate fica **vermelho** com `sections_of` devolvendo `[]`
- [ ] as contagens do `--smoke` entram numa asserção, não só na impressão
- [ ] `python tools/looks/selftest.py --quiet` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
