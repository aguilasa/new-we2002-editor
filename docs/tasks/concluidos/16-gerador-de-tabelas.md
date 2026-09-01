---
id: WTE-TASK-16
title: "tools/gen_tables_pas.py — offsets e tabelas estáticas"
type: ferramenta
category: dados
phase: 3
depends_on: ["WTE-TASK-15"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md §4.4 e Fase 3 item 3"
status: concluído
---

# WTE-TASK-16: Gerador de tabelas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.4 e Fase 3 item 3.
- O gerador **mais simples** dos quatro, e por isso o primeiro a rodar: a
  entrada é dado puro, sem fluxo de controle para traduzir. Serve de piloto do
  contrato de gerador antes do transpilador de verdade (WTE-TASK-17).

Entrada, tudo deste repositório:

| Arquivo | Conteúdo |
|---|---|
| `src/core/include/we2002/Offsets.hpp` | 69 `OFS_*` |
| `src/core/Tables.cpp` | 704 linhas, 16 tabelas |
| `src/core/include/we2002/Tables.hpp` | as declarações |

---

## Objetivo

`wte/tools/gen_tables_pas.py` emitindo uma unidade Pascal com os offsets como
`const` e as 16 tabelas como array constante.

### Requisitos

- **Nomes preservados.** `OFS_TEAM_NAME_1` continua `OFS_TEAM_NAME_1`. O
  glossário do `newWe2002` já traduziu tudo do italiano; não retraduzir, não
  "melhorar". Grepar um nome nas duas árvores tem de continuar funcionando.
- **Rastreabilidade herdada.** Os offsets carregam comentário com o nome antigo
  (`// was OFS_NOMI_SQ1`); preservar como comentário Pascal.
- **Tipo conforme a WTE-TASK-15.**
- `--check`, saída byte-estável, falha alta em construção não reconhecida.

### Conferência obrigatória

O valor de cada offset no Pascal gerado tem de ser **numericamente igual** ao do
`Offsets.hpp`. Gerar um teste que compara os 69, não confiar na inspeção.

Isso parece redundante — é o mesmo arquivo de entrada. Não é: erro de parsing de
literal (hex, sufixo, expressão) produz número plausível e errado, e o offset
errado só aparece quando a gravação corromper a imagem.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tools/gen_tables_pas.py` | criar |
| `wte/src/we2002_offsets.pas` | criar (gerado) |
| `wte/src/we2002_tables.pas` | criar (gerado) |
| `wte/tests/test_offsets.pas` | criar (gerado — ver o Log) |
| `wte/tests/test_offsets.cpp` | criar (gerado — o irmão C++ da conferência) |
| `wte/tools/test_gen_tables_pas.py` | criar — recusa com entrada plantada |

---

## Critério de conclusão

- [x] Os 69 offsets e as 16 tabelas emitidos
- [x] Nomes idênticos aos do `newWe2002`
- [x] Comentários `was OFS_*` preservados
- [x] Teste comparando os 69 valores contra o `Offsets.hpp`, verde
- [x] `--check` implementado e verde
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-09

- **Resumo do que foi feito:**

  `gen_tables_pas.py` lê `Offsets.hpp`, `Tables.hpp` e `Tables.cpp` e emite
  quatro arquivos: as duas unidades Pascal e os **dois dumpers** da conferência
  obrigatória. Saem 69 `OFS_*` + as 3 constantes de setor + `N_ROLES` e
  `START_LINK_COUNT`, e as 16 tabelas, com os tipos de `wte/re/tipos.md`
  (`ShortInt` para `char` numérico, `AnsiChar` para `char` de texto, `LongInt`
  para `int`, constante sem tipo para os offsets).

  **O que se aprendeu, e é o item que vale para as tasks 17 e 18:** a task pedia
  "um teste comparando os 69 valores contra o `Offsets.hpp`", e o caminho óbvio
  — o próprio parser do gerador conferindo a saída do gerador — **não prova
  nada**: erro de leitura de literal apareceria idêntico dos dois lados. A
  conferência foi montada como dois dumpers que emitem as mesmas linhas, um
  compilado pelo `fpc` a partir do Pascal gerado, o outro pelo `g++` a partir do
  C++ original. Nenhuma regex no circuito: cada valor vem de um compilador.
  Resultado medido: **1383 linhas idênticas** (74 constantes, 1048 elementos
  numéricos, 261 de texto). Os dois dumpers são gerados justamente para que
  tabela nova entre nos dois lados sozinha.

  Confirmado de passagem que o FPC aceita literal de string mais curto que o
  `array[0..N] of AnsiChar` e enche com `#0` — os `TXT` do dump saem em hex, e
  batem byte a byte com o C++.

- **Arquivos criados/modificados:**

  - `wte/tools/gen_tables_pas.py` — criado
  - `wte/tools/test_gen_tables_pas.py` — criado (19 testes)
  - `wte/src/we2002_offsets.pas`, `wte/src/we2002_tables.pas` — criados, gerados
  - `wte/tests/test_offsets.pas`, `wte/tests/test_offsets.cpp` — criados, gerados
  - `wte/tools/check_fase2.py`, `wte/re/fase-2.md` — reconciliação, **no mesmo
    commit** desta task: separá-la deixaria um commit com `make -C wte check`
    vermelho, porque o `fase-2.md` só volta a bater depois de as duas unidades
    novas existirem
  - `wte/tests/README.md` — a pasta deixou de estar vazia e de ser só Pascal

- **Problemas encontrados:**

  1. **`Tables.cpp` tem 17 arrays, não 16.** `Tables.cpp:332` define
     `char nomi_squadre[120][20]` — cópia não-`const`, com o nome italiano, de
     `TEAM_NAMES`, que o `extract_legacy_data.py` deixou para trás; não está em
     `Tables.hpp` e ninguém a referencia. Um gerador que varresse o `.cpp`
     emitiria uma tabela fantasma com nome italiano. O gerador passou a **casar
     pelo `.hpp`** e a **abortar** em definição não declarada, salvo entrada na
     lista `UNDECLARED_OK` com motivo escrito — assim tabela nova não some em
     silêncio. A sobra em si é do `newWe2002` e ficou onde está: mexer nela
     obriga a rodar o `ctest` e o golden daquele projeto, e não é escopo desta
     task.

  2. **A tabela de gerado da fase 2 quebrou.** O `check_fase2.py` varria
     `wte/src/*.pas` inteiro; as duas unidades novas caíram na coluna "escrito à
     mão" — porque a marca no cabeçalho delas é a do gerador *delas* — e os
     96.2% da §4.4 viravam 89.4%. O censo passou a excluir `we2002_*.pas`, com a
     razão escrita no próprio `fase-2.md`. Foi para o **mesmo commit** desta task,
     e não para um à parte: o `fase-2.md` só volta a bater depois de as duas
     unidades novas existirem, então separar deixaria um commit com
     `make -C wte check` vermelho.

  3. O gerador chamava `Path.relative_to(ROOT)` na mensagem de recusa, o que
     estourava `ValueError` para os arquivos plantados em `/tmp` — trocava a
     mensagem que o teste mede por um traceback. Virou a função `rel()`.
