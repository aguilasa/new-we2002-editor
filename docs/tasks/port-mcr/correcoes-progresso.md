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
| [CORR-MCR-007](/docs/tasks/port-mcr/CORR-MCR-007.md) | [MCR-TASK-04](/docs/tasks/port-mcr/04-conteiner-do-cartao.md) | o `card.py` está em português e a regra de idioma do código passou a ser en-US | Média | [x] concluída | 2026-09-07 |
| [CORR-MCR-008](/docs/tasks/port-mcr/CORR-MCR-008.md) | [MCR-TASK-05](/docs/tasks/port-mcr/05-layout-e-cross-check.md) | destino faltando mata o `layout.py` no import, e a tabela de controles não diz que ali o `--self-check` não roda | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-009](/docs/tasks/port-mcr/CORR-MCR-009.md) | [MCR-TASK-06](/docs/tasks/port-mcr/06-codec-de-atributos.md) | a tabela dos cinco controles descreve o defeito em prosa, e duas das cinco contagens de falha não reproduzem | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-010](/docs/tasks/port-mcr/CORR-MCR-010.md) | [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md) | o plano diz que **um** nome enche os dez bytes e são dois: os slots 5 e 20 | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-011](/docs/tasks/port-mcr/CORR-MCR-011.md) | [MCR-TASK-07](/docs/tasks/port-mcr/07-dorsais-e-nome.md) | a tabela de controles voltou à prosa, e a linha que ela descreve aparece duas vezes no arquivo | Baixa | [x] concluída | 2026-09-07 |
| [CORR-MCR-012](/docs/tasks/port-mcr/CORR-MCR-012.md) | [MCR-TASK-09](/docs/tasks/port-mcr/09-modelo-e-round-trip.md) | o check chamado "e nada mais" só afirma que algum byte mudou, e a exclusividade do caminho do dorsal fica sem guarda | Alta | [x] concluída | 2026-09-08 |
| [CORR-MCR-013](/docs/tasks/port-mcr/CORR-MCR-013.md) | [MCR-TASK-09](/docs/tasks/port-mcr/09-modelo-e-round-trip.md) | a §3.2 do plano ainda põe `Card` como dataclass do `model.py`, não cita o `Save`, e a task atribui a frase à §5.1 | Baixa | [x] concluída | 2026-09-08 |
| [CORR-MCR-014](/docs/tasks/port-mcr/CORR-MCR-014.md) | [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) | a varredura da Regra 1 e a de idioma usam `os.listdir` e param no topo: a `tools/mcr/ui/` da MCR-TASK-11 fica invisível para as duas | Alta | [x] concluída | 2026-09-08 |
| [CORR-MCR-015](/docs/tasks/port-mcr/CORR-MCR-015.md) | [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) | o bloco do `mcr_ui` entrou entre o comentário do `pes2_boot` e o `add_test` dele, e o `pes2_boot` ficou sem comentário | Baixa | [x] concluída | 2026-09-08 |
| [CORR-MCR-016](/docs/tasks/port-mcr/CORR-MCR-016.md) | [MCR-TASK-10](/docs/tasks/port-mcr/10-selftest-cli-e-gate.md) | "os três últimos nasceram na MCR-TASK-10" aponta `cli`/`selftest`/`ui_check`, e os três são `harness`/`controls`/`ui_check` | Baixa | [x] concluída | 2026-09-08 |

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
- [x] CORR-MCR-007 — traduzir o `card.py` para en-US e fechar a dívida da §3.5
- [x] CORR-MCR-008 — registrar o efeito do erro de import na tabela de controles e exigir o `attempt()` em volta do import no `selftest`
- [x] CORR-MCR-009 — trocar a prosa dos controles pela substituição literal, e reconciliar as duas contagens
- [x] CORR-MCR-010 — nomear os dois slots que enchem os dez bytes, no plano e na task
- [x] CORR-MCR-011 — pôr a substituição literal na tabela da 07 e subir a convenção para o perfil
- [x] CORR-MCR-012 — fechar o conjunto de bytes no check do dorsal, nos dois módulos, com o caso vermelho
- [x] CORR-MCR-013 — pôr `Player`/`Save` na §3.2 do plano e corrigir a citação de seção na task
- [x] CORR-MCR-014 — descer as duas varreduras com `os.walk`, e registrar o caso vermelho da `ui/` como controle
- [x] CORR-MCR-015 — pôr cada `add_test` sob o comentário que o descreve
- [x] CORR-MCR-016 — nomear os três módulos novos em vez de apontá-los por posição

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

### CORR-MCR-008

- **Arquivo com problema:** `docs/tasks/port-mcr/05-layout-e-cross-check.md`
  (tabela dos seis controles) e `docs/tasks/port-mcr/10-selftest-cli-e-gate.md`
  (o critério que falta)
