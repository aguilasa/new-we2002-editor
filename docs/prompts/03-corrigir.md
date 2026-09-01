# Corrigir

Você vai trabalhar no repositório localizado em:

- **Projeto:** `/home/ingmar/desenvolvimento/github/new-we2002-editor/`

**Este prompt é agnóstico de ciclo.** Ele tem o rito; o que é do ciclo — as
decisões confirmadas, as armadilhas, as fontes binárias, o que é gerado, os
gates e os arquivos quentes — mora no **perfil**, e quem o nomeia é o campo
`perfil:` do `docs/tasks/progresso.md`. **Leia o perfil antes de executar.**

A documentação de correções está em:

`docs/tasks/`

O arquivo de progresso das correções está em:

`docs/tasks/correcoes-progresso.md`

Os detalhes das correções estão nos arquivos `CORR-<PREFIXO>-*.md` no mesmo
diretório. **`<PREFIXO>` é do ciclo, e quem o declara é a primeira seção do
`correcoes-progresso.md`** — hoje `PES2`, antes `WTE`. Leia o prefixo ali; não
o deduza do prefixo das tasks nem do que este prompt escreve como exemplo.

## Objetivo

Quero que você execute **uma única correção por invocação** deste prompt. Nada
mais.

> **EXCLUSÃO OBRIGATÓRIA — uma correção por execução, nunca em paralelo:**
> Cada invocação executa exatamente **uma** correção.
> Nunca execute duas em paralelo nem em sequência na mesma invocação.
> Após concluir e commitar, **pare imediatamente**.

1. Leia `correcoes-progresso.md`
2. Identifique a **próxima correção não executada** (primeira com `[ ]`)
3. Respeite a ordem dos IDs e as dependências em `depends_on`
4. Abra **somente** o markdown dessa correção
5. Leia os arquivos mencionados **nessa correção** — e **confirme o problema com
   a ferramenta** antes de corrigir. O sintoma descrito pode já ter sido
   resolvido por uma task posterior; corrigir o que não está mais quebrado é
   como se introduz regressão em código que estava certo
6. Implemente exatamente a correção descrita na seção **Correção**
7. Atualize `correcoes-progresso.md` marcando `[x]`
8. Preencha o **Log de Execução** no arquivo da correção
9. **Pare.** Não leia nem execute a próxima correção

---

## Regras de seleção

1. Primeira correção com `[ ]` no `correcoes-progresso.md`
2. Se `depends_on` não estiver `[x]`, informe o bloqueio e pare
3. Se alguma correção estiver marcada como "em andamento", conclua-a antes

> **EXCLUSÃO OBRIGATÓRIA 1 — escopo de arquivo:**
> Abra **apenas o `CORR-<PREFIXO>-XXX.md` da correção selecionada**. Não leia os
> outros, mesmo que apontem para o mesmo gerador ou o mesmo formulário.
>
> **EXCLUSÃO OBRIGATÓRIA 2 — uma CORR por execução:**
> Após concluir, **pare**. Não avance para a próxima `[ ]`, mesmo que seja no
> mesmo arquivo.
>
> **EXCLUSÃO OBRIGATÓRIA 3 — sem tasks:**
> Este prompt é exclusivo para `CORR-<PREFIXO>-XXX`. **Nunca** execute uma
> tarefa (`<PREFIXO>-TASK-XX`, com o prefixo que o `progresso.md` declarar)
> por aqui — elas são do `prompts/01-executar.md` e rastreadas em
> `progresso.md`.
>
> **EXCLUSÃO OBRIGATÓRIA 4 — respeitar as decisões confirmadas:**
> Confirme que o fix é compatível com o que a CORR aponta como origem **e com
> as "decisões já confirmadas" do perfil do ciclo**. Nunca use a correção como
> desculpa para: **editar à mão arquivo que um gerador produz**, **colar saída
> de decompilador** em spec ou em código, ou **escrever no que o perfil marca
> como leitura pura** (o binário alvo, `roms/`) — a menos que a CORR diga isso
> explicitamente e o usuário tenha confirmado.

---

## Discrepância achada no caminho: conserte, não só registre

A lista "Arquivos a criar ou modificar" de uma CORR é o **mínimo**, não o teto.
Se durante a execução você achar uma discrepância que a correção cria, revela
ou torna enganosa, **resolva na mesma invocação**. Registrar no Log e seguir em
frente não é resposta: quem lê o doc errado no dia seguinte não lê o seu Log.

Isso vale principalmente para o caso mais comum aqui — **o doc que descrevia o
defeito envelhece junto com o conserto**. Neste repositório o padrão já
apareceu: o `CLAUDE.md` afirmou "Delphi 6" em dois lugares durante meses, e o
plano novo nasceu contradizendo-o; corrigir um sem o outro deixaria o
repositório dizendo as duas coisas.

Alvos prováveis de varredura, por serem os que repetem número e afirmação:

