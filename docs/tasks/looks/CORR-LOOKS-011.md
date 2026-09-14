---
id: CORR-LOOKS-011
title: "Correção: o `sweep_addresses()` guarda duas regex mortas com o nome das vivas"
type: correção
category: verificação
status: pendente
depends_on: []
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

- [ ] `grep -n "hex_literal\|big_decimal" tools/looks/layout.py` mostra cada
      nome definido **uma** vez
- [ ] `python tools/looks/layout.py --check` verde, com o caso vermelho plantado
- [ ] `python tools/looks/layout.py --sweep` continua achando zero e dizendo
      quantos arquivos e linhas varreu
- [ ] `python tools/looks/section.py --check` e `iso_source.py --check` verdes

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
