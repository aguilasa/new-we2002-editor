---
id: CORR-LOOKS-057
title: "Correção: o docstring do `layout.PLAYER_NATION` ensina a regra `código = índice − 1` que a própria task desmentiu"
type: correção
category: dados
status: concluído
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

- [x] `grep -rn "minus one" tools/looks/layout.py` não acha a regra como
      afirmação
- [x] o docstring aponta `looks.NATION_CODES` e diz o salto
- [x] `python tools/looks/selftest.py --quiet` verde, e o controle
      `looks-nation-code-is-the-index` continua vermelho
- [x] `roms/` intocada

## Log de Execução

**Executado em:** 2026-09-17

### Resumo do que foi feito

A evidência reproduz em `b95aca7`: `grep -rn "minus one" tools/looks/` acha a
regra **como afirmação** só no `layout.py:1400`; a outra ocorrência, no
`oracle.py:3553`, já a cita como o erro a evitar. E o `looks.py` mede o
contrário — `NATION_CODES = ((1, 54, -1), (55, 79, 40))`, com `Iceland` (valor
55) guardando **95** e a linha acabando em **119**.

O docstring do `layout.PLAYER_NATION` passou a dizer o que foi medido: o byte é
um **código** de nacionalidade, o código **não** é a posição na linha, os
valores 1 a 54 guardam 0 a 53 e daí em diante o código **salta 41**; quem
precisa dele pergunta ao `looks.NATION_CODES` / `looks.nation_code`, nunca a
uma conta escrita no módulo dos endereços.

A frase velha ficou registrada na forma do ciclo — **com a data e o que ela
dizia antes** —, com o motivo de ela ter parecido certa: cinco amostras, todas
abaixo do salto, que é o problema 2 do Log da própria LOOKS-TASK-23. É por isso
que o `grep` por `minus one` ainda acha a linha 1407: ali ela é registro
datado, não regra.

Os dois parágrafos medidos — o método das duas corridas com o mesmo número de
teclas, e o `0x800E9450 + 27` — ficaram como estavam.

### Gates

```text
$ grep -rn "minus one" tools/looks/layout.py
1407:This said "it is stored as the row's index **minus one**" until 2026-09-17
                                   # registro datado; a afirmação saiu

$ grep -n "NATION_CODES\|nation_code" tools/looks/layout.py
1404:made of are `looks.NATION_CODES` and `looks.nation_code`; whoever needs the

$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/looks/controls.py --only looks-nation-code-is-the-index
  RED    looks-nation-code-is-the-index looks.py :: NATION_CODES
$ python tools/looks/selftest.py --quiet
  ..... 73 of 73 controls red
looks_selftest: 0 failure(s)
$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

Varredura do termo em `docs`, `tools` e `CLAUDE.md`: as outras ocorrências de
`índice − 1` são o plano, a task 23 e a própria tabela de correções **nomeando
o erro**, e as de `tools/mcr/numbers.py` e `tools/port_database.py` são de
outro assunto.

`roms/` intocada; correção de docstring, nenhum emulador subiu.

### Problemas encontrados

Nenhum.

### Arquivos criados/modificados

- `tools/looks/layout.py` — o docstring do `PLAYER_NATION`
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