- **Sintoma:** nos dois controles que **tiram** um destino da tabela, o
  `_required()` levanta `LayoutError` no **import** e o `--self-check` sai por
  traceback — nenhuma das 29 asserções roda. O veredito é o certo e o Log o
  registra, mas não diz que ali o harness não chegou a começar. Adiante isso
  vira risco: se o `mcr_selftest` da MCR-TASK-10 — o gate **obrigatório** —
  importar `layout` no escopo do módulo, uma tabela quebrada derruba a corrida
  inteira em vez de virar uma falha nomeada.
- **Como foi detectado:** os seis controles replantados na revisão da
  MCR-TASK-05, dentro da árvore para o `--check` achar o `wte/re/mcr.md`. 6/6
  vermelhos, `rc=1`; as contagens 3, 1, 1, 3 batem, e o 18º destino precisa ir
  **no fim** da lista para dar 3.
- **Fix:** dizer na tabela de controles o que acontece com o `--self-check` nas
  linhas 1 e 3, e pôr na MCR-TASK-10 o critério de importar `layout` dentro do
  `attempt()`. O `layout.py` não muda: falhar no import é o comportamento certo
  para o módulo cuja razão de existir é a tabela.

### CORR-MCR-009

- **Arquivo com problema:** `docs/tasks/port-mcr/06-codec-de-atributos.md`
  (tabela dos cinco controles negativos)
- **Sintoma:** os cinco vereditos reproduzem (5/5 🔴, `rc=1`) e as três
  contagens de blobs batem exatamente — 87.484, 100.000, 93.748 —, mas duas das
  cinco contagens de falha não: o `speed`/`dribbling` trocado dá **2** e não 4,
  e o `stamina` movido um bit dá **5** e não 6. O defeito está descrito pelo
  efeito pretendido, não pela substituição literal, e "trocar dois campos no
  encoder" tem mais de uma leitura — o `encode_stream` é dirigido por tabela e
  ali a troca mudaria o decoder junto.
- **Como foi detectado:** os cinco controles replantados na revisão da
  MCR-TASK-06, numa cópia dentro da árvore com `PYTHONPATH=tools/mcr`. Todo o
  resto da task remediu exato, inclusive fora da ferramenta: as 29 expressões
  de `Player::Decode` transcritas à mão dão 0 divergências em 100.000 blobs, a
  tripwire lida com leitor próprio dá 23/23, e três tabelas de peso do upstream
  conferem contra o `Frmmcr.designer.vb`.
- **Fix:** escrever a edição exata em cada linha da tabela e reconciliar as duas
  contagens; registrar que a cópia plantada precisa de `PYTHONPATH` apontando
  `tools/mcr`, senão morre em `ModuleNotFoundError` antes de medir. E deixar
  uma linha na MCR-TASK-10 para os controles virarem subcomando do `selftest`,
  onde a contagem passa a ser medida em vez de anotada.

### CORR-MCR-010

- **Arquivo com problema:** `docs/PLAN-MCR-PY.md` §1.6 (linha 167) e
  `docs/tasks/port-mcr/07-dorsais-e-nome.md`
- **Sintoma:** os dois dizem que **o slot 20** enche os dez bytes. São **dois**:
  o slot 5 (`ジｮｰ･ﾛﾚﾝｿﾝ`) também, e o próprio `text.py --check` marca os dois
  com `<-- fills all ten bytes`. A afirmação de invariante continua certa; a
  enumeração é que está incompleta, e é ela que um teste copia.
- **Como foi detectado:** varredura independente da cópia da fixture na revisão
  da MCR-TASK-07 — `[j for j in range(23) if 0 not in nome(j)]` devolve
  `[5, 20]`.
- **Fix:** nomear os dois no plano e na task, e dizer que a contagem sai da
  ferramenta.

### CORR-MCR-011

- **Arquivo com problema:** `docs/tasks/port-mcr/07-dorsais-e-nome.md` (tabela
  dos seis controles) e `docs/prompts/perfil-mcr.md` (onde falta a convenção)
- **Sintoma:** as seis contagens estão **certas** — 7, 7, 2, 16, 1, 2,
  replantadas e reproduzidas —, mas a descrição de uma delas não identifica a
  linha, e `raw = int.from_bytes(table, "little")` existe **duas vezes**: na
  `decode_table` (linha 70) e na `encode_table` (93). Plantar na primeira dá 6
  falhas em vez de 2, e o leitor conclui que o Log erra.
- **Como foi detectado:** os seis controles replantados na revisão da
  MCR-TASK-07; o N3 precisou de duas tentativas.
- **Fix:** escrever a substituição e a **função** onde ela mora, e subir a
  convenção da CORR-MCR-009 para o perfil, que é onde as tasks 08 a 14 a leem
  antes de começar.

### CORR-MCR-012

- **Arquivo com problema:** `tools/mcr/model.py:285` (e o par em
  `tools/mcr/mcrio.py:384`)
- **Sintoma:** o check se chama "a number touches the record and the table, and
  nothing else" e a condição é `len(moved) > 0`. Uma escrita perdida em
  qualquer lugar do cartão o satisfaz. O check do atributo comum, doze linhas
  acima, mede exclusividade de verdade com `all(...)` — o caminho do dorsal,
  que é o único que grava em **dois** lugares, é o único sem essa asserção.
