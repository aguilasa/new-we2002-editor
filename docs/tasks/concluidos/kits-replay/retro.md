# Retro — kits-replay

Date: 2026-10-19

## Numbers

Tirados de `sh "$RITE_HOME/bin/rite" stats kits-replay --json`:

- Tasks: 19, todas `done`.
- Fixes: 32. Por status: 31 `done`, 1 `stale` (CORR-KRP-007). Por severidade: 0 critical, 0 high,
  17 medium, 15 low.
- Fixes por task: 1,68. Mais fixes por origem: KRP-TASK-06 (5) e KRP-TASK-22 (4).
- Revisão: mediana de 0 dias, máximo de 1 (19 revisadas).
- Por fase: a 2 é a mais cara (5 tasks, 12 fixes); as fases 4 e 4a, juntas, deram 2.

## Root-cause groups

Escrituração: 19. Engenharia: 13. Total: 32.

- **A. O Log cola um resumo ou um comando encurtado, não a saída da ferramenta.** 8, escrituração.
  Os casos: `--json` condensado por um extrator fora do Log, placeholder `<f>`, linha `$` com `…`,
  harness guardado em `work/`, `sh rite` que não roda.
  002, 005, 012, 019, 023, 026, 028, 030.
- **B. Texto escrito pelo esperado ou copiado de outro lugar, sem medir na HEAD.** 5, escrituração.
  Os casos: contagem copiada de um Log anterior, comentário tirado da geometria, explicação desmentida
  pela medição, "diferença do plano" que o plano já previa, data da decisão posta como data do revert.
  003, 007, 017, 021, 032.
- **C. Veredito fechado ou desfeito sem varrer quem o repetia.** 3, escrituração. O doc irmão, a §3.2
  do plano e as duas listas de "decisões já confirmadas" (plano e perfil).
  014, 027, 031.
- **D. Plano editado sem `files` e "Arquivos" no mesmo commit.** 2, escrituração. O modelo de task de
  fechamento dizia "nenhum: só reroda" e pedia "escrito no plano".
  020, 022.
- **E. Âncora escrita à mão.** 1, escrituração. 015.
- **F. Leitor, ramo ou asserção nova sem planta própria, ou planta que a fixture não distingue.**
  5, engenharia. Os casos: quatro leitores sem asserção de chaves, `game_pixels` sem planta, coluna de
  barba sem planta, exit 2 de `--player-looks` sem gate, quadrado simétrico com rotação identidade.
  004, 006, 010, 018, 024.
- **G. Número de sonda descartável que nenhuma ferramenta versionada imprime.** 2, engenharia. As
  CLUTs vizinhas da §3.1 e o `ANIME.BIN` inteiro na RAM do replay. 016, 029.
- **H. Reescrito em vez de reusado.** 2, engenharia. `confront_tab` copiou as flags sem `--kit-set` e
  fixou o caminho do venv do Linux. 011, 013.
- **I. A medida ou o gate depende do ambiente.** 2, engenharia. O timeout de 300 s estava a 86-92% de
  uso, e a altura da vista 3D muda com o comprimento do caminho da imagem. 009, 025.
- **J. Critério do plano julgado só em parte.** 1, engenharia. A virada sai "not judged" contra os
  390 quadros. 008.
- **K. Desvio da API do plano fora da lista de desvios.** 1, engenharia. `Figure.pieces`. 001.

## Proposals

### Keep in next profile

Entradas para `docs/prompts/perfil-kits-replay.armadilhas.md`, que o `/rite:new-cycle` copia com
`--pitfalls-from`:

- **K1 — `--json` vai inteiro, ou a linha `$` roda o modo texto (005, 012, 019, 023, 030).**
  Resumo de extrator, placeholder e `…` não são saída de ferramenta. A entrada existente "Linha `$`
  diferente do que rodou" passa a citar também 002, 026 e 028.
- **K2 — Asserção geométrica pede fixture assimétrica (006).** Use uma fixture assimétrica e com
  rotação diferente da identidade. Com fixture simétrica, espelho e rotação perdida passam verdes.
- **K3 — Leitor ou ramo novo ganha a própria planta (004, 010, 018, 024).** Reaproveitar o juiz de
  outro leitor não cobre as chaves, o buffer escolhido nem o código de saída do leitor novo.
