---
id: CORR-WTE-034
title: "Correção: a \"entrada real medida\" do `tipos.md` omite os cabeçalhos que declaram os campos que a tabela mapeia"
type: correção
category: dados
status: concluído
depends_on: []
---

# CORR-WTE-034: o inventário de entrada lista 5 arquivos, e a tabela mapeia campos de 4 outros

## Problema identificado

[`wte/re/tipos.md`](../../wte/re/tipos.md) abre declarando de onde a tabela
saiu:

> **Entrada real medida** — os tipos que de fato aparecem em
> `src/core/Database.cpp`, `Player.cpp`, `CdImage.cpp`, `TextCodec.cpp` e
> `Types.hpp`, que são as ~2.150 linhas que o transpilador digere.

As ~2.150 linhas conferem — são 2.147 exatas para esses cinco arquivos. O
problema é o resto: **a tabela e as cinco decisões mapeiam campos que não estão
em nenhum deles.** `Player.name`, `Player.url` e os 30 atributos estão em
`Player.hpp`; `Team.raw_formation`, as 48 cores, `flag_shape`, `link[46]` e
`Formation.roles/x/y` estão em `Team.hpp`; o `Offset = std::int64_t` está em
`CdImage.hpp`; o `Reporter` está em `Database.hpp`.

Duas consequências, e a segunda já se materializou:

1. Quem lê o `tipos.md` para dimensionar a entrada da WTE-TASK-17/18 recebe uma
   lista que **não contém as declarações dos registros que a camada de dados
   precisa gerar**.
2. O `UNITS` do `port_database_pas.py` (commit `8ae9170`) corrigiu por conta
   própria cinco cabeçalhos — `Types.hpp`, `CdImage.hpp`, `TextCodec.hpp`,
   `Player.hpp` e `Database.hpp` — e **`Team.hpp` ficou de fora**, que é
   justamente o que declara `Team`, `MlTeam` e `Formation`. `Database.hpp:44-48`
   os usa como campo; sem eles não há camada de dados completa, e nada no
   `--check` acusa a ausência.

Junto vai um segundo desacerto no mesmo parágrafo: das 16 linhas da tabela,
**três lideram com uma grafia C++ que não ocorre em lugar nenhum do
`src/core/`** — `std::uint8_t`, `std::uint16_t` e `std::int32_t`. Cada uma
dessas linhas também nomeia a grafia que ocorre (`unsigned char`,
`unsigned short`, `int`), então o mapeamento não está errado; errada está a
afirmação de que a coluna saiu do que a entrada usa. O critério de conclusão da
task pedia exatamente o contrário: "os tipos que a entrada real usa, **não os
que o enunciado supôs**" — e as três grafias ausentes são as do enunciado.

## Evidência

Contagem por arquivo, e o que a lista deixa de fora:

```console
$ wc -l src/core/Database.cpp src/core/Player.cpp src/core/CdImage.cpp \
        src/core/TextCodec.cpp src/core/include/we2002/Types.hpp
 1704 src/core/Database.cpp
  130 src/core/Player.cpp
   89 src/core/CdImage.cpp
   77 src/core/TextCodec.cpp
  147 src/core/include/we2002/Types.hpp
 2147 total

$ wc -l src/core/include/we2002/{Database,Player,Team,CdImage,TextCodec}.hpp
   60 Database.hpp
   95 Player.hpp
   91 Team.hpp
   77 CdImage.hpp
   18 TextCodec.hpp
```

Os campos que a tabela mapeia, e onde eles moram:

```console
$ grep -n 'raw_formation\|flag_colours\|link\[46\]' src/core/include/we2002/Team.hpp
41:    char raw_formation[31]{}, slot_role[10]{}, slot_x[10]{}, slot_y[10]{};
43:    unsigned short flag_colours[16]{};
70:    char raw_formation[31]{}, slot_role[10]{}, slot_x[10]{}, slot_y[10]{};
78:    unsigned char link[46]{};

$ grep -n 'char url\|char name' src/core/include/we2002/Player.hpp
62:    char url[500]{};
63:    char name[11]{};
```

