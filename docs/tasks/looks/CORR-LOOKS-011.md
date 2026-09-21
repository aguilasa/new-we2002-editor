---
id: CORR-LOOKS-011
title: "Correção: o `sweep_addresses()` guarda duas regex mortas com o nome das vivas"
type: correção
category: verificação
status: done
depends_on: []
origin: LOOKS-TASK-04
severity: low
done_on: 2026-09-14
done_commit: 3e223d2
---

# CORR-LOOKS-011: o `sweep_addresses()` guarda duas regex mortas com o nome das vivas

## Problema identificado

A task trocou o varredor de aspas por `tokenize`, e a troca deixou para trás as
duas regex do jeito antigo — compiladas no topo do `sweep_addresses()` e **nunca
usadas**:

```python
def sweep_addresses(root=None, stats=None):
    ...
    hex_literal = re.compile(r"0[xX][0-9a-fA-F]+")          # morta
    big_decimal = re.compile(r"(?<![\w.])\d{4,}(?![\w.])")  # morta
    findings = []
```

As que decidem estão no `_address_lines()`, com **os mesmos dois nomes** e
padrões diferentes — ancorados, porque ali o candidato já é um token inteiro:

```python
def _address_lines(source, path):
    hex_literal = re.compile(r"\A0[xX][0-9a-fA-F]+\Z")      # viva
    big_decimal = re.compile(r"\A\d{4,}\Z")                 # viva
```

Não é sujeira apenas: é uma **armadilha de manutenção** no arquivo que o perfil
lista como quente. Quem for afrouxar ou apertar o que conta como endereço —
aceitar `0o755`, exigir cinco dígitos, isentar um sufixo — vai achar as regex
lendo a função que tem o nome do comando, editar as de cima e não mudar
comportamento nenhum. O gate continua verde, a mudança não vale, e a explicação
não está em lugar nenhum.

É a menor das discrepâncias desta revisão, e a mais barata de fechar.

## Evidência

```
$ awk '/^def sweep_addresses/,/^def _address_lines/' tools/looks/layout.py \
    | grep -n "hex_literal\|big_decimal"
39:    hex_literal = re.compile(r"0[xX][0-9a-fA-F]+")
40:    big_decimal = re.compile(r"(?<![\w.])\d{4,}(?![\w.])")
```

Duas atribuições, nenhuma leitura — o corpo da função chama `_address_lines()` e
compara contra o conjunto `exempt`, e nada mais.

Que a varredura funciona apesar disso, esta revisão mediu: `layout.py --sweep`
dá `no address outside layout.py (3 file(s), 981 line(s) swept)`, e o caso
vermelho plantado do `self_check()` acha o que tem de achar. **O comportamento
está certo; o que está errado é o código que sobrou.**

## Causa raiz

A reescrita para `tokenize` moveu a decisão para outra função e não removeu as
regex da antiga.

## Correção

### Arquivo: `tools/looks/layout.py`

Apagar as duas linhas mortas do `sweep_addresses()`. O `import re` continua
necessário — o `_address_lines()` usa.

Se as regex vivas merecem ficar visíveis para quem lê o comando, que subam a
**constante de módulo** com nome próprio (`_HEX_LITERAL`, `_BIG_DECIMAL`),
compiladas uma vez e usadas no único lugar que decide. Duas cópias com o mesmo
nome em escopos diferentes é o que não pode continuar.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `tools/looks/layout.py` | modificar |

## Verificação

- [x] `grep -n "hex_literal\|big_decimal" tools/looks/layout.py` mostra cada
      nome definido **uma** vez
- [x] `python tools/looks/layout.py --check` verde, com o caso vermelho plantado
- [x] `python tools/looks/layout.py --sweep` continua achando zero e dizendo
      quantos arquivos e linhas varreu
- [x] `python tools/looks/section.py --check` e `iso_source.py --check` verdes

## Log de Execução

**Executado em:** 2026-09-14

**Resumo do que foi feito:**

As duas linhas mortas do `sweep_addresses()` saíram, e as vivas subiram a
**constante de módulo** com nome próprio — que é a segunda metade que a CORR
oferecia, e a que impede o mesmo tropeço de voltar:

```python
_HEX_LITERAL = re.compile(r"\A0[xX][0-9a-fA-F]+\Z")
_BIG_DECIMAL = re.compile(r"\A\d{4,}\Z")
```

Ficam ao lado do `ADDRESS_OWNER`, com o comentário dizendo por que são
ancoradas (quando são aplicadas, o candidato já é um token `NUMBER` inteiro do
`tokenize`, e não há o que procurar em volta) e por que são de módulo: para
haver **uma** definição de cada a editar.

Depois: cada nome aparece **uma vez definido e uma vez usado**.

```
$ grep -n "hex_literal\|big_decimal\|_HEX_LITERAL\|_BIG_DECIMAL" tools/looks/layout.py
744:_HEX_LITERAL = re.compile(...)
745:_BIG_DECIMAL = re.compile(...)
839:            if _HEX_LITERAL.match(body) or _BIG_DECIMAL.match(body):
```

O `import re` continua necessário, como a CORR previu.

Gates, e o que importa aqui é que o **comportamento não mudou**:

```
$ python tools/looks/layout.py --check
layout: self_check ok
$ python tools/looks/layout.py --sweep
layout --sweep: no address outside layout.py (3 file(s), 981 line(s) swept)
$ python tools/looks/section.py --check
section: self_check ok
$ python tools/looks/iso_source.py --check
iso_source: self_check ok
```

O caso vermelho plantado do `self_check()` continua achando os cinco que tem de
achar. E, para não confiar só nele, um `PLANTED = 0x8011C000` acrescentado ao
`section.py` real (nada commitado):

```
  section.py:483: PLANTED = 0x8011C000
layout --sweep: 1 line(s) carrying an address outside layout.py (3 file(s), 983 line(s) swept)
                                                                           (exit 1)
```

Arquivo restaurado e `git status` conferido antes do `git add`.

**Problemas encontrados:** nenhum.

A varredura de discrepância não achou documento que descreva as regex em si —
o plano e a task 03 descrevem a **regra** ("literal hexadecimal ou decimal de
quatro dígitos ou mais"), que continua verdadeira.

**Arquivos criados/modificados:**

- `tools/looks/layout.py` — as duas linhas mortas removidas, as vivas
  promovidas a `_HEX_LITERAL` e `_BIG_DECIMAL`
- `docs/tasks/looks/CORR-LOOKS-011.md` — este Log
- `docs/tasks/looks/correcoes-progresso.md` — tabela e checklist
