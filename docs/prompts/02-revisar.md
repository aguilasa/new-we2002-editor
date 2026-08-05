# Revisão de tarefas

Você vai trabalhar no projeto **WE2002 Team Editor → Lazarus**, localizado em:

- **Projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`
- **Fonte de verdade:** `docs/PLAN-WTE-LAZARUS.md`
- **Arquivo de progresso:** `docs/tasks/progresso.md`
- **Regras do repositório:** `CLAUDE.md`
- **Correções existentes:** `docs/tasks/CORR-WTE-*.md`

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
5. Para cada discrepância, crie um `CORR-WTE-XXX.md` e registre em
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

- `docs/PLAN-WTE-LAZARUS.md` — a seção referenciada pela task, mais §2 (método:
  spec, não transcrição), §4.4 e §4.5 (o que é gerado), §6 (testes) e §8
  (armadilhas)
- `CLAUDE.md` — em especial a regra do `:99` e a seção do `make wte`
- Os docs de `wte/re/` que a task cita

### Etapa 1 — Ler o escopo da tarefa

No markdown da tarefa:
- **Contexto/Objetivo** — o que devia entregar
- **Arquivos a criar ou modificar**
- **Critério de conclusão** — o checklist
- **Log de Execução** — o que foi dito que foi feito. **Use como pista, não
  como verdade.** É exatamente aqui que erro de número nasce

### Etapa 2 — Medir, não só ler

**Rode as ferramentas.** Todo número que a task ou o Log afirma tem de bater.

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

# os geradores conferem contra o commitado -- conforme forem existindo
python3 wte/tools/dfm_extract.py --check
python3 wte/tools/dfm2lfm.py --check
python3 wte/tools/gen_tables_pas.py --check
python3 wte/tools/port_database_pas.py --check

# o app compila
lazbuild wte/wte.lpi

# o gate de comportamento (a partir da WTE-TASK-22) -- feche janela no :99 antes
bash wte/tools/golden_check.sh

# o projeto irmao nao regrediu, se a task tocou em src/core/
ctest --preset debug
```

**Contagens que a task afirma se remede, não se relê.** Exemplos do que já está
no plano e pode ter mudado: 18 formulários, ~430 componentes, 96 handlers, 19 de
69 offsets, 70 strings com padding, 13 unidades, 197 bitmaps.

### Etapa 3 — Verificações específicas por fase

**Fase 0-1 (WTE-TASK-01 a 09) — infra e extração estática:**

- O gerador é **determinístico**? Rodar duas vezes dá bytes iguais? Sem isso o
  `--check` é decorativo
- Ele **falha alto** em construção que não reconhece, ou emite parcial? Saída
  truncada que "parece completa" é o furo principal desta fase
- Os 18 DFM decodificaram **inteiros**? Os três que o protótipo truncou
  (`ficha_creditos_equipo`, `ficha_movertodos`, `ficha_warning_2`) estão
  completos?
- Os blobs binários foram **preservados**, ou viraram `<bin N>`?
- O limite da tabela de offsets foi **medido** ou estimado pelo olho? Estimar
  aqui é a armadilha §8.7 — o slot 64 de um array de 63
- Todo número do doc veio de ferramenta versionada, não de script descartável?

**Fase 2 (WTE-TASK-10 a 14) — casca:**

- Algum `.lfm` ou unidade gerada foi **editado à mão**? Rode o `--check` sobre a
  árvore commitada. **Editar o gerado em vez do gerador é discrepância crítica**
- Propriedade que a LCL não tem virou **comentário**, ou sumiu calado? Sumir
  calado é diferença visual que só aparece muito depois da causa
- Os 96 stubs estão na **unidade certa**? A coluna `formulario` existe e foi
  usada? `FormCreate` aparece 17 vezes
- A comparação visual tem **veredito escrito por formulário**, ou uma frase
  geral? Frase geral não é conferência
- O roteiro de eventos é **arquivo fixo**, ou driver que reage à tela? Driver
  reativo muda o estímulo quando um lado diverge, e os dois param de receber a
  mesma entrada

**Fase 3 (WTE-TASK-15 a 21) — dados:**

- `FORBIDDEN` e `check_seeks()` **existem e foram testados com entrada
  plantada**, ou só com a entrada boa? Guard nunca exercitado é guard ausente
- A fração de código gerado foi **medida**? A tese da §4.5 diz "a maior parte";
  se veio metade à mão, a tese caiu e o plano precisa dizer
- Os dumps batem nas **duas** ROMs? A japonesa é o único teste real do
  `KanjiToAscii`/`AsciiToKanji`
- O bitfield de `SquadNumbers` foi conferido **contra imagem real**, ou
  presumido correto pelo `bitpacked record`? (§8.11)
- O **diff de controle** (gravar sem editar) foi medido antes dos offsets
  novos? Sem ele toda medição de offset vem contaminada
- Se a task tocou `src/core/`, o `ctest` e o golden do `newWe2002` rodaram
  depois?

**Fase 4-5 (WTE-TASK-22 a 33) — comportamento e features:**

- O harness roda o **controle** (original contra original) e ele fecha? Sem
  isso, verde e vermelho não significam nada
- Ele detecta um **byte plantado**, com o offset certo?
- As quatro guardas do golden estão implementadas (`DISPLAY` fixo, recusa com
  janela aberta, `_NET_WM_PID`, `roms/` intocada)?
- A convenção Borland foi aplicada **a todas as funções**, e `colorearClick` sai
  com a assinatura correta? Sem isso o decompilador entrega ruído convincente
