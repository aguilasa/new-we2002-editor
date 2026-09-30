# Retro — looks

Date: 2026-09-30

## Numbers

Tudo de `rite stats looks --json`, com o ciclo já arquivado:

- **40 tasks**, 40 feitas, 40 revisadas; atraso de revisão mediano **0 dias**,
  máximo 1.
- **109 correções**, todas fechadas: 0 críticas, **19 altas**, 45 médias, 45
  baixas — **2,73 por task**.
- Fases com mais correção: a 10 (vestido e a tela pintada, 7 tasks, **27**) e a 4
  (2 tasks, 12). As tasks que mais geraram: LOOKS-TASK-14 (9), 17 (7), 38 (6),
  08 e 15 (5 cada).
- **32** correções só de escrituração (grupos 1 a 4 abaixo), **77** de
  engenharia. **0** marcadas *stale*. Nenhum item sem Log.

## Root-cause groups

Por causa, não por sintoma. Cada correção está em um grupo só (109 no total).

| # | causa | tipo | n | correções |
|---|---|---|---|---|
| 1 | a transcrição de gate ou de comando no Log é de antes da última edição, ou não roda como escrita | escrituração | 7 | 032, 036, 041, 075, 076, 091, 093 |
| 2 | um veredito novo entrou num lugar e o texto antigo ficou noutro — docstring, cabeçalho de seção, título, §0, `CLAUDE.md` | escrituração | 20 | 002, 004, 007, 014, 024, 033, 035, 053, 056, 057, 058, 059, 065, 066, 079, 085, 086, 090, 094, 098 |
| 3 | lista de entregas mantida à mão no `progresso.md`, fora da região gerada, que o `rite check` não vê | escrituração | 2 | 080, 089 |
| 4 | trabalho empurrado para correção nova porque o arquivo (`controls.py`) estava com outro worker na mesma onda | escrituração | 3 | 081, 083, 084 |
| 5 | número escrito de memória ou de sonda descartável, sem comando versionado que o imprima | engenharia | 10 | 001, 022, 027, 031, 060, 064, 092, 096, 097, 099 |
| 6 | **um caso medido virou regra** — um slot, uma seção, uma janela, uma lista (a armadilha 19, repetida) | engenharia | 17 | 010, 013, 018, 021, 023, 025, 026, 029, 030, 043, 044, 047, 048, 062, 104, 105, 108 |
| 7 | um campo ligado só ao caso que tinha sido medido (a cabeça 24, a família A, a tupla de cinco) | engenharia | 5 | 034, 039, 049, 103, 109 |
| 8 | **um verificador que passa sem julgar** — sem caso vermelho, veredito impresso e não afirmado, pulo silencioso, função sem chamador | engenharia | 16 | 003, 005, 008, 009, 019, 040, 045, 046, 050, 052, 061, 063, 068, 071, 088, 095 |
| 9 | alvo de `ctest` inalcançável ou que sai 0 sem teste, e preflight que não pula com 77 | engenharia | 4 | 012, 015, 016, 017 |
| 10 | a outra máquina: caminho absoluto, largura de janela salva, fontconfig, interpretador, sessão MCP | engenharia | 6 | 051, 087, 100, 101, 102, 106 |
| 11 | modelo da tela ou da pose montado por suposição onde cabia medir | engenharia | 9 | 020, 028, 037, 038, 042, 054, 067, 070, 107 |
| 12 | saída da ferramenta: mensagem sem dica, contagem errada na linha, código morto, sintaxe que falta | engenharia | 10 | 006, 011, 055, 069, 072, 073, 074, 077, 078, 082 |

**O que os números dizem.** Os dois grupos maiores de engenharia (6 e 8, 33
correções, **8 das 19 altas**) são as duas faces do mesmo método: medir um caso
e escrever a regra, e escrever o verificador sem vê-lo ficar vermelho. O grupo
mais denso em gravidade é o 10: **4 das 6** correções de "a outra máquina" são
altas (100, 101, 102, 106) — todas achadas quando o ciclo rodou pela primeira
vez fora do Windows em que foi escrito. Os de
escrituração são quase todos o mesmo gesto — o texto que alguém lê não foi
reconciliado com a saída que a ferramenta imprime.

## Proposals

### Keep in next profile

Para o perfil do próximo ciclo (o da animação de `FOOT`,
[PLAN-LOOKS-FOOT.md](/docs/PLAN-LOOKS-FOOT.md)), no formato do arquivo de
armadilhas:

- **K1 — Uma medição de uma entrada, um valor e um slot não é a regra.** Antes
  de escrever "a 147 faz X", ela foi andada nos dois slots e nos três valores de
  `FOOT`? Grupos 6 e 7 — 010, 043, 044, 047, 048, 104, 105, 108, 109.
