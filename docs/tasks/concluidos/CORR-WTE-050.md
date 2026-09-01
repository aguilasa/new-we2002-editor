---
id: CORR-WTE-050
title: "Correção: a razão entrada × saída divide 3.692 linhas de Pascal por uma entrada que só explica 2.984 delas"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-050: as 708 linhas do `gen_tables_pas` entram no numerador e a entrada delas não entra no denominador

## Problema identificado

A seção **"2. Entrada × saída"** do
[`wte/re/fase-3-fechamento.md`](../../../wte/re/fase-3-fechamento.md), gerada por
`wte/tools/check_fase3.py`, afirma:

> 2504 linhas de C++ viraram 3692 de Pascal — razão 1.47.

As duas contagens existem, mas são de **populações diferentes**:

- **2504** é a soma das 11 entradas do `UNITS` do `port_database_pas.py` — só o
  transpilador;
- **3692** é a soma dos **oito** `.pas` da camada, e dois deles
  (`we2002_offsets.pas`, 106 linhas, e `we2002_tables.pas`, 602) **não saem do
  transpilador**: saem do `gen_tables_pas.py`, a partir de `Tables.cpp` (704),
  `Tables.hpp` (53) e `Offsets.hpp` (95) — 852 linhas que o denominador ignora.

Que essas três entradas fiquem fora do `UNITS` está certo e é decisão escrita
(`FORA_DO_TRANSPILADOR`: *"é do `gen_tables_pas.py` (WTE-TASK-16), não deste
gerador"*). O defeito é somar a **saída** dos dois geradores contra a **entrada**
de um só.

Com as duas metades fechadas, a razão é outra:

| conta | entrada | saída | razão |
|---|---:|---:|---:|
| publicada | 2504 (só o transpilador) | 3692 (os dois geradores) | **1.47** |
| só o transpilador | 2504 | 2984 | 1.19 |
| os dois geradores | 3356 | 3692 | 1.10 |

A frase migrou para a **§4.5 do plano** com a mesma forma — *"3.692 emitidas a
partir das 2.504 de entrada"* —, e ali ela sustenta a tese de que a fase 3 é
execução de gerador. A tese continua de pé por outro número (a fração de 92,5%);
o que não se sustenta é a relação de origem, porque 708 das 3.692 não vieram
daquelas 2.504.

## Evidência

A conta, no gerador (`wte/tools/check_fase3.py:303-305`):

```python
    razao = frac["total"] / total_entrada
    w(f"{total_entrada} linhas de C++ viraram {frac['total']} de Pascal —")
    w(f"razão {razao:.2f}. As duas contagens saem de ferramenta: a entrada é o")
```

`frac["total"]` vem de `DA_CAMADA`, que tem os oito arquivos e nomeia o gerador
de cada um — inclusive os dois do `gen_tables_pas.py`:

```python
    "we2002_offsets.pas": "gen_tables_pas.py",
    "we2002_tables.pas": "gen_tables_pas.py",
```

`total_entrada` vem de `entrada_do_transpilador()`, que percorre só `P.UNITS`:

```
$ python3 -c "import sys;sys.path.insert(0,'wte/tools');import port_database_pas as P;print([u for u,_ in P.UNITS])"
['we2002_types', 'we2002_team', 'we2002_cdimage', 'we2002_textcodec', 'we2002_player', 'we2002_database']
```

A entrada que falta no denominador:

```
$ wc -l src/core/Tables.cpp src/core/include/we2002/Tables.hpp src/core/include/we2002/Offsets.hpp
  704 src/core/Tables.cpp
   53 src/core/include/we2002/Tables.hpp
   95 src/core/include/we2002/Offsets.hpp
  852 total
```

E o `gen_tables_pas.py` lê as três (`TABLES_CPP = ROOT / "src/core/Tables.cpp"`,
linha 46; `parse_tables_cpp(TABLES_CPP, ...)`, linha 565).

A frase propagada, em `docs/PLAN-WTE-LAZARUS.md:589-591`:

> 3.415 linhas contra 277 escritas à mão, sobre 3.692 emitidas a partir das
> 2.504 de entrada.

## Causa raiz

`fracao_gerada()` mede os oito `.pas` (dois geradores) e
`entrada_do_transpilador()` mede só o `UNITS` de um deles; a razão divide um
pelo outro sem notar que são escopos diferentes.

## Correção

### Arquivo: `wte/tools/check_fase3.py`

O alvo é gerado — a correção entra no gerador. Duas rotas, e a segunda é
preferível:

1. **Fechar o denominador**: acrescentar as entradas do `gen_tables_pas.py`
   (`Tables.cpp`, `Tables.hpp`, `Offsets.hpp`) à tabela de entrada, marcadas com
   o gerador que as consome, e publicar a razão sobre os dois conjuntos
   completos (1.10);
2. **Separar por gerador**: uma linha de razão para o transpilador
   (2504 → 2984, 1.19) e outra para o `gen_tables_pas` (852 → 708, 0.84). Diz
   mais: tabela em Pascal é mais compacta que o inicializador em C++, e o
   transpilador é que infla — e cada razão passa a comparar entrada com a saída
   que ela produziu.

A lista `DA_CAMADA` já nomeia o gerador de cada `.pas`, então a separação é
mecânica. Vale um teste que reprove razão calculada sobre conjunto cuja saída
inclui gerador ausente do denominador.

### Arquivo: `docs/PLAN-WTE-LAZARUS.md`

Trocar *"3.692 emitidas a partir das 2.504 de entrada"* pela forma correta. A
fração de 92,5% não muda — ela não usa a entrada.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/check_fase3.py` | modificar |
| `wte/tools/test_check_fase3.py` | modificar — teste que prenda o pareamento entrada × saída por gerador |
| `wte/re/fase-3-fechamento.md` | modificar (regerado) |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.5) |

## Verificação

- [x] toda linha de saída contada tem a entrada do seu gerador no denominador —
      `conferir_entradas()` aborta, e o teste planta um terceiro gerador em
      `DA_CAMADA` para provar que aborta
- [x] o `fase-3-fechamento.md` e a §4.5 dizem a mesma razão, e ela fecha na
      calculadora — `2984/2504 = 1.19`, `708/852 = 0.83`, `3692/3356 = 1.10`
- [x] `python3 wte/tools/check_fase3.py --check` verde, duas vezes com o mesmo
      md5 (`06611754…`)
- [x] `make -C wte check` verde — 397 testes, `rc=0`
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

Adotada a **rota 2** da seção Correção — separar por gerador —, que é a que
diz mais. A seção 2 do `fase-3-fechamento.md` passou a trazer a entrada
etiquetada com o gerador que a consome e uma linha de razão por gerador:

| gerador | entrada | saída | razão |
|---|---:|---:|---:|
| `gen_tables_pas.py` | 852 | 708 | 0,83 |
| `port_database_pas.py` | 2504 | 2984 | 1,19 |
| **total** | **3356** | **3692** | **1,10** |

O que a razão única escondia fica dito: o transpilador **infla** (Pascal quer
`begin`/`end` onde o C++ tem chave, e declaração no topo do corpo) e o gerador
de tabelas **encolhe** (a tabela cabe em menos linha de Pascal do que de
inicializador C++). São efeitos de sinal oposto — somá-los não descrevia
nenhum dos dois.

As três entradas do `gen_tables_pas.py` **não** foram transcritas: são lidas
das constantes dele (`G.TABLES_CPP`, `G.TABLES_HPP`, `G.OFFSETS_HPP`), pelo
mesmo motivo que `blocos_manuais()` lê o `port_database_pas` em vez de copiar
os blocos — lista copiada envelhece calada.

`conferir_entradas()` é a guarda: gerador que aparece em `DA_CAMADA` e não tem
entrada no denominador aborta a geração. É o que impede a repetição — o
defeito nasceu quando o `gen_tables_pas.py` entrou na saída e ninguém somou a
entrada dele.

Três testes novos: o pareamento sobre a árvore real, a guarda plantando um
terceiro gerador, e a identidade entre `entrada_de_tabelas()` e as constantes
do `gen_tables_pas`.

A §4.5 do plano perdeu a relação de origem *"3.692 emitidas a partir das 2.504
de entrada"* e ganhou as duas razões. A fração de 92,5% ficou como estava —
ela não usa a entrada, e é assunto da
[CORR-WTE-051](/docs/tasks/concluidos/CORR-WTE-051.md), executada em seguida no mesmo
lote: ela pôs a mesma régua nos dois lados da subtração e a fração passou a
**91,8%**. Quem ler este Log depois disso lê o estado intermediário.

**Problemas encontrados:**

A tabela desta CORR dá **0.84** para a razão do `gen_tables_pas`; a medida é
`708 / 852 = 0,8309`, que arredonda para **0,83**. Diferença de
arredondamento, sem efeito no argumento — o número publicado é o que o gerador
calcula, não o transcrito aqui.

**Arquivos criados/modificados:**

- `wte/tools/check_fase3.py` — `entrada_de_tabelas()`, `entrada_por_gerador()`,
  `conferir_entradas()`, a seção 2 do markdown
- `wte/tools/test_check_fase3.py` — três testes
- `wte/re/fase-3-fechamento.md` — regerado
- `docs/PLAN-WTE-LAZARUS.md` — §4.5
