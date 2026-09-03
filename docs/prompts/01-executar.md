# Prompt para execução de tarefas

Você vai trabalhar no repositório localizado em:

- **Raiz do projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`
- **Arquivo de progresso:** `docs/tasks/progresso.md`. **O prefixo dos IDs de
  task é do ciclo, e quem o declara é este arquivo** — hoje `PES2-TASK-XX`,
  antes `WTE-TASK-XX`. Abaixo ele aparece como `<PREFIXO>`; leia-o ali, não
  o deduza do que este prompt escreve como exemplo nem de citação a task
  antiga.
- **Fonte de verdade:** **a que a própria task declarar** no campo
  `fonte_de_verdade` do frontmatter. Este prompt não conhece plano nenhum pelo
  nome, e não deve passar a conhecer — ver "A fonte de verdade mora na task"
  abaixo.
- **Tarefas detalhadas:** `docs/tasks/`
- **Regras do repositório:** `CLAUDE.md` — leia antes de tocar em qualquer coisa

- **Perfil do ciclo:** o que o campo `perfil:` do `progresso.md` nomear.
  **Leia-o antes de executar** — dele vêm as decisões confirmadas, as
  armadilhas, as fontes binárias, o que é gerado, os gates e os arquivos
  quentes deste ciclo. Este prompt tem o **rito**, e é agnóstico de projeto.

---

## Objetivo

Quero que você:

1. Leia `docs/tasks/progresso.md`
2. Identifique a **próxima tarefa não executada**, respeitando a ordem:
   - Fase 0 (infra) antes da 1 (extração estática), antes da 2 (casca), antes da
     3 (dados), antes da 4 (comportamento), antes da 5 (features), antes da 6
     (paridade), antes da 7 (acabamento)
   - Dentro da fase, seguir a ordem numérica (01, 02, …)
   - Verificar se as dependências declaradas em `depends_on` já estão
     concluídas — ver o grafo em `progresso.md`
3. Abra o markdown detalhado da tarefa em `docs/tasks/` — ver mapeamento abaixo
4. Leia o que o campo `fonte_de_verdade` do frontmatter apontar, e os demais
   docs que a task citar na seção "Contexto"
5. Execute a tarefa
6. Ao final, atualize o `progresso.md` marcando a tarefa como `✅ Concluído`
   (tabela de resumo E checklist da fase), e **preencha a coluna "Concluída
   em"** com a data do commit que fechou a tarefa
7. Preencha o **Log de Execução** no arquivo da tarefa: data, resumo, arquivos
   criados/modificados, problemas encontrados

---

## A fonte de verdade mora na task

**Este prompt é agnóstico de projeto.** Ele sabe ler o `progresso.md`, abrir o
markdown da tarefa e fazer o que ela pede — nada além disso. Não há plano,
fase ou prefixo de ID codificado aqui, e acrescentar um é regressão.

Duas consequências práticas:

| você precisa de | onde está |
|---|---|
| o arquivo da tarefa | **o link na tabela do `progresso.md`** — toda linha tem um |
| o que a tarefa considera verdade | **o campo `fonte_de_verdade`** do frontmatter dela |

O `fonte_de_verdade` é um caminho `/docs/...` mais a seção, e é **obrigatório**
em toda task. Se faltar, ou apontar para arquivo inexistente, **pare e
informe** — task que não diz contra o que ela se mede não é executável, e
adivinhar o plano pelo prefixo do ID é exatamente o acoplamento que esta seção
existe para impedir.

*(Houve aqui uma tabela `ID → arquivo` com as 51 linhas, e ela saiu em
2026-08-28. Ela duplicava os links que o `progresso.md` já tem — o próprio
prompt admitia isso na frase "se esta tabela divergir do `progresso.md`, o
`progresso.md` manda". Duplicata que se declara perdedora é duplicata que só
espera para envelhecer.)*

---

## Regras de seleção da tarefa

1. Procurar a **primeira tarefa com `⬜ Pendente`** no `progresso.md`, **na ordem
   em que o arquivo as apresenta** — de cima para baixo, tabela a tabela. O
   `progresso.md` é quem define a ordem; este prompt não a recalcula. Onde
   houver `phase:` no frontmatter, ela ordena dentro da tabela; onde não
   houver, vale a ordem escrita
2. Verificar se todas as tarefas em `depends_on` estão concluídas — se não,
   **não executar**, e informar o bloqueio
3. Se existir tarefa `🔄 Em andamento`, priorizar concluí-la
4. **Antecipação.** Tarefa fora da vez só entra com **pedido explícito do
   usuário**, `depends_on` inteiramente concluído e razão escrita.

   O padrão que autoriza: **tarefa de fase adiante que uma tarefa da fase
   corrente precisa**. Renumerar resolveria, mas mover uma task arrasta as
   vizinhas; antecipar com pedido explícito custa uma linha. Sem esse padrão,
   não antecipe.

   **Os precedentes do ciclo estão no perfil**, com a razão de cada um — leia-os
   antes de propor um novo, porque é neles que o critério fica concreto.
5. Dentro de uma fase, várias tarefas podem estar prontas ao mesmo tempo (as
   03-07, por exemplo, só dependem da 02). **Execute só uma** — a de menor ID

---

> **EXCLUSÃO OBRIGATÓRIA — uma tarefa por execução:**
> Este prompt executa **exatamente uma tarefa** por invocação.
> Nunca execute duas tarefas em paralelo nem em sequência na mesma invocação.
> Após concluir e commitar a tarefa selecionada, **pare imediatamente**.
> Não avance para a próxima tarefa pendente — aguarde nova invocação.

A exclusão acima vale para **este** prompt e não tem exceção aqui. Quem executa
mais de uma tarefa por invocação é o irmão em lote,
[`/docs/prompts/05-executar-lote.md`](/docs/prompts/05-executar-lote.md) (o
comando `/executar-lote`) — que relaxa essa regra e **só** ela, e cuja seleção,
ordem, gates e marcação de progresso continuam sendo os deste arquivo. Se você
foi invocado por aqui, o lote não é opção: uma tarefa, e pare.

---

## Contexto essencial — está no perfil do ciclo

**Leia o perfil antes de tocar em qualquer arquivo.** Ele traz as **decisões já
confirmadas** — coisas que não devem ser revertidas sem o usuário pedir — e as
**armadilhas medidas** do ciclo, cada uma tendo custado tempo real. Este prompt
não as repete, porque elas mudam com o ciclo e ele não.

Se a task em mãos declarar um `fonte_de_verdade` de outro projeto, leia o dela:
as decisões do perfil continuam valendo como contexto do repositório, não como
critério da tarefa.

Três armadilhas valem para o **repositório inteiro**, não para um ciclo, e por
isso ficam aqui:

1. **Cópia, sempre.** Os editores gravam in-place e cada imagem tem centenas de
   MB. **Nunca apontar nada para `roms/`.**
2. **Janela esquecida no `:98` derruba gate de GUI.** Os dois lados de um golden
   acham a janela por heurística; uma sobra de teste manual é dirigida em vez da
   que está sob teste, e o diff parece bug do port. Feche tudo antes.
3. **Todo número em doc vem de ferramenta**, não de soma à mão nem de script
   descartável que ninguém guardou.

Mais duas de GUI, que o `CLAUDE.md` detalha: `xdotool type --window` embaralha
string longa (usa `XSendEvent` — digite curto), e `xdotool windowactivate`
falha no Xvfb, que não tem window manager (dirija por coordenada absoluta).

---

## Arquitetura — o que vem do perfil

O perfil do ciclo traz, e você precisa dos cinco antes de executar:

| Do perfil | O que decide |
| --- | --- |
| **as fontes de verdade binárias** | o que é leitura pura, o que é sempre cópia, e o que pode ser escrito e sob que condição |
| **os oráculos, se houver** | contra o que a tarefa se mede. Um ciclo pode não ter nenhum — aí a evidência é outra, e o perfil diz qual |
| **o que é gerado, e por qual gerador** | corrigir arquivo gerado à mão não conta: a correção entra no gerador |
| **os gates** | quais rodar, e a partir de quando cada um existe |
| **os arquivos quentes** | onde a varredura de discrepância costuma esbarrar |

Estrutura comum a qualquer ciclo:

```text
new-we2002-editor/
  docs/
    tasks/                 # tasks, CORRs e progresso
    prompts/               # estes prompts + os perfis de ciclo
  roms/                    # imagens de teste (gitignored)
  work/                    # copias de trabalho (gitignored)
