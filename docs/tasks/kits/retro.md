# Retro — kits

Date: 2026-10-07

## Numbers

De `rite stats kits --json`:

- **Tasks:** 47, todas `done` (0 blocked, 0 skipped).
- **Fixes:** 90, todas `done` (0 stale). Por severidade: 3 high, 45 medium e 42 low.
- **Fixes por task:** 1,91. A mediana até a revisão foi de 0 dias, e o máximo de 1 dia, sobre 47 tasks revisadas.
- **Fixes por fase:**

  | Fase | Tasks | Fixes |
  |---|---|---|
  | 0 | 5 | 10 |
  | 1 | 6 | 14 |
  | 2 | 3 | 2 |
  | 3 | 3 | 5 |
  | 4 | 4 | 6 |
  | 5 | 3 | 4 |
  | 6 | 3 | 5 |
  | 7 | 3 | 6 |
  | 8 | 3 | 7 |
  | 9 | 3 | 4 |
  | 10 | 11 | 27 |

- **Origens com mais fixes:** KITS-TASK-43 (5); as tasks 07, 08, 16, 27 e 46 (4 cada).

## Root-cause groups

Total: 28 de escrituração (A + B) e 62 de engenharia (C a I), somando 90.

- **A — Escopo não declarado: 14, escrituração.**
  - O que aconteceu: uma edição fora do `files` da task. Pode ser uma nota de passagem para outra task, um defeito achado no caminho ou o próprio plano e perfil.
  - IDs: 012, 015, 024, 043, 046, 049, 055, 056, 075, 078, 081, 085, 086, 089.
- **B — Transcrição de Log aparada, parafraseada ou trocada: 14, escrituração.**
  - O que aconteceu: saída cortada sem marca, comando narrado, variável de ambiente fora do comando, caminho encurtado ou hash invertido.
  - IDs: 004, 006, 009, 019, 036, 038, 041, 042, 052, 057, 059, 060, 063, 074.
- **C — Número sem ferramenta versionada na HEAD: 16, engenharia.**
  - Dois casos: sonda descartável (002, 003, 005, 032, 040, 048, 077), ou número de memória, arredondado ou de corrida anterior (013, 022, 025, 030, 034, 051, 069, 072, 083).
- **D — Verificador sem vermelho visto: 23, engenharia.**
  - Três casos: asserção sem planta; veredito impresso e não afirmado; pulo silencioso ou ramo sem chamador.
  - IDs: 008, 014, 017, 020, 021, 027, 028, 031, 037, 039, 044, 045, 047, 053, 058, 061, 064, 067, 073, 076, 082, 084, 087.
- **E — Task fechada com critério sem medida: 4, engenharia.**
  - Três casos: metade de um critério da DoD, resultado negativo tomado como resposta, ou o slot que decide não rodado.
  - IDs: 010, 062, 071, 079. Duas são high (062, 071).
- **F — Veredito mudou e a varredura não chegou a quem dizia o anterior: 8, engenharia.**
  - IDs: 007, 029, 033, 035, 050, 066, 080, 090.
- **G — Constante nova inserida acima da docstring da constante anterior: 3, engenharia.**
  - A docstring passa a documentar a constante errada.
  - IDs: 065, 070, 088.
- **H — Regra de arquitetura (CLI só importa `core/api.py`): 2, engenharia.**
  - IDs: 001, 018.
- **I — Defeito pontual de código ou dado: 6, engenharia.**
  - 011: offset da receita de fixture.
  - 016: quebra de linha perdida.
  - 023: crédito de autor.
  - 026: causa errada do exit 127.
  - 054: `EDITOR_EXE` relativo ao CWD.
  - 068: contagem não exclusiva.

## Proposals

### Keep in next profile

Entradas para `docs/prompts/perfil-kits.armadilhas.md`, no formato do arquivo:

- **K1 — Edição fora do `files` entra por `rite set` no mesmo commit (grupo A, 14 fixes).**
  - Vale para nota de passagem a outra task, defeito achado no caminho e edição de plano ou perfil.
  - Ou se declara (`rite set <ID> --files …` e uma linha em "Arquivos a criar ou modificar"), ou fica fora do commit.
  - O `files` de passagem para task bloqueada é o caso mais frequente: 075, 078, 081, 085, 089.
- **K2 — Constante nova vai abaixo da docstring da anterior (grupo G).**
  - Em `tools/kits/**/*.py` cada constante tem a docstring logo abaixo.
  - Inserir na linha seguinte à constante quebra o par: 065, 070, 088.