`Team.hpp` fora do `UNITS` do transpilador já commitado — **estado de
2026-08-09, em `8ae9170`; corrigido em 2026-08-10, ver a nota na seção
"Correção"**:

```console
$ sed -n '71,77p' wte/tools/port_database_pas.py
UNITS: list[tuple[str, list[str]]] = [
    ("we2002_types", ["include/we2002/Types.hpp"]),
    ("we2002_cdimage", ["include/we2002/CdImage.hpp", "CdImage.cpp"]),
    ("we2002_textcodec", ["include/we2002/TextCodec.hpp", "TextCodec.cpp"]),
    ("we2002_player", ["include/we2002/Player.hpp", "Player.cpp"]),
    ("we2002_database", ["include/we2002/Database.hpp", "Database.cpp"]),
]

$ grep -n 'Team teams\|MlTeam\|Formation preset' src/core/include/we2002/Database.hpp
44:    Team teams[TEAMS_NATIONAL_ALLSTAR_SLOTS];
45:    MlTeam ml_teams[TEAMS_ML];        ///< Master League clubs
46:    MlTeam ml_default;                ///< the default-ML template
47:    Formation preset_formations[16];  ///< the 16 preset formations
```

As três grafias que a tabela cita e o `src/core/` não tem:

```console
$ grep -rnoE '\b(std::)?u?int(8|16|32|64)_t\b' src/core | sed 's/.*://' | sort | uniq -c
      1 int64_t
     31 uint32_t
```

Nenhuma ocorrência de `uint8_t`, `uint16_t` ou `int32_t` — as larguras de 8 e
16 bits aparecem só como `unsigned char` e `unsigned short`
(`Team.hpp:43-45`, 48 cores por time), e a de 32 com sinal só como `int`.

## Causa raiz

O inventário mediu os arquivos que o **plano** (§Fase 3 item 3) já listava, em
vez de medir onde estão declarados os campos que a tabela mapeia; as três
grafias vieram por herança da tabela de partida do enunciado.

## Correção

### Arquivo: `wte/re/tipos.md`

1. Trocar o parágrafo "Entrada real medida" pela lista completa, separando
   implementação de declaração e dizendo o total remedido:

   > **Entrada real medida** — `Database.cpp`, `Player.cpp`, `CdImage.cpp` e
   > `TextCodec.cpp` (2.000 linhas de implementação) mais os cabeçalhos que
   > declaram o que elas manipulam: `Types.hpp`, `Database.hpp`, `Player.hpp`,
   > `Team.hpp`, `CdImage.hpp` e `TextCodec.hpp` (341 linhas). **`Team.hpp` é o
   > que declara `Team`, `MlTeam` e `Formation`** — sem ele não há registro para
   > os campos das decisões 1 e 4.

2. Nas três linhas afetadas da tabela, deixar a grafia que ocorre e marcar a
   outra como *não presente na entrada, mapeada por completude* — ou removê-la.

### Arquivo: `wte/tools/port_database_pas.py`

Decidir e registrar o destino de `Team.hpp`: entrar no `UNITS` (em
`we2002_types`, junto com `Types.hpp`, ou em unidade `we2002_team` própria) ou
ser recusa explícita com razão escrita. Hoje ele simplesmente não é lido, e nada
acusa.

