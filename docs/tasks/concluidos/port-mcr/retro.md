# Retro — port-mcr

Date: 2026-09-30

## Numbers

Tudo de `rite stats port-mcr --json`, com o ciclo já arquivado:

- **17 tasks**, 17 feitas, 17 revisadas; atraso de revisão mediano **0 dias**,
  máximo 0.
- **30 correções**, todas `done` (`grep -h '^status:' CORR-*.md`: 30 × `done`,
  nenhuma *stale*): 0 críticas, **12 altas**, 1 média, 17 baixas — **1,76 por
  task**.
- Fases com mais correção: a 5 (3 tasks, **9**) e a 0 (3 tasks, 6). As tasks que
  mais geraram: MCR-TASK-17 (5), 01, 10 e 16 (3 cada).
- **14** correções só de escrituração (grupos 1, 2, 5, 8, 10 e 11 abaixo), **16**
  de engenharia. Nenhum item sem Log.

## Root-cause groups

Por causa, não por sintoma. Cada correção está em um grupo só (30 no total).

| # | causa | tipo | n | correções |
|---|---|---|---|---|
| 1 | o critério mudou numa task e o texto que o descrevia ficou em outro arquivo — regra, perfil, template, plano, a entrada da fase no perfil | escrituração | 5 | 001, 002, 003, 013, 022 |
| 2 | **um total que vive copiado em prosa em mais de um documento** — controles vermelhos, alvos de `ctest`, resultado da bateria limpa — e a task atualiza uma parte das cópias | escrituração | 3 | 017, 021, 024 |
| 3 | contagem escrita de cabeça, ou do caso que estava na mão, em vez de enumerada por conteúdo | engenharia | 4 | 010, 023, 026, 028 |
| 4 | a frase afirma outra coisa do que a medição mediu — o menor início como o único, o comportamento no jogo como a diferença de bytes, duas exclusões sob a mesma razão | engenharia | 4 | 004, 005, 027, 029 |
| 5 | referência por posição ou por linha que não aponta onde diz | escrituração | 2 | 006, 016 |
| 6 | **um verificador que passa sem julgar** — nome que promete mais do que a asserção, varredura que não desce, juiz que usa a aritmética do código sob teste, caso vermelho em script descartável, erro de import que impede o próprio self-check | engenharia | 5 | 008, 012, 014, 018, 025 |
| 7 | controle negativo anotado pelo efeito em prosa, não pela substituição literal que o produz — e não reproduz | engenharia | 2 | 009, 011 |
| 8 | idioma do arquivo: código anterior à decisão de en-US, e bloco reescrito no idioma de quem escrevia a doc | escrituração | 2 | 007, 019 |
| 9 | widget que recorta usado como validação: o `QSpinBox` mostra 10 onde o cartão diz 15 | engenharia | 1 | 020 |
| 10 | a fase pede captura no Log e a sessão correu na tela do usuário, sem gate que capturasse | escrituração | 1 | 030 |
| 11 | bloco novo do `CMakeLists.txt` inserido entre o comentário de outro teste e o teste | escrituração | 1 | 015 |

**O que os números dizem.** O grupo mais denso em gravidade é o 6: **4 das 5**
correções de verificador que não julga são altas (012, 014, 018, 025), e o 2 tem
as **3** altas das 3. Os dois juntos são 7 das 12 altas do ciclo. O 2 é
escrituração só na forma: o número que diverge é o do gate, e quem o lê decide se
o gate está verde. Os grupos 3 e 4 são o que o `looks` chamou de "um caso medido
virou regra" (grupo 6 de lá), aqui no terreno de engenharia reversa do option
file — a MCR-TASK-17 sozinha deu 4 deles (026 a 029).

## Proposals

### Keep in next profile

O próximo ciclo em Python + PySide6 é o dos uniformes,
[PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md), com a mesma forma deste — núcleo puro,
UI separada, controles plantados. No formato do arquivo de armadilhas:

- **K1 — Um total tem uma casa só.** Contagem de controles, de alvos de `ctest` e
  o resultado da bateria limpa aparecem em **um** documento, colado da
  ferramenta; os outros remetem ao comando que o imprime. Grupo 2 — 017, 021,
  024.
- **K2 — O juiz não sai do código sob teste.** O valor esperado de um check vem
  de fora da aritmética que ele julga, e o nome do check diz exatamente o que a
  asserção afirma ("e nada mais" exige asserção de exclusividade). Grupo 6 — 012,
  018.
- **K3 — Varredura de escopo recursivo desce, e prova que desce.** `os.walk`, não
  `os.listdir`, e o controle planta o defeito numa subpasta. Grupo 6 — 014.
- **K4 — Controle negativo é substituição literal versionada.** A tabela de
  controles registra o `old → new` exato, e o motor que o planta mora no
  repositório, não num script descartável. Grupo 7 e 6 — 009, 011, 025.
