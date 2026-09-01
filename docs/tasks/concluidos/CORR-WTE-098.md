---
id: CORR-WTE-098
title: "Correção: a §5.1 do plano ainda diz que o preço não precisa de golden, e ele tem um"
type: correção
category: processo
status: concluído
depends_on: []
---

# CORR-WTE-098: a §5.1 do plano ainda diz que o preço não precisa de golden

## Problema identificado

A §5.1 do [plano](/docs/PLAN-WTE-LAZARUS.md) — a fonte de verdade — descreve a
feature de preço como um handler só e sem régua de byte:

> **5.1 Preço derivado dos atributos.** `etiqprecioClick` (`0x00408bb8`) e o
> formulário `jugador`. […] **Não precisa de golden test de imagem**, precisa
> de tabela de verdade.

Medido desde então, e por duas tasks:

- a [WTE-TASK-30](/docs/tasks/concluidos/30-handlers-auxiliares.md) achou que o
  `MainForm.base_teamClick` — a outra metade da feature — **grava** um byte por
  jogador;
- a [WTE-TASK-32](/docs/tasks/concluidos/32-preco-do-jogador.md) escreveu o
  [`golden-22-precos`](../../../wte/tests/roteiros/golden-22-precos.txt) para
  medi-lo, e o registrou como gate.

O corpo da própria task já corrige a premissa (*"a régua desta task é dupla:
tela para a fórmula, byte para o time inteiro"*), e o critério de conclusão
dela diz *"`base_teamClick` com golden verde — byte, não tela"*. **O plano não
foi varrido junto.** É o mesmo sítio que a
[CORR-WTE-085](/docs/tasks/concluidos/CORR-WTE-085.md) já teve de corrigir uma vez: a
Fase 5 do plano descreve as quatro features com o que se sabia em 2026-08-05 e
envelhece a cada task que mede.

A frase *"Pronto quando: […] tabela de preço"*, no fim da mesma seção, herda o
mesmo engano.

## Evidência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
sed -n '963,968p' docs/PLAN-WTE-LAZARUS.md
grep -n "base_teamClick" docs/PLAN-WTE-LAZARUS.md
grep -n "base_teamClick" wte/tools/check_fase4.py wte/re/fase-4-golden.tsv
```

```text
963:**5.1 Preço derivado dos atributos.** `etiqprecioClick` (`0x00408bb8`) e o
966:… **Não precisa de golden test de imagem**, precisa de tabela de verdade.
(o grep de base_teamClick no plano nao imprime nada)

wte/tools/check_fase4.py:190:    "MainForm.base_teamClick": ("golden-22-precos",),
wte/re/fase-4-golden.tsv:golden-22-precos	controle	PASSOU	83	1	2026-08-24
wte/re/fase-4-golden.tsv:golden-22-precos	golden	PASSOU	79	2	2026-08-24
```

Rodado nesta revisão, em 2026-08-24: `controle` byte-idêntico, `golden`
byte-idêntico, e `positivo --plantar 3067450` detectando o byte plantado em
`OFS_COST_NATIONAL+46`. As duas corridas boas mudaram **22 bytes** em
`3067450..3067471` dos dois lados — o gate exercita a gravação, não o caminho
de desistir.

| Sítio | O que diz | Fonte |
|---|---|---|
| `docs/PLAN-WTE-LAZARUS.md:966` | não precisa de golden | escrito em 2026-08-05 |
| `docs/tasks/concluidos/32-preco-do-jogador.md` | régua dupla; golden verde é critério | medido 2026-08-21/24 |
| `wte/re/fase-4-golden.tsv` | `golden-22-precos`, duas corridas, PASSOU | a bateria |

## Causa raiz

A §5.1 foi escrita antes de alguém ler o `base_teamClick`, e as duas tasks que
mediram a outra metade atualizaram o corpo delas e a Fase 4 do plano, não a
Fase 5.

## Correção

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`, §5.1

Três ajustes, todos de fato medido:

1. Nomear as **duas** metades: `etiqprecioClick` (`0x00408bb8`, formulário
   `jugador`) e `MainForm.base_teamClick` (`0x00410ff4`), que é a de v0.99 —
   *"calculate credits for a whole team with just one click"*.
2. Trocar *"não precisa de golden test de imagem"* por a régua ser **dupla**:
   tabela de verdade para a fórmula, e golden de **byte** para o time inteiro,
   porque ele grava. Citar o `golden-22-precos`.
3. Ajustar o *"Pronto quando"* da Fase 5 para o mesmo: tabela de preço **e** o
   golden do preço do time.

Escrever também, em uma linha, o que a task rendeu e o plano não previa: a
tabela de verdade saiu **do byte**, não da tela — cada corrida do oráculo vale
22 amostras em vez de uma. É a substituição que fez a amostra chegar a 132
jogadores.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificar |

## Verificação

- [x] `grep -n "Não precisa de golden test de imagem" docs/PLAN-WTE-LAZARUS.md` sai vazio
- [x] `grep -n "base_teamClick" docs/PLAN-WTE-LAZARUS.md` imprime a §5.1 —
      linha 965, onde antes não havia ocorrência nenhuma
- [x] `make -C wte check` verde — 764 testes, `OK (skipped=1)`, com o
      `check_fase1.py` varrendo `docs/`
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-08-24

**Resumo do que foi feito:**

Os três ajustes que a correção pedia, todos de fato medido:

1. A §5.1 nomeia as **duas** metades — `jugador.etiqprecioClick`
   (`0x00408bb8`) e `MainForm.base_teamClick` (`0x00410ff4`), a de v0.99 — e diz
   o que muda entre elas: a mesma fórmula compilada duas vezes, de onde vem a
   soma, e que a segunda **grava**;
2. *"Não precisa de golden test de imagem"* virou a régua **dupla**, com o
   `golden-22-precos` citado pelo caminho;
3. O *"Pronto quando"* da Fase 5 ganhou *"e o golden do preço do time"*.

Entrou também a linha que a correção pedia sobre o que a task rendeu e o plano
não previa: a tabela de verdade saiu **do byte**, não da tela — o preço de um
jogador só se lê por OCR e o de vinte e três se lê com `cmp` —, e é o que fez a
amostra chegar a 132 jogadores em 6 times com 100% de acerto.

**Problemas encontrados:**

1. **Nenhum.** O sítio é um só e nada mais no plano dependia da frase velha: o
   `grep` de `base_teamClick` no plano não imprimia **nada** antes desta
   correção, o que é a própria medida de quanto a §5.1 tinha envelhecido.
2. O link para o roteiro é **relativo** (`../wte/tests/roteiros/…`) e é o certo:
   a regra de `/docs/` vale para alvo dentro de `docs/`, e este está fora.

**Arquivos criados/modificados:**

| Arquivo | Ação |
|---|---|
| `docs/PLAN-WTE-LAZARUS.md` | modificado — §5.1 e o *Pronto quando* da Fase 5 |
