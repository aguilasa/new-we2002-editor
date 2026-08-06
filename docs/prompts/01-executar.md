# Prompt para execução de tarefas

Você vai trabalhar no projeto **WE2002 Team Editor → Lazarus** (engenharia
reversa do editor do Obocaman, C++Builder 6 / Win32, e reimplementação em
Object Pascal sobre Lazarus/LCL no Linux), localizado em:

- **Raiz do projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`
- **Arquivo de progresso:** `docs/tasks/progresso.md`
- **Tarefas detalhadas:** `docs/tasks/`
- **Fonte de verdade do projeto:** `docs/PLAN-WTE-LAZARUS.md`
- **Regras do repositório:** `CLAUDE.md` — leia antes de tocar em qualquer coisa
- **Registro técnico dos achados:** `wte/re/`
- **Binário alvo:** `we-team-editor/we-team-editor.exe` — **somente leitura**

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
4. Leia a seção de `docs/PLAN-WTE-LAZARUS.md` referenciada no campo
   "Referência" da task, e os docs de `wte/re/` que ela citar
5. Execute a tarefa
6. Ao final, atualize o `progresso.md` marcando a tarefa como `✅ Concluído`
   (tabela de resumo E checklist da fase), e **preencha a coluna "Concluída
   em"** com a data do commit que fechou a tarefa
7. Preencha o **Log de Execução** no arquivo da tarefa: data, resumo, arquivos
   criados/modificados, problemas encontrados

---

## Mapeamento de tarefas — ID → arquivo

Se esta tabela divergir do `progresso.md`, **o `progresso.md` manda** — e a
divergência é achado a registrar.

| ID | Fase | Arquivo em `docs/tasks/` |
| --- | --- | --- |
| WTE-TASK-01 | 0 | `01-ferramental.md` |
| WTE-TASK-02 | 0 | `02-esqueleto-do-projeto.md` |
| WTE-TASK-03 | 1 | `03-extrator-de-dfm.md` |
| WTE-TASK-04 | 1 | `04-mapa-de-handlers.md` |
| WTE-TASK-05 | 1 | `05-inventario-de-strings.md` |
| WTE-TASK-06 | 1 | `06-mapa-de-offsets.md` |
| WTE-TASK-07 | 1 | `07-unidades-duvidosas.md` |
| WTE-TASK-08 | 1 | `08-convencao-dos-assets.md` |
| WTE-TASK-09 | 1 | `09-fechamento-fase-1.md` |
| WTE-TASK-10 | 2 | `10-conversor-dfm-para-lfm.md` |
| WTE-TASK-11 | 2 | `11-app-com-a-casca-completa.md` |
| WTE-TASK-12 | 2 | `12-comparacao-visual.md` |
| WTE-TASK-13 | 2 | `13-trace-de-eventos.md` |
| WTE-TASK-14 | 2 | `14-fechamento-fase-2.md` |
| WTE-TASK-15 | 3 | `15-mapeamento-de-tipo.md` |
| WTE-TASK-16 | 3 | `16-gerador-de-tabelas.md` |
| WTE-TASK-17 | 3 | `17-transpilador-da-camada-de-dados.md` |
| WTE-TASK-18 | 3 | `18-camada-de-dados-gerada.md` |
| WTE-TASK-19 | 3 | `19-os-50-offsets-restantes.md` |
| WTE-TASK-20 | 3 | `20-round-trip-headless.md` |
| WTE-TASK-21 | 3 | `21-fechamento-fase-3.md` |
| WTE-TASK-22 | 4 | `22-harness-golden.md` |
| WTE-TASK-23 | 4 | `23-formato-da-spec.md` |
| WTE-TASK-24 | 4 | `24-ghidra-convencao-borland.md` |
| WTE-TASK-25 | 4 | `25-handlers-de-carga.md` |
| WTE-TASK-26 | 4 | `26-handlers-de-edicao.md` |
| WTE-TASK-27 | 4 | `27-handlers-de-gravacao.md` |
| WTE-TASK-28 | 4 | `28-handlers-auxiliares.md` |
| WTE-TASK-29 | 4 | `29-fechamento-fase-4.md` |
| WTE-TASK-30 | 5 | `30-preco-do-jogador.md` |
| WTE-TASK-31 | 5 | `31-import-de-mcr.md` |
| WTE-TASK-32 | 5 | `32-camisa-e-bandeira-2d.md` |
| WTE-TASK-33 | 5 | `33-slots-de-master-league.md` |
| WTE-TASK-34 | 6 | `34-bateria-golden-completa.md` |
| WTE-TASK-35 | 6 | `35-divergencias-deliberadas.md` |
| WTE-TASK-36 | 6 | `36-buffers-e-truncamento.md` |
| WTE-TASK-37 | 6 | `37-reconferencia-de-ui.md` |
| WTE-TASK-38 | 7 | `38-nome-e-linhagem.md` |
| WTE-TASK-39 | 7 | `39-empacotamento.md` |
| WTE-TASK-40 | 7 | `40-verificacao-final.md` |

---

## Regras de seleção da tarefa

1. Procurar a **primeira tarefa com `⬜ Pendente`** no `progresso.md`, na ordem
   de fases e, dentro da fase, na ordem numérica
2. Verificar se todas as tarefas em `depends_on` estão concluídas — se não,
   **não executar**, e informar o bloqueio
3. Se existir tarefa `🔄 Em andamento`, priorizar concluí-la
4. **Exceção única e prevista:** a WTE-TASK-30 (preço) pode ser escolhida fora
   de ordem — plano §10 passo 5 — se a 24 e a 25 estiverem concluídas **e** o
   usuário pedir explicitamente. É isolada, não depende de gravação, e valida o
   ferramental de decompilação num alvo pequeno
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

## Contexto essencial — decisões já confirmadas

**Leia isto antes de tocar em qualquer arquivo.** São decisões de
`docs/PLAN-WTE-LAZARUS.md` que **não devem ser revertidas** sem o usuário pedir:

- **O original é Borland C++Builder 6, não Delphi.** Os dois usam a mesma VCL,
  os mesmos `rtl60.bpl`/`vcl60.bpl` e o mesmo `.dfm`; o que separa é o mangling
  `$qqr`, os símbolos `___CPPdebugHook`/`__GetExceptDLLinfo` e a string
  `c:\bcb\emuvcl\utilcls.h`. (§1.1)
- **Recuperação de especificação, não transcrição.** O decompilador serve para
  *responder perguntas*; a resposta vai para `wte/re/spec/<handler>.md`, e o
  Pascal é escrito **a partir do `.md`**. Nunca cole C++ decompilado em spec nem
  em código. (§2)
- **O que dá para gerar, se gera.** Formulários, esqueletos de unidade,
  offsets, tabelas e a camada de dados inteira saem de gerador. Corrigir arquivo
  gerado à mão não conta como correção — a correção entra no gerador e o
  arquivo é regenerado. (§4.4)
- **A camada de dados vem do `we2002_core` deste repositório, não do `.exe`.**
  Ele já é byte-idêntico ao `ed.exe` nas duas ROMs. (§4.5)
- **O transpilador só digere código deste repositório.** Nunca apontá-lo para
  saída de decompilador: ali o `FORBIDDEN` deixa de segurar e a saída é Pascal
  quebrado com cara de certo. (§8.10)
- **Diff antes de decompilador.** Pergunta de *onde* se responde com `cmp` em
  dois minutos; o decompilador é para pergunta de *fórmula*. (§4.2)
- **"100%" significa toda divergência conhecida e escrita**, não zero
  divergência. (§0, §9)
- **O `newWe2002` está com escopo fechado e verificado.** Mexer em `src/core/`
  exige rodar `ctest` e o golden dele depois. Só a WTE-TASK-18 prevê isso.

---

## Armadilhas medidas — valem para todas as fases

Cada uma custou tempo real, aqui ou no `newWe2002`.

1. **Ghidra assume `__cdecl`; o C++Builder passa `this` em `EAX`.** Sem
   convenção customizada (`EAX, EDX, ECX`), a saída do decompilador é ruído
   convincente — o pior tipo de erro, porque parece certo. (§8.1)
2. **`[^x]` casa `\n` em regex.** Foi assim que um `Seek(begin)` virou
   `SeekCurrent` no `port_database.py`: compilava, passava nos testes, passava
   no ASan, e só o confronto com o `ed.exe` mostrou.
3. **Cópia, sempre.** Os três editores gravam in-place e cada imagem tem
   ~474 MB. **Nunca apontar nada para `roms/`.**
4. **Diff de controle antes de medir qualquer coisa.** `Load`+`Save` sem editar
   já muda bytes: o `Save` reconstrói as all-star, e o original troca os dois
   primeiros cobradores de cada clube de ML. Sem o controle, toda medição vem
   contaminada.
5. **Janela esquecida no `:99` derruba o golden test.** Os dois lados acham a
   janela por heurística; uma sobra de teste manual é dirigida em vez da que
   está sob teste, e o diff parece bug do port. Feche tudo antes.
6. **`Ctrl+A` não seleciona tudo num `TEdit`.** Limpar campo com `End`,
   `shift+Home`, `BackSpace` — senão os dois lados recebem textos diferentes.
7. **`xdotool type --window` embaralha string longa** (usa `XSendEvent`).
   Digitar curto; mapear unidade para encurtar caminho, como o `make wte` faz.
8. **`xdotool windowactivate` falha no `:99`** — não há window manager. Dirigir
   por coordenada absoluta.
9. **Tipo de tamanho dependente de plataforma embaralha número de camisa.**
   `DWORD` virou 64-bit no Linux LP64 e custou o bug inteiro. Em FPC o risco
   irmão é a ordem de bit do `bitpacked record`. (§8.6, §8.11)
10. **Release não é o mesmo teste que Debug.** Um `strcpy` estourando um byte
    era invisível em Debug e derrubava o app em Release com `_FORTIFY_SOURCE`.
11. **Todo número em doc vem de ferramenta.** Os números da §1 do plano foram
    medidos por script descartável em 2026-08-05; a WTE-TASK-09 os remede com
    ferramenta versionada e reconcilia.

---

## Arquitetura do projeto

### As duas fontes de verdade binárias

| Fonte | Papel | Pode escrever? |
| --- | --- | --- |
| `we-team-editor/we-team-editor.exe` | alvo da RE, oráculo comportamental | **não** — leitura pura |
| `roms/*.bin` | imagens de teste, ~474 MB cada | **não** — sempre cópia |
| `src/core/` (`we2002_core`) | oráculo de formato, entrada do transpilador | só na rota 2 da WTE-TASK-18, com golden do `newWe2002` depois |

O `.exe` **não é editável** — diferente do `.diz` do projeto `snes`, aqui não há
ferramenta que escreva no binário e nem deve haver.

### Os dois oráculos

- **Oráculo A, comportamental:** `wte.exe` sob Wine 32-bit, dirigido por
  `xdotool` no `:99`. Responde *que bytes esta operação grava?*
- **Oráculo B, de formato:** o `we2002_core`, já byte-idêntico ao `ed.exe`.
  Responde *o que significam estes bytes?*

Combinados, a semântica sai sem decompilar. Ver §4.2 do plano.

### Estrutura

```text
new-we2002-editor/
  docs/
    PLAN-WTE-LAZARUS.md    # fonte de verdade deste projeto
    PLAN-LINUX.md          # o port Qt (newWe2002) -- projeto irmao, fechado
    tasks/                 # tasks, CORRs e progresso
    prompts/               # estes prompts
  wte/                     # o projeto Lazarus
    src/ forms/ re/ tools/ tests/ packaging/
  src/core/                # we2002_core -- entrada do transpilador, NAO alvo
  we-team-editor/          # o binario do Obocaman (gitignored)
  roms/                    # as duas imagens (gitignored)
```

### Comandos

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor

make wte            # abre o editor do Obocaman (oraculo A) no DISPLAY do shell
make wte-99         # idem, no Xvfb :99
make run-99         # abre o newWe2002 (o port Qt) no :99
make test           # ctest do newWe2002, sem os golden

lazbuild wte/wte.lpi                      # a partir da WTE-TASK-02
python3 wte/tools/<gerador>.py --check    # conforme forem existindo
bash wte/tools/golden_check.sh            # a partir da WTE-TASK-22
```

### A regra do `:99` — obrigatória

Toda execução com GUI acontece no `DISPLAY=:99`. O `:1` é a sessão real do
usuário. O Xvfb sobe via `xvfb-run` e tem cookie próprio:

```sh
export DISPLAY=:99
export XAUTHORITY=$(ps -o args= -C Xvfb \
  | sed -n 's/.*Xvfb :99 .*-auth \([^ ]*\).*/\1/p' | head -1)
