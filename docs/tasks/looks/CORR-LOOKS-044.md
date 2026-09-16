---
id: CORR-LOOKS-044
title: "Correção: a tabela diz que a tela da barba alcança cinco valores, e a tela alcança sete"
type: correção
category: montagem
status: concluído
depends_on: []
---

# CORR-LOOKS-044: `FACE` com `reach` 5 recusa `F` e `G`, que a tela oferece

## Problema identificado

`assembly.Effect` define `reach` como "quantos valores a **TELA** oferece,
andada de ponta a ponta", e dá **5** para o `FACE` ("bands 0 to 4, and then it
clamps"). Por isso o `edits()` recusa `F` e `G` — dezesseis dos cinquenta renders
do corpus caem nessa recusa.

Andada de ponta a ponta nos **dois** slots, a tela vai de `A` a **`G`**: sete
valores. O que a LOOKS-TASK-14 mediu como 5 é o alcance da **faixa** no `v` dos
dois quads de barba da seção 24 — e isso não é o alcance da tela. `F` e `G`
fazem alguma coisa que não é mover aquela faixa.

## Evidência

```text
$ python tools/looks/confront.py --reach FACE
  FACE on slot 2: 530 glyph pixel(s) at rest, still with nothing pressed; 6 Right(s)
      changed the label, so the screen reaches 7 of the 8 value(s) the field holds
  FACE on slot 1: 530 glyph pixel(s) at rest, still with nothing pressed; 6 Right(s)
      changed the label, so the screen reaches 7 of the 8 value(s) the field holds
```

Os quadros `work/looks-shots/reach-{1,2}-FACE-{1..7}.png` mostram `BTYPE` a
`GTYPE` e depois `GTYPE` de novo, com a seta direita sumindo na ponta. A contagem
por máscara de glifo tem controle ocioso (duas capturas sem tecla, mesma
máscara) e controle negativo (`confront-mask-sees-blink`).

A primeira versão dessa contagem, por diferença crua da célula, deu **8** no
slot 2: a caixa do cursor pisca, e a seta de fim de curso fica dentro da caixa
do `oracle.row_value`. É a mesma família da armadilha 19 do perfil.

## Causa raiz

Armadilha 19 outra vez, do outro lado: o alcance foi medido observando **uma**
coisa (a faixa na seção 24) e escrito como alcance da tela.

## Correção

### Arquivo: `tools/looks/assembly.py`

1. `reach` do `FACE` passa a 7 **ou** o campo ganha dois números — o que a tela
   oferece e o que a tabela sabe aplicar —, com a recusa de `F`/`G` dizendo
   "a tela oferece, e não foi medido o que faz", em vez de "a tela não alcança";
2. medir o que `F` e `G` escrevem (`oracle.py --patched FACE`, os dois slots) —
   pode ser outra seção, como o `HAIR` era.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/assembly.py` | modificar |
| `docs/PLAN-LOOKS-PY.md` | a definição de pronto, item 3, cita o alcance 5 |
| `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` | a leitura das 16 recusas |

## Verificação

- [x] a mensagem de recusa de `F` e `G` não afirma mais que a tela não chega lá
- *alternativa à linha acima, não tomada:* `F` e `G` desenhando, com o que
  escrevem medido — é a segunda metade, pede o emulador, e está no Log
- [x] `scene.py --corpus` remedido e o número novo escrito onde o velho estava

## Log de Execução

**Executado em:** 2026-09-16

### Resumo do que foi feito

A evidência reproduziu no emulador, andando a linha nos dois slots:

```text
$ python tools/looks/confront.py --reach FACE
  FACE on slot 2: 530 glyph pixel(s) at rest, still with nothing pressed; 6 Right(s)
      changed the label, so the screen reaches 7 of the 8 value(s) the field holds
  FACE on slot 1: idem, 7 of 8
```

**Feita a metade 1 da correção:** o `Effect` ganhou dois números. `reach` é o
que a **tela** oferece e passou a **7** para o `FACE`; `known` é o que a
**tabela** sabe aplicar e ficou em **5** — as faixas 0 a 4 dos dois quads de
barba. A recusa se partiu em duas, e cada uma diz o que é:

```text
FACE=F is value 5: the screen offers it -- it reaches 7 -- and what it writes
was not measured; this table knows 5 -- …
```

e um valor além da tela — o oitavo que os bits guardam e ninguém rotulou —
continua saindo como `… the screen was measured to reach 7`.

A varredura da CORR-LOOKS-038 sobre as faixas do `FACE` passou a andar o
`known`, porque são as faixas **medidas**; andar o `reach` pediria as faixas 5
e 6, que não são faixas de barba.

`scene.py --corpus` remedido: **31 desenhadas, 19 recusadas**, as mesmas 16 por
barba, agora com a razão nova. O número não muda — o que mudou é o que a
recusa afirma.

### A metade 2 não foi feita, e não por esquecimento

Medir o que `F` e `G` escrevem é `oracle.py --patched FACE` nos dois slots,
irmã da corrida que achou o `HAIR_MAP`. Não é leitura: é andar a linha no
emulador lendo o arquivo inteiro depois de cada tecla, e o resultado pode ser
outra seção. Fica aberta, escrita onde as 16 recusas são lidas — a
[`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md) — como
o que as destrava.

### Problemas encontrados

A mesma afirmação "a tela alcança cinco" estava também na tabela da §6(c) do
plano, corrigida aqui, e nos Logs das LOOKS-TASK-14 e 15, que são tasks
fechadas — anotadas em commit próprio.

Controle novo `assembly-unmeasured-as-unreached`: o valor que a tela oferece e
ninguém mediu aplicado assim mesmo. Vermelho.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — `Effect.known`, o `FACE` com 7/5, as duas
  recusas e as asserções
- `tools/looks/scene.py` — a varredura de faixas anda o `known`
- `tools/looks/controls.py` — `assembly-unmeasured-as-unreached`
- `tools/looks/ui_check.py` — a docstring do `REFUSED`
- `docs/PLAN-LOOKS-PY.md` — Definição de pronto, item 3, e a tabela da §6(c)
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — a leitura das 16
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-044.md` — este arquivo

*(preencher ao executar)*
