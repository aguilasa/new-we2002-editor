---
id: CORR-LOOKS-020
title: "Correção: quatro seções têm DOIS parceiros de espelho, e o `mirrors()` fica com o primeiro sem dizer que havia escolha"
type: correção
category: engenharia-reversa
status: concluído
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

- [x] `mirrors()` pareia dentro da lista, e `pieces.py --check-image` continua
      dando os mesmos onze nomes por boneco
- [x] ambiguidade que sobre é **recusada** com `BadPieces`, nomeando os
      candidatos
- [x] o `self_check()` tem o caso sintético de dois candidatos e roda sem disco
- [x] há controle novo — `pieces-mirror-unconfined` —, e o `selftest` conta
      **16 de 16** vermelhos
- [x] `python tools/looks/pieces.py --check` e `--check-image` verdes
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-15

### Resumo do que foi feito

O `mirrors()` deixou de parar no primeiro parceiro que serve. A busca virou
duas peças: `mirror_candidates()`, que devolve **todos** os espelhos de cada
seção, e o `mirrors()`, que filtra por **lista do cabeçalho** — par de espelho é
esquerda e direita *da mesma figura* — e **recusa** com `BadPieces` se ainda
sobrar mais de um, nomeando os candidatos. Escolher em silêncio era o defeito;
o conserto não troca a escolha por outra, tira a escolha.

O `name_pieces()` passou a ler as listas **antes** de parear, que é a ordem que
a regra exige. As seções que as duas listas compartilham — 9 e 10, os pés —
continuam parceiras uma da outra, porque estão juntas nos dois grupos.

E o `report()` diz o que antes não aparecia em lugar nenhum:

```text
  also mirrored across the two lists: 7~[19], 8~[18], 18~[8], 19~[7]
      the two figures carry the same shin mesh, so the pairing is confined to
      one list on purpose
```

### A evidência, reproduzida antes

```text
  section  7 has 2 mirror candidates: [(8, 'z'), (19, 'z')]
  section  8 has 2 mirror candidates: [(7, 'z'), (18, 'z')]
  section 18 has 2 mirror candidates: [(8, 'z'), (19, 'z')]
  section 19 has 2 mirror candidates: [(7, 'z'), (18, 'z')]
identical vertex sets (no negation): [(7, 18), (8, 19)]
mirrors() on file order:            {7: 8, 8: 7, 18: 19, 19: 18}   <- certo
mirrors() on order 7,19,8,18,...:   {7: 19, 19: 7, 8: 18, 18: 8}   <- cruza
```

A terceira linha é o mesmo arquivo, a mesma função e as mesmas seções, só
chegando noutra ordem. Depois do conserto, as duas ordens dão a mesma resposta,
e é isso que o caso sintético afirma.

### O caso vermelho, que roda sem disco

Duas cópias de um par espelhado — quatro seções, dois candidatos cada, que é a
forma do arquivo real em miniatura. Os três negativos que já existiam
(translação, comprimento diferente, eixo errado) não dizem nada sobre **duas
respostas certas**, que é o caso que este arquivo tem. Quatro asserções novas:

- cada uma das quatro tem exatamente dois candidatos;
- sem grupos, o pareamento **recusa** em vez de escolher;
- confinado às listas, cada cópia pareia dentro de si;
- e **a resposta não depende da ordem em que as seções chegam** — a mesma
  armadilha, montada como `7, 19, 8, 18`.

O controle `pieces-mirror-unconfined` planta o defeito de volta: com o filtro
de lista aberto (`if True`), o `pieces` fica vermelho.

### Problemas encontrados

Um erro meu na montagem do caso sintético, pego pelo próprio caso: a primeira
versão da ordem embaralhada punha as duas malhas iguais no mesmo grupo, de modo
que nenhuma seção tinha parceiro elegível e o pareamento saía vazio — verde por
não medir, exatamente o que este ciclo persegue. A ordem certa é a do arquivo:
`7` e `18` são a mesma malha, `8` e `19` são o espelho dela, e as listas são
`{7, 8}` e `{18, 19}`.

### Arquivos criados/modificados

- `tools/looks/pieces.py` — `mirror_candidates()`, `_together()`, o `mirrors()`
  confinado e recusador, o `name_pieces()` lendo as listas primeiro, a linha do
  `report()`, e os casos vermelhos novos no `self_check()`
- `tools/looks/controls.py` — o controle `pieces-mirror-unconfined`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
- `docs/tasks/looks/CORR-LOOKS-020.md` — este arquivo