- **K2 — O verificador nasce com o controle vermelho visto.** Toda asserção nova
  tem um defeito plantado em `controls.py` na mesma entrega, e o Log mostra o
  vermelho. Grupo 8 — 009, 040, 046, 063, 068, 095.
- **K3 — Número em Log ou doc sai de comando versionado.** Sonda que produziu
  um número vira opção de uma ferramenta antes do número entrar em texto. Grupo
  5 — 022, 027, 092, 097.
- **K4 — O Log cola a saída da HEAD entregue.** Os gates rodam depois da última
  edição, e a transcrição é colada daí, sem resumo dentro da cerca. Grupo 1 —
  032, 036, 041, 091, 093.
- **K5 — Fechar um veredito é varrer quem dizia o anterior.** Os termos do
  `rite sweep` incluem o número velho e o nome da incógnita, e a varredura olha
  docstrings e cabeçalhos de seção. Grupo 2 — 024, 033, 057, 058, 085, 094, 098.

### Promote to rite.toml / CLAUDE.md

- **P1 — "Número em Log ou doc é colado da ferramenta, na HEAD entregue."** Causou
  correções aqui (grupos 1 e 5, 17 correções) e no ciclo `wte` arquivado — ex.:
  *"o Log da WTE-TASK-17 diz 41 regras de substituição, e o gerador tem 47"*,
  *"o Log da WTE-TASK-18 diz que os testes do transpilador eram 33, e eram 38"*,
  *"o Log da WTE-TASK-22 diz 15 testes no `golden_veredito`, e são 18"*. Destino:
  uma linha na seção "Convenções da documentação" do `CLAUDE.md`.
- **P2 — "Verificador sem vermelho visto não é gate."** Causou correções aqui
  (grupo 8, 16) e no `port-mcr` — *"o julgamento do filtro dos diálogos não tem
  caso vermelho plantado"*. Destino: a mesma seção do `CLAUDE.md`.

### Rite issues (plugin)

Rascunhos; nenhum aberto.

- **I1 — `rite new-fix` escreve o corpo em inglês num repositório `docs_language =
  "pt-BR"`.** 16 das 109 correções (094 a 109) têm `## Problem` / `## Root cause`
  / `## Fix`, as outras 93 `## Problema` / `## Causa raiz` / `## Correção`. Uma
  varredura por `## Causa raiz` perde as 16 sem aviso — foi o que aconteceu ao
  preparar esta retro. Pedido: o `templates/fix.md` segue `docs_language`, ou o
  `rite check` avisa de corpo em idioma diferente do configurado.
- **I2 — O worker restrito aos arquivos declarados empurra edição obrigatória
  para o relatório, e ela só volta como correção nova depois da revisão.** Três
  correções (081, 083, 084) nasceram assim numa onda do `/rite:fix-all`: o
  `controls.py` estava com outro worker. Pedido: o relatório do worker ter um
  campo `followups` que o thread principal transforma em item na mesma corrida,
  ou o planejador de ondas serializar itens que tocam o arquivo de controles do
  ciclo.
- **I3 — Lista de entregas fora da região gerada não é vista pelo `rite check`.**
  080 e 089: a lista "entregas da Fase 10" do `progresso.md` é prosa à mão, e
  ficou atrás três tasks seguidas. Pedido: uma região gerada opcional de
  entregas por fase, a partir de um campo do frontmatter da task.

### Prune

- **R1 — O perfil do `looks` está no teto.** `docs/prompts/perfil-looks.md` tem
  85.288 bytes (`wc -c`), 83,3 dos 84 KiB de `[profile].max_kb`. O ciclo está arquivado,
  então o perfil não cresce mais; o próximo ciclo cita as armadilhas dele em vez
  de copiá-las (é o que a §5 do PLAN-LOOKS-FOOT já diz).
- **R2 — A armadilha 97 e a 104 dizem a mesma coisa de dois lados** (o
  `fit_centre` esconde a mira; o "não medido" que envelhece e deixou a figura
  fora do lugar). Nenhuma correção tocou a 97 depois da 104; ficam as duas, com
  uma remissão da 97 para a 104 — já feita na LOOKS-TASK-35. Nada a podar.

## Applied

Escolhidas em 2026-09-30:

- **P1 e P2** — no `CLAUDE.md`, em "Convenções da documentação", antes da
  região do Rite.
- **K1 a K5** — na §5.1 do [PLAN-LOOKS-FOOT.md](/docs/PLAN-LOOKS-FOOT.md), para
  o `/rite:plan-to-tasks` levar ao perfil do ciclo novo.

Não aplicadas: **I1 a I3** ficam como rascunho (nenhuma issue aberta), e **R1**
e **R2** não pedem edição.
