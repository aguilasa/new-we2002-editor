# Convenções de task

## A task declara a própria fonte de verdade

**Todo arquivo de task em `docs/tasks/` tem `fonte_de_verdade` no frontmatter**,
com um caminho `/docs/...` mais a seção:

```yaml
---
id: PAR-TASK-01
title: "Nomes e abreviações de time, pela tela"
type: verificação
category: ui
depends_on: []
fonte_de_verdade: "/docs/PARIDADE-FUNCIONAL.md §8.1"
status: pendente
---
```

O campo é **obrigatório**, e a mesma referência aparece em prosa na seção
`## Contexto` (`- **Referência:** ...`) — a duplicação é deliberada: o
frontmatter serve a quem automatiza, a prosa a quem lê.

### Por que, e o que isso proíbe

Os prompts de `docs/prompts/` — que os comandos de `.claude/commands/`
carregam — **são agnósticos de projeto**. Eles sabem:

1. ler `docs/tasks/progresso.md` e `docs/tasks/correcoes-progresso.md`;
2. abrir o markdown da task pelo **link na linha dela**;
3. fazer o que a task pede, medindo contra o que o `fonte_de_verdade` dela
   apontar.

Nada mais. **Não codifique num prompt** o nome de um plano, um prefixo de ID,
uma fase ou um mapeamento `ID → arquivo`. Este repositório já tem dois projetos
(`wte/` Lazarus e `newWe2002`) com planos diferentes no mesmo `progresso.md`, e
terá outros; prompt que conhece um deles pelo nome quebra no próximo.

Sintomas de que a regra foi violada, todos já vistos aqui:

| sintoma | o que estava errado |
|---|---|
| o prompt manda "ler a seção de `PLAN-X.md`" | fonte fixa; a task de outro projeto se mede contra outro arquivo |
| o prompt tem tabela `ID → arquivo` | duplica os links do `progresso.md`, e envelhece |
| o prompt ordena por prefixo de ID | ordem é do `progresso.md`, de cima para baixo |

### Ao criar uma task nova

- `fonte_de_verdade` preenchido e apontando para **arquivo que existe** — se
  a fonte ainda não existe, escreva-a antes, ou descreva o critério **dentro da
  própria task** e aponte para ela mesma;
- `status:` do frontmatter **igual** ao símbolo da tabela do `progresso.md`
  (`pendente`↔`⬜ Pendente`, `bloqueado`↔`❌ Bloqueado`, `concluído`↔`✅ Concluído`);
- linha na tabela do `progresso.md` **com link** para o arquivo — é assim que o
  prompt o encontra;
- `depends_on` só com IDs que existem.

Uma task que não diz contra o que se mede não é executável, e adivinhar o plano
pelo prefixo do ID é exatamente o acoplamento que esta regra impede.

## O ciclo declara o próprio perfil

**Todo `progresso.md` traz um campo `perfil:`** logo no cabeçalho, apontando
para um `/docs/prompts/perfil-<ciclo>.md`:

```markdown
**Perfil deste ciclo:** [`/docs/prompts/perfil-pes2.md`](/docs/prompts/perfil-pes2.md).
```

É a mesma mecânica do `fonte_de_verdade`, um nível acima: **a task nomeia o
plano contra o qual se mede; o progresso nomeia o perfil sob o qual o ciclo
roda.**

### O que fica no prompt e o que fica no perfil

| No prompt (agnóstico) | No perfil (do ciclo) |
| --- | --- |
| ler o progresso, achar a próxima pendente, conferir `depends_on` | as decisões já confirmadas, que não se revertem sem o usuário pedir |
| medir contra o `fonte_de_verdade` da task | as armadilhas medidas do ciclo |
| varrer discrepância, `[x]`/`✅` só depois do commit | as fontes de verdade binárias, e o que é leitura pura |
| um commit por item, reconciliação em commit próprio | o que é gerado, e por qual gerador |
| a regra do `:98` e "cópia, sempre" (são do repositório) | os gates, e a partir de quando cada um existe |
| a forma da tabela e do frontmatter | os arquivos quentes e os recursos serializados do ciclo |
| o padrão que autoriza antecipação | os precedentes de antecipação já aceitos |
| as quatro perguntas de revisão que valem para qualquer fase | as verificações específicas por fase |