```

E dois comandos que valem para o repositório, não para um ciclo:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
make run-98         # abre o newWe2002 (o port Qt) no :98
make test           # ctest do newWe2002, sem os golden
```

### A regra do Xvfb — obrigatória

Toda execução com GUI acontece no `DISPLAY=:98`. O `:1` é a sessão real do
usuário. **Era o `:99` até 2026-08-20**; a troca foi a pedido do usuário,
porque outro projeto desta máquina (`World-Of-Football`) mantém uma janela de
1024×768 no `:99` e a guarda de janela grande do gate — que existe justamente
para não dirigir a janela errada — passou a recusar toda corrida.

O servidor sobe **sem `-auth`**, então `XAUTHORITY` vazio é o certo:

```sh
export DISPLAY=:98
export XAUTHORITY=$(ps -o args= -C Xvfb \
  | sed -n 's/.*Xvfb :98 .*-auth \([^ ]*\).*/\1/p' | head -1)
```

Servidor levantado por `xvfb-run` **tem** cookie próprio, e sem apontar o
`XAUTHORITY` para ele o Qt e o Wine morrem com
`Invalid MIT-MAGIC-COOKIE-1 key`. As ferramentas tratam os dois casos sozinhas
(`roteiro.sh`, `make run-98`), e o número mora numa variável por ferramenta:
`XVFB`, `WTE_DISPLAY`, `GOLDEN_DISPLAY`.

