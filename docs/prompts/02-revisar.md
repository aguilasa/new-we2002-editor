# Revisão de tarefas

Você vai trabalhar no projeto **WE2002 Team Editor → Lazarus**, localizado em:

- **Projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`
- **Fonte de verdade:** **a que a própria task declarar** no campo
  `fonte_de_verdade` do frontmatter. Este prompt não conhece plano nenhum pelo
  nome — a task em mãos é quem diz contra o que ela se mede.
- **Arquivo de progresso:** `docs/tasks/progresso.md`. **O prefixo dos IDs de
  task é do ciclo, e quem o declara é este arquivo** — hoje `PES2-TASK-XX`,
  antes `WTE-TASK-XX`. Abaixo ele aparece como `<PREFIXO>`; leia-o ali, não
  o deduza do que este prompt escreve como exemplo nem de citação a task
  antiga.
- **Regras do repositório:** `CLAUDE.md`
- **Correções existentes:** `docs/tasks/CORR-*.md`. **O prefixo é do ciclo, e
  quem o declara é a primeira seção do `correcoes-progresso.md`** — hoje
  `PES2`, antes `WTE`. Leia-o ali; não o deduza do prefixo das tasks nem do
  que este prompt escreve como exemplo. Abaixo ele aparece como `<PREFIXO>`

---

## Objetivo

Quero que você:

1. Leia o `progresso.md` e identifique a **última tarefa marcada como
   `✅ Concluído`** cuja coluna **"Revisado em"** ainda esteja em
   `⬜ pendente` — a coluna é o registro de quais já passaram por aqui.
   **Havendo mais de uma `⬜ pendente`, revise a de menor ID**, e só ela: o
   `/executar-lote` fecha várias tarefas numa invocação, então a fila de espera
   por revisão tem mais de um item com frequência, e "última" ficaria ambíguo.
   A ordem de revisão é a ordem de execução
2. Use a tabela de mapeamento (em `01-executar.md`, ou os links da tabela de
   resumo do `progresso.md`) para achar o markdown da tarefa e leia-o
3. **Inspecione o artefato real** — cada arquivo que a tarefa dizia criar ou
   modificar, e **rode as ferramentas** que produzem os números que ela afirma
4. Compare o que foi pedido com o que existe
5. Para cada discrepância, crie um `CORR-<PREFIXO>-XXX.md` e registre em
   `correcoes-progresso.md`
6. Se não houver discrepância, diga isso explicitamente
7. Preencha a coluna **"Revisado em"** da tarefa revisada, na tabela de resumo
   do `progresso.md`, com a data do commit desta revisão (`AAAA-MM-DD`) —
   **inclusive quando a revisão não achou nada**

**A diferença deste projeto para um projeto de aplicação comum:** metade dos
artefatos é **gerada**, e a outra metade é verificada contra um **binário de
2002 rodando sob Wine**. Ler o código não basta nos dois casos. No gerado, o que
prova é o `--check`; no comportamento, o que prova é o golden test com o
controle fechando antes. **Rode a ferramenta.**

---

## Como revisar

### Etapa 0 — Ler o plano e as regras

- **o que o `fonte_de_verdade` da task apontar** — é ele que diz contra o que a
  tarefa se mede, e muda de task para task
- **o perfil do ciclo**, nomeado pelo campo `perfil:` do `progresso.md`: as
  decisões confirmadas, o que é gerado, os gates e as armadilhas medidas. É
  contra ele que se julga se a task respeitou o método do ciclo
- `CLAUDE.md` — em especial a regra do `:98`
- Os registros técnicos que a task cita, e que o perfil lista como quentes

### Etapa 1 — Ler o escopo da tarefa

No markdown da tarefa:
- **Contexto/Objetivo** — o que devia entregar
- **Arquivos a criar ou modificar**
- **Critério de conclusão** — o checklist
- **Log de Execução** — o que foi dito que foi feito. **Use como pista, não
  como verdade.** É exatamente aqui que erro de número nasce

### Etapa 2 — Medir, não só ler

**Rode as ferramentas.** Todo número que a task ou o Log afirma tem de bater.

**Quais ferramentas, e a partir de quando cada uma existe, está no perfil do
ciclo** — seção "gates". Rode as que se aplicam ao que a task tocou. Duas valem
para o repositório e não para um ciclo:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

ctest --preset debug     # o projeto irmao (newWe2002) nao regrediu,
                         # se a task tocou em src/core/
```

E antes de qualquer gate de GUI: **feche janela grande no `:98`** — os dois
lados acham a janela por heurística.

**Contagem que a task afirma se remede, não se relê.** Onde os valores correntes
moram — e se eles são gerados — está no perfil; não os copie para cá, senão esta
linha vira mais um sítio a reconciliar. No ciclo `wte/` isso já custou uma
correção: este arquivo entrou no perímetro de um `--check` justamente porque
número velho afirmado aqui reprova task correta.

### Etapa 3 — Verificações específicas por fase