- o **plano do ciclo** — o que a CORR citar, ou o que o perfil nomear
- `docs/tasks/progresso.md`
- `docs/tasks/<a task de origem>.md`
- o **perfil do ciclo** (`docs/prompts/perfil-*.md`) e os registros técnicos que
  ele listar como arquivos quentes
- `CLAUDE.md`
- `.claude/commands/*.md` — os wrappers dos slash commands. **Eles são
  versionados e reafirmam com outras palavras o rito que estes prompts
  descrevem**, então mudança de processo tem de entrar nos dois lugares. Já
  falhou uma vez: a CORR-WTE-001 acrescentou um passo à §4 do `01-executar.md`
  e o wrapper continuou enumerando o fechamento sem ele

Antes de commitar, faça a varredura:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o termo ou numero que voce mudou>" docs .claude CLAUDE.md \
  <as pastas de codigo que o perfil nomear>
```

Toda ocorrência que ficou falsa, incompleta ou apontando para o estado velho
entra nesta invocação.

**Como isso convive com o escopo (não há conflito):**

| Você achou | O que fazer |
| --- | --- |
| doc que a sua correção tornou falso ou incompleto | **conserte agora** |
| número que a sua ferramenta remede e não bate com o doc | **conserte agora**, com a data |
| rótulo ambíguo que a sua mudança cria | **conserte agora** |
| bug ou dívida sem relação com esta CORR | **abra `CORR-<PREFIXO>-XXX` novo** e siga |
| handler a implementar, formulário a gerar, trabalho de `<PREFIXO>-TASK` | **não faça** — as exclusões 2, 3 e 4 continuam valendo |

**Commit separado.** A correção num commit; a reconciliação de doc que ela
obrigou, em commit próprio, dizendo no corpo qual correção o provocou. Dois
commits na mesma invocação está certo.

**Se a discrepância for grande** — muda a conclusão de uma task, exige rodar o
golden inteiro (que custa ~1 GB de temporário e uma sessão de Wine), ou toca
decisão do plano — não a resolva de afogadilho: abra a CORR nova, registre o que
mediu, e reporte.

**Ao abrir CORR nova, releia o maior número do disco na hora de criar o
arquivo** — `ls docs/tasks/CORR-*.md | tail -1` —, e não use o número que o
inventário da fase 0 sugeria. Um `/revisar` pode ter criado CORRs entre uma
coisa e outra, e o próximo livre muda sem aviso. Já custou duas vezes: a
CORR-WTE-122/123 e a CORR-WTE-137, esta última com o arquivo de outra CORR
**sobrescrito** por ter o mesmo nome. O `git status` não acusa — o arquivo já
existia, e a substituição entra como modificação comum.

---

## O que o perfil do ciclo diz, e você tem de ler

O `perfil:` do `docs/tasks/progresso.md` nomeia o arquivo. Dele vêm, para esta
invocação:

| Do perfil | Por que importa aqui |
| --- | --- |
| **o que é leitura pura** | binário alvo e imagens de teste não se escrevem; trabalhe sobre cópia |
| **o que é gerado, e por qual gerador** | se o alvo da CORR estiver na lista, **a correção entra no gerador** e a árvore é regenerada. Editar a saída à mão não é correção — é a discrepância que a revisão deveria ter pegado |
| **os gates** | quais rodar, e a partir de quando cada um existe |
| **os arquivos quentes** | onde a varredura de discrepância costuma esbarrar |
| **as decisões confirmadas** | o que não se reverte sem o usuário pedir |

Estrutura comum a qualquer ciclo:

```text
new-we2002-editor/
  docs/
    tasks/                 # tasks, CORRs e progresso
    prompts/               # estes prompts + os perfis de ciclo
  roms/                    # imagens de teste (gitignored)
  work/                    # copias de trabalho (gitignored)
