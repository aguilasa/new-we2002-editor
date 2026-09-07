# Correções — port em Python do editor de `.mcr` do WE2002

Correções abertas pelo `/revisar` sobre as tasks deste ciclo. O andamento das
**tarefas** fica em [`progresso.md`](/docs/tasks/port-mcr/progresso.md).

**O prefixo deste pool é `CORR-MCR-`**, com numeração contínua a partir de
`001`. O pool é único dentro do ciclo, e não se cruza com o de nenhuma outra
pasta — o ciclo de PES2 tem o seu em
[`/docs/tasks/correcoes-progresso.md`](/docs/tasks/correcoes-progresso.md), e o
ciclo arquivado, o dele em
[`/docs/tasks/concluidos/correcoes-progresso.md`](/docs/tasks/concluidos/correcoes-progresso.md).

## Resumo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
| -- | -------------- | ------ | ----------- | ------ | ------------ |
| [CORR-MCR-001](/docs/tasks/port-mcr/CORR-MCR-001.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | `.claude/rules/tasks.md` afirma que os prompts apontam para `docs/tasks/progresso.md`, o que deixou de ser verdade em 2026-09-07 | Alta | [x] concluída | 2026-09-07 |
| [CORR-MCR-002](/docs/tasks/port-mcr/CORR-MCR-002.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | a verificação de Fase 0 do `perfil-mcr.md` pede um `grep` de escopo que não tem como sair vazio | Alta | [x] concluída | 2026-09-07 |
| [CORR-MCR-003](/docs/tasks/port-mcr/CORR-MCR-003.md) | [MCR-TASK-01](/docs/tasks/port-mcr/01-ciclo-em-subpasta.md) | o link do `progresso.md` no `correcoes-progresso.template.md` aponta para o ciclo raso, contra a própria frase ao lado | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-004](/docs/tasks/port-mcr/CORR-MCR-004.md) | [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | o inventário atribui todo o cache do WebView2 a `bin/`/`obj/`, e 164 arquivos dele são a linha `packages/` | Alta | [x] concluída | 2026-09-07 |
| [CORR-MCR-005](/docs/tasks/port-mcr/CORR-MCR-005.md) | [MCR-TASK-02](/docs/tasks/port-mcr/02-base-legal-e-linhagem.md) | os três `PlayerStatsSkills.dll` são declarados fora da conta e estão dentro da linha "o fonte que importa" | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-006](/docs/tasks/port-mcr/CORR-MCR-006.md) | [MCR-TASK-03](/docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md) | a citação da fixture compartilhada aponta a linha da constante cravada e atribui `WTE_MCR_ENTRADA` a um arquivo que não a tem | Baixa | [x] concluída | 2026-09-07 |

| [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md) | [MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) | o `card.py` está em português e a regra de idioma do código passou a ser en-US | Média | [ ] pendente | — |
**Criticidade:** 🔴 Alta · 🟡 Média · 🟢 Baixa
**Status:** `[ ]` pendente · `[x]` concluída · `[x]` envelhecida

---

## Checklist

- [x] CORR-MCR-001 — reconciliar as duas afirmações de `.claude/rules/tasks.md` sobre para onde os prompts apontam
- [x] CORR-MCR-002 — pôr o escopo medido no `grep` de Fase 0 do `perfil-mcr.md`
- [x] CORR-MCR-003 — levar o link do cabeçalho do `correcoes-progresso.template.md` para `<CICLO>/`
- [x] CORR-MCR-004 — corrigir a atribuição do WebView2 e declarar a profundidade do prefixo na tabela do inventário
- [x] CORR-MCR-005 — separar o que está fora da conta do que está dentro dela e não é fonte
- [x] CORR-MCR-006 — corrigir as duas referências do lado `wte/` e registrar o caminho cravado
- [ ] CORR-MCR-007 — traduzir o `card.py` para en-US e fechar a dívida da §3.5

---

## Detalhes por correção

### CORR-MCR-001

- **Arquivo com problema:** `.claude/rules/tasks.md` (linhas 29 e 176)
- **Sintoma:** a regra afirma, em tempo presente, que os prompts leem
  `docs/tasks/progresso.md`; desde a MCR-TASK-01 os cinco resolvem `<CICLO>` no
  Passo 0. O gêmeo dessa frase no `CLAUDE.md` foi atualizado no mesmo commit.
- **Como foi detectado:** `grep -n 'docs/tasks/progresso.md'
  .claude/rules/tasks.md`, contra o bloco `Passo 0` dos cinco prompts
  (md5 `aa2ef72d…`, idêntico nos cinco), na revisão da MCR-TASK-01.
- **Fix:** trocar o caminho cravado pela pasta resolvida na linha 29, e
  reescrever a linha 176 no espírito do `CLAUDE.md` — a intenção do parágrafo
  (`concluidos/` é história) continua valendo; só o caminho envelheceu.

### CORR-MCR-002

- **Arquivo com problema:** `docs/prompts/perfil-mcr.md` (linha 130)
- **Sintoma:** `grep -rn 'port-mcr' docs/prompts .claude` devolve **11**
  acertos, 7 deles dentro do próprio perfil — inclusive a linha que pede que
  ele saia vazio. O escopo medido pela MCR-TASK-01 devolve **0**.
- **Como foi detectado:** os dois `grep` rodados lado a lado na revisão da
  MCR-TASK-01, contra o critério de conclusão da própria task.
- **Fix:** escrever na linha da Fase 0 o escopo medido
  (`docs/prompts/0*.md docs/prompts/geral.md .claude/commands`) e dizer por que
  `.claude/rules/` e o perfil podem citar o ciclo.

### CORR-MCR-003

- **Arquivo com problema:** `docs/tasks/correcoes-progresso.template.md`
  (linha 3)
- **Sintoma:** o link diz `/docs/tasks/progresso.md` — o ciclo raso — enquanto
  a frase ao lado dele diz "o que mora **ao lado deste arquivo**". O
  instanciado deste ciclo escreve `/docs/tasks/port-mcr/progresso.md`; só o
  molde ficou para trás.
- **Como foi detectado:** leitura do template contra o item do critério da
  MCR-TASK-01; a conferência de existência de link não alcança
  `*.template.md`, e o destino existe de qualquer forma — só é o arquivo
  errado.
- **Fix:** apontar o link do cabeçalho para
  `/docs/tasks/<CICLO>/progresso.md`, como os demais links do mesmo arquivo.

### CORR-MCR-004

- **Arquivo com problema:** `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`
  (tabela "O que não entra, e por quê", célula de razão de `bin/` e `obj/`)
- **Sintoma:** a célula diz que ali mora **todo** o cache do WebView2, "1820
  arquivos e 319.637.837 B". Medido: só **1.656 / 218.698.891** estão sob
  `bin/`+`obj/`; os outros **164 / 100.938.946** são, byte a byte, a linha
  `packages/` da mesma tabela — as categorias são disjuntas, então a
  atribuição contradiz a tabela que ela anota. Junto: a legenda não diz que o
  prefixo casa em qualquer profundidade, e sem isso `.vs/` (20 contra 13 no
  topo) e `packages/` (164 contra 82) não reproduzem.
- **Como foi detectado:** dois `awk` sobre `git ls-tree -r -l HEAD` contra o
  SHA fixado, na revisão da MCR-TASK-02. Todo o resto do inventário remediu
  exato.
- **Fix:** pôr na célula os números medidos de `bin/`+`obj/`, e dizer na
  legenda que o WebView2 **atravessa** duas linhas e que o prefixo casa em
  qualquer profundidade. `NOTICE.md` não precisa de conserto — lá o WebView2
  aparece numa lista de naturezas, sem atribuição a diretório.

### CORR-MCR-005

- **Arquivo com problema:** `docs/tasks/port-mcr/02-base-legal-e-linhagem.md`
  (linha `resto (o fonte que importa)` e a nota logo abaixo dela)
- **Sintoma:** a nota diz que as três cópias de `PlayerStatsSkills.dll` estão
  "fora da conta por não ser arquivo". São arquivo, e estão dentro: 3 dos 72,
  35.328 dos 4.751.336 B. A mesma linha ainda carrega 6 `.jpg` e 2 `.ico`
  (195.476 B) sob a etiqueta "o fonte que importa".
- **Como foi detectado:** decomposição do resto por extensão, com a mesma
  classificação disjunta da tabela; ela fecha em 72 / 4.751.336.
- **Fix:** separar as duas naturezas — o raspador de fato não é arquivo; os
  `.dll` e a arte estão contados e não são fonte — e publicar a decomposição
  por extensão, que é o que torna a linha auditável.

### CORR-MCR-006

- **Arquivo com problema:** `docs/tasks/port-mcr/03-ambiente-fixture-e-qt.md`
  (`Problemas encontrados` §2)
- **Sintoma:** a citação `wte/tools/test_dump_mcr.py:341` é dada como o lugar de
  `WTE_MCR_ENTRADA` e `WTE_MCR_FIXTURE`. Medido: `WTE_MCR_FIXTURE` está na
  **354**, `WTE_MCR_ENTRADA` **não está nesse arquivo** (está em
  `wte/src/impl/ep2002_mainform.FormShow.inc:146` e nos roteiros), e a **341** é
  `ENTRADA = M.ROOT / "work" / "entrada.mcr"` — um caminho **cravado**, que é a
  parte mais afiada da armadilha e ficou sem registro.
- **Como foi detectado:** `grep -n` no arquivo citado e `git grep` da variável
  em `wte/tools` (vazio), na revisão da MCR-TASK-03. Todo o resto do Log
  remediu exato.
- **Fix:** nomear as três formas de alcance com as linhas certas, e dizer que a
  cravada é a razão de o digest ser a régua. O `perfil-mcr.md` não erra — cita
  só as variáveis.

### CORR-MCR-007

- **Arquivo com problema:** `tools/mcr/card.py` (o módulo inteiro)
- **Sintoma:** 17 docstrings, 36 linhas de comentário (mais 9 inline), os 9
  valores de estado de quadro, 15 das 20 chaves do `--json`, as 7 mensagens de
  recusa e os 20 `print` do CLI e do `self_check` estão em português, contra a
  §3.5 do plano, reescrita em 2026-09-07 para **en-US em todo o código do
  port**. Os identificadores **públicos** já são ingleses; os locais
  (`falhas`, `tenta`, `recusa`, `ok`, `nome`, `detalhe`, `excecao`, `trecho`) e
  o default `origin="<memoria>"` não.
- **Como foi detectado:** a decisão de idioma do dono do repositório,
  2026-09-07, aplicada de volta sobre o que a MCR-TASK-04 já havia entregue, e
  remedida por `ast`/`tokenize` na revisão dessa task. **Não é erro de
  execução** — a task cumpriu a regra que existia no dia. Referência: 25 dos 26
  módulos de `tools/pes2/` já estão em inglês.
- **Fix:** traduzir texto e identificadores locais, **preservando a API pública**
  e o comportamento; replantar os cinco controles negativos da MCR-TASK-04 e
  exigir 5/5 vermelhos, com as contagens 2, 8, 1, 1, 1, pelos trechos novos — o
  `recusa()` casa **substring** da mensagem, então traduzir um lado só deixa o
  gate verde por acidente. Depois disso, tirar a "dívida aberta" da §3.5 e a
  exceção do `perfil-mcr.md`.