> **✅ Esta metade já foi feita** — 2026-08-10, na varredura de concorrência da
> leva WTE-TASK-16/17/24. `Team.hpp` e `Team.cpp` entraram como unidade
> **`we2002_team`** própria, e o "nada acusa" virou gate: entrou a lista fechada
> `FORA_DO_TRANSPILADOR`, com motivo escrito por arquivo, mais o
> `test_nenhuma_entrada_do_core_fica_de_fora`, que cruza `src/core/` com o
> `UNITS` **nos dois sentidos** — reprova arquivo órfão e também motivo escrito
> para arquivo que não existe mais.
>
> Entrada remedida: **2.504 linhas** em 6 unidades. Recusas: 498 (eram 493).
>
> **O que sobra desta correção é o `tipos.md`** — o parágrafo "Entrada real
> medida" e as três grafias que não ocorrem na entrada. A §4.5 e a Fase 3 do
> [`PLAN-WTE-LAZARUS.md`](/docs/PLAN-WTE-LAZARUS.md) repetem o mesmo "~2.150" e
> entram junto.

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/tipos.md` | modificar |
| `wte/tools/port_database_pas.py` | modificar *(feito antes, em 2026-08-10 — ver a nota acima)* |
| `docs/PLAN-WTE-LAZARUS.md` | modificar (§4.5 e Fase 3 item 3, achado na varredura) |
| `docs/tasks/15-mapeamento-de-tipo.md` | modificar (varredura) |
| `docs/tasks/17-transpilador-da-camada-de-dados.md` | modificar (varredura) |
| `docs/tasks/18-camada-de-dados-gerada.md` | modificar (varredura) |

## Verificação

- [x] O `tipos.md` lista `Team.hpp` e os demais cabeçalhos, com a contagem de
      linhas remedida por `wc -l`
- [x] Nenhuma linha da tabela lidera com grafia que
      `grep -rnoE '\b(std::)?u?int(8|16|32|64)_t\b' src/core` não mostra
- [x] `Team`, `MlTeam` e `Formation` têm destino escrito — unidade
      `we2002_team`, com guarda que reprova header órfão (2026-08-10)
- [x] `python3 wte/tools/port_database_pas.py --check` continua verde
- [x] `make -C wte check` verde
- [x] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:** 2026-08-10

**Resumo do que foi feito:**

O parágrafo "Entrada real medida" do `tipos.md` virou tabela de duas linhas —
**2.016** de implementação (os cinco `.cpp`, `Team.cpp` incluído) e **488** de
declaração (os seis `.hpp`), **2.504** no total, batendo com o `UNITS` do
`port_database_pas.py` e com o que a WTE-TASK-17 mediu na execução. Junto foi o
que faltava dizer: os cabeçalhos não são apêndice, é neles que moram os campos
que a tabela mapeia, e `Team.hpp` é o que declara `Team`, `MlTeam` e
`Formation`, usados como campo em `Database.hpp:44-48`.

Nas três linhas da tabela, a grafia que ocorre passou a liderar e a ausente
ficou marcada como **não ocorre na entrada**: `unsigned char` (e não
`std::uint8_t`), `unsigned short` (e não `std::uint16_t`), `int` (e não
`std::int32_t`). A remedição por
`grep -rnoE '\b(std::)?u?int(8|16|32|64)_t\b' src/core` devolve só
`std::uint32_t` (30), `uint32_t` (1) e `std::int64_t` (1) — as duas linhas que
citam essas continuam certas.

A metade do `port_database_pas.py` já estava feita desde 2026-08-10 (unidade
`we2002_team` mais a lista `FORA_DO_TRANSPILADOR` e o
`test_nenhuma_entrada_do_core_fica_de_fora`); esta execução só conferiu que o
`--check` continua verde.

**Problemas encontrados:**

O "~2.150" tinha mais sítios do que a CORR previa. Além do `tipos.md` e da §4.5
do plano, a **Fase 3 item 3** do mesmo plano repetia o número (e omitia `Team`
da lista de unidades a gerar), o Log da WTE-TASK-15 o repetia como se fosse a
medida do inventário, o contexto da WTE-TASK-18 explicava a divergência como
pendência aberta, e o Log da WTE-TASK-17 apontava esta CORR como quem ainda ia
reconciliar. Os cinco entraram nesta invocação; o bloco de código da §4.5 passou
a listar os 11 arquivos, com a razão de os cabeçalhos entrarem escrita ao lado.

**Arquivos criados/modificados:**

- `wte/re/tipos.md`
- `docs/PLAN-WTE-LAZARUS.md`
- `docs/tasks/15-mapeamento-de-tipo.md`
- `docs/tasks/17-transpilador-da-camada-de-dados.md`
- `docs/tasks/18-camada-de-dados-gerada.md`
