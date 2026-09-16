---
id: CORR-LOOKS-049
title: "Correção: nas cabeças que não são A1, a pele pinta só a testa e a barba não aparece — os índices emprestados da seção 24 erram"
type: correção
category: render
status: pendente
depends_on: []
---

# CORR-LOOKS-049: `COLOUR BY BORROWED INDEX` está medido errado, pelo corpus

## Problema identificado

As quatro linhas de cor (`SKIN`, `H.COL`, `H.F.COL.`, `FACE`) têm os índices de
primitiva medidos na **seção 24**, a cabeça do estilo `A1`. Desde a
[`CORR-LOOKS-034`](/docs/tasks/looks/CORR-LOOKS-034.md) eles são aplicados às
outras doze cabeças **por empréstimo**, e cada parte assim tocada sai marcada
`COLOUR BY BORROWED INDEX` — a própria correção disse que isso era suposição.

O corpus de terceiro mediu a suposição, e ela está errada. Nas cabeças que não
são `A1`, com pele diferente de `A`:

- a pele nova pinta **a testa** e o rosto fica na pele `A`;
- a barba do nome não aparece no nosso render (`C-I3-A-C-A`, `C-K1-A-E-A`).

Nomeadas, as seis piores do corpus: `D-I3-A-A-A`, `C-I3-A-C-A`, `B-I3-A-A-A`,
`C-I3-A-A-A`, `C-K1-A-E-A` e `C-O1-A-A-A`.

## Evidência

```text
$ python tools/looks/corpus.py --score <pasta>
      self-score, grouped by head and skin:
        hair style A1     skin A       9 picture(s), mean 0.721, lowest 0.660
        hair style A1     skin not A  14 picture(s), mean 0.641, lowest 0.540
        hair style not A1 skin A      12 picture(s), mean 0.697, lowest 0.544
        hair style not A1 skin not A  12 picture(s), mean 0.411, lowest 0.266
      the 6 lowest self-scores -- drawn beside ours in <raiz>\work\looks-corpus\worst.png:
        D-I3-A-A-A   own 0.266  best D-A1-A-A-A   0.553 ...
        C-I3-A-C-A   own 0.312  best C-A1-A-A-A   0.671 ...
        B-I3-A-A-A   own 0.316  best B-A1-A-A-A   0.730 ...
        C-I3-A-A-A   own 0.317  best C-A1-A-A-A   0.719 ...
        C-K1-A-E-A   own 0.344  best C-A1-A-A-A   0.609 ...
        C-O1-A-A-A   own 0.353  best C-A1-A-C-A   0.707 ...

$ python tools/looks/scene.py --tuple B-I3-A-A-A      colour borrowed    9
$ python tools/looks/scene.py --tuple B-A1-A-A-A      colour borrowed    0
```

Um efeito de **interação**: cabeça não-`A1` sozinha (0,697) e pele não-`A`
sozinha (0,641) custam pouco; as duas juntas derrubam a média para **0,411**.
É o desenho de um erro de índice — pele certa em primitiva errada —, não de
pose nem de câmera, que custariam o mesmo nos quatro grupos. A tira
`worst.png` foi olhada: o JPEG tem o rosto inteiro na pele do nome, o nosso tem
só a faixa de cima.

## Causa raiz

Os índices `layout.SKIN_COLOUR_PRIMITIVES`, `HAIR_COLOUR_PRIMITIVES` e
`FACE_PRIMITIVES` são posições **dentro da seção 24**. As outras cabeças não
têm o mesmo número de primitivas (a 34 desenha 23, a 24 desenha 18), e a mesma
posição cai em outra parte da malha.

## Correção

### Arquivo: `tools/looks/layout.py` e `tools/looks/assembly.py`

Medir, por cabeça, quais primitivas cada linha de cor move — a irmã do
`oracle.py --writes HAIR`, que nomeou os quads de cabelo das quatro cabeças do
`HAIR_QUADS`: um breakpoint de escrita no CLUT id enquanto a linha é andada, em
cada uma das treze. Enquanto uma cabeça não tiver os índices dela, as linhas de
cor nela **recusam** em vez de pintar por empréstimo — a mesma escolha do
`head_of` para os três estilos não medidos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | os índices de cor por cabeça, com a medição ao lado |
| `tools/looks/assembly.py` | usar os da cabeça; recusar onde faltarem |
| `tools/looks/controls.py` | controle que volte ao empréstimo |

## Verificação

- [ ] `corpus.py --score` **verde sem o resíduo** `(False, False)` em
      `corpus.GROUP_RESIDUES` — o gate da
      [`CORR-LOOKS-050`](/docs/tasks/looks/CORR-LOOKS-050.md): com o conserto o
      grupo deixa de ser outlier, e o resíduo tem de sair (ele mesmo fica
      vermelho se sobrar); se as tuplas do grupo saírem como recusa, o grupo
      some do corpus e o resíduo sai pelo mesmo motivo
- [ ] `scene.py --tuple B-I3-A-A-A` sem `colour borrowed`
- [ ] controle negativo vermelho

## Log de Execução

*(preencher ao executar)*