Se por qualquer motivo não der para usar o `:98`, **pergunte antes** de cair
para o `:1`. Ver a seção do topo do `CLAUDE.md`.

**Registro histórico continua dizendo `:99`** — `CORR-*`, logs de execução e
prosa de medição descrevem o que aconteceu, e reescrevê-los falsificaria o
registro.

## Como executar

### 1) Ler contexto

- Ler `docs/tasks/progresso.md`
- Ler o markdown da tarefa — o link está na linha dela, na tabela do progresso
- Ler o que o campo `fonte_de_verdade` do frontmatter apontar, e os demais docs
  que a task citar na seção "Contexto"
- Se a task depender de outra concluída, **reler o artefato real** que ela
  produziu — o markdown descreve a intenção, e a execução pode ter adaptado

### 2) Executar

- Executar exatamente o escopo da tarefa
- Não alterar escopo nem antecipar trabalho de outra fase. Implementar handler é
  fase 4; fórmula de preço é fase 5. **Fechar um lote por inteiro vale mais que
  abrir três**
- Se a tarefa produzir arquivo gerado, ela produz **o gerador**, o `--check` e
  a saída — os três, não só a saída

### 3) Validar

Antes de marcar como concluída, verificar os **critérios de conclusão** do
markdown da tarefa.

Checklist geral por fase:

**O gate obrigatório de cada fase está no perfil do ciclo**, na seção "gates",
junto com a disponibilidade de cada ferramenta. Dois valem para **todas** as
fases de qualquer ciclo, e por isso ficam aqui:

| Fase | Gate obrigatório |
| --- | --- |
| todas | todo número novo em doc veio de **ferramenta**, não de contagem à mão |
| todas | `roms/` **intocada**; o que se mede, se mede sobre cópia |

**O controle vem antes do teste.** Original contra original tem de dar zero
divergência, e um byte plantado tem de ser detectado com o offset certo. Sem os
dois, verde e vermelho não significam nada.

Se a tarefa ficar parcialmente pronta:
- Não marcar como concluída no `progresso.md`
- Registrar no Log de Execução o que ficou pendente

**Resultado negativo é resultado legítimo.** Uma task de extração que conclui
"esta unidade VCL é dependência transitiva, não é usada" entregou exatamente o
que devia. Registre como resultado, não como falha.

### 4) Atualizar progresso

Se concluída:
- Trocar `⬜ Pendente` por `✅ Concluído` no `progresso.md` (tabela E checklist
  da fase)
- Preencher a coluna **"Concluída em"** com a data do commit que fechou a
  tarefa (`git log -1 --date=short --pretty=%ad`), formato `AAAA-MM-DD`. Data
  de commit, não data de hoje — quem lê o histórico depois cruza a tabela com o
  `git log`
