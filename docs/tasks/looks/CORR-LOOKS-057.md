---
id: CORR-LOOKS-057
title: "Correção: o docstring do `layout.PLAYER_NATION` ensina a regra `código = índice − 1` que a própria task desmentiu"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-LOOKS-057: a regra errada sobrevive no módulo dos endereços

## Problema identificado

A [`LOOKS-TASK-23`](/docs/tasks/looks/23-default-por-nacionalidade.md) mediu
que o código de nacionalidade **não** é a posição na linha `NAT`: os valores 1
a 54 guardam 0 a 53 e o código então **salta 41** — `Iceland`, valor 55, guarda
95; `Algeria`, valor 65, guarda 105; a linha acaba em 119. O achado está em
`looks.NATION_CODES`, no veredito da §10.3 (r), na armadilha 41 do perfil, e
tem controle plantado que fica vermelho exatamente quando alguém escreve a
regra ingênua (`looks-nation-code-is-the-index`).

**O docstring do endereço, que é o que se lê ao usar a constante, continua
ensinando a regra derrubada:**

```text
tools/looks/layout.py:1395
PLAYER_NATION = (0x800E7E0C, 0x800E946B)
"""The byte the `NAT` row of LOOKS SET writes: the player's nationality.

Not one of the twelve, which is the point ...  It is stored as the row's index
**minus one**, so the first nation the row offers, `Ireland`, is 0.
```

A frase é verdadeira para os 54 primeiros valores e falsa para os 25 seguintes
— e é a mesma inferência de cinco amostras que a execução registrou como
problema 2 do próprio Log ("cinco amostras concordaram com uma regra errada").
O `layout.py` é o **único módulo autorizado a carregar endereço** e o primeiro
lugar em que se lê o que um endereço guarda; quem usar `PLAYER_NATION` a partir
dele escreve `índice − 1` e erra 25 das 79 nações, sem sintoma — o byte é
plausível em qualquer valor.

## Evidência

A regra do módulo, contra a do `looks.py`, na árvore de `f7f9ecc`:

```text
$ python -c "... import looks; print(looks.NATION_CODES)"
((1, 54, -1), (55, 79, 40))

$ ... looks.nation_code(55), looks.nation_code(65), max
Iceland  -> 95      Algeria -> 105      último valor -> 119

$ grep -rn "index \*\*minus one\*\*" tools/looks/
tools/looks/layout.py:1399
```

É a única sobrevivência da regra na árvore. O `oracle.py` já a cita **como o
erro a evitar**:

```text
tools/looks/oracle.py:3553
        # been taken for "the code is the index minus one" -- which is what
```

E o controle plantado mede o contrário do que o docstring afirma:

```text
tools/looks/controls.py:684
        "looks-nation-code-is-the-index", "looks.py", "NATION_CODES",
        "NATION_CODES = ((1, 54, -1), (55, 79, 40))",
        "NATION_CODES = ((1, 79, -1),)",
```

## Causa raiz

O docstring foi escrito quando o endereço foi achado, com as primeiras cinco
amostras, e a correção que veio depois entrou no `looks.py` e nos documentos,
não nele.

## Correção

### Arquivo: `tools/looks/layout.py`

Trocar a frase por o que foi medido, apontando para onde a regra mora — algo
como: *o byte é o código de nacionalidade, e ele **não** é a posição na linha;
os valores 1 a 54 guardam 0 a 53 e o código salta 41 daí em diante
(`looks.NATION_CODES`, `looks.nation_code`)* —, com a data e o que a frase
dizia antes, como o resto do ciclo faz.

O parágrafo do método (as duas corridas com o mesmo número de teclas) e o do
`0x800E9450 + 27` ficam: os dois estão medidos.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |

## Verificação

- [ ] `grep -rn "minus one" tools/looks/layout.py` não acha a regra como
      afirmação
- [ ] o docstring aponta `looks.NATION_CODES` e diz o salto
- [ ] `python tools/looks/selftest.py --quiet` verde, e o controle
      `looks-nation-code-is-the-index` continua vermelho
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
