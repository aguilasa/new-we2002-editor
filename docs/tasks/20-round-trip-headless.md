---
id: WTE-TASK-20
title: "Round-trip headless contra o we2002_core, nas duas ROMs"
type: verificação
category: dados
phase: 3
depends_on: ["WTE-TASK-18", "WTE-TASK-19"]
status: concluído
---

# WTE-TASK-20: Round-trip headless

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` §4.2 (oráculo B), §6 e Fase 3
  itens 5 e 6.
- É o **aceite da fase 3**, e o primeiro momento em que o projeto afirma algo
  verificado sobre dados.

O oráculo aqui não é o `wte.exe` — é o `we2002_core`, cujo `Load`/`Save` já é
byte-idêntico ao `ed.exe`. Comparação campo a campo, não por olho.

### A dependência da WTE-TASK-19 é a parte que já veio

Esta task rodou com a
[WTE-TASK-19](/docs/tasks/19-os-50-offsets-restantes.md) ainda em aberto, e
isso foi **ordem, não resultado**: nenhum dos seis critérios daqui toca o
oráculo A. O registro dessa decisão mora no
[`progresso.md`](/docs/tasks/progresso.md), na nota *"A WTE-TASK-20 foi
executada antes de a 19 fechar"* — é lá que o estado das duas se lê, em vez de
repetido aqui.

O que a 20 precisaria da 19 são os offsets novos, e esses vieram: dos 50
`OFS_*` que a WTE-TASK-06 marcou `ausente`, **33 estão endereçados** por
execução e os **17** restantes — 14 `retomada de fronteira` e 3 `base de
varredura` — têm veredito estrutural tirado do `Database.cpp`. E **os 50
entram no dump desta task**: são todos nomes do nosso
`src/core/include/we2002/Offsets.hpp`, portanto todos têm lado C++. `ausente`
ali quer dizer *não casa com a tabela em `.data` do `wte.exe`*, não *falta no
`we2002_core`*.

Quem o `we2002_core` de fato não tem são as **faixas sem dono** — regiões que o
`wte.exe` endereça e nenhum `OFS_*` explica, como os 16 setores contíguos da
camisa em `21168024`..`21203815`. Essas não podem aparecer num diff de dump
Pascal × dump C++ nem se estivessem medidas, porque não há lado C++ para elas.
Continuam pendentes, e a região da camisa tem dono declarado: a
[WTE-TASK-29](/docs/tasks/29-camisa-e-bandeira-2d.md). O que **não** pode
acontecer é esta task afirmar cobertura sobre elas.

---

## Objetivo

Um programa de console em Pascal que abre a ROM, lê tudo, e um comparador que
confronta com o `we2002_core`.

### 1. O dumper Pascal

Emite, em formato estável e diffável, todo o estado que a camada de dados
carrega: times, jogadores, times de ML, formações predefinidas, números de
camisa, cobradores, links.

### 2. O dumper C++

O equivalente do lado do `we2002_core`. O repositório já tem
`tests/golden_tool.cpp` headless; ou se estende, ou se escreve um irmão.

### 3. O comparador

`diff` dos dois dumps. **Zero divergência** é o critério — diferente do golden
test de imagem, que aceita a faixa conhecida de 16 bytes. Aqui é leitura pura:
não há comportamento indefinido para preservar.

### 4. As duas ROMs

| ROM | O que valida |
|---|---|
| `roms/golden-european-deluxe.bin` | offsets, nomes latinos, **os ramos de mapeamento do codec** |
| `roms/japanese-shift-jis.bin` | **o ramo padrão do codec**: katakana vira espaço |

> **Corrigido na execução.** Este enunciado dizia que a japonesa é *o único
> teste real do codec de texto*, e medido é o contrário. O `KanjiToAscii` só
> conhece os bytes de chefe 130 (`0x82`, latino de largura dupla) e 129
> (`0x81`, o ponto); a European Deluxe guarda `82 68 82 8e …` → `Inter`, e a
> japonesa guarda `83 41 83 43 …`, que é katakana e cai no ramo padrão. São
> 95 de 95 campos decodificados na europeia contra 0 de 95 na japonesa. As
> duas continuam necessárias — por motivos trocados. Medida em
> [`../../wte/re/fase-3.md`](../../wte/re/fase-3.md).

### 5. Round-trip de gravação

Além de ler: gravar com a camada Pascal e comparar com a gravação do
`we2002_core` a partir do mesmo estado. Aqui a comparação é **byte a byte da
imagem**, e agora sim vale a ressalva conhecida — o `Save` reconstrói as
all-star. *(A ressalva sobre não-idempotência que esta linha trazia era do
`ed.exe`, não do `wte.exe` — medido pela
[CORR-WTE-109](/docs/tasks/CORR-WTE-109.md) em 2026-08-25.)*

### 6. `--check` na bateria

Os `--check` dos geradores das tasks 16, 17 e 18 registrados onde a
WTE-TASK-02 decidiu que a bateria mora.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/tests/dump_estado.pas` | criar — **em `tests/`, não em `tools/`**: é programa compilado, e a convenção do [`../../wte/tests/README.md`](../../wte/tests/README.md) é essa |
| `wte/tests/dump_estado.cpp` | criar — o irmão, em vez de estender o `tests/golden_tool.cpp` do `newWe2002` |
| `wte/tools/compare_dumps.py` | criar |
| `wte/re/fase-3.md` | criar, **gerado** |

---

## Critério de conclusão

- [x] Dump Pascal e dump C++ idênticos nas **duas** ROMs, zero divergência
      — 66.498 linhas por lado, **0 divergências** em cada ROM