- **K3 — Receita de gate no Log com caminhos absolutos e todas as variáveis no comando (063, 060, 034).**
  - O `ctest` roda de `build/tests`, e um `WE2002_LOOKS_IMAGE` relativo não resolve lá.
  - Shell com a variável já exportada produz um Log que não se reproduz.
- **K4 — Juiz afirma o que o critério diz, inclusive onde (087, 047, 082, 073).**
  - Localização ou conjunto impresso e não afirmado conta como gate ausente.
- **K5 — Resultado negativo não fecha critério (071, 079, 062).**
  - Se o instrumento planejado foi trocado, ou o caso que decide não rodou, a task vai para blocked com `--unblocked-by`. Não fecha.

### Promote to rite.toml / CLAUDE.md

- **Nenhuma regra nova.**
  - Os grupos B, C, D e F (61 fixes) já são as quatro regras de "Convenções da documentação" do `CLAUDE.md`, promovidas pelas retros do `looks` e do `port-mcr`.
  - Seguem causando a maior parte das fixes, mas a regra já está no lugar mais alto.
  - O grupo A não tem precedente medido nos ciclos arquivados: a busca por "escopo/declarar" nos `CORR-*` do `looks` e do `port-mcr` não acha caso de `files`. Fica como K1 até repetir.

### Rite issues (plugin)

- **I1 — O `rite reproduce` roda só a primeira linha de um comando com continuação `\`.**
  - Caso medido: a Evidência da CORR-KITS-089 é um `comm -13 \ <(…) \ <(…)`. O `reproduce --all` executou só `R=…`, com exit 0 e saída vazia, e marcou `why: ok`.
  - Saída vazia com `ok` é o que a triagem inline lê como NOT REPRODUCED, e isso marcaria *stale* uma fix real.
  - Pedido: juntar as linhas terminadas em `\`, ou devolver `cannot_decide` quando houver continuação.
- **I2 — O aviso de task de fechamento sugere uma dependência circular, e o próprio CLI recusa aplicá-la.**
  - A KITS-TASK-36 (fase 4) entrou depois do fechamento e depende da KITS-TASK-20.
  - O `rite check` avisa e sugere `rite set KITS-TASK-20 --depends-on …,KITS-TASK-36`, o que fecharia o laço 20 ↔ 36.
  - O `rite set` recusa com `KITS-TASK-20 is done: its dependencies were the order it ran in`, e o aviso fica permanente.
  - Pedido: calar o aviso quando a task da fase já depende da de fechamento.
  - Parente da issue #7 (fechada), que pediu o `--depends-on`; este é o caso que ele não cobre, a task já `done`. O mesmo aviso aparece em `pes2` (PES2-TASK-16 e 35).
- **I3 — Fix aberta com o caminho versionado do plugin na Evidência quebra no upgrade.**
  - As fixes 089 e 090 trazem `R=…/rite/0.15.0/bin/rite`, e o plugin passou à 0.16.0 no meio do ciclo.
  - Pedido: o `rite new-fix` sugerir `$RITE_HOME` ou o nome `rite`, não o caminho do cache.

### Prune

- **P1 — Duas linhas do perfil ficaram velhas com a fase 10.** São as linhas 17 e 31 de `docs/prompts/perfil-kits.md`.
  - Linha 17 diz: "Manga longa e braçadeira só no 3D depois de achadas e medidas; até lá o 3D diz que não as tem".
  - Linha 31 diz: "manga longa/braçadeira/árbitro esperam §4.3 e §4.5".
  - Manga longa e braçadeira foram medidas e desenhadas: KITS-TASK-43, 44, 47 e 40.
  - Proposta: só o árbitro continua esperando (§4.5).
- **O perfil está no tamanho:** 8.881 bytes (`wc -c`), sob o `max_kb = 84` e sob a meta de 12 KiB do comentário do `rite.toml`.

## Applied

Escolha do usuário (2026-10-07):

- **Keep K1 a K5:** gravadas em `docs/prompts/perfil-kits.armadilhas.md`.
- **Prune P1:** linhas 17 e 31 do perfil atualizadas; só o árbitro segue esperando (§4.5).
- **Issues I1 a I3:** pedido abrir com `gh issue create`, e **não foram abertas**.
  - O GitHub devolveu `500 Internal Server Error` em toda criação de issue em `aguilasa/rite`, pelos três caminhos: GraphQL, REST e MCP.
  - Foi em 2026-10-07, por volta das 15:15 UTC. Um teste com título descartável deu o mesmo 500.
  - Os três textos acima são os rascunhos, para abrir depois.
