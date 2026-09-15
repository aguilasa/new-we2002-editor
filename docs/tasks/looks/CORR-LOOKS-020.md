---
id: CORR-LOOKS-020
title: "Correção: quatro seções têm DOIS parceiros de espelho, e o `mirrors()` fica com o primeiro sem dizer que havia escolha"
type: correção
category: engenharia-reversa
status: pendente
depends_on: []
---

# CORR-LOOKS-020: o pareamento resolve uma ambiguidade que não sabe que tem

## Problema identificado

O primeiro dos cinco argumentos da task é o espelho, e **todos os outros quatro
dependem dele**: o `limbs()` corta a cadeia por onde o *lado* troca, e o lado
vem do pareamento. O `mirrors()` é quem o produz:

```python
def mirrors(sections):
    """index -> (partner index, axis), for every section that has one."""
    found = {}
    for i, one in enumerate(sections):
        if i in found:
            continue
        for j in range(i + 1, len(sections)):
            if j in found:
                continue
            axis = mirror_axis(one, sections[j])
            if axis is not None:
                found[i] = (j, axis)
                found[j] = (i, axis)
                break
    return found
```

O `break` assume que o parceiro é **único**. Neste arquivo ele não é: as pernas
dos dois bonecos têm **o mesmo conjunto de vértices**, então a perna esquerda do
jogador de linha é espelho tanto da perna direita dele quanto da perna direita
do goleiro. Medido: **quatro seções com dois candidatos cada**.

O resultado de hoje está **certo**, e por um motivo que não é regra nenhuma: 8
vem antes de 19 na varredura, e 19 aparece logo depois de 18. Trocada a ordem em
que as seções chegam à função, o pareamento passa a cruzar os dois bonecos — e
nada na saída diz que houve escolha. É a armadilha das oito listas de nome de
time do PES2 (§6.1 do [`/docs/PLAN-PES2-PSX.md`](/docs/PLAN-PES2-PSX.md)) na
mesma forma: casar por índice dá resultado plausível, e o plausível não é
conferível depois de escrito.

**A regra que falta é barata e já está medida:** par de espelho é par **dentro
da mesma lista do cabeçalho** — é a definição de esquerda e direita *do mesmo
boneco*. As listas já estão lidas pelo `modelfile.read_models()` e o
`name_pieces()` já as usa para tudo o mais.

E não há caso vermelho para isso. Os três casos negativos do `mirror_axis()`
cobrem translação, comprimento diferente e eixo errado; nenhum cobre **duas
respostas certas**, que é o caso que este arquivo tem de verdade.

## Evidência

Remedido nesta revisão, chamando o `pieces.mirror_axis()` commitado para todos
os pares de seções do `EDT_MOD.BIN`:

```text
  section  7 has 2 mirror candidates: [(8, 'z'), (19, 'z')]
  section  8 has 2 mirror candidates: [(7, 'z'), (18, 'z')]
  section 18 has 2 mirror candidates: [(8, 'z'), (19, 'z')]
  section 19 has 2 mirror candidates: [(7, 'z'), (18, 'z')]
```

A causa está um nível abaixo, e também foi medida: as seções 7 e 18 têm
**conjunto de vértices idêntico**, sem espelho nenhum, e o mesmo vale para 8 e
19 — são a mesma malha de perna nos dois bonecos, guardada duas vezes.

```text
identical vertex sets (no negation): [(7, 18), (8, 19)]
   7 vs 18: 240 of 1168 byte(s) differ -- todos em u, v e CLUT, nenhum em vértice
```

O pareamento de hoje, e o que a ordem decide:

```text
mirrors() on file order:            {7: 8, 8: 7, 18: 19, 19: 18}    <- certo
mirrors() on reversed order:        {7: 8, 8: 7, 18: 19, 19: 18}    <- certo
mirrors() on order 7,19,8,18,...:   {7: 19, 19: 7, 8: 18, 18: 8}    <- cruza os bonecos
```

A terceira linha é o mesmo arquivo, a mesma função e as mesmas seções — só
chegando noutra ordem. Com ela, a perna esquerda do jogador de linha vira o
espelho da perna direita **do goleiro**, o `limbs()` corta a cadeia noutro
lugar, e os nomes saem de um pareamento que atravessa dois modelos **sem uma
linha de aviso**.

## Causa raiz

O `mirrors()` para no primeiro parceiro que serve, e neste arquivo há seções com
dois — porque os dois bonecos têm a mesma malha de perna.

## Correção

### Arquivo: `tools/looks/pieces.py`

1. **Parear dentro da lista**, que é o que a semântica pede: o `mirrors()`
   recebe a que lista cada seção pertence (já disponível pelo
   `modelfile.read_models()`, como o `name_pieces()` faz) e só considera
   candidato da **mesma** lista. As seções que as duas listas compartilham — 9 e
   10 — continuam parceiras uma da outra, e o caso é o mesmo nos dois lados.
2. **Recusar em vez de escolher** quando sobrar ambiguidade depois disso:
   `BadPieces`, dizendo quais são os candidatos. Escolher em silêncio é o que
   esta CORR existe para tirar.
3. **Dizer que havia dois.** O `report()` já imprime `mirror` por peça; ao lado,
   quando a seção tem mais de um candidato **fora** da lista dela, vale a
   observação — é o fato interessante sobre este arquivo (a perna é a mesma nos
   dois bonecos) e hoje ele não aparece em lugar nenhum.

### Caso vermelho

O catálogo ganha um controle no feitio dos três da task: trocar o `break` por
uma varredura que colete **todos** os candidatos e fique com o último, ou
alimentar o `mirrors()` com as seções na ordem `7, 19, 8, 18` — as duas formas
têm de deixar o `pieces` vermelho. E o `self_check()`, que roda sem disco, ganha
o caso sintético: duas cópias de um par espelhado, quatro seções, dois
candidatos por seção, e a asserção de que o pareamento sai **dentro** de cada
cópia ou é recusado.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/pieces.py` | modificar |
| `tools/looks/controls.py` | modificar |

## Verificação

- [ ] `mirrors()` pareia dentro da lista, e `pieces.py --check-image` continua
      dando os mesmos onze nomes por boneco
- [ ] ambiguidade que sobre é **recusada** com `BadPieces`, nomeando os
      candidatos
- [ ] o `self_check()` tem o caso sintético de dois candidatos e roda sem disco
- [ ] há controle novo, e o `selftest` conta um controle a mais, todos vermelhos
- [ ] `python tools/looks/pieces.py --check` e `--check-image` verdes
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