- [x] Codec de texto exercitado — **e a premissa deste enunciado corrigida**:
      quem exercita os ramos de mapeamento é a europeia (95 de 95), e a
      japonesa exercita o ramo padrão (0 de 95)
- [x] Round-trip de gravação byte a byte, com a ressalva das all-star registrada
      — **0 bytes** de divergência Pascal × C++; contra o original, 270 B em 4
      faixas (europeia) e 1.249 B em 15 (japonesa), que é a ressalva
- [x] Bitfield de `SquadNumbers` conferido contra imagem real (§8.11)
      — as duas formas no dump (23 desempacotados + as 4 palavras cruas), 64
      de 64 registros não zerados nas duas ROMs
- [x] `--check` dos três geradores na bateria de testes
      — `gen_tables_pas.py`, `port_database_pas.py` e agora `compare_dumps.py`
      entram pelo `wildcard` do `wte/Makefile`; `make -C wte check` rc=0
- [x] Trabalhado só sobre cópia; `roms/` intocada
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-10

- **Resumo do que foi feito:**

  **Zero divergência nas duas metades, nas duas ROMs, na primeira corrida.** O
  par de dumpers escreve o mesmo formato (`chave = valor`, vetor de bytes em
  `<n>:<hex>` cortado no último byte não-zero — sem perda, já que o resto é
  zero por definição) e o `diff` saiu vazio: 66.498 linhas de cada lado. O
  round-trip de gravação também: `Load`+`Save` do Pascal e do C++ produzem
  imagens byte a byte iguais.

  **O que se aprendeu, e não estava no enunciado:** a premissa do codec estava
  invertida. A task dizia que a ROM japonesa é *o único teste real* do
  `KanjiToAscii`; medido, ela é o teste do **ramo padrão**. O codec, portado
  verbatim de `edDlg.cpp:732-809`, só conhece o byte de chefe 130 (`0x82`,
  latino de largura dupla) e 129 (`0x81`, o ponto) — a European Deluxe guarda
  `82 68 82 8e …` e decodifica `Inter`; a japonesa guarda `83 41 83 43 …`, que
  é katakana e vira espaço. São **95 de 95** decodificados na europeia contra
  **0 de 95** na japonesa. As duas continuam necessárias, por motivos
  trocados. O enunciado foi corrigido e o achado está preso em teste
  (`test_a_premissa_do_codec_esta_invertida`).

  **A guarda que faltava e entrou:** zero contra zero não prova nada. Se o
  `Save` parasse de gravar, as duas imagens continuariam iguais e o critério
  passaria verde. Por isso o TSV mede também o round-trip **contra o
  original** — 270 B em 4 faixas na europeia, 1.249 B em 15 na japonesa —, e
  um teste exige que esse número seja maior que zero. Essa coluna é a
  ressalva das all-star: o `Save` reconstrói as squads a partir dos links e o
  original troca os dois primeiros cobradores de cada clube de ML.

- **Arquivos criados/modificados:**

  | Arquivo | Ação |
  |---|---|
  | `wte/tests/dump_estado.pas` | criado — o dumper Pascal, com `--roundtrip` |
  | `wte/tests/dump_estado.cpp` | criado — o irmão do lado `we2002_core` |
  | `wte/tools/compare_dumps.py` | criado — compila, roda, compara, gera o `fase-3.md` |
  | `wte/tools/test_compare_dumps.py` | criado — 16 testes |
  | `wte/re/fase-3.md` | criado, **gerado** |
  | `wte/re/fase-3.tsv` | criado — a evidência |
  | `wte/tools/README.md`, `wte/tests/README.md` | atualizados |
  | `docs/tasks/20-round-trip-headless.md` | corrigido: a premissa do codec e os caminhos dos arquivos |

- **Problemas encontrados:**

  **Duas divergências entre o enunciado e o estado real, as duas registradas
  em vez de contornadas em silêncio:**

  1. o enunciado põe `dump_estado.pas` em `wte/tools/`. A convenção do
     `wte/tests/README.md`, estabelecida pela WTE-TASK-16, é que **programa
     compilado mora em `tests/`** e o driver Python em `tools/`. Além de
     convenção, é obrigação técnica aqui: o `wildcard` do `wte/Makefile`
     enumera `tools/*.py`, e um `.pas` ali seria inofensivo, mas o par ficaria
     separado do `test_offsets.*`, que é exatamente o mesmo padrão;
  2. o enunciado admite estender o `tests/golden_tool.cpp` do `newWe2002`.
     Escrevi um irmão. O escopo daquele projeto está fechado e verificado, e o
     `golden_tool` é a metade do gate dele; um binário à parte, compilado com
     `g++` direto sobre `src/core/*.cpp`, não toca nisso — e mantém o `wte/`
     independente do CMake da raiz, como decidiu o `wte/README.md`.
     `ctest -E golden` do `newWe2002` continua verde, e `git status` de
     `src/` e `tests/` está limpo.

  **`Sofifa.cpp` fica fora da lista de fontes C++** de propósito: é o único do
  núcleo que puxa libcurl, e nada do estado despejado vem dele. Incluí-lo faria
  o dumper deixar de compilar numa máquina sem a lib, por nada. Há teste para
  isso.

  **A medição não entra no `make check`.** São quatro cópias de ~474 MB; o
  alvo roda em segundos e tem de continuar assim. O `--check` confere o texto
  gerado contra o TSV, e a remedição completa fica sob `WTE_ROUNDTRIP=1`, que
  **pula com mensagem** em vez de passar em silêncio. Medido: a remedição
  reproduz o TSV byte a byte.
