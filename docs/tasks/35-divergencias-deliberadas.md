---
id: WTE-TASK-35
title: "Registro das divergências deliberadas"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-34"]
status: pendente
---

# WTE-TASK-35: Divergências deliberadas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 2 e §0.

> **"100%" aqui significa: todo handler com veredito escrito e toda gravação
> byte-idêntica.** Não significa que nenhuma divergência é aceita — significa
> que nenhuma é *desconhecida*.

O precedente é o `newWe2002`, cujo escopo Linux fechou com **uma** divergência
aceita: a faixa de 16 bytes em `405724..405739`, o slot 64 de um array de 63 que
o `ed.exe` lê e grava a partir de memória vizinha. Documentada, explicada,
reproduzida no golden test como exceção nomeada.

**Diferença de política em relação ao `newWe2002`:** lá o objetivo era clonar o
`ed.exe` inclusive nos defeitos. Aqui o plano (§0) permite **não** reproduzir bug
do original — mas exige registro.

---

## Objetivo

Um documento no formato que o
[`PARIDADE-FUNCIONAL.md`](/docs/PARIDADE-FUNCIONAL.md) já usa: o que diverge, por
quê, e que evidência sustenta.

### Cada entrada precisa de

| Campo | Por quê |
|---|---|
| o que diverge | a operação e os bytes, ou o comportamento visível |
| natureza | bug do original, limitação de plataforma, ou escolha |
| decisão | reproduzir, corrigir, ou não implementar |
| razão | por que essa decisão e não outra |
| evidência | o diff, a captura, ou o teste que mostra |
| onde o teste sabe | se a bateria golden precisa de exceção nomeada |

O último campo é o que evita divergência documentada virar divergência
silenciosa: uma exceção no golden sem entrada aqui é buraco.

### Candidatas já conhecidas antes de a task rodar

- **Sufixo ` [Lazarus]` no `Caption` dos 18**
  ([WTE-TASK-11](/docs/tasks/11-app-com-a-casca-completa.md)) — **já está no
  código**, diferente das outras quatro, que são hipóteses.
  *Natureza:* escolha. *Decisão:* manter.
  *Razão:* o `Caption` vem do DFM, e o do `MainForm` é literalmente
  `' W11 Team Editor PT by chagas_michel!'`; a partir da WTE-TASK-22 os dois
  editores rodam no mesmo `:99` e o harness acha janela por título e por
  tamanho — título igual faria ele dirigir o lado errado (armadilha 6 do
  [`progresso.md`](/docs/tasks/progresso.md)).
  *Evidência:* posto em tempo de execução por `MarcaOsTitulos`, em
  `wte/src/wtemain.pas`, não no `.lfm`, que é gerado.
  *Onde o teste sabe:* no `:99` não há window manager, nenhuma barra de título
  é desenhada, e a captura da
  [WTE-TASK-12](/docs/tasks/12-comparacao-visual.md) não enxerga o sufixo —
  num desktop de verdade enxerga, e deve.
- **Tolerância de cor do render 2D** (WTE-TASK-32), se a igualdade exata não
  sair.
- **Cinco glifos que não acinzentam** — medido pela
  [CORR-WTE-060](/docs/tasks/CORR-WTE-060.md) em 2026-08-18, e **já está no
  código**, como o sufixo acima: não é hipótese, é comportamento em produção.
  *Natureza:* limitação de plataforma (widgetset), não bug do original nem do
  port. *Decisão:* não reproduzir.
  *Razão:* a LCL desenha o glifo de um botão desabilitado aplicando
  `gdeDisabled`, que é **conversão para tons de cinza**; pixel com `R = G = B`
  é ponto fixo dela. Glifo desenhado só com preto e branco puros sobre a cor
  transparente é portanto **invariante**, e o botão apaga logicamente sem mudar
  um pixel. O `comctl32` do Win32 não faz grayscale — monta o glifo
  desabilitado de uma máscara monocromática, em que preto vira sombra
  (`#A6A6A6`) e branco vira transparente. Igualar exigiria desenhar à mão um
  segundo glifo (`NumGlyphs = 2`) que **não existe no recurso do original**, ou
  reescrever o `TButtonGlyph` da LCL.
  *Evidência:* `iguala_nombres` muda **518 px** no oráculo sob Wine e **0** no
  port (`compara_tela.sh --habilitacao`, recorte `(344,184,73,25)`). As duas
  hipóteses anteriores — cor transparente e `ParentFont` — foram **refutadas**
  num harness LCL isolado: `ParentFont := True` continua dando 0 px, e recolorir
  o glifo do vizinho para a mesma cor de fundo dá 513 px, não 0. A regra é o
  grayscale, e o número fecha dos dois lados: `boton_nombres2iso` tem **280
  pixels não-cinza** no glifo e muda **280 px** no app rodando. Detalhe em
  [`MainForm.iguala_nombresClick`](../../wte/re/spec/MainForm.iguala_nombresClick.md).
  *Onde o teste sabe:*
  [`check_glifos_disabled.py`](../../wte/tools/check_glifos_disabled.py) varre
  os **59** botões com glifo dos 18 formulários e declara os **5** invariantes —
  `iguala_nombres`, `parriba`, `pabajo` (`MainForm`), `oscurecer` e `aclarar`
  (`color`). Glifo que entre ou saia desse conjunto derruba o
  `make -C wte check`. O `compara_tela.py` precisa da mesma exceção nomeada
  quando os cinco forem exercitados — hoje só o `iguala_nombres` cai na faixa
  medida, e ele aparece lá como `DIVERGE`.
- **`TStaticText` no GTK2** (§8.9), se o fundo não puder ficar idêntico.
- **Rótulos cortados por fonte substituta** — acontece nos dois lados, e talvez
  não conte como divergência; decidir.
- **Comportamento de truncamento de campo** (WTE-TASK-36), se o Pascal não
  reproduzir o do buffer fixo.

### O que não entra aqui

Divergência **não** deliberada. Se algo diverge e ninguém sabe por quê, isso é
bug aberto, não entrada neste documento. Confundir os dois é como uma lista de
problemas conhecidos vira desculpa.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/divergencias.md` | criar |
| `wte/tools/golden_suite.sh` | modificar — exceções nomeadas |

---

## Critério de conclusão

- [ ] Toda divergência da bateria com entrada completa
- [ ] Toda exceção do golden com entrada correspondente
- [ ] Divergência sem causa conhecida classificada como bug aberto, não como deliberada
- [ ] As quatro candidatas conhecidas decididas
- [ ] Commit no formato conventional, em inglês

## Log de Execução *(preenchido após execução)*

- **Executado em:**
- **Resumo do que foi feito:**
- **Arquivos criados/modificados:**
- **Problemas encontrados:**
