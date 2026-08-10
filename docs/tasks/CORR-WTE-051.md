---
id: CORR-WTE-051
title: "Correção: a fração de 92,5% subtrai linhas úteis de um total que conta linhas em branco"
type: correção
category: dados
status: pendente
depends_on: []
---

# CORR-WTE-051: as duas colunas da fração não contam a mesma coisa

## Problema identificado

A tabela da seção 1 do
[`wte/re/fase-3-fechamento.md`](../../wte/re/fase-3-fechamento.md) apresenta três
colunas — **linhas**, **à mão**, **por regra** — em que a terceira é a subtração
das duas primeiras, e fecha em `3692 − 277 = 3415`, os 92,5% publicados.

As duas primeiras usam réguas diferentes:

- **linhas** vem de `linhas(texto)`, que é `len(splitlines())` — conta **tudo**,
  inclusive linha em branco;
- **à mão** vem de `confere_bloco()`, que filtra `if l.strip()` — conta só
  **linha útil**.

Os blocos manuais têm **26 linhas em branco**. Elas estão dentro do Pascal
escrito à mão, foram emitidas junto com ele, e a subtração as credita à coluna
**por regra** — isto é, conta como transpilação linha em branco que veio de
constante do gerador.

O efeito na manchete:

| régua | fração |
|---|---:|
| publicada (total com brancos − manual sem brancos) | **92,5%** |
| mesma régua nos dois lados, com brancos | 91,8% |
| mesma régua nos dois lados, sem brancos | 92,2% |

Nenhuma das três muda a conclusão da fase — a tese da §4.5 sobrevive a 91,8%
igual. O que está errado é a forma: uma subtração entre contagens que não são
comensuráveis, publicada como se fosse.

O documento também não diz qual régua usa, então quem recontar por fora — com
`wc -l` sobre os blocos, por exemplo — acha 303 e não 277, sem nada que explique
a diferença.

## Evidência

As duas definições, em `wte/tools/check_fase3.py`:

```python
def linhas(texto: str) -> int:
    return len(texto.splitlines())          # linha 94 -- conta branco
...
    uteis = [l.strip() for l in texto.splitlines() if l.strip()]
    ...
    return len(uteis)                       # confere_bloco -- nao conta branco
```

Recontado por fora, com as duas réguas:

```
$ python3 - <<'EOF'
... (soma os 8 .pas e os blocos de MANUAIS/MANUAL_TIPOS/MANUAL_DECLS, com o
     mesmo dedupe do check_fase3)
EOF
total linhas dos 8 .pas: 3692
manual (so nao-vazias, regra do check_fase3): 277
manual (todas as linhas do bloco): 303
fracao publicada: 92.5% 3415 de 3692
fracao com a mesma regra nos dois lados: 91.8%
denominador so nao-vazias: 3537 -> 92.2%
```

`303 − 277 = 26` é o tamanho do desvio.

## Causa raiz

`confere_bloco()` filtra linha em branco porque casa o bloco contra a saída
(linha vazia casaria com qualquer coisa), e o número de retorno dessa
conferência foi reaproveitado como contagem — sem que o total do arquivo
passasse pelo mesmo filtro.

## Correção

### Arquivo: `wte/tools/check_fase3.py`

Separar as duas responsabilidades de `confere_bloco()`: ela continua casando por
linha útil, e a **contagem** passa a usar a mesma régua do total. A escolha mais
simples é contar linha útil dos dois lados — a fração vira 92,2% e o
denominador passa a ser 3537 —, mas contar tudo dos dois lados (91,8%) também
serve. O que não serve é uma de cada.

Qualquer que seja a escolha, o cabeçalho da tabela deve dizer a régua, e o
teste `test_a_maior_parte_e_transpilacao` deve ganhar um irmão que reprove
mistura: contar os blocos manuais pelas duas réguas e exigir que a publicada
seja a mesma dos dois lados da subtração.

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

A §4.5 repete `92,5% ... 3.415 linhas contra 277 ... sobre 3.692`; atualizar
junto com a regeração.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase3.py` | modificar |
| `wte/tools/test_check_fase3.py` | modificar — teste que reprove régua misturada |
| `wte/re/fase-3-fechamento.md` | modificar (regerado) |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.5) |

## Verificação

- [ ] a coluna **por regra** é a subtração de duas contagens da mesma régua, e a
      régua está escrita no documento
- [ ] recontar por fora com a régua declarada dá o número publicado
- [ ] `python3 wte/tools/check_fase3.py --check` verde, duas vezes com o mesmo
      resultado
- [ ] `make -C wte check` verde
- [ ] a §4.5 do plano e o `fase-3-fechamento.md` dizem a mesma fração

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