- **Como foi detectado:** plantio em `Save._write_number` que escreve um byte
  nos dez intocados do jogador 5 **só quando o dorsal muda** — sobrevive ao
  round-trip, que regrava os mesmos valores. Os dois `--self-check` saem
  `rc=0`, `FAIL=0`, e o check nomeado diz `ok`; só o
  `mcrio.py --edit-probe 0 number 30` mostra, reportando **3** bytes
  (`0x05404`, `0x05907`, `0x059ba`) contra os 2 do Log.
- **Fix:** fechar o conjunto nos dois módulos — os destinos legítimos são o
  registro de 12 bytes e os 4 grupos da tabela de 5 bits — e pôr o plantio na
  tabela de controles da task, como substituição literal com a função.

### CORR-MCR-013

- **Arquivo com problema:** `docs/PLAN-MCR-PY.md` linha 295 (§3.2) e
  `docs/tasks/port-mcr/09-modelo-e-round-trip.md` (critério de conclusão)
- **Sintoma:** a árvore de módulos do plano diz `model.py  Card / Player /
  Formation -- dataclasses`; o que existe é `Player` e `Save` no `model.py`,
  `Card` como classe comum no `card.py` e `Formation` no `formation.py`. O
  `Save` não aparece no plano inteiro. A task registra a divergência e a
  justifica — corretamente —, mas a atribui à **§5.1**, que é o round-trip e
  não nomeia classe nenhuma.
- **Como foi detectado:** `grep -n "model.py" docs/PLAN-MCR-PY.md` e
  `grep -n '\bSave\b' docs/PLAN-MCR-PY.md` (vazio) durante a revisão da
  MCR-TASK-09; o commit `16a0ae0` editou a linha logo abaixo dessa.
- **Fix:** levar a decisão ao plano — o inventário passa a nomear `Player` e
  `Save`, e a dizer onde `Card` e `Formation` moram — e corrigir a citação de
  seção na task para §3.2.

### CORR-MCR-014

- **Arquivo com problema:** `tools/mcr/layout.py` (`address_monopoly`) e
  `tools/mcr/glossary.py` (`sweep`)
- **Sintoma:** as duas enumeram com `os.listdir` e não descem. A pasta
  `tools/mcr/ui/`, que a **MCR-TASK-11** cria a seguir, sai do escopo das duas
  sem aviso — enquanto a metade da Regra 3 que testa import **desce** e passa a
  reportar `ok` sobre ela. O critério desta task escreve o escopo como
  `tools/mcr/**.py`, e `**` é recursivo.
- **Como foi detectado:** um `_probe.py` plantado em `tools/mcr/ui/` com
  `0x62A8` e `25266` (as duas notações que a `address_monopoly` diz varrer) e
  com `jugador`/`cancha` (que estão no dicionário): `--rule1` dá 0,
  `glossary.py` dá 0, `selftest.py` dá 0 falhas e `ctest -R mcr_selftest`
  passa. O mesmo arquivo apontado à mão é acusado com 4 queixas.
- **Fix:** `os.walk` nas duas, caminho relativo nas mensagens, e o plantio na
  `ui/` registrado como controle no `controls.py` — senão o caso deixa de ser
  exercitável assim que a pasta existir de verdade.

### CORR-MCR-015

- **Arquivo com problema:** `tests/CMakeLists.txt`, linhas 136-155
- **Sintoma:** o `if(UNIX AND Python3_FOUND) … mcr_ui` entrou **entre** o
  comentário do `pes2_boot` e o `add_test` dele. Quem lê o `mcr_ui` atravessa
  cinco linhas sobre DuckStation, `PES2_IMAGE` e noventa segundos; o
  `pes2_boot` ficou sem comentário. Os dois blocos ainda dizem "third …
  bracket" sobre coisas diferentes.
- **Como foi detectado:** leitura do arquivo na revisão da MCR-TASK-10, com
  `grep -n "^# \|add_test(NAME" tests/CMakeLists.txt`. O comportamento dos
  dois testes está certo — 1 passed, 2 skipped —, o defeito é de leitura.
- **Fix:** mover um dos dois blocos inteiro, comentário junto, e nomear o
  projeto em cada frase "third bracket".

### CORR-MCR-016

- **Arquivo com problema:** `docs/PLAN-MCR-PY.md` linha 309 (§3.2)
- **Sintoma:** "**Os três últimos nasceram na MCR-TASK-10**" — os três últimos
  da lista são `cli.py`, `selftest.py` e `ui_check.py`; os três que a task
  criou, e que o próprio parágrafo então explica, são `harness.py`,
  `controls.py` e `ui_check.py`. Os dois primeiros foram inseridos no meio da
  lista.
- **Como foi detectado:** diff do bloco contra `68e55a2^` durante a revisão da
  MCR-TASK-10.
- **Fix:** nomear os três na abertura em vez de apontá-los por posição — nome
  resiste a reordenação, posição não.