**Elas moram no perfil do ciclo**, porque são a parte da revisão que muda
inteira de um projeto para o outro: o que se pergunta de uma fase de extração de
formulário não é o que se pergunta de uma fase de inventário de texto.

Abra a seção "verificações específicas por fase" do perfil, ache a fase da task
em mãos (a coluna `Fase` do `progresso.md`), e responda item a item. Se o perfil
não tiver entrada para essa fase, **diga isso na saída** em vez de improvisar —
fase sem verificação escrita é achado, e vira CORR.

Quatro perguntas valem para **qualquer** fase de qualquer ciclo:

- A ferramenta é **determinística**? Rodar duas vezes dá bytes iguais? Sem isso
  o `--check` é decorativo
- Ela **falha alto** no que não reconhece, ou emite parcial? Saída truncada que
  "parece completa" é o furo mais caro de achar
- Todo número do doc veio de **ferramenta versionada**, não de script
  descartável nem de contagem à mão?
- Algum arquivo **gerado** foi editado à mão? Rode o `--check` sobre a árvore
  commitada. Editar o gerado em vez do gerador é discrepância crítica

### Etapa 4 — Classificar discrepâncias

| Tipo | Descrição | Ação |
| --- | --- | --- |
| **Crítica** | Arquivo gerado editado à mão; decompilado colado em spec ou código; gate de comportamento sem controle; gravação divergente sem veredito; `roms/` tocada; asset de terceiro versionado; `LICENSE` adicionado | Criar CORR |
| **Alta** | Número em doc que não bate com a ferramenta; guard não exercitado; gerador não determinístico; limite de array estimado; teste numa amostra só quando o ciclo tem duas; propriedade descartada em silêncio | Criar CORR |
| **Baixa** | Veredito de formulário ausente; spec sem campo evidência; doc desatualizado sem contradição; link de tabela faltando | Criar CORR |
| **Não é discrepância** | Diferença intencional já registrada no Log; resultado negativo (unidade transitiva, offset irrelevante) — é resultado legítimo | Ignorar, mas registrar no relatório |

**Resultado negativo não é discrepância.** Uma task que conclui "os 105
uniformes são índice direto, sem tabela" ou "`Printers` é dependência
transitiva" entregou o que devia.

---

## Como criar arquivos de correção

### Determinar o próximo ID

1. Leia os `CORR-*.md` existentes em `docs/tasks/`
2. O maior número + 1 é o próximo
3. Se não existir nenhum, comece em `CORR-<PREFIXO>-001`, com o prefixo que o
   `correcoes-progresso.md` declarar

### Formato de cada `CORR-<PREFIXO>-XXX.md`

```markdown
---
id: CORR-<PREFIXO>-XXX
title: "Correção: <descrição curta do problema>"
type: correção
category: <engenharia-reversa | ui | dados | comportamento | features | verificação | processo>
status: pendente
depends_on: []
---

# CORR-<PREFIXO>-XXX: <título>

## Problema identificado

<Qual arquivo/endereço tem o problema; o estado atual, com o comando que o
revela; por que está errado — o que a task pedia vs. o que existe>

## Evidência

<A saída da ferramenta, recortada. Não a impressão. Se for número, os dois
valores e a fonte de cada um. Se for comportamento, o offset do diff.>

## Causa raiz

<Uma frase>

## Correção

### Arquivo: `<caminho>`

<O que fazer, com o código ou o roteiro do estado correto. Se o alvo for
arquivo gerado, a correção entra no **gerador**.>

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `caminho` | criar / modificar |

## Verificação

- [ ] <item verificável, com o comando que o verifica>
- [ ] `--check` do gerador afetado continua verde (se tocar em gerado)
- [ ] o build do ciclo compila, sem warning novo (se tocar em código)
- [ ] o gate de comportamento do ciclo verde, com o controle fechando antes
      (se tocar em comportamento)
- [ ] `ctest --preset debug` e o golden do `newWe2002` verdes (se tocar em
      `src/core/`)
- [ ] `roms/` intocada

## Log de Execução *(preenchido após execução)*

**Executado em:**

**Resumo do que foi feito:**

**Problemas encontrados:**

**Arquivos criados/modificados:**
```

### Criar/atualizar `correcoes-progresso.md`

Em `docs/tasks/correcoes-progresso.md`.

Se ainda não existir:

```markdown
# Progresso de Correções — <o ciclo em vigor>

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-<PREFIXO>-001](/docs/tasks/CORR-<PREFIXO>-001.md) | [<PREFIXO>-TASK-01](/docs/tasks/01-ferramental.md) | <título> | Crítica/Alta/Baixa | [ ] pendente | — |

## Checklist

- [ ] CORR-<PREFIXO>-001 — <título curto>

## Detalhes por correção

### CORR-<PREFIXO>-001

- **Arquivo com problema:** `caminho`
- **Sintoma:** <o que está errado>
- **Como foi detectado:** <a ferramenta e o comando>
- **Fix:** <o que fazer>
```

