# Prompt para execução de tarefas em lote

Você vai trabalhar no repositório localizado em:

- **Raiz do projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`
- **Arquivo de progresso:** `docs/tasks/progresso.md`. **O prefixo dos IDs de
  task é do ciclo, e quem o declara é este arquivo** — hoje `PES2-TASK-XX`,
  antes `WTE-TASK-XX`. Abaixo ele aparece como `<PREFIXO>`; leia-o ali, não
  o deduza do que este prompt escreve como exemplo nem de citação a task
  antiga.
- **Tarefas detalhadas:** `docs/tasks/`
- **Fonte de verdade:** **a que a própria task declarar** no campo
  `fonte_de_verdade` do frontmatter. Este prompt não conhece plano nenhum pelo
  nome — a task em mãos é quem diz contra o que ela se mede.
- **Regras do repositório:** `CLAUDE.md` — leia antes de tocar em qualquer coisa

---

## Objetivo

Executar **N tarefas pendentes** nesta invocação, em ordem de fase e de
dependência, paralelizando só o que a matriz de conflito autoriza. `N` é **2**
por padrão.

Este prompt é o irmão em lote do [`/docs/prompts/01-executar.md`](/docs/prompts/01-executar.md).
**Ele relaxa exatamente uma regra daquele — "uma tarefa por invocação" — e
nenhuma outra.** Tudo o mais continua valendo palavra por palavra:

- ordem de fases, ordem numérica dentro da fase, `depends_on` conferido;
- antecipação de tarefa fora da vez só com pedido **explícito** do usuário —
  os precedentes do ciclo estão no perfil;
- escopo da tarefa não se alarga nem antecipa fase seguinte;
- tarefa que produz arquivo gerado produz **o gerador, o `--check` e a saída**;
- `✅ Concluído` só depois do commit, e descreve estado já commitado;
- `status: pendente` → `status: concluído` no frontmatter do markdown da tarefa;
- Log de Execução preenchido no markdown da tarefa;
- coluna "Revisado em" vai para `⬜ pendente`, **nunca** para uma data;
- commit em inglês, conventional, sem footer de co-autoria, sem `git add -A`;
- `roms/` intocada, `we-team-editor.exe` leitura pura, nada de decompilado
  colado, nada de editar à mão o que um gerador produz.

Em dúvida sobre qualquer ponto não coberto aqui, o `01-executar.md` é a fonte.

> **EXCLUSÃO OBRIGATÓRIA — sem CORRs:**
> Este prompt é exclusivo para `<PREFIXO>-TASK-XX`, com o prefixo que o
> `progresso.md` declarar. **Nunca** execute uma correção
> (`CORR-<PREFIXO>-XXX`, com o prefixo que o `correcoes-progresso.md` declarar)
> por aqui — elas são do `03-corrigir.md` / `04-corrigir-tudo.md` e rastreadas
> em `correcoes-progresso.md`.

> **EXCLUSÃO OBRIGATÓRIA — lote tem tamanho, e o tamanho é pequeno:**
> Não existe "executar tudo". O padrão é 2, o usuário pode pedir outro número,
> e ponto. Lote grande não é feature: cada tarefa deste projeto termina em
> commit próprio e em gate medido, e um lote que atravessa uma fase inteira
> entrega um `progresso.md` que ninguém consegue auditar depois.

> **EXCLUSÃO OBRIGATÓRIA — respeitar as decisões confirmadas:**
> Nunca use o lote como desculpa para editar à mão arquivo que um gerador
> produz, colar saída de decompilador em spec ou em código, ou escrever no que o
> perfil marca como **leitura pura** (o binário alvo, `roms/`). As "decisões já
> confirmadas" do perfil do ciclo valem aqui inteiras.

---

## Argumentos

| `$ARGUMENTS` | Significado |
| --- | --- |
| vazio | **2** tarefas — as duas próximas prontas |
| só dígitos (`3`) | esse número de tarefas |
| IDs (`<PREFIXO>-TASK-03 <PREFIXO>-TASK-05`) | esse conjunto, ainda em ordem de dependência |
| `--plano` | pare depois da fase 0 e entregue só o plano |
| número **e** IDs juntos | **erro** — pergunte ao usuário qual dos dois vale |

Se houver menos tarefas prontas do que `N`, execute as que houver e **diga
isso**. Nunca complete o lote com tarefa cuja dependência não fechou, e nunca
troque a ordem para caber mais.

---

## "Em lote" não é "em paralelo"

São duas coisas diferentes, e confundi-las torna este prompt inútil na fase 4.

- **Lote** é quantas tarefas a invocação fecha: `N`.
- **Paralelo** é quantas rodam ao mesmo tempo: o que a matriz de conflito
  deixar, que às vezes é **uma**.

Um lote de 2 em que as duas serializam no `:98` roda em sequência, e está
correto. A economia ali não é de tempo de máquina — é de rito: um plano, um
inventário, uma varredura de discrepância no fim.

O paralelismo de verdade paga onde as tarefas são **extração estática**:
leitura pura sobre o binário, cada uma escrevendo o seu próprio arquivo. Esse é
o lote canônico deste comando, e o perfil do ciclo diz quais fases têm essa
forma.

---

## Fase 0 — inventário e plano (sempre, e sempre primeiro)

1. Ler `docs/tasks/progresso.md` — a **tabela de resumo** e o **checklist da
   fase**. Se as duas listas divergirem, a divergência é o primeiro achado do
   relatório; não escolha uma em silêncio.
2. Listar as `⬜ Pendente` na ordem: fase 0 antes da 1, antes da 2, …, e dentro
   da fase por ID crescente.
3. Filtrar por `depends_on` **satisfeito** — usar o grafo do `progresso.md`.

> **A ordem é a do `progresso.md`, lida de cima para baixo.** Este prompt não a
> recalcula nem conhece prefixo de ID: onde houver `phase:` no frontmatter, ela
> ordena dentro da tabela; onde não houver, vale a ordem escrita. Tarefa marcada
> ❌ não é selecionável. Cada uma declara a própria fonte no campo
> `fonte_de_verdade` — leia a dela, não um plano fixo.
   Dependência que só fecharia dentro deste mesmo lote **não** conta como
   satisfeita para efeito de seleção paralela; ela força ordem.
4. Se existir tarefa `🔄 Em andamento`, ela é a primeira do lote.
5. Pegar as `N` primeiras prontas.
6. Ler **só o cabeçalho** do markdown de cada uma (frontmatter, Contexto/
   Objetivo, "Arquivos a criar ou modificar", Critério de conclusão) para
   montar o conjunto de arquivos previsto. O escopo de arquivo continua valendo
   **dentro** de cada execução: ao executar a 03 você não abre a 05.
7. Montar a **matriz de conflito** e derivar as ondas.
8. Imprimir o plano antes de tocar em arquivo: lote, ondas, o que é paralelo, o
   que é sequencial, e **por que** cada par ficou sequencial.

### Tarefa de fechamento nunca divide lote com dependência sua

As tarefas 09, 14, 21, 29, 34 e 40 fecham fase e dependem de tudo que veio
antes. O filtro de `depends_on` já as segura, mas fica escrito porque o erro é
tentador: fechar a fase 1 "junto com" a 08 entrega um fechamento que mediu um
estado que ainda ia mudar.

---

## Matriz de conflito — o que pode e o que não pode em paralelo

Duas tarefas só rodam em paralelo se **todas** as condições valerem:

- nenhuma depende da outra;
- os conjuntos de arquivos previstos são **disjuntos**;
- nenhuma das duas toca um **recurso serializado** da tabela abaixo.

### Recursos serializados (uma tarefa por vez, sempre)

| Recurso | Por que serializa |
| --- | --- |
| **o `DISPLAY=:98`** | não há window manager, e os dois lados do golden acham a janela por heurística. Duas sessões de GUI simultâneas dirigem a janela uma da outra, e o diff resultante parece bug do port |
| o gate de comportamento / `work/` | cópias de centenas de MB por rodada, num diretório de trabalho único. Duas rodadas simultâneas leem a cópia da outra |
| Wine / `work/wineprefix*` | prefix único por editor; `wineserver` compartilhado |
| qualquer gerador em modo de escrita | regenera a árvore inteira — duas execuções simultâneas leem a saída da outra |
| saída de build | objetos compilados e binário únicos |
| projeto do Ghidra | banco de dados único, escrita exclusiva |
| `git` (index, `HEAD`, commit) | **sempre no thread principal**, nunca dentro de subagente |
| `docs/tasks/progresso.md` | toda tarefa escreve nele — tabela, checklist, duas colunas de data. É o arquivo mais garantido de colidir |
| o arquivo de build do ciclo | quando a bateria de `--check` mora num alvo só, **toda tarefa que cria gerador acrescenta um alvo ali** — e várias querem a mesma mão no mesmo arquivo. O perfil diz se o ciclo tem esse arquivo e qual é |
| o arquivo de `fonte_de_verdade` de duas tasks do lote | tarefa que reconcilia número do plano colide com irmã que lê o mesmo |

**A serialização do `:98` é a mais restritiva deste projeto.** Na prática,
**toda tarefa que exercita o oráculo, roda o golden ou tira captura é
sequencial**: as 12, 13, 22, 25 a 27, 30, 34 e 37, entre outras.

O caso exemplar é o par **12 e 13**: o grafo do `progresso.md` diz "em paralelo"
— e diz certo, porque nenhuma depende da outra. A matriz diz **sequencial**,
porque as duas dirigem janela no `:98`. Quando o grafo e a matriz divergem,
**a matriz manda**: o grafo fala de dependência lógica, a matriz fala de
recurso físico.

### Arquivos quentes (presumir conflito)

Além dos serializados, presuma conflito em qualquer par que possa cair nos
mesmos: `CLAUDE.md`, o plano do ciclo, os registros técnicos que o **perfil**
listar como quentes, `docs/prompts/*` (os perfis inclusive),
`.claude/commands/*`.

**Na dúvida, sequencial.** O ganho de paralelizar duas extrações é de minutos; o
custo de duas edições concorrentes no mesmo `.md` é uma reconciliação manual e
um número que ninguém remede.

### O que é sempre seguro em paralelo

**A leitura de contexto e a extração estática.** Rodar `objdump`, `strings`,
`grep`, `cmp`, `git show`, `--check`, e ler plano, task e registro técnico. É o
que torna a fase 1 o lote canônico.

**Ressalva:** leitura que exige **abrir o oráculo no `:98`** não é leitura pura
para efeito de paralelismo — ela ocupa o display. Essas vão em série.

---

## Fase 1 — ler o contexto do lote inteiro (paralelo)

Para cada tarefa do lote, e podendo ser um subagente por tarefa, **read-only**:

- ler o markdown da tarefa por inteiro;
- ler o que o campo `fonte_de_verdade` da task apontar, o **perfil do ciclo**,
  e os registros técnicos que ela citar;
- se a tarefa depende de outra já concluída, **reler o artefato real** que
  aquela produziu — o markdown descreve a intenção, e a execução pode ter
  adaptado;
- conferir se o markdown da tarefa ainda bate com o estado real (número que
  mudou, ferramenta que não existe mais, endereço reclassificado).

Três desfechos:

| Resultado | O que fazer |
| --- | --- |
| bate | entra no lote de execução |
| o markdown envelheceu | **adapte, corrija o markdown, registre no Log de Execução.** Divergência entre doc e ferramenta é achado, não ruído |
| a tarefa mudou de tamanho, ou a dependência não entregou o que dizia | tire do lote e reporte. Redimensionar tarefa de afogadilho no meio de um lote é pior que no singular |

Tarefa fora do lote **não bloqueia** as outras, a menos que alguém dependa dela.

---

## Fase 2 — executar, onda a onda

Para cada onda, na ordem:

1. Executar as tarefas da onda — em paralelo se a matriz permitir, senão em
   sequência. Cada execução segue o `01-executar.md` §"Como executar" passos 2 e
   3: exatamente o escopo da tarefa, e os critérios de conclusão do markdown
   dela.
2. **Os subagentes editam; quem commita é o thread principal.** Subagente não
   roda `git`, não roda o build do ciclo, não roda o gate de comportamento, não
   roda gerador em modo de escrita, não abre janela no `:98`, e **não escreve no
   `progresso.md` nem no arquivo de build do ciclo**. Tarefa que precisa de um desses é
   sequencial por definição — está na tabela de recursos serializados.
3. As edições do arquivo de build da onda inteira são aplicadas pelo thread
   principal, uma por uma, **depois** que os geradores da onda existem. Cada
   alvo novo vai no commit da sua tarefa, não num commit avulso.
4. Rodar os gates aplicáveis, **uma tarefa por vez**, mesmo que a edição tenha
   sido paralela.
5. Commitar, **um commit por tarefa**, em ordem de ID crescente dentro da onda.
   Reconciliação de doc que não pertence a nenhuma tarefa vai em commit próprio,
   dizendo no corpo qual tarefa a provocou.
6. Marcar o progresso daquela tarefa (seção abaixo). Só **depois** do commit.

### Gates por fase

Os mesmos do `01-executar.md`:

| Fase | Gate obrigatório |
| --- | --- |
| todas | todo número novo em doc veio de **ferramenta**, não de contagem à mão |
| todas | `roms/` **intocada**; o que se mede, se mede sobre cópia |

**O gate obrigatório de cada fase está no perfil do ciclo**, na seção "gates".
Os dois de cima valem para qualquer fase de qualquer ciclo, e por isso ficam
aqui.

**O controle vem antes do teste.** Original contra original tem de dar zero
divergência, e um byte plantado tem de ser detectado com o offset certo. Sem os
dois, verde e vermelho não significam nada.

### Marcação de progresso, por tarefa

Depois do commit daquela tarefa, e para ela só:

- `⬜ Pendente` → `✅ Concluído` no `progresso.md`, **tabela E checklist da
  fase**;
- **"Concluída em"** com a data do commit **daquela** tarefa
  (`git log -1 --date=short --pretty=%ad`), formato `AAAA-MM-DD`. Num lote as
  tarefas podem cair em dias diferentes: a data é **por tarefa**, nunca a do
  fechamento do lote;
- célula do ID como link `[<PREFIXO>-TASK-XX](/docs/tasks/XX-nome.md)` — sempre
  `/docs/` + caminho do arquivo, ver `.claude/rules/links.md`;
- **"Revisado em"** de `—` para `⬜ pendente`. **Não escreva data aí** — quem
  revisa é o `/revisar`, em invocação separada;
- `status: pendente` → `status: concluído` no frontmatter do markdown da tarefa;
- **Log de Execução** no markdown da tarefa: data, resumo do que se **aprendeu**,
  arquivos criados/modificados, problemas encontrados.

Tarefa parcial **não** vira `✅ Concluído` — registre no Log o que ficou
pendente e diga isso na saída.

### Depois de cada commit, antes do próximo

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git status --short          # limpo para a tarefa que acabou
grep -rn "<o termo que voce mudou>" docs .claude CLAUDE.md \\
  <as pastas de codigo que o perfil nomear>
```

**A varredura de discrepância se repete a cada tarefa, não uma vez no fim.** Num
lote, a tarefa *k+1* costuma tornar falso um doc que a *k* acabou de escrever.

### Quando uma tarefa falha no meio do lote

- Não marque `✅ Concluído`. Registre o status parcial e as pendências no Log de
  Execução, e commite o que estiver **coerente** (se nada estiver, não commite).
- **Não aborte o lote.** Siga para as tarefas que não dependem dela.
- Se o que falhou for um gate global (o build do ciclo não compila, o gate de
  comportamento
  vermelho no **controle**, `ctest` do `newWe2002` quebrado), aí **pare o
  lote**: gate global quebrado contamina toda tarefa seguinte, e commit em cima
  disso é dívida que ninguém acha depois.

O caso mais provável de gate global quebrado aqui é o **controle do golden**: se
original contra original não fecha, o problema é do harness ou do `:98`, não das
tarefas — e nenhum resultado do lote significa nada até isso voltar.

---

## Fase 3 — fechamento do lote

1. `git status --short` limpo.
2. `git log --oneline` do lote, para conferir um commit por tarefa (mais os de
   reconciliação).
3. Conferir que a tabela e o checklist do `progresso.md` concordam, e que toda
   linha `✅ Concluído` tem data, link e `⬜ pendente` em "Revisado em".
4. Conferir os links de doc, se algum markdown ganhou link novo:

   ```bash
   grep -rnoE '\]\([^)]*\.md[^)]*\)' --include='*.md' docs | grep -v '](/docs/'
   ```

5. Varredura final de discrepância pelos termos de todas as tarefas do lote.
6. Se alguma tarefa ficou de fora (parcial, bloqueada, redimensionada), ela
   aparece no relatório — nunca some em silêncio.
7. Conferir que `work/` não ficou com cópia de imagem esquecida — cada rodada de
   golden deixa ~950 MB para trás.

**O lote deixa mais de uma tarefa esperando revisão.** É esperado: o `/revisar`
pega uma por invocação, a de **menor ID** entre as `⬜ pendente`. Não tente
revisar nada por aqui.

---

## Formato de saída esperado

1. **O plano** — lote selecionado e por quê, ordem de dependência, ondas, e a
   justificativa de cada par que ficou sequencial
2. **Fase 1** — por tarefa: o que o contexto mostrou, e se o markdown envelheceu
3. Por tarefa executada: resumo, arquivos criados/modificados, gates com o
   **resultado medido**, e o **SHA do commit**
4. As tarefas que ficaram de fora, com o motivo
5. `git status --short` limpo e o `git log --oneline` do lote
6. **O que o lote ensinou que vale para o próximo.** Se nada surpreendeu, diga
   isso
7. Bloqueios e pendências

---

## Regra final

Não me entregue um plano e pare — a menos que `$ARGUMENTS` diga `--plano`.
Execute exatamente `N` tarefas (2 por padrão), um commit por tarefa,
`✅ Concluído` só depois do commit.
Paralelize só o que a matriz de conflito autoriza; **na dúvida, sequencial** — e
o `:98` é sempre sequencial.
Nada de correção (`CORR-*`), nada de decompilado colado, nada de editar à mão o que um
gerador produz, nada de escrever no `.exe` ou em `roms/`.
`push` só se o usuário pedir.