- Alguma spec tem **C++ decompilado colado**? A §2 depende disso e ninguém
  confere sozinho
- Quantas specs se apoiam só em "observação de tela"? São hipóteses vestidas de
  spec
- `trivial` virou maioria esmagadora? Provavelmente foi atribuído sem olhar —
  amostre cinco e reconfira
- A fórmula de preço tem **as duas fontes** (tabela de verdade e disassembly)
  concordando, ou só uma?
- O render 2D tem tolerância **medida**, com máximo conhecido e causa nomeada,
  ou tolerância implícita?

**Fase 6-7 (WTE-TASK-34 a 40):**

- A bateria cobre **edição múltipla** e **gravação dupla**, ou só operação
  isolada? O editor não é idempotente, e isso só aparece na segunda gravação
- Toda exceção do golden tem entrada em `divergencias.md`? Exceção sem entrada é
  divergência silenciosa
- Divergência sem causa conhecida foi classificada como **bug aberto**, ou
  entrou como "deliberada"? Confundir os dois é como lista de problemas
  conhecidos vira desculpa
- A condição "roda sem Wine" foi **testada**, ou presumida?
- Algum asset do Obocaman foi versionado? (`we-team-editor/` é gitignored)
- Foi adicionado `LICENSE`? **Não deve haver.**

### Etapa 4 — Classificar discrepâncias

| Tipo | Descrição | Ação |
| --- | --- | --- |
| **Crítica** | Arquivo gerado editado à mão; decompilado colado em spec ou código; golden sem controle; gravação divergente sem veredito; `roms/` tocada; asset de terceiro versionado; `LICENSE` adicionado | Criar CORR |
| **Alta** | Número em doc que não bate com a ferramenta; guard não exercitado; gerador não determinístico; limite de array estimado; teste só numa das duas ROMs; propriedade descartada em silêncio | Criar CORR |
| **Baixa** | Veredito de formulário ausente; spec sem campo evidência; doc desatualizado sem contradição; link de tabela faltando | Criar CORR |
| **Não é discrepância** | Diferença intencional já registrada no Log; resultado negativo (unidade transitiva, offset irrelevante) — é resultado legítimo | Ignorar, mas registrar no relatório |

**Resultado negativo não é discrepância.** Uma task que conclui "os 105
uniformes são índice direto, sem tabela" ou "`Printers` é dependência
transitiva" entregou o que devia.

---

## Como criar arquivos de correção

### Determinar o próximo ID

1. Leia os `CORR-WTE-*.md` existentes em `docs/tasks/`
2. O maior número + 1 é o próximo
3. Se não existir nenhum, comece em `CORR-WTE-001`

### Formato de cada `CORR-WTE-XXX.md`

```markdown
---
id: CORR-WTE-XXX
title: "Correção: <descrição curta do problema>"
type: correção
category: <engenharia-reversa | ui | dados | comportamento | features | verificação | processo>
status: pendente
depends_on: []
---

# CORR-WTE-XXX: <título>

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
- [ ] `lazbuild wte/wte.lpi` compila (se tocar em Pascal)
- [ ] `golden_check.sh` verde, com o controle fechando antes (se tocar em
      comportamento)
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
# Progresso de Correções — WE2002 Team Editor → Lazarus

## Resumo executivo

| ID | ID Task Origem | Título | Criticidade | Status | Concluída em |
|---|---|---|---|---|---|
| [CORR-WTE-001](/docs/tasks/CORR-WTE-001.md) | [WTE-TASK-01](/docs/tasks/01-ferramental.md) | <título> | Crítica/Alta/Baixa | [ ] pendente | — |

## Checklist

- [ ] CORR-WTE-001 — <título curto>

## Detalhes por correção

### CORR-WTE-001

- **Arquivo com problema:** `caminho`
- **Sintoma:** <o que está errado>
- **Como foi detectado:** <a ferramenta e o comando>
- **Fix:** <o que fazer>
```

Se já existir, acrescente sem alterar as entradas anteriores.

**Três regras da tabela de resumo, que valem para toda linha nova:**

1. **A célula do ID é link** para o markdown da correção —
   `[CORR-WTE-XXX](/docs/tasks/CORR-WTE-XXX.md)`. **Sempre `/docs/` + caminho
   do arquivo**, nunca relativo, como manda
   `.claude/rules/links.md`. O `/revisar` cria o `.md` na mesma
   invocação, então o link nunca nasce quebrado.
2. **A coluna "ID Task Origem" é a tarefa que esta revisão estava revisando**,
   também linkada: `[WTE-TASK-XX](/docs/tasks/XX-nome-do-arquivo.md)`. É sempre
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
> **Não rode gerador em modo de escrita.** Rodar `--check`, `lazbuild`,
> `golden_check.sh`, `ctest`, `objdump`, `cmp` é obrigatório e não conta como
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
git add docs/tasks/CORR-WTE-XXX.md docs/tasks/correcoes-progresso.md \
        docs/tasks/progresso.md
git commit -m "docs: open CORR-WTE-XXX from the WTE-TASK-YY review"
```

O `progresso.md` entra **sempre**, porque é onde mora a coluna "Revisado em".

**Revisão que não achou discrepância também commita**, e aí o `progresso.md` é
o único arquivo do commit:

```bash
git add docs/tasks/progresso.md
git commit -m "docs: review WTE-TASK-YY: <o que foi medido>, no discrepancy"
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