```

Sem o `XAUTHORITY` o Qt e o Wine morrem com `Invalid MIT-MAGIC-COOKIE-1 key`.
Se por qualquer motivo não der para usar o `:99`, **pergunte antes** de cair
para o `:1`. Ver a seção do topo do `CLAUDE.md`.

---

## Como executar

### 1) Ler contexto

- Ler `docs/tasks/progresso.md`
- Ler o markdown da tarefa em `docs/tasks/`
- Ler a seção de `docs/PLAN-WTE-LAZARUS.md` referenciada, e os docs de
  `wte/re/` citados na task
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

| Fase | Gate obrigatório |
| --- | --- |
| 0 | `lazbuild` compila e abre janela no `:99`; `make wte` ainda abre o original |
| 1 | ferramenta determinística, `--check` verde, saída byte-estável; nenhum número vindo de contagem à mão |
| 2 | `--check` do `dfm2lfm.py` verde; os 18 formulários abrem; nenhum arquivo gerado editado à mão |
| 3 | `FORBIDDEN` e `check_seeks()` ativos; dumps Pascal e C++ idênticos nas **duas** ROMs |
| 4-6 | `golden_check.sh` verde, com o **controle** (original contra original) fechando antes |
| 7 | árvore instalada funciona depois de movida; app roda sem Wine |
| todas | todo número novo em doc veio de ferramenta; `roms/` intocada |

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
  `[WTE-TASK-XX](/docs/tasks/XX-nome-do-arquivo.md)` — **sempre no formato
  `/docs/` + caminho do arquivo**, nunca relativo, como manda
  `.claude/rules/links.md`. Linha de tabela sem link é defeito,
  mesmo em linha pendente
- Trocar a coluna **"Revisado em"** de `—` para `⬜ pendente` — a tarefa passou
  a existir para ser revisada, e o `02-revisar.md` procura por esse marcador.
  **Não escreva data aí**: quem revisa é o `/revisar`, em invocação separada
- Trocar `status: pendente` por `status: concluído` no **frontmatter do arquivo
  da tarefa**. O campo duplica a coluna Status do `progresso.md`; os dois têm de
  concordar, senão o arquivo da task afirma o contrário do índice
- Preencher o **Log de Execução** no arquivo da tarefa:
  - **Executado em:** data de hoje
  - **Resumo do que foi feito:** 2-3 linhas, dizendo **o que se aprendeu**
  - **Arquivos criados/modificados:** lista
  - **Problemas encontrados:** ou "Nenhum"

> **Número da §1 do plano que a tarefa mediu e o quadro da WTE-TASK-09 não
> lista: acrescente a linha ao quadro.** Registrar no Log "reconciliação é da
> WTE-TASK-09" não basta — a 09 executa o quadro, e o que não está nele não é
> remedido. Quadro em
> [`/docs/tasks/09-fechamento-fase-1.md`](/docs/tasks/09-fechamento-fase-1.md),
> seção "Recontagem obrigatória"; a linha nova diz a afirmação do plano e a
> ferramenta (ou o comando, se não houver gerador) que a remede.
>
> Isso já falhou duas vezes: os imports de `rtl60`/`vcl60` da WTE-TASK-07
> ([CORR-WTE-012](/docs/tasks/CORR-WTE-012.md)) e os bitmaps da WTE-TASK-08
> ([CORR-WTE-014](/docs/tasks/CORR-WTE-014.md)) — os dois medidos, os dois
> encaminhados para a 09, os dois ausentes do quadro que ela executa.

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
