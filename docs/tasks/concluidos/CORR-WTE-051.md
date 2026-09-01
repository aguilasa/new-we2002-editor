---
id: CORR-WTE-051
title: "Correção: a fração de 92,5% subtrai linhas úteis de um total que conta linhas em branco"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-051: as duas colunas da fração não contam a mesma coisa

## Problema identificado

A tabela da seção 1 do
[`wte/re/fase-3-fechamento.md`](../../../wte/re/fase-3-fechamento.md) apresenta três
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

- [x] a coluna **por regra** é a subtração de duas contagens da mesma régua, e a
      régua está escrita no documento — *"A régua é a mesma nas três colunas:
      linha física, branco incluído"*
- [x] recontar por fora com a régua declarada dá o número publicado —
      `total=3692 mao=303 regra=3389 pct=91.8%`
- [x] `python3 wte/tools/check_fase3.py --check` verde, duas vezes com o mesmo
      md5 (`b53ed5b4…`)
- [x] `make -C wte check` verde — 399 testes, `rc=0`
- [x] a §4.5 do plano e o `fase-3-fechamento.md` dizem a mesma fração (91,8%),
      e o `progresso.md` e a WTE-TASK-21 também

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

`confere_bloco()` ficou com as duas responsabilidades **separadas e ditas**:
continua casando por linha útil — linha vazia casaria com qualquer coisa, e a
pergunta do casamento é *este bloco ainda é emitido?* — e passou a **contar**
linha física, que é a régua do total.

Das duas opções da seção Correção escolhi contar tudo dos dois lados (91,8%),
e não linha útil dos dois (92,2%), por duas razões: linha em branco dentro de
um bloco manual **foi escrita à mão** e sai emitida junto, então creditá-la ao
gerador é o próprio defeito; e assim o documento inteiro passa a usar **uma
régua só** — o total da seção 1 (3692) é o mesmo número que a seção 2 usa como
saída, o que não aconteceria com 3537.

| | antes | agora |
|---|---:|---:|
| total | 3692 (com branco) | 3692 (com branco) |
| à mão | 277 (sem branco) | 303 (com branco) |
| por regra | 3415 | 3389 |
| fração | 92,5% | **91,8%** |

A tabela ganhou o parágrafo que declara a régua, e a diferença de 26 linhas
está nomeada ali.

Dois testes novos e um reescrito: a recontagem por fora da coluna **à mão** com
a régua do total; a régua da contagem presa com bloco plantado (3 linhas
físicas, 2 úteis, tem de devolver 3); e o
`test_bloco_presente_conta_as_linhas_uteis`, que prendia a régua antiga,
virou `test_bloco_presente_casa_por_linha_util_e_conta_todas`.

**Problemas encontrados:**

A varredura de discrepância puxou quatro sítios além dos previstos na CORR — a
fração e as 277 linhas viviam também no `progresso.md`, na tabela de critérios
da WTE-TASK-21 e duas vezes no Log dela. Todos foram reconciliados dizendo a
régua; o parágrafo do Log que narra o dedupe (320 → 277, 91,3% → 92,5%) ficou
como está, porque é história daquele momento, com uma nota dizendo que aqueles
três números são de linha útil e que a régua publicada mudou depois.

**Arquivos criados/modificados:**

- `wte/tools/check_fase3.py` — `confere_bloco()` e o texto da seção 1
- `wte/tools/test_check_fase3.py` — dois testes novos, um reescrito
- `wte/re/fase-3-fechamento.md` — regerado
- `docs/PLAN-WTE-LAZARUS.md` — §4.5
- `docs/tasks/concluidos/progresso.md` — o resumo da WTE-TASK-21 *(reconciliação)*
- `docs/tasks/concluidos/21-fechamento-fase-3.md` — critério e Log *(reconciliação)*
