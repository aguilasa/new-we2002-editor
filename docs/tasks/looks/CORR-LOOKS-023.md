---
id: CORR-LOOKS-023
title: "Correção: \"nenhuma outra peça toca a paleta das chuteiras\" é conferido só no `EDT_MOD.BIN`, e seis seções do `MODEL.BIN` a amostram"
type: correção
category: textura
status: pendente
depends_on: []
---

# CORR-LOOKS-023: a exclusividade da paleta de chuteira é medida em metade do modelo

## Problema identificado

O rótulo "Botines" do CARP foi confirmado por exclusividade, e é o argumento
certo — o `pieces.py` já sabia que as seções 9 e 10 são o **pé**, então a paleta
que só elas amostram é a da chuteira. O `texture.py --check-image` imprime:

```text
CARP's "Botines": 67940 -- the only palette the foot section(s) sample,
  at vram (0,484), and no other piece touches it
```

A segunda metade da frase é conferida **só dentro do `EDT_MOD.BIN`**. Medido: a
paleta em (0, 484) é amostrada também por **seis seções do `MODEL.BIN`** — 11,
12, 22, 23, 63 e 64 —, cinco primitivas cada, trinta no total. O próprio
relatório da ferramenta diz, duas linhas acima, que aquele id de CLUT aparece
**142** vezes na geometria; as seções 9 e 10 respondem por **112**. As outras
trinta não estão em nenhum lugar da conta.

Por que isso não é implicância: o `MODEL.BIN` é de onde vem a **cabeça**, e é o
arquivo que a [`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)
e a [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md) vão ler em
seguida. Quem ler "a paleta da chuteira, e nenhuma outra peça a toca" e depois
encontrar seis seções do `MODEL.BIN` amostrando-a vai suspeitar **da leitura do
CLUT**, que é justamente o que a [`CORR-LOOKS-018`](/docs/tasks/looks/CORR-LOOKS-018.md)
acabou de endireitar — e não da fronteira da frase.

E a frase é fácil de endireitar sem perder força: a exclusividade **entre as
peças nomeadas** continua valendo e continua confirmando o rótulo. O que falta é
dizer o alcance, e que trinta primitivas de fora dele compartilham a paleta —
que é um achado pequeno e útil por si, porque aponta quais seções do `MODEL.BIN`
olhar quando a Fase 3 for nomeá-las (luva, meião, o que for).

**A cabeça não está entre elas**, e isso vale registrar junto: a `MODEL.BIN`
seção 24 amostra `(16, 480)` em dezesseis primitivas e `(144, 480)` em duas — as
duas linhas de paleta que o Log já nomeia como as da cabeça — e nunca (0, 484).

## Evidência

Medido nesta revisão, sobre o disco japonês, com o `section.py` commitado:

```text
  section  9: {(0, 484): 56}
  section 10: {(0, 484): 56}
  other EDT_MOD.BIN sections sampling (0,484): none
  MODEL.BIN sections sampling (0,484): {11: 5, 12: 5, 22: 5, 23: 5, 63: 5, 64: 5}
  MODEL.BIN section 24 (head) cluts: {(16, 480): 16, (144, 480): 2}
```

E a linha do próprio relatório, que fecha a conta pelo outro lado:

```text
      vram (0,484)     4 bpp  x142   <- 256 entries at 67940
```

`112 + 30 = 142`. A parte do `EDT_MOD.BIN` reproduz exatamente o que o Log
afirma; o que não está dito é de onde vêm os trinta que faltam.

## Causa raiz

A exclusividade é calculada sobre as peças que o `pieces.name_pieces()` conhece,
que são as do `EDT_MOD.BIN` mais a cabeça, e a frase impressa não diz esse
alcance.

## Correção

### Arquivo: `tools/looks/texture.py`

A linha do "Botines" passa a dizer o alcance e o resto: *"the only palette the
foot sections sample, and no other **named piece** touches it; N primitives in
`MODEL.BIN` sections ... share it"* — com os números vindos da varredura, nunca
escritos. Se a conta for barata (e é: as duas varreduras de seção já estão
feitas no mesmo comando), vale imprimir, para **cada** id de CLUT que resolve
neste arquivo, quantas primitivas de cada arquivo o pedem — hoje o relatório dá
o total e a resolução, e é a soma por arquivo que teria mostrado isto sozinha.

### Arquivo: `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md`

O item "Botines" com o alcance da afirmação, e as seis seções nomeadas como
pergunta aberta encaminhada à Fase 3 — não como problema.

### Arquivo: `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md`

Ela já recebeu desta task as paletas lidas e os quatro ids de fora do arquivo.
Ganha a linha das seis seções do `MODEL.BIN` que compartilham a paleta da
chuteira: são candidatas nomeáveis pelo mesmo método que nomeou as onze peças.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/texture.py` | modificar |
| `docs/tasks/looks/10-lista-de-cluts-do-dat2d.md` | modificar |
| `docs/tasks/looks/11-qual-imagem-e-o-cabelo.md` | modificar |

## Verificação

- [ ] a linha do "Botines" diz **entre as peças nomeadas**, e diz quantas
      primitivas de fora compartilham a paleta
- [ ] o relatório soma cada id de CLUT **por arquivo**, e `112 + 30 = 142` fecha
      na saída
- [ ] as seis seções do `MODEL.BIN` estão nomeadas na LOOKS-TASK-11 como
      candidatas
- [ ] `python tools/looks/texture.py --check-image` continua `ok`
- [ ] `python tools/looks/selftest.py` verde
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
