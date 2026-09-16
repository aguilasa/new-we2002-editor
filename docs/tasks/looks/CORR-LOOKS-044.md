---
id: CORR-LOOKS-044
title: "Correção: a tabela diz que a tela da barba alcança cinco valores, e a tela alcança sete"
type: correção
category: montagem
status: pendente
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

- [ ] a mensagem de recusa de `F` e `G` não afirma mais que a tela não chega lá
- [ ] ou `F` e `G` desenham, com o que escrevem medido
- [ ] `scene.py --corpus` remedido e o número novo escrito onde o velho estava

## Log de Execução

*(preencher ao executar)*
