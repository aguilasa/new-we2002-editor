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

- **Tolerância de cor do render 2D** (WTE-TASK-32), se a igualdade exata não
  sair.
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
