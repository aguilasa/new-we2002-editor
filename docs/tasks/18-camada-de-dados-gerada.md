---
id: WTE-TASK-18
title: "Gerar a camada de dados e fazê-la compilar"
type: implementação
category: dados
phase: 3
depends_on: ["WTE-TASK-17"]
status: concluído
---

# WTE-TASK-18: Camada de dados gerada

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 3 item 3.
- Executar o transpilador da WTE-TASK-17 sobre as 2.504 linhas (medidas — ver o
  `wte/re/transpilador.md`; o `tipos.md` e a §4.5 do plano dizem o mesmo número
  desde a [CORR-WTE-034](/docs/tasks/CORR-WTE-034.md)) e resolver o que
  o `FORBIDDEN` recusar.

> **Escopo ampliado pela WTE-TASK-17 — o passe estrutural é desta task.**
>
> O `tools/port_database.py`, o precedente, pôde ser substituição textual pura
> porque a fonte e o alvo dele são a **mesma linguagem**. C++ → Pascal não pode:
> bloco, cabeçalho de laço, assinatura de função e declaração de variável não
> têm forma comum, e nenhuma regex os alcança sem casamento de chave.
>
> A WTE-TASK-17 entregou a camada de **statement e expressão** — 47 regras, os
> dois guards, 38 testes — e pôs a estrutura no `FORBIDDEN` em vez de deixá-la
> passar. Emitir `.pas` com corpo em C++ produziria um artefato que parece
> camada de dados, não compila, e convida a "só ajustar à mão" o que a §4.4
> proíbe.
>
> Das **498 recusas** que o `wte/re/transpilador.md` lista, **454 são o passe
> estrutural** e 44 são construção C++ sem tradução decidida. Construir o passe
> é a primeira parte desta task; as outras 44 são as três rotas de sempre.
>
> O que o passe precisa cobrir, medido na entrada: `{ }` → `begin`/`end`;
> `for (i = 0; i < N; i++)` → `for i := 0 to N-1 do`, e passo ≠ 1 → `while`;
> assinatura de função → `procedure`/`function` com as locais **hoisted** para
> um bloco `var`; `struct` → `record`, com `packed` só onde a decisão 2 do
> `tipos.md` manda; `switch` → `case`, e **fallthrough não traduz** (há dois,
> em `Database.cpp:450` e `:1256`, e os dois decidem quantos bytes ler).

**O que o `FORBIDDEN` recusa não é falha do gerador — é trabalho identificado.**
Cada recusa tem três saídas, e a decisão vai escrita:

1. **Estender a tabela** — a construção tem tradução mecânica, faltava a regra.
2. **Ajustar a entrada** — o C++ do `we2002_core` pode ser reescrito num estilo
   que o transpilador digere, **sem mudar comportamento**, e isso melhora os
   dois lados. Exige rodar o golden test do `newWe2002` depois.
3. **Porte manual daquele trecho** — último recurso, e o trecho fica marcado.

A opção 2 tem custo escondido: mexer em `src/core/` afeta o `newWe2002`, que
está com escopo fechado e verificado. **Não fazer sem rodar `ctest` e o golden.**

---

## Objetivo

Unidades Pascal geradas, compilando, com o registro do que foi recusado.

### Escopo

| Entrada | Saída |
|---|---|
| `Database.cpp` + `.hpp` | `we2002_database.pas` |
| `Player.cpp` + `.hpp` | `we2002_player.pas` |
| `CdImage.cpp` + `.hpp` | `we2002_cdimage.pas` |
| `TextCodec.cpp` + `.hpp` | `we2002_textcodec.pas` |
| `Types.hpp` | `we2002_types.pas` |
| `Team.hpp` + `.cpp` | `we2002_team.pas` — `Team`, `MlTeam`, `Formation` |

**`Sofifa.cpp` fica de fora.** O import do SoFIFA está desligado no `newWe2002`
desde 2026-08-05, o editor do Obocaman não tem nada equivalente, e trazer 805
linhas sem consumidor é peso morto.

### Regras que a camada tem de preservar

Vindas do `newWe2002`, todas com custo pago:

- **Nunca recalcular EDC/ECC.** O editor original não recalcula; um port deve
  **preservar**, não "corrigir".
- **Setores MODE2/2352.** Os offsets pulam cabeçalho de setor manualmente; se um
  round-trip falhar, a primeira suspeita é fronteira de setor.