- Conferir que a célula do ID é **link para o markdown da tarefa**, no formato
  `[<PREFIXO>-TASK-XX](/docs/tasks/XX-nome-do-arquivo.md)` — **sempre no formato
  `/docs/` + caminho do arquivo**, nunca relativo, como manda
  `.claude/rules/links.md`. Linha de tabela sem link é defeito,
  mesmo em linha pendente
- Trocar a coluna **"Revisado em"** de `—` para `⬜ pendente` — a tarefa passou
  a existir para ser revisada, e o `02-revisar.md` procura por esse marcador.
  **`⬜ pendente` é o único valor que este prompt escreve nessa célula.** Nem
  data, nem `✅ Concluído`: quem revisa é o `/revisar`, em invocação separada, e
  é ele quem escreve ali — é a mesma cerca que o `02-revisar.md` já tem do outro
  lado ("a única célula do `progresso.md` que este prompt escreve é a Revisado
  em"). Escrever `✅ Concluído` aí — o símbolo da coluna **vizinha**, copiado uma
  casa adiante — **tira a tarefa da fila do `/revisar`** e afirma uma revisão que
  não houve; foi o que aconteceu com as PES2-TASK-32 e 33 (CORR-PES2-022)
- Trocar `status: pendente` por `status: concluído` no **frontmatter do arquivo
  da tarefa**. O campo duplica a coluna Status do `progresso.md`; os dois têm de
  concordar, senão o arquivo da task afirma o contrário do índice
- Preencher o **Log de Execução** no arquivo da tarefa:
  - **Executado em:** data de hoje
  - **Resumo do que foi feito:** 2-3 linhas, dizendo **o que se aprendeu**
  - **Arquivos criados/modificados:** lista, **conferida contra o commit**
  - **Problemas encontrados:** ou "Nenhum"

> **A lista de arquivos se confere contra o commit, não contra a memória.** É
> uma linha, e responde sozinha:
>
> ```bash
> git show --stat --format= HEAD
> ```
>
> Todo caminho que aparecer ali tem de estar na lista — em nome próprio ou
> numa forma coletiva ("os dois `.uses`", "os `ep2002_*.pas` regerados"). O
> arquivo da própria tarefa é a única omissão convencional.
>
> **Já falhou quatro vezes**, e sempre no mesmo formato: o item que entra no
> meio da execução, por um motivo lateral, e não volta para a lista ao escrever
> o Log — [CORR-WTE-078](/docs/tasks/concluidos/CORR-WTE-078.md),
> [CORR-WTE-087](/docs/tasks/concluidos/CORR-WTE-087.md),
> [CORR-WTE-099](/docs/tasks/concluidos/CORR-WTE-099.md) e
> [CORR-WTE-107](/docs/tasks/concluidos/CORR-WTE-107.md) — a última pelo **repasse** para
> a task seguinte, que é o pior item a faltar porque é o único que não é
> arquivo de ferramenta. A -099 foi pelo `.gitignore`
> que ganhou quinze linhas ao ver um binário compilado aparecer no
> `git status`. É justamente o tipo que alguém procura depois, porque é o
> único que não é sobre o assunto da tarefa.

> **Número do plano que a tarefa mediu e a task de recontagem não lista:
> acrescente a linha ao quadro dela.** Registrar no Log "a reconciliação é da
> task NN" não basta — quem executa o quadro remede o que está nele, e o que
> não está não é remedido. A linha nova diz a afirmação do plano e a ferramenta
> (ou o comando, se não houver gerador) que a remede. Se o ciclo em vigor não
> tiver task de recontagem, o destino é o próprio plano, com a data.
>
> Isso já falhou duas vezes no ciclo `wte/`: os imports de `rtl60`/`vcl60` da
> WTE-TASK-07 ([CORR-WTE-012](/docs/tasks/concluidos/CORR-WTE-012.md)) e os
> bitmaps da WTE-TASK-08
> ([CORR-WTE-014](/docs/tasks/concluidos/CORR-WTE-014.md)) — os dois medidos, os
> dois encaminhados para a task de fechamento, os dois ausentes do quadro que
> ela executa.

> **Pendência encaminhada para outra task só vale com a linha escrita NA
> task de destino.** Escrever *"encaminhado para a WTE-TASK-NN"* no Log da task
> que fecha **não encaminha nada**: quem executar a NN lê o arquivo dela, não o
> Log da anterior. Abra a entrada no destino, no formato que ele usa, e só
> então cite o encaminhamento no seu Log.
>
> É a mesma família do quadro da WTE-TASK-09 acima, um nível mais geral, e já
> falhou duas vezes: a WTE-TASK-30 com dono errado
> ([CORR-WTE-086](/docs/tasks/concluidos/CORR-WTE-086.md)) e o vaivém dos cobradores, que
> a WTE-TASK-34 encaminhou para a 35 sem que a 35 tivesse uma linha sobre ele
> ([CORR-WTE-105](/docs/tasks/concluidos/CORR-WTE-105.md)). A terceira passagem da
> WTE-TASK-31 batizou o defeito: **prosa vencida** — documento que envelhece
> sozinho enquanto outro o lê como estado corrente.

> **Marcar `✅ Concluído` não é o passo final — o commit é.** `✅ Concluído`
> descreve um estado que precisa **já existir commitado** quando você escrever
> isso, não uma intenção. Só escreva depois de fechar o passo 5 com sucesso.

### 5) Commit

Commitar artefatos e documentação **juntos, no mesmo commit**.

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git add <arquivos específicos> docs/tasks/progresso.md docs/tasks/<arquivo-da-task>.md
git commit -F - <<'MSG'
docs: <titulo imperativo curto>

<corpo>
MSG
```

**O formato deste repositório é conventional commit, em inglês** — diferente do
projeto `snes`. Siga o histórico:

```
docs: break the Lazarus reverse-engineering plan into 40 tasks
docs: correct the wte binary's toolchain to C++Builder 6
build: add a make wte target for Obocaman's team editor
feat(app): park the SoFIFA import behind app::SOFIFA_ENABLED
```

- **Inglês**, tipo em minúscula, escopo opcional, primeira linha < 72 caracteres
- Imperativo: "add", não "added"
- O corpo diz **o que se aprendeu**, não só o que se marcou. As boas mensagens
  deste repo registram a armadilha que quase pegou
- **Sem footer de co-autoria**
- Nunca `git add -A` nem `git add .` — sempre listar os arquivos
- **Não versione:** `we-team-editor/`, `roms/`, `work/`, saída de build,
  cópias de imagem, projeto do Ghidra
- **`git commit` precisa rodar de fato.** Depois, `git status --short` e
  confirme que não sobrou nada pendente desta tarefa
- **Existe remote** (`git@github.com:aguilasa/new-we2002-editor.git`), diferente
  do projeto `snes`. Mas **`push` só quando o usuário pedir** — não empurre por
  conta própria

---

## Formato de saída esperado

Ao concluir, informe:

1. Qual tarefa foi selecionada e por quê (próxima pendente, fase e dependências
   verificadas)
2. Resumo do que foi feito
3. Arquivos criados ou modificados
4. Confirmação de que o critério de conclusão foi atendido, com o **resultado
   medido** de cada gate (`--check`, golden, dumps, controle)
5. **SHA do commit** e confirmação de que `git status --short` está limpo para
   esta tarefa
6. **O que a tarefa ensinou que vale para a próxima.** Se nada surpreendeu,
   diga isso
7. Bloqueios ou pendências, se houver

---

## Regras importantes

- Nunca escolha uma tarefa aleatória; sempre a próxima pendente na ordem
- Faça apenas **uma tarefa por vez**
- Não marque como concluída sem execução real e validação dos critérios
- **Não marque `✅ Concluído` sem o commit já feito**
- Nunca aponte ferramenta nenhuma para `roms/` — cópia, sempre
- Nunca cole saída de decompilador em spec nem em código Pascal
- Nunca edite à mão arquivo que um gerador produz
- Se o markdown da tarefa estiver desatualizado em relação ao estado real
  (número que mudou, endereço reclassificado, ferramenta que não existe mais),
  **adapte, corrija o markdown, e registre no Log de Execução** — divergência
  entre doc e ferramenta é achado, não ruído

---

## Regra final

Não me entregue um plano.
Execute **exatamente uma** tarefa pendente — a próxima na ordem das fases —
atualize o progresso ao final e **pare**.
Nunca execute mais de uma tarefa por invocação, mesmo que a primeira termine
rapidamente.