### Por que, e o que isso proíbe

O motivo é o mesmo do `fonte_de_verdade`, e a falha que o mostrou foi medida:
três correções seguidas tiraram dos prompts o nome do plano e os dois prefixos
de ID, e o corpo operacional do ciclo `wte/` continuou lá — 64 caminhos `wte/`
cravados e 73 linhas de checklist sobre `.dfm` e `.lfm` num arquivo que executa
tasks de PES2 ([CORR-PES2-004](/docs/tasks/CORR-PES2-004.md)).

**Não escreva num prompt** o nome de uma ferramenta, de um gerador, de um
diretório de código ou de uma fase de projeto. Se a frase deixa de ser
verdadeira quando o ciclo muda, ela é do perfil.

**A distinção que custa reconhecer:** trocar um nome específico por um
placeholder nem sempre é o conserto. Um checklist que pergunta *"os 18 DFM
decodificaram inteiros?"* não vira agnóstico ao ser reindexado por
`<PREFIXO>-TASK-01 a 09` — vira uma **afirmação falsa** sobre o ciclo novo.
Texto que descreve um ciclo se **move** para o perfil dele; só o que descreve o
rito se generaliza no lugar.

**Citação datada de ciclo fechado fica onde está.** Uma armadilha que os
prompts registram — *"isso já falhou duas vezes no ciclo `wte/`"* — é evidência
do que aconteceu, e apagá-la para satisfazer um `grep` destrói o registro.

## As CORRs são autocontidas

`CORR-*.md` **não** leva `fonte_de_verdade`: ela traz `## Problema
identificado`, `## Evidência`, `## Causa raiz` e `## Correção`, que já dizem
contra o que o fix se mede. A origem — a task que a gerou — é a segunda coluna
da tabela do `correcoes-progresso.md`.

O pool de correções é **único dentro do ciclo**, com numeração contínua a
partir de `001`. **O prefixo é do ciclo, não da ferramenta** — quem o declara é
o `correcoes-progresso.md` vivo, na primeira seção. Foi `CORR-WTE-` de 001 a
143 no ciclo arquivado em `docs/tasks/concluidos/`, e é `CORR-PES2-` no ciclo
de PES2. **Quem abre uma correção lê o prefixo ali, nunca o deduz do prefixo
das tasks nem do que um prompt escreveu.** Dois pools no mesmo ciclo custariam
um segundo prompt de correção sem ganho nenhum.

**O prefixo das tasks segue a mesma regra, e quem o declara é o
`progresso.md`.** Foi `WTE-TASK-` no ciclo arquivado, e é `PES2-TASK-` no ciclo
de PES2. Os prompts escrevem os dois como `<PREFIXO>-TASK-XX` e
`CORR-<PREFIXO>-XXX` justamente por isso: **exclusão que nomeia um prefixo
morto não exclui coisa nenhuma** — as três "nunca execute … por aqui"
passaram um ciclo inteiro sem alcançar task alguma.

## Projeto encerrado vai para `docs/tasks/concluidos/`

Quando um projeto fecha, **tudo dele desce um nível**: as tasks, as `CORR-*.md`
e os dois arquivos de progresso vão juntos para `docs/tasks/concluidos/`, e
`docs/tasks/` fica só com `progresso.template.md` e
`correcoes-progresso.template.md` — a base do próximo.

**A pasta é um conjunto fechado, e é isso que faz a convenção continuar
valendo.** A task é conferida contra o `progresso.md` que mora **ao lado dela**;
o `tools/check_tasks.py` varre `docs/tasks/` e cada subpasta que tenha um
`progresso.md` próprio, e nunca cruza uma pasta com o progresso de outra. Mover
as tasks sem mover o progresso junto quebraria as três convenções de uma vez.

**Os prompts continuam apontando para `docs/tasks/progresso.md`** — o vivo, o
que a próxima leva de tasks vai criar do template. Eles não conhecem o arquivo,
e não devem: `concluidos/` é história, e prompt que aponta para história executa
task já feita.

## Conferência

```bash
cd /home/ingmar/desenvolvimento/github/new-we2002-editor
python3 tools/check_tasks.py
```

Ele confere as quatro coisas da lista acima em todas as tasks, e é o que impede
a regra de virar prosa. Rode antes de commitar task nova.