- **Leitura curta não é erro.**
- **`Load`+`Save` sem editar nada não devolve a imagem intacta**, e não deveria:
  o `Save` reconstrói as all-star a partir dos links. O oráculo faz o mesmo.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/src/we2002_*.pas` | criar (6, gerado) |
| `wte/re/recusas.md` | criar — cada recusa, a rota escolhida, a razão |
| `src/core/*` | modificar **só** se a rota 2 for escolhida, e com golden rodado |

---

## Critério de conclusão

- [x] Passe estrutural implementado no `port_database_pas.py`, com teste
- [x] As seis unidades geradas e compilando
- [x] Toda recusa do `FORBIDDEN` com rota escolhida e razão escrita
- [x] Se houve rota 2: `ctest` e o golden do `newWe2002` verdes depois
      — **não houve rota 2**; `src/core/` não foi tocado
- [x] Trechos de porte manual marcados no código gerado
- [x] `Sofifa.cpp` fora, e a razão registrada
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-10

- **Resumo do que foi feito:**

  As **498 recusas** viraram **zero**, e nenhuma precisou da rota 2 — `src/core/`
  não foi tocado. 454 delas eram o passe estrutural (bloco, `for`, assinatura),
  que é um problema só; o resto se dividiu entre rota 1 (fallthrough,
  `static_assert`, `sizeof`) e rota 3 (`CdImage`, `SquadNumbers`, `Reporter`,
  sidecar — os quatro já desenhados no `tipos.md`). O veredito por recusa está em
  [`wte/re/recusas.md`](../../wte/re/recusas.md).

  **O que a task ensinou, e não estava previsto:** o passe estrutural não é a
  parte perigosa. As decisões que mudam comportamento em silêncio estão nos
  **detalhes de precedência e de escopo**, e nenhuma delas deixava token para o
  `FORBIDDEN` pegar. Sete defeitos da tabela da WTE-TASK-17 saíram daí, e quatro
  produziriam Pascal que compila e faz outra coisa:

  1. as SUBS rodavam **dentro de literal** — `"Error ! Impossible to open CD
     image !"` saía como `'Error not Impossible …'`, com a regra `!` → `not`
     comendo o texto que o usuário lê;
  2. o `&` era apagado em toda posição de argumento, então
     `ResolveMlLink(&link[i*2])` passava um **Byte** onde a rotina espera
     ponteiro;
  3. `a == 1 && b > 2` virava `a = 1 and b > 2`, que o FPC lê como
     `a = (1 and b) > 2` — em C `==` liga mais forte que `&&`, em Pascal `and`
     liga mais forte que `=`;
  4. `x |= defence-12` virava `(x or defence) - 12`, porque em Pascal `or` e `-`
     têm a mesma precedência.

  E duas armadilhas de linguagem que só o `fpc` mostra: `as` (parâmetro de
  `AsciiToKanji`) é o operador de type-cast do Pascal, e `Report(report, …)` não
  compila porque o Pascal **não distingue caixa** — o parâmetro esconde a rotina.
  A rotina portada à mão virou `Reportar`.

  A tradução de `for` também não é de estilo: em Pascal o valor da variável de
  controle **depois** do laço é indefinido e atribuir a ela **dentro** é
  proibido, e a entrada faz as duas coisas (`TextCodec.cpp:42` lê `i` depois;
  `Database.cpp:762` faz `i = 1750` para pular 46 slots de custo). Esses viram
  `while`; os demais viram `for..to..do`.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tools/port_database_pas.py` | passe estrutural, 3 passes novos de expressão, tabela de manuais, terceiro guard |
  | `wte/tools/test_port_database_pas.py` | 58 testes (eram **38**). Os dois números são desta task e se remedem com `git show <commit>:wte/tools/test_port_database_pas.py \| grep -cE '^[[:space:]]+def test_'` — `d8af56a` dá 38, `7b642f7` dá 58; no `HEAD` já são outros |
  | `wte/src/we2002_{types,team,cdimage,textcodec,player,database}.pas` | criados, **gerados** |
  | `wte/re/transpilador.md` | regerado |
  | `wte/re/recusas.md` | criado |
  | `wte/tests/test_camada_dados.pas` | criado — 23 casos que provam as decisões de tipo |
  | `wte/tests/README.md`, `wte/re/fase-2.md` | atualizados (o segundo, pelo próprio `check_fase2.py`) |

- **Problemas encontrados:**

  Um item da task estava desatualizado e foi corrigido: o enunciado prevê
  `wte/re/recusas.md` "cada recusa, a rota escolhida, a razão", e a tabela de
  recusas da WTE-TASK-17 contava `[[fallthrough]]` duas vezes (entrada e saída
  do mesmo par de linhas). O `recusas.md` registra as duas contagens como o par
  que são, em vez de repetir o número.

  Duas divergências entre doc e ferramenta, as duas corrigidas: o checklist da
  fase 3 no `progresso.md` dizia "as **cinco** unidades de dados geradas", e o
  escopo desta task lista **seis** desde a [CORR-WTE-034](/docs/tasks/CORR-WTE-034.md),
  que acrescentou `we2002_team.pas`; e o `emitir_doc` do transpilador ainda
  escrevia "as cinco unidades" na linha de "nenhuma recusa".

  O `check_fase2.py` reprovou depois desta task, e **corretamente**: a frase que
  ele gera lista os `.pas` fora da conta da casca, e passaram de 2 para 8. Foi
  regerado; a fração de 96,2% não mudou, porque a exclusão é por prefixo.

  Nada ficou pendente. O que esta task **não** mede, e é da WTE-TASK-20: que a
  camada Pascal leia e grave os mesmos bytes que o `we2002_core` nas duas ROMs.
  Compilar e provar as decisões de tipo é condição necessária, não suficiente —
  o `Load` inteiro ainda não rodou contra imagem nenhuma.