- **K4 — Monte as flags e o caminho do venv com o código do `confront.py` (011, 013).** Importe de lá;
  copiar a lista perde a flag que o original passa.
- **K5 — Fato que sustenta breakpoint ou faixa vira `--check` antes de entrar no plano (016, 029).**
  É o caso de "o arquivo está na RAM" e de "a caixa pega o vizinho".
- **K6 — Desfazer um veredito varre as listas de decisões confirmadas (014, 027, 031).** Varra as do
  plano e as do perfil, e a linha "Feito" da seção. Data do desfazer é a do commit (032).
- **K7 — Gate com margem e medida sem dependência de caminho (009, 025).** O timeout fica em pelo
  menos 1,5× o tempo medido. A vista de confronto se mede com o caminho de imagem fixado.
- **Atualizar** a entrada "Edição fora do `files` declarado" com `proven by` 020 e 022.

### Promote to rite.toml / CLAUDE.md

- **P1 — Na primeira regra entre ciclos do `CLAUDE.md` ("número colado da ferramenta"), acrescentar:
  "`--json` cola o documento inteiro; resumo de extrator, placeholder e linha `$` encurtada contam
  como número reescrito".** O grupo A deu 8 fixes aqui e 3 no `kits-3d` (004, 010, 033), com a regra
  e a armadilha K3 do `kits-3d` já valendo. A forma específica que repetiu é o `--json` condensado.
- **P2 — Na terceira regra ("fechar um veredito é varrer"), pôr na enumeração "as listas de
  decisões confirmadas do plano e do perfil" e "a linha Feito da seção".** O grupo C deu 3 fixes
  aqui, além das 20 do `looks` e das 8 do `port-mcr`. Os lugares que escaparam desta vez não estão
  na lista da regra.
- Os grupos D (2) e F (5) já são regras do `CLAUDE.md`, a quinta e a segunda. Não há lugar mais alto
  no repositório para eles. Ver R1.

### Rite issues (plugin)

Medido no `rite_lib/ops.py` da 0.22.0. **Este ciclo não acrescenta caso a R1**, e o que ele
mostra são dois defeitos do aviso em si:

- **R1, rascunhada no `kits-3d`:** `rite close` registra "Outside declared files" e fecha assim
  mesmo. O #4, fechado na v0.15.1, fez disso um aviso de propósito. Nenhuma fix daqui é caso dela:
  a 020 não teve aviso (R2), e na 022 o plano estava declarado (R3).
- **R2 — `files` vazio desliga o aviso (020).** `ops.py:443` faz
  `_outside_declared(...) if declared else []`. O commit `5a3e0df4` da KRP-TASK-11 mudou o
  `docs/PLAN-KITS-REPLAY.md` com `files` vazio, e o Log não tem a linha "Outside declared files".
  A task que declara menos é a que escapa.
- **R3 — os arquivos de estado do próprio rite contam como fora do escopo (022).** No commit
  `c74ba1cb` da KRP-TASK-22, o `rite set --files` gravou `progress.json` e `progresso.md`, e o
  `close` os listou como fora (linha 215 do arquivo da task). `_outside_declared` isenta só o
  documento do item, e esse ruído treina quem lê a ignorar o aviso.

### Prune

- **Nada a podar.** O perfil tem 7.613 bytes e as armadilhas 3.996 (`wc -c`), sob `max_kb = 84`.
  Nenhuma fix tocou as entradas herdadas "Constante nova acima da docstring", "Receita de gate sem
  caminho absoluto", "Controle físico vazando" e "Reordenou botão". Elas continuam valendo para
  `tools/kits/`, e a próxima fase do projeto mexe ali.

## Applied

Escolha do usuário (2026-10-19):

- **Keep K1 a K7:** gravadas em `docs/prompts/perfil-kits-replay.armadilhas.md`. As entradas "Edição
  fora do `files` declarado" e "Linha `$` diferente do que rodou" ganharam as fixes deste ciclo no
  `proven by`.
- **Promote P1 e P2:** primeira e terceira regras entre ciclos do `CLAUDE.md`, e o retro deste ciclo
  entrou na lista de fontes delas.
- **Issues:** R2 aberta como [aguilasa/rite#20](https://github.com/aguilasa/rite/issues/20) e R3
  como [aguilasa/rite#21](https://github.com/aguilasa/rite/issues/21). R1 continua só rascunho,
  porque este ciclo não traz caso para ela.
- **Prune:** nada.