- **K5 — Amostra se conta por conteúdo.** Cartões, imagens, padrões: por digest,
  não por arquivo nem pelos que a task usou; a frase diz "o menor", não "todos".
  Grupos 3 e 4 — 026, 027, 028.
- **K6 — Mudou o critério, reconcilia na mesma task.** Perfil, regra, plano e a
  entrada da fase em "Verificações específicas por fase" — fase nova nasce com
  ela. Grupo 1 — 002, 013, 022.

### Promote to rite.toml / CLAUDE.md

- **P1 — "Fechar um veredito é varrer quem dizia o anterior."** Causou correções
  aqui (grupos 1 e 2, 8 correções) e no `looks` (grupo 2 de lá, 20 correções:
  *"um veredito novo entrou num lugar e o texto antigo ficou noutro"*). Era o K5
  do `looks`, guardado para um perfil; com dois ciclos, sobe. Destino: uma linha
  em "Convenções da documentação" do `CLAUDE.md`, ao lado das duas regras da
  retro do `looks`.
- **P2 — "Um caso medido não é a regra; amostra se conta por conteúdo."** Causou
  correções aqui (grupos 3 e 4, 8 correções) e no `looks` (grupos 6 e 7, 22).
  Destino: a mesma seção do `CLAUDE.md`.

Reforçadas, sem edição: as duas regras que a retro do `looks` promoveu hoje
("número colado da ferramenta" e "verificador sem vermelho visto não é gate")
explicam os grupos 6 e 7 daqui — 025 é citada naquela promoção. Todas as
correções deste ciclo são anteriores a ela.

### Rite issues (plugin)

Rascunhos; nenhum aberto. Todos medidos nesta sessão, com o plugin 0.11.0.

- **I1 — O caminho do arquivo de armadilhas ignora o `profile:` do ciclo.** O
  `progresso.md` declara `profile: /docs/prompts/perfil-mcr.md`, e o
  `rite resolve-cycle port-mcr --json` devolve esse perfil, mas deriva
  `"pitfalls": "docs/prompts/perfil-port-mcr.armadilhas.md"` do nome do ciclo
  (`pitfalls_exists: false`). Um ciclo cujo perfil tem outro nome que a pasta
  nunca acha as armadilhas ao lado dele. Pedido: derivar do perfil resolvido
  (`perfil-mcr.armadilhas.md`), ou aceitar `pitfalls:` no frontmatter.
- **I2 — O `rite archive` reescreve o alvo do link, e não o texto.** Depois do
  `5fe42b5b`, o `CLAUDE.md` tinha `[docs/tasks/port-mcr/](docs/tasks/concluidos/port-mcr/progresso.md)`
  e três trechos dizendo que o ciclo era vivo; foi preciso um commit à mão
  (`397e8826`). No arquivo arquivado sobram `progresso.md:13` (*"Pasta deste
  ciclo: `docs/tasks/port-mcr/`"*) e `perfil-mcr.md:133,179`. Pedido: o
  `archive` avisar (`--json` → `stale_mentions`) das ocorrências do caminho
  antigo que ficaram em prosa e em texto de link, sem reescrevê-las.
- **I3 — `rite archive --dry-run` não pré-visualiza a reescrita.** O dry-run deu
  `"rewritten": []`; a corrida real, sobre a mesma árvore, reescreveu **43**
  arquivos. A confirmação que o `/rite:close-cycle` pede ao usuário fica sem a
  informação que a justificaria. Pedido: o dry-run calcular e listar `rewritten`.

### Prune

- **R1 — `[profile].max_kb = 84` perdeu o motivo.** O comentário diz que o teto
  foi erguido até o maior perfil legado e deve voltar para perto de 12; o maior
  era o do `looks` (85.981 bytes, `wc -c docs/prompts/perfil-*.md`), agora
  arquivado. O maior perfil de ciclo vivo é o do `pes2`, com 26.082. Proposta:
  `max_kb = 28` — **antes**, conferir se `rite check --all --include-archived`
  mede perfil de ciclo arquivado, porque então o `looks` ficaria vermelho.
- **R2 — O perfil `perfil-mcr.md` não tem o que podar.** 18.366 bytes, ciclo
  arquivado, não cresce mais; fica como registro. O que vale levar adiante está
  no K1 a K6, que o próximo ciclo cita em vez de copiar o perfil.

## Applied

Escolhidas em 2026-09-30:

- **P1 e P2** — no `CLAUDE.md`, em "Convenções da documentação", depois das
  duas regras da retro do `looks`; o parágrafo que as introduz passou a citar as
  duas retros.

Não aplicadas: **K1 a K6** ficam aqui, para o `/rite:plan-to-tasks` dos
uniformes citar; **R1** (`max_kb`) fica como proposta; **I1 a I3** ficam como
rascunho (nenhuma issue aberta); **R2** não pede edição.