```

### A regra do `:98`

Toda execução com GUI acontece no `DISPLAY=:98`, com o `XAUTHORITY` resolvido
pelo `ps` (ver `CLAUDE.md`). **Feche qualquer janela grande no `:98` antes de
rodar um gate de GUI** — os dois lados de um golden acham a janela por
heurística, e uma sobra de teste manual é dirigida em vez da que está sob teste.

---

## Como executar

### 1) Ler contexto

- Ler `correcoes-progresso.md`
- Ler o `CORR-<PREFIXO>-XXX.md`
- **Reproduzir a evidência** da seção "Evidência" com o mesmo comando. Se o
  resultado não bater com o que a CORR descreve, **pare e reporte** — a CORR
  pode ter envelhecido
- Se a correção tocar comportamento, reler a spec dele onde o perfil disser
  que ela mora

### 2) Implementar

- Implementar exatamente o que está na seção **Correção**
- Não antecipar trabalho de outra fase. A lista de arquivos da CORR é o
  **mínimo**: discrepância que o conserto revelar entra nesta invocação, na
  regra "Discrepância achada no caminho" acima
- **Se o alvo for arquivo gerado, a correção entra no gerador e a árvore é
  regenerada.** Ver a tabela acima
- **Se a correção for de spec, ela não pode virar transcrição.** O campo
  evidência diz de onde veio o fato; trecho de decompilado vai parafraseado,
  nunca copiado
- **Se a correção tocar `src/core/`**, lembre que o `newWe2002` está com escopo
  fechado e verificado: rode `ctest` e o golden dele depois, e diga o resultado

### 3) Validar

Antes de marcar como concluída, todos os itens do checklist **Verificação** da
CORR, mais os gates que se aplicarem:

| Se a correção tocou | Gate |
| --- | --- |
| gerador ou saída de gerador | `--check` verde; rodar duas vezes dá bytes iguais |
| código compilado | o build do ciclo, sem warning novo |
| comportamento (handler, gravação) | o gate de comportamento do ciclo, com o **controle** fechando antes |
| `src/core/` | `ctest --preset debug` e o golden do `newWe2002` verdes — ele está com escopo fechado |
| número em doc | o número novo veio de ferramenta, não de soma à mão |
| qualquer coisa que escreva na imagem | trabalhou sobre cópia; `roms/` intocada |

**Os comandos concretos estão no perfil**, com a disponibilidade de cada um.
Esta tabela diz *o que* conferir; o perfil diz *como*, no ciclo em vigor.

Antes de fechar, a varredura de discrepância:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
grep -rn "<o termo que voce mudou>" docs .claude CLAUDE.md \
  <as pastas de codigo que o perfil nomear>
```

Toda ocorrência que ficou falsa, incompleta ou apontando para o estado velho é
trabalho **desta** invocação.

Se a correção ficar parcialmente pronta:
- Não marcar como concluída
- Atualizar o **Log de Execução** com o status parcial e as pendências

### 4) Atualizar progresso

Se concluída:
- Trocar `[ ]` por `[x]` no `correcoes-progresso.md` (tabela E checklist)
- Preencher a coluna **"Concluída em"** com a data do commit que aplicou a
  correção (`git log -1 --date=short --pretty=%ad`), formato `AAAA-MM-DD`. É a
  mesma data do `Executado em` do Log — se divergirem, uma delas está errada
- Conferir que a célula do ID é link para o markdown da correção
  (`[CORR-<PREFIXO>-XXX](/docs/tasks/CORR-<PREFIXO>-XXX.md)`, **sempre `/docs/` + caminho
  do arquivo**, como manda `.claude/rules/links.md`); se a linha
  veio sem link, ponha
- Trocar `status: pendente` por `status: concluído` no **frontmatter do
  `CORR-<PREFIXO>-XXX.md`**. O `02-revisar.md` abre toda correção com `pendente`, e o
  campo duplica a coluna Status do `correcoes-progresso.md`; os dois têm de
  concordar. Mesma regra do `01-executar.md` §4 para as tasks
- Preencher o **Log de Execução**:
  - **Executado em:** data de hoje
  - **Resumo do que foi feito:** 2-3 linhas
  - **Problemas encontrados:** ou "Nenhum"
  - **Arquivos criados/modificados:** lista

> **Marcar `[x]` não é o passo final — o commit é.** `[x]` descreve um estado
> que precisa **já existir commitado** quando você escrever isso, não uma
> intenção.

### 5) Commit

Código e documentação da correção juntos, no mesmo commit:

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
git add <arquivos específicos> docs/tasks/CORR-<PREFIXO>-XXX.md docs/tasks/correcoes-progresso.md
git commit -m "fix: <titulo curto no imperativo>"
```

- **Inglês, conventional commit** — `fix:`, `docs:`, `refactor:`… Primeira linha
  < 72 caracteres, imperativo
- O corpo diz **o que se aprendeu** — as boas mensagens deste repo registram a
  armadilha que quase pegou
- **Sem footer de co-autoria**
- Nunca `git add -A` nem `git add .`
- **Não versione:** `we-team-editor/`, `roms/`, `work/`, saída de build,
  cópias de imagem, projeto do Ghidra
- **`git commit` precisa rodar de fato.** Depois, `git status --short` limpo
  para esta correção
- **Existe remote**, mas **`push` só se o usuário pedir**

---

## Formato de saída esperado

1. Qual correção foi selecionada e por quê
2. **Confirmação de que o problema foi reproduzido**, com o comando e a saída
3. Resumo do que foi feito
4. Arquivos criados ou modificados
5. Resultado de cada gate aplicável, com o número medido
6. **SHA do commit** e confirmação de `git status --short` limpo
7. Bloqueios ou pendências

---

## Regra final

Não me entregue um plano.
Execute **uma única** correção pendente (a próxima `[ ]`), atualize o progresso
ao final e **pare**.
**Não marque `[x]` sem o commit já ter sido feito.**
Não avance para a seguinte mesmo que seja no mesmo arquivo.
Uma correção por invocação — nunca em paralelo, nunca em sequência na mesma
invocação.