Se já existir, acrescente sem alterar as entradas anteriores.

**Três regras da tabela de resumo, que valem para toda linha nova:**

1. **A célula do ID é link** para o markdown da correção —
   `[CORR-<PREFIXO>-XXX](/docs/tasks/CORR-<PREFIXO>-XXX.md)`. **Sempre `/docs/` + caminho
   do arquivo**, nunca relativo, como manda
   `.claude/rules/links.md`. O `/revisar` cria o `.md` na mesma
   invocação, então o link nunca nasce quebrado.
2. **A coluna "ID Task Origem" é a tarefa que esta revisão estava revisando**,
   também linkada: `[<PREFIXO>-TASK-XX](/docs/tasks/XX-nome-do-arquivo.md)`. É sempre
   a mesma para todas as CORRs abertas numa invocação — a que você escolheu no
   passo 1.
   **Não é a task que a correção menciona no texto**: uma CORR aberta revisando
   a 17 pode falar da 18, e as duas coisas são diferentes.
3. **A coluna "Concluída em" nasce `—`** e só é preenchida por quem executa a
   correção (`03-corrigir.md` ou `04-corrigir-tudo.md`), com a data do commit. O
   `/revisar` **não** preenche: ele abre a correção, não a fecha.

---

## Restrições

> **EXCLUSÃO OBRIGATÓRIA 1 — sem implementações:**
> Este prompt é exclusivo para **revisão e criação de CORRs**.
> **Nunca** execute tasks nem CORRs por aqui.
> Não marque tarefas como concluídas no `progresso.md`. A **única** célula do
> `progresso.md` que este prompt escreve é a coluna "Revisado em" da tarefa
> que ele acabou de revisar — nunca "Status", nunca "Concluída em", nunca
> outra linha.
> **Não rode gerador em modo de escrita.** Rodar `--check`, o build, o gate de
> comportamento, `ctest`, `objdump`, `cmp` é obrigatório e não conta como
> implementação. Rodar um gerador **sem** `--check` reescreve a árvore e é
> implementação.
>
> **EXCLUSÃO OBRIGATÓRIA 2 — uma revisão por execução:**
> Revise **somente a última tarefa concluída** — a de **menor ID** entre as que
> estão em `⬜ pendente`, se houver mais de uma.
> Após criar os arquivos de correção e commitar, **pare imediatamente**.
> Não existe irmão em lote deste prompt: fila de várias esperando revisão se
> esvazia uma invocação por vez.
>
> **EXCLUSÃO OBRIGATÓRIA 3 — nada de escrever no binário nem nas ROMs:**
> O `we-team-editor.exe` é leitura pura. As imagens de `roms/` também.
> Se precisar exercitar o oráculo, trabalhe sobre cópia em `work/`.

---

## Formato de saída esperado

1. **Tarefa revisada:** ID e título
2. **Artefatos inspecionados:** arquivos lidos e **comandos rodados**
3. **Números medidos vs. números afirmados:** tabela, quando houver divergência
4. **Discrepâncias encontradas:** ID + descrição de uma linha + criticidade
5. **Não-discrepâncias notadas:** diferenças intencionais, e por quê
6. **CORRs criadas:** lista
7. **`correcoes-progresso.md` atualizado:** sim/não
8. **"Revisado em" preenchido:** a data escrita na linha da tarefa
9. Se nenhuma discrepância: declaração explícita de que a tarefa está correta,
   **dizendo quais gates você mediu para afirmar isso**

---

## Commit final

A revisão normalmente produz só markdown em `docs/tasks/`:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git add docs/tasks/CORR-<PREFIXO>-XXX.md docs/tasks/correcoes-progresso.md \
        docs/tasks/progresso.md
git commit -m "docs: open CORR-<PREFIXO>-XXX from the <PREFIXO>-TASK-YY review"
```

O `progresso.md` entra **sempre**, porque é onde mora a coluna "Revisado em".

**Revisão que não achou discrepância também commita**, e aí o `progresso.md` é
o único arquivo do commit:

```bash
git add docs/tasks/progresso.md
git commit -m "docs: review <PREFIXO>-TASK-YY: <o que foi medido>, no discrepancy"
```

Sem esse commit a revisão não deixa rastro nenhum, e a próxima invocação
reviveria a mesma tarefa — a coluna existe justamente para isso. **Revisão sem
achado é resultado legítimo**; o título diz o que você mediu para poder afirmar.

Mensagem em **inglês, conventional commit**, no estilo do histórico deste
repositório. Sem footer de co-autoria. Nunca `git add -A`. **`push` só se o
usuário pedir.**

Se a revisão identificar necessidade de ajuste imediato, **não implemente
aqui**; registre a CORR.

---

## Regra final

Não me entregue um plano e não implemente nada.
Meça, compare com **somente a última tarefa concluída**, crie os arquivos de
correção necessários e **pare**.
Uma revisão por invocação — nunca agrupe múltiplas tarefas.
